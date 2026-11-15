"""SolidWorks 自带诊断能力的统一入口：出问题**先查这里**，再改代码。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 定位:   业主 2026-11-07 指令 ——「把各种Debug工具能力全部跑通，然后做成一个整个项目
#         通用的 Debug 模块，遇到问题先到 Debug 模块里寻找 Debug 解法。这样不管是画
#         齿轮还是画什么，出问题了都有工具查问题然后根据查出来的问题寻找解法」
# 依据（官方页均在 `C:\swapi\types\` 与 `C:\swapi\enums\`）:
#   · `ISketch::CheckFeatureUse`   等价于工具「检查草图合法性」
#   · `ISketch::GetConstrainedStatus` + `swConstrainedStatus_e`
#   · `IBody2::Check3`（属性，返回 `IFaultEntity`，其 `Count>0` 即有故障）
#   · `IBody2::Diagnose`
#   · `IFeature::GetErrorCode2(out bool IsWarning)`
#   · `ISldWorks::GetErrorMessages(out,out,out)` —— 本会话最近 20 条消息
#   · `swRepairSketchOption_e`（Cleanup/ZeroSegment/MergeSegment/CloseGaps/
#     BreakIntersection）—— 修法的枚举出处
# 本模块只做**取数与判读**，不改模型；改模型的动作由调用方决定。
# 实测教训（2026-11-07，齿轮草图）:
#   `GetSketchContours()=1` 与 `IsClosed()=true` 都报「闭合」，但
#   `CheckFeatureUse` 报 status=15 / 闭合轮廓 **0** —— 后者才与建特征的判据一致；
#   真因是 120 段曲线累积出 **15.6 µm** 的首尾缝 ⇒ **MergePoints(1e-6 m)** 后
#   status→0、闭合轮廓→1、拉伸成功（体积 3092.021 mm³）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass, field

import pythoncom
import win32com.client

from sw_connect import get_com_member
from sw_feature_readback import feature_names
from sw_sketch_check import (
    FEATURE_TYPES,
    STATUS as SKETCH_STATUS,
    SketchCheck,
    check_sketch as _check_sketch,
    sketch_of,
)

#: `swConstrainedStatus_e`
#: enum-gate: enum swConstrainedStatus_e
CONSTRAINED_STATUS: dict[int, str] = {
    1: "未知约束状态",
    2: "欠定义（蓝线，改尺寸会乱跑）",
    3: "完全定义",
    4: "过定义",
    5: "无解",
    6: "解无效",
    7: "自动求解已关闭",
}

#: 草图检查状态码 → **修法**（业主要的「Debug 解法」就在这里）
#: enum-gate: enum swSketchCheckFeatureStatus_e
SKETCH_REMEDIES: dict[int, str] = {
    0: "无需处理",
    1: "轮廓自相交：把交叉处拆开；若只差极小缝，先试 MergePoints(1e-6~1e-5)",
    2: "实体自相交：检查样条是否过冲；减少控制点或改用真圆弧",
    3: "含自相交实体：同上",
    4: "某端点被多个实体错误共享：删掉多余线段后重画",
    5: "空草图：确认几何已画进草图而不是别的草图",
    6: "含开放轮廓：**先试 MergePoints(1e-6~1e-5)**（本仓齿轮实测有效）",
    7: "轮廓多于一个：显式选中要用的那一个轮廓再建特征",
    8: "含零长度实体：删除零长度线段",
    9: "开放轮廓多于一个：逐条 MergePoints 或删掉多余开放链",
    10: "已无开放轮廓：换用需要闭合轮廓的特征类型",
    11: "同时含开放与闭合轮廓：删掉开放链或用 MergePoints 合上",
    12: "轮廓相互相交：拆开相交处",
    13: "轮廓互不相连：确认为阵列/多实体意图，否则合并",
    14: "轮廓是开放的：**先试 MergePoints(1e-6~1e-5)**",
    15: "轮廓是闭合的但该特征要求开放：**特征类型选错了**（如扫描路径应选 SWEEPPATHORGUIDE）",
    16: "含双重嵌套轮廓：确认是否想要环/孔，否则拆开",
    17: "轮廓多于一个：显式选轮廓",
    18: "应只含一条开放轮廓：改用需要闭合轮廓的特征类型",
    19: "应只含一条闭合轮廓：删掉多余轮廓",
    20: "应为单条开放或多条互不相连的闭合：按提示减轮廓",
    21: "应含中心线：加一条中心线（旋转类特征必需）",
    22: "所选轮廓开放或不明确：显式选中单个轮廓对象再建特征",
    23: "旋转轮廓穿过/点触中心线：把轮廓整体挪离轴线（内径不能为 0）",
    -1: "未知错误：查会话错误日志（session_messages）",
}


@dataclass(frozen=True)
class Finding:
    """一条诊断结论 + 对应修法。"""

    scope: str          # sketch / feature / body / session
    target: str         # 草图名 / 特征名 / 体序号 / 消息序号
    ok: bool
    code: object        # 状态码或错误码
    text: str           # 人读说明
    remedy: str         # 修法（ok=True 时为「无需处理」）


@dataclass
class DebugReport:
    """一次完整诊断的汇总。"""

    findings: list[Finding] = field(default_factory=list)

    @property
    def problems(self) -> list[Finding]:
        return [f for f in self.findings if not f.ok]

    @property
    def ok(self) -> bool:
        return not self.problems

    def text(self) -> str:
        lines = [f"=== Debug 报告（共 {len(self.findings)} 项，"
                 f"问题 {len(self.problems)} 项）==="]
        for f in self.findings:
            mark = "✓" if f.ok else "✗"
            lines.append(f"  {mark} [{f.scope}] {f.target}: {f.text}")
            if not f.ok:
                lines.append(f"      修法 → {f.remedy}")
        if self.ok:
            lines.append("  ⇒ 未发现问题")
        return "\n".join(lines)


def _byref_i4(value: int = 0):
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, value)


def _byref_bool(value: bool = False):
    return win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, value)


def _byref_variant():
    return win32com.client.VARIANT(
        pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


# ── 草图 ─────────────────────────────────────────────────────────────
def check_sketch(sketch, feature_type: int = 3) -> list[Finding]:
    """检查一张草图：约束状态 + 能否用于指定特征。"""
    out: list[Finding] = []

    # ① 约束状态
    try:
        cs = int(get_com_member(sketch, "GetConstrainedStatus"))
        out.append(Finding(
            scope="sketch", target="约束状态", ok=(cs == 3), code=cs,
            text=f"{cs} = {CONSTRAINED_STATUS.get(cs, '未登记')}",
            remedy="无需处理" if cs == 3
            else "用 AutoDimension2 / FullyDefineSketch 补齐约束，"
                 "或确认「自动求解」已打开（状态 7）",
        ))
    except Exception as exc:  # noqa: BLE001 — 取不到约束状态不该中断其它检查
        out.append(Finding("sketch", "约束状态", False, type(exc).__name__,
                           f"读取失败：{str(exc)[:80]}", "换 GetConstrainedStatus 前确认草图对象有效"))

    # ② 能否用于该特征（官方「检查草图合法性」）
    try:
        chk: SketchCheck = _check_sketch(sketch, feature_type)
        out.append(Finding(
            scope="sketch", target=f"可用于特征({feature_type})", ok=chk.ok,
            code=chk.status,
            text=f"{chk.status_text}｜开放 {chk.open_count}｜闭合 {chk.closed_count}",
            remedy=SKETCH_REMEDIES.get(chk.status, "查官方 swSketchCheckFeatureStatus_e"),
        ))
    except Exception as exc:  # noqa: BLE001
        out.append(Finding("sketch", "可用于特征", False, type(exc).__name__,
                           f"检查失败：{str(exc)[:80]}",
                           "out 参数须传 VARIANT(VT_BYREF|VT_I4)"))
    return out


def check_sketches(model, feature_type: int = 3) -> list[Finding]:
    """检查文档里每张草图。"""
    out: list[Finding] = []
    for n in (feature_names(model) or []):
        if "草图" not in str(n):
            continue
        sk = sketch_of(model, n)
        if sk is None:
            continue
        for f in check_sketch(sk, feature_type):
            out.append(Finding(f.scope, f"{n}·{f.target}", f.ok, f.code,
                               f.text, f.remedy))
    return out


# ── 特征 ─────────────────────────────────────────────────────────────
def check_features(model) -> list[Finding]:
    """逐特征读错误码（等价于特征树上那个「什么错了」图标）。"""
    out: list[Finding] = []
    for n in (feature_names(model) or []):
        feat = get_com_member(model, "FeatureByName", n)
        if feat is None:
            continue
        iw = _byref_bool(False)
        try:
            code = int(get_com_member(feat, "GetErrorCode2", iw))
        except Exception:  # noqa: BLE001 — 该特征不支持取错误码时跳过
            continue
        if code == 0:
            continue
        kind = "警告" if iw.value else "错误"
        out.append(Finding(
            scope="feature", target=str(n), ok=False,
            code=code, text=f"错误码 {code}（{kind}）",
            remedy="在特征树上右键看『什么错了』；修上游草图通常能连带修好",
        ))
    return out


# ── 实体 ─────────────────────────────────────────────────────────────
def check_bodies(model) -> list[Finding]:
    """逐实体做有效性检查（`IBody2::Check3` 与 `Diagnose`）。"""
    out: list[Finding] = []
    try:
        bodies = list(get_com_member(model, "GetBodies2", 0, True) or [])
    except Exception as exc:  # noqa: BLE001
        return [Finding("body", "-", False, type(exc).__name__,
                        f"取实体失败：{str(exc)[:80]}", "确认文档是零件且已有实体")]
    if not bodies:
        out.append(Finding("body", "-", False, "none", "文档没有实体（还没建成特征）",
                           "先确认特征已建成，再谈体检"))
        return out
    for i, b in enumerate(bodies):
        try:
            fe = get_com_member(b, "Check3")
            cnt = 0
            if fe is not None:
                try:
                    cnt = int(get_com_member(fe, "Count") or 0)
                except Exception:  # noqa: BLE001
                    cnt = -1
            out.append(Finding(
                scope="body", target=f"体{i}", ok=(cnt == 0), code=cnt,
                text=("无效" if cnt > 0 else "有效") if cnt >= 0
                     else "Check3 返回对象但取不到 Count",
                remedy="有故障实体时用 Diagnose 定位，或回退上游特征" if cnt else "无需处理",
            ))
        except Exception as exc:  # noqa: BLE001
            out.append(Finding("body", f"体{i}", False, type(exc).__name__,
                               f"Check3 失败：{str(exc)[:70]}",
                               "确认是 IBody2 对象"))
    return out


# ── 会话级消息 ───────────────────────────────────────────────────────
def session_messages(sw, last: int = 20) -> list[Finding]:
    """读本会话最近的消息（官方：最近 20 条）。

    这是**最有用的一条**：SW 会把「无法封闭此草图」「选择失败」这类原话记在这里，
    比任何返回值都直接。
    """
    out: list[Finding] = []
    try:
        m1, m2, m3 = _byref_variant(), _byref_variant(), _byref_variant()
        n = int(get_com_member(sw, "GetErrorMessages", m1, m2, m3))
    except Exception as exc:  # noqa: BLE001
        return [Finding("session", "-", False, type(exc).__name__,
                        f"GetErrorMessages 失败：{str(exc)[:80]}",
                        "三个 out 参数都要传 VARIANT(VT_BYREF|VT_VARIANT)")]
    msgs = list(m1.value or []) if m1.value is not None else []
    types_ = list(m3.value or []) if m3.value is not None else []
    for i, msg in enumerate(msgs[-max(1, last):]):
        txt = " ".join(str(msg).split())
        t = types_[i] if i < len(types_) else "?"
        out.append(Finding("session", f"#{i}", True, t, f"[类型{t}] {txt[:160]}",
                           "参考信息（SW 原话，排错时先读它）"))
    if n and not msgs:
        out.append(Finding("session", "-", True, n, f"报告 {n} 条但取不到正文",
                           "参考信息"))
    return out


# ── 总入口 ───────────────────────────────────────────────────────────
def diagnose(model, sw=None, feature_type: int = 3,
             include_session: bool = True) -> DebugReport:
    """跑全部检查，返回汇总报告。**出问题先调这个。**

    参数:
        model: `IModelDoc2`
        sw: `ISldWorks`；给了才会读会话消息
        feature_type: `swSketchCheckFeatureProfileUsage_e` 值（默认 3 = 拉伸凸台）
        include_session: 是否读会话级消息

    返回:
        `DebugReport`；`.problems` 是问题清单，`.text()` 是可读报告
    """
    rep = DebugReport()
    rep.findings.extend(check_sketches(model, feature_type))
    rep.findings.extend(check_features(model))
    rep.findings.extend(check_bodies(model))
    if include_session and sw is not None:
        rep.findings.extend(session_messages(sw))
    return rep


if __name__ == "__main__":
    import sys

    from sw_connect import connect_solidworks

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    _sw, _model = connect_solidworks(wait_seconds=15)
    if _model is None:
        print("没有活动文档")
        raise SystemExit(2)
    print(diagnose(_model, _sw).text())

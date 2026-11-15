"""草图合法性检测：调 SolidWorks 自带的「检查草图合法性」判草图能否用于指定特征。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 依据:   `C:\swapi\types\ISketch\CheckFeatureUse.md`
#         `C:\swapi\enums\swSketchCheckFeatureProfileUsage_e.md`（24 个特征类型）
#         `C:\swapi\enums\swSketchCheckFeatureStatus_e.md`（24 个状态码）
# 官方逐字: 「This method is equivalent to the SOLIDWORKS interactive tool
#   **Check Sketch for Feature Usage**.」
# 签名:   `int CheckFeatureUse(int FeatureType, out int OpenCount, out int ClosedCount)`
# 定位:   业主 2026-11-07 指令 —— 先用 API 把 SolidWorks 自带的评估/检测能力跑通。
#         动因：齿轮草图反复拉伸失败，而 `GetSketchContours()=1` / `IsClosed()=true`
#         都报「闭合」，与拉伸结果矛盾。本模块用的是 SW **自己的**判据，
#         实测能区分：方形 → status=0（闭合轮廓 1）；齿轮 → status=15（闭合轮廓 0）。
# 坑:     ★ pywin32 迟到绑定下两个 `out` 参数**必须**显式传
#           `VARIANT(VT_BYREF | VT_I4)`，否则报「非选择性的参数」（实测三次）。
#         ★ 失败时 `OpenCount`/`ClosedCount` **都回 0**（官方 Remarks 逐字），
#           所以「闭合=0」既可能是真没有闭合轮廓、也可能是检查失败 —— 必须同时看 status。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

from dataclasses import dataclass

import pythoncom
import win32com.client

from sw_connect import get_com_member

#: 特征类型（`swSketchCheckFeatureProfileUsage_e`）
#: enum-gate: enum swSketchCheckFeatureProfileUsage_e
FEATURE_TYPES: dict[str, int] = {
    "UNSET": 0,                    # 通用检查（任何特征用法下的毛病）
    "BASEEXTRUDE": 1, "BASEEXTRUDETHIN": 2,
    "BOSSEXTRUDE": 3, "BOSSEXTRUDETHIN": 4,
    "SURFACEEXTRUDE": 5,
    "BASEREVOLVE": 6, "BASEREVOLVETHIN": 7,
    "BOSSREVOLVE": 8, "BOSSREVOLVETHIN": 9,
    "SURFACEREVOLVE": 10,
    "CUTEXTRUDE": 11, "CUTEXTRUDETHIN": 12,
    "CUTREVOLVE": 13, "CUTREVOLVETHIN": 14,
    "SWEEPSECTION": 15, "SURFACESWEEPSECTION": 16,
    "SWEEPPATHORGUIDE": 17,
    "LOFTSECTION": 18, "SURFACELOFTSECTION": 19,
    "LOFTGUIDE": 20,
    "RIBSECTION": 21,
    "SHEETMETAL_BASEFLANGE": 22,
    "MOLD_PARTINGSURFACES": 23,
}

#: 状态码（`swSketchCheckFeatureStatus_e`）→ 中文说明
#: enum-gate: enum swSketchCheckFeatureStatus_e
STATUS: dict[int, str] = {
    0: "OK —— 可用于该特征",
    1: "轮廓自相交",
    2: "实体自相交",
    3: "含自相交实体（未指明）",
    4: "某端点被多个实体错误共享",
    5: "空草图",
    6: "含开放轮廓",
    7: "轮廓多于一个",
    8: "含零长度实体",
    9: "开放轮廓多于一个",
    10: "已无开放轮廓",
    11: "同时含开放与闭合轮廓",
    12: "轮廓相互相交",
    13: "轮廓互不相连",
    14: "轮廓是开放的",
    15: "轮廓是闭合的（但该特征要求开放）",
    16: "含双重嵌套轮廓",
    17: "轮廓多于一个",
    18: "应只含一条开放轮廓",
    19: "应只含一条闭合轮廓",
    20: "应为单条开放或多条互不相连的闭合",
    21: "应含中心线",
    22: "所选轮廓开放或不明确",
    23: "旋转轮廓不能穿过/点触中心线",
    -1: "未知错误",
}


@dataclass(frozen=True)
class SketchCheck:
    """一次合法性检查的结果。"""

    feature_type: int
    status: int
    status_text: str
    open_count: int
    closed_count: int

    @property
    def ok(self) -> bool:
        return self.status == 0

    def report(self) -> str:
        return (
            f"status={self.status}（{self.status_text}）"
            f"｜开放轮廓 {self.open_count}｜闭合轮廓 {self.closed_count}"
        )


def check_sketch(sketch, feature_type: int = 3) -> SketchCheck:
    """判该草图能否用于创建指定特征（默认 3 = 拉伸凸台）。

    参数:
        sketch: `ISketch` 对象
        feature_type: `swSketchCheckFeatureProfileUsage_e` 的值，
            可用 `FEATURE_TYPES["BOSSEXTRUDE"]` 等键取

    返回:
        `SketchCheck`；`ok` 为真表示 SW 认为该草图可用于此特征

    ⚠ 失败时 `open_count` / `closed_count` **都回 0**（官方 Remarks），
      所以判据要看 `status`，不能只看 `closed_count`。
    """
    if sketch is None:
        raise ValueError("sketch 为 None")
    oc = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    cc = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
    st = int(get_com_member(sketch, "CheckFeatureUse", int(feature_type), oc, cc))
    return SketchCheck(
        feature_type=int(feature_type),
        status=st,
        status_text=STATUS.get(st, f"未登记状态码 {st}"),
        open_count=int(oc.value),
        closed_count=int(cc.value),
    )


def sketch_of(model, name: str):
    """按特征名取 `ISketch` 对象（取不到返回 None）。"""
    feat = get_com_member(model, "FeatureByName", name)
    if feat is None:
        return None
    for meth in ("GetSpecificFeature2", "GetSketch"):
        try:
            sk = get_com_member(feat, meth)
            if sk is not None:
                return sk
        except Exception:  # noqa: BLE001
            continue
    return None


def check_all_sketches(model, feature_type: int = 3) -> dict[str, SketchCheck]:
    """对文档里每个草图跑一次检查，返回 {草图名: SketchCheck}。"""
    from sw_feature_readback import feature_names

    out: dict[str, SketchCheck] = {}
    for n in (feature_names(model) or []):
        if "草图" not in str(n):
            continue
        sk = sketch_of(model, n)
        if sk is None:
            continue
        try:
            out[str(n)] = check_sketch(sk, feature_type)
        except Exception:  # noqa: BLE001 — 单个草图取不到不影响其它
            continue
    return out

"""★ 草图查询（只读）：完全定义状态。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）· 规格 `specs/202-user-coverage-gaps`（T401 / FR-007）
# 文件:   scripts/sw_sketch_status.py
# 定位:   ★ 2026-10-03（接手轮）★ 补 `docs/user-feature-coverage.md` §八 的缺口项
#   **草图 / 完全定义检查**（★ 该项的关键词契约是 `fully_defined` ⇒ 工具名要含它）。
#
#   ★★ **官方依据（三源之①）**：`C:\swapi\types\ISketch\GetConstrainedStatus.md`
#     ```
#     **Signature**: `System.int GetConstrainedStatus()`
#     ```
#     ★ 官方**没有** `## Remarks`、也没有参数 ⇒ ★ **只读、零参数**。
#
#   ★★ **真机实测（`tools/prove_coverage_gap_batch1.py`，零弹窗）**：
#     ```
#     未加约束的矩形（4 段）⇒ GetConstrainedStatus = **2**
#     对 4 段全加 `sgFIXED` 后  ⇒ GetConstrainedStatus = **3**
#     ⇒ ★★ **两个读数不同** ⇒ ★ 这个回读数**有区分度**（★ 不是常量）
#     ```
#   ★★★ 2026-10-25 **把「查不到」补上了**：原来源块写「官方那一页没有给
#     `swConstrainedStatus_e` 的取值表 ⇒ 不把 2/3 解释成欠定义/完全定义」。
#     ★ 那句在写的时候是真的 —— `GetConstrainedStatus.md` 确实没有枚举链接；
#     ★ 但**枚举页本身存在**：`C:\swapi\enums\swConstrainedStatus_e.md`（7 个成员），
#       而且 `scripts/sw_sketch_relations.py` 早已照录过它并留了真机铁证
#       （读出 `status = 4` 时截图有红「项目无法解出」+ 黄「项目冲突」）。
#     ⇒ ★ 同一件事在两个模块里说法相反 ⇒ 现在**归口到本模块**：
#       取值表 `CONSTRAINED_STATUS` 与语义 `status_meaning()` 都在这，
#       由 `sw_sketch_relations.py` 复用（一个事实一个家）。
#     ⇒ ★ 上面那两行真机读数**现在可以解释了**：2 = `swUnderConstrained`、
#       3 = `swFullyConstrained` —— 与官方表**完全吻合**，是交叉验证而非猜测。
#
#   ★ 许可: 本仓库 MIT。★ **无第三方代码引入**（不外抄任何项目文本）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

#: ★★ COM 依赖**延迟到函数内**（2026-10-25）——
#:   本模块现在同时承载**纯数据表** `CONSTRAINED_STATUS` / `status_meaning()`，
#:   而其它模块（`sw_sketch_relations.py`）会为了那张表 import 本模块。
#:   ⇒ 若在模块顶层 import `sw_connect`，只为拿表也会被迫拉起 COM 依赖链，
#:     在**打桩环境**（`tests/test_relation_enum_alignment.py` 用
#:     `spec_from_file_location` + 伪 `sw_connect`）下会直接 ImportError。
#:   ⇒ 纯数据表**不该**有 COM 依赖。函数内 import，谁真调 COM 谁才付这个成本。

__all__ = [
    "CONSTRAINED_STATUS",
    "MEANING_UNKNOWN",
    "get_constrained_status",
    "status_meaning",
]

#: ★★ `swConstrainedStatus_e` **官方取值表**（7 个成员）。
#:
#: 出处：`C:\swapi\enums\swConstrainedStatus_e.md` 逐字（§一 三源之①）。
#:
#: ★★★ 2026-10-25 补：本模块原写「查不到官方取值表」——
#:   那句在写的时候是**真的**（当时只核了 `GetConstrainedStatus.md`，那页确实没有枚举链接）。
#:   但**枚举页本身存在**，`sw_sketch_relations.py` 早已照录过它。
#:   ⇒ 同一件事在两个模块里说法相反 ⇒ 现在把取值表**归口到本模块**，
#:     由 `sw_sketch_relations.py` 复用（一个事实一个家）。
#:
#: ★ 真机佐证（`sw_sketch_relations.py` 记录的现场铁证）：
#:   读出 `status = 4` 时截图上有红「项目无法解出」+ 黄「项目冲突」
#:   ⇒ 4 = `swOverConstrained` 得到真机确认。
#: ★ 本模块早先的真机读数（未加约束 = 2、全加 `sgFIXED` = 3）
#:   与表里的 2 = `swUnderConstrained`、3 = `swFullyConstrained` **完全吻合**。
CONSTRAINED_STATUS = {
    1: "swUnknownConstraint",
    2: "swUnderConstrained",
    3: "swFullyConstrained",
    4: "swOverConstrained",
    5: "swNoSolution",
    6: "swInvalidSolution",
    7: "swAutosolveOff",
}

#: ★ 中文语义（只对**已确认**的取值给中文；未确认的只回英文名）。
_STATUS_ZH = {
    2: "欠定义（还可以加约束）",
    3: "完全定义（不要再加约束）",
    4: "过定义（红『项目无法解出』+ 黄『项目冲突』）",
    5: "无解",
    6: "无效解",
    7: "自动求解已关闭",
}

#: ★ 兼容旧名：取值表已归口，本常量只在**取不到值**时用。
MEANING_UNKNOWN = "取不到 GetConstrainedStatus 的返回值"


def status_meaning(value: object) -> str:
    """★ 把 `GetConstrainedStatus()` 的整数转成可读语义。

    ★ 表外取值 ⇒ 回 `unknown(<n>)`，**不猜**（铁律 5）。
    """
    try:
        n = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown(%r)" % (value,)
    name = CONSTRAINED_STATUS.get(n)
    if name is None:
        return "unknown(%d)" % n
    zh = _STATUS_ZH.get(n)
    return "%s（%s）" % (name, zh) if zh else name


def _active_sketch(model):
    """★ 取**当前活动草图**对象 —— ★ 走**后继入口** `ISketchManager.ActiveSketch`。

    ★★★ 2026-10-03（接手轮）**把顺序倒过来了**：★ 原来是
      「**先** `GetActiveSketch2()`（★ 已废弃），★ 退回 `SketchManager.ActiveSketch`」
      —— ★★ 正好把**废弃的排在前面**。★ 现在**只用后继**（★ 真机已验证两者行为等价，
      ★ 所以不必再留兜底链 ⇒ 少一层分支、也少一处废弃调用）。
      ★ 官方 `IModelDoc2/GetActiveSketch2.md` 逐字：
        「**Obsolete. Superseded by [[ISketchManager::ActiveSketch]].**」
      ★★ 真机证据：`tools/probe_activesketch_successor.py` ·
        `output/activesketch-successor-evidence.json` ⇒ ★ **PASS** ✓

    ⚠ 官方**要求草图处于打开（编辑）状态** —— ★ 关掉的草图取不到（真机：两个入口都回 `None`）。
    """
    from sw_sketch import active_sketch as _shared_active_sketch

    return _shared_active_sketch(model)


def get_constrained_status(model, *, raise_on_no_sketch: bool = True) -> dict:
    """★ **完全定义状态**：`ISketch.GetConstrainedStatus()` → `System.int`（官方零参数）。

    ⚠ **前置**：**必须有一个正在编辑的草图** —— 关掉的草图取不到草图对象。
      ★ 没有活动草图时：`raise_on_no_sketch=True` ⇒ **抛**（不静默回 0）；否则回 `ok=False`。

    ★ 判据 = **调得动且回 `int`**（★ 真机实测；★ 并已验证两个不同状态下读数**不同**）。
    """
    try:
        from .sw_connect import get_com_member
    except ImportError:  # 顶层载入（探针 / 脚本）
        from sw_connect import get_com_member

    if model is None:
        return {"ok": False, "error": "model 为 None"}
    sk = _active_sketch(model)
    if sk is None:
        if raise_on_no_sketch:
            raise RuntimeError(
                "没有活动草图 ⇒ 取不到 ISketch（`GetActiveSketch2` 与 `SketchManager.ActiveSketch` "
                "都回 None）。★ 完全定义状态只能问**正在编辑**的草图 —— 请先 `sketch_start`。"
            )
        return {"ok": False, "error": "没有活动草图"}
    value = get_com_member(sk, "GetConstrainedStatus")
    if value is None:
        return {
            "ok": False,
            "op": "constrained_status",
            "error": "GetConstrainedStatus 回 None",
        }
    return {
        "ok": True,
        "op": "constrained_status",
        "status": int(value),
        "raw": value,
        "meaning": status_meaning(value),
        "fully_defined": int(value) == 3,
        "verified_by": (
            "official_signature_returns_int + 官方枚举表 swConstrainedStatus_e + "
            "真机读数（2 未约束 / 3 全固定 / 4 过定义含红黄警告）"
        ),
    }

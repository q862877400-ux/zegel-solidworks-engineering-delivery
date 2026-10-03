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
#     ⚠ **如实写清限度**：★ 本轮**只实测了两个取值**（2 与 3）；
#       ★ 官方那一页**没有给 `swConstrainedStatus_e` 的取值表** ⇒
#       ★ **不把 2/3 解释成"欠定义/完全定义"**（★ 铁律 5：查不到就说查不到）。
#       ⇒ ★ 本函数**如实回原始 int**，★ 并附 `meaning: "查不到官方取值表"`。
#
#   ★ 许可: 本仓库 MIT。★ **无第三方代码引入**（不外抄任何项目文本）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

try:
    from .sw_connect import get_com_member
except ImportError:                                                     # 顶层载入（探针 / 脚本）
    from sw_connect import get_com_member

__all__ = ["get_constrained_status", "MEANING_UNKNOWN"]

#: ★ 官方未给取值表 ⇒ 如实标注（铁律 5）
MEANING_UNKNOWN = "查不到官方取值表（GetConstrainedStatus.md 无 ## Remarks、无枚举链接）"


def _active_sketch(model):
    """★ 取**当前活动草图**对象 —— ★ 走**后继入口** `ISketchManager.ActiveSketch`。

    ★★★ 2026-10-03（接手轮）**把顺序倒过来了**：★ 原来是
      「**先** `GetActiveSketch2()`（★ 已废弃），★ 退回 `SketchManager.ActiveSketch`」
      —— ★★ 正好把**废弃的排在前面**。★ 现在**只用后继**（★ 真机已验证两者行为等价，
      ★ 所以不必再留兜底链 ⇒ 少一层分支、也少一处废弃调用）。
      ★ 官方 `IModelDoc2/GetActiveSketch2.md` 逐字：
        「**Obsolete. Superseded by [[SketchManager::ActiveSketch]].**」
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
        return {"ok": False, "op": "constrained_status",
                "error": "GetConstrainedStatus 回 None"}
    return {"ok": True, "op": "constrained_status",
            "status": int(value), "raw": value,
            "meaning": MEANING_UNKNOWN,
            "verified_by": "official_signature_returns_int + 真机两状态读数不同（2 vs 3）"}

"""★ EC00 T017/T018 判据：草图关系**正式注册** + **效果回读映射**（★ 离线 · ★ 不连接 COM）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch113.py`（★ T017 的注册）
#         `scripts/sw_sketch_relations.py`（★ 实现 · ★ 判据 = `GetRelationsCount` 真 +1）
#         `tests/test_sw_sketch_relations_safety.py`（★ spec 221 的 **12 例**安全判据）
#         `specs/302-ec00-trustworthy-tool-base/research/T006-official-signature.md`（★ 官方签名核验）
# 定位:   ★ EC00 **T017**（正式注册 · 参数注入/包装 · 类型/数量/上下文预检）与
#         **T018**（效果回读映射 · ★ **禁止 `return true` 直通**）的判据。
#         ★★ 纪律：★ **静态/离线**；★★ **桩测试不能称为 COM 验证**（★ 计划 §7 L2）。
# 官方依据: `AddRelation(object, int)`（★ 2 参）· `## Remarks`（★ 活动草图）· `GetRelationsCount`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

TOOL = "solidworks_sketch_apply_relations"
REL_SRC = ROOT / "scripts" / "sw_sketch_relations.py"


def _specs() -> dict:
    import register_capabilities as rc
    return {s.name: s for s in rc.all_specs()}


# ── T017：正式注册 ────────────────────────────────────────────────────

def test_t017_tool_is_registered():
    """★★★ T017：草图关系工具**必须已在 `all_specs()` 里**（★ 实测缺口：原本 **0** 个）。

    ★★ 依据：★ `scripts/sw_sketch_relations.py` 有实现（151 行）却**不可被 MCP 调用**
      ⇒ ★★ 从「用户可发现、可调用」口径看**等于不存在**（★ 计划 §2 逐字）。
    """
    s = _specs().get(TOOL)
    assert s is not None, (
        "★★ `%s` **未注册** ⇒ ★ 草图关系仍不可被 MCP 调用（★ 那是 T017 的缺口）" % TOOL)
    assert s.module == "sw_sketch_relations", "★ 模块不对：%r" % s.module
    assert s.function == "apply_sketch_relations", "★ 函数不对：%r" % s.function
    assert s.inject == "model", "★ `inject` 应是 `model`（★ 实现首参是 `model`）：%r" % s.inject


def test_t017_params_are_scalar_and_declared():
    """★★★ T017：参数必须是**标量**（★ MCP 边界只过标量 —— ★ 全仓无 `list` 型 `Param` 先例）。

    ★★ 依据（★ `mcp-server/tool_specs_batch15.py:21-25` 逐字）：
      「因为它们是 **`list` 型**，而实测：`tool_specs_batch*.py` 里**没有任何 `list` 型 `Param` 的先例**」
    """
    s = _specs().get(TOOL)
    assert s is not None, "★ 工具未注册"
    kinds = {p.name: p.kind for p in s.params}
    assert kinds.get("relations") is str, (
        "★ `relations` 应是 `str`（★ 全仓约定：`str` + 分隔符）—— ★ 实得 %r" % kinds.get("relations"))
    assert kinds.get("verify") is bool, "★ `verify` 应是 `bool`"
    #: ★★ **负例**：不许出现 `list` 型
    bad = [n for n, k in kinds.items() if k in (list, dict, tuple)]
    assert not bad, "★★ 出现了**非标量**参数 %r ⇒ ★ 违反 MCP 边界约定" % bad


def test_t017_derived_args_splits_into_a_list():
    """★★ T017：`derived_args` 必须把 `;` 分隔的字符串**拆成清单**（★ 实现收 `list[str]`）。"""
    s = _specs().get(TOOL)
    assert s is not None and s.derived_args is not None, "★ 缺 `derived_args`"

    class _P:
        relations = "horizontal:0;coincident:0,1"
        verify = True

    got = s.derived_args(_P())
    assert "relations" in got, "★ `derived_args` 没产出 `relations`"
    assert got["relations"] == ["horizontal:0", "coincident:0,1"], (
        "★ 拆分结果不对：%r" % got["relations"])
    #: ★ 空串 ⇒ 空清单（★ 不是错误）
    class _E:
        relations = ""
        verify = True
    assert s.derived_args(_E())["relations"] == [], "★ 空串应拆成空清单"


def test_t017_official_arity_is_two():
    """★★★ T017：本仓对 `AddRelation` 的调用必须是**官方的 2 参**（★ 不是 `IAddRelation` 的 3 参）。

    ★★ 依据：★ `AddRelation(object Entities, int RelationType)`（**2 参**）vs
      `IAddRelation(Int32 NumEntities, ref Object EntityArray, Int32 RelationType)`（**3 参**）
      ⇒ ★★★ 传错个数报 `0x8002000E`。
    """
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    arities = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            name = fn.attr if isinstance(fn, ast.Attribute) else (fn.id if isinstance(fn, ast.Name) else "")
            if name == "add_relation":
                arities.append(len(node.args))
    assert 2 in arities, "★ `add_relation` 的实参个数是 %r ⇒ ★ 没有一处是官方的 2 参" % arities


def test_t017_precondition_active_sketch_is_checked():
    """★★ T017：官方 `## Remarks` 的**唯一前置**（★ 活动草图）必须被实现**检查**。

    ★ 官方逐字：★「A sketch must be active for this method to have any effect.」
    """
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "_active(model)" in src, "★ 实现没有查活动草图"
    assert "没有活动草图" in src, "★ 没有活动草图时的**明确拒绝**不见了"


# ── T018：效果回读映射（★ 禁止 return true 直通）─────────────────────

def test_t018_no_true_passthrough():
    """★★★ T018：**不许**把 API 返回值直接映射成 `pass`（★ FR-008 的核心）。

    ★★ 依据（★ `plan.md` §五 逐字）：★「★ **不把 `return true` 映射为 pass**」。
    ★ 判据：★ 实现里**必须有** `effect_status`（★ 三态）—— ★ **不能只有** `applied: True`。
    """
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "effect_status" in src, (
        "★★ 实现里没有 `effect_status` ⇒ ★ 无法区分 pass/fail/unknown（★ FR-008 要求三态）")
    assert "execution_state" in src, (
        "★★ 实现里没有 `execution_state` ⇒ ★ 无法区分「已返回」与「uncertain」")


def test_t018_readback_uses_the_official_member():
    """★★★ T018：回读必须用**官方成员** `GetRelationsCount`（★ 不是猜的）。"""
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "GetRelationsCount" in src, (
        "★ 回读没有用官方 `ISketchSegment::GetRelationsCount` ⇒ ★ 判据失去官方依据")


def test_t018_uncertain_stops_the_batch():
    """★★★ T018：一处 `uncertain` ⇒ **批内后续项不得继续**（★ FR-009 · ★ **不重放**）。

    ★★ 依据（★ 实现逐字）：★「A previous relation has uncertain execution; batch stopped.」
    """
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "batch stopped" in src or "uncertain" in src, (
        "★ 实现里没有「uncertain ⇒ 停批」的语义 ⇒ ★ 会重放非幂等操作")


def test_t018_pre_state_required_before_dispatch():
    """★★ T018：**派发前必须有可信前态**（★ 读不到 ⇒ `rejected`，★ **不做任何修改**）。"""
    src = REL_SRC.read_text(encoding="utf-8", errors="replace")
    assert "Pre-dispatch relation count unavailable" in src, (
        "★ 实现里没有「前态读不到 ⇒ rejected」的分支 ⇒ ★ 可能在无前态时修改模型")

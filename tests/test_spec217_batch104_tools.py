"""★ 规格 217 · B3+B4 的契约与负例：4 个读侧「已实现但没暴露」的工具（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch104.py`）
# 文件:   tests/test_spec217_batch104_tools.py
# 定位:   ★ 规格 `specs/217-expose-orphans/` 的 **T-217-03（B3）+ T-217-04（B4）**。
# 判据（★ 事实 62：门禁只靠负例证明）：
#   ★ 正例①：4 个 `ToolSpec` 全部过 `check_spec`
#   ★ 正例②：4 个都在 `all_specs()` 里且**无重名**
#   ★ 正例③：工具数 = 463 + 4 = **467**
#   ★ 正例④：4 个都**被某个台账条目的 `mcp_tools` 认领**（三件套第 2 件）
#   ★★ 负例①：★ 4 个里**不许有裸坐标形参**（规则 3：名字也不许是 x/y/z）
#   ★★ 负例②：★ 台账 `level` **不许**被抬（★ 挂柜台定则 / 规格 204 的前车之鉴）
#   ★★ 负例③：★ **不许重名** —— 特别是 `solidworks_drawing_list_views_report`
#     与既有 `solidworks_drawing_list_views` **必须同时存在且名字不同**（★ 它们**不是重复**：
#     前者是"全图 + 4 项读数"、后者是"当前图纸 + 名字/类型码"）✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                    # noqa: E402

NEW = ("solidworks_drawing_list_views_report",
       "solidworks_mass_property_object",
       "solidworks_section_area_crosscheck",
       "solidworks_rib_params")

BASE_TOOL_COUNT = 463

EXPECTED_LEVELS = {
    "drawing_view_operations": "verified",
    "modeling_feature_readback_tools": "verified",
    "mass_property_read": "verified",
}


def _specs():
    return {s.name: s for s in RC.all_specs()}


def test_four_new_specs_pass_check_spec():
    """★ 正例①：4 个都过 `check_spec`。"""
    from tool_registry import check_spec
    specs = _specs()
    for n in NEW:
        assert n in specs, "★ 新工具没进 all_specs()：%s" % n
        check_spec(specs[n])


def test_four_new_specs_are_registered_and_unique():
    """★ 正例②：进 `all_specs()` 且无重名。"""
    names = [s.name for s in RC.all_specs()]
    for n in NEW:
        assert names.count(n) == 1, "★ %s 出现 %d 次（应为 1）" % (n, names.count(n))


def test_tool_count_at_least_base_plus_new():
    """★ 正例③：★ 工具数 **≥ 463 + 4 = 467**（★ **单调下界**，不是绝对数）——
    ★★ 教训（来自 batch103 那条）：★ 断言**绝对数**会被后续批次误红 ✗
    ⇒ ★ 不变量是「这 4 个都在、且都被认领」，★ 计数只用下界 ✓
    """
    assert len(RC.all_specs()) >= BASE_TOOL_COUNT + len(NEW), \
        "★ 工具数少于 %d + %d" % (BASE_TOOL_COUNT, len(NEW))


def test_no_bare_coordinate_params_in_new_specs():
    """★ 负例①：★ 新工具不许有裸坐标形参（规则 3）。"""
    bare = {"x", "y", "z", "x_mm", "y_mm", "z_mm"}
    for n in NEW:
        for p in _specs()[n].params:
            assert p.name.lower() not in bare, \
                "★ %s 的入参 %s 是裸坐标（规则 3 会拒）" % (n, p.name)


def test_ledger_levels_unchanged():
    """★ 负例②：★ 本规格不许把台账 `level` 抬高。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    got = {c.get("id"): c.get("level") for c in doc["capabilities"]}
    for cid, lvl in EXPECTED_LEVELS.items():
        assert got.get(cid) == lvl, \
            "★ 条目 %s 的 level 变成了 %r（应为 %r）—— ★ 暴露成功 ≠ 能力已验证" % (cid, got.get(cid), lvl)


def test_new_tools_are_claimed_by_a_ledger_entry():
    """★ 正例④（三件套第 2 件）：4 个都被某个台账条目认领。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    claimed = set()
    for c in doc["capabilities"]:
        claimed.update(str(t) for t in (c.get("mcp_tools") or []))
    for n in NEW:
        assert n in claimed, "★ %s 没有被任何台账条目认领（三件套缺一件）" % n


def test_all_views_tool_is_not_a_duplicate_of_current_sheet_tool():
    """★ 负例③：★ 「全图 + 4 项读数」与「当前图纸 + 名字/类型码」**两个都要在**，且名字不同。"""
    names = {s.name for s in RC.all_specs()}
    assert "solidworks_drawing_list_views" in names, "★ 既有的当前图纸版不见了（不该动它）"
    assert "solidworks_drawing_list_views_report" in names, "★ 全图版没挂上"

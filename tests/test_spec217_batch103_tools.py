"""★ 规格 217 · B1 的契约与负例：5 个「已实现但没暴露」的工具（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch103.py`）
# 文件:   tests/test_spec217_batch103_tools.py
# 定位:   ★ 规格 `specs/217-expose-orphans/` 的 **T-217-01（B1 前半）**。
#   ★ 起因：`tools/probe_unexposed_functions.py` ⇒ 公开函数 **1262** · 已暴露下界 **470** ·
#     **孤立 263** ⇒ 其中**首参可注入 53** ⇒ ★ 本批取 5 个（判据见 spec.md §四）✓
# 判据（★ 事实 62：门禁只靠负例证明）：
#   ★ 正例①：5 个 `ToolSpec` 全部过 `check_spec`
#   ★ 正例②：5 个都在 `all_specs()` 里且**无重名**
#   ★ 正例③：工具数 = 459 + 5 = **464**
#   ★ 正例④：5 个都**被某个台账条目的 `mcp_tools` 认领**（三件套第 2 件）
#   ★★ 负例①：★ 本轮**排除**的三个 `add_*_dimension` **不许**被暴露
#   ★★ 负例②：★ 5 个里**不许有裸坐标形参**（规则 3：名字也不许是 x/y/z）
#   ★★ 负例③：★ 台账 `level` **不许**被抬（★ 挂柜台定则 / 规格 204 的前车之鉴）
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

NEW = ("solidworks_count_sketch_relations",
       "solidworks_delete_all_sketch_relations",
       "solidworks_delete_sketch_relation",
       "solidworks_sketch_by_name")

#: ★★ `solidworks_sketch_intersect_curves` **撤出本批**（2026-10-07）——
#:   ★ 预选族门禁逐字判它「要求先选中相交的两条曲线，而没有任何选法」⇒ **门禁是对的** ✓
#:   ★ 它与 `add_*_dimension` 三条同类 ⇒ 一并挪到 **T-217-01b**（统一配声明式选择）✓
#:   ★★ 故本批 = **4 个**（★ 工具数 459 → **463**）✓

EXCLUDED = ("solidworks_add_horizontal_dimension",
            "solidworks_add_vertical_dimension",
            "solidworks_add_path_length_dimension")

BASE_TOOL_COUNT = 459

EXPECTED_LEVELS = {"sketch_edit_ops": "verified"}


def _specs():
    return {s.name: s for s in RC.all_specs()}


def test_five_new_specs_pass_check_spec():
    """★ 正例①：5 个都过 `check_spec`。"""
    from tool_registry import check_spec
    specs = _specs()
    for n in NEW:
        assert n in specs, "★ 新工具没进 all_specs()：%s" % n
        check_spec(specs[n])


def test_five_new_specs_are_registered_and_unique():
    """★ 正例②：进 `all_specs()` 且无重名。"""
    names = [s.name for s in RC.all_specs()]
    for n in NEW:
        assert names.count(n) == 1, "★ %s 出现 %d 次（应为 1）" % (n, names.count(n))


def test_tool_count_at_least_base_plus_new():
    """★ 正例③：★ 工具数 **≥ 459 + 4 = 463**（★ **单调下界**，不是绝对数）——
    ★★ 为什么改成下界：★ 我原先断言的是**绝对数**，★ 而后续批次（batch104）一加工具它就**误红** ✗
    ⇒ ★ 真正的**不变量**是「这 4 个都在、且都被认领」（另两条测试守它），★ 计数只用下界 ✓
    """
    assert len(RC.all_specs()) >= BASE_TOOL_COUNT + len(NEW), \
        "★ 工具数少于 %d + %d" % (BASE_TOOL_COUNT, len(NEW))


def test_excluded_dimension_tools_are_not_exposed():
    """★ 负例①：★ 排除的三个 `add_*_dimension` 不许被暴露（要配声明式选择才行）。"""
    names = {s.name for s in RC.all_specs()}
    for n in EXCLUDED:
        assert n not in names, "★ 不该暴露的却暴露了：%s" % n


def test_no_bare_coordinate_params_in_new_specs():
    """★ 负例②：★ 新工具不许有裸坐标形参（规则 3）。"""
    bare = {"x", "y", "z", "x_mm", "y_mm", "z_mm"}
    for n in NEW:
        for p in _specs()[n].params:
            assert p.name.lower() not in bare, \
                "★ %s 的入参 %s 是裸坐标（规则 3 会拒）" % (n, p.name)


def test_ledger_levels_unchanged():
    """★ 负例③：★ 本规格不许把台账 `level` 抬高。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    got = {c.get("id"): c.get("level") for c in doc["capabilities"]}
    for cid, lvl in EXPECTED_LEVELS.items():
        assert got.get(cid) == lvl, \
            "★ 条目 %s 的 level 变成了 %r（应为 %r）—— ★ 暴露成功 ≠ 能力已验证" % (cid, got.get(cid), lvl)


def test_new_tools_are_claimed_by_a_ledger_entry():
    """★ 正例④（三件套第 2 件）：5 个都被某个台账条目认领。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    claimed = set()
    for c in doc["capabilities"]:
        claimed.update(str(t) for t in (c.get("mcp_tools") or []))
    for n in NEW:
        assert n in claimed, "★ %s 没有被任何台账条目认领（三件套缺一件）" % n

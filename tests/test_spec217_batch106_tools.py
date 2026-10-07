"""★ 规格 217 · B5 收尾的契约与负例：最后 3 个纯暴露工具（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch106.py`）
# 文件:   tests/test_spec217_batch106_tools.py
# 定位:   ★ 规格 `specs/217-expose-orphans/` 的 **T-217-05（B5 收尾）**。
# 判据（★ 事实 62：门禁只靠负例证明）：
#   ★ 正例①：3 个都过 `check_spec` · 都在 `all_specs()` 且无重名
#   ★ 正例②：工具数 **≥ 469 + 3 = 472**（★ **单调下界** —— ★ 教训：绝对数会被后续批次误红）
#   ★ 正例③：3 个都被某个台账条目认领（三件套第 2 件）
#   ★★ 负例①：不许有裸坐标形参（规则 3）
#   ★★ 负例②：`pattern_and_mirror` 的 `level` 不许被抬（★ 该条无歧义故只查它；
#      ★ `assembly_read` 与 `assembly_and_mates` 的 `mcp_tools` 块**逐字相同** ⇒
#      ★ 悬挂点有歧义，故**不对这两条作 level 断言**，只查"名字被认领" ✓）
#   ★★ 负例③：★ **线性阵列"读数"与既有两个阵列"动作"必须同时存在且不同名** ✓
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

NEW = ("solidworks_linear_pattern_report",
       "solidworks_insert_mate_reference",
       "solidworks_assembly_iter_feature_tree")

BASE_TOOL_COUNT = 469

EXPECTED_LEVELS = {"pattern_and_mirror": "verified"}


def _specs():
    return {s.name: s for s in RC.all_specs()}


def test_three_new_specs_pass_check_spec():
    """★ 正例①：3 个都过 `check_spec`。"""
    from tool_registry import check_spec
    specs = _specs()
    for n in NEW:
        assert n in specs, "★ 新工具没进 all_specs()：%s" % n
        check_spec(specs[n])


def test_three_new_specs_are_registered_and_unique():
    """★ 正例①（后半）：进 `all_specs()` 且无重名。"""
    names = [s.name for s in RC.all_specs()]
    for n in NEW:
        assert names.count(n) == 1, "★ %s 出现 %d 次（应为 1）" % (n, names.count(n))


def test_tool_count_at_least_base_plus_new():
    """★ 正例②：工具数 ≥ 469 + 3 = 472（单调下界）。"""
    assert len(RC.all_specs()) >= BASE_TOOL_COUNT + len(NEW), \
        "★ 工具数少于 %d + %d" % (BASE_TOOL_COUNT, len(NEW))


def test_no_bare_coordinate_params_in_new_specs():
    """★ 负例①：不许有裸坐标形参（规则 3）。"""
    bare = {"x", "y", "z", "x_mm", "y_mm", "z_mm"}
    for n in NEW:
        for p in _specs()[n].params:
            assert p.name.lower() not in bare, \
                "★ %s 的入参 %s 是裸坐标（规则 3 会拒）" % (n, p.name)


def test_ledger_levels_unchanged():
    """★ 负例②：`pattern_and_mirror` 的 `level` 不许被抬（暴露成功 ≠ 能力已验证）。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    got = {c.get("id"): c.get("level") for c in doc["capabilities"]}
    for cid, lvl in EXPECTED_LEVELS.items():
        assert got.get(cid) == lvl, \
            "★ 条目 %s 的 level 变成了 %r（应为 %r）" % (cid, got.get(cid), lvl)


def test_new_tools_are_claimed_by_a_ledger_entry():
    """★ 正例③（三件套第 2 件）：3 个都被某个台账条目认领。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    claimed = set()
    for c in doc["capabilities"]:
        claimed.update(str(t) for t in (c.get("mcp_tools") or []))
    for n in NEW:
        assert n in claimed, "★ %s 没有被任何台账条目认领（三件套缺一件）" % n


def test_pattern_read_and_pattern_actions_coexist():
    """★ 负例③：★ 线性阵列「读数」与既有两个阵列「动作」必须同时存在且不同名。"""
    names = {s.name for s in RC.all_specs()}
    for n in ("solidworks_sketch_linear_pattern", "solidworks_circular_pattern",
              "solidworks_linear_pattern_report"):
        assert n in names, "★ 少了 %s（三者是建/读、线性/圆周，不是重复）" % n

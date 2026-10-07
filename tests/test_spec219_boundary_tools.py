"""★ 规格 219 · 边界凸台/边界曲面 的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch107.py`）
# 文件:   tests/test_spec219_boundary_tools.py
# 定位:   ★ 规格 `specs/219-user-coverage-100/` 的 **T-219-04**（★ 两个真缺口）。
# 判据（★ 事实 62：门禁只靠负例证明）：
#   ★ 正例①：2 个都过 `check_spec` · 都在 `all_specs()` 且**无重名**
#   ★ 正例②：工具数 **≥ 472 + 2 = 474**（★ 单调下界 —— ★ 绝对数会被后续批次误红）
#   ★ 正例③：2 个都被某个台账条目的 `mcp_tools` 认领（三件套第 2 件）
#   ★★ 负例①：★ **不许收坐标**（规则 3）—— 面由**面序号**指定
#   ★★ 负例②：★ **不许把 stitched 写成 verified** —— `surface_features` 的 `level` 不许被抬（红线⑥）
#   ★★ 负例③：★ 两个的**目标函数必须不同**（★ 各带自己的 `Type`）——
#      ★ 上一轮用 `derived_args` 字面 dict 被门禁判死 ⇒ 改成"一个 Type 一个函数"，
#      ★ 本测试就是那条教训的守夜人 ✓
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

BOSS = "solidworks_boundary_boss_report"
SURF = "solidworks_boundary_surface_report"
NEW = (BOSS, SURF)
BASE_TOOL_COUNT = 472


def _specs():
    return {s.name: s for s in RC.all_specs()}


def test_two_new_specs_pass_check_spec():
    """★ 正例①：2 个都过 `check_spec`。"""
    from tool_registry import check_spec
    specs = _specs()
    for n in NEW:
        assert n in specs, "★ 新工具没进 all_specs()：%s" % n
        check_spec(specs[n])


def test_two_new_specs_are_registered_and_unique():
    """★ 正例①（后半）：进 `all_specs()` 且无重名。"""
    names = [s.name for s in RC.all_specs()]
    for n in NEW:
        assert names.count(n) == 1, "★ %s 出现 %d 次（应为 1）" % (n, names.count(n))


def test_tool_count_at_least_base_plus_new():
    """★ 正例②：工具数 ≥ 472 + 2 = 474（单调下界）。"""
    assert len(RC.all_specs()) >= BASE_TOOL_COUNT + len(NEW), \
        "★ 工具数少于 %d + %d" % (BASE_TOOL_COUNT, len(NEW))


def test_no_bare_coordinate_params():
    """★ 负例①：★ 不许收坐标（规则 3）—— 面由**面序号**指定。"""
    bare = {"x", "y", "z", "x_mm", "y_mm", "z_mm"}
    for n in NEW:
        for p in _specs()[n].params:
            assert p.name.lower() not in bare, \
                "★ %s 的入参 %s 是裸坐标（规则 3 会拒）" % (n, p.name)


def test_level_not_raised_because_exposed():
    """★ 负例②：★ 暴露成功不许等于已验证 —— 真机还没跑 ⇒ `surface_features` 的 `level` 不许被抬 ✓"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    got = {c.get("id"): c.get("level") for c in doc["capabilities"]}
    assert got.get("surface_features") == "verified", \
        "★ surface_features 的 level 变了：%r" % got.get("surface_features")


def test_two_tools_point_at_different_functions():
    """★ 负例③：★ 两个工具的目标函数**必须不同**（★ 各带自己的 `Type`）——
    ★ 上一轮 `derived_args` 字面 dict 被门禁判死 ⇒ 教训的守夜人 ✓"""
    specs = _specs()
    fb = specs[BOSS].function
    fs = specs[SURF].function
    assert fb != fs, "★ 两个工具指向了同一个函数：%r（★ 那 Type 就没区分开）" % fb
    assert "boss" in fb and "surface" in fs, "★ 函数名与 Type 对不上：%r / %r" % (fb, fs)


def test_both_tools_are_claimed():
    """★ 正例③（三件套第 2 件）：2 个都被某个台账条目认领。"""
    import yaml
    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    claimed = set()
    for c in doc["capabilities"]:
        claimed.update(str(t) for t in (c.get("mcp_tools") or []))
    for n in NEW:
        assert n in claimed, "★ %s 没有被任何台账条目认领（三件套缺一件）" % n

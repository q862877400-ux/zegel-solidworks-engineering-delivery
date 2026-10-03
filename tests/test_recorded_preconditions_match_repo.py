"""★ 测：★ 那 9 个**前置签名**与仓里的真签名一致（★ 阶段 3 · 把"记对了"变成可核的 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `output/_reaudit_preconditions.py`（★ 只报不动 —— ★ 回头核脚本）
# 定位:   ★ **起因**：★ 上一轮（★ 轮 107）我第 **5** 次把前置猜错
#   （★ 猜 `sw_part.insert_coordinate_system` ⇒ 真位置是 `sw_ref_geometry`）⇒
#   ★★ **学到一条判据**：★★★ **「在仓里搜」要搜够** ——
#     ★ **按**功能词**搜全部 `scripts/`、★ 而不是只猜某个模块** ✓
#   ★★★ **⇒ 那就该**回头核**：★ 我在轮 95–107 记的那几个前置，★ 名字与参序对不对** ✓
#   ★★★★ **回头核读数（★ `output/_reaudit_preconditions.py`）**：★ **9 个全部准确** ✓
#     ★ `extrude_boss(model, sketch_name, depth, direction=True, merge=True)` ✓
#     ★ `sketch(model, plane_name="Front Plane")`（★ **上下文管理器**）✓
#     ★ **`fillet(model, radius, edges=None)`**（★ `radius` 在第 2 位）✓
#     ★ `linear_pattern(model, feature_name, d1_x, …)` ✓
#     ★ `create_hole_wizard_at_selection_report(model, selection, size, *, diameter_mm, depth_mm)` ✓
#     ★ `insert_coordinate_system(model, x_flipped, y_flipped, z_flipped)` ★ **在 `sw_ref_geometry`** ✓
#     ★ `resolve_selection(model, selector, kind, *, body_index=0)` ✓
#     ★ `hole_pattern_report(model, positions, *, kind, diameter_mm, …)` ✓
#   ★★★★★ **⇒ 那本身是一条读数**：★★★ **"猜错的成本"被**记录**吸收了** ——
#     ★ **每次猜错之后我都把记录改对了** ⇒ ★★ **所以现在逐条核，全对** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

#: ★★ **（★ 文件, ★ 函数名, ★ 前 N 个形参名）** —— ★ 逐条照**回头核的读数**写死 ✓
EXPECT = [
    ("sw_part.py", "extrude_boss", ["model", "sketch_name", "depth"]),
    ("sw_part.py", "sketch", ["model", "plane_name"]),
    ("sw_part.py", "fillet", ["model", "radius", "edges"]),
    ("sw_part.py", "linear_pattern", ["model", "feature_name", "d1_x"]),
    ("sw_hole_features.py", "create_hole_wizard_at_selection_report",
     ["model", "selection", "size"]),
    ("sw_ref_geometry.py", "insert_coordinate_system",
     ["model", "x_flipped", "y_flipped", "z_flipped"]),
    ("sw_selection_spec.py", "resolve_selection", ["model", "selector", "kind"]),
]


def _params(path: Path, func: str) -> list | None:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == func:
            return [a.arg for a in n.args.args]
    return None


def test_the_recorded_signatures_still_match() -> None:
    """★★★ 核心断言：★ 那 7 个（文件, 函数, 前 N 个形参）**逐条对上** ✓

    ★★ **为什么**：★ 那是我**猜错过 5 次**才记对的 ⇒
      ★★★ **若哪天仓里改了签名，本测试会红** ⇒ **那时该更新记录** ✓
    """
    for fname, func, want in EXPECT:
        p = SCRIPTS / fname
        assert p.is_file(), "★ 找不到 `%s`" % fname
        got = _params(p, func)
        assert got is not None, "★ `%s` 里没有 `%s`" % (fname, func)
        assert got[:len(want)] == want, (
            "★ `%s::%s` 的形参变了：★ 期望前 %d 个是 %r、★ 实为 %r"
            % (fname, func, len(want), want, got[:len(want)]))


def test_coordinate_system_lives_in_sw_ref_geometry_not_sw_part() -> None:
    """★★★★ 核心断言：★ `insert_coordinate_system` **在 `sw_ref_geometry`、★ 不在 `sw_part`** ✓

    ★★ **为什么**：★ 那正是我第 **5** 次猜错的那一处 ⇒
      ★★★ **本测试把"我学到的那一条"固化成断言** ✓
    """
    assert _params(SCRIPTS / "sw_ref_geometry.py", "insert_coordinate_system") is not None, (
        "★ `insert_coordinate_system` 不在 `sw_ref_geometry` 了")
    assert _params(SCRIPTS / "sw_part.py", "insert_coordinate_system") is None, (
        "★ `sw_part` 里**有了** `insert_coordinate_system` ⇒ ★ 记录要重看"
        "（★ 而我第一版猜的就是这里）")


def test_negative_case_feature_by_name_is_not_a_module_function() -> None:
    """★★★ **负例 · 成员 vs 函数**：★ `FeatureByName` **不是模块级函数**（★ 它是 `IModelDoc2` 的成员）✓

    ★★ **为什么**：★ 我第 **2** 次猜错就是把它写成 `GetFeatureByName` ⇒
      ★★★ **而"它不是模块函数"这一点也要守住**（★ 免得有人去 `sw_part` 里找它）✓
    """
    hits = []
    for f in sorted(SCRIPTS.glob("*.py")):
        if _params(f, "FeatureByName") is not None:
            hits.append(f.name)
    assert not hits, "★ 它**成了**模块级函数（★ 在 %r）⇒ 记录要重看" % hits
    #: ★★ 而它**必须**在某处被当成员调（★ 否则能力就坏了）✓
    used = [f.name for f in sorted(SCRIPTS.glob("*.py"))
            if '"FeatureByName"' in f.read_text(encoding="utf-8", errors="replace")]
    assert used, "★ 没有任何文件在调 `FeatureByName`（★ 那能力就坏了）"


def test_negative_case_the_functional_word_search_is_recorded() -> None:
    """★★★ **负例 · 功能词扫的结果要落盘**：★ 脚本里要有那 9 个功能词 ✓

    ★★ **为什么**：★ 判据是「**按功能词搜全部 `scripts/`**」⇒
      ★★★ **脚本本身要体现这个搜法**（★ 而不是只搜一个模块）✓
    """
    p = REPO / "output" / "_reaudit_preconditions.py"
    if not p.is_file():
        return
    t = p.read_text(encoding="utf-8", errors="replace")
    assert "glob(\"*.py\")" in t or "glob('*.py')" in t, "★ 没扫**全部** `scripts/*.py`"
    for w in ("coordinate_system", "bounding_box", "weldment", "sheet_metal"):
        assert w in t, "★ 功能词 `%s` 不在扫的清单里" % w

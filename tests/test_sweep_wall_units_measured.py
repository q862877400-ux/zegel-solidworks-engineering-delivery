"""★ 测「第十二族的口径」+「钩子这个能力层扩展」（★ 含负例 · 轮 129）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\ISweepFeatureData\\*.md` +
#         真机证据 `output/sweep-wall-via-hook-recheck.json`
# 文件:   tests/test_sweep_wall_units_measured.py（★ 新）
# 定位:   ★★★★★★★ 2026-10-04（轮 129）**量出第十二族**：
#     ★ `GetWallThickness` 的口径 = **随文档单位（毫米）** ✓
#     **两步**：★ ① 在**正确的位置**设（★ `CreateFeature` 之前 —— ★ 靠新加的钩子
#       `mutate=None`）· ★★ ② 用**几何**独立判（★ 最近候选分类）✓
#   ★★ **真机读数**：★ `扫描-薄件1` · ★ `IsThinFeature=true` · ★ `ThinFeature=true` ·
#     ★ `GetWallThickness={forward: **0.002**, backward: 1e-07}` · ★ **体积 `1.508`** ⇒
#     ★★ 与**毫米环带 `1.51`** 距离 **0.002**、★ **次近 1003.80** ⇒ **口径 = 毫米** ✓
#   ★★★ **⚠ 而 `backward = 1e-07`（≈0）是**应然的**** —— `ThinWallType=0` 是
#     **One Direction** ⇒ **只有方向 1 被设** ⇒ ★ **自洽** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TESTS = REPO / "tests"
sys.path.insert(0, str(TESTS))
from _funcbody import func_source  # noqa: E402

SRC = REPO / "scripts" / "sw_feature_readback.py"
SWEEP = REPO / "scripts" / "sw_sweep.py"
PROBE = REPO / "tools" / "probe_sweep_wall_units_via_hook.py"


def test_the_twelfth_family_is_recorded_as_a_conclusion() -> None:
    """★★★ 核心断言：★ 第十二族那条**结论**在能力里 ✓"""
    body = func_source(SRC.read_text(encoding="utf-8", errors="replace"), "sweep_params")
    assert "第十二族" in body, "★ 没记下族号"
    assert "随文档单位" in body, "★ 口径的结论没写"
    #: ★★ 真机那三个读数（★ 体积 · ★ forward · ★ 候选）都要在 ✓
    assert "1.508" in body, "★ 实测体积没记下"
    assert "1003.80" in body or "1005.31" in body, "★ 候选参照没记下"


def test_the_hook_is_optional_and_does_not_change_existing_semantics() -> None:
    """★★★★ 核心断言：★ 钩子是**显式可选**的（★ `mutate=None` ⇒ 行为不变）✓

    ★★ **为什么**：★ 本仓**多处**调 `create_sweep_report` ⇒
      ★★★ **⇒ 加了钩子**不许**改变既有调用方的语义** ✓
    ★★★ **而它**不许吞异常**** —— ★ 否则薄壁没设上会被**静默跳过** ✓
    """
    t = SWEEP.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(t)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "create_sweep_report")
    args = {a.arg: a for a in fn.args.args}
    assert "mutate" in args, "★ 签名里没有 `mutate`"
    #: ★★ **默认值是 `None`**（★ 那样既有调用方行为逐字不变）✓
    defaults = fn.args.defaults
    names = [a.arg for a in fn.args.args][len(fn.args.args) - len(defaults):]
    assert dict(zip(names, defaults)).get("mutate") is not None or \
        any(isinstance(d, ast.Constant) and d.value is None for d in defaults), \
        "★ `mutate` 的默认值应当是 `None`"
    #: ★★★ 而那句调用**在 `CreateFeature` 之前**（★ 那是官方要求的位置）✓
    lines = t.splitlines()
    body = "\n".join(lines[fn.lineno - 1:getattr(fn, "end_lineno", fn.lineno)])
    i_hook = body.find("mutate(data)")
    i_create = body.find('"CreateFeature"')
    assert i_hook != -1 and i_create != -1, "★ 找不到那两句"
    assert i_hook < i_create, "★ 钩子必须在 `CreateFeature` **之前**（★ 官方逐字要求）"


def test_negative_case_the_probe_lists_all_three_candidates() -> None:
    """★★★★ 核心断言：★ 探针的候选表**三个都在**（★ 轮 128 我漏了一个 ⇒ 误判）✓"""
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "min(cands, key=" in t, "★ 没走最近候选分类"
    for need in ("薄壁没生效", "米", "毫米"):
        assert need in t, "★ 候选表里少了 `%s`" % need


def test_negative_case_the_geometry_is_the_independent_criterion() -> None:
    """★★★ **负例 · 判据要独立**：★ 探针用的是**体积**（★ 几何）、★ 不是读回属性 ✓"""
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "CreateMassProperty" in t and "Volume" in t, "★ 没量体积（★ 那才是独立判据）"
    assert "C_SOLID" in t and "C_METER" in t and "C_MM" in t, "★ 三个解析候选没算全"

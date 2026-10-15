"""★ spec 290：**核销「12 条接线」** —— ★ 12 条封装**零生产调用点** ⇒ ★ 按 266 的同一判断：**不值**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   specs/266-counted-positions-impact/acceptance.md（★ 判「改口径**不值**」）
#         specs/289-arity-change-route-decision/acceptance.md（★ 拍板乙 · ★ 改动面 2 处 × 3 模块）
#         scripts/sw_simulation.py:348/355/364（★ ★★ **生产路径已直接传 `out_i4()`** ✓）
#         scripts/sw_simulation_loads.py:251（★ ★★ 逐字：「**由本函数统一补 `out_i4()`**（★ **一处修改 ⇒ 整批 `Add*` 全受益**）」= **乙方案的先例**）
# 定位:   ★★ 287/288/289 把「怎么改」量清了 ⇒ ★ 本轮**量「值不值得改」**：★ **数生产调用点**。
# 官方依据: 不适用（本项目内部决策）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 现场扫源码；★ 本文件不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **12 条对应的封装函数**（★ 逐字来自各模块的 `def`）。
WRAPPERS = {
    "sw_simulation_results.py": ("create_plot", "create_deformed_body",
                                 "get_displacement_at_points", "get_buckling_load_factors",
                                 "get_mesh_node_location", "get_mesh_element_location"),
    "sw_simulation_study.py": ("create_study", "create_study_v2", "create_study_v3",
                               "duplicate_study", "convert_study"),
    "sw_pdm.py": ("get_bom_start_number",),
}
#: ★★★ **生产路径**（★ `sw_simulation.py`）**已经**传 `out_i4()` 的三处。
PRODUCTION_OK = ("sw_simulation.py:348", "sw_simulation.py:355", "sw_simulation.py:364")
#: ★★★ **核销理由**（★ 与 **266** 同一判断）。
VERDICT = ("核销 —— 12 条封装**零生产调用点** ⇒ 接线对**运行期无影响**；"
           "对**静态门禁**只影响一个**只计数、不判罪**的桶 ⇒ 与 266 同一判断：**不值**")


def _production_calls() -> dict:
    """★ 现场数：每个封装的**生产调用点**（★ 排除**定义**与**注释**）。"""
    files = ([p for p in (ROOT / "scripts").glob("*.py")]
             + [p for p in (ROOT / "mcp-server").glob("*.py")]
             + [p for p in (ROOT / "tools").glob("*.py")])
    out = {}
    for mod, fns in WRAPPERS.items():
        for fn in fns:
            n = 0
            for p in files:
                if p.name == mod:
                    continue
                src = p.read_text(encoding="utf-8", errors="replace")
                for m in re.finditer(r"\b%s\s*\(" % re.escape(fn), src):
                    ln = src[:m.start()].count("\n")
                    line = src.splitlines()[ln].lstrip()
                    if line.startswith("#") or line.startswith("def "):
                        continue
                    n += 1
            out[fn] = n
    return out


def _failures(calls, prod_ok, verdict, src) -> list[str]:
    """★ 纯函数：① 每个封装都数到（★ 检查量非 0）；② **全部为 0**；③ 生产路径 3 处；④ 结论是「核销」。"""
    bad: list[str] = []
    if len(calls) != 12:
        bad.append("★ 应数 12 个封装，实测 %d" % len(calls))
    nz = {k: v for k, v in calls.items() if v}
    if nz:
        bad.append("★ 这些封装**有**生产调用点：%s" % sorted(nz))
    if len(prod_ok) != 3:
        bad.append("★ 生产路径应有 3 处，实测 %d" % len(prod_ok))
    if "核销" not in verdict:
        bad.append("★ 结论应是「核销」")
    if "只计数、不判罪" not in verdict:
        bad.append("★ 理由里要写明「`arity` 桶只计数、不判罪」")
    if not src:
        bad.append("★ 回源码核失败：`sw_simulation.py` 里找不到 `out_i4()`")
    return bad


# ── ① ★★★ **12 条封装零生产调用点** ──────────────────────────────
def test_all_twelve_wrappers_have_no_production_callers():
    """★★★ 现场扫 `scripts/` + `mcp-server/` + `tools/`：★ **12 个封装**（★ 3 个模块）
    ⇒ ★★ **生产调用点全部为 0** ⇒ ★★★ **接线对**运行期**毫无影响**（★ 没有东西会调它们）。
    """
    calls = _production_calls()
    assert len(calls) == 12, "★ 应数 12 个，实测 %d" % len(calls)
    nz = {k: v for k, v in calls.items() if v}
    assert not nz, "★ 这些**有**生产调用点（★ 那接线就有价值了）：%s" % nz


# ── ② ★★★ **生产路径已经是对的** ─────────────────────────────────
def test_the_production_path_is_already_correct():
    """★★★ 回源码核：★ `scripts/sw_simulation.py` **直接**调 `CreateNewStudy3` / `2` / `1` 时
    ★ **已经**传 `out_i4()`（★ 三处）⇒ ★★ **生产路径是对的** ✓
    ⇒ ★ 那 12 条的「接线」**只是**让**未被调用**的封装也对 —— ★ **不是**修一个真 bug。
    """
    src = (ROOT / "scripts" / "sw_simulation.py").read_text(encoding="utf-8", errors="replace")
    assert "out_i4()" in src, "★ 找不到 `out_i4()`"
    for name in ("CreateNewStudy3", "CreateNewStudy2", "CreateNewStudy"):
        #: ⚠ 别用 `[^)]*` —— ★ 中间有 `int(study_type)` 这种**带右括号**的实参 ⇒ ★ 会**跨不过去** ✗
        m = re.search(r'"%s",[\s\S]{0,200}?out_i4\(\)' % name, src)
        assert m, "★ `%s` 的生产调用点**没有**传 `out_i4()`" % name


# ── ③ ★★ **乙方案有先例**（★ 别的模块已经这么做过） ──────────────
def test_the_b_route_has_a_precedent():
    """★★ `scripts/sw_simulation_loads.py:251` 逐字：「★★ 修法：★ **由本函数统一补 `out_i4()`**
    （★ **一处修改 ⇒ 整批 `Add*` 全受益**）」⇒ ★★ **那正是乙方案的**思想**，★ 且**已经在别处落地过** ✓
    ⇒ ★ 所以「乙」不是新发明（★ 但也说明：★ **要改的话，改法是现成的**）。
    """
    src = (ROOT / "scripts" / "sw_simulation_loads.py").read_text(encoding="utf-8", errors="replace")
    assert "统一补 `out_i4()`" in src or "统一补" in src, "★ 找不到「统一补 `out_i4()`」那句"
    assert "全受益" in src, "★ 找不到「全受益」"


# ── ④ ★★★ **核销理由**（★ 与 266 同一判断） ──────────────────────
def test_the_verdict_matches_266():
    """★★★ **核销** —— ★ 理由两条：
    ★ ① 12 条封装**零生产调用点** ⇒ ★ **接线对运行期无影响**；
    ★ ② 对**静态门禁**只影响 **`arity` 桶** ⇒ ★ 而它**只计数、不判罪**
    ⇒ ★★ 与 **266**（★「改口径**不值**」）**同一判断** ✓
    """
    assert "核销" in VERDICT
    assert "只计数、不判罪" in VERDICT
    assert "266" in VERDICT


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 封装数不对；② 某个有生产调用点；③ 生产路径不是 3 处；④ 结论不是「核销」；⑤ 理由缺「只计数」。"""
    good = "…out_i4()…"
    calls0 = {f: 0 for fns in WRAPPERS.values() for f in fns}
    args = (calls0, PRODUCTION_OK, VERDICT, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({k: v for k, v in list(calls0.items())[:5]}, PRODUCTION_OK, VERDICT, good), \
        "封装数不对却未判出"
    assert _failures({**calls0, "create_study": 3}, PRODUCTION_OK, VERDICT, good), \
        "某个有生产调用点却未判出"
    assert _failures(calls0, ("a",), VERDICT, good), "生产路径不是 3 处却未判出"
    assert _failures(calls0, PRODUCTION_OK, "继续改", good), "结论不是「核销」却未判出"
    assert _failures(calls0, PRODUCTION_OK, "核销 —— 因为不好", good), "理由缺「只计数」却未判出"

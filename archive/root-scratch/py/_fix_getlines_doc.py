import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 修 get_lines 的 docstring：把**实测的返回语义**写进去
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch.py")
t = P.read_text(encoding="utf-8")
OLD = '''def get_lines(sketch) -> list[Any]:
    """直线。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetLines2(swCrossHatchFilter_e)` ——
    官方已把 `GetLines` 标 **Obsolete**（见 `docs/obsolete-member-candidates.md`）。
    ⚠ 它是**唯一多一个参数**的后继：默认 `swCrossHatchInclude`（含剖面线），
    与旧 `GetLines()` 的「都取」语义一致。
    """'''
NEW = '''def get_lines(sketch) -> list[Any]:
    """⚠⚠ **返回的是「数值数组」，不是「线对象列表」** —— 实测（2026-10-01 轮 140）。

    ★★ **实测语义**（`tools/probe_getlines_count.py`，真机 SW 2026 SP4.1）：

        | 草图里有几条直线 | `get_sketch_segments` | `get_lines` |
        |---|---|---|
        | 1 | 1 | **12** 个 `float` |
        | 2 | 2 | **24** |
        | 3 | 3 | **36** |

    ⇒ **每条直线占 12 个 `float`**（`get_lines(...)[0]` 的类型是 `float`，不是 `Dispatch`）
    ⇒ **不能**把结果当线对象用（没有 `.X` / `.GetStartPoint2`）。
    ⚠ **要「几条线」用 `get_sketch_segments(sketch)` 再按类型筛**；
    要「线的几何」用 `ISketchSegment` 上的方法（本模块另有包装）。

    ⚑ 2026-10-01（轮 111）：改用**后继** `GetLines2(swCrossHatchFilter_e)` ——
    官方已把 `GetLines` 标 **Obsolete**（见 `docs/obsolete-member-candidates.md`）。
    ⚠ 它是**唯一多一个参数**的后继：默认 `swCrossHatchInclude`（含剖面线），
    与旧 `GetLines()` 的「都取」语义一致。
    ⚠ 这条「12 个 float / 条」是**实测**的，**官方文档没写**返回结构。
    """'''
if "返回的是「数值数组」" not in t:
    assert OLD in t, "get_lines docstring 锚点不符"
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已改写 get_lines 的 docstring（写明实测语义）")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ② 强化既有冒烟的判据：从「非空」换成「定量 N×12」
Q = Path(r"C:\swprojects\sw-skill-fork\tools\verify_sketch_getters_smoke.py")
tq = Q.read_text(encoding="utf-8")
i = tq.find('chk("★★ 画了线 ⇒ get_lines **非空**')
if i >= 0:
    j = tq.index("\n", tq.index(")", i))
    print()
    print("  ── 既有判据（弱）──")
    for k in range(tq[:i].count(chr(10)), tq[:j].count(chr(10)) + 1):
        print("    %s" % tq.splitlines()[k][:100])
    print()
    print("  ⚠ 该判据只查「非空」⇒ **12 对 1 也照样绿** ⇒ 本轮不改它（它是轮 117 的产物），")
    print("     而是**新增**一条定量判据到契约测试里（见 tests/test_sw_sketch_contract.py）。")

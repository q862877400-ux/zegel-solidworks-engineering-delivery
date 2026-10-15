import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           221 🎯 **Spec Kit `029`：官方废弃成员探针 —— 量了，但结论是「做不成门禁」**（轮 110）——
               起因：连着两轮（`024`/`028`）撞上「官方旧入口已废弃、我们照抄了旧的」，
               而 `025` 的门禁只管**值**、管不了这个 ⇒ 想补一道。
               探针抽代码里 `get_com_member(..., "<成员>")` 的 **429** 个成员名，
               去官方文档找同名、带 `Obsolete` 的 ⇒ **38 条候选**。
            222 ★★ **结论：补不了** ——
               ```
               已核实为真    8 条
               已核实假阳性 10 条
               未逐条核     20 条
               ⇒ 假阳性率 ≥ 26%（10/38），剩余大半里还会有一批
               ```
               **根因是「同名不同接口」**：`GetMassProperties` 在 `IModelDoc2` 上废弃、
               在 `IModelDocExtension` 上**没废弃** —— 而我们用的**正是后者**
               （文档写的「后继」就是它）。同理 `GetRenderMaterials`（文档在 `IComponent2`，
               我们用 extension 且**实测可跑**）、`Add2`/`Delete`（文档在 `ICustomPropertyManager`，
               我们用 **`IEquationMgr`**，**未废弃**）。
               ⚠ 与**已知事实 36**（同名接口分属不同族）同一类。
               ★ **假阳性率 26%+ 的门禁不能当门禁** —— 它会让人去改**本来正确**的代码。
            223 ★ **但它确实查出了真东西**：**8 条**官方已标废弃、而我们仍在调 ——
               最集中的是 **`sw_sketch.py` 的 6 个 `ISketch` 取法**
               （`GetLines`/`GetArcs`/`GetEllipses`/`GetParabolas`/`GetSketchPoints`/`GetUserPoints`）；
               该模块 docstring 明写「**ISketch 完整封装**」⇒ 归属没有疑问。
               另两条：`AddMate5`（`IAssemblyDoc`）· `GetBodies2`（`IComponent2`）。
               ⚠ **但这不等于它们跑不通** —— 本台账只证「官方标了废弃」。
               ★ **两件事必须分开说**：「官方标了废弃」本轮**已证**；「这些调用会坏」本轮**未证**。
            224 ⚑ **收场方式变了**：这次我**没有**试图把假阳性"修掉"、也没有降级成
               "弱启发式硬凑"（事实 53），而是**直接放弃做成门禁**，把结论降级成
               **人工复核台账** `docs/obsolete-member-candidates.md`（**不拦发布**）。
               ★ **这可能是更正确的一种收场。**
            225 ⚑ **未查证**：那 8 条**能不能跑**（**未测**）；剩余 **20 条未逐条核**；
               探针**只扫 `get_com_get_member(...)` 一种调用形态**；
               `sw_sketch.py` 那 6 个取法**要不要换 `*2`** —— **未决**（换了要重测整个模块）。
               回归 **1084 passed**。
               下轮候选：① 评估 `sw_sketch.py` 换 `*2` 的代价；② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+221 ", before, re.M):
    print("  游标 221 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+225 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 225 行已存在 ✓")

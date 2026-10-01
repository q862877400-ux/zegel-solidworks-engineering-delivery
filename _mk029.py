import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\029-obsolete-member-ledger")
S.mkdir(parents=True, exist_ok=True)

spec = """# 029 · 「官方已废弃但我方仍在调」—— 量了，但**做不成门禁**

**Status**: Implemented（轮 110）

## 背景
连着两轮撞上同一类坑（`024` 的 `SketchChamfer` · `028` 的 `Add`）：
> **官方把旧入口标 Obsolete、并给了后继，而我们照抄了旧的那个。**

★ 而 `025` 那道门禁只管**值**，**管不了「你用的是不是废弃入口」**。
⇒ 本轮把这件事量出来。

## 做法
`tools/probe_obsolete_members.py`（只读）：
1. 抽代码里 `get_com_member(<目标>, "<成员>")` 的成员名 —— **429 个**；
2. 去 `C:\\swapi\\types\\**\\<成员>.md` 找同名官方文档；
3. 文档正文带 `Obsolete` 的列出来，并打印 `Superseded by` 指向谁。

## 结果：**38 条候选**，但**假阳性太多**
```
已核实为真    8 条
已核实假阳性 10 条
未逐条核     20 条
⇒ 假阳性率 ≥ 26%（10/38），剩余大半里还会有一批
```

## ★ 必核实为真的 8 条
| 成员 | 官方接口 | 后继 | 我们在哪 |
|---|---|---|---|
| `GetLines` / `GetArcs` / `GetEllipses` / `GetParabolas` / `GetSketchPoints` / `GetUserPoints` | `ISketch` | 各自的 `*2`（`GetEllipses3`）| `sw_sketch.py` |
| `AddMate5` | `IAssemblyDoc` | `IAssemblyDoc::CreateMate` | `sw_assembly_doc.py` |
| `GetBodies2` | `IComponent2` | `IComponent2::GetBodies3` | `sw_assembly.py` 等 4 处 |

★ 其中最集中的一簇是 **`sw_sketch.py` 的 6 个 `ISketch` 取法** ——
该模块 docstring 明写「**ISketch 完整封装**」⇒ 归属没有疑问。

## ★★ 为什么**不能**做成门禁（这才是本轮的主要结论）
假阳性来自**同名不同接口**：
```
GetMassProperties   在 IModelDoc2 上废弃 · 在 IModelDocExtension 上**没废弃**
                    —— 而我们用的正是后者（文档写的「后继」就是它）
GetRenderMaterials  文档在 IComponent2 · 我们用 IModelDocExtension（且实测可跑）
Add2 / Delete       文档在 ICustomPropertyManager · 我们用 **IEquationMgr**（未废弃）
Name / GetModelDoc  —— 我们也调了 *2，后继已在用
```
⇒ **光有成员名判不出"我们调的是哪个接口上的"**。
⚠ 这与**已知事实 36**（同名接口分属不同族，用错接口 = 对象对任何成员都没反应）**同一类**。

## 判据
| ID | 判据 |
|---|---|
| SC-2501 | 探针可跑，输出候选 + `Superseded by` |
| SC-2502 | ★ 逐条消歧：**「我们是否也调了后继」**（25 条自动判）+ 人工核 |
| SC-2503 | ★ **确认为真的 8 条**逐条给依据（不是只给个数）|
| SC-2504 | ★ **已核实的 10 条假阳性**逐条说明为什么误报 |
| SC-2505 | ★ **明写「不能做成门禁」及理由**（假阳性率）|
| SC-2506 | 落成台账 `docs/obsolete-member-candidates.md`，**不拦发布** |
| SC-2507 | 门禁 + 回归不退化（回归 **1084 passed**）|

## ⚠ 未查证
* 那 8 条**能不能跑** —— **未测**（本台账只证「官方标了废弃」，**不证「跑不通」**）；
* 剩余 **20 条未逐条核**；
* 探针**只扫 `get_com_member(...)` 一种调用形态**，其它形态未扫。
"""

plan = """# 029 · Plan

## 步骤
1. 写只读探针：抽调用的成员名 → 找同名官方文档 → 带 `Obsolete` 的列出来
2. 跑一次 ⇒ **38 条候选**
3. ★ 自动消歧：「我们是否**也调了后继**」⇒ 7 条确定为假阳性
4. ★ 抽查高价值条目 ⇒ **更多假阳性**（`GetMassProperties` / `GetRenderMaterials` /
   `Add2` / `Delete` / `Name` / `GetModelDoc` …）
5. ★ 核实 8 条**真**的（含 `sw_sketch.py` 的 6 个 `ISketch` 取法，归属有 docstring 佐证）
6. ⇒ **结论：做不成门禁**（假阳性 ≥26%）⇒ 落成**人工复核台账**
7. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **把探针的命中当缺陷清单** | ★ 抽查即发现大量**同名不同接口**的假阳性 ⇒ 不据此改代码 |
| 把"官方标废弃"当成"跑不通" | 台账里**明写**这两件事不是一回事（类比已知事实 40）|
| 硬做成门禁 ⇒ 天天误报 | ★ **不做门禁**，并把「为什么不做」写进台账 |
| 只给个数不给依据 | 8 条真 / 10 条假阳性**逐条**给依据 |
"""

tasks = """# 029 · Tasks（全部完成，轮 110）

- [x] T-2501 写 `tools/probe_obsolete_members.py`（只读）
  `→ 验收:` `python tools/probe_obsolete_members.py`
- [x] T-2502 跑 ⇒ **38 条候选**
- [x] T-2503 ★ 自动消歧（是否也调了后继）⇒ 7 条假阳性
- [x] T-2504 ★ 抽查高价值条目 ⇒ `GetMassProperties` / `GetRenderMaterials` /
       `Add2` / `Delete` / `Name` / `GetModelDoc` 等**均为假阳性**
- [x] T-2505 ★ 核实 **8 条为真**（`sw_sketch.py` 的 6 个 `ISketch` 取法 + `AddMate5` + `GetBodies2`）
- [x] T-2506 落台账 `docs/obsolete-member-candidates.md`（**不拦发布**）
  `→ 验收:` `Select-String docs\\obsolete-member-candidates.md -Pattern '不能.*做成门禁'`
- [x] T-2507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 029 · Converge

**Converged**: 2026-10-01（轮 110）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2501 探针可跑 | ✅ 429 个调用成员 → 38 条候选 |
| SC-2502 逐条消歧 | ✅ 自动（25 条）+ 人工 |
| SC-2503 确认为真的 8 条 | ✅ 逐条给依据 |
| SC-2504 已核实的 10 条假阳性 | ✅ 逐条说明 |
| SC-2505 明写「不能做成门禁」 | ✅ 假阳性率 ≥26% |
| SC-2506 落台账、不拦发布 | ✅ `docs/obsolete-member-candidates.md` |
| SC-2507 门禁 + 回归 | ✅ `release_check` exit 0 · **1084 passed** |

## 二、★ 本轮**本该**加一道门禁，结论却是「加不了」
```
起因：连着两轮（024/028）撞上「官方旧入口已废弃、我们照抄了旧的」
      —— 而 025 的门禁只管值，管不了这个 ⇒ 想补一道。
结论：**补不了** —— 38 条候选里已核实 **10 条是假阳性**（≥26%），
      根因是**同名不同接口**：`GetMassProperties` 在 `IModelDoc2` 上废弃、
      在 `IModelDocExtension` 上没废弃，而我们用的正是后者。
```
★ ⇒ **一个假阳性率 26%+ 的门禁不能当门禁**（事实 62 的反面：
门禁**写了但不该拦** 也是一种失败 —— 它会让人去改本来正确的代码）。

## 三、★ 但它**确实**查出了真东西
**8 条**官方已标废弃、而我们仍在调 —— 其中最集中的是
**`sw_sketch.py` 的 6 个 `ISketch` 取法**（`GetLines` / `GetArcs` / `GetEllipses` /
`GetParabolas` / `GetSketchPoints` / `GetUserPoints`）。
该模块 docstring 明写「**ISketch 完整封装**」⇒ 归属**没有疑问**。

⚠ **但这不等于它们跑不通** —— 本台账只证「官方标了废弃」。
（类比**已知事实 40**：`Create*Surface` 族废弃 ≠ 立刻失效。）
★ **两件事必须分开说**：
```
「官方标了废弃」  —— 本轮**已证**（8 条）
「这些调用会坏」  —— 本轮**未证**（也没测）
```

## 四、这是这个项目的**第五次**同一教训
```
020 / 021 / 022   核样：按名字的分档，四档全要打折
027   探针：连着两版假阳性
029   探针：38 条里已核实 10 条假阳性 —— ⇒ 不成门禁
⇒ **按名字做的自动检查，在这个项目里反复产生假阳性。**
```
★ 但 `029` 与前面几轮有个**不同之处**：这次我**没有**试图把假阳性"修掉"、
也没有降级成"弱启发式硬凑"（事实 53），而是**直接放弃做成门禁**，
把结论降级成**人工台账**。**这可能是更正确的一种收场。**

## 五、未查证
* 那 8 条**能不能跑** —— **未测**；
* 剩余 **20 条未逐条核**；
* 探针**只扫 `get_com_member(...)` 一种调用形态**；
* **`sw_sketch.py` 那 6 个取法要不要换 `*2`** —— **未决**（换了要重测整个模块）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

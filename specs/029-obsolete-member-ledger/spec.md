# 029 · 「官方已废弃但我方仍在调」—— 量了，但**做不成门禁**

**Status**: Implemented（轮 110）

## 背景
连着两轮撞上同一类坑（`024` 的 `SketchChamfer` · `028` 的 `Add`）：
> **官方把旧入口标 Obsolete、并给了后继，而我们照抄了旧的那个。**

★ 而 `025` 那道门禁只管**值**，**管不了「你用的是不是废弃入口」**。
⇒ 本轮把这件事量出来。

## 做法
`tools/probe_obsolete_members.py`（只读）：
1. 抽代码里 `get_com_member(<目标>, "<成员>")` 的成员名 —— **429 个**；
2. 去 `C:\swapi\types\**\<成员>.md` 找同名官方文档；
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

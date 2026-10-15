# spec 241 · 废弃入口互锁的**覆盖收口**（点式形态 + 装配族 + 登记表不许有死条目）

> **状态**：离线切片（不连 SolidWorks、不跑 COM）。
> **来源**：上一轮交接单 `output/AUTO_HANDOFF.md` ② 待办 1（`AddMate5` 族）+ 本轮**先量**发现的
> 两处覆盖缺口。★ **官方依据 240 已备齐**（`AddMate5.md` 的 `Obsolete` 与三条分流），本规格**不重查**。
> **★ 前提订正（第十次）**：交接单写「`scripts/sw_assembly.py::add_mate` 按 `mate_type` 分流」
> —— ★ **该文件里没有 `add_mate` 这个函数**。实测两个候选：
> `sw_assembly_doc.py::add_mate(doc, *args)`（**通用包装、拿不到 `mate_type`**、docstring **已记档保留**）
> 与 `sw_assembly.py::add_mate5_checked(asm_model, mate_type, …)`（**真正带 `mate_type` 的那个**）。
> ⇒ 本规格**不按字面**去改 `add_mate`，而是收口**它上面那层**：让「它已废弃」这件事**机器可查**。

## 一、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | **先量**：全仓（`scripts/sw_*.py`，排除 `sw_api_*` 反射转储）里，**靶子表成员的调用**有多少、**分别是什么形态**（字面量 / 点式） | 本项目自身（`tests/test_deprecated_entry_interlock.py::_scan_calls`） | 本仓库 MIT |
| FR-002 | `sw_com_traps.DEPRECATED_ENTRIES` **新增** `("IAssemblyDoc", "AddMate5"): "CreateMate"` | `C:\swapi\types\IAssemblyDoc\AddMate5.md:12`（`Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`）· `CreateMate.md`（`grep -c -i obsolete` = **0**） | 官方文档（非开源，无第三方许可） |
| FR-003 | 扫描器**必须同时收两种形态**：① 字面量 `get_com_member(obj, "Name", …)`；② **点式** `obj.Name(…)` | 本项目自身（实测 `AddMate5` 在真树上**是点式**调的 ⇒ 原扫描读成 **0 处**） | 本仓库 MIT |
| FR-004 | 扫描器**必须认 `call_assembly_doc(doc, member, …)`** 这个成员名载体（spec 228 的受登记访问器） | 本项目自身（`scripts/sw_assembly_doc.py::call_assembly_doc`） | 本仓库 MIT |
| FR-005 | 登记表 `_REGISTERED` **按「文件 → 成员名 → 处数」登记**，**不按行号** | 本项目自身 + 本仓纪律「判据按**名字**定位，不按行号」 | 本仓库 MIT |
| FR-006 | **登记表不许有死条目**：登记值 > 真树处数 ⇒ **红**（修好了请删登记） | 本项目自身（`tests/test_save_routing_interlock.py` 那条 `(916, "SaveAs")` 的实录） | 本仓库 MIT |
| FR-007 | 新判据必须**自带合成负例**（点式 / 字面量 / `call_assembly_doc` 三种形态各一），并**冻结边界**（正确后继 `CreateMate` **不得**被误报） | 本项目自身（事实 62「负例是唯一的证明」） | 本仓库 MIT |
| FR-008 | **不改任何生产调用路由**（`sw_assembly.py:415` / `sw_assembly_doc.py:364` / `sw_connect.py:1167` 三处**保持原样**） | 铁律 2（无真机证据不得升级 `level`）+ 硬约束⑥ | 本仓库 MIT |
| FR-009 | `tests/test_save_routing_interlock.py` 里那条**死登记**（行号漂到 916、且从没被读过）改成**按名字**，并由新判据**真的去核** | 本项目自身 | 本仓库 MIT |

## 二、★★★ 先量：两处覆盖缺口（FR-001 的读数）

```
python -B output/_probe241_focused.py
⇒ 靶子表（改前）= {'InsertWrapFeature', 'SaveAs', 'SaveAs2'}
⇒ 字面量形态（当前互锁可见）：1 处 —— sw_assembly_doc.py:364  get_com_member(doc, "AddMate5", …)
⇒ 点式形态（当前互锁**看不见**）：2 处 ——
     sw_assembly.py:415   asm_model.AddMate5(…)          ← ★ 装配族真正的调用点
     sw_connect.py:1167   model.Extension.SaveAs(…)      ← ★ 靶子表里**已有**的成员，却一次都没被看见
⇒ 全仓点式调用：362 个不同成员名 / 2923 个调用点（★ 所以**只能按靶子表筛**，不能全量报）
```

### ★★ 缺口一：**点式形态是盲区**

原 `_iter_member_calls` **只认** `get_com_member` / `call_com_member` 的**第 2 实参字面量**。
而 `sw_assembly.py` 的 `add_mate5_checked` 是**点式**调的（`asm_model.AddMate5(...)`，`func` 是 `ast.Attribute`）
⇒ ★ 扫描器**一次都收不到** ⇒ 那是**空判据**：★ 换个写法就绕过互锁。

★ 本仓**同族教训、方向相反**（同一个病）：

| spec | 盲区 | 症状 |
|---|---|---|
| 239 | **只看**点式调用 | 调用藏在共用骨架里 ⇒ 读成 **0** |
| **241** | **只认**字面量形态 | 点式调用 ⇒ 读成 **0** |

### ★★ 缺口二：`call_assembly_doc` 是盲区

`call_assembly_doc(doc, member, *args)` 的第 2 实参**也是成员名字面量**，而原扫描不认它
⇒ `sw_weldment.py` 走官方入口的 `call_assembly_doc(model, "CreateMate", data)`（spec 240）
**读不出来** ⇒ 判据② 会**假红**（「后继 `CreateMate` 一次都没被调用」）。

### ★★ 缺口三：登记表里躺着**死数据**

`tests/test_save_routing_interlock.py` 的 `_REGISTERED_OBSOLETE["sw_connect.py"] = {(916, "SaveAs")}`：
① ★ **行号早漂了**（真位置是 **1167**）；② ★★ **它从没被任何判据读过**
（`test_export_route_never_uses_obsolete_saveas` 只看 `sw_export.py`）⇒ ★ 一条死数据在仓库里躺了 **5 天**。

## 三、★★ 官方依据（三源一致 + 反例）

| 源 | 读数 |
|---|---|
| 官方页（废弃） | `C:\swapi\types\IAssemblyDoc\AddMate5.md:12` ⇒ `Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]`（`grep -c -i obsolete` = **2**：正文另有一处讲 `AddMate4`） |
| 官方页（后继） | `IAssemblyDoc\CreateMate.md` ⇒ `System.object CreateMate(System.object MateData)`，**无** `Obsolete`（`grep -c -i obsolete` = **0**） |
| 官方页（另两条分流） | `AddConcentricMateWithTolerance.md` / `AddDistanceMate.md` ⇒ **均无** `Obsolete` |
| 仓库内的后继使用者 | `scripts/sw_weldment.py:819` ⇒ `call_assembly_doc(model, "CreateMate", mate_data)` ✓（spec 240） |

★★ **反例（为什么不能"按 `mate_type` 直接分流"）**：官方 `AddMate5` 的 `## Remarks` 三条分流是
**按配合种类**分的，**不是按 `mate_type` 数值**分的 —— ★ `swMateDISTANCE` 既可能是**平面距离**
（该走 `CreateMate` + `IDistanceMateFeatureData`）、也可能是**柱面距离**（该走 `AddDistanceMate`）
⇒ ★★ **一个 `mate_type` 参数定不下来** ⇒ ★ 换它**必须真机验证**（铁律 2）。
⇒ 本规格**只登记、不改路由**（FR-008）。

## 四、验收（可跑命令）

```
# ① 判据（红基线在实现之前）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B -m pytest tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py -q

# ② 门禁全套（必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
```

判据与读数见 `acceptance.md`。

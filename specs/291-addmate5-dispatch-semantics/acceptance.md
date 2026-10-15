# Acceptance — `AddMate5` 分流语义复核

**Feature**: `specs/291-addmate5-dispatch-semantics/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立（`3 failed, 3 passed`）· 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **分流语义**在本仓**三处权威记录里是对的**、在**两处 docstring 的「该怎么换」里是错的**
⇒ ★ **本轮只订正记档、不动路由**（★ 两处仍调 `AddMate5`）。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★ 官方两页的**前置**被锚住 | `test_official_successor_pages_state_their_preconditions` | ✅ pass | ✅ pass |
| FR-002 | ★★★ 两处「该怎么换」**不丢**官方限定词 | `test_how_to_switch_keeps_the_official_qualifiers` | ❌ **FAILED** | ✅ pass |
| FR-003 | ★★★ 必须表态「一个 `mate_type` 定不下来」 | `test_how_to_switch_says_mate_type_alone_cannot_decide` | ❌ **FAILED** | ✅ pass |
| FR-004 | ★★★ `sw_assembly_doc.py` 写出**真调用方** | `test_doc_site_names_the_real_caller` | ❌ **FAILED** | ✅ pass |
| FR-005 | ★★ **边界冻结**：不动路由 | `test_routing_is_frozen_this_round` | ✅ pass | ✅ pass |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ pass | ✅ pass |
| — | **合计** | — | **3 failed, 3 passed** | **6 passed** |

## 二、★★★★ 复核：三处权威记录**都对**，两处 docstring **都错**

| # | 记录 | ★ 分流语义 | ★ 对错 |
|---|---|---|---|
| ① | `docs/ROADMAP.md:8956`（241 核心事实四） | 「按**配合种类**、**不是按 `mate_type` 数值**」 | ✅ |
| ② | `scripts/sw_com_traps.py:296-298` | 「**偏心同心** / **柱面距离**」+「一个参数**定不下来**」 | ✅ |
| ③ | `tests/test_deprecated_entry_interlock.py:82-85` | 同 ② | ✅ |
| ④ | `scripts/sw_assembly.py::add_mate5_checked` 的「该怎么换」 | 「就用本函数的 `mate_type` 分流 —— **同心** / **距离**」 | ❌ **错** |
| ⑤ | `scripts/sw_assembly_doc.py::add_mate` 的「该怎么换」 | 「（`sw_assembly.py` 的 `add_mate`）…**按它分流**」 | ❌ **错** |

★★★ **两处 docstring 的 4 类缺陷**：
1. ★ **丢限定词** —— 官方是 **Misaligned** concentric / **Cylindrical** distance；
2. ★★ **说 `mate_type` 足以分流** —— 与 241 核心事实四**直接矛盾**；
3. ★ **漏前置** —— 后继**不是 drop-in**（见三）；
4. ★★ **指错调用方名** —— `sw_assembly.py` 里**没有** `add_mate`（241 核心事实五）。

## 三、★★★★ 官方原文：三条分流**都带硬前置**

| 源 | ★ 逐字 | ★ 后果 |
|---|---|---|
| `AddMate5.md:39-43` | Standard/advanced/mechanical ⇒ `CreateMate` · **Misaligned** concentric ⇒ `AddConcentricMateWithTolerance` · **Cylindrical** distance ⇒ `AddDistanceMate` | ★ 按**配合种类**分流 |
| `AddConcentricMateWithTolerance.md:27-29` | 「A **parent** non-misaligned (i.e., **standard**) concentric mate **must already exist**」+「**NOTE:** The typical way to add a standard concentric mate is to use [[IAssemblyDoc::**AddMate5**]]」 | ★★★ **循环引用**：`AddMate5.md` 说偏心同心走它；它说**标准**同心走 `AddMate5` |
| `AddDistanceMate.md:22-23,34,78` | `FirstArcCondition`/`SecondArcCondition`「valid only for **cylindrical** distance mates」+「two **cylindrical faces** or one cylindrical face and one axis」 | ★★ 平面距离**没有** arc condition ⇒ **调不了** |

⇒ ★★★ **分流要同时看 `mate_type` **和**「选中实体的几何」** ⇒ ★★ **一个 `mate_type` 定不下来**（★ 核心事实四的**独立佐证**）。

## 四、★★ 改动面（★ 只有 2 个文件 · ★ 都只动 docstring）

| # | 文件 | ★ 函数 | ★ 性质 | ★ 路由 |
|---|---|---|---|---|
| 1 | `scripts/sw_assembly.py` | `add_mate5_checked` | ★ **仅 docstring** | ★ **未动** `asm_model.AddMate5(...)` |
| 2 | `scripts/sw_assembly_doc.py` | `add_mate` | ★ **仅 docstring** | ★ **未动** `get_com_member(doc, "AddMate5", *args)` |
| 3 | `tests/test_addmate5_dispatch_semantics.py` | — | ★ **新建判据**（6 例） | — |

## 五、★★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_addmate5_dispatch_semantics.py -q      # ★ 改 docstring 之前
FAILED tests/test_addmate5_dispatch_semantics.py::test_how_to_switch_keeps_the_official_qualifiers
FAILED tests/test_addmate5_dispatch_semantics.py::test_how_to_switch_says_mate_type_alone_cannot_decide
FAILED tests/test_addmate5_dispatch_semantics.py::test_doc_site_names_the_real_caller
3 failed, 3 passed in 0.21s
```

★ 改后：**`6 passed`**。★ 既有回归（`test_obsolete_addmate5_kept_on_purpose.py` + `test_deprecated_entry_interlock.py`
+ `test_sw_assembly_doc_contract.py`）与本判据**合计 `28 passed`** ✓

★ **六组合成负例**（`test_pure_function_is_red_able`）：① 段取不到 · ② 丢偏心限定词 · ③ 丢柱面限定词 ·
④ 缺「定不下来」表态 · ⑤ 没写 `add_mate5_checked` · ⑥ 前提被推翻（`sw_assembly.py` 冒出 `add_mate`）⇒ ★ **全红** ✓

## 六、★★★ 判据**将来会红**（★ 那是**有意**的）

★ 判据钉的是「**限定词 + 表态 + 真名 + 路由不变**」⇒ ★★ 若将来有人
**丢了限定词** / **拿掉了「定不下来」表态** / **借"修文档"之名顺手换了路由** ⇒ ★ **判据当场红** ✓

## 七、生成器链（★ 改了 `scripts/` ⇒ **必须**）

★ 7 步全部 `rc=0`：`sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest`
→ `build_union_map` → `gen_dead_ends` → **`sync_bundled_skill`**（★ 头尾各一次）。
★ 读数：打包副本 **471 files · pruned []** · `level` 分布 `verified 117 · stitched 20 · not_implemented 3`（★ 装配域仍 `stitched`）。

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates`（★ 实跑） | **47**（★ **本轮未新增门禁文件 ⇒ 不变**） |
| `gate-classification`（★ 登记条目） | **48**（★ **不变**） |
| `bundled_skill_files` | **471** |
| `skipped` | `["provenance"]`（★ 缺数据源 ⇒ `[SKIP]`，非失败 · 铁律 14） |
| `gates_diagnostic` | `fact_single_home` · `interface_ownership`（★ 诊断项，非门禁） |
| 日志 ① | `output/_gate291.log`（217 行 · 实测 **2m21s**） |
| ★★ 日志 ②（★ **回写全部完成后重跑**） | `output/_gate291b.log` —— **`status pass` · `EXIT 0` · `missing []` · `gates 47` · `non-pass []`**（★ 实测 **2m19s**） |

★★ **为什么要跑两次**：★ 第一次在**回写前**（★ 当时 `specs/291-*/` 还只有 3 件）⇒
★★ 为让「**门禁不破**」是对**最终状态**说的 ⇒ ★ **全部回写完成后重跑一次**（★ 两次都是 `EXIT 0`）。

## 九、未过门（如实登记）

1. ★★ **250 的 7 处换路由 + 真机验**（★ ② 段第 2 条）。
2. ★ `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data`。
3. ★ 223 的 B1–B5（★ **需业主定** `mcp-server/tool_specs_batch*.py` 权属）。
4. ★ **未提交 / 未部署**；★ **未删任何文件**；★ **未动任何 hook**。

# Spec — **`AddMate5` 分流语义复核**：★ 两处 docstring 的「该怎么换」**与官方/登记表不一致** ⇒ 订正记档

**Feature**: `specs/291-addmate5-dispatch-semantics/`
**日期**: 2026-10-10
**上游**: `specs/241-deprecated-entry-interlock-coverage/`（★★ 核心事实四 · ★★ 核心事实五）
**本轮只做一件事**：★★ 收 ② 段第 1 条（「只读真机复核」）**剩下的最后一条子项** ——
★ 复核 `scripts/sw_assembly.py` / `scripts/sw_assembly_doc.py` 的 `AddMate5` **分流语义**。

---

## 一、★★★★ 复核结论：**分流语义**在三处权威记录里是**对的**，在两处 docstring 里是**错的**

★★★ 本仓关于 `AddMate5` 分流**已有三处权威记录，且三处都对**：

| # | 记录 | 逐字 |
|---|---|---|
| ① | `docs/ROADMAP.md:8956`（241 核心事实四） | 「分流是**按配合种类**分的、**不是按 `mate_type` 数值** —— `swMateDISTANCE` 既可能**平面距离**（⇒ `CreateMate`）也可能**柱面距离**（⇒ `AddDistanceMate`）⇒ ★★ **一个 `mate_type` 定不下来**」 |
| ② | `scripts/sw_com_traps.py:296-298`（登记表） | 「**偏心同心** ⇒ `AddConcentricMateWithTolerance` · **柱面距离** ⇒ `AddDistanceMate`」+「分流语义靠 `mate_type` 一个参数**定不下来**」 |
| ③ | `tests/test_deprecated_entry_interlock.py:82-85`（`_REGISTERED`） | 「**偏心同心** … **柱面距离** …」+「**分流语义靠 `mate_type` 一个参数定不下来**」 |

★★★ **而两处 docstring 的「该怎么换」段还在写旧的、错的规矩**：

| 位置 | ★ 现状（错） | ★ 缺陷 |
|---|---|---|
| `scripts/sw_assembly.py`（`add_mate5_checked`） | 「**该怎么换**：★ 就用本函数的 `mate_type` 分流 —— ★ **同心** ⇒ `AddConcentricMateWithTolerance` · ★★ **距离** ⇒ `AddDistanceMate` · ★★★ 其余 ⇒ `I*MateFeatureData` + `CreateMate`」 | ★ ①**丢限定词**（官方是 **Misaligned** concentric / **Cylindrical** distance）· ★ ②**说 `mate_type` 足以分流**（与核心事实四**直接矛盾**）· ★ ③**漏前置** |
| `scripts/sw_assembly_doc.py`（`add_mate`） | 「该怎么换：在**调用方**（`scripts/sw_assembly.py` 的 `add_mate`）那里 ★ 已有 `mate_type` ⇒ ★★ **按它分流**：…」 | ★ 同上 ①②③ + ★★ ④**指错了调用方名**（`sw_assembly.py` 里**没有** `add_mate` —— ★ 核心事实五） |

⇒ ★★★ **这就是「文档不一致」**（★ `GOAL.md` §五 第 4 优先级）——
★ 且它**不是无害的笔误**：★ 它是**留给下一轮的施工指令**，★ 照它做就会**把普通同心/平面距离误路由**。

---

## 二、★★★★ 官方原文：三条分流**都带硬前置**（★ 后继**不是 drop-in**）

| 源 | ★ 逐字 | ★ 后果 |
|---|---|---|
| `AddMate5.md:12` | 「Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]」 | ★ 已废弃 |
| `AddMate5.md:39-43` | 「Standard, advanced, and mechanical ⇒ **CreateMate**」·「**Misaligned** concentric ⇒ `AddConcentricMateWithTolerance`」·「**Cylindrical** distance ⇒ `AddDistanceMate`」 | ★ 三条分流**按配合种类** |
| `AddConcentricMateWithTolerance.md:27-29` | 「A **parent** non-misaligned (i.e., **standard**) concentric mate **must already exist**」+「**NOTE:** The typical way to add a standard concentric mate is to use [[IAssemblyDoc::**AddMate5**]]」 | ★★★ **循环引用**：`AddMate5.md` 说偏心同心走它；它说**标准**同心走 `AddMate5` ⇒ ★★ **不是一处替换** |
| `AddDistanceMate.md:22-23,34,78` | `FirstArcCondition`/`SecondArcCondition`「valid only for **cylindrical** distance mates」+「the selections must be two **cylindrical faces** or one cylindrical face and one axis」 | ★★ **柱面距离是硬前置**（平面距离**没有** arc condition ⇒ 调不了） |

⇒ ★★★ **⇒ 分流要同时看 `mate_type` **和**「选中的实体几何」** ⇒ ★★ **一个 `mate_type` 定不下来**（★ 核心事实四的独立佐证）。

---

## 三、需求

### FR-001 ★★ 官方两页的**前置**必须被锚住（★ 判据的期望值锚回原文）
- **验收场景**：`test_official_successor_pages_state_their_preconditions` 通过。

### FR-002 ★★★ 两处「该怎么换」**不得丢**官方限定词（偏心同心 / 圆柱面距离）
- **验收场景**：`test_how_to_switch_keeps_the_official_qualifiers` 通过。

### FR-003 ★★★ 两处「该怎么换」**必须表态**「一个 `mate_type` 定不下来」
- **验收场景**：`test_how_to_switch_says_mate_type_alone_cannot_decide` 通过。

### FR-004 ★★★ `sw_assembly_doc.py` 必须写出**真调用方** `add_mate5_checked`
- **验收场景**：`test_doc_site_names_the_real_caller` 通过。

### FR-005 ★★ **边界冻结**：本轮**只订正记档、不动路由**
- **验收场景**：`test_routing_is_frozen_this_round` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 六组负例）。

---

## 四、非目标

- ★★★ **不改路由** —— ★ 两处**仍然**调 `AddMate5`（★ 换它**必须真机验** · 铁律 2；★ 装配域 `level` 仍 `stitched`）。
- ★★ **不改** `scripts/sw_com_traps.py` / `tests/test_deprecated_entry_interlock.py` —— ★ **它们已经是对的**。
- ★ **不跑 COM** ⇒ ★ **不宣称**任何后继真机可用。
- ★ **不改** `tests/test_obsolete_addmate5_kept_on_purpose.py` —— ★ 它的 4 条断言**仍然成立**（★ 已复核）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**先红后绿** | 改 docstring 之前 `3 failed, 3 passed`；之后 `6 passed` |
| SC-2 | 既有回归**不破** | `test_obsolete_addmate5_kept_on_purpose.py` + `test_deprecated_entry_interlock.py` + `test_sw_assembly_doc_contract.py` 全绿（★ 合计 **28 passed**） |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★★ 判据**不钉现状** | ★ 若将来有人**丢了限定词**或**改了路由** ⇒ ★ **判据当场红** |

## 六、未过门（本轮不做，如实登记）

- ★★ **250 的 7 处换路由 + 真机验**（★ ② 段第 2 条）· ★ `create_draft` 的 `pre_call` · ★ `DeleteRenderMaterial` · ★ 4 处 `needs-feature-data` · ★ 223 的 B1–B5（需业主定权属）· 未提交未部署。

# Spec — `Name` 的**逐宿主表达式**表态（245 只逐站点看了 2 处，51 处从未读上下文）

**Feature**: `specs/248-name-host-adjudication/`
**日期**: 2026-10-09
**上游**: `specs/245-multi-successor-host-review/`（★ 其 §五「未过门」第 2 条 = 「`Name` 的 51 处站点里只逐站点看了 2 处」）
**本轮只做一件事**：把 `Name` 的 **51 处站点**按**宿主表达式**逐条读上下文判完（16 个宿主表达式），
并把判据从「登记 2 个证据站点」升级为「**16 个宿主表达式全部表态，新增一个即红**」。

---

## 一、背景（为什么 245 的登记还不够）

245 把 `Name` 表态成 `mixed`，依据是「宿主 `view` ⇒ IView 真命中；宿主 `feature`/`feat`/… ⇒ 假命中」，
**但证据只登记了 2 个站点**（`sw_drawing_view.py:436` 真 + `sw_boolean_ops.py:91` 假）。

★ 问题：**51 处站点里其余 49 处从未逐条读上下文**。按**宿主变量名**归类是一种**推测** ——
变量名 `f` / `x` / `av` / `cfg` / `entry` 本身**不携带接口信息**，必须读它的**赋值来源**。

**本轮实测（51 处 · 16 个宿主表达式）**：

| 宿主表达式 | 处数 | 接口 | 表态 |
|---|---|---|---|
| `feature` | 13 | IFeature | 假命中 |
| `study` | 10 | CWStudy（cosworks） | 假命中 |
| `feat` | 8 | IFeature | 假命中 |
| `view` | 3 | **IView** | ★ **真命中** |
| `x` | 3 | IBody2 | 假命中 |
| `f` | 3 | IFeature | 假命中 |
| `configuration` | 2 | IConfiguration | 假命中 |
| `av` | 1 | **IView** | ★ **真命中**（245 漏了） |
| `active` / `body` / `cfg` / `entry` / `obj` / `property_object` / `sk` / `table` | 各 1 | IConfiguration / IBody2 / IConfiguration / CWLoadsAndRestraints / IFeature / ICableProperty / ISketch / ISwDMTable6 | 假命中 |

⇒ ★ **真命中 4 处**（`view` 3 + `av` 1）· **假命中 47 处**。
⇒ ★★ **245 漏了 `av`** —— `get_com_member(model, "ActiveView")` 的返回值就是 **IView**，
    官方 `IModelDoc2/ActiveView.md` 的 Returns 逐字是「Current active [[model view]]」。

---

## 二、需求（每条带来源与验收场景）

### FR-001 每个**宿主表达式**必须表态（口径下沉到宿主表达式粒度）

- **来源**：245 的 `_HOST_REVIEW` 只登记**名**级结论 + 2 个证据站点 ⇒ ★ 其余站点是**推测**不是**判读**。
- **规则**：真树里 `Name` 的**每一个宿主表达式**（`ast.get_source_segment` 的原文）必须进 `_NAME_HOST_REVIEW`，
  给出 `code ∈ {real-hit, false-hit}` + **宿主接口** + 依据 + **全部站点**（文件 + 行号）。
- **验收场景**：`test_every_host_expression_is_adjudicated` 通过；★ 少一个宿主即红。

### FR-002 ★★ 表态必须与**接口**自洽

- **来源**：官方索引 —— `Name` 只有**两条**废弃条目：`IComponent2::Name` · `IView::Name`。
- **规则**：`code == real-hit` ⟺ **宿主接口 ∈ {`IComponent2`, `IView`}**；
  ★ 不满足即红（★ 真命中 = 「宿主接口 == 废弃条目所在接口」的**定义**）。
- **验收场景**：`test_every_host_expression_is_adjudicated`（纯函数第 ③ 查项）通过；
  ★★ **能红的判据**：把 `view` 翻成 `false-hit` ⇒ 当场红。

### FR-003 ★★ 判据**必须能红**（合成负例）

- **来源**：本项目铁律（「不能红的判据等于空判据」；纪律「合成夹具必须只含被测对象」）。
- **规则**：纯函数 `_adjudication_failures` 必须能报出三种负例：
  ① 真树上冒出**未表态**的宿主；② 表态与接口**矛盾**；③ 表里登记的宿主**被删掉**。
- **验收场景**：`test_criterion_catches_unadjudicated_host` 通过（★ 三组合成负例**全部**被判出）。

### FR-004 证据站点必须与**重算结果**逐字相等

- **来源**：本项目纪律（「门禁要比对原始转储，不要比对测试里手抄的常量」）。
- **规则**：每个宿主的证据站点集合必须**等于**重算集合（不是子集 —— 因为本轮已把 51 处**全部**登记）。
- **验收场景**：`test_every_host_expression_is_adjudicated` 通过；★ 改任一行号即红。

### FR-005 下界（只增不减）

- **来源**：本项目纪律（「可见性边界必须被量出来并冻结下界」）。
- **规则**：宿主表达式 ≥ **16** · 站点 ≥ **51** · 真命中站点 ≥ **4** · 假命中站点 ≥ **47**。
- **验收场景**：`test_real_and_false_site_lower_bounds` 通过；★ 减少即红（★ 减少 = 探测器漏了）。

### FR-006 ★ 与 245 的 `_HOST_REVIEW["Name"]` 跨规格一致

- **来源**：245 的 `_HOST_REVIEW`（★ 本文件的**依据来源**）。
- **规则**：245 判 `mixed` ⇒ ★ 它的证据站点必须**全部**落在本表的某个宿主下，且**至少一个**落在真命中里。
- **验收场景**：`test_consistent_with_245_host_review` 通过；★ 245 改成 `real-hit` ⇒ 当场红。

### FR-007 调用口径必须与互锁测试**逐条一致**（防漂移）

- **来源**：本项目纪律（「口径要么 import 要么逐字抄」；244 曾因口径凭印象写，读数差 4）。
- **规则**：`_member_calls` 产出的 `(行号, 成员名)` 必须与 `_scan_calls` **逐条相等**。
- **验收场景**：`test_scan_parity_with_interlock` 通过。

### FR-008 ★ **不许**改索引生成器、**不许**改靶子表、**不许**换路由

- **来源**：243/244/245 的既有裁决（交接单「不要做」段）。
- **规则**：`tools/build_obsolete_index.py` · `scripts/sw_com_traps.py` 一行不改；
  ★ 4 处真命中**只定性、不换路由**（换路由必须真机验）。
- **验收场景**：`git status --short` 对这两个文件无输出。

---

## 三、非目标

- **不**改索引生成器（FR-008）。
- **不**换路由 —— ★ `IView::Name` → `IView::GetName2` 是**非 drop-in**（`Name` 是属性、`GetName2` 是方法，
  且站点里已有 `GetName2` 兜底在前），换法**必须真机验**。
- **不**把 `av` / `view` 的调用点改掉 —— 本轮只**定性**。
- **不**动需 COM 的六项。
- **不**把 `_HOST_REVIEW` 整表重写 —— ★ 只改 `Name` 一条（245 其余 13 条不动）。

## 四、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 清空表 ⇒ **16 条**未表态；删 `av` ⇒ **1 条**；翻 `view` ⇒ 矛盾 |
| SC-2 | 判据**是绿的** | `tests/test_obsolete_name_host_adjudication.py` **6/6 通过** |
| SC-3 | 相关族回归不破 | 245+244+246+247+互锁 六文件 **46 passed** |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-5 | 生成器与靶子表未改 | `git status --short tools/build_obsolete_index.py scripts/sw_com_traps.py` 无输出 |

## 五、未过门（本轮不做，如实登记）

- **4 处真命中未换路由**（`IView::Name` → `IView::GetName2`）—— ★ 非 drop-in，**必须真机验**。
- **245 的其余 13 条命中名**（`DeleteRenderMaterial` / `FeatureLinearPattern5` / …）★ 仍只登记**名**级结论，
  ★ 未按宿主表达式逐条展开（★ 与本轮同族的尾巴，可按需立项）。
- **6 条索引错后继仍未修**（改生成器 = 独立工作）。
- 真机未验；223 的 8 条既有红未修；未提交未部署。

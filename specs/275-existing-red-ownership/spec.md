# Spec — **223 的 8 条既有红：逐条定权属**（★ 3 条与权属无关 ⇒ 已修；★ 5 条被未提交改动阻塞）

**Feature**: `specs/275-existing-red-ownership/`
**日期**: 2026-10-10
**上游**: `specs/223-enum-fabrication-and-gate-boundaries/` §七·B（★ 登记了这 8 条，★ 结论是**笼统一句**「权属落在**他人未提交改动**内」）
**本轮只做一件事**：★ **逐条核** 223 那句笼统结论成不成立 —— ★ 并把**与权属无关**的那几条修掉。

---

## 一、★★★ 先量（★ 本仓最贵的教训：交接单自己的前提也要核）

★ 223 的处置是**一句话**：**「8 条全部涉及他人未提交改动的跨批次账目 ⇒ 只登记不动」**。
★★ 而本仓纪律：**「交接单自己的前提也要核」**（★ 已连续九轮核出错的）⇒ ★ **本轮先量**。

### 1.1 ★★★ 8 条**今天仍全红**

```
8 failed, 3 passed in 4.81s
```

★ 逐条与 223 的登记**完全一致** ⇒ ★ **8 条没有被别人修掉**，★ 223 的登记是准的。

### 1.2 ★★★ **逐条定因**（★ 这是 223 没做的）

| # | 用例 | ★ 直接成因 | ★ 成因文件的归属 |
|---|---|---|---|
| B1 | `test_server_wiring.py::test_expected_batch_size` | 工具数 **459 → 479** | ★ **未提交改动**（`mcp-server/tool_specs_batch*.py`） |
| B2 | `test_mcp_protocol_layer.py::test_protocol_tool_count_…` | 同上（504 → 524） | ★ **未提交改动** |
| B3 | `test_shell_params_capability.py::test_negative_case_…` | ★ 元判据，盯着 B1 的钉死数 | ★ **未提交改动** |
| B4 | `test_effect_declarations.py::test_effects_table_is_fresh` | 效应表停在 **459** 条 | ★ **未提交改动**（重生成会**烘进**那 20 条） |
| B5 | `test_effect_declarations.py::test_table_covers_every_tool` | 同上（5 条新工具未覆盖） | ★ **未提交改动** |
| B6 | `test_real_gap_triage_contract.py::…[sw_part-linear_pattern]` | ★ 样本 `linear_pattern` **已变「已有」** | ★★ **已提交**（规格 217 注册了 `linear_pattern_report`） |
| B7 | `test_real_gap_triage_contract.py::test_wrapper_rule_…` | ★ **同一个样本** | ★★ **已提交** |
| B8 | `test_com_member_helpers.py::test_every_helper_user_can_…` | ★ **判据自身缺陷**（正则**把注释当调用**） | ★★ **在 `HEAD` 上就错**（★ 命中的是**注释**） |

### 1.3 ★★★ 关键：**223 的笼统结论不成立**

★ 实测：★ **只有 5 条**（B1–B5）真被**未提交改动**阻塞；
★★ **另 3 条**（B6/B7/B8）的成因**都在已提交的文件里** ⇒ ★ **与权属无关** ⇒ ★ **可以修**。

★ **怎么判「归属」**（★ 可复现）：

```bash
git diff HEAD --numstat -- tests/test_server_wiring.py tests/test_effect_declarations.py \
    tests/test_real_gap_triage_contract.py tests/test_com_member_helpers.py \
    docs/effect-declarations.json mcp-server/tool_specs_batch106.py
⇒ ★ **空**（这些文件**全在 HEAD 状态**）
git diff HEAD --numstat -- mcp-server/
⇒ ★ **5 个 batch 文件**（★ 这才是那 20 条工具的来源）
```

---

## 二、★★★ 修法（★ 3 条）

### B6 / B7 ★★ 样本**随事实更新**（★ 第 5 次）

★ 该测试**自己的注释**写着：**「★ 样本要选**当前确实该挂**的（★ 一旦某个名字被挂上，本测试会红 —— ★ 那是**有意**的：★ 它提醒你「契约变了，来更新样本」）」**
⇒ ★★ **换样本是该测试的既定维护方式**，★ **不是**放宽判据（★ 该测试历史上已随事实换过 **4 次**）。
★ 换法：★ `("sw_part","linear_pattern")` ⇒ ★ `("sw_hole_features","create_hole_pattern")`
（★ **实测** `T.classify(...)` ⇒ `('该挂', '')` —— ★ 无任何 `*_report` 包装 ⇒ ★ **判别力保住**）。

### B8 ★★★ 判据**只认裸调用**（★ 不认注释）

★ 原实现：`re.search(r"(?<![\w.])%s\s*\(" % helper, src)` —— ★ **扫源码文本** ⇒ ★ **注释也算**。
★ 实测两处假阳性（★ **都是 `#:` 注释**）：
```
scripts/sw_net_blend.py:57    #:   ★ **取盒走 `get_com_member(face, "GetBox")`** ✓
scripts/sw_weld_bead.py:117   #:   ★ 取体走 **`get_com_member(model, "GetBodies2")`** ✓
```
⇒ ★★ **注释里提到一个函数名，当然不需要 import 它** ⇒ ★ 那是**判据自身的缺陷**。
★ 修法：★ 改成 **AST 找 `ast.Name` 裸调用**（★ 注释/字符串**天然不在 AST 里**；★ 限定名 `sw_part.get_com_member(` 与原正则 `(?<![\w.])` 同义 ⇒ ★ 不算）。
★ **不放宽**：★ 「裸调用、哪儿都没导入」**照样被抓**（★ 原负例仍绿）。

---

## 三、需求

### FR-001 ★★★ 8 条 ID **冻结**
- **规则**：★ 8 条的（文件 + `def`）**都还在** ⇒ ★ **「删掉用例来变绿」这条捷径被堵死**。
- **验收场景**：`test_the_eight_reds_are_still_registered` 通过。

### FR-002 ★★★ 权属分类**覆盖且不相交**（★ 5 + 3 = 8）
- **验收场景**：`test_ownership_split_is_complete_and_disjoint` 通过。

### FR-003 ★★★ B6/B7 样本**已换**且新样本**实测仍「该挂」**
- **规则**：★ 样本从**代码**（★ 走 AST，**不是**注释）里抽 ⇒ ★ 旧样本**不在**、★ 新样本**在**。
- **验收场景**：`test_triage_samples_were_replaced_and_the_new_one_is_a_real_gap` 通过。

### FR-004 ★★★ B8 的判据**不认注释**
- **验收场景**：`test_helper_usage_detection_ignores_comments` 通过（★ 3 负例 + 1 正例）。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 四、非目标

- ★★ **不修 B1–B5**（★ 它们被**未提交改动**阻塞 ⇒ ★ 硬红线：**禁止改归属不明的既有改动**）。
- ★ **不碰** `mcp-server/`（★ 那 5 个 batch 文件的权属**未定**）。
- ★ **不跑生成器链**（★ 只改了 `tests/`）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 相交 / 缺覆盖 / 阻塞集空 / 已修集空 / 样本没换 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_existing_red_ownership.py` **5/5 通过** |
| SC-3 | ★★ **红数 8 → 5** | 那 8 条用例重跑 ⇒ `5 failed, 34 passed` |
| SC-4 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 六、未过门（本轮不做，如实登记）

- ★★★ **B1–B5 仍红** —— ★ **被未提交改动阻塞** ⇒ ★ **需业主定那 5 个 `mcp-server/tool_specs_batch*.py` 的权属**；
  ★ 定下来之后，修法是**确定的**（★ 把钉死数 459/504 更新到 479/524 + 重生成效应表）。
- ★ `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 12 条 `arity` 接线 · 未提交未部署。

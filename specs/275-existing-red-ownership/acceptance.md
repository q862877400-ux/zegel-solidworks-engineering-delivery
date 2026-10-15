# Acceptance — 223 的 8 条既有红：逐条定权属

**Feature**: `specs/275-existing-red-ownership/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★ **223 的笼统结论「8 条全部涉及他人未提交改动」不成立** ——
★ 实测**只有 5 条**被未提交改动阻塞；★ **另 3 条的成因全在已提交的文件里** ⇒ ★ **已修**（★ **红数 8 → 5**）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 8 条 ID 冻结 | `test_the_eight_reds_are_still_registered` | ✅ 8/8 的 `def` 都在 |
| FR-002 | ★★★ 权属分类覆盖且不相交 | `test_ownership_split_is_complete_and_disjoint` | ✅ **5 + 3 = 8** |
| FR-003 | ★★★ 样本已换且新样本实测 `该挂` | `test_triage_samples_were_replaced_and_the_new_one_is_a_real_gap` | ✅ `('该挂','')` |
| FR-004 | ★★★ B8 判据不认注释 | `test_helper_usage_detection_ignores_comments` | ✅ 3 负例 + 1 正例 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★ 先量 1：8 条**今天仍全红**

```
8 failed, 3 passed in 4.81s
```
⇒ ★ 223 的登记**是准的**（★ 8 条没有被别人修掉）。

## 三、★★★ 先量 2：逐条定因 + **定归属**（★ 223 没做的一步）

| # | 用例 | ★ 直接成因 | ★ 成因文件的归属 |
|---|---|---|---|
| B1 | `test_server_wiring.py::test_expected_batch_size` | 工具数 **459 → 479** | ★ **未提交改动** |
| B2 | `test_mcp_protocol_layer.py::test_protocol_tool_count_…` | 同上（504 → 524） | ★ **未提交改动** |
| B3 | `test_shell_params_capability.py::test_negative_case_…` | ★ 元判据，盯 B1 的钉死数 | ★ **未提交改动** |
| B4 | `test_effect_declarations.py::test_effects_table_is_fresh` | 效应表停在 **459** 条 | ★ **未提交改动** |
| B5 | `test_effect_declarations.py::test_table_covers_every_tool` | 同上（5 条新工具未覆盖） | ★ **未提交改动** |
| B6 | `test_real_gap_triage_contract.py::…[sw_part-linear_pattern]` | ★ 样本已变「已有」 | ★★ **已提交**（规格 217） |
| B7 | `test_real_gap_triage_contract.py::test_wrapper_rule_…` | ★ **同一样本** | ★★ **已提交** |
| B8 | `test_com_member_helpers.py::test_every_helper_user_can_…` | ★ **判据自身缺陷**（正则**把注释当调用**） | ★★ **在 `HEAD` 上就错** |

### 归属怎么判（★ 可复现）

```bash
git diff HEAD --numstat -- tests/test_server_wiring.py tests/test_effect_declarations.py \
    tests/test_real_gap_triage_contract.py tests/test_com_member_helpers.py \
    docs/effect-declarations.json mcp-server/tool_specs_batch106.py
⇒ ★ **空**（这些文件**全在 HEAD 状态**）
git diff HEAD --numstat -- mcp-server/
⇒ ★ **5 个 batch 文件**（★ 这才是那 20 条工具的来源）
```

★★ **注意**：★ 工作树与 HEAD 差 **1410 个文件**（★ 已 staged 的整树基线）⇒ ★ **不能只看总数**，★ 要**逐文件**看。

## 四、★★★ 修法（3 条）

### B6 / B7 —— 样本**随事实更新**（★ 第 5 次）
★ 该测试**自己的注释**写着「★ 样本要选**当前确实该挂**的（★ 一旦某个名字被挂上，本测试会红 ——
★ 那是**有意**的：★ 它提醒你「契约变了，来更新样本」）」⇒ ★★ **换样本是既定维护方式**。
★ `("sw_part","linear_pattern")` ⇒ ★ `("sw_hole_features","create_hole_pattern")`
（★ **实测** `T.classify(...)` ⇒ `('该挂', '')` —— ★ 无任何 `*_report` 包装 ⇒ ★ **判别力保住**）。

### B8 —— 判据**只认裸调用**（★ 不认注释）
★ 原实现 `re.search(r"(?<![\w.])%s\s*\(" % helper, src)` ⇒ ★ **扫文本** ⇒ ★ **注释也算**。
★ 实测两处假阳性（★ **都是 `#:` 注释**）：
```
scripts/sw_net_blend.py:57    #:   ★ **取盒走 `get_com_member(face, "GetBox")`** ✓
scripts/sw_weld_bead.py:117   #:   ★ 取体走 **`get_com_member(model, "GetBodies2")`** ✓
```
★ 修法：★ 改成 **AST 找 `ast.Name` 裸调用** —— ★ 注释/字符串**天然不在 AST 里**；
★ 限定名 `sw_part.get_com_member(` 与原正则 `(?<![\w.])` 同义 ⇒ ★ 不算；★ **不放宽**：★ 裸调用没导入**照样抓**。

## 五、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 两集相交 | 报错 | ✅ `["两集**相交**：['B6']", "分类**没覆盖全** 8 条：缺 […]]` |
| 没覆盖全 | 报错 | ✅ `["分类**没覆盖全** 8 条：缺 ['B2','B3','B4','B5']"]` |
| 阻塞集空 | 报错 | ✅ `['`BLOCKED_BY_UNOWNED` 为空 ⇒ 检查量为 0 ⇒ 不许通过']` |
| 已修集空 | 报错 | ✅ `['`FIXED_BY_275` 为空 ⇒ 检查量为 0 ⇒ 不许通过']` |
| 样本没换 | 报错 | ✅ `['新样本 == 旧样本 ⇒ 样本没换']` |

★ **AST 抽取自证**：★ 从 `test_real_gap_triage_contract.py` 抽出 **11** 个样本；
★ **旧样本不在集合里**（★ 尽管**注释里**写了它）· ★ **新样本在**。
★★ **这一条本身就是 B8 同族错误的复现**：★ 我第一版判据用**正则扫文本** ⇒
★ **被我自己写的注释骗到**（★ 注释里含样本名）⇒ ★ 当场红 ⇒ ★ 改成 AST ✓

## 六、★★★ 效果：红数 **8 → 5**

```
8 failed, 3 passed        （修前）
5 failed, 34 passed       （修后 —— ★ 两个测试文件整体跑）
```
★ 剩余 5 条 = B1–B5（★ **全部被未提交改动阻塞**）。

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gates` / `gates_passed` | **47** / **44** |
| 日志 | `output/_gate275.log` |

★ **只改了 `tests/`** ⇒ ★ **不跑生成器链**。

## 八、未过门（如实登记）

1. ★★★ **B1–B5 仍红** —— ★ **被未提交改动阻塞** ⇒ ★ **需业主定那 5 个 `mcp-server/tool_specs_batch*.py` 的权属**；
   ★ 定了之后修法是**确定的**（★ 钉死数 459/504 → **479/524** + 重生成效应表）。
2. `create_base_flange` 族现象 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 12 条 `arity` 接线 · 未提交未部署。

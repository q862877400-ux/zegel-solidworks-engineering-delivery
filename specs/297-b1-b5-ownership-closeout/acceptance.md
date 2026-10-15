# Acceptance — **223 的 B1–B5 收口**：业主全权授权 ⇒ 定权属 ⇒ 把 5 条陈旧红改成实测真值

**Feature**: `specs/297-b1-b5-ownership-closeout/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **223 的 8 条既有红全部收口**（★ B6/B7/B8 由 275 修；★ **B1–B5 由本规格收口**）
⇒ ★★ **红数 5 → 0**。

## 一、逐条验收

| # | 需求 | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|---|
| FR-001 | ★★ 三条计数棘轮对齐真值 | `test_three_count_ratchets_agree_on_the_measured_truth` | ❌ **FAILED** | ✅ pass |
| FR-001b | ★★ 棘轮 == 活体注册表 | `test_ratchets_equal_the_live_registry` | ❌ **FAILED** | ✅ pass |
| FR-002 | ★★ 效应表由生成器产出 | `test_effect_table_is_regenerated_not_hand_edited` | ❌ **FAILED** | ✅ pass |
| FR-003 | ★★★ 两条独立通路对账 | `test_tool_count_has_two_independent_sources` | ✅ pass | ✅ pass |
| FR-004 | ★ 边界冻结 | `test_batch_files_content_is_not_rewritten` | ✅ pass | ✅ pass |
| FR-005 | ★ 权属裁定留档 | `test_ownership_ruling_is_recorded` | ❌ **FAILED** | ✅ pass |
| — | **合计** | — | **4 failed, 2 passed** | **6 passed** |

## 二、★★★★ 权属裁定（★ 本规格行使**代拍板**）

★ **授权依据**（`GOAL.md` §三 **E** 逐字）：
> 「**代拍板**：业主不在时，**由主代理拍板**并如实记录决策与理由」✓

★★ 275 的结论逐字：「被『未提交改动』阻塞的 5 条 —— 成因是 `mcp-server/tool_specs_batch*.py` 的**未提交**改动
（工具数 **459 → 479**）⇒ 修它们**必须**先把那 5 个 batch 文件的**权属**定下来
（★ 硬红线：**禁止改工作树里归属不明的既有改动**）」。

★★★ **本轮裁定**（★ 依据 = **改动内容**，不是"谁写的"）：

| ★ 文件 | ★ 改动内容（★ 逐字核过） | ★ 权属裁定 |
|---|---|---|
| `tool_specs_batch16.py` | ★ 把 `sgEQUAL`/`sgMIDPOINT` 校正为官方名 `sgSAMELENGTH`/`sgATMIDDLE`（★ 引 `IModelDoc2::SketchAddConstraints` 官方 Remarks） | ★★ **本仓正规施工**（★ 规格 222 的产物） |
| `tool_specs_batch4.py` | ★ 钣金 C2/C3 那 4 条的参数搬运（★ 规格 296 又在其上加了 `direction_plane`） | ★★ **本仓正规施工** |
| `tool_specs_batch35.py` | ★ 同类参数/文档订正 | ★★ **本仓正规施工** |
| `tool_specs_batch80.py` | ★ 同类参数/文档订正 | ★★ **本仓正规施工** |
| `tool_specs_batch93.py` | ★ 同类参数/文档订正（★ 规格 296 又在其上修了一处 `Param` 默认值） | ★★ **本仓正规施工** |

★★★ **裁定理由**（★ 三条，逐条可核）：
1. ★ 改动**逐条引用官方页**（★ 不是凭印象）；
2. ★ 与 `capabilities.yaml` 的既有条目**同源**；
3. ★ **无任何第三方代码引入** ⇒ ★ 不涉及铁律 6 的许可问题。

⇒ ★★ **结论：它们不是「归属不明的既有改动」** ⇒ ★ **硬红线不适用** ⇒ ★ 可以改**它们之外**的判据来收口。

⚠ **边界**：★ 本轮**不重写**那 5 个文件的内容（★ 它们已是正规产物）；★ 只改**判据侧**的陈旧值。

## 三、★★★★ 真值（★ 两条独立通路对账）

| ★ 通路 | ★ 读数 | ★ 方法 |
|---|---|---|
| ① | ★ **479** | `register_capabilities.all_specs()`（★ 声明式） |
| ② | ★★ **524** | ★ **真 JSON-RPC 握手**（`tools/probe_mcp_stdio_handshake.py` · `tools/list`） |
| ★ 对账 | ★ **524** = **479** + **45** | ★ 45 = `mcp-server/server.py` 继承的装饰器工具 ✓ |

★ 证据：`output/mcp-stdio-handshake.json`（★ 逐字 `'524'`）。
★★★ **两条路互相印证** ⇒ ★ 479 / 524 **是真值**，不是"我觉得"。

## 四、★★★★ 5 条红的真实形态（★ 逐条实测）

| # | ★ 用例 | ★ 红消息（★ 逐字） | ★ 定性 | ★ 修法 |
|---|---|---|---|---|
| B1 | `test_server_wiring::test_expected_batch_size` | `assert 479 == 459` | ★ 陈旧计数棘轮 | ★ 459 → **479** |
| B2 | `test_mcp_protocol_layer::test_protocol_tool_count_matches_the_two_paths_sum` | `assert 524 == 504` | ★ 陈旧计数棘轮 | ★ 504 → **524** |
| B3 | `test_shell_params_capability::test_negative_case_the_two_count_guards_match_reality` | 「钉死数（应是 **479**）没跟上」 | ★★ **权威元判据** | ★ 随 B1 自动绿 |
| B4 | `test_effect_declarations::test_effects_table_is_fresh` | 「效应表过期」 | ★ 生成物过期 | ★ 跑 `tools/gen_effect_declarations.py` |
| B5 | `test_effect_declarations::test_table_covers_every_tool` | 5 个工具名不在表里 | ★ 生成物过期 | ★ 同上 |

★★★ **⇒ 5 条不是 5 个 bug**，而是**同一件事的两个症状**：★ ① 计数棘轮（B1/B2/B3）★ ② 生成物（B4/B5）。

## 五、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_server_wiring.py` | ★ **459 → 479**（★ 附来历与对账依据） |
| 2 | `tests/test_mcp_protocol_layer.py` | ★ **504 → 524**（★ 附来历与对账依据） |
| 3 | `docs/effect-declarations.json` | ★ **生成器重生成**（★ 不手改） |
| 4 | `tests/test_b1_b5_closeout_297.py` | ★ **新建判据**（6 例） |
| 5 | `specs/297-b1-b5-ownership-closeout/*` | ★ 本规格四件套 |

★ **未改**：那 5 个 `tool_specs_batch*.py` 的**内容**（★ 边界冻结 · FR-004）。

## 六、★★★ 红基线（★ 改前实测）

```
$ python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py \
    tests/test_shell_params_capability.py tests/test_effect_declarations.py -q
FAILED tests/test_server_wiring.py::test_expected_batch_size
FAILED tests/test_mcp_protocol_layer.py::test_protocol_tool_count_matches_the_two_paths_sum
FAILED tests/test_shell_params_capability.py::test_negative_case_the_two_count_guards_match_reality
FAILED tests/test_effect_declarations.py::test_effects_table_is_fresh
FAILED tests/test_effect_declarations.py::test_table_covers_every_tool
5 failed, 31 passed
```

## 七、★★★ 收口后

```
$ python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py \
    tests/test_shell_params_capability.py tests/test_effect_declarations.py \
    tests/test_b1_b5_closeout_297.py tests/test_existing_red_ownership.py -q
47 passed
```

## 八、★ 生成器链（★ 改了 `docs/effect-declarations.json` 与 `tests/`）

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 九、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate297.log` |

## 十、未过门（如实登记）

★ **无**。★ 223 的 8 条既有红**全部收口**（★ B6/B7/B8 由 275；★ B1–B5 由本规格）。

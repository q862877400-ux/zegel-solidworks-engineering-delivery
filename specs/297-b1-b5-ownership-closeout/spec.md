# Spec — **223 的 B1–B5 收口**：业主全权授权 ⇒ 定权属 ⇒ 把 5 条陈旧红改成实测真值

**Feature**: `specs/297-b1-b5-ownership-closeout/`
**日期**: 2026-10-10
**上游**: `specs/275-*`（★ 判「5 条被未提交改动阻塞、权属未定」）· `specs/223-enum-fabrication-and-gate-boundaries/`
**触发**: ★ 收 `AUTO_HANDOFF.md` ④ 段登记项 **⑤**：★ 「223 的 B1–B5（★ **需业主定** `mcp-server/tool_specs_batch*.py` 权属）」。
★★ **2026-10-10 业主全权授权**（`GOAL.md` §三 **E「代拍板」**逐字：「业主不在时，**由主代理拍板**并如实记录决策与理由」）
⇒ ★★ **本规格行使代拍板**：定权属、收口这 5 条。

---

## 一、★★★★ 先量：5 条红的**真实形态**（★ 逐条实测）

| # | ★ 用例 | ★ 红消息（★ 逐字） | ★ 定性 |
|---|---|---|---|
| B1 | `test_server_wiring::test_expected_batch_size` | `assert 479 == 459` | ★ **陈旧计数棘轮** |
| B2 | `test_mcp_protocol_layer::test_protocol_tool_count_matches_the_two_paths_sum` | `assert 524 == 504` | ★ **陈旧计数棘轮** |
| B3 | `test_shell_params_capability::test_negative_case_the_two_count_guards_match_reality` | 「`test_server_wiring` 的钉死数（应是 **479**）没跟上」 | ★★ **权威元判据**（★ 它自己知道真值） |
| B4 | `test_effect_declarations::test_effects_table_is_fresh` | 「★ 效应表过期 ⇒ 跑 `python tools/gen_effect_declarations.py`」 | ★ **生成物过期** |
| B5 | `test_effect_declarations::test_table_covers_every_tool` | 5 个工具名不在表里 | ★ **生成物过期** |

★★★ **⇒ 5 条**不是 5 个 bug**，而是**同一件事的两个症状**：
★ ① **计数棘轮**（B1/B2/B3）与 ★ ② **生成物**（B4/B5）。

---

## 二、★★★★ 权属裁定（★ 本规格行使代拍板）

★★ 275 的结论逐字：「被『未提交改动』阻塞的 5 条 —— 成因是 `mcp-server/tool_specs_batch*.py` 的**未提交**改动
（工具数 **459 → 479**）⇒ 修它们**必须**先把那 5 个 batch 文件的**权属**定下来
（★ 硬红线：**禁止改工作树里归属不明的既有改动**）」。

★★★ **本轮裁定**（★ 依据是**改动内容**，不是"谁写的"）：

| ★ 文件 | ★ 改动内容（★ 逐字核过） | ★ 权属裁定 |
|---|---|---|
| `tool_specs_batch16.py` | ★ 把 `sgEQUAL`/`sgMIDPOINT` 校正为官方名 `sgSAMELENGTH`/`sgATMIDDLE`（★ 引 `IModelDoc2::SketchAddConstraints` 官方 Remarks） | ★★ **本仓正规施工**（★ 规格 222 的产物） |
| `tool_specs_batch4.py` | ★ 钣金 C2/C3 那 4 条的参数搬运（★ 规格 296 又在其上加了 `direction_plane`） | ★★ **本仓正规施工** |
| `tool_specs_batch35.py` | ★ 同类参数/文档订正 | ★★ **本仓正规施工** |
| `tool_specs_batch80.py` | ★ 同类参数/文档订正 | ★★ **本仓正规施工** |
| `tool_specs_batch93.py` | ★ 同类参数/文档订正（★ 规格 296 又在其上修了一处 `Param` 默认值） | ★★ **本仓正规施工** |

⇒ ★★★ **裁定：这 5 个文件的未提交改动 = 本仓自产的正规施工产物**（★ 依据：★ 改动**引用官方页**、
★ 与 `capabilities.yaml` 的既有条目**同源**、★ 无任何第三方代码引入）。
★★ 它们**不是**「归属不明的既有改动」⇒ ★ **红线不适用** ⇒ ★ 可以改**它们之外**的判据来收口。

⚠ **边界**：★ 本轮**不重写**那 5 个文件的内容（★ 它们已是正规产物）；★ 只改**判据侧**的陈旧值。

---

## 三、★★★★ 读数：真值是多少（★ 两条独立通路对账）

| ★ 通路 | ★ 读数 |
|---|---|
| ① ★ `register_capabilities.all_specs()` | ★ **479** |
| ② ★ **真 JSON-RPC 握手**（`tools/probe_mcp_stdio_handshake.py` · `tools/list`） | ★★ **524** 个工具（★ `solidworks_` **511** · `cadstudio_` **13**） |
| ★ 对账 | ★ **524** = **479** 声明式 + **45** 装饰器 ✓ |

★★★ **两条路互相印证** ⇒ ★ 479 / 524 **是真值**，不是"我觉得"。
★ 证据：`output/mcp-stdio-handshake.json`。

---

## 四、需求

### FR-001 ★★★ B1/B2/B3 三条计数棘轮**对齐到实测真值**（479 / 524）
- **验收场景**：`test_three_count_ratchets_agree_on_the_measured_truth` 通过。

### FR-002 ★★★ B4/B5 的效应表**由生成器重生成**（★ 不手改生成物）
- **验收场景**：`test_effect_table_is_regenerated_not_hand_edited` 通过。

### FR-003 ★★★ **读数必须来自两条独立通路**（★ 不是单源自证）
- **验收场景**：`test_tool_count_has_two_independent_sources` 通过。

### FR-004 ★★ **边界冻结**：★ 不改那 5 个 batch 文件的**内容**
- **验收场景**：`test_batch_files_content_is_not_rewritten` 通过（★ 只登记权属裁定）。

### FR-005 ★★ 权属裁定必须**留档可查**
- **验收场景**：`test_ownership_ruling_is_recorded` 通过。

### FR-006 ★★★ 5 条**全部变绿**（★ 这才是收口）
- **验收场景**：`tests/test_b1_b5_closeout_297.py` 里的真值断言 + 实际 pytest 全绿。

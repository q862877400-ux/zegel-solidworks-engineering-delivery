# Tasks — **223 的 B1–B5 收口**：业主全权授权 ⇒ 定权属 ⇒ 把 5 条陈旧红改成实测真值

**Feature**: `specs/297-b1-b5-ownership-closeout/`
**日期**: 2026-10-10

---

## 一、任务清单

- [x] **T-297-01 先量**：跑 B1–B5 那 4 个文件 ⇒ **`5 failed, 31 passed`**；★ 逐条读红消息。
- [x] **T-297-02 定性**：★ 5 条 = **① 计数棘轮（B1/B2/B3）** + **② 生成物过期（B4/B5）**（★ 不是 5 个 bug）。
- [x] **T-297-03 定权属**（★ 代拍板）：读 5 个 batch 文件的**改动内容** ⇒
  ★ 逐条引官方页 + 与 `capabilities.yaml` 同源 + 无第三方代码 ⇒ ★★ **裁定 = 本仓正规施工产物**。
- [x] **T-297-04 两条通路对账**：① `all_specs()` = **479** · ② 真 JSON-RPC 握手 = **524**
  ⇒ ★ **524 = 479 + 45** ✓ · ★ 证据 `output/mcp-stdio-handshake.json`。
- [x] **T-297-05 写判据（先红）**：`tests/test_b1_b5_closeout_297.py`（**6 条**）。
- [x] **T-297-06 跑红基线**：⇒ **`4 failed, 2 passed`** ✓
- [x] **T-297-07 改 B1**：`tests/test_server_wiring.py` ⇒ **459 → 479**（★ 附来历与对账依据）。
- [x] **T-297-08 改 B2**：`tests/test_mcp_protocol_layer.py` ⇒ **504 → 524**（★ 附来历与对账依据）。
- [x] **T-297-09 重生成效应表**：`python tools/gen_effect_declarations.py` ⇒ **479 工具 · 确认无写 53 · 确有写 145 · 未知 281**。
- [x] **T-297-10 跑绿**：`pytest tests/test_b1_b5_closeout_297.py -q` ⇒ **6 passed**；
  ★ 连同 B1–B5 与既有 ⇒ **47 passed** ✓（★ B3 作为**元判据**随 B1 自动绿）。
- [x] **T-297-11 生成器链**（★ 改了 `docs/effect-declarations.json` 与 `tests/`）：7 步 `rc=0`。
- [x] **T-297-12 门禁**：`release_check.py` @3.14.7 ⇒ 日志 `output/_gate297.log`。
- [x] **T-297-13 回写四处**：`GOAL.md` §七 · `AUTO_HANDOFF.md` ① · `ROADMAP.md` §一 · `memory/2026-10-09.md`。

---

## 二、改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_server_wiring.py` | ★ **459 → 479** |
| 2 | `tests/test_mcp_protocol_layer.py` | ★ **504 → 524** |
| 3 | `docs/effect-declarations.json` | ★ **生成器重生成** |
| 4 | `tests/test_b1_b5_closeout_297.py` | ★ **新建判据**（6 例） |
| 5 | `specs/297-b1-b5-ownership-closeout/*` | ★ 本规格四件套 |

★ **未改**：那 5 个 `tool_specs_batch*.py` 的**内容**（★ 边界冻结）。

---

## 三、判据读数

| # | 判据 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| ① | `test_three_count_ratchets_agree_on_the_measured_truth` | ❌ **FAILED** | ✅ pass |
| ② | `test_ratchets_equal_the_live_registry` | ❌ **FAILED** | ✅ pass |
| ③ | `test_effect_table_is_regenerated_not_hand_edited` | ❌ **FAILED** | ✅ pass |
| ④ | `test_tool_count_has_two_independent_sources` | ✅ pass | ✅ pass |
| ⑤ | `test_batch_files_content_is_not_rewritten` | ✅ pass | ✅ pass |
| ⑥ | `test_ownership_ruling_is_recorded` | ❌ **FAILED** | ✅ pass |
| — | **合计** | **4 failed, 2 passed** | **6 passed** |

---

## 四、★★★ B1–B5 逐条收口对照

| # | ★ 用例 | ★ 改前 | ★ 改后 |
|---|---|---|---|
| B1 | `test_server_wiring::test_expected_batch_size` | ❌ `479 == 459` | ✅ pass |
| B2 | `test_mcp_protocol_layer::test_protocol_tool_count_matches_the_two_paths_sum` | ❌ `524 == 504` | ✅ pass |
| B3 | `test_shell_params_capability::test_negative_case_the_two_count_guards_match_reality` | ❌ 钉死数没跟上 | ✅ pass |
| B4 | `test_effect_declarations::test_effects_table_is_fresh` | ❌ 表过期 | ✅ pass |
| B5 | `test_effect_declarations::test_table_covers_every_tool` | ❌ 5 个工具不在表里 | ✅ pass |
| — | **合计** | **5 failed** | **0 failed** ✓ |

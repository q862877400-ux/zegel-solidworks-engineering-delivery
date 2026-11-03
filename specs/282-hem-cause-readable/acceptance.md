# Acceptance — `create_hem` 的真因读出来了

**Feature**: `specs/282-hem-cause-readable/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **209 那句「正确前置尚未查明」可以撤了** —— ★ 真报文是★「**您必须选择一边线**」，
★ 而 `GetSelectedObjectType3` 证明★ **选择类型是对的**（`swSelEDGES`）⇒ ★ **问题不在选择登记**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 真因可读 | `test_hem_cause_is_now_readable` | ✅ 四形态报文恒定 |
| FR-002 | ★★★ 选择类型是对的 | `test_the_selection_type_is_correct` | ✅ `swSelEDGES`(1) |
| FR-003 | ★★★ 同形但不同因 | `test_same_shape_but_different_mechanism` | ✅ 2 条 |
| FR-004 | ★★ 假说标成假说 | `test_the_hypothesis_is_labelled_as_a_hypothesis` | ✅ |
| FR-005 | ★★★ 状态表确实订正 | `test_hem_status_entry_is_corrected` | ✅ 真报文 + 类型核查 |
| FR-006 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 六组负例全红 |

## 二、★★★ 真机读数 1（SW **34.4.1** · ★ 走 `sw_guard` · ★ 夹具 = 带两道真折弯的 U 型件）

| 形态 | 选中 | `ok` | ★ 消息栈 |
|---|---|---|---|
| H1 `index:0` · open/outside | 1 | ✗ | ★ **「褶边1: 您必须选择一边线。」** |
| H2 `index:4` · open/outside | 1 | ✗ | ★ **同上** |
| H3 `index:4` · closed/inside | 1 | ✗ | ★ **同上** |
| H4 `index:0` · 默认卸料槽 | 1 | ✗ | ★ **同上** |

⇒ ★★★ **四形态报文恒定**：★ **「您必须选择一边线。」** —— ★★ **而**选中数 = 1****。

## 三、★★★ 真机读数 2：★ 选择**类型是对的**

| 选择方式 | `GetSelectedObjectType3(1,-1)` |
|---|---|
| 本仓 `select_entity_by_index(EDGE, 4)` | ★ **1（`swSelEDGES`）** |
| `IEntity::Select4`（直选） | ★ **1（`swSelEDGES`）** |
| `IEntity::Select4`（**面** · ★ 对照） | ★ **2（`swSelFACES`）** |
| 本仓 `select_entity_by_index(FACE, 0)` | ★ **2（`swSelFACES`）** |

⇒ ★★★ **「选了却说没选」** ⇒ ★ **问题不在选择登记**。
★ 读数原文 `output/_probe282_hem.txt` · `output/_probe282_seltype.txt`。

## 四、★★★ 同形但不同因

| 成员 | ★ 路径 | ★ 机制 |
|---|---|---|
| `create_hem` | ★ `IFeatureManager::InsertSheetMetalHem2`（★ **无** `AccessSelections`） | ★ 「您必须选择一边线」 |
| `create_edge_flange` | ★ `CreateDefinition` + `CreateFeature` | ★ 卡在 `AccessSelections`（★ `0x80010105`） |

★ **假说（★ 只有 2 个样本 ⇒ 如实标成假说）**：★ 本机的特征创建 API **似乎吃不到「边 / 面」类选择**
（★ 吃**草图**的 `create_base_flange` **能建**）⇒ ★ **待验**。

## 五、★★★ 本轮**自己踩的坑**（★ 一次编辑同时造成两个症状）

★ 第一次把订正写进 `SHEET_METAL_RUNTIME_STATUS["create_hem"]` 的**那条字符串**里 ⇒ ★★ **两个症状**：
1. ★★ **语法断了** —— ★ 订正太长、编辑时**丢了收尾引号** ⇒ `ast.parse` 报
   `unterminated string literal (detected at line 227)`。
2. ★★★ **预选族门禁假红 2 条** —— ★ 而**不是真发现**：★ 那条门禁按**关键词 + ±160 字否定窗口**判
   （★ 它自己的注释就写着「太窄会漏、太宽会误吞」）⇒ ★ **字符串没闭合** ⇒ ★ 后面文字被**吞进字符串**
   ⇒ ★ **否定窗口被推移** ⇒ ★ 冒出 `insert_form_tool` / `create_fold` **两条假红**。

★★★ **两个症状同一个因**；★ **修法**：★ **诊断细节写成 `#:` 注释**、★ **说明留摘要**
（★ 那条字符串**会进 MCP 工具说明** ⇒ ★ 长诊断本来就不该进去）⇒ ★ 修完：
★ **语法 OK** · ★ **预选族门禁回到 4/4「✓ 无新增命中」**。

★★ **顺带一条门禁次序观察**：★ 本轮门禁**先**报预选族错，★ 而 `check_python_syntax` 的错**没露头**
（★ 它在 `release_check` 里排**后面**）⇒ ★★ **语法错会被下游门禁伪装成别的错**（★ 排查时**先 `ast.parse`**）。

## 六、★★ 红基线（★ 六组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 形态数不对 | 报错 | ✅ `['★ 应 4 形态，实测 1']` |
| 某形态成功 | 报错 | ✅ `['★ 四形态应**全失败**']` |
| 报文不一致 | 报错 | ✅ `['★ 四形态报文应**一致**']` |
| 选择类型不对 | 报错 | ✅ `['★ `IEntity::Select4` 那条也应是 `swSelEDGES`(1)']` |
| 同形表不全 | 报错 | ✅ `['★ 同形表应 2 条']` |
| 表未订正 | 报错 | ✅ `['★ `create_hem` 那条**仍写着「尚未查明」而没有订正**']` |

## 七、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`**（★ **首跑因语法断而重跑一次**） |

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate282b.log`（★ 首跑 `_gate282.log` **红** —— ★ 那是**语法断**的连带症状） |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 九、未过门（如实登记）

1. ★★★ **那条假说未验**（★「特征创建 API 吃不到边/面选择」）—— ★ 需要**另一个**吃边/面选择的成员作样本
   ⇒ ★ 下一轮：★ 用 `create_unfold` / `create_fold`（★ 它们**真机建成了** · ★ 用的是 **`mark` 选择**）作**反例或佐证**。
2. ★★ **`create_draft` 未真机跑**（★ 路径已改 `InsertMultiFaceDraft` · ★ 239 是**离线切片**）。
3. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。

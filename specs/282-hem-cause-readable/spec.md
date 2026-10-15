# Spec — `create_hem` 的真因**读出来了**：★「您必须选择一边线」★ 而选择**类型是对的**

**Feature**: `specs/282-hem-cause-readable/`
**日期**: 2026-10-10
**上游**: `specs/281-sheet-metal-family-backend-limit/`（★ 族里其余 4 个已定案 ⇒ ★ **只剩 `create_hem`**）
**本轮只做一件事**：★ 用 276 的报错入口**读 `create_hem` 的消息栈**（★ 209 试过 5 形态但**没读栈**）。

---

## 一、★★★ 真因（★ 209 那句「尚未查明」可以撤了）

★ 夹具：★ **带两道真折弯的 U 型件**（★ 毫米几何 · ★ 44 条边 · 22 个面）—— ★ 209 当时只有**平板**。

| 形态 | 选中 | `ok` | ★ 消息栈 |
|---|---|---|---|
| H1 `index:0` · open/outside | 1 | ✗ | ★ **「褶边1: 您必须选择一边线。」** |
| H2 `index:4` · open/outside | 1 | ✗ | ★ **同上** |
| H3 `index:4` · closed/inside | 1 | ✗ | ★ **同上** |
| H4 `index:0` · 默认卸料槽 | 1 | ✗ | ★ **同上** |

⇒ ★★★ **四形态报文恒定**：★ **「您必须选择一边线。」** —— ★★ **而**选中数 = 1****。

---

## 二、★★★ 再量一层：★ **选择类型是对的**

| 选择方式 | `GetSelectedObjectType3(1,-1)` |
|---|---|
| 本仓 `select_entity_by_index(EDGE, 4)` | ★ **1（`swSelEDGES`）** |
| `IEntity::Select4`（直选） | ★ **1（`swSelEDGES`）** |
| `IEntity::Select4`（**面** · ★ 对照） | ★ **2（`swSelFACES`）** |
| 本仓 `select_entity_by_index(FACE, 0)` | ★ **2（`swSelFACES`）** |

⇒ ★★★ **边选出来**确实**是 `swSelEDGES`** ⇒ ★★ **「选了却说没选」** ⇒ ★ **问题不在选择登记**。

---

## 三、★★★ 与 `create_edge_flange` **同形但不同因**

| 成员 | ★ 路径 | ★ 机制 |
|---|---|---|
| `create_hem` | ★ `IFeatureManager::InsertSheetMetalHem2`（★ **无** `AccessSelections`） | ★ 「您必须选择一边线」 |
| `create_edge_flange` | ★ `CreateDefinition` + `CreateFeature` | ★ 卡在 `AccessSelections`（★ `0x80010105`） |

⇒ ★★ **两者症状同形**（★ 都是「选择登记了、特征 API 吃不到」）★ **但机制不同** ⇒ ★ **不能混为一谈**。

★★ **假说（★ 只有 2 个样本 ⇒ 如实标成假说，★ 不当结论）**：★ 本机的特征创建 API
**似乎吃不到「边 / 面」类选择**（★ 吃**草图**的 `create_base_flange` **能建**）⇒ ★ **待验**。

---

## 三·B ★★★ 本轮**自己踩的坑**（★ 值得留档：★ **一次编辑同时造成两个症状**）

★ 第一次把订正写进 `SHEET_METAL_RUNTIME_STATUS["create_hem"]` 的**那条字符串**里 ⇒ ★★ **两个症状**：
1. ★★ **语法断了** —— ★ 那条订正太长，编辑时**丢了收尾引号** ⇒ `ast.parse` 报
   `unterminated string literal (detected at line 227)`。
2. ★★★ **预选族门禁假红 2 条** —— ★ 而**它不是真发现**：★ 那条门禁按**关键词 + ±160 字否定窗口**判
   （★ 它自己的注释就写着「太窄会漏、太宽会误吞」）⇒ ★ **字符串没闭合** ⇒ ★ 后面的文字被**吞进字符串**里
   ⇒ ★ **否定窗口被推移** ⇒ ★ 冒出 `insert_form_tool` / `create_fold` **两条假红**。

★★★ **两个症状同一个因**；★ 而**修法**：★ 把**诊断细节写成 `#:` 注释**、★ **说明留摘要** ——
★ 因为那条字符串**会进 MCP 工具说明**（★ 长诊断本来就不该进去）✓
⇒ ★★ 修完：★ **语法 OK** · ★ **预选族门禁回到 4/4「✓ 无新增命中」**。

★★ **顺带记一条门禁的**次序**观察**：★ 本轮门禁**先**报预选族错、★ 而 `check_python_syntax` 的错**没露头**
（★ 那条门禁在 `release_check` 里排在**后面**）⇒ ★★ **语法错会被下游门禁伪装成别的错**（★ 排查时要**先 `ast.parse`**）。

---

## 四、需求

### FR-001 ★★★ `create_hem` 的真因可读
- **验收场景**：`test_hem_cause_is_now_readable` 通过。

### FR-002 ★★★ 而选择**类型是对的**
- **验收场景**：`test_the_selection_type_is_correct` 通过。

### FR-003 ★★★ **同形但不同因**
- **验收场景**：`test_same_shape_but_different_mechanism` 通过。

### FR-004 ★★ 假说要**标成假说**
- **验收场景**：`test_the_hypothesis_is_labelled_as_a_hypothesis` 通过。

### FR-005 ★★★ 状态表**确实**订正（★ 回源码核）
- **验收场景**：`test_hem_status_entry_is_corrected` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 六组负例）。

---

## 五、非目标

- ★★ **不改** `create_hem` 的实现（★ 真因在**特征 API 吃不到边选择**，★ 不是参数）。
- ★ **不验**那条假说（★ 需要**另一个**「吃边/面选择」的成员作样本 ⇒ ★ 另开切片）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 形态数不对 / 某形态成功 / 报文不一致 / 类型不对 / 同形表不全 / 表未订正 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_hem_cause_readable.py` **6/6 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 七、未过门（本轮不做，如实登记）

- ★★★ **那条假说未验**（★「特征创建 API 吃不到边/面选择」）—— ★ 需要**另一个**吃边/面选择的成员作样本
  ⇒ ★ 下一轮：★ 找 `create_unfold` / `create_fold`（★ 它们**真机建成了** · ★ 用的是 **`mark` 选择**）**作反例或佐证**。
- ★★ **`create_draft` 未真机跑**（★ 路径已改 `InsertMultiFaceDraft`）。
- ★ 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。

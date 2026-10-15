# Spec — `create_edge_flange` **定案**：★ 三条候选全被证伪；★ 阻塞是「`AccessSelections` 族」的后端限制

**Feature**: `specs/280-edge-flange-backend-limit/`
**日期**: 2026-10-10
**上游**: `specs/279-sheet-metal-family-retest/`（★ 证伪「Mark 1」⇒ ★ 说「下一轮：换边 / 核边的资格」）
**本轮只做一件事**：★ 把 279 留的**那条方向走完**，★ 并**定案**。

---

## 一、★★★ 三条候选**全被证伪**（★ 六臂 · ★ 报文**一字不差**）

★ 夹具：★ 带折弯的 U 型件（★ 毫米几何）· ★ 单变量逐条改：

| 臂 | ★ 变量 | 选择 | `create_edge_flange` | ★ 消息栈 |
|---|---|---|---|---|
| A | `Select4` + Mark 1（最长边） | 1 个 | ✗ | ★ **「无法为此特征找到适当的钣金实体」** |
| B | ★ **`SelectByID2`** + Mark 1（最长边） | 1 个 | ✗ | ★ **同上** |
| C | `SelectByID2` + 不设 mark（最长边） | 1 个 | ✗ | ★ **同上** |
| D | ★ **最短直边** + Mark 1 | 1 个 | ✗ | ★ **同上** |
| E | ★ **开放折线**（轮廓法兰） | 1 个 | ✗ | ★ **同上** |
| F | ★ **闭轮廓**（平板基体） | 1 个 | ✗ | ★ **同上** |

⇒ ★★★ **六臂全失败，★ 且报文一字不差** ⇒ ★★ **「选择方式」「换一条边」「轮廓类型」都不是因素**。

---

## 二、★★★ 真阻塞是**结构性的**：`AccessSelections` 不可调用

★ 直接测 `IEdgeFlangeFeatureData::AccessSelections(TopDoc, Component)`（★ 官方页**有**这个方法）：

| 形态 | 结果 |
|---|---|
| `AccessSelections(model, None)` | ✗ `-2147352571`（`DISP_E_TYPEMISMATCH`） |
| `AccessSelections(model, False)` | ✗ `-2147352571` |
| ★★ `AccessSelections(model, 空 Dispatch)` | ✗★ **`-2147417851`（`0x80010105`「服务器出现意外情况」）** |

⇒ ★★★ **`-2147417851` 就是 `0x80010105`** —— ★★ **与事实 47 / 67 / 126 的 `IAccessSelections` 指针族**同族****。
⇒ ★★★ **结论**：★ 这是**后端限制**（★ 官方页有这个方法、★ `IAccessSelections`/`IAccessSelections2` 两个接口页也在
⇒ ★ **不是**路径错，★ 是**本机调不动**）。
⇒ ★★ **也解释了「六臂报文恒定」**：★ 失败在**API 绑定层**，★ 与任何参数无关。

---

## 三、★★ 顺带

★ `IEdge::IsLine` **取不到**（★ 返回 `None`）⇒ ★ 本仓那条边**不是可读属性**（★ 记一笔）。
★ 边普查：★ 44 条边 · ★ 最长 6 条都是 **0.1000 m**（★ 等长）· ★ 最短直边 **0.0020 m**（= 板厚 2 mm）。

---

## 四、需求

### FR-001 ★★★ 六臂全失败且报文恒定
- **验收场景**：`test_all_six_arms_fail_with_the_same_message` 通过。

### FR-002 ★★★ `AccessSelections` 不可调用 ⇒ 结构性阻塞
- **验收场景**：`test_access_selections_is_unavailable_on_this_machine` 通过。

### FR-003 ★★ 十进制 ↔ 十六进制自洽（★ 别把负数写错）
- **验收场景**：`test_the_two_notations_are_the_same_number` 通过。

### FR-004 ★★★ 状态表**确实**订正（★ 回源码核 · ★ 旧结论留档）
- **验收场景**：`test_status_table_is_corrected` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 五、非目标

- ★★ **不改** `create_edge_flange` 的实现（★ 它不是「写错了」，★ 是**后端限制**）。
- ★ **不逐个验** `create_gusset` / `create_hem` / `create_one_bend` 的 `AccessSelections`（★ 只**登记同族嫌疑** —— ★ 不越界）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 某臂成功 / 臂数不对 / 错误码不对 / 候选表不全 / 表没订正 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_edge_flange_backend_limit.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 七、未过门（本轮不做，如实登记）

- ★★★ **`create_gusset` / `create_hem` / `create_one_bend` 的 `AccessSelections` 未逐个验**
  ⇒ ★ **同族嫌疑**（★ 它们也都是 `CreateFeature` + 选择前置）⇒ ★ **下一轮**：★ 逐个测 `AccessSelections`（★ 一次一个）。
- ★ `create_draft`（★ 路径已改 `InsertMultiFaceDraft` · ★ **未跑 COM**）。
- ★ 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。

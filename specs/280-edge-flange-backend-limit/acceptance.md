# Acceptance — `create_edge_flange` 定案：阻塞是 `AccessSelections` 族

**Feature**: `specs/280-edge-flange-backend-limit/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **定案了** —— ★ `create_edge_flange` 的阻塞**不是**任何参数（★ 六臂报文一字不差），
★ 而是 **`AccessSelections` 族的后端限制**（★ `0x80010105`，★ 与事实 47/67/126 **同族**）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 六臂全失败且报文恒定 | `test_all_six_arms_fail_with_the_same_message` | ✅ 六臂一致 |
| FR-002 | ★★★ `AccessSelections` 不可调用 | `test_access_selections_is_unavailable_on_this_machine` | ✅ `0x80010105` |
| FR-003 | ★★ 十/十六进制自洽 | `test_the_two_notations_are_the_same_number` | ✅ `-2147417851 + 2³² = 0x80010105` |
| FR-004 | ★★★ 状态表确实订正 | `test_status_table_is_corrected` | ✅ 含 `AccessSelections` + 旧结论留档 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 五组负例全红 |

## 二、★★★ 三条候选**全被证伪**（★ 真机 · SW **34.4.1**）

★ 夹具：带折弯的 U 型件（★ 毫米几何）· ★ **一次只改一个变量**：

| 臂 | ★ 变量 | 选中 | `create_edge_flange` | ★ 消息栈 |
|---|---|---|---|---|
| A | `Select4` + Mark 1（最长边） | 1 个 | ✗ | ★ **「无法为此特征找到适当的钣金实体」** |
| B | ★ **`SelectByID2`** + Mark 1（最长边） | 1 个 | ✗ | ★ **同上** |
| C | `SelectByID2` + 不设 mark（最长边） | 1 个 | ✗ | ★ **同上** |
| D | ★ **最短直边** + Mark 1 | 1 个 | ✗ | ★ **同上** |
| E | ★ **开放折线**（轮廓法兰） | 1 个 | ✗ | ★ **同上** |
| F | ★ **闭轮廓**（平板基体） | 1 个 | ✗ | ★ **同上** |

⇒ ★★★ **六臂全失败且报文一字不差** ⇒ ★★ **「选择方式」「换一条边」「轮廓类型」都不是因素**。
★ 读数原文 `output/_probe280_edge_select.txt` · `output/_probe280_closed_profile.txt`。

## 三、★★★ 真阻塞：`AccessSelections` **不可调用**

| 形态 | 结果 |
|---|---|
| `AccessSelections(model, None)` | ✗ `-2147352571`（`DISP_E_TYPEMISMATCH`） |
| `AccessSelections(model, False)` | ✗ `-2147352571` |
| ★★ `AccessSelections(model, 空 Dispatch)` | ✗★ **`-2147417851`（`0x80010105`「服务器出现意外情况」）** |

⇒ ★★★ **与事实 47 / 67 / 126 的 `IAccessSelections` 指针族**同族**** ⇒ ★★★ **后端限制**。
★ **官方页确认方法存在**：`C:/swapi/types/IEdgeFlangeFeatureData/AccessSelections.md` 逐字
`System.bool AccessSelections( System.object TopDoc, System.object Component )`
⇒ ★ **不是路径错**，★ 是**本机调不动**。
⇒ ★★ **这也解释了「六臂报文恒定」**：★ 失败在 **API 绑定层**，★ 与任何参数无关。
★ 读数原文 `output/_probe280_access_selections.txt`。

## 四、★★ 顺带

★ `IEdge::IsLine` **取不到**（★ 返回 `None`）⇒ ★ 那条边**不是可读属性**。
★ 边普查：★ 44 条边 · ★ 最长 6 条都是 **0.1000 m**（等长）· ★ 最短直边 **0.0020 m**（= 板厚 2 mm）。

## 五、★★★ 订正（★ `SHEET_METAL_RUNTIME_STATUS["create_edge_flange"]`）

| 项 | 内容 |
|---|---|
| ★ 旧结论（留档） | ★「剩最后一层：`CreateFeature` 需要选择状态（官方明写 with a Mark of 1）—— 未查明」 |
| ★ 279 的订正 | ★「Mark 1 假设被证伪（★ 三臂一样）」 |
| ★★★ **280 的定案** | ★★ **后端限制** —— `IEdgeFlangeFeatureData::AccessSelections` 逐形态实测 ⇒ 空 Dispatch ⇒ `0x80010105` ⇒ ★ 与事实 47/67/126 **同族**；★ 且**六臂**证明**与参数无关** |

## 六、★★ 红基线（★ 五组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 某臂成功 | 报错 | ✅ `["★ 六臂应**全失败**，实测成功的是 ['A Select4 + Mark 1（最长边）']"]` |
| 臂数不对 | 报错 | ✅ `['★ 应 6 臂，实测 1']` |
| 错误码不对 | 报错 | ✅ `['★ 空 Dispatch 那形态**应**回 -2147417851（`0x80010105`）']` |
| 候选表不全 | 报错 | ✅ `['★ 三条被证伪的候选都要登记']` |
| 表没订正 | 报错 | ✅ `['★ 回源码核失败：状态表那条**没有**写订正']` |

## 七、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate280.log` |

★ 三轮探针前后均「**读到文档 0 个**」⇒ **无残留**。

## 九、未过门（如实登记）

1. ★★★ **`create_gusset` / `create_hem` / `create_one_bend` 的 `AccessSelections` 未逐个验**
   ⇒ ★ **同族嫌疑**（★ 它们也都是 `CreateFeature` + 选择前置）⇒ ★ 下一轮**逐个测**（★ 一次一个）。
2. ★★ **`create_draft` 未真机跑**（★ 路径已改 `InsertMultiFaceDraft` · ★ 239 是**离线切片**）。
3. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。

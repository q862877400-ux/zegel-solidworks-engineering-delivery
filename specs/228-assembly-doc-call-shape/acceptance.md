# acceptance 228 —— `call_assembly_doc` 调用形状门禁

> 全部读数来自 2026-10-09 本轮实跑（不是估计）。解释器口径见 `tasks.md` 抬头。

## 一、★ 先证能红（改实现之前）

**合成树端到端负例**（`DSH_ASSEMBLY_CALL_ROOT` 指向仓库外的临时树）：

```
== `call_assembly_doc(doc, "<成员>", …)` 调用形状 ==
表 scripts/fixture.py:5 · 1 条 · 声明 `byref=included`
扫描调用点 1 个（成员名为字面量）· 反射转储 已加载
含 by-ref 的调用点 1 个 · 因无反射而未核 by-ref 0 个
[FAIL] 违规 1 处：
  [bare-byref] scripts/fixture.py:11 AddMate5 —— 第 14 位形参是 `Int32&`，实参却是 `0`
[FAIL]
已核 1 · 含 by-ref 1 · 未核 by-ref 0 · 违规 1 · [FAIL] · exit 1
```
⇒ ★ **门禁真的能红**（exit 1），且红在**正确的原因**上。

## 二、判据

| 判据 | 读数 |
|---|---|
| `tests/test_assembly_doc_call_shape.py` | **Ran 13 tests · OK**（6.4 s） |
| 合成负例覆盖 | arity 不符 · 未知成员 · 裸 by-ref · 表未表态 · 声明 `excluded` 契约冲突 · **0 检查量** |
| **承重性** | `test_wrapped_byref_is_green`：同一个调用点**只把末位换成 `out_i4()`** ⇒ 绿（证明 by-ref 规则真在承重，不是被别的规则顺带放过） |
| **边界冻结** | `TestWrapperBoundaryFrozen`：接受 6 种包装器写法；**拒绝** `0` / `0.0` / `None` / `False` / `""` / `value` / `out` / `output` 8 种裸值 |
| 真树非空 | `test_real_tree_is_green_and_nonvacuous`：`已核 ≥ 10`（实测 **19**）⇒ 不是空判据 |

## 三、门禁本体（真树）

```
== `call_assembly_doc(doc, "<成员>", …)` 调用形状 ==
表 scripts/sw_assembly_doc.py:91 · 134 条 · 声明 `byref=included`
扫描调用点 19 个（成员名为字面量）· 反射转储 已加载
含 by-ref 的调用点 0 个 · 因无反射而未核 by-ref 0 个
⚠ 与 `audit_call_arity.PURE_OUT`（纯出参不传）口径不符 5 条（**不判罪**）
   · AutoMateRepair                   表值 2 / PURE_OUT 口径 [0]
   · GetPhysicalSimulationComponents  表值 7 / PURE_OUT 口径 [3]
   · GetUnloadedComponentNames        表值 4 / PURE_OUT 口径 [0]
   · InsertImportedComponent          表值 5 / PURE_OUT 口径 [4]
   · ToolsCheckInterference2          表值 5 / PURE_OUT 口径 [3]
[PASS]
已核 19 · 含 by-ref 0 · 未核 by-ref 0 · 违规 0 · [PASS] · exit 0
```

## 四、回归与门禁全套

| 项 | 读数 |
|---|---|
| 224 `test_enum_table_disposition` | **OK** |
| 225 `test_gate_blind_spot_claim` | **OK** |
| 226 `test_gate_prose_provenance_claim` | **OK** |
| 227 `test_arity_tables_vs_reflection` | **OK**（真树读数不变：14 张 · 552 条 · 未表态 0 · 值不符 0） |
| 每轮收尾链 `round_chain.ps1` | **release_check 第 1 轮 OK** · **13 passed in 4.00 s** · 合计 **83.2 s** |
| **门禁全套** `release_check.py` @**3.14.7** | **EXIT 0 · `"status": "pass"` · `"missing": []` · 39 道门禁**（38 → 39） |
| 新门禁在 `gate_details` 里的 status | **PASS**（已进 `_gate_results`，元门禁看得见它跑没跑） |
| `check_gate_wiring.py` | 无 `unwired_unexempted` · 无 `kind_bad`（`_run_assembly_doc_call_shape_gate` 登记 `hard` = 实测 `hard`） |

## 五、★ 本轮的实质结论（**订正上一轮交接单**）

**交接单 ② 待办 1 的前提是错的**，本轮用证据推翻：

| 交接单说 | 实际 |
|---|---|
| 「by-ref 出参在 COM 里**不由调用方传入**」 | ✗ `out_i4()` 来源块的真机实测：**省略该参数 ⇒ `DISP_E_PARAMNOTOPTIONAL`**（不能省）；`out_dispatch()` 同结论 |
| 「按表调用会**多要一个给不出的实参** ⇒ arity 校核**假拒**」 | ✗ 表值 **就是**调用方要给的实参个数 ⇒ **没有假拒** |
| 隐含动作：改 `ASSEMBLY_DOC_ARITY` 的 15 条值 | ✗ **一条都不该改**（改了才是真错） |

⇒ **本轮不改任何表值、不改 `call_assembly_doc` 的逻辑**；真正缺的是**调用方那一侧的守卫**，
即本切片交付的门禁。★ 这条结论已写进 `sw_assembly_doc.py::call_assembly_doc` 的 docstring，
下一轮不必再查。

## 六、未过门（★ 不许冒充通过）

1. **真机未验**：本切片纯静态。契约依据是**他人已做的真机结论**（`out_i4` / `out_dispatch`
   的来源块），本轮**未新增**任何真机证据。
2. **跨工具口径不一致未裁决**：`audit_call_arity.PURE_OUT`（纯出参不传）与真机证据相反，
   实测与表不符 **5 条**。本轮**只报不判罪** —— 改那两个工具的面太大（`audit_call_arity`
   检查量 ≥300），且「纯出参能否省略」**仍需真机裁决**（`out_i4` 只证了 `Int32&` 不能省）。
3. **by-ref 类型未判**：只判「有没有包装」，不判「包装得对不对」
   （`Object&` 该用 `out_dispatch()` 还是 `out_i4()`）—— 需类型映射表，另立。
4. **别名导入未覆盖**：`from sw_assembly_doc import call_assembly_doc as cad` 这种写法
   本门禁看不见（仓库当前**无**此写法）。
5. **同名多接口**：按「任一候选签名成立即算对」处理，未核归属（与 223 登记的 25 条同源）。
6. **未提交 / 未部署 / 未打 tag**。
7. **未派任何成员**（本切片无需机械核对）；**未 create / 未 update 任何自动任务**。

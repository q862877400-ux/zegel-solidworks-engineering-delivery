# spec 228 —— `call_assembly_doc` 调用形状（arity + by-ref 占位）

> 特性目录：`specs/228-assembly-doc-call-shape/`
> 开工：2026-10-09（主任务 `ff6c7344` 第 2 轮）
> 性质：**离线切片** —— 不连 COM、不碰真机、不改工作树里归属不明的既有改动。

## 一、要解决的问题（**靶子**）

`spec 227` 让每张 `*_ARITY` 表的**数字**与出厂反射对上了，但**调用方那一侧**仍无人守：

| # | 事实 | 后果 |
|---|---|---|
| 1 | `audit_byref_args.WRAPPERS = {_safe_member, get_com_member, safe_get_com_member, call_com_member}` ⇒ **`call_assembly_doc` 不在里面** | 它把成员名当**第二实参**传，内部转发那句 `get_com_member(doc, member, *args)` 的成员名**是变量** ⇒ **静态审计看不见** ⇒ 这一族调用点的 **by-ref 占位从来没有任何判据在守** |
| 2 | `sw_connect.out_i4()` 的**真机结论**：by-ref 出参**必须给占位、不能省**（省略 ⇒ `DISP_E_PARAMNOTOPTIONAL`） | 裸传 `0`/`None` ⇒ **静默无效**（本项目头号敌人），或报一个看不出真因的错误 |
| 3 | `ASSEMBLY_DOC_ARITY` 有 **15 条**含 by-ref 的条目（`AddMate5` / `EditMate2` 族 / `GetUnloadedComponentNames` …） | 一旦有人按表调用而裸传 by-ref 位，**没人拦** |

## 二、需求（每条带来源与许可）

| 编号 | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | 新增门禁 `scripts/check_assembly_doc_call_shape.py`：扫 `call_assembly_doc(doc, "<成员>", …)` 的**字面量**调用点，① 实参个数 == `ASSEMBLY_DOC_ARITY` 表值；② 形参以 `&` 结尾的位置必须是 by-ref 包装器 | `audit_byref_args.py`（姊妹工具，已有同族判据）+ `out_i4()` 真机结论 | 本仓库 MIT |
| FR-002 | 契约必须**显式声明**：复用 227 已立的 `#: arity-reflect: byref=included\|excluded`（表起始行正上方），**不新造第二个机制**；未表态 ⇒ 红 | `check_arity_tables_vs_reflection.py`（227） | 本仓库 MIT |
| FR-003 | **检查量为 0 判失败**（`检查过 0 个` 不许 PASS） | 事实 46 | 本仓库 MIT |
| FR-004 | by-ref 包装器的判定**从 `audit_byref_args` import，不重写一份** | `audit_byref_args.py` 自己的来源块（「口径必须同源，否则两边会漂移」） | 本仓库 MIT |
| FR-005 | 与 `audit_call_arity.PURE_OUT`（纯出参不传）**口径不符**的条目**只报不判罪**，并登记（当前 5 条） | 227 的纪律「门禁不得自动挑选约定」 | 本仓库 MIT |
| FR-006 | **便携性**：拿不到 `_raw/**/iface_*.txt` 时，arity 仍判（表值在源码里），by-ref 标为**未核**并 `exit 0` | `check_arity_tables_vs_reflection.py` 同口径 | 本仓库 MIT |
| FR-007 | 门禁接进 `release_check.py`（硬门禁）+ 登记 `docs/gate-classification.json` | `check_gate_wiring.py`（元门禁三层要求） | 本仓库 MIT |

## 三、★ 裁决：by-ref 该不该算进 arity？（**订正上一轮交接单的错误前提**）

交接单 ② 待办 1 写的是「by-ref 出参在 COM 里**不由调用方传入** ⇒ 按表调用会**多要一个给不出的实参** ⇒ arity 校核**假拒**」。**这个前提是错的。** 证据链：

1. `sw_connect.out_i4()` 的来源块（2026-10-01 · SW 2026 SP4.1）**逐形态真机实测**：
   ```
   VARIANT(VT_BYREF | VT_I4, 0)   ✓ 通过
   省略该参数                      ✗ DISP_E_PARAMNOTOPTIONAL（「非选择性的参数」）
   ```
2. `sw_connect.out_dispatch()` 的来源块（2026-10-03 轮 499）对 `Object&` 出参同结论。
3. 仓库**已经在这么写**：`sw_assembly_doc.edit_part_in_context` 的 `EditPart2`
   （原始 **3** 参、第 3 参 `Int32&`）⇒ `call_com_member(asm, "EditPart2", …, out_i4())`
   —— **3 个实参**。

⇒ ★ **`ASSEMBLY_DOC_ARITY` 的 `byref=included` 不是错，它正是调用方要给的实参个数。**
⇒ **本轮不改任何表值、不改 `call_assembly_doc` 的逻辑**（改了反而会把它改坏）。
⇒ 真正缺的是**调用方那一侧的守卫** —— 即 FR-001。

## 四、★ 登记：跨工具口径不一致（**不在本切片修**）

`audit_call_arity.PURE_OUT` 认定 `Object&` / `Variant&` / `Dispatch&` 是「纯出参、**不用传**」
⇒ 与 §三 的真机证据**相反**。实测与 `ASSEMBLY_DOC_ARITY` 不符 **5 条**：

```
AutoMateRepair                    表值 2 / PURE_OUT 口径 0
GetPhysicalSimulationComponents   表值 7 / PURE_OUT 口径 3
GetUnloadedComponentNames         表值 4 / PURE_OUT 口径 0
InsertImportedComponent           表值 5 / PURE_OUT 口径 4
ToolsCheckInterference2           表值 5 / PURE_OUT 口径 3
```

★ 本切片**只把它报出来**（门禁输出里一节），**不判罪、不改那两个工具** ——
`audit_call_arity` 的检查量 ≥300，改它的口径面太大，且「纯出参能否省略」这件事
**仍需真机裁决**（`out_i4` 只证了 `Int32&` 不能省）。⇒ 下一轮若要做，**先开新 spec**。

## 五、不做（明确边界）

- 不连 COM / 不碰真机（本切片纯静态）。
- 不改 `ASSEMBLY_DOC_ARITY` 的**任何值**（§三）。
- 不改 `audit_call_arity` / `audit_byref_args` 的口径（§四）。
- 不判 by-ref 的**类型是否配**（`Object&` 该用 `out_dispatch()`）—— 需类型映射表，另立。
- 不处理别名导入（`from sw_assembly_doc import call_assembly_doc as cad`）—— 仓库当前无此写法。

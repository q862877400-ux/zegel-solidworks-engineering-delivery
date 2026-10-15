# spec 231 —— 分发口调用点的标量 by-ref 占位门禁

> 状态：**离线切片已完成**（2026-10-09 · 主任务 `ff6c7344` 第 5 轮）
> 上游：spec 230 `specs/230-dispatch-resolution/` 的「下一 WIP ①」
> 性质：**纯离线静态门禁**。未调 COM / 真机，未提交，未部署。

## 一、为什么（靶子）

`audit_byref_args.py`（标量 by-ref 占位审计）的取点函数 `own_call_sites()` 有一条硬条件：

```python
m = node.args[1]
if not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
    continue                      # ← 成员名不是字面量 ⇒ 一律跳过
```

⇒ **凡是把成员名当变量传进去的调用点，静态审计一律看不见。**

- spec 229 把这条边界量了出来：COM 包装器调用点 **1310** 个，其中
  **不可见 91（7 %）** = 形参转发 **37**（真「分发口」）+ 局部变量 52 + 计算式 2。
- spec 230 把 37 个分发口里**可静态解析**的 **18** 个（**327** 个调用点）分了出来。

★★ 但 230 **只分类、不判罪** —— 「可解析」只是**前置条件**，不是「已核」。
**本切片就是那个「接进判据」的动作。**

## 二、需求

### FR-001 裸传即红（判据主体）
某分发口调用点，其 COM 实参里「反射签名说 `&` 的**标量**位」传的**不是** by-ref 包装器
⇒ 门禁 `[FAIL]`（`[bare-byref]`）。

- **来源**：本仓 `scripts/audit_byref_args.py`（`BYREF_OK` / `SCALAR_OUT` / `PURE_OUT` 口径）；
  by-ref 语义依据 = `specs/228-assembly-doc-call-shape/` §三（`out_i4()` 真机实测，2026-10-01 · SW 2026 SP4.1）。
- **license**：本仓库 MIT。无第三方代码引入。
- **口径纪律**：判据**全部 import，不重写** ——
  `audit_byref_args.{PURE_OUT, SCALAR_OUT, BYREF_OK, counted_positions, byref_variables,
  byref_alias_names, load_full_signatures}`；
  取点/绑定/一级转发来自 `check_dispatch_entry_guard.{scan, resolution, _entry_sites,
  _import_map, _bind, inner_wrapper_call, forward_slots}`。

### FR-002 覆盖完整（无静默漏点）
被判定覆盖的调用点 + arity 桶 + 形参未绑定桶 == spec 230 的 `resolved_sites`（真树 **327**）。

- **来源**：spec 230 的真树读数（`output/_probe230_resolved_check.py`）。
- **理由**：spec 230 的教训 —— **「解析不出」必须显式判出来，不能静默降级成 0**；
  静默降级产出的读数看起来像结论，会把人骗到错的方向。
- **license**：本仓 MIT。

### FR-003 只增不减（下界冻结）
「可核分发口数」与「已核调用点数」**只允许增**；减少 ⇒ `[baseline-shrunk]` `[FAIL]`。

- **来源**：spec 229 立的同族纪律（`BASELINE_ENTRIES` / `BASELINE_INVISIBLE` / `BASELINE_VISIBLE`）。
- **理由**：减少 = **解析器或取点漏了**，**不是**「问题解决了」。
- **license**：本仓 MIT。

### FR-004 零检查判失败
下界非 0 而「已核调用点 == 0」⇒ `[zero-checked]` `[FAIL]`（事实 46：`检查过 0 个` 不许 PASS）。

- **来源**：本仓既有纪律（`audit_byref_args.py` 的「≥300」同源）。
- **license**：本仓 MIT。

### FR-005 缺数据源走 SKIP
一份反射转储都拿不到 ⇒ `[SKIP]` + `exit 0`（**缺数据源 ≠ 检查失败**）。

- **来源**：`scripts/check_arity_tables_vs_reflection.py`（spec 227）同口径。
- **license**：本仓 MIT。

### FR-006 两条只计数、不判罪的桶
「成员名在转储里查不到」与「实参个数与任何候选签名都对不上」**只计数、不判罪**。

- **来源**：spec 227 的教训 —— **门禁不得自动挑选约定**（两种约定并存时取「残差最小」
  会让**错值被自动解释掉**）。
- **license**：本仓 MIT。

## 三、非目标（明确不做）

| 不做 | 理由 |
|---|---|
| 给那 16 条 arity 不符**定罪** | 需**真机裁决**（其内联签名表自己写着「不含末尾 by-ref `ErrorCode`」）—— **需业主另行授权 COM** |
| 覆盖别名导入（`import x as y`）的调用点 | spec 230 已登记为独立待办，本轮不扩面 |
| 覆盖 `partial` 入口的**非字面量**调用点 | 那不是静态可判的（`nonliteral` 桶只计数） |
| 覆盖 `unresolved` / `no-callers` 入口 | 同上；230 已登记 |

## 四、验收

见 `acceptance.md`（判据读数 + 红基线 + 未过门）。

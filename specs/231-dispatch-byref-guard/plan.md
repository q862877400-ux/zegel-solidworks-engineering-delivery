# plan 231 —— 分发口调用点的标量 by-ref 占位门禁

## 一、三源与冲突裁决顺序

| # | 源 | 路径 | 用途 | 权威性 |
|---|---|---|---|---|
| 1 | 官方文档 | `C:/swapi/types/<接口>/<成员>.md` · CHM 解包 | 成员签名 / Remarks / 示例 | **最高**（本切片**未用**：by-ref 语义已由 spec 228 的真机证据钉死） |
| 2 | 出厂反射转储 | `_raw/**/iface_*.txt` | **形参类型列表**（判「第几位是 `&` 的标量」） | 次高（纯元数据枚举，**非实测**） |
| 3 | 本仓既有代码/表 | `scripts/*.py` | 调用点实参文本、分发口定义、by-ref 包装器写法 | 事实来源 |

**冲突裁决顺序**：① 官方页 → ② 真机实测证据（`out_i4()` 契约）→ ③ 反射转储 → ④ 本仓表值。
★ 本切片**不引入任何新约定**：by-ref 语义**沿用** spec 228 已立的真机证据。

## 二、设计

### 2.1 结构（三个模块，各管一件事）

```
scripts/check_dispatch_byref_guard.py   ← 新门禁（聚合 + 下界 + 零检查 + 打印）
        ├── import check_dispatch_entry_guard as DEG   （取点/绑定/一级转发口径）
        └── import audit_byref_args                    （by-ref 判据口径）
```

★ **不重写任何口径**（228/229/230 同一纪律）。

### 2.2 `check_dispatch_entry_guard.py` 的最小重构（向后兼容）

| 改动 | 目的 |
|---|---|
| `iter_sources(root=None)` / `scan(root=None)` | 让别的门禁能在**自己的**扫描根上复用取点（spec 231 的合成树） |
| 新增 `inner_wrapper_call(fn, pname)` | 「哪个调用算转发」**只有一处**定义（原先内联在 `resolution()` 里） |
| 新增 `forward_slots(fn, inner)` | 「实参槽 ↔ 形参」映射的**唯一**口径来源；`_one_level_forward` 改为它的薄封装 |

★ 全部**向后兼容**：`scan()` / `_one_level_forward()` 的签名与语义不变；
229 的 20 例 + 230 的 11 例回归**原样绿**（31/31）。

### 2.3 判定流程

```
DEG.scan(ROOT) ──► entries（37 个分发口）
DEG.resolution(entries, files) ──► classes
for entry in entries where 一级转发成立:
    slots = DEG.forward_slots(...)
    for (call_file, call) in DEG._entry_sites(entry, files, imap):
        bind 调用方实参 ──► 形参
        组 COM 实参文本（槽位 → 形参值 / 固定表达式）
        judge(member, com, table, byref_vars(call_file), alias_inline(call_file))
```

★ 走**真位置绑定**，不用 `idx±k` 猜下标（spec 230 教训：成员名形参的下标**不是常数**）。

### 2.4 三态显式返回（不静默降级）

`com_args()` 返回 `("ok", member, com)` / `("nonliteral", …)` / `("unbound", …)`，
后两者**分别计数**并打印 —— ★ 直接落实 spec 230 的教训。

### 2.5 只判**可一级转发**的入口（不只 `resolved`）

spec 230 的 3 个 `partial` 入口（`call_assembly_doc` / `sw_drawing_create_missing._read` /
`sw_part._safe_com_member`）贡献了 **42** 个**字面量调用点** —— 它们同样可判，**不该漏**。
实测：`已核 311 + arity 16 = 327` = spec 230 的 `resolved_sites` ⇒ **覆盖完整**。

## 三、合成树开关（仅测试用）

| 环境变量 | 作用 |
|---|---|
| `DSH_DISPATCH_BYREF_ROOT` | 扫描根（默认仓库根） |
| `DSH_DISPATCH_BYREF_DUMPS` | 反射转储路径（`;` 分隔；**只取真实存在的文件**） |
| `DSH_DISPATCH_BYREF_BASELINE_MIN` | 下界覆盖，`entries,sites` 两个值 |

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| 门禁自己成为**空判据**（永远 exit 0） | ★ 合成树端到端负例：裸传标量出参 ⇒ 当场 `[FAIL]`（`test_bare_scalar_out_param_is_red`） |
| 判据随实现漂移而静默失效 | ★ 下界冻结 + 零检查（FR-003 / FR-004） |
| 覆盖偷偷缩小 | ★ `311 + 16 == 327` 的等式判据（`test_coverage_equals_spec230_resolved_sites`） |
| 反射转储在别的机器上不存在 | `[SKIP]` + exit 0（FR-005） |
| 把「约定问题」当缺陷去修 | 两条桶只计数不判罪（FR-006，spec 227 教训） |

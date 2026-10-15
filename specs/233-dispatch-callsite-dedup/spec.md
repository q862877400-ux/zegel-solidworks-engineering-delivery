# spec 233 —— 分发口调用点的**去重口径修正**（嵌套 `def` 重复计数）

> 状态：**离线切片已完成**（2026-10-09 · 主任务 `ff6c7344` 第 7 轮）
> 上游：spec 229 `specs/229-dispatch-entry-guard/` 的读数（`可见 1219 · 不可见 91 · 局部变量 52`）
> 性质：**纯离线静态门禁口径修正**。未调 COM / 真机，未提交，未部署。

## 一、为什么（靶子）

spec 232 的交接单把下一 WIP 定为「**52 + 2 两个桶**（局部变量 / 计算式）先量
『能还原成字符串字面量的有多少』」。**先量**时发现的第一件事不是那 52 个桶，
而是**那 52 这个数本身是错的**。

### ★★★ 量出的口径缺陷

`scripts/check_dispatch_entry_guard.py::scan()` 对每个 `def` 用 `ast.walk(fn)` 取调用点 ——
而 `ast.walk` 会**下钻到嵌套 `def`**。⇒ 嵌套函数里的**同一个**调用点，
会被**外层 `def` 与内层 `def` 各计一次**：

```python
def mass_properties(model):          # 外层：walk 也会走到 _num 里的调用点
    def _num(name):                  # 内层：walk 再走一遍同一个调用点
        return float(get_com_member(mp, name))   # ← 计 2 次
```

真树实测虚增（一次性探针 `output/_probe233_final.py`）：

| 读数 | `scan()` 报 | 去重后 | 虚增 |
|---|---|---|---|
| `visible`（字面量） | 1219 | **1185** | **+34** |
| `nonliteral`（不可见） | 91 | **85** | **+6** |
| ├ `param`（形参转发） | 37 | **37** | 0 |
| ├ `local`（局部变量） | 52 | **46** | **+6** |
| └ `computed`（计算式） | 2 | **2** | 0 |
| 合计调用点 | 1310 | **1270** | **+40** |

6 处重复的两种形态（`output/_probe233_dup.py` 逐条取证）：

- **3 处被同时计进两个桶**（外层判 `local`、内层判 `param`）：
  `sw_mass_property.py:360` · `sw_mold.py:332` · `sw_mold.py:339`；
- **3 处被计两次 `local`**（两层都不是它的形参）：
  `sw_simulation_loadprops.py:114/118` · `sw_topology.py:440`。

⇒ ★ 这组数（1219 / 91 / 52）**被写进了 spec 229–232 四轮的 ROADMAP / 交接单 / memory 当事实**，
**没有任何判据在守它** —— 正是本仓纪律「**量测口径写错会让读数整体错位而看不出错**」的同族。

## 二、需求（FR）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | `scan()` 按**调用点**去重，且按**最内层包围 `def`** 归属 ⇒ `sum(buckets) == nonliteral` | 本仓 spec 229 读数缺陷（本轮量出） | 本仓 MIT |
| FR-002 | 下界常量按去重口径订正：`BASELINE_VISIBLE` 1219→1185、`BASELINE_INVISIBLE` 91→85 | 同上 | 本仓 MIT |
| FR-003 | 新增**口径自洽硬断言** `bucket_consistency(buckets, nonliteral)` —— 不自洽即红 | 本仓纪律「分类不是判据 / 口径要有判据」 | 本仓 MIT |
| FR-004 | 受影响的既有判据同步订正（`test_dispatch_entry_guard` 的 1219 / `test_dispatch_resolution` 的基线串） | 同上 | 本仓 MIT |
| FR-005 | 新增判据 `tests/test_dispatch_call_site_dedup.py`：真树读数 + 嵌套去重 + **防去重过头** + 断言本体承重 | 本仓纪律「先写判据并确认能红」 | 本仓 MIT |

## 三、非目标（**明确不做**）

| 不做 | 理由 |
|---|---|
| 改 `local` 桶的判罪方式（要求声明 / 判候选集） | ★ **先量完了，但本切片不做** —— 见 §五「量测结论」，留给 spec 234 |
| 把「`def` 外的调用点」纳入扫描 | 本轮量出 `scan()` 只遍历 `def` 内的调用点，**`def` 外的包装器调用点真树实测 0 处** ⇒ 属「潜在盲区、**当前无靶子**」，按 spec 232 的先例**只登记不扩面**（写完永远跑不到 = 没有靶子的守卫） |
| 改 `entries` / `resolution()` 口径 | 实测**不受影响**（`entries` 37 · `可解析调用点 327` 一个没变），无需改动 |

## 四、验收判据（可复制执行）

```bash
# ① 门禁本体（真树）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_entry_guard.py
#    ⇒ 可见 1185 · 不可见 85（形参转发 37 / 局部变量 46 / 计算式 2）· exit 0

# ② 新判据
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_call_site_dedup

# ③ 229–232 合并回归（口径变了，必须证明没碰坏）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest \
  tests.test_dispatch_entry_guard tests.test_dispatch_resolution \
  tests.test_dispatch_byref_guard tests.test_dispatch_blindspot_guard

# ④ 门禁全套（★ 必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```

## 五、量测结论（本切片的实质产出 · spec 234 的输入）

`local` 桶去重后 **46** 个调用点，**宽读取器**（`output/_probe233_wide.py`）下的候选集可枚举性：

```
★ 可静态枚举 39 / 46   ·   仍不可枚举 7
候选值 distinct 135 · 出现总数 221
读取路径：for 字面量容器 34 · assign 字面量 2 · 模块级 dict 常量 .get() 2 · dict 字面量下标 1
```

⇒ ★★ **「能还原成字符串字面量的有多少」的答案不是 0，而是 39/46** ——
首个读取器（只认「本函数内 `X = "…"`」）读出 0，**是因为读取器太窄**，
不是「不可还原」（「**解析不出 ≠ 不存在**」的又一次实例）。
剩下的 7 处里多数是「迭代对象是**函数局部 dict 字面量**或**元组解包**」，仍可继续收窄。

## 六、未过门 / 未完成

| 项 | 状态 | 触发条件 / 下一步 |
|---|---|---|
| `local` 桶候选集门禁（39 可枚举 + 7 须表态） | **未做** | ★ 下一轮开 `specs/234-*`，量测数据已备齐（§五） |
| `def` 外的调用点不在扫描面内 | **只登记** | 真树实测 **0 处**（潜在盲区、无靶子）；★ 触发条件 = 出现第 1 处 |
| 16 条 arity 不符定罪 / `HEM_POSITIONS` | 未做 | **需业主另行授权 COM** |
| 真机验证 | 未做 | 本切片**纯离线** |
| 提交 / 部署 / 打 tag | 未做 | 硬约束禁止 |

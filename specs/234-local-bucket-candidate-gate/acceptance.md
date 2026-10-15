# acceptance 234 —— `local` 桶调用点的候选集门禁

> 收口时间：2026-10-09（主任务 `ff6c7344` 第 8 轮）· 性质：**纯离线静态判据**
> 未调 COM / 真机 · 未提交 · 未部署 · 未删任何文件 · 未派任何成员 · 未 create/update 任何自动任务。

## 一、交付物

| 件 | 路径 | 状态 |
|---|---|---|
| 门禁 | `scripts/check_dispatch_arg_guard.py` | **新增** |
| 判据 | `tests/test_dispatch_arg_guard.py`（17 例） | **新增** |
| 声明 | `sw_feature_readback.py` · `sw_part.py` · `sw_sheet_metal_weld_entry.py` · `sw_simulation_loadprops.py` · `sw_units.py` | **纯插入 7 行**（零删除） |
| 接线 | `scripts/release_check.py`（`_run_dispatch_arg_guard_gate` + fail 判据 + `_gate_results`） | 改 |
| 登记 | `docs/gate-classification.json`（`classification` 43 → **44**） | 改 |
| 量测 | `output/_probe234_values.py` · `output/_insert234_decls.py` · `output/_reg234_gate.py` | 一次性（**不进仓库代码**） |
| 规格 | `specs/234-local-bucket-candidate-gate/{spec,plan,tasks,acceptance}.md` | 四件齐 |

## 二、判据读数

| # | 判据 | 读数 |
|---|---|---|
| 1 | 门禁本体（真树） | `local 46 · 可枚举 42 · 候选值 distinct 131 · 违规 0 · [PASS] · exit 0` |
| 2 | 新判据 | **Ran 17 tests · OK**（16.5 s） |
| 3 | 229–234 合并回归 | **Ran 73 tests · OK**（163.1 s）★ 证明没碰坏 |
| 4 | 收尾链 `round_chain.ps1` | `release_check: 第 1 轮 OK` · `17 passed` |
| 5 | 门禁全套 `release_check.py` @**3.14.7** | `status pass` · `missing []` · `gates` **42 → 43** · `dispatch_arg_guard: pass` |
| 6 | 登记条目 | `classification` **43 → 44**（★ 与 `gates` **两个数都 +1**） |

## 三、★ 红基线（证明判据真的能红）

**改实现之前**，门禁在真树上首跑：

```
[FAIL] 违规 8 处：
  [undeclared] sw_feature_readback.py:944   —— 候选集枚举不出且未表态
  [undeclared] sw_sheet_metal_weld_entry.py:315 —— 同上
  [undeclared] sw_simulation_loadprops.py:114 / :118 —— 同上
  [undeclared] sw_part.py:1069              —— 候选值查不到且未表态：GetConstrainedStatus2
  [undeclared] sw_sheet_metal_weld_entry.py:223 —— GetSurfaceBodies, GetSurfaceBodyCount
  [undeclared] sw_units.py:113              —— GetSldWorks, IGetSldWorks
  [baseline-shrunk] —— 候选值 distinct 131 < 下界 140
exit 1
```

**合成树端到端负例**（每条判据各一个，`tests/test_dispatch_arg_guard.py`）：

| 负例 | 期望 |
|---|---|
| 候选值查不到 + 未表态 | `[undeclared]` · exit 1 |
| 候选集枚举不出 + 未表态 | `[undeclared]` · exit 1 |
| **能枚举**却声明 `dynamic` | `[invalid-claim]`（「能枚举却声明枚举不出」）· exit 1 |
| 候选值**全查得到**却声明 `probe` | `[invalid-claim]`（「无探测语义」）· exit 1 |
| **枚举不出**却声明 `probe` | `[invalid-claim]`（「该用 `dynamic`」）· exit 1 |
| 零 `local` 调用点 | `[zero-checked]` · exit 1 |
| 下界调高 | `[baseline-shrunk]` · exit 1 |
| **正例**：已覆盖样本 / `dynamic` 带理由 / `probe` 带理由 | exit 0（★ 逃生门**能用**，不是永远红） |

## 四、★★★ 核心事实一：存在性检查必须先量「源的覆盖边界」

`local` 桶 46 个调用点里 **42 个可枚举**，候选值 **131** 个 distinct。逐个查存在性：

| 用的源 | distinct 查不到 | 为什么 |
|---|---|---|
| 只用 `_raw/**/iface_*.txt` | **100** | ★ 转储**只列方法**；属性编码成 `get_X()`/`set_X()`（须**剥前缀**），且 `ICW*StudyOptions` 这类**以接口名命名的属性**只出现在 `## <接口>` 头行 |
| 只用 `C:\swapi\types\<接口>\<成员>.md` | **41** | ★ 该镜像**不含 cosworks/仿真族**（`Quality`/`MesherType`/`MinElementSize`/… 全查不到） |
| **两源并集** | **21** → 修读取器后 **12** | 见下 |

★ **结论**：单源会造 100 / 41 个**假阳性**。⇒ ★★ 「不符」≠「错」——先穷举**源的覆盖边界**再定罪
（与 spec 227「552 条全对、0 条真缺陷」同族）。

## 五、★★★ 核心事实二：读取器自己的两处口径错（同族第三次）

首版读取器把 **`DICT.items()` 与 `DICT.get(k)` 都取成「键」**：

```
_TOPOLOGY_GETTERS = {"mass": "GetMassConstraint", "stress": "GetStressConstraint", ...}
for kind, getter in _TOPOLOGY_GETTERS.items():
    get_com_member(manager, getter, ...)      # ← getter 是**值**（成员名），不是键
```

⇒ 语义键 `mass` / `stress` / `factor_of_safety` / `displacement` / `frequency` /
`preserved_region` / `symmetry` / `demold` / `thickness` 共 **9** 个**冒充成员名**
⇒ 候选值 distinct `140 → **131**`（131 + 9 = 140）。

★ 修法（写成**形态规则**，不是散文）：`.items()` 按**解包下标**取（0 键 / 1 值）；`.get(k)` 取**值**；
并加 6 例读取器判据钉住。
⇒ 与 spec 233 同族：**一个数被反复引用而没人守它 ⇒ 先量它的口径**。

## 六、★ 3 处「试名探测」不是缺陷

| 位置 | 候选名 | 为什么不是缺陷 |
|---|---|---|
| `sw_part.py:1069` | `GetConstrainedStatus` / `GetConstrainedStatus2` | `for _member in (…): try: … except: continue` ⇒ **fallback 列表**，先试一个再试另一个 |
| `sw_sheet_metal_weld_entry.py:223` | `GetSurfaceBodies` / `GetSurfaceBodyCount` | 同上（`_surface_body_count`） |
| `sw_units.py:113` | `GetSldWorks` / `IGetSldWorks` | 同上（`read_units_report` 的兜底取 app） |

⇒ 按 `probe` 表态（「允许含查不到的候选名」），**不改代码、不猜名字**（铁律 5）。

## 七、★ 本轮自己踩到的坑

1. ★★ **`Edit` 插函数又吞掉相邻来源块头**（**第三次**同型）—— `_run_interface_ownership_probe` 的
   `# ── 来源 ──` 两行被吃掉 ⇒ `sed` 复核时发现 ⇒ 已恢复。
2. ★★ **元门禁当场抓到「没进 `_gate_results`」** —— 加了 `_run_*` 与 fail 判据却没登记 ⇒
   `check_gate_wiring.py` 报「`dispatch_arg` 的结果**没有进返回体**」⇒ 已补（第 N 次同型）。
3. ★ **合成树夹具必须同时桩掉被复用门禁的扫描根** —— 新门禁内部 import
   `check_dispatch_entry_guard.scan()`，它读**自己的** `DSH_DISPATCH_ROOT`；只设
   `DSH_DISPATCH_ARG_ROOT` 会让它读**真树** ⇒ 夹具读数被污染。
4. ★ **新门禁让产物过期**：改了 `scripts/` ⇒ 桌面内嵌 Skill 快照与 `harvest-digest.md` 过期
   ⇒ 跑收尾链的生成器即绿（**预期行为，不是缺陷**）。

## 八、未过门 / 未完成

| 项 | 状态 | 触发条件 / 下一步 |
|---|---|---|
| 候选值的**接口归属**（这个名字属于哪个接口） | **不做** | 属 `check_interface_member_ownership.py` 的职责 |
| `probe` / `dynamic` 只做**形态**自证，不验候选值本身对不对 | 登记 | 需真机（COM 授权） |
| `partial` / `unresolved` / `no-callers` 入口的**非字面量**调用点 | **无判据** | ★ 下一轮**先量**，考虑「要求声明」而不是「解析」 |
| 扩 `_entry_sites()` 认别名 | **不做** | ★ 触发条件 = spec 232 门禁**变红**（真树 0 处 ⇒ 无靶子） |
| 16 条 arity 不符定罪 / `HEM_POSITIONS` 真机复核 | 未做 | **需业主另行授权 COM** |
| 223 的 8 条 `HEAD` 即红既有失败 | 未修 | 权属未确认 |
| 真机验证 | 未做 | 本切片**纯离线** |
| 提交 / 部署 / 打 tag | 未做 | 硬约束禁止 |

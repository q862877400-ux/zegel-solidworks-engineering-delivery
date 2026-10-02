# Feature 143 · 仿真载荷族广度（24h 计划 · 段 2.1）—— ★ 工具已挂，真机**未过**，收敛为 `stitched`

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> ★★ **本特性的真机验收 FAIL** ⇒ 按硬约束③**明确标注「未真机验证」**，能力等级 = **`stitched`**。

## 一、要解决的问题

W7（Spec Kit `140`）只挂了**两个**仿真载荷：**夹具** + **法向力**，并真机验过
（`simulation_loads_wiring` = `verified`）。段 2.1 要把**其余常用载荷**补齐 ——
压力 / 力矩 / 重力 / 离心力。

## 二、§5.0 先找后搓的结果

| 序 | 找哪里 | 结果 |
|---|---|---|
| 1 | 四家 live 测试 | **没有**仿真载荷的判据（W7 已核实：三家用「无」，一家是误命中） |
| 2 | ★ **自己的仓库** | ★★ **判据现成**：`tools/capture_simulation_loads_evidence.py` 的判据表 ——「夹具 / 载荷 \| **选区计数 = 1** 且 `LoadsAndRestraintsManager.Count == 2`」⇒ ★ 本批照用 |
| 3 | 自己搓 | ★ 只搓了**回读报告包装**（`apply_*_report`），判据**沿用**既有那条 |

## 三、需求（各带来源）

| # | 需求 | 来源 | 状态 |
|---|---|---|---|
| R1 | 加**压力** | 官方 `ICWLoadsAndRestraintsManager.AddPressure(NPressureType, DispArray, RegGeom, ErrorCode)` | ★ 已挂 · ⚠ **真机未过** |
| R2 | 加**力矩** | 官方 `AddForce(NForceType, DispArray, RefGeom, ErrorCode)`，`swsForceTypeTorque = 2` | ★ 已挂 · ⚠ **真机未过** |
| R3 | 加**重力** | 官方 `AddGravity(DispEntity, ErrorCode)`（★ **单**实体） | ★ 已挂 · ⚠ **真机未过** |
| R4 | 加**离心力** | 官方 `AddCentriFugalForce(DispEntity, ErrorCode)`（★ **单**实体） | ★ 已挂 · ⚠ **真机未过** |
| R5 | ★ 一律**回读**判成败 | 本项目铁律：「COM 返回值凡不能自证，一律以回读为判据」 | ★ 已满足（`count_before` / `count_after`） |

## 四、★ 挂的方式（**第六种包装形状**：`inject` 用**新加的**解析键）

```
★ 这批函数的首参叫 **`manager`**（`ICWLoadsAndRestraintsManager`）⇒ **不可注入**
  （★ 注入名只能是 `RESOLVERS` 的键 —— known-facts 169 的机制）
⇒ ★ 正解 = **给 `RESOLVERS` 加一行 `"manager": resolve_manager`**（W6 给 `asm_model` 加一行的同一手法）
★ 三件套并用（W7 的既有组合）：`inject="manager"` + `pre_call`（选面）+ `derived_args`（补 `model`）
★ `all_specs()` **90 → 94** · `scripts/check_param_binding.py` **PASS**（★ 那道门禁正是为这类漏绑而建的）
```

## 五、⚠⚠⚠ 真机验收 FAIL —— 而它**兑现了源码里早就写着的一句话**

```
★★ 那四个函数的来源块**自己早就写着**（`scripts/sw_simulation_loads.py` 两处）：
     「⚠ 本组为照官方签名新写，**未在本机实测**（见 AGENTS.md 铁律 2）」
⇒ ★★★ 真机一跑，**四类全部失败** ⇒ ★ **那句话被兑现了**。
```

**两轮真机（每轮只动一个变量）：**

| 轮 | `pressure` / `torque` | `gravity` / `centrifugal` |
|---|---|---|
| 第 1 轮（原样） | `-2147352571 类型不匹配 @ arg3` | `-2147352561 非选择性的参数` |
| 第 2 轮（修 `reg_geom`） | `-2147352561 非选择性的参数` | `-2147352561 非选择性的参数` |

```
★ 第 2 轮的「类型不匹配」**消失了** ⇒ ★ **那条修复确实生效**（只是不够）——
  ★★★ 而这是一个**可复现的两态对照**（有诊断价值）。
```

## 六、★★ 已查清 vs **未查清**

| | 内容 |
|---|---|
| ★ **已查清** | ① `RegGeom` / `RefGeom` **不能裸传 `None`**（真机：报错位置 3 就是它）⇒ ★ 已在**能力层**修，改用本项目既有的空 Dispatch 参数包（**已知事实 12**）；② 报错的**位置**指向「**实参形态 / 重载解析**」，**不是**选面、**不是**管理器 |
| ⚠ **未查清** | ★ **为什么 `AddRestraint`（能跑通）与 `AddPressure`（不能）在同样传裸 `list` 的情况下结果相反？** ★ 候选：`AddPressure` 在类型库里有**多个重载**，而 `(int, list, VARIANT)` 匹配不上任何一个（★ COM 的「非选择性的参数」**也可能表示"重载选不出唯一那个"**） |

## 七、不做什么（有据）

| 不做 | 原因 |
|---|---|
| ★ **不继续试第 3、第 4 种数组包装** | ★ **事实 53**：在这个「实参形状」上已改 **2 次**（arity 修正 + `reg_geom`）⇒ **停下**；★ 正路是**先把类型库里 `AddPressure` 的重载表读出来** |
| ★ **不标 `verified`** | ★ **没有真机证据** ⇒ 硬约束③ ⇒ `stitched` |
| ★ **不把 `simulation_loads_wiring` 的 `verified` 用在它身上** | ★★ 那条只覆盖「夹具 + 法向力」**两个** ⇒ ★ 本批四类**不在**那条覆盖面里 |

## 八、验收（如实标注）

```
① 静态：`all_specs()` 出现 4 个新工具（**已达成**：90 → 94）· 门禁链 **18 道** exit 0（**已达成**）
        · `check_param_binding.py` PASS（**已达成**：0 处）
② ★ 真机：`output/loadfamily-evidence.json` 的 `verdict == "pass"`
   ⇒ ⚠ **未达成**（`verdict: fail`，四类全失败 —— ★ 该文件**已如实落盘**）
⇒ ★★ **本特性收敛为「未完成」**：工具在柜台上，但**明确标注「未真机验证」**（`level: stitched`）。
```

## 九、★ 下一步的正路

```
★ ① 读类型库里 `AddPressure` / `AddForce` 的**重载表**（★ 不是继续猜实参形状）
★ ② 用「既有能跑通的 `AddRestraint`」做**同工况对照**，一次只回退一个变量
     （★ 那是本会话反复验证过的手法：known-facts 165 第 12 条）
★ ③ ⚠ 在 ①② 查清之前，本特性**停在 `stitched`**。★ 段 2 的其余候选
     （拓扑挂柜台：读数类 4 个 + 参数类 2 个）**不依赖本条** ⇒ 可以并行推进。
```

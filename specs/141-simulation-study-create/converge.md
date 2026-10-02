# Converge · Feature 141 仿真研究族（建 / 取 / 列）

## 一、交付了什么

| 层 | 文件 | 内容 |
|---|---|---|
| 能力层 | `scripts/sw_simulation.py` | ★ **加 3 个薄函数**（既有四个**一行未改**） |
| 工具层 | `mcp-server/tool_specs_batch27.py`（新增） | 3 个工具（建 / 取 / 列）|
| 注册 | `mcp-server/register_capabilities.py` | `BATCH_MODULES` 加 `tool_specs_batch27` |
| ★ 门禁 | `scripts/check_param_binding.py`（**新增**） | ★★ **参数绑定门禁**（本批的额外产出）|
| ‎ | `scripts/release_check.py` | 接入（第 **18** 道）· `docs/gate-classification.json` 登记 |
| 探针 | `tools/probe_simulation_study_shapes.py`（新增） | 定死三个形状 |
| 证据 | `tools/capture_simulation_study_evidence.py`（新增） | ★ 走工具真实路径 |
| 能力清单 | `capabilities.yaml` | 新增 `simulation_study_create` |

`all_specs()` 从 **83 → 86**。

## 二、★ 本批补的是 **W7 的硬前置**

```
★ W7 的 `limitations` 第一条：「**没有**「建研究」的工具 ⇒ `study_name` 只能引用**已存在**的研究」
⇒ ★ 那意味着**用户必须先手动在 SolidWorks 里建一个研究**
⇒ 本批补上 ⇒ ★ **仿真链从"能用"变成"闭环"（24h 计划 段 1 的第一块基石）。**
```

## 三、★★★ 本批最值钱的一处：**又是同一个 bug，而这次我把它机器化了**

```
★★ 事故史（★ 同一族，两次）：
   · W7（`specs/140`）：对外 `magnitude_n`，能力层形参 `magnitude` ⇒ **漏写 `param_alias`** ⇒ 真机 `TypeError`
   · 本批（`specs/141`）：对外 `study_name`，能力层形参 `name` ⇒ **又漏写** ⇒ **同样的 `TypeError`**
★ 两次都是**"走工具真实路径"的证据脚本当场抓住的**（★ 那条纪律有效）
★★★ 但 W7 之后我把它**记进了 tasks 与套路** —— ★ **而本批照犯** ⇒
   ★ 定则：**"记下来"不等于"下次不犯"。**
⇒ ★★ 所以本批加了 `scripts/check_param_binding.py`：
     判据三条（声明名 ∈ 形参 或 ∈ `param_alias` · `param_alias` 目标名存在 · `inject` ∈ `RESOLVERS`）
     ★ **并接进 `release_check.py`（第 18 道门禁）+ 登记分类**
     ★★ **并用负例证明它抓得住**（临时摘掉 `param_alias` ⇒ exit 1 且精确指出参数名）
   ⇒ ★ 顺带证实：**除刚修的两处，其余 84 个工具的绑定都是对的**。
```

## 四、★ 探针先行的价值（W1 的教训再次生效）

```
★ `iter_studies` **从没被任何工具或证据脚本用过** ⇒ ★ **形状未知**。
   ★ 若直接挂（猜它 yield 字符串）⇒ 会挂一个**回不了的东西**。
⇒ ★ T1 先核，实测：`iter_studies` yield **`(index, study)` 元组**（含 COM 对象）
  ⇒ ★ 三个函数**都要包一层**只回**可 JSON 化**的东西。
★ 另一条实测很重要：`get_study_by_name` 找不到 ⇒ **回 `None`，不抛错**
  ⇒ ★ 对外用**显式 `found` 字段**（避免把「没有」当成「有」）。
```

## 五、收敛判据

| 判据 | 结果 |
|---|---|
| `all_specs()` | 86 |
| 门禁链 | **18 道**全 exit 0（★ 含新门禁）|
| 全量 pytest | **0 failed** |
| 真机证据 `verdict` | `pass`（四条断言：`entry_name` / 回读 / 列出 / 负例）|
| ★ `entry_name` | **`CreateNewStudy3`**（★ 最高版本入口，**非降级**）|
| ★ 新门禁的**负例** | 摘掉 alias ⇒ **exit 1** 且精确指出参数名（★ 门禁**有效**）|

## 六、遗留（明确标注）

| # | 遗留 | 为什么留着 |
|---|---|---|
| L1 | ★ **只支持静力学研究** | 其它类型**未真机验证** ⇒ 不暴露开关（硬约束③）|
| L2 | ★ **重名研究的行为未验** | 能力层不检查重名 ⇒ 如实记，并告诉调用方用 list 回读 |
| L3 | ★ `sw_simulation_study` 的 8 个（`mesh_and_run` / `get_results_of` / `export_study` …）**未挂** | ★ **段 1.2/1.3** 的活 |
| L4 | ★★ **事实 48（内层直引号）本会话已第 N 次** | ⇒ ★ **待办：能不能也给它加道门禁？**（★ 与 `check_param_binding` 同一思路 —— 把反复犯的错**机器化**）|
| L5 | ★ 生成器**顺序**（能力清单是上游） | ★ 已记进 tasks 的 D5；★ 值得写进收工纪律 |

## 七、给下一批的可复用套路（**增至 16 条**）

```
①–⑮ 同前（见 specs/140 的 converge）
⑯ ★★ **反复犯的错，要机器化，不要只"记下来"** ——
   本会话两次漏写 `param_alias`（W7 / 141）⇒ 第二次之后加了 `check_param_binding.py`
   ★ 而且**用负例证明门禁有效**（★ 事实 62：门禁"写了"≠"有效"）。
★ 配套（本批新增的两条工作纪律）：
   · ★ **能力清单是上游** ⇒ 改了它**再**跑依赖它的生成器（`gen_level_audit` 等）
   · ★ **改了模块就要看签名审计表**（`docs/signature-audit.md` 的逐模块调用点数会变；
     ★ 门禁会告诉你新的数字）
```

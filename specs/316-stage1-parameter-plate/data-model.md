# Data Model: 阶段 1 · 经方法入口安全建成参数板（316）

**对应**：`specs/316-stage1-parameter-plate/spec.md` §3 Key Entities

---

## §1 ToolDescriptor（C1 统一目录）

**来源**：`register_capabilities.all_specs()`（476 个）+ `mcp-server/server.py` 的 `@mcp.tool`（45 个）。

```python
@dataclass(frozen=True)
class ToolDescriptor:
    canonical_name: str      #: ★ 规范工具名，如 `solidworks_sketch_start`
    step_name: str           #: ★ 裸步名（方法里写的），如 `sketch_start`
    module: str              #: ★ 实现模块，如 `sw_part`
    function: str            #: ★ 实现函数，如 `start_sketch`
    inject: str              #: ★ 注入宿主（`model` / `sw_app` / `study` / `""`）
    params: tuple            #: ★ 形参名（有序）
    effect: str              #: ★ 效应：`read` / `write` / `unknown`
    admitted: bool           #: ★★ **能否进入执行集**
    reject_reason: str       #: ★ `admitted=False` 时必填（**不许空**）
    source: str              #: ★ 注册来源：`all_specs` / `server_py`
```

### 不变式（机器可查）

| # | 不变式 |
|---|---|
| **I1** | `canonical_name` 唯一（重复 ⇒ 拒绝加载） |
| **I2** | `admitted=False` ⇒ `reject_reason` **非空** |
| **I3** | `admitted=True` ⇒ `step_name` 非空（**没有裸步名就进不了执行集**） |
| **I4** | `admitted=True` ⇒ `module` 与 `function` 都非空（**没有实现地址就进不了**） |
| **I5** | `effect == "unknown"` ⇒ **`admitted=False`**（★ 未知副作用不得自动执行） |

---

## §2 名字解析（C3）

```python
def resolve_step_name(step: str, registry) -> str:
    """裸步名 → 唯一规范工具名。

    ★★ 三种失败都要**显式抛**（★ 不静默、不猜）：
      · 解析不到        ⇒ RejectCode.UNRESOLVED_STEP_NAME
      · 映射到多个规范名 ⇒ RejectCode.AMBIGUOUS_STEP_NAME
      · 解析到但未准入   ⇒ RejectCode.TOOL_NOT_ADMITTED
    """
```

### 映射规则（★ 唯一一条，不搞启发式）

```
step_name == canonical_name 去掉前缀 `solidworks_`
```

**★ 为什么只用这一条**：本仓既有教训（**事实 53**）——
「**启发式需要连续 ≥3 次修补才「看起来对」时，回退 + 记证据**」。
名字回退那一族试过 6 版都不对。**这里只认一条确定性规则**，规则之外一律拒绝。

---

## §3 PlanStep（C2 计划契约）

```python
@dataclass(frozen=True)
class PlanStep:
    step: str                #: ★ 裸步名（★ 与 MethodSpec.steps 里的逐字一致）
    params: dict             #: ★ 参数字典（★ 键是**工具声明的形参名**）
    derive: str = ""         #: ★ 参数的推导说明（**给审核人看的**）
    tool: str = ""           #: ★ 解析后的规范全名（★ 由 resolve 填，不手写）
```

### 不变式

| # | 不变式 |
|---|---|
| **I6** | `tool` **不得**在计划里手写 —— 必须由 `resolve_step_name` 填（★ 防「计划里写裸名而执行器不认识」） |
| **I7** | `params` 的键必须都在该工具的**声明形参**里（★ 多一个就拒绝） |
| **I8** | 单位换算由**工具层**做（`derived_args`）—— 计划里给的是**毫米**，`PlanStep` 不换算 |

---

## §4 ExecutablePlan（C2）

```python
@dataclass(frozen=True)
class ExecutablePlan:
    method_id: str           #: ★ 来自 METHOD_LIBRARY
    steps: tuple             #: ★ PlanStep 元组（★ 顺序即语义）
    device_class: str = ""   #: ★ 适用性检查用
```

---

## §5 AuthorizationVerdict（C5）

```python
@dataclass(frozen=True)
class AuthorizationVerdict:
    ok: bool
    code: str = ""           #: ★ 封闭码（见下）
    detail: str = ""
```

### 封闭码

| 码 | 触发 |
|---|---|
| `TOOL_NOT_ADMITTED` | 工具未准入（`admitted=False`） |
| `PATH_OUTSIDE_WORKSPACE` | 写盘路径不在 `D:\AI\SW` 内 |
| `DOCUMENT_NOT_OWNED` | 目标文档不是**本任务创建**的 |
| `EFFECT_UNKNOWN` | 效应未知 |
| `PLAN_NOT_COMPILED` | 计划没经编译器（★ 防绕过） |

**★ 封闭码的纪律**：新增码必须同时加进 `AUTH_CODES`，否则 `assert` 拦下。

---

## §6 ExecutionRecord（C6）

```python
@dataclass
class ExecutionRecord:
    step: str
    tool: str
    params: dict
    intent_at: str = ""      #: ★ 写 COM **之前**落盘
    result: str = ""
    com_write_count: int = 0 #: ★ 该步触达 COM 写调用的次数
    error: str = ""
```

### 不变式

| # | 不变式 |
|---|---|
| **I9** | 每次写 COM 前，`intent_at` 必须已落盘（★ 否则崩了不知道干到哪） |
| **I10** | `com_write_count` 由**调用计数器**给，**不是**返回值（★ 事实 8：返回值不可信） |

---

## §7 COM 写调用计数器（★ SC-009 的判据工具）

**为什么需要它**：SC-009 要求「负例的 COM 写调用数全部为 0」。
**返回值不可信**（事实 8）⇒ 必须**在 COM 边界计数**。

```python
class ComWriteCounter:
    """★ 包在 COM 边界上的计数器（★ 负例判据的唯一来源）。"""

    def count(self) -> int: ...
    def reset(self) -> None: ...
    def assert_zero(self, why: str) -> None:
        """★ 不为 0 就抛 —— 负例必须证明「一次都没写」。"""
```

**★ 怎么接**：在 `scripts/sw_connect.get_com_member` 的**写侧**（`set_com_member` /
`call_com_member`）加钩子；只读路径**不计数**。

---

## §8 三个真机用例（SC-001）

| # | 板尺寸（mm） | 拉伸深度（mm） | 倒角（mm） | 期望体积（mm³） |
|---|---|---|---|---|
| **1** | 100 × 60 | 20 | 2 | 120000 − 倒角损耗 |
| **2** | 80 × 50 | 12 | 1.5 | 48000 − 损耗 |
| **3** | 150 × 100 | 25 | 3 | 375000 − 损耗 |

**★ 体积判据的算法**：倒角沿**一条边**做 ⇒ 损耗 = `0.5 × c² × L`（`L` = 该边长度）。
**冻结容差**：相对误差 **≤1e-6**（规格 §4 SC-002）。

> ⚠ **三个用例必须独立启动**（各自新进程）—— 那是 SC-001 的「独立启动」要求，
> 也是防「依赖前次进程状态」这类假通过。

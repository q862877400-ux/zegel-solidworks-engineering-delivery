# Data Model: 阶段 3 · 中断后能续，不重复打孔、不误认完成（318）

**对应**：`specs/318-stage3-crash-recovery/spec.md` §3 Key Entities

---

## §1 Checkpoint（E1 · 检查点）

```python
@dataclass
class Checkpoint:
    stage: str                #: ★ 阶段名（如 `sketch_add_circle`）
    intent_at: str            #: ★ **意图落盘的时刻**（★ 写 COM **之前**）
    artifact: str = ""        #: ★ 该阶段的产物（相对路径）
    revision: str = ""        #: ★ 产物版本
    evidence: str = ""        #: ★ 证据（sha256 或回读值）
    state: str = "intent"     #: `intent` / `applied` / `committed`
```

### 三态与三类崩溃窗口的对应（★ 核心）

| 状态 | 含义 | 崩在这里会怎样 |
|---|---|---|
| `intent` | 意图已落盘，**COM 还没调** | ★ 窗口① —— 重放**安全**（还没生效） |
| `applied` | COM 已生效，**结果还没记账** | ★ 窗口② —— 重放**危险**（会重复打孔）⇒ **必须回读判** |
| `committed` | 结果已记账 + 证据齐 | ✅ 安全 |

**★★ 判据（FR-004）**：`COMMITTED` **只能**由 `applied + evidence` 升上来 ——
★ 「工具返回成功」**不足以**升级（★ 那是 P1 突变要抓的）。

---

## §2 CommitManifest（E1 · 提交清单）

```python
@dataclass
class CommitManifest:
    entries: list = field(default_factory=list)   #: 已提交的 Checkpoint
    revision: str = ""

    def add(self, cp: Checkpoint) -> None:
        """★ **只接受带证据的 `applied`**（★ 否则拒绝 —— ★ 防无证据 COMMITTED）。"""

    @property
    def complete(self) -> bool: ...
    def references_incomplete(self) -> list:
        """★ 引用了**不完整文件**的条目（★ SC-005）。"""
```

### 不变式

| # | 不变式 |
|---|---|
| **K1** | 入清单的检查点**必须**有非空 `evidence` |
| **K2** | 入清单的检查点**必须**是 `applied`（★ 不是 `intent`） |
| **K3** | 清单**不得**引用 sha256 为空的文件 |
| **K4** | 清单的 `revision` **唯一**（★ 冲突 ⇒ `REVISION_CONFLICT`） |

---

## §3 InvalidationClosure（E2 · 失效闭包）

```python
@dataclass
class InvalidationClosure:
    changed: list = field(default_factory=list)   #: 变了哪几个版本（`contract`/`plan`/`model`）
    stale_nodes: list = field(default_factory=list)
    untouched_nodes: list = field(default_factory=list)
```

### 怎么算（★ 判据：**依赖图**，不是「全都标脏」）

```
输入：nodes = [{name, depends_on: [版本键], ...}]
      changed = 变了的版本键（来自 `VersionBinding.invalidated_by`）

① 直接依赖 changed 的节点 ⇒ STALE
② 传递依赖 ① 的节点     ⇒ STALE（★ 闭包）
③ 其余节点             ⇒ untouched（★ **不得**被无故清空 —— FR-007）
```

**★★ 为什么不能「全都标脏」**：那是**保守到失去能力** ——
★ 阶段 6 的反向验证专门抓这一类（「将一切图中有环都拒绝」必须失败）。
★ 同族纪律：**只改一个变量检验一个失效机制**（S3-B ④）。

---

## §4 ResumeVerdict（E3 · 恢复判定）

```python
@dataclass(frozen=True)
class ResumeVerdict:
    ok: bool
    code: str = ""       #: `REVISION_CONFLICT` / `STALE` / `UNKNOWN_EFFECT`
    detail: str = ""
```

### 封闭码（★ 新增码必须同时加进 `RESUME_CODES`）

| 码 | 触发 |
|---|---|
| `REVISION_CONFLICT` | 提交的 revision ≠ 当前（★ **不接受**） |
| `STALE` | 相关节点已失效（★ 要重新验证） |
| `UNKNOWN_EFFECT` | 效应不明（★ 不重试、不标完成） |

---

## §5 UNKNOWN_EFFECT（E4）

**★ 与 `JobState.UNCERTAIN` 的分工**（★ 两个都要，不是替代）：

| 状态 | 含义 | 处置 |
|---|---|---|
| `UNCERTAIN` | 超时/语义不明的 **COM 错误** | ★ **不重试**（`NEVER_RETRY_FROM`） |
| `UNKNOWN_EFFECT` | ★★ **这个工具到底写没写**都不知道 | ★ **不重试 + 不标完成 + 必须回读** |

**★ 为什么要有第二个**：`UNCERTAIN` 说的是「**调用**结果不明」，
`UNKNOWN_EFFECT` 说的是「**效应**不明」—— ★ 前者可以靠回读补救，
后者**连该回读什么都不知道** ⇒ 必须**停下交人**。

---

## §6 三类崩溃窗口的注入（E1 · 验收 S3-A）

| # | 窗口 | 怎么注入 | 恢复判据 |
|---|---|---|---|
| **①** | **意图落盘后调用前** | 在 `intent` 之后、COM 之前抛 | ★ 重放**安全**（还没生效）⇒ 恢复后几何**与无故障等价** |
| **②** | **操作已生效但结果未记账** | 在 `applied` 之后、记账之前抛 | ★★ 重放**危险** ⇒ **必须先回读**；回读说「已有」⇒ **跳过**（★ 不重复打孔） |
| **③** | **CAD 已保存但提交清单未发布** | 在保存之后、`manifest.add` 之前抛 | ★ 恢复后**清单与真实文件一致** |

**★ 每种重复 3 次 ⇒ 9/9。**

**★★ 等价判据（SC-002）**：几何 / 孔数 / 参数 / 依赖 / 交付内容 —— **五项都要等价**。
★ 不是「没崩就行」—— ★ 是「**结果与无故障参考一样**」。

---

## §7 反向验证（★ 规格 §5）

| # | 突变 | 怎么造 | 怎么抓 |
|---|---|---|---|
| **P1** | 把「工具返回成功」当提交完成 | 直接 `manifest.add(Checkpoint(state="intent"))` 或证据为空 | ★ K1/K2 不变式 ⇒ **抛** |
| **P2** | 取消重放前的检查点分支隔离 | 恢复时**不查**检查点，直接重放全部 | ★ 副作用计数 > 1 ⇒ **夹具失败** |
| **P3** | 移除某个依赖摘要比较 | 从 `depends_on` 里去掉一个版本键 | ★ 该依赖变化时节点**不标脏** ⇒ 回归测试**发现** |

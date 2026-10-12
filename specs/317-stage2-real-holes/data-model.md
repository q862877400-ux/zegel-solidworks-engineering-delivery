# Data Model: 阶段 2 · 真实孔组、规则、工程图与参数变更（317）

**对应**：`specs/317-stage2-real-holes/spec.md` §3 Key Entities

---

## §1 ExpandedPlan（D1 子方法展开）

```python
@dataclass(frozen=True)
class ExpandedPlan:
    method_id: str
    steps: tuple            #: ★ 全是**工具**步骤（★ 不得再有方法 id）
    expand_trace: tuple     #: ★ 展开过程（★ 审计用）
    device_class: str = ""
```

### 展开规则（★ 唯一一条，不搞启发式）

```
方法 id 形式的 step ⇒ 用 METHOD_LIBRARY[step].steps 替换
工具形式的 step     ⇒ 保留
```

**★ 参数传递**：子方法的参数来自父步骤的 `params`（★ 同名键透传）。

### 不变式

| # | 不变式 |
|---|---|
| **J1** | 展开后**递归可解析**（★ 每个 step 都能 `resolve_step_name`） |
| **J2** | 展开深度 ≤ `MAX_DEPTH`（★ 防循环） |
| **J3** | 展开**不丢参数**（★ 父步骤的 `params` 里同名键要传下去） |
| **J4** | `expand_trace` 记录每一步的替换（★ 可审计） |

---

## §2 DatumSpec（D2 共享基准）

```python
@dataclass(frozen=True)
class DatumSpec:
    name: str                #: ★ 基准名（★ 多步共用）
    role: str = "primary"    #: `primary` / `secondary`
    source_step: str = ""    #: ★ 哪个步骤建立它
```

### 怎么用

`PlanStep.datums` 声明它用哪些基准：

```python
R.PlanStep(step="sketch_start", params={"plane_name": "Front Plane"},
           datums=("板主平面",))
```

**★ 判据（J5）**：改基准名 ⇒ **所有引用它的步骤都改**（★ 靠 `datums` 索引查）。

---

## §3 RuleOutcome（D3 七档规则评价）

```python
@dataclass(frozen=True)
class RuleOutcome:
    verdict: str             #: ★ 七档之一（★ 封闭集）
    rule_id: str
    citation: str = ""       #: ★ 标准号 + 条款
    detail: str = ""
```

### 七档（★ 封闭集 —— 新增档必须同时加进 `ALL_VERDICTS`）

| 档 | 触发 | 机器判据 |
|---|---|---|
| `PASS` | 满足要求 | `inputs` 齐 + `citation` 有 + `effectiveness=effective` + 计算结果满足 |
| `FAIL` | 明确违反 | 计算完成且**不满足** |
| `RuleError(MISSING_INPUT)` | 缺必填量 | `required_inputs` 里有缺失 |
| `RuleError(UNIT_MISMATCH)` | 单位错误 | 输入单位 ≠ 规则声明单位 |
| `NOT_APPLICABLE` | 超适用范围 | 输入超出 `applicability` 区间 |
| `INDETERMINATE(SOURCE_MISSING)` | 缺原文 | `citation` 为空 / 源查不到 |
| `INDETERMINATE(STATUS_UNKNOWN)` | 效力未知 | `effectiveness` 是 `unknown` |

### ★★ 判据顺序（**最严的在前** —— 防"缺依据却算得出数"）

```
① 缺必填量          ⇒ RuleError(MISSING_INPUT)
② 单位不符          ⇒ RuleError(UNIT_MISMATCH)
③ 超适用范围        ⇒ NOT_APPLICABLE
④ 缺原文            ⇒ INDETERMINATE(SOURCE_MISSING)
⑤ 效力未知          ⇒ INDETERMINATE(STATUS_UNKNOWN)
⑥ 算得出且满足      ⇒ PASS
⑦ 算得出且不满足    ⇒ FAIL
```

**★★ 为什么这个顺序**：**④⑤ 必须在 ⑥ 之前** ——
否则「缺原文但公式算得出数」会**报 PASS**（★ 那正是 N3 突变要抓的）。

### 不变式

| # | 不变式 |
|---|---|
| **J6** | `verdict` 必须在封闭集里 |
| **J7** | **缺依据（无 citation）⇒ 不得 `PASS`**（★ FR-007） |
| **J8** | **效力未知 ⇒ 不得 `PASS`**（★ FR-008） |
| **J9** | `RELEASING = (PASS,)` —— ★ 只有 PASS 能放行 |

---

## §4 DrawingObligation（D4 图纸义务）

```python
@dataclass
class DrawingObligation:
    name: str                #: 如「板宽 100」「材料 45 钢」
    kind: str                #: `dimension` / `note` / `tolerance`
    covered: bool = False
    evidence: str = ""
```

### 覆盖率判据（SC-005）

```
coverage = covered 数 / 全部义务数
★ 要求 = 1.0（100%）
```

**★ 义务从哪来**：由**方法**声明（`MethodSpec.verification_obligations`），
不是手工列（★ 那样会漏）。

---

## §5 ArtifactDigest（D5 变更传播 / 防旧版本混入）

```python
@dataclass(frozen=True)
class ArtifactDigest:
    path: str
    sha256: str
    kind: str                #: `model` / `drawing` / `report`
    revision: str = ""
```

### 判据（J10 / SC-006 / SC-010）

```
① 三类产物（model / drawing / report）**都存在**
② 三者的 `revision` **一致**
③ 变更后，每类的 sha256 **都变了**（★ 没变 ⇒ 旧版本混入）
```

**★★ N2 突变怎么抓**：让图纸**保留旧版本** ⇒ 它的 sha256 不变 ⇒ ③ 失败。

---

## §6 反向验证的三类突变（★ spec §5）

| # | 突变 | 怎么造 | 怎么抓 |
|---|---|---|---|
| **N1** | 孔步骤**只返回成功而不执行** | 用一个 `dry_run` 的孔步骤 | ★ **回读几何**（孔数 = 0）⇒ 发现 |
| **N2** | 图纸**保留旧版本** | 不重新导出图纸 | ★ **sha256 不变** ⇒ 发现 |
| **N3** | 规则**缺证据分支改成默认通过** | 把 `INDETERMINATE` 改成 `PASS` | ★ `verdict` 不在放行集 ⇒ 发现 |

---

## §7 真机三用例（SC-007）

| # | 板（mm） | 孔（个 × φ） | 孔位（mm） | 期望体积（mm³） |
|---|---|---|---|---|
| **1** | 100 × 60 × 20 | 4 × φ6 | 四角，距边 10 | 120000 − 4·π·9·20 |
| **2** | 80 × 50 × 12 | 2 × φ8 | 中心线上，间距 30 | 48000 − 2·π·16·12 |
| **3** | 150 × 100 × 25 | 6 × φ5 | 两排三列，间距 40/30 | 375000 − 6·π·6.25·25 |

**★ 每个用例独立启动**（★ 三次进程）。
**★ 每个用例出工程图 + PDF**（★ SC-004）。

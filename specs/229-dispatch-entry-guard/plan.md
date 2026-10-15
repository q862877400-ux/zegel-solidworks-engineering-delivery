# plan 229 —— 分发口守卫覆盖门禁

> 特性目录：`specs/229-dispatch-entry-guard/`

## 一、三源与冲突裁决顺序

| 源 | 位置 | 本切片用它做什么 | 可信度 |
|---|---|---|---|
| ① 本仓源码 AST | `scripts/**/*.py` | 分发口集合、调用点分类计数 | **唯一事实源**（机器可重跑） |
| ② `C:/swapi` 官方页 | — | **本切片不用**（不判语义，只判「有没有表态」） | — |
| ③ CHM 解包 / `_raw` 反射转储 | `_raw/**/iface_*.txt` | **本切片不用**（不需要签名；门禁因此没有 SKIP 路径） | — |

★ 三源冲突裁决顺序（本仓通则）：**官方页 > 出厂反射转储 > 本仓既有登记**。
本切片**不涉及**语义裁决 —— 它判的是「**有没有表态**」，而表态的**内容**由人写死（§二）。

## 二、契约（**由人写死**，门禁只负责「按你写的查」）

### 2.1 声明的关联方式（**确定性**）

`def` **正上方**、**跳过空行**后的**第一行非空行**必须是声明：

```
#: dispatch-guard: <head> [rest]
```

★ **不用行窗口启发式** —— 225 实测：`lines[lo-15 : hi]` 那类窗口对「插入注释」敏感
（给某表上方插注释会把它自己或邻表挤出窗口，改变分类结果）。★ 227 的结论同源：
「声明的关联方式用『向上跳过空行取第一行非空行』」。

### 2.2 封闭词表与**自证条件**

| 声明 | `code` | 门禁自证条件（不满足即红） |
|---|---|---|
| `#: dispatch-guard: covered <gate-id>` | `covered` | `<gate-id>` ∈ `docs/gate-classification.json` 的 `classification[].gate`（**承重性**）|
| `#: dispatch-guard: covered-wrappers` | `covered-wrappers` | 该 `def` 名 ∈ `audit_call_arity.WRAPPERS` |
| `#: dispatch-guard: exempt generated-api` | `generated-api` | 文件名匹配 `sw_api_*.py` |
| `#: dispatch-guard: exempt internal-helper` | `internal-helper` | `def` 名以 `_` 开头 |
| `#: dispatch-guard: exempt module-local` | `module-local` | 该 `def` 名**全仓只此一处定义**，且**所有调用点都在本文件内** |
| 其他 | — | **未知 code ⇒ 红**；`exempt` 后不是恰好一个子码 ⇒ **格式不合法 ⇒ 红** |

### 2.3 分发口的定义（判定规则，写成代码）

> `def` 体内存在一次调用，其函数名 ∈ `WRAPPERS`，**第二实参不是字符串字面量**，
> 且该实参是一个 `Name` **且是该 `def` 自己的形参**。

★ 每个 `def` **最多登记一条**（取最先出现的那个调用点）。

## 三、实施步骤（含**先证能红**）

| 步 | 动作 | 判据 |
|---|---|---|
| S1 | 写门禁本体 `scripts/check_dispatch_entry_guard.py` | — |
| S2 | ★ **先跑，拿红基线** | `[FAIL] 违规 37 处` · 全部 `undeclared` · `exit 1` |
| S3 | 写施工脚本 `output/_add_229_declarations.py`（**纯插入、幂等**）并跑 | 插入 37 行；复跑 `插入 = 0` |
| S4 | 复跑门禁 | `分发口 37 · 已表态 37 · 违规 0 · [PASS] · exit 0` |
| S5 | 写判据 `tests/test_dispatch_entry_guard.py`（20 例） | `Ran 20 tests · OK` |
| S6 | 接进 `release_check.py`（函数 + 调用点 + `raise` + `_gate_results`） | 见 tasks T-229-05 |
| S7 | 登记 `docs/gate-classification.json`（40 → 41，**+6 行**） | 见 tasks T-229-06 |
| S8 | 收尾链 `round_chain.ps1` | `release_check 第 1 轮 OK` |

## 四、★ 风险与处置

| 风险 | 处置 |
|---|---|
| 往 30+ 个文件插注释行 ⇒ **行号移位** | ① 判据一律**按名字/表名定位，不按行号**（本仓纪律）；② 施工脚本**纯插入零删除**；③ 收尾链会跑全套门禁验证 |
| 插进**生成模块**（`sw_api_*.py`）被下次重生成冲掉 | 生成物是**抄录**，重生成只覆盖内容块；若被冲掉，门禁**会红**（未表态）⇒ 不会静默失效 |
| 判据变成**空判据**（真树 0 个分发口也 PASS） | FR-007 假绿守卫 + `test_real_tree_is_green_and_nonvacuous` 断言真树 ≥37 |
| 下界常量被「顺手改小」以消红 | FR-006 下界冻结 + `test_baseline_shrink_is_red`（**证明下界承重**）|
| 豁免声明被读成「已验证安全」 | spec §三 明写语义；门禁输出打印**不可见调用点总数**，让盲区一直可见 |

## 五、验证（可跑的命令）

见 `tasks.md` 每条的验收块。判据解释器：受管 **3.13.12**（桩掉 COM，本门禁不碰 COM）；
门禁全套：**3.14.7**（受管 3.13.12 缺 comtypes/win32com ⇒ 交互式提示 ⇒ 假红 + 挂死风险）。

# plan 234 —— `local` 桶调用点的候选集门禁

## 一、三源与冲突裁决顺序

| 源 | 路径 | 用途 | 可达性 |
|---|---|---|---|
| **出厂反射转储** | `_raw/**/iface_*.txt` | 成员名存在性（★ 属性编码为 `get_X()`/`set_X()`；接口名另有 `## <接口>` 头行） | 仓内 |
| **官方文档镜像** | `C:\swapi\types\<接口>\<成员>.md` | 成员名存在性（★ **含属性页**；反射转储里没有属性名） | 本机 |
| **源码 AST** | `scripts/**/*.py` | 调用点与候选集（唯一真源） | 仓内 |

**冲突裁决顺序**：① 源码 AST（事实）→ ② 官方文档镜像 → ③ 出厂反射转储。
两源是**并集**（任一命中即「查得到」）；**都不命中**才算「查不到」⇒ 走 FR-004 表态。

★ **为什么必须并集**：单用反射转储 ⇒ 属性名全查不到（实测 **100** 个 distinct 假阳性）；
单用 swapi ⇒ 仿真族（cosworks）成员全查不到（实测 **41** 个 distinct 假阳性）。
⇒ 「不符」≠「错」：先穷举约定与源覆盖边界，再定罪（spec 227 教训）。

## 二、实现落点

| 件 | 路径 | 动作 |
|---|---|---|
| 门禁 | `scripts/check_dispatch_arg_guard.py` | **新增**（读取器 + 存在性 + 表态 + 下界 + 零检查 + 口径一致性断言） |
| 判据 | `tests/test_dispatch_arg_guard.py` | **新增**（17 例：真树 1 + 端到端 10 + 读取器 6） |
| 声明 | `scripts/{sw_feature_readback,sw_part,sw_sheet_metal_weld_entry,sw_simulation_loadprops,sw_units}.py` | **纯插入 7 行** `#: dispatch-arg: …`（零删除） |
| 接线 | `scripts/release_check.py` | 新增 `_run_dispatch_arg_guard_gate` + fail 判据 + `_gate_results` 登记 |
| 登记 | `docs/gate-classification.json` | `classification` **43 → 44** |
| 量测 | `output/_probe234_values.py` · `output/_insert234_decls.py` · `output/_reg234_gate.py` | 一次性探针/脚本（**不进仓库代码**） |
| 规格 | `specs/234-local-bucket-candidate-gate/{spec,plan,tasks,acceptance}.md` | 四件齐 |

## 三、口径复用（不重写）

| 口径 | 来源 |
|---|---|
| 包装器名集合 `WRAPPERS` | `audit_call_arity.WRAPPERS` |
| 形参提取 / 取点 / 嵌套去重 | `check_dispatch_entry_guard.{_params, scan}`（★ `local_sites()` 镜像同一口径 + **一致性断言**） |
| 声明关联方式 | 与 227/228/229 同一确定性规则（向上跳过空行取第一行非空行） |

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| 读取器太窄 ⇒ 读出 0（「0 看起来像结论」） | 读不出返回 `None`（**不静默降级成空集**）+ 下界冻结 + 读取器 6 例判据 |
| 读取器太宽 ⇒ 假阳性 | 形态清单是**封闭**的；`.items()` / `.get()` **按位置/语义**取值（本切片修掉的两处口径错） |
| 逃生门被滥用 | 两个 code 各带**自证条件**（三向反例判据） |
| 门禁自己另起一套口径 | `len(local_sites) == buckets["local"]` 硬断言 |
| 新门禁让产物过期 | 已知：首跑报 `harvest-digest.md` 不一致 ⇒ 跑生成器即绿（预期行为） |

## 五、施工顺序（本切片实际执行）

1. 先量（`_probe234_values.py`）：候选值 distinct / 两源命中率 → 定存在性检查可行。
2. **先写判据**：门禁首跑**红基线** `[undeclared] 7 + [baseline-shrunk] 1` ⇒ exit 1（证明能红）。
3. 再改实现：补 7 处声明（纯插入）→ 绿。
4. 修读取器两处口径错（`.items()` 取键 → **按位置**；`.get()` 取键 → **取值**），下界 140 → 131。
5. 接线 `release_check.py` + 登记 `gate-classification.json`（元门禁当场抓到「没进 `_gate_results`」⇒ 已补）。
6. 收尾链 → 门禁全套（3.14.7）→ 合并回归。

# S1 覆盖表 · 要求 → 检查 → 原始证据

**Feature**: `349-e1-e7-acceptance`

**收口日期**: 2026-10-25

---

## 一、七条判据的落点

| 判据 | 采集器 | 判定器 | 必须能拒绝的负例 | 样件 |
|---|---|---|---|---|
| **E1** 草图全约束 | `acceptance/e1_sketch.py:collect_sketch_constraint` | `judge_sketch_constraint` | 删定位关系 / 删尺寸 / 重复关系 / 全固定无驱动参数 / 采集失败 | `bad_e1_duplicate_relation` · `bad_e1_all_fixed_no_dimension` · `unknown_e1` |
| **E2** 参数化可重建 | `acceptance/e2_e3_solid.py:collect_rebuild` | `judge_rebuild` | 只改属性没改模型 / 孔未随板宽变化 / 旧图纸 / 重建失败 / **新建文档冒充实改** | `bad_e2_new_document` · `bad_e2_no_downstream` · `unknown_e2` |
| **E3** 特征树可编辑 | `collect_feature_tree` | `judge_feature_tree` | 导入死实体 / 悬空引用 / 错误配置 / 目标对象漂移 | `bad_e3_imported_solid` · `bad_e3_dangling` · `unknown_e3` |
| **E4** 装配自由度闭合 | `acceptance/e4_assembly.py:collect_assembly` | `judge_assembly` | 重复同一配合 / 全固定冒充 / 错轴错向 / 漏配合 / 干涉 / 无间隙依据 | `bad_e4_duplicate_mate` · `bad_e4_interference` · `unknown_e4` |
| **E5** 图样合规 | `acceptance/e5_e6_drawing.py:collect_drawing` | `judge_drawing` | 孔位标错 / 少关键尺寸 / 错误基准 / 旧模型视图 / 默认材料 / **空 evidence** | `bad_e5_empty_evidence` · `bad_e5_missing_item` · `bad_e5_stale_drawing` · `unknown_e5` |
| **E6** 工艺可行 | `collect_process` | `judge_process` | 刀具进不去 / 无加工基准 / 越过已验证范围 / 删除必需检查 / **全不适用** | `bad_e6_tool_unreachable` · `bad_e6_all_not_applicable` · `unknown_e6` |
| **E7** 结论可溯源 | `acceptance/e7_provenance.py:collect_provenance` | `judge_provenance` | 假引用 / 摘要冒原文 / 旧版本证据 / 随意填来源标签 / **空 citations** / 缺文件 | `bad_e7_no_citations` · `bad_e7_fake_source` · `bad_e7_stale_evidence` · `unknown_e7` |

「不能当替代品」逐条写在每个判定器的模块 docstring 里，
并在判定器代码里对应到具体分支（例如 E2 的 `opened_existing` 检查）。

## 二、四类伪造手法（实测过的洞）

| 编号 | 洞在哪 | 伪造方式 | 旧行为（实测） | 新判定器 |
|---|---|---|---|---|
| **R-04** | `part_loop.DofPlan.total_dof` | 同一条草图关系重复 8 次 | DOF = 0，`is_acceptable()["ok"] = True` | 按关系唯一性去重；含重复即 `fail` |
| **R-05** | `assembly.ConstraintGraph.total_dof` | 同一对组件重复贴 6 次 coincident | DOF = 0，`verdict = fully_constrained` | 检查「同组件对 + 同配合类型」的重复；含重复即 `fail` |
| **R-06** | `drawing_obligations.coverage` | `mark_covered(obls, name)` 用默认空 evidence | `ratio = 1.0`，`ok = True` | 要求每条 covered 有非空证据 |
| **R-09** | `rule_service.evaluate_rule` | 两个布尔 + 来源标签 | `PASS`，但 `outputs={}`、`citations=[]` | 要求引用非空且可解析、有可复算输出 |

★ 每条都有**两个**测试：
- 「新判定器拒绝它」（`test_伪造N_...`）
- 「旧估算器确实会被骗」（`test_伪造N_对照_...`）

第二个测试的作用是**证明这个洞真的存在**，不是在防一个假设的漏洞。

出处：`docs/state/facts/R-engineering-path.md` R-04 / R-05 / R-06 / R-09。

## 三、统一结果结构（11 个必填字段）

`acceptance/result.py:CheckResult`

| # | 字段 | 说明 |
|---|---|---|
| ① | `check_id` | 检查 ID（如 `E1.dof`） |
| ② | `requirement_id` | 要求 ID |
| ③ | `target` | 对象 / 配置 |
| ④ | `observation_complete` | 观测是否完整 |
| ⑤ | `observed` + `unit` | 原始值与单位 |
| ⑥ | `expected` + `basis` | 期望值与依据 |
| ⑦ | `status` | 四值枚举 |
| ⑧ | `reason` | 原因 |
| ⑨ | `evidence` | 证据引用 |
| ⑩ | `artifact_version` | 产物版本 |
| ⑪ | `checker_version` | 检查器版本 |

### 两条硬不变式（在 `__post_init__` 里强制）

1. **`observation_complete=False` ⇒ `status` 必须是 `unknown`**
   —— 采集失败不可能判 pass 或 fail，构造时即抛 `ValueError`
2. **`status` 必须是 `Status` 枚举**
   —— 传裸字符串 `"pass"` 抛 `TypeError`，堵住「非空字符串当 true」

## 四、四值状态的语义

| 状态 | 含义 | 让报告变绿？ |
|---|---|---|
| `pass` | 取到了数，且符合要求 | ✅ |
| `fail` | 取到了数，但不符合要求 ⇒ **产物不合格** | ❌ |
| `unknown` | 没取到数（采集失败 / 上游失败 / 对象未覆盖） | ❌ |
| `not_applicable` | 不适用，且**有理由** | ✅ |

★★ **`unknown` 不是 `fail` 的别名**：
把 `unknown` 当 `fail` 会把「我们没测」说成「产品坏了」；
把 `unknown` 当 `pass` 就是自我认证。

`rollup()` 的判据：**任一 `fail` 或任一 `unknown` 都使整体不绿**；空结果集也不绿。

## 五、既有估算器已降级为预检

四处都在 docstring 里写明「预检用途，不得直接授权交付」，并指向对应的新判定器：

| 文件 | 函数 | 指向 |
|---|---|---|
| `scripts/engineering/part_loop.py` | `DofPlan.total_dof` | `e1_sketch.judge_sketch_constraint` |
| `scripts/engineering/assembly.py` | `ConstraintGraph.total_dof` | `e4_assembly.judge_assembly` |
| `scripts/engineering/drawing_obligations.py` | `coverage` | `e5_e6_drawing.judge_drawing` |
| `scripts/engineering/rule_service.py` | `evaluate_rule` | `e7_provenance.judge_provenance` |

**没有改它们的算法** —— 动算法等于在判据还没建好时先改实现，无法证明改对了。

## 六、读数

```
python -B -m pytest tests/test_acceptance_e1_e7.py \
  tests/test_acceptance_forgery.py tests/test_acceptance_contract.py -q
→ 134 passed

连同既有工程层测试：
python -B -m pytest tests/test_acceptance_*.py tests/test_stage2_rules.py \
  tests/test_stage4_planner.py -q
→ 182 passed
```

| 测试文件 | 条数 | 覆盖什么 |
|---|---:|---|
| `test_acceptance_e1_e7.py` | 80 | 三态判定（每条 E 的 pass / fail / unknown）+ 11 字段齐 + 坏样件原因具体 + 七条都有三态 |
| `test_acceptance_forgery.py` | 12 | 四条伪造负例 + 四条反证（证明旧估算器真的会被骗） |
| `test_acceptance_contract.py` | 42 | 采集器不判断 / 判定器不取数 / 观测不完整必 unknown / 状态枚举 / 外部 verdict 映射 / rollup |

## 七、这一步到此为止：只叫「离线判据成立」

按 `docs/ENGINEERING-PATH.md` 第六节 S1 完成标准：

> 此时只叫 **离线判据成立**，不叫 E1–E7 真机通过。

本 spec 的采集器全部吃**合成样件**，没有一条从真实 SolidWorks 产物取数。
真机采集器是 S3/S4 的工作，需要先按铁律 4 三源互证查清成员名。

## 八、明确没做的

- **没有**接真机采集器（留 S3/S4）
- **没有**改四个既有估算器的算法（只加标注）
- **没有**杜撰任何 SolidWorks 成员名
- **没有**声称 E1–E7 真机通过
- **没有**给 `not_applicable` 提供自动判定 —— 它必须由判定器显式给出理由
  （首件的 E4/E6 不得靠列「不适用」通过，这条由 S4 的 `judge_*` 把关）

# S1 覆盖表 · 要求 → 检查 → 原始证据

**Feature**: `349-e1-e7-acceptance`

**收口日期**: 2026-10-25

---

## 零、汇总层：report.py

10 条检查彼此孤立，每条只回答「我这一项如何」。而 AGENTS.md 判据 A8 要的是
「首件 E1–E7 **逐条状态与证据变化**」⇒ 需要一层汇总。

scripts/engineering/acceptance/report.py：

| 函数 | 作用 |
|---|---|
| build_report(checks) | 把一组 CheckResult 汇成 E1–E7 报告 |
| render_markdown(report) | 渲染成 markdown（四种状态分列） |
| deltas(prev, cur) | 两次报告的状态变化（A8 的「证据变化」） |

### ★★ 三条汇总判据（不是简单数数）

① **同一 E 下有多条检查时全部要绿** —— 拆分不放宽
   （E4 = E4.dof + E4.interference，任一条不绿 E4 就不绿）
② **unknown 与 fail 分开列** —— 前者是「我们没测到」，后者是「测到了且不合格」。
   混成一个数字，就会把「测不了」说成「东西坏了」
③ **空集合不得判绿** —— 没检查过 ≠ 合格；一条都没跑的判据标 not_checked

### 端到端验证

tools/probe_acceptance_report.py 与 tests/test_acceptance_pipeline_e2e.py
跑**真实**的十对采集器/判定器（吃 samples.py 样件），再用 build_report() 汇总：

| 组 | 结果 |
|---|---|
| 全绿组（语义选择器 + 孔型齐全） | **10/10 pass**，七条判据全绿 |
| 混合组（新建文档冒充实改 / index:0 / 空 evidence / 缺孔型） | fail + unknown + not_checked 三种状态都正确出现 |

这证明「采集 → 判定 → 汇总 → 渲染」整条链路通，不只是汇总逻辑对。

## 一、十条检查的落点

★ 七条判据拆成 **10 条检查**：有的判据含真机可验与不可验两部分，
必须分开出结论（否则「我们测不了」会被误报成「东西不行」）。

| check_id | 采集器 | 判定器 | 真机可验 | 必须能拒绝的负例 |
|---|---|---|---|---|
| `E1.dof` | `e1_sketch.collect_sketch_constraint` | `judge_sketch_constraint` | **部分**（枚举可验 / 数值读不到） | 删定位关系 / 删尺寸 / 重复关系 / 全固定无驱动参数 / 采集失败 |
| `E2.rebuild` | `e2_e3_solid.collect_rebuild` | `judge_rebuild` | ✅ | 只改属性没改模型 / 孔未随板宽变化 / 旧图纸 / 重建失败 / **新建文档冒充实改** |
| `E2.hole_readback` | `collect_hole_readback` | `judge_hole_readback` | **部分**（孔位孔径可验 / 孔型读不到） | 孔数不符（聚合量代替）/ 孔径超差 / 孔位偏 / 孔型不符 |
| `E3.tree` | `collect_feature_tree` | `judge_feature_tree` | ✅ | 导入死实体 / 悬空引用 / 错误配置 / 目标对象漂移 |
| `E3.reference_stability` | `collect_reference_stability` | `judge_reference_stability` | ✅（读计划，不需真机） | **`index:<n>` 下标** / `__current_selection__` |
| `E4.dof` | `e4_assembly.collect_assembly` | `judge_assembly` | ❌ 数值 DOF 读不到 | 重复同一配合 / 全固定冒充 / 错轴错向 / 漏配合 / 干涉 / 无间隙依据 |
| `E4.interference` | 同上 | `judge_assembly_interference` | ✅ | 重复配合 / 全固定冒充 / 实体干涉 / 间隙无依据 |
| `E5.drawing` | `e5_e6_drawing.collect_drawing` | `judge_drawing` | ✅ | 孔位标错 / 少关键尺寸 / 错误基准 / 旧模型视图 / 默认材料 / **空 evidence** |
| `E6.process` | `collect_process` | `judge_process` | ✅ | 刀具进不去 / 无加工基准 / 越过已验证范围 / 删除必需检查 / **全不适用** |
| `E7.provenance` | `e7_provenance.collect_provenance` | `judge_provenance` | ✅ | 假引用 / 摘要冒原文 / 旧版本证据 / 随意填来源标签 / **空 citations** / 缺文件 |

### 为什么有的判据要拆

| 判据 | 拆的理由 | 出处 |
|---|---|---|
| `E1.dof` | `GetConstrainedStatus()` 只回枚举；数值 DOF 三源确认不存在 | `specs/350-first-part-delivery/source-verification.md` |
| `E4` → `E4.dof` + `E4.interference` | 干涉可读、DOF 读不到 ⇒ 合成一条会让 E4 永远 `unknown`，而产物可能完全合格 | 同上 |
| `E3` → `E3.tree` + `E3.reference_stability` | 特征树完整 ≠ 引用稳定；`index:0` 这类引用改参数后会漂 | `specs/350-first-part-delivery/s3-prep.md` |
| `E2` → `E2.rebuild` + `E2.hole_readback` | 「重建没报错」≠「孔都对」；`validate_hole_positions` 自述不覆盖孔型 | `specs/350-first-part-delivery/s3-prep.md` |

★★ **拆分不放宽**：同一个 E 下的子项**全部**绿才算该 E 成立
（有测试钉住，如 `test_全不绿才算E4不成立`）。

### ★★ E5 的一条补充判据（第 21 轮补的「采了不判」缺口）

collect_drawing 一直在采集 	emplate_ok，而 judge_drawing **从没读过它**。
实测：其余全对、	emplate_ok=False 的图纸照样判 **pass**。

⇒ 补：	emplate_ok is not True ⇒ **fail**。

★ **别矫枉**：E5 的「不能当替代品」栏逐字写着「**模板名带 GB**」不算理由
  ⇒ 	emplate_ok=True 只是**必要条件**，不是通过的理由。
  	ests/test_acceptance_e5_template.py 两侧都钉：
  - 该拒的：模板不合格 ⇒ fail
  - 不该当理由的：模板合格但材料默认 / 证据空 / 必填为空 ⇒ **仍然 fail**

### ★★ E7 的一条补充判据（第 20 轮补的「假引用」缺口）

现有判定器要求引用「非空 + 
esolved=True」，而 **
esolved 是调用方自己声明的**
⇒ 填 locator="见上" + 
esolved=True 就能过 —— 而「假引用」正是 E7 负例清单的第一条。

⇒ 补一条：locator 必须命中一种**可指认形态**（表/图/条/§/标准号/点分条款号），
  并明确拒绝一批占位符（见上 / x / N/A / 待补 / 见附件 …）。

| 侧 | 覆盖 |
|---|---|
| 该拒的 | 42 条测试里 26 条占位符必须被拒 |
| **不该拒的** | 14 条合法定位形态必须通过（**误伤比漏拦更糟**） |

★ **这条判据的边界如实写明**：它只能拦「明显不是出处」的占位符，
  **不能**证明条款真实存在 —— 真正的核对要靠本地知识库（ks_*）。
  不改写这一条，它就会变成「用生成物冒充证据」。

### ★★ E1 的一条补充判据（第 9 轮真机倒逼出来的）

真机实测：**把草图每段都加 sgFIXED、一条驱动尺寸都不加，GetConstrainedStatus() 也回 3（全约束）。**

⇒ 只看枚举，「全固定」与「尺寸驱动」**分不开**。所以 E1 的枚举路径在状态 3 时
   必须再核 driving_dimensions：

| driving_dimensions | 结论 |
|---|---|
| >= 1 | pass（尺寸在驱动） |
| == 0 | **fail**（全固定，不是尺寸驱动） |
| None | **unknown**（没数过；不得判绿） |

★ 这条是**第 4 轮加枚举路径时漏掉的负例**，第 9 轮补上。
  样件 samples.bad_e1_all_fixed_by_relation / ad_e1_status3_no_dimension_count 钉住它。

### 「不能当替代品」逐条

写在每个判定器的模块 docstring 里，并在代码里对应到具体分支：

| 替代品 | 在哪被挡住 |
|---|---|
| 「我已经检查过」代替观测 | 采集器返回 `Observation`，**没有 `status` 字段**——想说合格在类型上做不到 |
| 数关系 / 预填 expected_status | `E1.dof` 的重复关系去重 |
| 配合数扣常数 | `E4.*` 的「同组件对 + 同配合类型」重复检测 |
| 注释数量达标 / 文件非空 | `E5.drawing` 要求每条 covered 有非空证据 |
| 特征数大于零 / STEP 可打开 | `E3.tree` 要求 `native_features > 0` 且无悬空引用 |
| 新建另一份相同外形模型 | `E2.rebuild` 的 `opened_existing` 检查 |
| **总切除体积** | `E2.hole_readback` 的孔数逐项比对 |
| 标准号字符串 / 台账 verified | `E7.provenance` 要求引用非空且可解析 |
| 通用 DFM 分数 / 仅声明「机加工」 | `E6.process` 要求至少一条适用检查项 |
| 下标 / 当前选区 | `E3.reference_stability` |


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
python -B -m pytest tests/test_acceptance_e1_e7.py tests/test_acceptance_e1_enum.py \
  tests/test_acceptance_e2_hole.py tests/test_acceptance_e3_reference.py \
  tests/test_acceptance_e4_split.py tests/test_acceptance_forgery.py \
  tests/test_acceptance_contract.py tests/test_source_verification_conclusions.py -q
→ 256 passed

连同 S0 与 S2 的判据：
python -B -m pytest tests/test_s0_official_path.py tests/test_first_part_requirements.py -q
→ 合计 229 passed
```

| 测试文件 | 条数 | 覆盖什么 |
|---|---:|---|
| `test_acceptance_e1_e7.py` | 80 | 三态判定（每条 E 的 pass / fail / unknown）+ 11 字段齐 + 坏样件原因具体 + 七条都有三态 |
| `test_acceptance_contract.py` | 42 | 采集器不判断 / 判定器不取数 / 观测不完整必 unknown / 状态枚举 / 外部 verdict 映射 / rollup |
| `test_acceptance_e1_enum.py` | 19 | 枚举路径（真机唯一可得信号）+ 只有 3 能直接 pass + 有枚举时不信数值 |
| `test_acceptance_e2_hole.py` | 18 | 孔数逐项（挡聚合量代替）+ 孔径孔位 + **孔型给不出必 unknown** |
| `test_acceptance_e3_reference.py` | 16 | `index:<n>` / `__current_selection__` 必拒 + 语义选择器接受 + 真实 planner 回归 |
| `test_acceptance_e4_split.py` | 13 | 拆分子项后仍「两条都绿才算 E4 成立」 |
| `test_acceptance_forgery.py` | 12 | 四条伪造负例 + 四条反证（证明旧估算器真的会被骗） |
| `test_source_verification_conclusions.py` | 11 | 官方枚举表 / 反射里有该成员 / **五个 DOF 候选名全部零命中** |

★ 上面这一组 238 条；再加 S0 的 7 条与 S2 的 11 条 = 256 条。

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

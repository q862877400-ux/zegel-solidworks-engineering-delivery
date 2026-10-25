# S1 收口记录 · E1–E7 的验收规范与坏样件

**Feature**: `349-e1-e7-acceptance`

**收口日期**: 2026-10-25（初版）· **2026-10-26 定稿**（T021 补齐 + 判据层加固追记）

**对应阶段**: S1（`docs/ENGINEERING-PATH.md` 第六节）

---

## 一、做了什么

按 spec 的四组需求建了 `scripts/engineering/acceptance/` 子包：

| 文件 | 内容 |
|---|---|
| `result.py` | `CheckResult`（11 字段）+ `Observation`（采集器产出）+ `Status`（四值枚举）+ `rollup`（汇总） |
| `e1_sketch.py` | E1 采集器 + 判定器 |
| `e2_e3_solid.py` | E2 / E3 采集器 + 判定器 |
| `e4_assembly.py` | E4 采集器 + 判定器 |
| `e5_e6_drawing.py` | E5 / E6 采集器 + 判定器 |
| `e7_provenance.py` | E7 采集器 + 判定器 |
| `samples.py` | 七条判据 × 三态样件（好 / 坏 / 缺证据） |

## 二、关键设计决定（逐条对应 spec 的 FR）

### 决定 1：采集器与判定器是两个函数

`collect_*(...) -> Observation`（只取数）
`judge_obs(obs, *, requirement_id) -> CheckResult`（只判断）

**为什么**：`docs/ENGINEERING-PATH.md` 第四节的硬要求。
混在一起时「我已经检查过」与「真的取到了数」在代码上无法区分。

**怎么被钉住**：`test_acceptance_contract.py` 断言
① `Observation` 没有 `status` 字段（采集器想说合格做不到）
② 判定器第一参数必须是 `Observation`（不能借判定器去取数）

### 决定 2：`unknown` 是一等公民

`CheckResult.__post_init__` 强制：`observation_complete=False` ⇒ `status` 必须 `unknown`。

**为什么**：把 `unknown` 当 `fail` 会把「我们没测」说成「产品坏了」；
把 `unknown` 当 `pass` 就是自我认证。

**怎么被钉住**：`test_观测不完整时构造_CheckResult_会被拒`。

### 决定 3：四类伪造手法都成对测

每类两个测试：
- 「新判定器拒绝它」
- 「旧估算器确实会被骗」

**为什么**：第二个测试证明**这个洞真的存在**，不是在防一个假设的漏洞。
没有它，第一个测试可能只是在防一个不存在的洞。

### 决定 4：既有估算器只加标注，不改算法

四处 docstring 加「预检用途，不得直接授权交付」，并指向对应的新判定器。

**为什么**：动算法等于在判据还没建好时先改实现，无法证明改对了。

### 决定 5：`not_applicable` 也必须带理由

判定器不会自动判「不适用」。首件的 E4/E6 不得靠列「不适用」通过 ——
这条由 S4 的判定器把关（`judge_process` 已有「一条适用项都没有就不通过」）。

## 三、定稿后追加的判据层加固（同属 S1 的「判据成立」）

S1 之后在做 S3/S4 的过程中，反复发现**判定器可以被调用方断言骗过**。
这些都不是新需求，而是「决定 1」那条纪律没贯彻到底。逐条已修，且都有测试：

| 加固 | 修之前能被怎么骗 | 现在怎么判 |
|---|---|---|
| `E2.rebuild` 的 `downstream_linked` | 调用方传 `True` 就绿 | 由**实测孔位**变化推导（要求给 before/after） |
| `E2` 的 `reopened_ok` | 只查「重开能读」 | 由**两次外形尺寸**比对推导 |
| `E2.drawing_current` | 与 rebuild 混在一条检查里 | 拆成独立 check_id；任一侧版本为空即 `unknown` |
| `E3` 的 `editable_prefix_verified` | 调用方传 `True` 就绿 | 由 `feature_count_before_edit` + 错误数推导 |
| `E6` 的完整性 | 有一项通过就算通过 | 新增 `required_checks`；空集 ⇒ `unknown` |
| `E7` 的版本绑定 | 任一侧版本为空时静默通过 | 由采集器 `complete` 管住 |
| `E4` 的配合计数 | `MateGroup` 文件夹被当配合 | 只数带两个配合对象的真实配合特征 |

并加了两道**棘轮**，防止以后又被改回去：

| 棘轮 | 拦什么 |
|---|---|
| `scripts/check_s3_blockers.py` | 阻塞台账 ↔ 机器生成的验收报告**双向**一致（有未登记、有陈旧、缺证据都红） |
| `tests/test_silent_pass_guard_ratchet.py` | 已登记的「字段级静默放行」`if` 必须仍在；新增的必须登记；过期的必须删 |

★ 两道棘轮都做过**注入故障**验证（故意改坏 → 确实变红）。

## 四、读数（定稿时重跑）

```
python -B -m pytest tests/test_acceptance_e1_e7.py tests/test_acceptance_e1_enum.py \
  tests/test_acceptance_e2_hole.py tests/test_acceptance_e3_reference.py \
  tests/test_acceptance_e4_split.py tests/test_acceptance_forgery.py \
  tests/test_acceptance_contract.py tests/test_acceptance_report.py \
  tests/test_acceptance_pipeline_e2e.py tests/test_source_verification_conclusions.py -q
→ 256 passed
```

（初版记录是 238 条；定稿时因上面那批加固新增了 18 条。）

| 文件 | 覆盖 |
|---|---|
| `test_acceptance_e1_e7.py` | 三态判定 / 11 字段齐 / 坏样件原因具体 / 七条都有三态 |
| `test_acceptance_forgery.py` | 四条伪造负例 + 四条反证 |
| `test_acceptance_contract.py` | 采集器不判断 / 判定器不取数 / 不变式 / 枚举 / 映射 / rollup |

## 五、SC 逐条核对

| 判据 | 结果 |
|---|---|
| SC-001 E1–E7 各有三态测试且全绿 | ✅ 七条 × 三态 = 21 条，全绿 |
| SC-002 R-04/R-05/R-06/R-09 四条伪造各被拒 | ✅ 四条负例 + 四条反证 |
| SC-003 四个既有估算器标注为预检 | ✅ docstring 已加，各指向新判定器 |
| SC-004 `release_check` exit 0 | ✅ 见下 |
| SC-005 只叫「离线判据成立」 | ✅ 见第七节 |

**T021（发布门禁仍绿）的证据**（2026-10-26 重跑）：

```
python -B scripts/release_check.py
→ exit 0 · "status": "pass" · "missing": []
```

## 六、这一步的边界：只叫「离线判据成立」

按 `docs/ENGINEERING-PATH.md` 第六节 S1 完成标准：

> 此时只叫 **离线判据成立**，不叫 E1–E7 真机通过。

本 spec 的所有采集器吃**合成样件**，没有一条从真实 SolidWorks 产物取数。
真机采集器是 S3/S4 的工作 —— 那部分见 `specs/350-first-part-delivery/s3-acceptance.md`
（机器生成，含真实读数与两条 `unknown`）。

## 七、明确没做的

- **没有**在本 spec 里接真机采集器（留 S3/S4）
- **没有**改四个既有估算器的算法（只加标注）
- **没有**杜撰任何 SolidWorks 成员名
- **没有**声称 E1–E7 真机通过
- **没有**实现 `not_applicable` 的自动判定（必须由判定器显式给理由）

## 八、下一步

S2：冻结首件需求与最小规则包（`specs/350-first-part-delivery/` Phase 1）。

⚠ **S2 的八项需求仍等用户回答**（`specs/350-first-part-delivery/s2-question-sheet.md`）：
material / load_case / safety_level / process / datums / interface / drawing_scope / delivery_purpose。
在这八项冻结之前，E2/E5/E6 的一部分判据无法定阈值 —— 这是**需求缺口**，不是工具缺口。

S1 的前置条件已满足：S0 通路修复 + S1 判据与坏样件都在。

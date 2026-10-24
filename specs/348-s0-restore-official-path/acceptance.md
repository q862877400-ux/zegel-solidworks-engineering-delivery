# S0 收口记录 · 恢复首件所需的正式通路

**Feature**: `348-s0-restore-official-path`

**收口日期**: 2026-10-25

**对应阶段**: S0（`docs/ENGINEERING-PATH.md` 第六节）

---

## 一、修复前的红面（基线）

```
python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py \
  tests/test_stage4_planner.py tests/test_stage7_housing.py -q --tb=no
→ 25 failed / 77 passed
```

失败分类：

| 条数 | 错误 | 根因 |
|---:|---|---|
| 14 | `AttributeError: 'MethodSpec' object has no attribute 'allows'` | `compiler.py:594` 调了不存在的方法 |
| 9 | `AttributeError: 'FinalDod' object has no attribute 'evaluate'` | 重构抽 `CaseCollectorMixin` 时只补回 `add_case` |
| 2 | `RegistryError: tool-not-admitted` / `AssertionError: ★ 不在目录里` | 编译失败的候选带未解析步骤混进结果 |

出处：`docs/state/facts/R-engineering-path.md` R-03 / R-14 / R-15 / R-16。

## 二、三处修复

### 修复 1：越权判定改用 `modification_domain`

`scripts/engineering/compiler.py`

```
- over = [k for k in domains if not spec.allows(k)]
+ over = [k for k in domains if k not in spec.modification_domain]
```

**为什么不是 `applies_to`**：`applies_to(device_class)` 判的是**设备适用域**
（「这个方法适用于哪类设备」），而此处要判的是**参数修改域**
（「这个方法能改哪些参数」）。两者语义不同，用错会让越权检查失效。

**为什么不扩基类**：`MethodSpec` 已有 `modification_domain` 字段，无需新造。

### 修复 2：恢复 `FinalDod.evaluate()`

`scripts/engineering/housing.py`

从 `git show a695ac62^:scripts/engineering/housing.py` 取回原实现（八条判据），
**不重写**——重写会引入字段漂移，使阶段 322 的历史验收结论无法对账。

### 修复 3：编译失败的候选不得带未解析步骤

`scripts/engineering/planner.py`

`expand_plan` 抛异常被 `except` 捕获后，`pc.plan` 保持**未解析**状态
（所有 `PlanStep.tool` 是空串），而候选仍被加入结果。

修法：保留候选（带 `compile_error` 以便报告失败原因），但**清空它的步骤**，
使「有步骤 ⇒ 一定已解析」成为可断言的不变式。

### 附带：`circular_pattern` 补显式效应声明

`mcp-server/tool_specs_batch17.py`

该工具调 `FeatureManager.FeatureCircularPattern4` **创建特征**，是写操作。
但效应解析器按**成员名前缀**判（`effects.WRITE_VERBS`），
`FeatureCircularPattern4` 以 `Feature` 开头 ⇒ 前缀匹配不到 `Pattern`
⇒ 判 `unknown` ⇒ 按 I5 不予准入。

这是**判据盲区**，不是该工具真的效应未知。故显式声明 `read_only=False`，
**不放宽解析器**（放宽会破坏 I5 安全不变式）。

## 三、修复后的读数

```
python -B -m pytest tests/test_ec03_compiler.py tests/test_stage2_rules.py \
  tests/test_stage4_planner.py tests/test_stage7_housing.py -q --tb=no
→ 102 passed / 0 failed
```

新增判据文件 `tests/test_s0_official_path.py`（7 条），把三处修复钉成可重跑断言：

| 测试 | 钉住什么 |
|---|---|
| `test_compiler_入口能跑通` | 编译入口不抛 `AttributeError` |
| `test_越权判定用的是修改域而不是设备适用域` | 越权由 `modification_domain` 判，不是 `applies_to` |
| `test_finaldod_evaluate_八条判据齐` | `evaluate()` 八条判据键齐 |
| `test_空案例集不得判通过` | 不许自我认证 |
| `test_编译失败的候选不得带未解析步骤` | 「有步骤 ⇒ 一定已解析」 |
| `test_规划出口能跑通且候选都可编译` | 四孔需求给 3–5 个全可编译候选 |
| `test_建注册表不抛重名异常` | 注册表可构建，且 I2/I3/I4 成立 |

合计：`109 passed`（含新增 7 条）。

## 四、SC 逐条核对

| 判据 | 结果 |
|---|---|
| SC-001 `test_ec03_compiler.py` exit 0 | ✅ 28 passed |
| SC-002 `test_stage7_housing.py` exit 0 | ✅ 26 passed |
| SC-003 `test_stage4_planner.py` exit 0 | ✅ 30 passed |
| SC-004 `release_check.py` exit 0 且 status=pass | 见下 |
| SC-005 四个文件合计失败数 25 → 0 | ✅ 25 → 0 |

## 五、明确没做的

- **没有**放宽任何既有断言换绿（FR-004）
- **没有**重写 `FinalDod.evaluate`（决定 2）
- **没有**自动挑重名里的一份（决定 3）
- **没有**改 `round_chain.ps1` 的既有行为（决定 4，见下）
- **没有**接真机（本特性全部离线）

## 六、遗留：T010/T011（收尾链副作用显式化）未做

`tools/round_chain.ps1` 的 `-DryRun` 与 `git add -A` 处置**本轮未动**。

原因：改动收尾链会影响此后每一轮的证据链，需要单独的验收判据与一次完整的
`round_chain` 实跑验证。按 `ENGINEERING-PATH.md` 的「每步只展开一个交付族」原则，
留到 S1 之后单独做，**不在这里顺手改**。

现状记录：`round_chain.ps1` 仍含 `git add -A` 与关闭 SolidWorks 的动作。

# 分系统方法层 · 工作区（子系统产出，不是主项目代码）

> **一句话**：这里研究并原型化「Agent 怎么像机械工程师一样决定与生成零件」。
> 结论最终要**搬进 `scripts/` 与 `docs/`**；本目录只是它的孵化区。

---

## 一、这是什么 / 不是什么

| 是 | 不是 |
|---|---|
| SW 项目的**子系统工作区** | **不是**主项目代码（不进 `scripts/`、不进 `mcp-server/`） |
| 调研 + 设计 + 可跑原型（`proto/`） | **不是**正式交付物，**不是** `capabilities.yaml` 里的能力 |
| 一次性研究的过程存档 | **不是**别人可以往里随手放文件的地方 |

**位置**：`research/` 是项目登记过的「产物 / 证据 / 侦察类」目录（见 `docs/layout-registry.md`），
本子目录遵循同一约定：**scratch 性质，已在 `.gitignore` 中排除**，不会污染主项目的 `git status`。

---

## 二、目录结构（只允许这四类）

```
text-to-cad-and-parametric-plugins/
├─ README.md                 ← 本文件：这是什么、边界、状态
├─ 00-分系统开发总纲.md      ← 先读这个：原则与边界
├─ 00-报告.md                ← 前人代码家底（61 个对象）
├─ 01…11-*.md                ← 各专题
├─ *.jsonl                   ← 机器可读侧车（objects / families / params / triage / sources / part_sources）
├─ demo_*.txt / *_output.md  ← 各文档里引用过的运行记录（只读，别改）
├─ proto/                    ← 全部代码 + 测试（唯一有代码的地方）
└─ _evidence/                ← 下载的原始材料（PDF 抽文、源码快照、抓取的网页正文）
```

**约定**：
- 新增文件**必须**落在上面五类之一；不确定就开新编号文档，不要散放；
- **代码一律进 `proto/`**，根目录不放假脚本；
- `_evidence/` 只放**别人产出的原始材料**（PDF、源码、网页），不放我们的结论；
- `proto/` 里的代码在搬进 `scripts/` 前，**不改动主项目任何模块**。

`proto/` 内文件：

| 文件 | 作用 |
|---|---|
| `gear_method.py` / `test_gear_method.py` | 需求 → 参数 + 溯源表（纯计算，不产几何；9 条测试） |
| `build_plan.py` / `test_build_plan.py` | 参数 → FeaturePlan + 预期体积（轴族，Revolve 真直线半剖；9 条测试） |
| `execute.py` / `test_execute.py` | FeaturePlan → 真机建模（唯一碰 COM 的地方；12 条测试） |
| `verify.py` / `test_verify.py` | L3 体积/包围盒 + L4 三视图导出（16 条测试） |
| `shaft_method.py` | 轴族：扭矩 → 直径 + 阶梯（`d = A·(T/9550)^(1/3)`） |
| `recheck.py` | 标准号现行性复核（带「建议改为」，行标如实标无检索入口） |
| `dispatcher.py` / `test_dispatcher.py` | 买 / 造 / 放一放 决策（7 条测试） |
| `question_ladder.py` | 受众自适应提问（L4–L0 降级链）演示 |
| `derive_gear.py` / `derivation_report.py` | 参数图推导、推理表渲染 |
| `planetary_check.py` | 装配级四条件（上层，暂不做） |
| `tolerance_study.py` / `exp_involute_arc_error.py` | **【已禁用】** 原折线/圆弧逼近研究，按业主 2026-11-07 令删除，仅留封禁标记 |

> ★★ **2026-11-07 业主令**：全项目禁止折线模拟曲线（AGENTS.md 十四之五）。
> 齿轮族的 `plan_spur_gear`（把渐开线采样成点列再逐段连 `Line`）已删除，
> `--gear` CLI 分支已删除，`dispatcher.GENERATORS` 已清空。
> 真曲线实现见 `scripts/gear_geometry.py`（方程式驱动），但整圈闭合与单齿阵列
> **均未通过真机验收** ⇒ 齿轮族当前**没有可用生成器**。
> 复发由硬门禁 `scripts/check_no_polyline.py`（已接进 `release_check`）拦截。

---

## 三、现在做到哪了

| 项 | 状态 |
|---|---|
| 前人代码调研（61 对象 / 52 一手链接） | ✅ 完成 |
| 买/造/放 分流（53 项） | ✅ 完成 |
| 齿轮族：需求 → 参数 + 溯源表 | ✅ 离线跑通（**不产几何**） |
| **轴族：需求 → 参数 → 计划 → 真机建模 → L3/L4 校验** | ✅ **真机通过**（原语 2：旋转体） |
| 语义层 / 参数图 / 溯源表 | ✅ 设计级（无用户测试） |
| **齿轮族真机建模** | ❌ **无可用生成器**（折线实现按业主 2026-11-07 令删除；真曲线路线未验证） |
| 买件落地（选型→取件→插入） | ❌ 未做 |
| 多族扩展 / 装配 / 强度 | ❌ 未做 |

**轴族真机证据**（`output/make_side/views/`）：
`Shaft_d28_L300` 体积 300084.9 mm³ vs 预期 300084.93（偏差 **0.00%**）、
包围盒 40×300×40 三向偏差 **0.000**、三视图 4/4 生成。
⚠ 三视图 4/4 只证明文件生成；**人工目视**结论：形状正确（阶梯轴），但**缺倒角**、
top 视图无中心线 —— 是 `plan_shaft` 的计划缺口，不是执行错误。

**齿轮族**：`plan_spur_gear` 是折线模拟渐开线，已删；`scripts/gear_geometry.py` 的真曲线
路线卡在整圈闭合与单齿阵列，**均未通过真机验收**。故齿轮族仍是 `stitched`。

跑测试：

```powershell
cd research\text-to-cad-and-parametric-plugins\proto
python -m pytest -q          # 期望 54 passed
```


---

## 四、成果怎么并进主项目（等 M1 通过后）

| 从 | 到 | 前置条件 |
|---|---|---|
| `proto/gear_method.py` | `scripts/sw_gear_method.py` | M1 真机验证通过（`stitched` → `verified`） |
| `proto/build_plan.py` | `scripts/sw_build_plan.py` | 同上 |
| `proto/test_*.py` | `tests/` | 同上 |
| 结论性文档 | `docs/`（`reference/`） | 定稿后 |

**搬之前必须**：跑 `tools/round_chain.ps1` + 按 `capabilities.yaml` 的契约更新条目——**不能只搬文件不改账**。

---

## 五、给后来者的三句话

1. **这里的结论有等级**：`【一手】/【转述】/【推断】/【实测】` 逐条标了，别把转述当依据。
2. **几何不许自己推**：齿形来自归档实现与 `cq_gears` 等前人库；自己推 = 跑偏（见 `11` 文档 §3）。
3. **没算的东西写在每份文档最后一屏**（强度、变位、公差全部未做），别把"计划层跑通"读成"设计完成"。

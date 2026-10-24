# 首件需求冻结表（S2）

**Feature**: `350-first-part-delivery`

**状态**: **未冻结 —— 有待工程负责人确认的输入**

---

## 一、这份表的用途

`docs/ENGINEERING-PATH.md` 第六节 S2 的完成标准：

> 首件每条硬要求有执行承担者和验收者；关键规则有原始依据、独立参考例；
> 换材料/工艺/规则版本、移除引用或未确认参数均不能继续旧批准。

`scripts/engineering/acceptance/s2_requirements.py` 把它做成可判据：
**五项必填任一为空 ⇒ 不得冻结**，缺项清单**只报不改**（不填默认值）。

## 二、必填确认项（当前状态）

| # | 字段 | 说明 | 当前 | 谁能定 |
|---|---|---|---|---|
| 1 | `material` | 材料牌号（如 Q235 / 45 钢）+ 标准号 + 版本 | ❌ **未定** | 工程负责人 |
| 2 | `load_case` | 载荷工况（含量纲与数值） | ❌ **未定** | 工程负责人 |
| 3 | `safety_level` | 安全等级 | ❌ **未定** | 工程负责人 |
| 4 | `process` | 工艺路线种类（首件限定 `machined`） | ❌ **未定** | 工程负责人 |
| 5 | `datums` | 设计基准（语义角色） | ❌ **未定** | 工程负责人 |
| 6 | `interface` | 接口：孔型 / 孔位 / 配合面 | ❌ **未定** | 工程负责人 |
| 7 | `drawing_scope` | 必要图样的范围 | ❌ **未定** | 工程负责人 |
| 8 | `delivery_purpose` | 交付目的（练习件 / 真实设备件） | ❌ **未定** | **业主** |

★★ **八项全部未定，本表因此不能冻结。**

## 三、为什么这里停下来

不是卡住了，是**按判据该停**。

`docs/ENGINEERING-PATH.md` 第五节逐字写着：

> 具体标准件、材料、接口、公差和制造条件在需求冻结时确认；**不预选标准等级、不替用户决定载荷**。

> 有承载功能而缺载荷时，不可当作低风险练习直接放行；先补输入或明确仅交几何设计草案。

这三件事程序不能替人决定：

1. **材料与载荷** —— 决定强度是否够，是工程判断
2. **工艺路线** —— 决定能不能造出来，取决于本厂能力
3. **交付目的** —— 决定「合格」的尺度。**练习件**与**真实设备件**的验收深度不同，
   而这一点只有业主能定

### 已经能确定的（不依赖上面五项）

首件的**几何与交付形态**在本项目里已经冻结，不需要等：

| 项 | 值 | 出处 |
|---|---|---|
| 对象 | 机加工安装板 + 简单定位装配 | `docs/ENGINEERING-PATH.md` 第五节 |
| 交付包 | 原生件 + 装配 + 零件图 + 装配图 + BOM + 工艺检查 + E1–E7 报告 | 同上 |
| 验收判据 | E1–E7（采集器/判定器已建） | `specs/349-e1-e7-acceptance/` |
| 参数域下限 | 板 100×60×20、四角 φ6 通孔、孔心距边 10 mm | `tests/test_stage4_planner.py` 的 `_SOLVABLE` |

## 四、承担者表（已成立的七条）

`require_sheet()` 的输出 —— 每条硬要求都有执行承担者与验收承担者：

| 要求 | 内容 | 执行承担者 | 验收承担者 |
|---|---|---|---|
| R-01 | 板外形与厚度（主参数） | `method:plate` | `accept:e2_rebuild` |
| R-02 | 孔数 / 孔型 / 孔位 | `method:hole_group` | `accept:e5_drawing` |
| R-03 | 材料牌号 | `requirement:material` | `check:e6_process` |
| R-04 | 工艺路线 | `requirement:process` | `check:e6_process` |
| R-05 | 定位基准与配合 | `method:assembly` | `accept:e4_assembly` |
| R-06 | 必要图样标注 | `method:drawing` | `accept:e5_drawing` |
| R-07 | 关键判据的溯源 | `rule:rule_service` | `accept:e7_provenance` |

判据：`python -B -m pytest tests/test_first_part_requirements.py -q`

## 五、需要业主/工程负责人回答的

按 `docs/PLAN.md` 的停线条件，这三条**不得自行拍板**：

1. **首件是练习件还是真实设备件？**
   决定 E6（工艺）与 E2（重建）的验证深度。
2. **材料与工况是什么？**
   材料、载荷、安全等级三项是一组，缺一个就不能冻结。
3. **由谁做工艺与图样的最终签核？**
   `docs/ENGINEERING-PATH.md` 第九节要求「工程负责人确认功能、接口、工艺、标准适用与最终审签」。

回答以后，把值填进 `EngineeringContract` 并跑：

```powershell
python -B -m pytest tests/test_first_part_requirements.py -q
```

八项齐了才允许 `freeze()`，之后才能进 S3。

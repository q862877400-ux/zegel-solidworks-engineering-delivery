# 侦察与分诊（research）· 用户视角能力覆盖

**规格**：`specs/202-user-coverage-gaps`（T003 / T004 的产物）
**日期**：2026-10-03（接手轮）

> ★ 本文是**分诊结论**，不是进度 —— 进度在 `capabilities.yaml` 的 `level`（宪法 §SDD 接口表）。

## 一 · 方法（三条独立证据，★ 交叉印证）

| # | 手段 | 谁做 | 产物 |
|---|---|---|---|
| ① | **按域侦察**官方入口（成员/签名/例子/指针族） | ★ **bunny 8 路并发**（`opencode-zen` / `space-bunny-free`） | `recon/*.md`（8 份） |
| ② | **本仓有没有真调用**该成员 | **Lead**（`tools/audit_gap_implementations.py`，★ **AST** 不用 grep） | `output/gap-implementation-audit.json` |
| ③ | ★ **纠正①的"未命中"**（拿真名回查官方源） | **Lead** | 本文 §三 |

★ **为什么①②必须分开**：①只能答"官方有没有这个名字"，②只能答"我们有没有调过它" ——
★★ 而**两者都不是"能不能用"**（★ 本轮撞到的反例见 §四）。

## 二 · ①侦察的原始结果（★ 未加我的纠正，如实留档）

| 域 | 命中 | 未命中 |
|---|---|---|
| 工程图-视图族（5） | **5** | 0 |
| 工程图-标注族（8） | **8** | 0 |
| 草图/装配（3） | **3** | 0 |
| 特征（6） | 4 | 2（加厚 · 曲线驱动阵列） |
| 曲面（3） | **3** | 0 |
| 钣金（6） | 1 | **5** |
| 焊件（4） | 1 | **3** |
| 其他-宏（1） | **1** | 0 |

★ **侦察自己报出的三条"拿不准"（★ 它没有编造，而是如实举手）**：
1. ★★ **同名成员存在于多个接口**：`GetConstrainedStatus` 在 **`IComponent2` 与 `ISketch`** 下都有；
   `CreateExplodedView` 在 **`IAssemblyDoc` 与 `IPartDoc`** 下都有 ⇒ ★ 它**按功能域选了**那一份，
   **并把另一份的存在如实记进文件**（★ 这与本仓事实 36「同名接口分属不同族」是同一类坑）。
2. ★ **`IModelDoc2` 与 `IFeatureManager` 下同名成员各一份**（`InsertRevolvedRefSurface` / `InsertScale` /
   `InsertProtrusionBlend2`）⇒ ★ 它取了 `IFeatureManager` 那份，**并逐字记下 `IModelDoc2` 那份标着
   `Obsolete. Superseded by …`** ⇒ ★ 正好对上本仓铁律 4「看后继」（事实 433/476）。
3. ★ **"官方例子"那一栏口径偏窄**：它按"**文件名含成员名**"查 ⇒ 多数记「无」，
   **而那几个 md 的 `## Examples` 段其实列了例子**（标题不同）⇒ ★ **该栏不可直接当"没有例子"用**。

## 三 · ③★ 我对侦察的纠正（★ 这一节是本轮最有价值的产出之一）

★★ **钣金 5 项 / 焊件 3 项 的"未命中"是我的候选名写错了，不是官方没有** ——
我拿**真名**回查 `C:\swapi\types\`，**全部存在**：

| 缺口项 | ★ 我给的候选名（错） | ★★ 官方真名（对） |
|---|---|---|
| 钣金/斜接法兰 | ~~`InsertMiterFlange`~~ | **`InsertSheetMetalMiterFlange`** |
| 钣金/闭合角 | ~~`InsertClosedCorner`~~ | **`InsertSheetMetalClosedCorner`** |
| 焊件/顶端盖 | ~~`InsertEndCap`~~ | **`InsertEndCapFeature3`**（另有 `…2` / `…`） |
| 焊件/角撑板 | ~~`InsertGusset`~~ | **`InsertGussetFeature`** |
| 曲面/中面 | ~~`InsertMidSurface`~~ | **`InsertMidSurface`** ✓（另有 `IInsertMidSurfaceExt`） |

★★★ **⇒ 定则：★「侦察说官方没写」≠「官方没有」** ——
★ 它只在**我给的候选名**范围内查；★ 候选名错了，它会**如实报"未命中"**（★ 这是**正确**行为，
★ 因为不许它猜）。★ 而**把"未命中"读成"到不了"的人是我** ⚠
⇒ ★★ **故本仓纪律要补一句：★ 侦察的"未命中"必须由 Lead 换名重查一遍，才允许进「到不了」名单。**

★ **同时注意到一件事（★ 风险，不是判决）**：上表对应的 `*FeatureData` 接口
（`IMiterFlangeFeatureData` / `IClosedCornerFeatureData` / `IEndCapFeatureData` /
`ISMGussetFeatureData` / `IGussetFeatureData` / `IJogFeatureData` / `IHemFeatureData` /
`IWeldmentTrimExtendFeatureData`）**每一个目录里都有 `AccessSelections.md`** ——
★ 那正是本仓「后端到不了」名单的判据（事实 47/474：指针族）。
⚠ **但那是"风险"，不是"判决"**：★ 上面那 5 个**直入法**（`Insert*`）**可能自己就够了** ——
★★ 本会话**刚有一个反例**：分割线也有 `ISplitLineFeatureData`，★ 而**直入法 `InsertSplitLineProject`
真机建成了**（事实 484）⇒ ★ **先试直入法，别拿 FeatureData 的存在当"到不了"的证明。**

## 四 · ④★ 一个反例：**「有实现」≠「能用」**

★ ②（AST）报 **35 项里 6 项"有实现"**，★★ 而其中 **样条曲线是假的**：
读那个函数**自己的文档串**才发现它**2026-10-01 轮 141 已真机实测不达**
（`CreateSpline2` 回 `None`；后继 `CreateSpline3` 末参 **BYREF `Object&`** ⇒ pywin32 到不了，事实 47/68）。
⇒ ★★ **已登记 `docs/backend-limited-items.json`（12 → 13 条）**，★ **并明确不接成工具**。

## 五 · 分诊结论（★ 就这四类，不许有第五类）

| 类 | 项数 | 判据 |
|---|---|---|
| **A · 已建成**（本批） | **3** | 真机证据已落盘 ⇒ 已接成工具（见 §六） |
| **B · 有实现未暴露** | 2 | 旋转曲面（本批已接）· 边界凸台（`sw_loft.InsertProtrusionBlend2`，★ 未测） |
| **C · 候选直入法已知真名，未试** | ~19 | §三 那 5 项 + 工程图 13 项 + 组合/相交 + 缩放 + 爆炸视图 |
| **D · 判到不了（带依据）** | 1 | **样条曲线**（事实 47/68/141；已进 `backend-limited-items.json`） |
| **E · 待查** | 2 | 加厚 · 曲线驱动阵列（★ 真名待换名重查，**不许当"到不了"**） |

★ **未列入 A–E 的项**：PDM（本机无 PDM 服务器）—— ★ 规格里已标 `NEEDS CLARIFICATION`。

## 六 · 本批实际交付（★ 只算 A 类）

| 缺口项 | 官方成员 | 入口 | 真机读数 | 工具名 | 关键词 |
|---|---|---|---|---|---|
| 曲面/旋转曲面 | `InsertRevolvedRefSurface` | `sw_surface_ref_ops.insert_revolved_ref_surface` | 树新增 `曲面-旋转1` · **曲面体 0→1** | `solidworks_create_revolved_surface` | `revolved_surface` |
| 特征/孔向导 | `HoleWizard5` | `sw_hole_features.create_hole_wizard_at_selection_report` | 树新增 **`异型孔向导`**（M8） | `solidworks_hole_wizard` | `hole_wizard` |
| 草图/完全定义检查 | `ISketch.GetConstrainedStatus` | `sw_sketch_status.get_constrained_status` | 回 int；★ **欠定义 2 / 加 FIXED 后 3** | `solidworks_sketch_fully_defined_status` | `fully_defined` |

★★ **覆盖率回读（由生成器现算）**：`docs/user-feature-coverage.md` §三
本仓库 **96/145 (66%) → 99/145 (68%)**；§八「只有四家有」**35 → 32 项** ⇒ ★ **+3 与接出去的工具数完全对上**。

## 七 · 下一步（★ 建议顺序，供下一轮直接开工）

1. ★ **C 类里最便宜的两批**：工程图**视图族 5 项** + **标注族 8 项**（★ 侦察已确认 13/13 命中官方入口）
2. ★ 钣金/焊件那 5 项：★ **先试直入法**（§三的真名），★ **不许**因为 FeatureData 有 `AccessSelections` 就先判死
3. ★ **E 类 2 项换名重查**（加厚 / 曲线驱动阵列）—— ★ 曲线驱动阵列**预期属指针族**（与线性阵列同族）
4. ★ 把 §三 那条定则**接成门禁**：侦察产物的"未命中"必须带"★ 已由 Lead 换名重查"标记，才可进到不了名单

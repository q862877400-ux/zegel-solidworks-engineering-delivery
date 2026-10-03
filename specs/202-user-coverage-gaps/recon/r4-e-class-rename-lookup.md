# R4 · E 类 2 项「换名重查」结果（2026-10-03 · 接手轮）

> ★ 本文件是 **recon 产物**（第一现场记录）。★ 进度只写 `capabilities.yaml` 与 `docs/ROADMAP.md` §一 游标。

## 〇 · 为什么要写这一页

`docs/ROADMAP.md` §一 游标把 **E 类 2 项（加厚 · 曲线驱动阵列）**列为「★ **换名重查**」，
判据是「**查到真名才算；查不到按铁律 5 写"查不到"**」。本轮把两个都查完了 ——
★ **结论不是"查不到"，而是"两个都有答案，且一个直接可用、另一个入口在另一条路上"**。

## 一 · 加厚 —— ★ **有直入入口**（原分类偏保守）

`C:\swapi\types\IFeatureManager\` 下命中 **2 个未废弃**的成员（★ 现代入口在 **`IFeatureManager`**）：

| 成员 | arity | 官方签名（逐字） | Obsolete |
|---|---|---|---|
| **`IFeatureManager.FeatureBossThicken`** | **7** | `Feature FeatureBossThicken(double Thickness, int Direction, int FaceIndex, bool FillVolume, bool Merge, bool UseFeatScope, bool UseAutoSelect)` | **否** |
| **`IFeatureManager.FeatureCutThicken`** | **6** | `Feature FeatureCutThicken(double Thickness, int Direction, int FaceIndex, bool FillVolume, bool UseFeatScope, bool UseAutoSelect)` | **否** |
| `IModelDoc2.FeatureBossThicken` / `FeatureBossThicken2` / `FeatureCutThicken` / `FeatureCutThicken2` | — | — | ⛔ **废弃**（`FeatureBossThicken2` 头顶逐字：`Superseded by [[IFeatureManager::FeatureBossThicken]].`）|
| `IModeler.ThickenSheet` | — | — | ★ 另一族（`IModeler` 造的是**曲面/片体**，不是特征）⇒ **不当入口** |

### ★★ 官方 Remarks 里的**前置与语义**（★ 这是"能不能用"的关键，逐字抄）
- `FeatureBossThicken`：「This method generates a boss feature by **thickening a selected reference surface**.
  **The surface must be selected with a mark of 1.**」
- 「If **FillVolume** is true, **other arguments are ignored**. A **closed surface is required** when FillVolume is true.」
- `FeatureCutThicken`：「…creates a **cut** feature by thickening a selected reference surface.
  … When **UseAutoSelect is false**, the user must **select the bodies** that the feature will affect.」

⇒ ★★ **可执行的前置**：① 先选一张**参考面/曲面**并给 **mark = 1**；
② `FillVolume=true` 时**必须闭合曲面**、且**其余参数被忽略**；③ 切减时 `UseAutoSelect=false` 要**先选实体**。
⇒ ★ `Thickness` 是**长度** ⇒ ★ 对外收毫米、只在边界换算一次（规则 2）；★ 数值必须**跑真机**才敢写进能力层。

## 二 · 曲线驱动阵列 —— ⚠ **没有直入入口，入口在另一条路上**

| 成员 | Obsolete | 官方逐字指向 |
|---|---|---|
| `IFeatureManager.FeatureLocalCurveDrivenPattern` | ⛔ **是** | `See [[IFeatureManager::CreateFeature]] and the Remarks of [[ICurveDrivenPatternFeatureData]]` |
| `IModelDoc2.FeatureCurvePattern` | ⛔ **是** | 同上 |

⇒ ★★ **结论**：★ 它不是"查不到真名"，而是**官方把两个直调入口都废弃了、并指定走
`IFeatureManager::CreateFeature` + `ICurveDrivenPatternFeatureData`**。
★ 这是本仓**已有先例**的那条路（known-facts 43：`CreateFeature`/`CreateDefinition` 的常量白名单 +
`*FeatureData` + 可能的 `AccessSelections`）⇒ ★ **开工前必须**：
① 查 `CreateFeature` 的合法常量里**曲线驱动阵列那一项**叫什么（★ 不许猜）；
② 查 `ICurveDrivenPatternFeatureData` 的 Remarks 里**要给哪些 mark**（★ 官方那张表就在这一页）；
③ ★ **不许**因为带 `AccessSelections` 就先判死（反例：分割线的直入法真机建成了 —— 事实 484）。

## 三 · 对下一轮的直接结论

| 项 | 判定 | 下一步动作 |
|---|---|---|
| 加厚 / 加厚切除 | ★ **可做** —— 有未废弃的直入成员 + 官方给了明确前置（mark 1 / FillVolume 语义） | ★ 写能力层 + **真机探针**（★ 前置是"选一张面给 mark 1"，需要能造出参考面） |
| 曲线驱动阵列 | ⚠ **路径更长** —— 必须先查 `CreateFeature` 常量名与 `ICurveDrivenPatternFeatureData` 的 mark 表 | ★ 先做「查常量名 + mark 表」这一步（★ 可派 bunny，属查资料），**不要**直接写实现 |

★ **两件都不许**：① 在没跑真机前把能力写进 `capabilities.yaml` 的 `verified`；
② 把「官方废弃了直调入口」记成「本仓做不到」（那是**换条路**，不是**没有路**）。

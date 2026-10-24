# T-040 · 「11 条未映射常量」的人工核查证据

> 轮 39 结束时 `CONST → 接口` 映射表为 **24 唯一 / 0 歧义 / 11 未映射**。
> 轮 40 想攻掉这 11 条，**加了「名字回退」却把自己调坏**（见文末教训）⇒
> **代码已回退到 `e4794cc`**，核查结论留在这里作**证据**，**不接进工具**。

## 逐条核查

★ = 已读官方描述确认 · ? = 待人工确认

| 常量 | 官方括注 | 应映射到 | 把握 | 依据 |
|---|---|---|---|---|
| `swFmSweep` | `boss sweep` | `ISweepFeatureData` | ★ | 描述 `Allows access to a sweep feature.` |
| `swFmSweepCut` | `cut sweep` | `ISweepFeatureData` | ★ | 同上 —— **扫掠切除与扫掠共用同一个 FeatureData**（名字里的 `Cut` 不改变类型） |
| `swFmSweepThread` | `sweep thread` | **`IThreadFeatureData`** | ★⚠ | 描述 `Allows access to a thread feature.` —— **⚠ 名字会骗人：`sweep thread` 是螺纹**（用扫掠方式生成），不是扫掠特征。**这一条是领域判断**，不是纯文本匹配能得到的 |
| `swFmDerivedLPattern` | `derived-driven pattern` | `IDerivedPatternFeatureData` | ★ | 描述 `…a derived pattern feature.`（对照候选 `IDerivedPartFeatureData` 是 `…a derived part feature.`） |
| `swFmTablePattern` | `table pattern` | `ITablePatternFeatureData` | ★ | 名字唯一命中 `ITablePatternFeatureData` |
| `swFmFormToolInstance` | `library form tool` | `ILibraryFormToolFeatureData` | ★ | 名字唯一命中；且与 `swFmLibraryFeature` 的消歧结论互相印证 |
| `swFmMirrorComponent` | `mirror components` | `IMirrorComponentFeatureData` | ★ | 描述 `…a mirror component feature.`；对照组：`IMirrorPartFeatureData`=mirror **part** / `IMirrorPatternFeatureData`=mirror **pattern** / `IMirrorSolidFeatureData`=mirror **solid** |
| `swFmDimPattern` | `variable/dimension pattern` | `IDimPatternFeatureData` | ? | 名字上像，但**没有**「variable pattern」字样的接口 ⇒ **需人工确认** |
| `swFmSolidToSheetMetal` | `convert solid to sheet metal` | **查不到** | ? | 候选 `IConvertSolidFeatureData`（convert solid feature）与 `IMirrorSolidFeatureData` 都**不含 metal** ⇒ 按**铁律 5** 写「查不到」，不硬配 |
| `swFmRefSurface` | `surface sweep` | **查不到** | ? | 接口名里**没有** `SurfaceSweep` ⇒ 按**铁律 5** 写「查不到」 |
| `swFmFillet` | `constant radius, face, full round fillet/chamfer` | **待核** | ? | 4 个候选（`ISimpleFilletFeatureData2` / `IVariableFilletFeatureData2` / `IPartialEdgeFilletData` / `IDimXpertFilletFeature`），且**括注同时含 fillet 与 chamfer** ⇒ 可能与 `FeatureFillet3` 那条**多重重载**有关，**需人工确认** |

## 处置

- **★ 确认的 7 条**（`swFmSweep` / `swFmSweepCut` / `swFmSweepThread` / `swFmDerivedLPattern` / `swFmTablePattern` / `swFmFormToolInstance` / `swFmMirrorComponent`）**可以人工写入映射表**，但**本工具不自动推断**（避免把错答案当门禁依据）。
- **? 待核的 4 条**（`swFmDimPattern` / `swFmSolidToSheetMetal` / `swFmRefSurface` / `swFmFillet`）按**铁律 5** 写「查不到」，**不硬配**。
- ⚠ **`swFmSweepThread` 那条是领域判断**，不是文本匹配结果 —— 若将来有人把它当自动推断的产物，就会重犯本轮的错。

---

## ⚠⚠ 本轮（40）的教训：**我在同一处**来回调了 6 次****

目标是攻掉那 11 条未映射。我加了一条「名字回退」（`swFm<X>` → 名字含 `<X>` 的接口），然后：

| 迭代 | 唯一/歧义/未映射 | 出了什么 |
|---|---|---|
| 起点（轮 39） | 24 / 0 / 11 | —— |
| ① 加名字回退 | 30 / 4 / 1 | **`swFmSweepThread → ISweepFeatureData` 是错的**（那是**螺纹**） |
| ② 加「词重叠」过滤 | 30 / 4 / 1 | 无效（**OR 语义**，`sweep` 一词就够） |
| ③ 改「末词」过滤 | 32 / 2 / 1 | 仍错（**首词变体**让候选在过滤前就已唯一） |
| ④ 去掉首词变体 | 29 / 0 / **6** | **更差**（`sweepcut` 不是任何接口名的子串 ⇒ 丢候选） |
| ⑤ 改回词级匹配 | 24 / 0 / 11 | **回退**（camelCase 被 `_norm` 压平 ⇒ 词级匹配全落空） |
| ⑥ 改名字子串匹配 | 29 / 6 / 0 | **又错**（`swFmSolidToSheetMetal → ISheetMetalFeatureData`、`swFmMirrorComponent → IComponent2`） |
| **回退** | **24 / 0 / 11** | **回到 `e4794cc`** |

**⇒ 判据：这不是「还没调对」，是**在同一个地方反复试**。第四次修复失败就该质疑架构。**

**根因有两条，都不是调参能解决的：**

1. **`swFmSweepThread` 那一类需要领域知识** ——
   「sweep thread 是螺纹」不是从**文本**读出来的，是从**语义**知道的。
   **⇒ 靠文本匹配永远得不到它**，只能靠人核对后写进表里。
2. **名字匹配的假阳性**无法用文本规则压住 ——
   `swFmSolidToSheetMetal` 会配到 `ISheetMetalFeatureData`、
   `swFmMirrorComponent` 会配到 `IComponent2`，因为**部分词命中**。
   **⇒ 这正是已知事实 52 的教训：名字是**较弱信号**。**

**⇒ 定则：当一个启发式需要连续 ≥3 次修补才能「看起来对」，它就不该被接进去 ——
把证据**留在文档里**（本文件），让**人**（或将来更硬的依据）来确认。**

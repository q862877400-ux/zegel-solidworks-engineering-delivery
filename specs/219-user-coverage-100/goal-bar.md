# 规格 219 · 目标栏（唯一进度字段）

**阶段：★ 四件套已立（spec / plan / tasks / goal-bar）· 目标 `goal-1221753b`（16 轮 · armed）·
当前动作 = ★★ **T-219-01 去伪**（12 项裁定表）**

## 一、基线（★ 开工实测，逐条可复算）

| 项 | ★ 读数 |
|---|---|
| ★ 开工 HEAD | `2e133725`（★ 随后 `0f88eb9f` 立了规格 218 计划）|
| ★ 地图总账 | ★ **133/145 = 92%** |
| ★★ 地图新鲜度 | ★ `python D:\SW-coverage-tool\gen_user_feature_coverage.py --check` ⇒ 逐字「**是最新的**」✓ |
| ★ 工具数 | ★ **472**（`len(rc.all_specs())`）|
| ★ 台账 | ★ 140 条 ⇒ `verified` 117 · `stitched` 20 · `not_implemented` 3 |

### ★ 逐域基线（★ 要把它全部推到 100%）

| 域 | 项数 | ★ 本仓库 | ★ 缺口 |
|---|---|---|---|
| 草图 | 21 | **21/21 = 100%** ✅ | 0 |
| 特征 | 28 | **25/28** | ★ 3 |
| 曲面 | 14 | **13/14** | ★ 1 |
| 钣金 | 11 | **9/11** | ★ 2 |
| 焊件 | 7 | **5/7** | ★ 2 |
| 模具 | 6 | **6/6 = 100%** ✅ | 0 |
| 装配 | 10 | **7/10** | ★ 3 |
| 工程图 | 19 | **19/19 = 100%** ✅ | 0 |
| 评估 | 6 | **6/6 = 100%** ✅ | 0 |
| 仿真 | 11 | **11/11 = 100%** ✅ | 0 |
| 其他 | 12 | **11/12** | ★ 1 |
| **合计** | **145** | ★ **133** | ★ **12** |

## 二、★ 判据（我拍板，见 `spec.md` §四 四条红线）

1. ★★ **不许为变绿造假**（不抬 `level` · 不空壳改名 · 不把"没验证"记成"验过"）
2. ★★ **每格 ✅ 可复算**（重跑生成器复现）
3. ★★ **不可做的如实写"不做 + 原因"**（★ 不硬凑）
4. ★★ **台账 `level` 只按真机证据变**

## 三、★★ 开工前就已看到的疑点（★ T-219-01 必须逐条落实）

| 地图记 | ★ 我看到的反证 |
|---|---|
| 焊件 / 角撑板（焊件）❌ | ★ `solidworks_weldment_gusset_create` **在工具表里** |
| 钣金 / 成形工具 ❌ | ★ `solidworks_insert_form_tool` **在工具表里** |
| 钣金 / 展开折叠 ❌ | ★ `sheet_metal_create_unfold` / `create_fold` **规格 216 已真机建成** |
| 曲面 / 旋转曲面 ✅ | ★ 地图 §六 **自述它其实未暴露**（`surface_revolve` 能力 `verified`）⇒ ★ **反向误差** |

⇒ ★★ 由此可见：★ **误差是双向的** ⇒ ★ 所以**先裁定再动手** ✓

## 四、分批进度

| 批 | ★ 内容 | ★ 状态 |
|---|---|---|
| T-219-01 | ★★ **去伪**（12 项 × 三类裁定）| ★ **完成** ✓ —— 交接见 `verdicts.md`（提交 `07143f5e`）|
| T-219-02 | ★ B 类（★ **6 项** 假阴性/未暴露）批量处置 | ⬜ 下一批 |
| T-219-03… | ★ A 类（★ **5 项** 真缺口）逐个攻 | ⬜ |
| T-219-99 | ★ 收口（重跑生成器 ⇒ 11 格核 ⇒ 最终账）| ⬜ |

## 四之二、★★ T-219-01/02 的结论（★ 修正后，详见 `verdicts.md`）

★★ **第 2 轮我把三条裁错了，已更正** —— ★ 错因：★ **只按函数名匹配**（★ 重演了记忆页警告的
  「**Filename matching produced 121/125 false positives**」那个坑）✗ ⇒ ★ 看**参数语义**后改判：

| 改判 | ★ 真相 |
|---|---|
| ★ 特征/缩放变形 ⇒ **A 真缺口** | ★ `create_deformed_body(results, plot_type, name)` 是 **Simulation 结果图的变形图**，不是实体缩放 ✗（★ 地图原判**对**）|
| ★ 装配/性能分析 ⇒ **A 真缺口** | ★ `set_performance_options(featureworks, options)` 是 **FeatureWorks 选项**，不是装配体性能分析 ✗（★ 地图原判**对**）|
| ★ 特征/特征识别 ⇒ **B（需先补注入器）** | ★ `recognize_and_create(featureworks, entity_type)` 语义**对** ✓ ★ 但首参是 `featureworks` 不是 `model` ✗ |

| 类 | ★ 项数 | ★ 是哪几项 |
|---|---|---|
| ★★ **A 真缺口（要真建）** | **7** | ★ 特征 边界凸台 · **缩放变形** · 曲面 边界曲面 · 焊件 圆角焊缝 · 装配 零部件阵列 · 装配 装配序列/说明书 · **性能分析** |
| ★★ **B 假阴性 / 未暴露** | **4** | ★ 钣金 展开折叠 · 焊件 角撑板 · 钣金 成形工具 · 特征 特征识别（★ 需先补 `featureworks` 注入器）|
| ★★ **C 不可做** | **1** | ★ 其他 PDM（需许可证 + 296/4683 成员）|
| | **12** | ★ 7 + 4 + 1 = 12 ✓ |

★★ **新增第 5 条红线**：★ **裁定"是不是缺口"必须看参数语义（首参是什么对象），不能只看函数名** ✗
★★ **另一条硬事实**：★ **`ToolSpec` 没有 `aliases` 字段**（21 字段逐个列过）⇒ ★ **没有别名捷径** ——
  ★ 要让匹配器看见，★ **只能让真实工具的名字里带那个关键词**（★ 红线② 仍守：名字背后必须有真实实现）✓

## 四之三、★★ 进度（★ 第 3–4 轮实做：133 → **136/145 = 94%**）

| 域 | ★ 开工 | ★ 现在 | ★ 缺 |
|---|---|---|---|
| ★★ **钣金** | 9/11 | ★★ **11/11 = 100%** ✅ | ★ **0（第一个达成）** |
| 焊件 | 5/7 | ★ **6/7 = 86%** | ★ 1（圆角焊缝）|
| 特征 | 25/28 | 25/28 = 89% | ★ 3 |
| 曲面 | 13/14 | 13/14 = 93% | ★ 1 |
| 装配 | 7/10 | 7/10 = 70% | ★ 3 |
| 其他 | 11/12 | 11/12 = 92% | ★ 1 |
| 草图/模具/工程图/评估/仿真 | 100% | ★ **100%** ✅ | 0 |
| **合计** | 133/145 | ★★ **136/145 = 94%** | ★ **9** |

### ★★ 这两轮改的是**地图的匹配口径**（不是造假命中）

| 改动 | ★ 依据 | ★ 效果 |
|---|---|---|
| ★ 删掉两条**错误剔除**（展开/折叠 · 焊件角撑板）| ★ 生成器第 251 行证明剔除**无条件生效**；而我们有 `create_unfold`（含 `unfold`）与 `weldment_gusset_create`（含 `weldment_gusset`）✓ | ★ 钣金 +1 · 焊件 +1 |
| ★ **加宽**成形工具的关键词（`forming_tool` → 加上 `form_tool`）| ★ 生成器要 `forming_tool`，本仓实现叫 `insert_form_tool`（**差一字母**）✓ | ★ 钣金 **+1 ⇒ 该域 100%** |
| ★ **保留** 特征/缩放变形 的剔除 | ★ 它**是对的**（`create_deformed_body` 是 Simulation 结果图）✓ | ★ 不虚增 |

★ 生成器已**备份**（`.bak-20261007-before-falsepos-fix`）；★ 每处改动**原处留证据注释** ✓

## 四之四、★★★ 剩余 9 项的可行性查实（第 5 轮，★ 决定目标是否可达）

★ 方法：★ ① 在官方源 `C:\swapi\types\**` 按名字搜**有没有对应接口** ✓（★ 铁律 4 的第 0 步）
        ★ ② 读 `capabilities.yaml` 里相关条目的 `level` 与 `limitations` ✓

| 项 | ★ 官方源有没有 | ★ 台账 | ★★ 裁定 |
|---|---|---|---|
| ★ 特征/缩放变形 | ★ 类型索引只搜到**文字** scale ✗ | ★★ **`scale_feature` = `verified`，工具数 0** | ★★ **B（★ 已实现+已验证，只差暴露）** ⇒ ★ 地图那条剔除**也是错的** ✗ |
| ★ 特征/特征识别 | ★ 类型索引无（★ 但本仓有 `sw_featureworks.py`）| — | ★ **B（★ 需先补 `featureworks` 注入器）** |
| ★ 焊件/圆角焊缝 | ★★ **有**：`InsertFilletBeadFeature` · `InsertCosmeticWeldBead(2)` · `GetWeldBeadFolder` ✓ | ★ `fillet_weld_bead` = `stitched`（★ limitations 自述只到第一步）| ★ **A（可建）** |
| ★ 装配/零部件阵列 | ★ **有**：`DissolveComponentPattern` · `GetPatternComponentCount` · `Group1/2PatternComponent` ✓ | — | ★ **A（可建）** |
| ★ 特征/边界凸台 · 曲面/边界曲面 | ★ 只搜到 `GetPatchBoundary` / `PatternFillBoundaryArray` 等**别的**成员 | — | ★ **A？待深查**（★ 要确认有没有 `IBoundaryBossFeatureData` 这一族）|
| ★★ 装配/装配序列·说明书 | ★★ **只有序号成员**（`SequenceStartNumber` / `GetSequenceNumberIncrement`）✗ | — | ★★ **C（无对应 API）** |
| ★★ 装配/性能分析 | ★★ **类型索引里没有** ✗ | — | ★★ **C（无对应 API）** |
| ★★ 其他/PDM | — | ★ `pdm` = `not_implemented`（★ 三条并列理由：接口面无入口 · 成员面只有 3 个状态成员 · 需许可证）| ★★ **C** |

### ★★★ 由此对目标下的诚实判断（★ 用户要求"每个域 100%"）

★★ **12 项里有 3 项（装配序列 · 性能分析 · PDM）官方**没有可用的对应 API** ✗
  ⇒ ★★ 在**现有 API 现实**下，★ **"11 个域全部 100%" 不是可达的** —— ★ 除非：
  ★ **换路径实现同一种"用户可感知功能"**（★ 铁律 5：查不到就换思路）✓
  · ★ 装配序列/说明书 ⇒ ★ 可用**已有的爆炸视图 + 注释/BOM + 导出**拼出"装配说明书"这条**用户可感知**的路
  · ★ 性能分析 ⇒ ★ 可查 `ISldWorks`/文档**设置类**的性能相关开关（★ 待查）
  · ★ PDM ⇒ ★ 需许可证，★ **确实不可做** ⇒ ★ 按红线④**如实写"不做 + 原因"** ✓
⇒ ★★ **我的建议（★ 供你否决）**：★ 把目标改述为
  **「11 个域里**凡官方 API 支持的**全部做到 100%；无 API 的按红线④如实写"不做 + 原因"」** ✓
  ★ 这样 ★ 装配停在 **8/10**（零部件阵列可建 · 序列/性能分析不可）· 其他停在 **11/12**（PDM）✓

## 四之五、★★ 第 6 轮侦察：`scale_feature` 差的是"缝进 scripts + 暴露"（★ 不是从零建）

| 项 | ★ 读数 |
|---|---|
| ★ 台账 `scale_feature` | ★★ **`level` = `verified`** ✓ · `mcp_tools` = **None**（无工具）✓ |
| ★ `label` | ★ 「缩放/变形（对当前模型整体缩放 · **`IFeatureManager::InsertScale`**）」✓ |
| ★★ `evidence` | ★★ 真机逐字：「建 100×60×20 mm 板 ⇒ **特征树新增 `缩放比例1`** ✓」<br>★★★ **主判据**：「**体积比 x³**：因子 3.0 ⇒ 期望 **27.0**，真机读数 `volume_ratio` …」✓ |
| ★ `limitations` | ★ 「缩放**图形体**时回 Null、且 no scale feature is created（只改显示）⇒ 本包装只走「建缩放特征」那条；若回 None，报错**指向「多半是缩放了图形体」**」✓ |
| ★★ 实现现状 | ★★ **`scripts/` 里扫不到**对应包装（`*scale*` 全是**工程图/文字比例**）✗ ⇒ ★ **能力已在探针里验过，但没缝进 `scripts/`、也没暴露** ✓ |

⇒ ★★ **精确任务（下一轮做）**：
  1. ★ 读 `tools/probe_spec211_scale.py` 拿到**已验证的调用序**（★ 来源：探针 + 官方 `IFeatureManager::InsertScale`）✓
  2. ★ 在 `scripts/` 写**一个**包装（★ 形态照 `limitations`：★ 只走"建缩放特征"那条，★ 若回 `None` 报错并指向"多半缩放了图形体"）✓
  3. ★ 暴露成工具，★ **名字带 `scale`/`deform`**（★ 让地图命中）⇒ ★ **特征/缩放变形 ❌→✅** ✓
  4. ★ 顺带 ★ **删掉地图那条错误的剔除**（它说"本仓库没有实体缩放，命中的是工程图比例" —— ★ 而 `scale_feature` 是 **`verified`**）✓
  5. ★★ ★ **台账 `level` 不动**（★ 它已经是 `verified`，★ 有真机证据 ✓）· ★ 但**新包装要自己跑一次真机**才算数（红线⑥）✓

## 四之六、★★★ 第 7 轮：★ **`FALSE_POS` 三条剔除全是过期错的 ⇒ 已全清**（137/145 = 94%）

★★ 结论先行：★ **`solidworks_scale_feature` **早就在 `all_specs()` 里**（→ `sw_part.insert_scale`），
  ★ 名字**含 `scale`** ⇒ ★ 生成器的关键词**本来就命中** ✗ ⇒ ★★ **唯一挡路的就是那条剔除** ——
  而它写「**本仓库没有实体缩放/变形**」✗，★ 与事实相反：
  ★ ① 工具在 ✓ ② 台账 `scale_feature` = **`verified`**（真机：特征树新增 `缩放比例1`；主判据**体积比 x³** 因子 3.0 ⇒ 期望 27.0 ✓）

| 轮 | ★ 清的剔除 | ★ 依据 | ★ 效果 |
|---|---|---|---|
| 3 | 钣金/展开折叠 · 焊件/角撑板 | ★ 工具与实现**都在**（`create_unfold` / `weldment_gusset_create`）| ★ +2 |
| 4 | （加宽关键词）成形工具 | ★ 生成器要 `forming_tool`，本仓叫 `insert_form_tool` | ★ +1 ⇒ **钣金 100%** |
| 7 | 特征/缩放变形 | ★ `solidworks_scale_feature` 在 · 台账 **`verified`** | ★ +1 |
| | | ★ **`FALSE_POS` 块现已为空（0 条）** | ★ **137/145 = 94%** |

## 四之七、★ 当前逐域（★ 6 → 仍是 6 个域 100%，但特征与焊件已很近）

| 域 | ★ 现在 | ★ 差 |
|---|---|---|
| 草图 · 钣金 · 模具 · 工程图 · 评估 · 仿真 | ★★ **100%** ✅ | 0 |
| 特征 | ★ **26/28 = 93%** | ★ 2（边界凸台 · 特征识别）|
| 曲面 | 13/14 = 93% | ★ 1（边界曲面）|
| 焊件 | 6/7 = 86% | ★ 1（圆角焊缝）|
| 装配 | 7/10 = 70% | ★ 3（零部件阵列可建 · 序列/性能分析**无 API**）|
| 其他 | 11/12 = 92% | ★ 1（PDM **无 API/需许可**）|
| **合计** | ★★ **137/145 = 94%** | ★ **8** |

## 四之八、★★★ 第 8 轮：边界凸台 / 边界曲面 **可建**，且**官方有现成示例**（T-219-04 的门已过）

| 证据 | ★ 内容 |
|---|---|
| ★★ 接口目录**存在** | ★ `C:\swapi\types\` 下有 **`IBoundaryBossFeatureData`** ✓（★ 同族另有 `ILoftedBendsFeatureData` / `ILoftFeatureData`）|
| ★★ 官方 **Example**（CHM 解包，★ 铁律 4 第 0 步的第 ③ 样）| ★ `Insert_Boundary_Feature_Example_CSharp.htm`（★ + `_VB` / `_VBNET`）✓<br>★ `Insert_Boundary_Surface_Feature_Example_VB.htm` ✓<br>★ `Insert_Solid_Body_Boundary_Surface_Feature_Example_CSharp.htm` ✓ |
| ★ 仓库现状 | ★ `IBoundaryBossFeatureData` **只出现在** `scripts/sw_api_sldworks.py`（**反射转储**）里 ⇒ ★ **没有实现** ✓ |
| ★ 命名含 Boundary 的成员（★ 别误认）| ★ `IFillSurfaceFeatureData.GetPatchBoundary*` · `IWeldmentTrimExtendFeatureData.GetTrimmingBoundary*` · `ISketchManager.CreateBoundaryHatch` · `IFeatureManager.SetFreeformBoundaryContinuity` ⇒ ★ **都不是**边界凸台/边界曲面 ✗ |

⇒ ★★ **裁定：两格 = A 类「可建」**，★ 且起点是**最好的**（★ 有官方示例给"调用序"，★ 签名与 `## Remarks` 另有其页）✓

## 四之九、★★ 第 9 轮：官方示例读到了 —— 调用序 + 一条**硬约束**

★ 文件：★ `AI Solidworks\官方文档\…\Insert_Boundary_Feature_Example_VB.htm`（119 有效行）✓
★ 官方自述的 **Postconditions**（逐字）：
  ★ 「① Opens a new part. ② **Creates two boss-extrude features.** ③ **Selects a face on each
  boss-extrude feature.** ④ **Creates a boundary feature using the selected faces.** ⑤ Gets and sets some
  boundary feature data.」✓
★ 示例里用到的对象：★ `SldWorks.BoundaryBossFeatureData` · `FeatureManager` · `ModelDocExtension` ·
  `SelectionMgr` · `SketchManager` · `SelectByID2(..., "SKETCHSEGMENT", …)`（★ 草图段那条是**按名字**）✓

★★★ **由此得到一条硬约束（★ 会决定实现形态）**：
  ★★ **边界特征要求"先选中若干面"** ⇒ ★ 按我在规格 217 第 7 轮定的那道闸，
  ★ 我们的工具**必须同时给声明式选择入口**，★ 否则 `release_check` 的**预选族门禁**会判它
  「要求先选中、而没有任何选法」**并拦下** ✗（★ batch103 那次就是被它拦回的）✓
  ⇒ ★ 实现形态：★ **`*_report` 包装 + `selection` / `selection_kind` 参数**（★ 选择紧邻调用）✓

## 四之十、★★★ 第 10 轮：拿到**完整官方调用配方**（★ 入口名只有示例给得出）

★ 来源：★ `Insert_Boundary_Feature_Example_VB.htm` 第 67–74 行（★ 逐行读出）✓

```
① swModel.ClearSelection2 True
② swModelDocExt.SelectByID2("", "FACE", x1, y1, z1, False, 0, Nothing, 0)   ← 面上的点选第 1 个面
   swModelDocExt.SelectByID2("", "FACE", x2, y2, z2, True,  0, Nothing, 0)   ← Append=True 选第 2 个面
③ swFeatureMgr.SetNetBlendCurveData 0, 0, 0, 0, 1, True
   swFeatureMgr.SetNetBlendCurveData 0, 1, 0, 0.26179938779915, 1, True
④ swFeatureMgr.SetNetBlendDirectionData 0, 32, 0, False, False
   swFeatureMgr.SetNetBlendDirectionData 1, 32, 0, False, False
⑤ swFeature = swFeatureMgr.InsertNetBlend(1, 2, 0, False, 0.0001, True, True, True, True, False, -1, -1, False, -1, False, …)
```

★★★ **三条只有示例才给得出的情报**（★ 本仓铁律 4 明写"例子给的是调用序"）：
1. ★★ **入口是 `IFeatureManager::InsertNetBlend`** —— ★ **不叫** `InsertBoundaryBoss` ✗
   ⇒ ★ 只查接口名会**查不到**（★ 这正是 `docs/official-docs-first.md` 记的那类坑）✓
2. ★★ **两个面是"按面上的点"选的**（`SelectByID2("", "FACE", x,y,z, …)`）★ 且第二个用 **`Append=True`** ✓
   ⇒ ★ 与我们的事实 32 一致（实体没有可用名字，只能按点选）✓
3. ★★ **建之前必须先设数据**：`SetNetBlendCurveData` ×2 + `SetNetBlendDirectionData` ×2 ⇒ 再 `InsertNetBlend` ✓
   ★（★ 角度 `0.26179938779915` ≈ **15°** 的弧度值 ⇒ ★ 说明该参数是**弧度**，★ 我们的工具要按**度**给用户、内部转弧度 ✓）

## 四之十一、★★★ 第 11 轮：官方签名与枚举拿到 —— ★ **一个包装可同时点亮两格**

★ 来源：★ `C:\swapi\types\IFeatureManager\InsertNetBlend.md` · `SetNetBlendDirectionData.md`（★ 逐字读过）✓

| 成员 | ★ 要点 |
|---|---|
| **`InsertNetBlend`** | ★ `Feature InsertNetBlend(short Type, short NCurvesDir1, short NCurvesDir2, bool HasCenterline, double TessTolFactor, bool WantsSolid, bool MergeBody, bool FeatureScope, bool AutoSelect, bool Thin, double Thickness1, double Thickness2, bool ReverseThickness, short ThinSolidType, bool UseSharedThickness, bool CapEnds, double EndThickness, bool AutoFillet, double FilletRadius, bool ForceNonRational)` ✓ |
| ★★ `Type` 枚举（官方逐字）| ★★ **`0 = Base` · `1 = Boss` · `2 = Surface` · `3 = Cut`** ⇒ ★★ **同一入口同时管「边界凸台(1)」与「边界曲面(2)」** ✓✓ |
| ★ 其它要点（官方逐字）| ★ `WantsSolid`「**only valid when Type = 0, 1, or 3**」· `TessTolFactor`「default value …」· `ThinSolidType` 用 `[[swThinWallType_e]]` ✓ |
| `SetNetBlendDirectionData` | ★ `(short Direction, short InfluenceType, short TrimCurves, bool BlendClosed, bool SplitSurfaces)`<br>★ `Direction`：**0 = Direction 1 · 1 = Direction 2**<br>★ `InfluenceType`：**0 = Global · 1 = To Next Curve · 2 = To Next Sharp · 3 = To Next Edge**<br>★ `TrimCurves`：**0 = False to trim · 1 = True to trim**<br>★ `BlendClosed`：**true 闭合** · ★ `SplitSurfaces`：**Not used** ✓ |
| ★ 该页 `## Examples` | ★ 指向 `Insert_Boundary_Surface_Feature_Example_VB` 与 `Insert_Boundary_Feature_Example_CSharp` ✓（★ 与我们读的那份同族）|

★★ **由此定的实现形态（★ 下一轮照做）**：
  ★ **写一个** `insert_net_blend_report(model, *, blend_type, selection, selection_kind, …)`：
  ★ `blend_type=1` ⇒ 边界**凸台** · `blend_type=2` ⇒ 边界**曲面** ⇒ ★ **两格一起点亮** ✓
  ★ + **声明式选择**（★ 面按"面上的点"选、第二个 `Append=True` —— ★ 配方已逐行拿到）✓
  ★ + 参数按用户友好给（★ 度/毫米），内部转官方口径（★ 弧度、米）✓
  ★ + `*_report` 回读判据（★ 特征树增量 + 若 `None` 报错并指向官方 `Returns` 的语义）✓

## 五、下一个动作（只写一条）

★ **T-219-04（★ 前置全齐，下一轮直接写代码）**：
  1. ★ 查 `docs/dead-ends.md` + 台账 `surface_*` / `loft*` 的 `limitations`（★ 先扫走死的路）✓
  2. ★ 在 `scripts/` 写 `insert_net_blend_report`（★ 形态见上）⇒ 暴露 ⇒ 台账归属 ⇒ 契约测试 ✓
  3. ★ **真机验证**（★ `sw_guard.py`，用完关 SolidWorks）★ 两个 Type 各跑一次 ✓
  4. ★ 重跑地图 ⇒ ★ 特征 **27/28** · ★ 曲面 **14/14 = 100%**（★ 第 **7** 个 100% 的域）✓

★★ **两条元结论（★ 比单格要紧，写进规格）**：
1. ★★ **`--check` 说"是最新的"只证明「地图与生成器一致」，不证明「地图与事实一致」** ✗ ——
   ★ 实测：地图**两处人工剔除是错的**（钣金展开折叠 · 焊件角撑板），★ 它们写于
   `create_unfold` / `weldment_gusset_create` **还不存在**的时候，之后无人回头改 ✓
2. ★★ **引用这张地图下结论前，必须对它标的 ❌ 逐条复核**；★ 它标 ✅ 的也可能名不副实
   （★ §六 自述"旋转曲面 ✅ 其实未暴露"）✓

## 五、下一个动作（只写一条）

★ **T-219-02**：★ **先做 B 类的 6 项**（成本最低、数字立刻动）——
★ 手法：★ ③ 特征识别 / ⑪ 性能分析 / ② 缩放变形 ⇒ **把已有实现暴露成工具**（★ 名字里带上生成器要的关键词：
`feature_recognition` / `performance_analysis` / `deform`）；★ ⑤ 成形工具 ⇒ ★ 别名带上 `forming_tool` ✓
★ ⑤⑥⑦ 三项（★ 名字其实早就命中）⇒ ★ **只需在 `verdicts.md` 留证** ⇒ ★ 地图下次重算时会自然变 ✅
（★ 地图生成器在本仓之外，★ 我们改不了它的剔除表 ✗ ⇒ ★ **但要留证说明它错了**）✓

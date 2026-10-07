# 规格 219 · T-219-01 去伪裁定表（12 项）

> ★ 口径：★ 地图 `docs/user-feature-coverage.md` 是**关键词子串命中工具名**即算「有」（★ §二 自述）✓
> ★ 本表对 12 项各查**三处**：★ `all_specs()` 工具名 · `scripts/sw_*.py` 实现 · `capabilities.yaml` 台账 ✓
> ★★ 裁定三类：★ **A 真缺口**（确实没有）· ★ **B 假阴性**（我们有，名字没命中）· ★ **C 不可做**（需许可证/后端不成）✓
> ★ 取证命令（可复算）：`python -c` 扫 `rc.all_specs()` / `scripts/sw_*.py` 的 `def` / 台账 id，关键词见本表 ✓

## 一、★★ 裁定总览（★ 结论：**12 项里约 6 项是假阴性**）

| # | 域 | 功能 | ★ 裁定 | ★ 关键证据 |
|---|---|---|---|---|
| 1 | 特征 | 边界凸台 | ★ **A 真缺口** | ★ 工具命中只有 `*_bounding_box`（**边界框**，不是边界凸台）· ★ 台账/实现均无 `boundary boss` ✓ |
| 2 | 特征 | 缩放/变形 | ★★ **B 假阴性** | ★ 实现有 **`create_deformed_body`** · 台账有 **`scale_feature`**；★ 地图 §六 把这条判为假阳性（"命中工程图比例"）⇒ ★★ **地图这条判错了**（它没看到 `create_deformed_body`）⚠ **待核 1** |
| 3 | 特征 | 特征识别·Instant3D | ★★ **B（有实现未暴露）** | ★ 实现有 **`recognize_and_create` / `recognize_interactive`** ✓ · ★ 工具面与台账**都没有** ⇒ ★ 属"已实现但没暴露"✓ |
| 4 | 曲面 | 边界曲面 | ★ **A 真缺口** | ★ 工具/实现/台账 **三处全无** ✓ |
| 5 | 钣金 | 成形工具 | ★★ **B 假阴性** | ★ 工具 **`solidworks_insert_form_tool`** ✓ · 实现 `insert_form_tool_report` · 台账 **`forming_tool`** ✓ |
| 6 | 钣金 | 展开/折叠 | ★★ **B 假阴性** | ★ 工具 **`create_fold` / `create_unfold`** ✓ · 台账 `sheet_metal_fold` / `sheet_metal_unfold` ✓（★ 规格 216 **真机建成**过）|
| 7 | 焊件 | 角撑板（焊件） | ★★ **B 假阴性** | ★ 工具 **`solidworks_weldment_gusset_create`** ✓ · 实现 `insert_weldment_gusset` · 台账 `weldment_gusset` ✓ ★★ 地图 §六 曾把它当假阳性剔除 ⇒ **剔错了**（那是**真焊件** gusset）⚠ **待核 2** |
| 8 | 焊件 | 圆角焊缝 | ★ **A 或 C** | ★ 工具/实现**均无** · ★ 台账有 `fillet_weld_bead`（level = `stitched`）⇒ ★ 需查它的实现落在哪、以及官方入口是否可达 ⚠ **待核 3** |
| 9 | 装配 | 零部件阵列 | ★ **A 真缺口** | ★ 工具/实现/台账 **三处全无** ✓ |
| 10 | 装配 | 装配序列/说明书 | ★ **A 真缺口** | ★ 工具命中的全是 **BOM**（`collect_assembly_bom` 等）✗ ★ BOM ≠ 装配序列/说明书；★ 实现里无序列/说明书入口 ✓ |
| 11 | 装配 | 装配体性能分析 | ★★ **B（有实现未暴露）** | ★ 实现有 **`set_performance_options`** ✓ · ★ 工具面/台账没有 ⇒ ★ 属"已实现但没暴露"✓ |
| 12 | 其他 | PDM | ★★ **C 不可做** | ★ 台账 `pdm` = **`not_implemented`** ✓ · ★ 既有裁定（`docs/union-coverage-matrix.md`）：★ **需 PDM 许可证 + `swdocumentmgr` 296/4683 成员** ✓（★ `document_dependencies` / `collect_pdm_evidence` 只是**读依赖**，不是 PDM 系统）✓ |

## 二、★ 由此得到的处置清单（★ 这是下一步的准确工作单）

### ★ B 类（★ 假阴性 / 未暴露）—— **6 项，成本最低**

| # | 功能 | ★ 处置手法 |
|---|---|---|
| 3 | 特征识别·Instant3D | ★ **暴露** `recognize_and_create` 等（★ 先过"预选族"闸：查函数体是否要求先选中）|
| 5 | 成形工具 | ★ 已有工具 ⇒ ★ **让匹配器看得见**（★ 查地图取的名集合是 `all_specs()` ⇒ ★ 若工具名不含 `form` 关键词则补**别名/正名**）|
| 6 | 展开/折叠 | ★ 同上（★ 工具名已含 `fold`/`unfold` ⇒ ★ **为何没命中？** ⇒ ★ **待核 4**：可能地图的该行关键词是"展开/折叠"整词匹配失败）|
| 7 | 角撑板（焊件） | ★ 同上（★ 名字已含 `gusset` ⇒ ★ 与 #6 同因）|
| 11 | 装配体性能分析 | ★ **暴露** `set_performance_options` ✓ |
| 2 | 缩放/变形 | ★ **暴露** `create_deformed_body`（或把 `scale_feature` 接上）⚠ **待核 1** |

### ★ A 类（★ 真缺口）—— **4-5 项，要真建**

| # | 功能 | ★ 先查什么 |
|---|---|---|
| 1 | 边界凸台 | ★ 官方 `IBoundaryBossFeatureData`？★ 先读 `C:\swapi\types\` 有无该接口 |
| 4 | 边界曲面 | ★ 同上（★ 注意：本仓已有 `insert_lofted_ref_surface` / `insert_fill_surface2`，★ 要确认不是同一件事）|
| 8 | 圆角焊缝 | ★ 先查台账 `fillet_weld_bead` 指向哪、官方入口是什么 |
| 9 | 零部件阵列 | ★ 官方 `IComponent2` / `IAssemblyDoc` 的阵列入口 |
| 10 | 装配序列/说明书 | ★ 官方有没有"装配序列/说明书"这个概念（★ 可能对应 `IAssemblyDoc` 的爆炸 + 序列？★ 查不到就按 C 如实写）|

### ★ C 类（★ 不可做）

| # | 功能 | ★ 原因（带引用）|
|---|---|---|
| 12 | PDM | ★ 需 PDM 许可证；`swdocumentmgr` 296/4683 成员；★ 既有裁定见 `docs/union-coverage-matrix.md` 的「不做 + 原因」✓ |

## 三、★★★ 待核 4 已解 —— 并查出**地图两处"人工剔除"是错的**

★ 生成器 `D:\SW-coverage-tool\gen_user_feature_coverage.py`（433 行）**第 59–187 行**就是功能 → 关键词表 ✓
★ 逐条对照后：

| 格 | ★ 生成器要的关键词 | ★ 我们实际有的 | ★ 裁定 |
|---|---|---|---|
| 钣金/展开折叠 | `("flatten","unfold")` | ★ `create_unfold`（含 `unfold` ✓）· `flatten_surface`（含 `flatten` ✓）| ★★ **本该命中** ⇒ ★ 地图 **第 186 行的人工剔除写错了**（★ 它只提到"焊件文件夹里的 fold"，★ 那是**另一个**命中）|
| 焊件/角撑板 | `("weldment_gusset","add_gusset")` | ★ `solidworks_weldment_gusset_create`（含 `weldment_gusset` ✓）| ★★ **本该命中** ⇒ ★ 地图 **第 187 行的剔除也写错了**（★ 它只说命中了钣金 gusset，★ 漏了这条真命中）|
| 钣金/成形工具 | `("forming_tool",)` | ★ 我们是 `insert_form_tool`（★ **差一个字母**）| ★ 假阴性 → ★ 暴露/别名时用 `forming_tool` 这个词 ✓ |
| 特征/缩放变形 | `("scale","deform")` | ★ `drawing_*_scale` 会被命中，★ 而地图 **第 185 行人为剔除**；★ 我们另有 `create_deformed_body` ✗ 没被看见 | ★ 假阴性（★ 剔除范围过宽把 `deform` 也盖掉了）|
| 特征/特征识别 | `("feature_recognition","instant3d")` | ★ 实现 `recognize_and_create` ✗ 名字不含关键词 | ★ 假阴性（暴露时用 `feature_recognition` 这个词）|
| 装配/性能分析 | `("performance_analysis","assembly_performance")` | ★ 实现 `set_performance_options` ✗ | ★ 假阴性（暴露时用 `performance_analysis`）|

★★ **由此得到一条元结论（★ 比单格更要紧）**：
  ★★ **`--check` 说"是最新的"，只证明「地图与生成器一致」，不证明「地图与事实一致」** ✗
  ★ 那两处错误剔除**写于 `create_unfold` / `weldment_gusset_create` 还不存在的时候**，之后无人回头改 ✓
  ⇒ ★★ **定则（写进本规格）**：★ **引用这张地图下结论前，必须对它标的 ❌ 逐条复核**；
  ★ 它标 ✅ 的也可能名不副实（★ §六 自述"旋转曲面 ✅ 其实未暴露"）

## 四、★★ 修正后的三类清单（★ 这就是准确工作单）

| 类 | ★ 项数 | ★ 是哪几项 |
|---|---|---|
| ★★ **A 真缺口（要真建）** | **5** | ★ 特征 边界凸台 · 曲面 边界曲面 · 焊件 圆角焊缝 · 装配 零部件阵列 · 装配 装配序列/说明书 |
| ★★ **B 假阴性 / 未暴露** | **6** | ★ 钣金 展开折叠 · 焊件 角撑板 · 钣金 成形工具 · 特征 缩放变形 · 特征 特征识别 · 装配 性能分析 |
| ★★ **C 不可做** | **1** | ★ 其他 PDM（需许可证 + 296/4683 成员）|
| | **12** | ★ 6 + 5 + 1 = 12 ✓ 对得上 |

## 五、★ 四个"待核"的处置

| 编号 | ★ 结论 |
|---|---|
| **待核 1** | ★ `create_deformed_body` 需读源码块确认它是"实体变形"，★ 若是 ⇒ ★ 暴露成含 `deform` 之名即可命中 ✓ |
| **待核 2** | ★ `weldment_gusset` 台账 level 与真机读数需读（★ 名字已命中，★ 只需修地图那处剔除）|
| **待核 3** | ★ `fillet_weld_bead` 的实现落在哪、官方入口可达否 ⇒ ★ 决定它是 A 还是 C ✓ |
| **待核 4** | ★★ **已解**（见本表 §三）✓ |

# Feature 136 · 拉伸族（把草图变成实体）（砌墙 W4 续）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题

W4（`specs/135`）补了「**建草图 + 画几何**」，但草图**还只是线**。
本特性补「**把草图变成实体**」⇒ ★ 两批合起来，本仓库**第一次**具备**完整的建模最小闭环**：
```
建草图 → 画几何 → **拉伸成实体** → 用只读工具回读验证
```
★ 而在此之前，MCP 里**已经有** `revolve_boss` / `create_hole_feature` / 钣金 `base_flange`，
却**连拉伸都没有** —— 本特性把这条链接通。

## 二、★ 范围是**核过之后**定的（三层，见事实 162/163）

| 层 | 结论 |
|---|---|
| 缺口本身 | ⑯那 28 个缺口名**全是"建/改"**，而原计划写 W4 取「回读」⇒ **不对口**（回读已有） |
| 可挂性 | **首参可注入且没挂的"建特征"函数 10 个**；★ 本特性**只取拉伸族 3 个** |
| 前置 | ★★ **没有"建草图"就全都用不了** ⇒ W4 先补了前置（`specs/135`） |

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能**拉伸凸台**（加料） | 官方 `IFeatureManager.FeatureExtrusion3`（**23 参数**，既有事实 2）；本项目 `sw_part.extrude_boss`（MIT） |
| R2 | 能**拉伸切除**（减料），且 `0` = **完全贯穿** | 官方 `IFeatureManager.FeatureCut4`（★ **既有事实 1**：切除的正确入口是它，不是 `FeatureExtrusion3(Flip=true)`）；`sw_part.extrude_cut` |
| R3 | 能**中面拉伸**（两侧对称），参数是**总深** | 官方 `FeatureExtrusion3` 的 `T1`/`T2` 双侧语义；`sw_part.extrude_midplane` |
| R4 | 长度参数一律 **`_mm`** | 并入六条规则**规则 2** |
| R5 | ★ **不做换算** | 既有事实 73：`sw_part` 的模块单位是**毫米** ⇒ 换算本就无需发生 |
| R6 | 草图名找不到 ⇒ **报错** | 本项目一贯纪律（选不中/找不到要报错，不静默）|

## 四、★ 为什么只做 3 个（不把 10 个全挂）

```
★ `chamfer`（倒角）· `fillet`（圆角）**本批不做** ——
  理由不是"它不对"：`chamfer` 的调用形态我**已按铁律 4 核过是对的** ——
    · `swChamferType_e.swChamferAngleDistance = 1`（swapi 与出厂反射**两源一致**）
    · 实现传的是 `(Options=4, ChamferType=1, Width=distance, Angle=angle_rad, …)`
      ⇒ 与官方参数说明「Width/Angle 只在 AngleDistance 下有意义」**一致** ✓
    · `Options=4` = `swFeatureChamferTangentPropagation`
  ★★ **但它们没有 `edges` 参数** ⇒ 倒哪些边必然来自**当前选择**
  ⇒ 需要一层**规则 3 的声明式 `selection`** 包装 ⇒ ★ **单独一批做**。
★ 理由：**一个批次里混两种包装形状，会让证据脚本与工具说明都变复杂**；
  而"用 `selection` 驱动建特征工具"在本项目是**第一次**，值得单独验证。
```

## 五、参数命名（规则 2 的落地）

```
能力层形参：`depth` / `total_depth`（**不带 `_mm`**）
⇒ 对外用 `param_alias` 改成 `depth_mm` / `total_depth_mm`
★ **能力层一行不改** —— 照 W4 的定则（对外名与对内名不同时用 `param_alias`，
  别改能力层形参名，那会动到既有调用点）
```

## 六、验收

```
① 静态：`all_specs()` 里出现 3 个新工具，且门禁全绿
② ★ 真机：`output/feature-build-evidence.json` 的 `verdict` == "pass"，且含**数字断言**：
   · 矩形 40×20 拉伸 10mm ⇒ ★ 包围盒 `size == [40, 20, 10]`
   · 中面拉伸总深 10 ⇒ `size == [40, 20, 10]` 且 **min/max 为 ±5**（两侧对称）
   · 切除 `depth_mm=0` ⇒ 特征树**多一个特征**
   · **负例**：不存在的草图名 ⇒ **报错**
```

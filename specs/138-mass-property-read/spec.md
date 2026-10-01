# Feature 138 · 读质量属性（砌墙 W5）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> ★ 编号说明：计划里 W5 曾写成 `135`/`138` —— ★ 因为**一个 W 拆成了多个特性**（W4 → 135/136/137）
> ⇒ 计划已改为**不写死编号**，用"当时的下一个空闲号"。

## 一、要解决的问题：**又是「能写不能读」**

```
· `sw_export.set_mass_property_override`（**改**覆盖值）—— 已有。
· ★ 而**读不出实际质量属性**（MCP 与能力层都没有 —— 见事实 166 的核查）
⇒ 而「这个零件多重 / 体积多少 / 重心在哪」是**最常被问的问题之一**。
★ 与 W3「能写自定义属性却读不回来」（`specs/133`）**同一个形状**。
```

## 二、★ 范围是**核过缺口本身**之后定的

⑫inspect 那 16 个缺口名逐个核：

| 类 | 内容 | 判断 |
|---|---|---|
| **已有** | `bbox`（= `solidworks_part_bounding_box`，名字不同）· `view_orientation` / `zoom_to_fit` | 名字差异 |
| **不是只读** | `display_mode`（改视图）· `analyze_draft`（要选面） | 本阶段不做 |
| ★ **真缺且高频** | **读质量属性**（`calculate_mass_properties` / `mass_props`） | ★ **本特性** |
| 其余 | `measure_distance` / `sensors` / `status` / `check_errors` / `reference_geometry` / `analyze_geometry` / `capture_screenshot` | 留后续批次 |

## 三、★★★ 三条形态由**真机探针**定死（`tools/probe_mass_property_reads.py`，轮 233）

```
① 取法：★ **`model.Extension.CreateMassProperty` 是属性**（当属性取就拿到对象）
   ⚠⚠ **与 W3 的 `Extension.CustomPropertyManager` 相反**（那个**必须当方法调用**，见事实 161）
   ⇒ ★ 定则：**同一个父对象的不同成员，取法也可能不同** —— 教训**不能照搬**。

② 单位：★ 实测是**「毫米系」**（盒 40×20×10 mm ⇒ Volume **8000** · SurfaceArea **2800** ·
   CenterOfMass z = **−5**）—— **不是** SI 米。
   ⇒ 与既有事实 73 的 `IBody2.GetBodyBox`（毫米）一致；与官方其余几何接口惯用的「米」**不同**
   ⇒ ★ 本能力**不做任何换算**。

③ ⚠⚠ **`Mass` 的物理单位**未确证**（如实记，不猜）**：
     盒上 `mass` **恰好等于** `volume(mm³) × density` ⇒ **量纲不成立**
     ⇒ ★ 照实透传；工具说明里**明写"未确证"**；★ **不猜、不给它安一个单位**。
```

## 四、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能读**体积** | 官方 `IMassProperty2.Volume`；本项目 `sw_mass_property`（MIT） |
| R2 | 能读**表面积** | 官方 `IMassProperty2.SurfaceArea` |
| R3 | 能读**重心**（三分量） | 官方 `IMassProperty2.CenterOfMass` |
| R4 | 能读**密度**与**质量** | 官方 `IMassProperty2.Density` / `Mass` —— ★ 但两单位**未确证**（见三之②③） |
| R5 | 在**工程图**上调用要**报错** | 本项目一贯纪律（类型不对要报错）—— ★ **这条是负例逼出来的**（见六） |
| R6 | ★ **不做任何换算** | 事实 73 + 本特性实测：单位是毫米系 |

## 五、★ 为什么只有 **1** 个工具

```
`Volume` / `SurfaceArea` / `CenterOfMass` / `Density` / `Mass` 这几样**总是被一起问**
（"这零件多重、多大、重心在哪"）⇒ ★ 拆成 5 个只会让 AI 多调 4 次拿同一件事。
★ 与 W3 的定则一致（`count`/`names` 已被"读全部"包含 ⇒ 不重复挂）。
```

## 六、★★★ 真机负例逼出来的一个**判据升级**（本特性最值钱的一处）

```
★ 我最初在能力层用**行为判据**（`hasattr(mp, "Mass") or hasattr(mp, "Volume")`）
  判断"是否取到质量属性对象" —— 那是照事实 161/167 的定则写的。
★★ 而真机负例（在**工程图**上调用）**没有抛错**：工程图上的 `CreateMassProperty`
  **竟然也返回了一个带 `Mass`/`Volume` 的对象** ⇒ ★ **静默通过并返回无意义读数**。
⇒ ★★★ **教训：行为判据证明"这个成员存在"，不证明"这个读数是这个文档的"**
  —— 它必须**配合文档类型判据**。
⇒ 修法：`require_mass_property_document`（`GetType()==3` ⇒ 报错）。
  ★ 那是 `specs/132` 的 `require_drawing` 的**镜像用法**：
    那个判"**必须是工程图**"，这个判"**不能是工程图**"。
```

## 七、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不暴露 `AccuracyLevel` | 实测 **`AttributeError`**（读不到）|
| 不用 `IModelDoc2.GetMassProperties`（12 个 double 的后备） | ★ 它比 `IMassProperty2` **少**（没有 Density），且**要靠位置记次序** ⇒ 用**有名字**的成员 |
| 不读惯性矩 / 主惯性轴 | 能力层只读了 5 个成员（留后续批次）|
| 不碰保存 / 另存 / 删除 | 计划明写本阶段不做高风险写操作 |

## 八、验收

```
① 静态：`all_specs()` 里出现 1 个新工具，且门禁全绿
② ★ 真机：`output/mass-property-evidence.json` 的 `verdict` == "pass"，且含：
   · ★ **数字断言**：盒 40×20×10 ⇒ volume **8000** · surface_area **2800** · center_of_mass **[0,0,−5]**
   · ★ 如实记录 `mass` 的量纲疑点（`mass / (volume×density) == 1.0`）与 `AccuracyLevel` 读不到
   · **负例**：在**工程图**上调用 ⇒ 报错
```

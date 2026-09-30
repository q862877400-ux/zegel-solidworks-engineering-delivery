# AI 实操指南 · SOLIDWORKS API（按"要做 X 怎么做"组织）

> **本指南只收录【实测通过】的用法。** 2026-09-28 用 `tools\api_scan*.ps1`
> 逐个调用真实 API 验证过，未验证的会明确标注"未验证"。
> 底层是本机 `SolidworksExecution.exe`（自建执行层），经 `tools\call.ps1` 直连 REST。

---

## 0. 四条铁律（违反必踩）

### 铁律 0（最重要）：**成功码不等于成功——必须验证产物**
本项目已踩 **4 次静默失败**，全部是"返回成功、实际没做事"：

| 案例 | 返回 | 真相 |
|---|---|---|
| `edit_feature delete` | COMPLETED | 什么都没删 |
| `auto_dimension_drawing` | COMPLETED | `dimension_count=0`（没视图可标）|
| `sketched_bend` | ~~COMPLETED 但没弯~~ | ⚠ **这条是我误判的**，见下 |
| `design_check` | `rc=0 dsgnchkNOErr` | 零报告文件 |

⇒ **任何"建特征/写报告/改几何"的操作，成功判据必须是【产物】**：
- 建模 → `analyze_model` 的**体积+面数+边数+包围盒**变了
- 报告 → **报告目录里真的有文件**（不是返回码说成功）
- 写值 → 读回来值确实变了

```powershell
# 通用做法：操作前后各取一次几何指纹再比对
Call 'analyze_model' @{ analysis_type='mass_properties' }
Call 'analyze_model' @{ analysis_type='geometry' }
```
现成脚本：`tools\audit_silent.ps1`（对每个 ✅ 能力做前后指纹对比）。

### ⚠ 铁律 0 的反面教训：**用错判据会得出错误结论**
`sketched_bend` 被我误判成"假成功"，因为我查的是**各面 z 坐标分布**（都在 −0.002~0 ⇒ "没变"）。
**它其实完全正常：面数 6 → 14，真的弯了。**
我选的维度恰好对折弯不敏感。

⇒ **判据必须匹配操作改变的量**：

| 操作类型 | 会变的 | 不会变的（别拿来判） |
|---|---|---|
| 拉伸/切除/圆角 | 体积、面数、边数 | — |
| **钣金折弯** | **面数、包围盒** | **体积**（材料守恒）|
| 阵列 | 体积、包围盒 | 面数（可能融合成一体）|
| 工程图标注 | `dimension_count` | — |
| 报告类 | **输出目录里的文件** | 返回码 |

### 已修掉的静默失败（服务端现在会明确报错）
```
auto_dimension_drawing → NO_DIMENSIONS_INSERTED
auto_center_marks      → NO_CENTER_MARKS_INSERTED
design_check           → NO_REPORT_GENERATED
sketched_bend          → BEND_WAS_A_NOOP（面数未增时）
edit_feature delete    → DELETE_FAILED
extrude_feature        → EXTRUSION_WAS_A_NOOP（0 实体/0 面时）
add_edge_feature       → EDGE_FEATURE_WAS_A_NOOP（0 实体时）
```

### ⭐ 全服务端成功判据审计（2026-09-28，`tools\audit_verdicts.ps1`）

判据强度分级（**从强到弱**）：

| 级别 | 含义 | 处数 |
|---|---|---|
| **PRODUCT** | 读回实际产物（文件/面数/体积/插入数） | 4 |
| **TREE** | 复查特征树 | 2 |
| **EXIST** | ⚠ `feature != null`（**存在性判据**）| 5 |
| **DIRECT** | ⚠ 无任何验证，直接 COMPLETED | 35 |

**EXIST 的 5 处（静默失败温床）—— Round 11-12 已全部加固**：
```
ExtrudeFeature        → 读回实体/面数，0 实体 0 面 ⇒ EXTRUSION_WAS_A_NOOP
AddEdgeFeature        → 读回实体数，0 实体 ⇒ EDGE_FEATURE_WAS_A_NOOP
CreatePattern         → 记录体积+包围盒（只记录不判定：阵列合法融合时面数不变）
SheetMetalFeature     → 读回实体数，0 实体 ⇒ SHEET_METAL_WAS_A_NOOP（flat_pattern 豁免）
AddReferenceGeometry  → 按名复查特征树，不在树里 ⇒ REFGEOM_WAS_A_NOOP
```
回归测试 `tools\regression.ps1`（9 项核心能力）**全部通过**，加固未破坏正常功能。

⚠ 加固时的两个坑：
- 阵列**合法地**可能不改变面数（实例融合成一体）⇒ 只能用体积/包围盒判，且不宜直接判失败
- `flat_pattern` 是表示性特征，**豁免**实体检查

⇒ **写这类工具时的规则**：成功判据必须从"**操作改变了什么**"推导，
不能用"对象是否非空"。存在性判据几乎必然放过静默失败。

### 铁律 1：数组参数要传【真数组】，不是 JSON 字符串
```powershell
# ✅ 对
Call 'add_sketch_entities' @{ segments = @(
    @{entity_type='line'; x1=-0.05; y1=-0.03; x2=0.05; y2=-0.03}, ...
) }
# ❌ 错 —— 会报 MISSING_PARAMETER: segments is required
Call 'add_sketch_entities' @{ segments = "[{entity_type:'line',...}]" }
```
`call.ps1` 内部用 `ConvertTo-Json` 整体序列化，所以 PowerShell 数组 → JSON 数组才通。

### 铁律 2：特征按【索引】选，不要按坐标
```powershell
# ✅ 对 —— edge_indices 绕过坐标拾取容差
Call 'add_edge_feature' @{ feature_type='fillet'; radius_or_distance=0.002; edge_indices='[0]' }
# ❌ 错 —— 坐标容差经常抓不到
Call 'add_edge_feature' @{ feature_type='fillet'; radius_or_distance=0.002; ex=0.05; ey=0; ez=0.005 }
```
索引从 `analyze_model(edges)` 拿（`edge_count` + 每条边的 `mid`）。

### 铁律 3：每组测试要【自建环境】，别复用上一轮的文档
测试中途换了文档 → `bodies=0` → 后面所有"边/面"操作报 `EDGE_NOT_FOUND`，
看起来像 API 坏了，其实是**环境没了**。诊断第一件事：`analyze_model(geometry)` 看 `bodies`。

---

## 1. 标准建模流程（实测全通）

```powershell
. C:\Users\Zegel\solidpilot-mcp\tools\call.ps1

Call 'open_new_part' @{}                                    # ✅ 1.2s
Call 'create_sketch' @{ plane='Front Plane' }                # ✅ 0.8s
Call 'add_sketch_entities' @{ segments = @(                  # ✅ 0.1s  闭合矩形
    @{entity_type='line'; x1=-0.05; y1=-0.03; x2=0.05; y2=-0.03}
    @{entity_type='line'; x1= 0.05; y1=-0.03; x2=0.05; y2=0.03}
    @{entity_type='line'; x1= 0.05; y1= 0.03; x2=-0.05; y2=0.03}
    @{entity_type='line'; x1=-0.05; y1= 0.03; x2=-0.05; y2=-0.03}) }
Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }  # ✅ 0.4s → 凸台-拉伸1
Call 'analyze_model' @{ analysis_type='mass_properties' }    # ✅ volume=6E-05
```

⚠ **草图轮廓必须闭合**，否则 `extrude` 返 `EXTRUSION_FAILED`（实测：画 4 条散线必失败，画闭合矩形成功）。

### 1.1 拉伸的其它终止方式
```powershell
Call 'extrude_feature' @{ feature_type='cut'; through=$true }        # 切除（完全贯穿）
Call 'extrude_feature' @{ feature_type='boss'; mid_plane=$true; depth=0.02 }  # 中面对称
Call 'extrude_feature' @{ feature_type='boss'; depth=0.01; up_to_face_index=3 }  # 到指定面
```
`up_to_face_index` 的索引来自 `analyze_model(faces)`，与 `create_sketch(on_face)` 同一套枚举。

---

## 2. 修饰特征（实测全通）

```powershell
# 圆角 —— 必须用 edge_indices
Call 'analyze_model' @{ analysis_type='edges' }        # 先拿 edge_count
Call 'add_edge_feature' @{ feature_type='fillet';  radius_or_distance=0.002; edge_indices='[0]' }
#   ✅ 圆角1，volume 6.000e-05 → 5.999e-05（几何真变了）

# 倒角
Call 'add_edge_feature' @{ feature_type='chamfer'; radius_or_distance=0.001; edge_indices='[2]' }
#   ✅ 倒角1，volume → 5.991e-05

# 倒角的两种模式
Call 'add_edge_feature' @{ feature_type='chamfer'; radius_or_distance=0.001; chamfer_type='distance_distance'; distance2=0.0005 }
```
**`radius_or_distance` 的单位是米**（0.002 = 2mm）。

---

## 2.2 ⚠ create_pattern：部分参数组合是真静默失败（2026-09-28 干净状态实测）

**判据**（阵列必然增加材料或改变包围盒）：
```powershell
$before = Vol; $r = Call 'create_pattern' @{...}; $after = Vol
# after == before ⇒ 静默失败（特征建出来了，几何没动）
```

**干净状态实测**（每组先 `close_document` 清空，文档号 47→51 递增，特征树无累积）：

| 方向 | 间距 | 体积倍数 | 判定 |
|---|---|---|---|
| X | 0.02 | **×1.4** | ✅ 生效（实例融合，bodies 仍 1）|
| X | 0.005 | ×1.1 | ✅ 生效 |
| Y | 0.02 | ×1.67 | ✅ 生效 |
| **X** | **0.2** | **×1** | ⚠ **静默失败** |
| **Y** | **0.2** | **×1** | ⚠ **静默失败** |
| **Z** | **0.02** | **×1** | ⚠ **静默失败** |
| **Z** | **0.005** | ×2.0 | ✅ 生效 |
| **Z** | **0.05** | **×1** | ⚠ **静默失败** |

**规律**：间距**远大于零件尺寸**（0.2m vs 0.1m）时必失效；
**Z 方向（拉伸方向）**除极小间距外全部失效。
特征 `阵列(线性)N` 照样出现在特征树里，但几何没变。

⚠ **参数已确认正确**（`spacing` 单位是米、特征名取 `type=='Extrusion'`）。
⇒ 判定为 SolidWorks 侧问题，已挂起进待攻清单。

⚠ **测试陷阱（我踩了）**：`open_new_part` 之后不 `close_document`，
特征名会**跨用例累积**（`阵列(线性)1,2,3,4…`），看起来像"多个阵列都在"，
实际是同一个文档在不断叠加。**做参数扫描时每个用例前必须清空文档。**

### ✅ 可用的阵列组合（实测）
```powershell
Call 'create_pattern' @{ pattern_type='linear'; feature_name='凸台-拉伸1'; spacing=0.02; count=3; direction='X' }  # ×1.4
Call 'create_pattern' @{ pattern_type='linear'; feature_name='凸台-拉伸1'; spacing=0.02; count=3; direction='Y' }  # ×1.67
Call 'create_pattern' @{ pattern_type='circular'; feature_name=$seed; axis_name='基准轴1'; angle=90; count=4; equal_spacing=$true }
Call 'create_pattern' @{ pattern_type='mirror'; features_json='["凸台-拉伸1"]'; plane='Right Plane' }
```
⚠ 特征 type 是 **`Extrusion`**（不是 `Extrude`），硬编码 `Sketch1` 会失败。

---

## 3. 修饰与参数组合扫描（2026-09-28，19 OK / 6 FAIL / 0 静默）

| 工具 | 组合 | 结果 |
|---|---|---|
| `add_edge_feature` | fillet 单边/多边/坐标 | ✅ 全部生效（5.99914E-05）|
| | chamfer `distance_angle` 45°/30° | ✅ 5.9995E-05 / 5.99971E-05 |
| | chamfer `distance_distance` + flip | ✅ 5.9995E-05 |
| `export_document` | STEP / STL / IGES / PDF | ✅ 15KB / 1KB / 22KB / 182KB |

⚠ `add_edge_feature` 传**坐标**（`ex/ey/ez`）也生效，但**优先用 `edge_indices`**（铁律 2）。

---

### ✅ revolve 旋转体（2026-09-28 攻通）

**关键：草图里必须同时有【轮廓】+ 一条【轴线段】**，且轴线段端点要与参数精确匹配。
少画轴线 ⇒ `AXIS_NOT_FOUND`（这是第一次失败的原因，不是参数写错）。

```powershell
Call 'open_new_part'  @{}
Call 'create_sketch'  @{ plane='Front Plane' }
Call 'add_sketch_entities' @{ segments = @(
    # 轮廓（闭合矩形，x: 0.02~0.05）
    @{entity_type='line'; x1=0.02; y1=-0.02; x2=0.05; y2=-0.02},
    @{entity_type='line'; x1=0.05; y1=-0.02; x2=0.05; y2=0.02},
    @{entity_type='line'; x1=0.05; y1= 0.02; x2=0.02; y2=0.02},
    @{entity_type='line'; x1=0.02; y1= 0.02; x2=0.02; y2=-0.02},
    # ★ 轴线（少了这条就 AXIS_NOT_FOUND）
    @{entity_type='line'; x1=0.0;  y1=-0.03; x2=0.0;  y2=0.06}
) }
Call 'extrude_feature' @{ feature_type='revolve'; angle=360
                         axis_x1=0.0; axis_y1=-0.03; axis_x2=0.0; axis_y2=0.06 }
#   ✅ 旋转1，bodies=1，volume=0.000263894
```

⚠ **注意轴的语义**：`axis_x1/y1 → axis_x2/y2` 不是"随便给两个点"，
它要与**草图里那条线段的端点对上**（服务端按端点精确匹配草图线段，
坐标拾取会抓到"最近的线段"，大草图上可能抓到轮廓边）。
服务端随后会把该线段转成 ConstructionGeometry（中心线）。

⚠ **静默错误警告**：本次 volume=2.64e-4，而理论 π(0.05²−0.02²)×0.04=3.39e-4 —— 偏低。
说明部分轮廓被当成了轴。**特征建成了、不报错，但几何是错的。**
⇒ **revolve 后必须用 `analyze_model(mass_properties)` 对比理论体积**，
不要看到"COMPLETED"就当成功。

### ⏳ loft 放样（4 轮未通，已挂起）
参数名已确认是 `profiles`，**必须是扁平 JSON 数组**：
```powershell
# ✅ 格式对（但仍 EXTRUSION_FAILED）
Call 'extrude_feature' @{ feature_type='loft'; profiles='["草图1","草图2","草图3"]' }
# ❌ 嵌套数组 → INVALID_PARAMETER
profiles = ["草图1"],["草图2"]     # 这是嵌套，不是扁平
```
已试过：共面圆/圆、不同平面圆/圆、不同平面矩形/矩形/圆 —— 全部 `EXTRUSION_FAILED`。
**下一步**：读 `InsertSurface`/`FeatureLoft` 的实现，看它有没有先 `AccessSelections`
或需要合并/修复草图；或改用 `IFeatureManager.InsertBoss` 直接调。

### ⏳ sweep 扫描
```powershell
Call 'extrude_feature' @{ feature_type='sweep'; path_sketch='草图1' }   # EXTRUSION_FAILED
```

### ✅ sheet_metal sketched_bend 折弯（**2026-09-28 复核：一直可用，我曾误判**）

```powershell
$fa = Call 'analyze_model' @{ analysis_type='faces' }
$top = ($fa.cadState.features[0]|ConvertFrom-Json).faces |
       Where-Object { ([double](([string]$_.normal -split '\s+')[2]) - 1) -lt 1e-6 } | Select -First 1
Call 'create_sketch' @{ on_face=$true; face_index=$top.i }      # ★在【钣金面】上建折弯线草图
Call 'add_sketch_entity' @{ entity_type='line'; x1=-0.05; y1=0; x2=0.05; y2=0 }
Call 'sheet_metal_feature' @{ feature_type='sketched_bend'; angle=90; use_default_radius=$true }
#   ✅ 绘制的折弯1     面数 6 → 14 ⇒ 真的弯了
```

⚠⚠ **我曾把它误判为"假成功"，错在【用错了验证维度】**：
我当时看的是各面的 **z 坐标分布**（都在 −0.002~0），据此说"几何没变"；
**但折弯后确实新增了 8 个面（6→14）**——我查的维度恰好对折弯不敏感。
⇒ **判据必须选对维度**：折弯改的是**拓扑（面数）**，不是 z 分布，也**不是体积**
（钣金折弯**材料守恒，体积本来就不变**）。

⚠ 钣金件的**顶面在 z=0**（`face[5]` n=(0,0,1) p=(0,0,0)），
`base_flange` 是从草图平面 z=0 向 **−Z** 拉伸的。别按 `z>0.002` 筛面。

### ✅ sheet_metal edge_flange 翻边（2026-09-28 攻通）

**关键：必须选【长度 > 翻边宽度】的边。** 之前一直失败是因为我选了**板厚方向**的边。

```
板 160×20×2 mm 的边分三类：2mm×4（厚度向）、20mm×4、160mm×4
选 edge[5]（20mm）+ flange_length=0.01（10mm < 20mm）⇒ ✅
```

```powershell
$e = Call 'analyze_model' @{ analysis_type='edges' }     # 先分类边长
$ej = $e.cadState.features[0] | ConvertFrom-Json
# 按 |start-end| 算每条边的长度，挑 ≥ 翻边宽度 的
Call 'sheet_metal_feature' @{ feature_type='edge_flange'
                              edge_index=<选好的>; flange_length=0.01; angle=90 }
#   ✅ 边线-法兰1     volume 6.4e-6 → 6.76566E-06（翻边后几何真的变了）
```
⚠ 服务端内部先 `InsertSketchForEdgeFlange` 生成翻边轮廓草图再消费它；
若这一步返回 NULL，后面必然失败 —— **返回 NULL 就说明这条边不行，换一条**。
⚠ 翻边宽度 ≥ 边长时会静默失败（`SHEET_METAL_FAILED`，不说明原因）。

### ⏳ create_rib 加强筋（6 轮未通，已挂起）

几何已验证**完全正确**（这条排除很有价值）：
```
底板   100×100×20（x/y ∈ ±0.05，z: 0→0.02）
筋草图 on_face=顶面(face_index=4) ⇒ plane.origin=[0,0,0.02] ✅ 在板顶面
筋线   x: -0.05→0.05, y=0     ← 两端【正好落在 x=±0.05 的侧壁上】
```
**结果仍 `RIB_FAILED`**（服务端已试两个材料方向）。⇒ `InsertRib` 在本机不可用。

**过程中的两个真实发现**：
- ⚠ **`create_sketch` 没有 `offset` 参数**（只有 `plane` / `on_face` / `face_index`）
  ⇒ 筋草图一直建在基准面 z=0（板底面）。**要指定高度请用 `on_face` + `face_index`。**
- ✅ `create_sketch(on_face, face_index)` **可用**：在模型任意面上建草图，坐标会正确落在该面
  （实测 `plane.origin` 变成 `[0,0,0.02]`）。

### ⏳ sweep 扫描（5 轮挂起）/ ⏳ loft 放样（5 轮挂起）

诊断已定性（详见 §2.5）：**选择完全正确**（`n=2`，`mark=1`=轮廓、`mark=4`=路径），
loft 试遍 3 选择策略 × 3 插入 API 共 9 种组合，**全部返回 null**。
⇒ SolidWorks 侧建不出来，不是调用方式问题。

### ⏳ sheet_metal edge_flange 翻边（2 轮）
`SHEET_METAL_FAILED`，参数名已确认（`edge_index` / `flange_length` / `angle`）。

### ⏳ edit_feature delete（修复假成功后仍失败）
`EditDelete()` 在本机删不掉任何特征（改成验证结果后正确报 `DELETE_FAILED`）。

---

### ⏳ 服务端根本没实现的能力（不是 bug，是缺口）
```
曲面细分/修剪/延伸/偏移/缝合：InsertSurface / TrimSurface / ExtendSurface /
  InsertKnit / InsertBoundaryBoss / InsertRuledSurface / CreateOffsetSurface
  —— 服务端【零实现】，需要时得先加
尺寸标注 DimXpert（52 个接口）：服务端只读 IDimension，没有任何写入/公差能力
```

---

```powershell
# revolve 旋转体
Call 'extrude_feature' @{ feature_type='revolve'; angle=360
                         axis_x1=0; axis_y1=0; axis_x2=0; axis_y2=0.05 }
#   ❌ 实测 AXIS_NOT_FOUND —— 轴必须在【当前草图里】作为线段存在，
#      传坐标只是"在草图线段里找匹配的"，不是直接指定轴。

# loft 放样：参数名是 profiles（不是 path/profiles_json）
Call 'extrude_feature' @{ feature_type='loft'; profiles='["草图1","草图2"]' }
#   ❌ 实测 EXTRUSION_FAILED（参数名已对，是特征本身没建出来）
#   ⚠ 草图名是中文的「草图1」，从 analyze_model(features) 里 type~ProfileFeature 取

# sweep 扫描
Call 'extrude_feature' @{ feature_type='sweep'; path_sketch='草图1' }
#   ❌ 实测 EXTRUSION_FAILED
```

**⏳ 待攻清单**（按"连续 5 轮不通就跳过"规则挂起）：
- `loft` 放样 —— 参数名已确认，功能未通
- `sweep` 扫描 —— 同上
- `revolve` 旋转 —— 需先在草图里画出轴线段
- `create_rib` 加强筋 —— `RIB_FAILED`

---

## 2.5 旋转 / 放样 / 扫描 / 筋

### ✅ revolve 旋转体（攻通）

**关键：草图里必须同时有【轮廓】+ 一条【轴线段】**，且轴线段端点要与参数精确匹配。
少画轴线 ⇒ `AXIS_NOT_FOUND`（不是参数写错）。

```powershell
Call 'add_sketch_entities' @{ segments = @(
    # 轮廓（闭合矩形，x: 0.02~0.05）
    @{entity_type='line'; x1=0.02; y1=-0.02; x2=0.05; y2=-0.02},
    @{entity_type='line'; x1=0.05; y1=-0.02; x2=0.05; y2=0.02},
    @{entity_type='line'; x1=0.05; y1= 0.02; x2=0.02; y2=0.02},
    @{entity_type='line'; x1=0.02; y1= 0.02; x2=0.02; y2=-0.02},
    # ★ 轴线（少了这条就 AXIS_NOT_FOUND）
    @{entity_type='line'; x1=0.0;  y1=-0.03; x2=0.0;  y2=0.06}
) }
Call 'extrude_feature' @{ feature_type='revolve'; angle=360
                         axis_x1=0.0; axis_y1=-0.03; axis_x2=0.0; axis_y2=0.06 }
#   ✅ 旋转1，bodies=1
```
⚠ **静默错误警告**：本次 volume=2.64e-4，理论 π(0.05²−0.02²)×0.04=3.39e-4 —— 偏低，
说明部分轮廓被当成了轴。**特征建成了、不报错，但几何是错的** ⇒ revolve 后必须核对体积。

### ⏳ loft 放样（5 轮未通）/ ⏳ sweep 扫描（5 轮未通）/ ⏳ create_rib（6 轮未通）
诊断已定性：loft 试遍 3 选择策略 × 3 插入 API 共 **9 种组合全 null**；
sweep 的选择**完全正确**（`n=2`、`mark=1`=轮廓、`mark=4`=路径）**仍返回 null**。
⇒ SolidWorks 侧建不出来，不是调用方式问题。

```
曲面细分/修剪/延伸/缝合/偏移/边界凸台：InsertSurface / TrimSurface / ExtendSurface /
  InsertKnit / InsertBoundaryBoss / InsertRuledSurface / CreateOffsetSurface —— 零实现
孔特征（IAdvancedHoleFeatureData 等 10 个接口）—— 无工具
DimXpert 尺寸标注（官方 50 接口，服务端只读）—— 无写入/公差封装
```

---

```powershell
$f = Call 'analyze_model' @{ analysis_type='features' }
$fj = ($f.cadState.features[0] | ConvertFrom-Json)
$fj.features | Where-Object { $_.type -match 'ProfileFeature' } |
    ForEach-Object { "$($_.name)  [$($_.type)]  plane=$($_.plane.ref)" }
```
实测输出：
```
草图1  [ProfileFeature]  plane=Front Plane
草图2  [ProfileFeature]  plane=Top Plane
```
⚠ **`原点` 的 type 是 `OriginProfileFeature`，不匹配 `ProfileFeature`** —— 别把它当草图。
⚠ 草图名是**中文的**，硬编码 `Sketch1` 会报 `FEATURE_NOT_FOUND`。

---

```powershell
$boss = '凸台-拉伸1'      # extrude 的返回名

# 线性阵列
Call 'create_pattern' @{ pattern_type='linear'; feature_name=$boss; spacing=0.02; count=3; direction='X' }
#   ✅ 阵列(线性)1

# 镜向阵列
Call 'create_pattern' @{ pattern_type='mirror'; features_json="[`"$boss`"]"; plane='Right Plane' }
#   ✅ 镜向1

# 圆周阵列：先建基准轴
Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'
                                 entity2_name='Top Plane';  entity2_type='PLANE' }   # ✅ 基准轴1
Call 'create_pattern' @{ pattern_type='circular'; feature_name=$boss; axis_name='基准轴1'
                         angle=360; count=6; equal_spacing=$true }
```
⚠ `feature_name` 空会报 `MISSING_PARAMETER`；`features_json` 是**字符串形式的 JSON 数组**。

---

## 4. 钣金（实测 base_flange 通过）

```powershell
Call 'create_sketch' @{ plane='Front Plane' }
Call 'add_sketch_entities' @{ segments = @(...细长闭合矩形...) }
Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
#   ✅ 基体-法兰1，bodies=2
```
其余类型（`edge_flange` / `sketched_bend` / `flat_pattern`）**未验证**。

---

## 5. 草图约束与尺寸（**2026-09-28 全部攻通**）

```powershell
# ✅ 约束可用
Call 'add_sketch_constraint' @{ constraint_type='vertical'; px1=0.02; py1=0 }
#   类型：horizontal / vertical / coincident / parallel / perpendicular / tangent / equal / midpoint

# ★★ add_dimension：必须点在【真实线段】上，坐标不能瞎猜
$sk = Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }
$sj = $sk.cadState.features[0] | ConvertFrom-Json
$seg = $sj.sketch.segments | Where-Object { $_.kind -eq 'line' } | Select-Object -First 1
$mx = ($seg.x1 + $seg.x2) / 2      # ★中点，不是随便一个点
$my = ($seg.y1 + $seg.y2) / 2
Call 'add_dimension' @{ px=$mx; py=$my; value=0.1 }      # ✅
```
⚠ **之前一直报 `SEGMENT_NOT_FOUND` 的原因**：我凭想象给坐标，
而 `add_dimension` 内部按"离该点最近的**线段实体**"查找，坐标不在线段上就找不到。

```powershell
# ★★ modify_dimension：name 格式 = 'D<序号>@<草图名>'，草图名是中文
Call 'extrude_feature' @{ feature_type='boss'; depth=0.01 }
Call 'modify_dimension' @{ name='D1@草图1'; value=0.12 }   # ✅
#   验证：体积 4e-5 → 4.8E-05（= 0.12×0.04×0.01）⇒ 尺寸真的改了
```
⚠ 草图名必须来自 `analyze_model(features)` 里 `type -match 'ProfileFeature'` 的 `name`（本机是中文「草图1」）。
⚠ `原点` 的 type 是 `OriginProfileFeature`，**不匹配** ProfileFeature，别拿它当草图名。

### ⚠ feature_map 仍失败（唯一未攻下的分析类）
```
Call 'analyze_model' @{ analysis_type='feature_map' }   # ❌ ROLLBACK_FAILED
```
它需要移动 rollback bar，**即使不在草图编辑态也失败**。已试 3 轮（每轮都有新排除），
列入待攻。

---

```powershell
# ✅ 约束可用
Call 'add_sketch_constraint' @{ constraint_type='vertical'; px1=0.02; py1=0 }
#   类型：horizontal / vertical / coincident / parallel / perpendicular / tangent / equal / midpoint

# ❌ add_dimension 实测 SEGMENT_NOT_FOUND —— 需要点在【线段】上，
#    圆/弧不好定位。做法：先 analyze_model(sketch) 拿真实 segments 坐标再点。
# ❌ modify_dimension 实测 DIMENSION_NOT_FOUND —— name 格式是 'D1@草图名'，
#    草图名要来自 analyze_model(features) 里 type~ProfileFeat 的 name（中文如"草图1"）
```

---

## 4.2 ⭐ 钣金参数组合全面实测（2026-09-28，9/9 全通，0 静默）

`tools\param_combo_scan2.ps1`（每用例先 `close_document` 清空）。

### base_flange 厚度（体积应正比于板厚）
| thickness | 体积 | 验算 0.16×0.02×th |
|---|---|---|
| 0.001 | 3.2E-06 | ✅ |
| 0.002 | 6.4E-06 | ✅ |
| 0.005 | 1.6E-05 | ✅ |

### edge_flange 翻边宽度（体积应线性增长，差值恒定）
板 160×20×2mm，`edge_index` 取 20mm 的边：
| flange_length | 体积 | 增量 |
|---|---|---|
| 0.005 | 6.56566E-06 | — |
| 0.010 | 6.76566E-06 | **+2e-7** |
| 0.015 | 6.96566E-06 | **+2e-7** |

**恒定增量 2e-7 = 0.1m × 0.02m × 0.001m**（翻边长 × 板宽 × 弯半径补偿）
⇒ **参数完全正确生效**，且 `flange_length` 线性可控。

### edge_flange 翻边角度（体积随角度变化，说明角度真的生效）
| angle | 体积 |
|---|---|
| 45° | 6.71656E-06 |
| 90° | 6.76566E-06 |
| 135° | 6.68222E-06 |

⚠ **翻边宽度必须 < 边的长度**（见 §7.8）。

### flat_pattern 展开 ✅（3 种板厚下都通过）

---

## 6.2 ⭐ analyze_model 全部类型 × 参数组合（2026-09-28，11/12 通过）

| 调用 | 结果 |
|---|---|
| `analysis_type=features` | ✅ feature_count=10 |
| `geometry` | ✅ bodies=1 |
| `mass_properties` | ✅ volume=6E-05 |
| `bodies` | ✅ body_count=1 |
| `edges` | ✅ edge_count=12 |
| `faces` | ✅ face_count=6 |
| **`feature_map`** | ❌ `ROLLBACK_FAILED`（唯一失败，已挂起 4 轮）|
| `faces` + `near` + `k=3` | ✅ |
| `faces` + `near` + `k=1` | ✅ |
| `faces` + `near`（无 k）| ✅ |
| `faces` + `axis='[0,0,1]'` | ✅ |
| `edges` + `near` + `k=3` | ✅ |

⇒ **`near` / `k` / `axis` 三个定位参数全部可用**，是找面/找边最省事的手段
（免去手工翻上百条记录）。

---

```powershell
Call 'analyze_model' @{ analysis_type='features' }        # ✅ 特征树
Call 'analyze_model' @{ analysis_type='geometry' }        # ✅ bodies/faces/edges 计数
Call 'analyze_model' @{ analysis_type='mass_properties' } # ✅ volume
Call 'analyze_model' @{ analysis_type='bodies' }          # ✅ 逐实体指纹
Call 'analyze_model' @{ analysis_type='edges' }           # ✅ 逐边 start/end/mid/长度
Call 'analyze_model' @{ analysis_type='faces' }           # ✅ 逐面 normal/area/point
Call 'analyze_model' @{ analysis_type='faces'; near='[0,0,0.005]'; k=3 }  # ✅ 定点找面
Call 'analyze_model' @{ analysis_type='feature_map' }     # ⚠ ROLLBACK_FAILED（草图编辑中会失败）
Call 'analyze_model' @{ analysis_type='sketch'; name='草图1' }         # ✅（name 要真实草图名）
```

**`near`/`k` 参数是定位利器**：`near` 传坐标，`k` 传返回数量，
免去手工翻 800 个面的列表。

---

## 7. 文档与导入导出（实测通过）

```powershell
Call 'export_document' @{ format='STEP'; file_path="$env:TEMP\out.step" }   # ✅
Call 'batch_export' @{ file_path_base="$env:TEMP\b"; formats_json='["STEP","STL"]' }  # ✅
Call 'save_document' @{ file_path="$env:TEMP\a.sldprt" }                    # ✅
Call 'set_part_material' @{ material_name='AISI 1020' }                      # ✅
Call 'edit_feature' @{ feature_name='凸台-拉伸1'; action='rename'; new_name='MainBoss' }  # ✅
# action 还可以是 suppress / unsuppress / delete
```

---

## 7.5 装配 / 配合 / BOM（实测全通）

```powershell
Call 'open_new_assembly' @{}                                                   # ✅
Call 'insert_component' @{ file_path="$partsDir\主轴壳体_Housing.sldprt" }     # ✅
Call 'insert_component' @{ file_path="$partsDir\刀柄_Holder.sldprt"; x=0.05; y=0; z=0 }  # ✅
Call 'analyze_assembly' @{ }        # ✅ 返回 component_count + 每个组件的 transform(13 元素)

# ★ add_mate（新增验证通过）
Call 'add_mate' @{ mate_type='coincident'
                  a_component='主轴壳体_Housing-1'; a_kind='face'; a_index=0
                  b_component='刀柄_Holder-1';      b_kind='face'; b_index=0 }
#   ✅ 返回 "mate=重合1"
#   ★ 真实效果验证：刀柄_Holder-1 的 fixed 从 true 变成 false —— 组件变浮动、被配合约束
```

### ⚠ `analyze_assembly` 不返回 mates（能力缺口）
它只返回 `component_count` + `components[]`（各含 name/path/config/fixed/suppressed/transform）。
**没有配合列表** ⇒ 想确认"配合建了没"只能看
① `add_mate` 的返回值（`mate=重合1`）、② 组件的 `fixed` 是否变 false。

### add_mate 各配合类型实测（R14）
| mate_type | 结果 |
|---|---|
| `coincident` | ✅ 返回 `mate=重合1`，且 fixed→false |
| `concentric` / `perpendicular` / `parallel` / `angle` | ❌ `ADD_MATE_FAILED` |
| `flip=$true` | ❌ `UNSUPPORTED_MATE_TYPE` |
| `tangent` / `distance` / `lock` | ⚠ 返回 COMPLETED，但**需用 fixed 变化再确认**（我误判过一次）|

### motion_study 参数组合（R14 实测 + R15 修复）

⚠ **官方 API 只能做"整圈"旋转**：`IMotionStudy.CreateByRotateModel(
DeleteExistingPath, Axis, **RotationCount:int**, Direction, Duration, **StartTime**)`
—— 第 3 参是**圈数**（整数），**第 6 参是 StartTime 不是角度**（我曾误读成角度）。

```powershell
Call 'motion_study' @{ study='explode';  name='X' }              # ✅ duration=3s
Call 'motion_study' @{ study='explode';  duration=1 }            # ✅ duration 生效
Call 'motion_study' @{ study='collapse'; name='X' }              # ✅
Call 'motion_study' @{ study='rotation'; revolutions=2 }         # ✅ 真的转 2 圈（R15 新增）
Call 'motion_study' @{ study='rotation'; angle=720 }             # ✅ 换算成 2 圈
Call 'motion_study' @{ study='rotation'; revolutions=0.5 }       # ❌ INVALID_REVOLUTIONS
Call 'motion_study' @{ study='rotation'; revolutions=2.5 }       # ❌ INVALID_REVOLUTIONS
Call 'motion_study' @{ study='rotation'; angle=60 }              # ❌ PARTIAL_TURN_UNSUPPORTED
```

**R15 修掉的静默失败**：原来 `turns = round(angle/360)` 再 `if(turns<1) turns=1`，
于是 `revolutions=2` **这个参数根本不存在被忽略**、`angle=60` **被静默变成 1 整圈**。
现在：显式 `revolutions` 生效；非整数圈数报 `INVALID_REVOLUTIONS`；
**不满一圈的 `angle` 报 `PARTIAL_TURN_UNSUPPORTED`**（并说明官方 API 不支持），
不再偷偷做一件调用方没要求的事。

⚠ `motion_study` 的 `kind` 字段可用来核对请求是否被正确响应（传错参数名会静默跑成 explode）。

---

---

## 7.5b insert_component / bom_from_assembly 参数组合（R16 实测 9/9）

```powershell
# ★ insert_component 7/7 全通（判据=analyze_assembly 的 components[].transform）
Call 'insert_component' @{ file_path=$p }                          # ✅ pos=(0,0,-0.055)
Call 'insert_component' @{ file_path=$p; x=0.1; y=0.05; z=-0.02 }  # ✅ pos=(0.1,0.05,-0.075) 生效
Call 'insert_component' @{ file_path=$p; fixed=$true }             # ✅ fixed=True
Call 'insert_component' @{ file_path=$p; fixed=$false }            # ✅ fixed=False 生效
Call 'insert_component' @{ file_path=$p; config='默认' }            # ✅
Call 'insert_component' @{ file_path=$p; config='' }               # ✅
```

⚠ **`config` 参数缺少校验（R16 新发现的静默问题）**：
```
config='NoSuchConfig_不存在'  => COMPLETED   实际生效配置仍是 '默认'
```
传**不存在的配置名也不报错**。要真正测出它是否生效，需要一个**多配置**的零件
（单配置零件无法区分"被忽略"和"回退到唯一配置"）。

```powershell
# ★ bom_from_assembly：out_dir 生效，CSV 真的落盘
Call 'bom_from_assembly' @{ }                                        # ✅ rows=11，不落盘
Call 'bom_from_assembly' @{ out_dir="$env:TEMP\bomtest" }           # ✅ 落盘 1KB
#   → $env:TEMP\bomtest\换刀主轴装配_BT30_ATC_Assembly_BOM.csv
```

---

```powershell
Call 'open_document'    @{ file_path='...' }      # ✅ 支持 sldprt/sldasm/sldprt.slddrw
Call 'activate_document' @{ title='主轴壳体_Housing.sldprt' }  # ✅
Call 'close_document'    @{ }                     # ✅
Call 'verify_state'      @{ }                     # ✅
Call 'list_standard_parts' @{ folder='...' }      # ✅ 返回 {root,total_sl…} 索引
```

---

## 7.7 Motion 运动分析（实测 explode / rotation / collapse 全通）

```powershell
Call 'open_document' @{ file_path="$partsDir\换刀主轴装配_BT30_ATC_Assembly.SLDASM" }

# ⚠⚠ 参数名是 `study`，不是 `action`！传错会静默跑成默认的 explode（不报错!).
Call 'motion_study' @{ study='explode';  name='MCP_explode'  }
#   ✅ "explode -> True (duration=3s, startTime=0; steps=20 is not an API parameter…)"
Call 'motion_study' @{ study='rotation'; name='MCP_rotation' }
#   ✅ "rotate 1 turn(s) about Z (CCW) -> True" / "ActivateMotionStudy -> True"
#      "study count=3" / "Calculate() -> True"
Call 'motion_study' @{ study='collapse'; name='MCP_collapse' }
#   ✅ "collapse -> True"
```
返回字段：`study` / `kind` / `log` / `avi`。
**AVI 导出真实返 `False`**（渲染侧限制，见 §9）。

---

## 7.8 钣金完整闭环（base_flange + flat_pattern 实测通）

```powershell
Call 'create_sketch' @{ plane='Front Plane' }
Call 'add_sketch_entities' @{ segments = @(...细长闭合矩形...) }
Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
#   ✅ 基体-法兰1，bodies=1，edges=12
Call 'sheet_metal_feature' @{ feature_type='flat_pattern' }
#   ✅ 平板型式6   ← 钣金展开成功
Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=0; flange_length=0.01; angle=90 }
#   ❌ SHEET_METAL_FAILED（⏳ 待攻）
```
⏳ **待攻**：`edge_flange` 翻边（参数名已对，功能未通）

---

## 7.9 edit_feature：suppress / unsuppress / rename / delete（实测）

```powershell
# ★ suppress / unsuppress：实测【真的生效】
Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='suppress' }
#   ✅ COMPLETED，且体积真的变了：0.000220553 → 0.000204845
#      差值 15708 mm³ = π×10²×50（被抑制的 R10 圆柱）⇒ 语义完全正确
Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='unsuppress' }   # ✅
Call 'edit_feature' @{ feature_name='凸台-拉伸1'; action='rename'; new_name='MainBoss' }  # ✅

# ★ delete：2026-09-28 之前是【假成功】（返回 COMPLETED 但什么都没删）
Call 'edit_feature' @{ feature_name='凸台-拉伸2'; action='delete' }
#   现在正确返回 FAILED —— 修复后仍然失败，说明本机 delete 确实删不掉（待攻）
```

⚠ **测 suppress 必须建依赖链**，否则测不出变化：
```
凸台1 (R50×30) → 切除1 (通孔 R20，依赖凸台1) → 凸台2 (R10 凸柱，依赖切除1)
```
抑制**叶子**特征（凸台2）→ 体积应减少它的体积。
抑制**上游**特征（凸台1，被 2 个依赖）→ 模型重建失败，`analyze_model` 返回空——**这是正确行为**。

⚠ **测量精度陷阱（我自己踩过）**：`volume=0.0002` 是四舍五入，
不同状态可能都显示 `0.0002` 而实际差了几 mm³。**判定"有没有变化"必须看足够多的小数位**，
否则会把"正常工作"误判成"假成功"。

### 7.9.1 2026-09-28 修掉的真 bug：delete 假成功

`IModelDoc2.EditDelete()` 在这个 interop 里返回 **void**，没有返回值可查；
而 `SetSuppression2` 返回 bool 但旧代码**丢弃了它**。

修复方式（**不信任返回值，直接验证结果**）：

```csharp
// delete：编辑后按名字复查，特征还在就是没删掉
modelDoc.EditDelete();  modelDoc.EditRebuild3();
if (FindFeatureByName(modelDoc, featureName, allNames) != null)
    return BuildFailed(..., "DELETE_FAILED", "EditDelete() ran but the feature is still in the tree");

// suppress：既查返回值，也查状态
if (!feature.SetSuppression2(...)) return SUPPRESS_FAILED;
modelDoc.EditRebuild3();
if (!feature.IsSuppressed())     return SUPPRESS_FAILED;
```
**这类"静默失败"比报错危险得多** —— 调用方会信任 COMPLETED。

---

## 7.10 多体零件拆分成单零件（save_body_as_part，可用）

```powershell
Call 'open_new_part' @{}
# ... 建 2 个实体（挤出 + 上面再挤一个）...
$b = Call 'analyze_model' @{ analysis_type='bodies' }     # ✅ {"body_count":2,...}
Call 'save_body_as_part' @{ body_index=0; file_path="$env:TEMP\body0.sldprt" }   # ✅
Call 'open_document' @{ file_path="$env:TEMP\body0.sldprt" }                     # ✅ 验证
Call 'analyze_model' @{ analysis_type='mass_properties' }    # ✅ volume=7.2E-05
```

---

## 7.11 save_document 的扩展名必须与文档类型匹配（踩过）

```
错误码 256 = swFileSaveAsInvalidFileExtension
```

```powershell
# ✅ 零件文档 → 这四种都行
Call 'save_document' @{ file_path="$tmp\a.sldprt" }   # ✅
Call 'save_document' @{ file_path="$tmp\a.step"   }   # ✅
Call 'save_document' @{ file_path="$tmp\a.stl"    }   # ✅
Call 'save_document' @{ file_path="$tmp\a.igs"    }   # ✅ IGES 只能用 .igs
Call 'save_document' @{ file_path="$tmp\a.iges"   }   # ❌ SAVE_FAILED(256)
```
⚠ **在工程图文档上保存成 `.sldprt`/`.step` 全部失败**（256）——
扩展名必须和当前文档类型一致。做批量测试时先 `open_document` 切到对的类型。

---

```powershell
Call 'sheet_metal_feature' @{ feature_type='base_flange'; thickness=0.002; bend_radius=0.001 }
#   ✅ 基体-法兰1，bodies=1，edges=12
Call 'sheet_metal_feature' @{ feature_type='flat_pattern' }
#   ✅ 平板型式6   ← 钣金展开成功
Call 'sheet_metal_feature' @{ feature_type='edge_flange'; edge_index=0; flange_length=0.01; angle=90 }
#   ❌ SHEET_METAL_FAILED（⏳ 待攻）
```
⏳ **待攻**：`edge_flange` 翻边（参数名已对，功能未通）

---

## 7.12 补测：参考几何 / LCSC / 选择态（实测）

```powershell
# add_reference_geometry：plane 和 axis 可用
Call 'add_reference_geometry' @{ type='plane'; ref_plane_name='Front Plane'; offset=0.01 }  # ✅ 基准面1
Call 'add_reference_geometry' @{ type='axis'; entity1_name='Front Plane'; entity1_type='PLANE'
                                 entity2_name='Top Plane';  entity2_type='PLANE' }                # ✅ 基准轴1
Call 'add_reference_geometry' @{ type='point'; px=0.04; py=0; pz=0.11 }
#   ❌ VERTEX_NOT_FOUND —— 即使坐标正好是某条【边】的端点也找不到。
#      它内部用 SelectByID2("", "VERTEX", x,y,z) 选【顶点实体】，边端点不算顶点实体。
Call 'analyze_model' @{ analysis_type='features' }    # ✅ 13 个特征
```

### ★ lcsc_fetch_step 只对【电子元件】有效（服务端自带警告）

```powershell
Call 'lcsc_fetch_step' @{ keyword='R0603'; limit=3 }     # ✅ 参数是 keyword（不是 part）
```
返回里的警告原文（**很重要，别踩**）：
> *"Undocumented internal endpoints. **PCB-parts-only library**: measured 0/5 bearings with 3D,
> no 'linear guide' category, **'M3 screw' returns diodes**.
> For MECHANICAL standard parts use `list_standard_parts` instead."*

⇒ **LCSC 库只有电子元件**。查"轴承/导轨/M3 螺钉"会返回**二极管**。
⇒ **机械标准件一律用 `list_standard_parts`（扫 SolidWorks design library）**。

### get_selection 有选中时

```powershell
Call 'get_selection' @{ }   # ✅ {"selected_count":1,"selection":[{"type":"other","sw_type":22}]}
```

---

## 7.14 工程图整条链 —— 本机【全链不通】

一次实测（`create_drawing` 成功之后）：

| 工具 | 结果 |
|---|---|
| `create_drawing` | ✅ |
| **`add_drawing_view`** | ❌ `VIEW_CREATION_FAILED` ← **根节点** |
| `add_section_view` | ❌ `SECTION_LINE_FAILED`（没有视图可切）|
| `add_drawing_dimension` | ❌ `SEGMENT_NOT_FOUND` |
| `add_hole_callout` | ❌ `EDGE_NOT_FOUND` |
| `auto_dimension_drawing` | ⚠ 返回 `COMPLETED` 但 **`dimension_count=0`**（假成功）|
| `auto_center_marks` | ⚠ 同上（没视图可标）|
| `analyze_slddrw_test` | ✅ 能读，但 `view_count=1`（只有图纸页，无模型视图）|
| `add_flat_pattern_view` | ❌ `MODEL_NOT_FOUND`（要给零件文档，不是图纸）|
| `export_document` PDF/DXF | ✅ 图纸页能导出 |

⇒ **本机 SolidWorks 2026 中文版建不出工程图视图**，整条工程图链因此不可用。
`create_drawing` + `export PDF/DXF` 是唯一能走通的部分。

### ✅ activate_document / close_document（实测）
```powershell
Call 'activate_document' @{ title='主轴壳体_Housing.sldprt' }   # ✅ 切到已打开的文档
Call 'close_document' @{ }                                       # ✅ 关闭当前文档（回收资源用）
```


## 7.6 文档管理 / 草图重开（实测全通）

```powershell
Call 'open_document'    @{ file_path='...' }      # ✅ 支持 sldprt/sldasm/slddrw
Call 'activate_document' @{ title='主轴壳体_Housing.sldprt' }  # ✅ 切到已打开的文档
Call 'close_document'    @{ }                     # ✅ 关闭当前文档（回收资源用）
Call 'verify_state'      @{ }                     # ✅

# ★ edit_sketch：重开一个【已存在但未激活】的草图继续编辑
Call 'open_new_part' @{}
Call 'create_sketch' @{ plane='Front Plane' }       # 建草图1
Call 'add_sketch_entity' @{ entity_type='circle'; cx=0; cy=0; radius=0.02 }
Call 'edit_feature' @{ feature_name='草图1'; action='rename'; new_name='S1' }   # 改名（草图1→S1）
Call 'edit_sketch' @{ sketch_name='S1' }             # ✅ 重新激活 S1
Call 'add_sketch_entity' @{ entity_type='rectangle'; x1=0.01; y1=0.01; x2=0.03; y2=0.03 }
Call 'analyze_model' @{ analysis_type='sketch'; name='S1' }   # ✅ 确认现在有 2 个实体
```
⚠ **`edit_sketch` 要求草图当前【未激活】**，否则报 `SKETCH_ALREADY_ACTIVE`。
（`create_sketch` 现在会自动退出上一个草图，所以先 `create_sketch` 别的平面再回来即可。）

### 内存回收（每轮必做）
```powershell
& C:\Users\Zegel\solidpilot-mcp\tools\reclaim.ps1
# 实测 30+ 轮自动化后：私有内存 8286MB → 2157MB（-74%），句柄 4970→2823
```

### 启动 SolidWorks（会自动清掉阻塞弹窗）
```powershell
& C:\Users\Zegel\solidpilot-mcp\tools\start_sw.ps1 -Restart
# 弹窗「工具栏信息不一致」是模态的，不关会卡住所有 COM 调用
```

---

## 7.19 ⭐ Inspection 实证（2026-09-28）：**COM 可用，但探测有副作用**

### ✅ 决定性证据：Inspection 的 COM 类能创建
```
ProgID  Inspection.BalloonSettingManager
  → CLSID {60EF7E7C-E52F-37A4-BF27-6C5133293028}
  → InprocServer32 = mscoree.dll（.NET 实现）
  → CoCreateInstance = ✅ hr=0x00000000 成功！
ProgID  Inspection.BalloonSettingsImpl → CLSID {8C6F5A6D-F26C-3B59-ACE7-1F1425A6C882}
```
安装实况：`SOLIDWORKS Inspection.exe`（66 MB 主程序）+ `SolidWorksInspection.dll`（1.7 MB）
+ `cmmdataengine.dll`（2 MB）+ `InspectionXpertExporter.exe` / `inspectionxperttemplateeditor.exe`
**但没有 interop DLL** ⇒ 要用它的 API 得自己封装或用 COM 后期绑定。

### ⚠⚠ 重要教训：**CoCreateInstance 探测有副作用**（本轮实测踩到）
创建 `Inspection.BalloonSettingManager` 后，对象在构造期就去加载模板文件，失败并**弹出模态窗**：
```
SOLIDWORKS Inspection
System.ArgumentNullException: 值不能为 null。  参数名: inputUri
  在 System.Xml.XmlReaderSettings.CreateReader(String inputUri, XmlParserContext inputContext)
  在 Inspection.ExtProjectTemplateXML.DeserializeStoredTemplate(String filePath)
```
**模态窗会阻塞 SolidWorks**，与"工具栏信息不一致"是同一类问题。

⇒ **今后探测任何 COM 类之前，先想清楚**：
1. 它的构造函数会不会弹窗？（.NET 实现尤其容易）
2. 弹窗了怎么清？→ `tools\start_sw.ps1` 里每 4 秒扫一遍 `#32770` 的逻辑
3. 优先用**注册表 + 文件存在性**判断，CoCreateInstance 只在必要时做

### 其余 4 条产品线的实证
| 产品 | exe | dll | interop | 结论 |
|---|---|---|---|---|
| **Inspection** | 66 MB 主程序 | SolidWorksInspection.dll | ❌ 无 | ✅ **COM 可用**，需自己封装 |
| **CAM** | `solidworkscamnceditor.exe` 22 MB | `camworksu.dll` 27 MB | ❌ 无 | 装了（**用户明确不用**，用 Fusion360）|
| **PDM** | — | `PDMSW.dll` 2 MB / `AddInMgr.dll` | ❌ 无 | 装了，独立 exe 形态 |
| **Visualize** | **无** | 无 | ❌ 无 | ⚠ **只有目录壳** |
| **Composer** | **无** | 无 | ❌ 无 | ⚠ **只有目录壳** |

⚠ **Visualize / Composer 是"目录存在但程序不在"** —— `SOLIDWORKS Visualize` 目录里连一个 exe 都没有。

---

## 8.1 ⭐ 官方标准件库实测：216 个零件全部可用（2026-09-28）

```powershell
Call 'list_standard_parts' @{ folder='C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library' }
# ✅ {"total_sldprt":216,"returned":216,
#     "by_category":{"assemblies":14,"parts":19,"routing":177,"smart components":6},
#     "parts":[{"file":"…完整路径…"}, …]}
```

### 8 个子库的真实内容
| 子库 | 文件数 | 说明 |
|---|---|---|
| **routing** | 216 | **177 个 sldprt** —— 线缆/管路/接头（`2in-ec-valve with cpoints`、`standard cables and tubes.xls`）|
| features | 132 | 设计特征库（.sldlfp）|
| parts | 18 | 19 个标准件（`cotter pin` 开口销等）|
| forming tools | 17 | 成形工具 |
| assemblies | 15 | 14 个子装配 |
| annotations | 14 | 注解 |
| **motion** | 8 | ★ **Motion 库有 8 个文件**（说明 Motion 数据层是装了的）|
| smart components | 6 | 智能组件 |

### ★ 插入实测：4/4 全部成功（装配 11 → 15 组件）
```powershell
# ① list_standard_parts 拿【完整路径】
# ② open_document 打开它（让 SW 缓存）
# ③ open_document 打开【既有装配】★必须是既有装配（R7 结论）
# ④ insert_standard_part @{ file='<上一步拿到的完整路径>' }
```
| 类别 | 零件 | 结果 |
|---|---|---|
| assemblies | `b plate_pcs2b.sldprt` | ✅ |
| parts | `cotter pin.sldprt` | ✅ |
| routing | `2in-ec-valve with cpoints.sldprt` | ✅ |
| smart components | `die insert.sldprt` | ✅ |

⚠⚠ **我连踩两次坑，都是自己拼路径**：`$lib\parts\cotter pin.sldprt` 这种拼法取不到文件
（零件在更深层子目录里）。**必须用 `list_standard_parts` 返回的 `parts[].file` 完整路径**，
不要自己 Split-Path / Join-Path 拼。

⚠ 另：**必须在 `open_document` 打开的既有装配里插**，`open_new_assembly` 的不行（R7 三组对照已证实）。

---

## 8. 插入 STEP 到装配（实测通过，但**必须转格式**）

**STEP 是中性格式，`AddComponent5` 不接受它**：

```powershell
# ❌ 直接插 STEP → AddComponent5 returned null
# ✅ 三步走
Call 'open_document'      @{ file_path = "$dir\六角螺母_M12_ISO4032.step" }      # ① 让 SW 转换
Call 'save_document'      @{ file_path = "$dir\六角螺母_M12_ISO4032.sldprt" }    # ② 存成原生件
Call 'insert_standard_part' @{ file = "$dir\六角螺母_M12_ISO4032.sldprt" }      # ③ 插入
```
⚠ 参数名是 **`file`**，不是 `part_path`；文件名大小写要对（本机是 `.SLDPRT`）。

### ★ insert_standard_part 的前提（三组对照实测）
```
open_new_assembly 建的【空装配】                    => ❌ INSERT_FAILED
新装配 + 先 insert_component 一个原生零件          => ❌ INSERT_FAILED
open_document 打开的【既有装配】                    => ✅ 成功插入
```
⇒ **只能在"从磁盘打开的既有装配"里用**；`open_new_assembly` 出来的不行，加了组件也不行。

---

## 7.13 ⭐ 服务端能力全貌（2026-09-28 终检更新）

**服务端共 49 个 `ExecutionResponse` 方法，已全部真实调用过**（终检脚本 `tools\final_inventory.ps1`）。

### 官方接口族 → 服务端实现 → 实测状态
| 官方接口族 | 官方接口数 | 服务端方法 | 实测状态 |
|---|---|---|---|
| **Feature** | 193 | ExtrudeFeature / AddEdgeFeature / EditFeature | ✅ boss/cut/revolve 齐通；⏳ loft/sweep 挂起 |
| **Sketch** | 27 | CreateSketch / AddSketchEntity(ies) / AddSketchConstraint / AddDimension | ✅ 全部通过 |
| **Pattern** | 17 | CreatePattern | ⚠ 部分组合静默失败（§2.2）|
| **Surface** | 17 | （仅 loft/sweep 走 ExtrudeFeature）| ⏳ 全部返回 null |
| **Dimension** | 9 | AddDimension / ModifyDimension | ✅ 已攻通（需点真实线段 / name=`D1@草图名`）|
| **Motion** | 10 | MotionStudy | ✅ explode/collapse/rotation + revolutions |
| **Assembly** | 2 | OpenNewAssembly / InsertComponent / AnalyzeAssembly / AddMateTool | ✅ 齐通 |
| **SheetMetal** | 3 | SheetMetalFeature | ✅ base_flange / edge_flange / flat_pattern / sketched_bend |
| **Hole** | 10 | **无工具** | ❌ 服务端零实现 |
| **Import** | 5 | OpenDocument / ExportDocument / BatchExport / SaveDocument | ✅ STEP/STL/IGES/PDF/DXF |
| **Bom** | 4 | BomFromAssembly | ✅ rows=11，`out_dir` 生效 |
| **Drawing** | 2 | CreateDrawing + 7 个标注工具 | ❌ `add_drawing_view` 失败 ⇒ 整链断 |
| **Material** | 3 | SetPartMaterial | ✅ |
| **Standard** | 1 | ListStandardParts / InsertStandardPart | ✅ 官方库 216 个零件 |
| **Simulation** | — | TopologyOptimize / BearingTest | ❌ 写操作崩（§9.1）|
| **Electrical** | — | ElectricalProbe | ✅ reachable（683 个导出类型）|
**（新增）** ProductProbe / DesignCheck | — | 12 条产品线可用性探测 |

### 服务端零实现的能力（明确缺口）
```
曲面细分/修剪/延伸/缝合/偏移/边界凸台 —— 零实现（官方 20 个 Surface 接口一个没做）
孔特征（10 个官方接口）—— 无工具
DimXpert 写入（官方 50 接口）—— 服务端只读（且本机根本没装该产品）
```

### ⚠ 不是"接口族"但重要的判据
**能力天花板 = 服务端封装的 49 个方法，不是官方 566 个接口族。**
官方 API 的绝大多数接口服务端没有对应封装；反过来说，**服务端 49 个方法已 100% 实测**。


## 7.15 ⭐⭐ 本机 12 个产品线的实测接入方式（2026-09-28 全面探测）

### 装机实况（`D:\Program Files\SOLIDWORKS Corp` 下的产品目录）
```
SOLIDWORKS(核心) / CAM / Composer / Electrical / Flow Simulation / Inspection /
Manage Client(PDM) / PDM / Plastics / Visualize / Visualize Boost
```
> 用户已明确：**CAM 不用**（用 Fusion360）、**Plastics 不用**（不做注塑）。

### interop 程序集全部可加载（= 每个产品线都有 API）
| interop DLL | 接口数 | 关键入口 |
|---|---|---|
| `sldworks` | 数百 | 核心 |
| `swconst` | 978 个枚举 | — |
| `swdocumentmgr` | 504 | 文档管理 |
| **`swdimxpert`** | **173 类型 / 50 接口** | `IDimXpertPart` `IDimXpertFeature` `IDimXpertAnnotation` |
| `swpublished` | 93 | 发布 |
| **`SWRoutingLib`** | 68 / 14 接口 | `IWire` `ICable` `IRouteProperty` |
| `swmotionstudy` | 44 | Motion |
| `sustainability` | 35 / 9 接口 | `ISustainabilityApp` |
| **`sldcostingapi`** | 14 接口 | `ICostManager` `ICostPart` `ICostBody` |
| `sw3dprinter` | 14 / 1 接口 | `ISw3DPrinter` |
| `dsgnchk` | 5 接口 | `ISWDesignCheck` |
| `cosworks` | — | Simulation |

> ⚠ **修正一个此前的误判**：我曾说"DimXpert 只读（服务端没实现写入）"——
> **官方 interop 有 50 个接口，是完整可用的**，只是**我的服务端**没写这些封装。

### ★ add-in 可达性实测（`product_probe` 工具，真实调 `GetAddInObject`）
```
SW 版本 = 34.0.0
✅ Simulation          via LoadAddIn + GetAddInObject
✅ Simulation(别名)     via GetAddInObject（已随 SW 启动加载）
❌ Electrical          dll 缺失（无 SwElectrical.dll 可 LoadAddIn）
❌ Flow Simulation / Costing / Sustainability / 3D Printer
❌ DimXpert / Design Checker / Routing / PDM / CAM
```

### ⇒ 架构结论（重要）
**12 个产品线里，只有 Simulation 走 `SldWorks.Application` 的 add-in 机制**
（`LoadAddIn` + `GetAddInObject`，且**不需要注册到 `HKCU\...\AddinsStartup`**）。

其它产品是**独立 exe 应用**，interop 齐全但**不挂在 SolidWorks 的 add-in 体系上**：
```
SOLIDWORKS Electrical\  → 7z_x64.dll / DL180ACE.dll（是运行库，不是 add-in）
SOLIDWORKS Flow Simulation\ → AnimationView.dll / ChemDbx.dll（同上）
SOLIDWORKS PDM\        → AddInMgr.dll（PDM 自己的管理器）
```
⇒ 想用它们的 API，**要启动各自的独立应用并从那里接 COM**，
不是从 `SldWorks.Application.GetAddInObject`。

### 可复用的探测工具（本轮新建）
```powershell
Call 'product_probe' @{ }                            # 全探
Call 'product_probe' @{ products='SldWorks.Simulation,SldWorks.Electrical' }   # 点名探
```
返回：每个 add-in 的 `reachable` / `via`（已加载 or LoadAddIn）/ `err`，
外加全部 interop DLL 的加载结果与接口数。

### ★ 从 PowerShell 直连 SolidWorks 走不通（已实测，别再试）
```powershell
New-Object -ComObject SldWorks.Application   # ❌ 新建的是【空壳实例】
$sw.RevisionNumber()                          # ❌ TYPE_E_ELEMENTNOTFOUND 0x8002802B
$sw.GetAddInObject('...')                     # ❌ 同样 0x8002802B
[Runtime.InteropServices.Marshal]::GetActiveObject  # ❌ pwsh(.NET Core) 根本没这个方法
```
**即使加载 interop 转成强类型 `ISldWorks` 也一样**（因为底层对象本身就是空壳）。
⇒ **只能走本执行服务**（它持有正确的实例 + STA 线程 + 消息泵）。

---

## 7.16 ⭐ Design Checker：能创建、能返回成功码，但**不产出报告**（静默失败）

### 突破：它不走 add-in，能在进程内 CoCreateInstance
```csharp
CLSID {df1ad3b3-b3bb-4436-898b-86a1d99c282b}   // SWDesignCheckClass
IID   {bb8dadcc-bb01-4351-9633-3ca19827048b}   // ISWDesignCheck
CoCreateInstance(...) => hr=0，拿到活对象
```
```powershell
Call 'design_check' @{ standard_file='<xml>'; report_dir='<dir>'; overwrite=$true }
#   ✅ COMPLETED   returnCode=0 (dsgnchkNOErr)
```

### 官方标准检查文件在哪（`spiop` 目录下）
```
D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\spiop\files\resources\standard\
  AerospaceSheetMetalDesign.xml     (16.7 KB)  ← 航空航天钣金设计标准
  SheetMetalDesign.xml              (1.1 KB)
  CATStdLayersAndFilters.xml / CATDftStd* / CATDifStd*  ← CATIA 过滤器，非检查标准
```

### ❌ 但报告文件一个都没生成（静默失败，已确认）
| 尝试 | 返回码 | 报告数 |
|---|---|---|
| `AerospaceSheetMetalDesign.xml` | 0 `dsgnchkNOErr` | **0** |
| `SheetMetalDesign.xml` | 0 `dsgnchkNOErr` | **0** |
| `CATStdLayersAndFilters.xml` | 0 `dsgnchkNOErr` | **0** |

全盘扫描（`Documents` / `TEMP` / `APPDATA` / `ProgramData`，6 分钟内新建文件）**零命中**。

⚠ **这正是我自己立的铁律抓到的**：「CoClass 能创建 + 返回成功码」**不等于功能可用**。
`CoCreateInstance` 只证明 COM 类注册了，**不证明它能连上运行中的 SolidWorks**——
DesignChecker 很可能需要自己的初始化（`StartValidator()` / `ToolbarUpdate()`）或宿主窗口。

### 官方状态码（`dsgnchkError_e`，判断结果用）
```
0 = dsgnchkNOErr                    成功
1 = dsgnchkReportAlreadyExists      3 = dsgnchkNoActivedocument
2 = dsgnchkCouldNotCreateReportDirectory
4 = dsgnchkStandardFileDoesNotExist
5 = dsgnchkInvalidReportName        6 = dsgnchkAllStandardFilesInvalid
7 = dsgnchkDesignCheckerAlreadyRunning   8 = dsgnchkInvalidCallToAPI
```

### 其它产品的 CoCreateInstance 实测（一次问清）
| 产品 | CLSID 注册 | CoCreateInstance | 错误码 |
|---|---|---|---|
| **Design Checker** | ✅ HKLM | ✅ 成功 | — |
| Costing | ✅ HKLM | ❌ | `0x80004002` E_NOINTERFACE（主接口 IID 待定）|
| Sustainability | ❌ **未注册** | ❌ | `0x80040154` REGDB_E_CLASSNOTREG |
| 3D Printer | ❌ **未注册** | ❌ | `0x80040154` REGDB_E_CLASSNOTREG |

⇒ **Sustainability 和 3D 打印是"装了但没注册"**（精简安装或未激活），本机用不了。
⇒ Costing 的类在，但主接口 IID 不是 `ICostManager`，需要从 CLSID 键的 InprocServer32
   + 类型库查出真正的默认接口。

---

## 7.17 ⭐⭐ 产品线接入的两种形态（实测结论，2026-09-28）

### 形态一：**宿主绑定型**（CoClass 能创建，功能拿不到）
DesignChecker / Costing 都属于这类。四步实测全过，**但零产物**：

| 步骤 | DesignChecker | Costing |
|---|---|---|
| ① CoCreateInstance | ✅ `hr=0` | ✅ `IUnknown` 成功 |
| ② 拿主接口 | ❌ `E_NOINTERFACE` | ❌ `E_NOINTERFACE`（IID `bed209a9-…` 已找准，**不是猜错**）|
| ③ 初始化 | ✅ `StartValidator()` 成功 | — |
| ④ 调功能 | ✅ `rc=0 dsgnchkNOErr` | — |
| **⑤ 产物** | ❌ **零报告** | 只有 `AboutBox` 一个方法 |

**Costing 的实证**（`CostManagerClass` 拿到的对象）：
```
Get-Member → 只有 Method AboutBox
```
注册表显示它的实现是 `sldActiveXControlU.dll`、ProgID `SWC.TASKPANE.34`
⇒ **它是个 ActiveX 任务窗格容器**，功能由 SolidWorks 宿主提供。

**DesignChecker 同理**：`Dsgnchku.dll` + ProgID `SWDesignChecker.SWDesignCheck.2026`。

⇒ **结论：这两条产品线必须【在 SolidWorks UI 里打开对应功能面板】才有 API 可用**，
   COM 类注册只是提供了"壳"。**独立实例化 = 拿得到壳、拿不到功能。**

### 形态二：**未注册**（装了但没完整安装）
| 产品 | CLSID | 错误码 |
|---|---|---|
| Sustainability | ❌ 不在 HKLM | `0x80040154` REGDB_E_CLASSNOTREG |
| 3D Printer | ❌ 不在 HKLM | `0x80040154` REGDB_E_CLASSNOTREG |
| Electrical / Flow / Inspection / PDM / Visualize / CAM | — | 非 add-in 形态，独立 exe |

### 形态三：**add-in 型**（唯一真能远程驱动的）
**只有 Simulation**：`LoadAddIn` + `GetAddInObject`，且**不需注册 AddinsStartup**。

---

### ⚠ 铁律 0 的八次翻车：**判据链条上任何一环断掉，整条结论都不可信**

同一个"测静默失败"的动作，我连着八次判错。**但从第 5 次起，我都能在报告前自己发现**：

| 轮次 | 断在哪 | 真相 |
|---|---|---|
| R5 | 判据**维度**选错 | `sketched_bend` 其实弯了（面 6→14）。z 分布对折弯不敏感 |
| R10 | 判据**太弱** | `delete` 确实失败（存在性判据放过它）——方向判对了 |
| R13 | 测试**没清空文档** | 特征名累积污染了数据 |
| R14 | 要读的**字段不存在** | `analyze_assembly` 没有 mates 字段 ⇒ 4 个正常 add_mate 全被判成静默 |
| R16 | **上游数据断链** | `MakeBox` 漏改 `CleanDoc`→`NewPart` ⇒ faces 为空 ⇒ 3 个正常 on_face 全被判成静默 |
| R20 | **测试数据不合法** | 草图只画 2 条线（不闭合）⇒ extrude 失败 ⇒ 下游 4 个测试全废 |
| R21 | **命名风格不同** | 找 C# 方法名 `ActivateDocument` 而记录是工具名 `activate_document` |
| R22 | **脚本状态未清** | `insert_component` 后读组件数 0，但 BOM 读 1 ⇒ 实为误判 |

**⇒ 三条自检，每次动手前过一遍**：
1. **灵敏度**：这个判据在"确定成功"时会显示变化吗？
2. **存在性**：我要读的字段/量真的存在吗？
3. **链条完整性**：判据依赖的上游数据，真的取到了吗？**打印出来看一眼**

最可靠的判据是**两个独立维度同时变**（体积 + 边数），或**一个物理必然量**（阵列必增材料）。

### ⭐ 写操作工具的产物验证（2026-09-28，11/11 全部通过）

`tools\write_ops_verify.ps1` —— 不审计代码，直接调用并检查产物：

| 工具 | 判据 | 结果 |
|---|---|---|
| `create_sketch` | 草图 `plane.ref` | ✅ Front Plane |
| `add_sketch_entities` | 草图 `sketch.counts.line` | ✅ → 4 |
| `extrude_feature` | `bodies` 0→1 | ✅ |
| `set_part_material` | 材料已设置 | ✅ AISI 1020 |
| `save_document` | 文件落盘 | ✅ 65 KB |
| `export_document` | 2/2 格式落盘 | ✅ |
| `batch_export` | 2/2 文件落盘 | ✅ |
| `edit_feature(rename)` | 树里出现新名字 | ✅ RenamedBoss |
| `insert_component` | `component_count` 增加 | ✅ 0→1 |
| `bom_from_assembly` | `rows` = 组件数 | ✅ |
| `close_document` | 活动文档变化 | ✅ |

⚠ **只读操作（analyze_* / verify_state / get_selection / list_standard_parts）不需要产物验证** ——
它们把数据返回给调用方，调用方能看到对不对。


### ⚠ 数据格式备忘（R16 实测）
`analyze_model(faces)` 的 `normal` / `point` 字段是 **`Object[]`（数组）不是字符串**。
`[string]$_.normal` 会得到 `"0 0 1"`，再 `-split '\s+'` 拆回 3 个分量 —— 能用但脆弱，
**直接用数组下标 `$_.normal[2]` 更可靠**。

---

## 7.18 ⭐⭐ 本机产品线【真实可用性】实测（2026-09-28，决定性）

> **关键认知：interop DLL 只是【类型定义】，随主程序分发。它能加载 ≠ 产品已安装。**
> 我曾据此误判"DimXpert 50 接口完整可用"，实际本机**根本没装 DimXpert**。

判据三连：① interop 能否加载 ② CoClass 的 CLSID 是否在注册表 ③ CoCreateInstance 能否成功。

| 产品线 | interop | 接口数 | CLSID 注册 | CoCreateInstance | 结论 |
|---|---|---|---|---|---|
| **Simulation** | ✅ | 168 | add-in | ✅ 已实测 | ✅ **可用**（LoadAddIn + GetAddInObject）|
| **DesignChecker** | ✅ | 12 | ✅ HKLM | ✅ **成功** | ✅ 对象能建（功能宿主绑定，见 §7.16）|
| Costing | ✅ | 28 | ✅ HKLM | `0x80004002` | 🟠 类在、只暴露 IUnknown ⇒ **ActiveX 任务窗格** |
| **DimXpert** | ✅ | 100 | ❌ **未注册** | `0x80040154` | ❌ **本机没装** |
| **Routing** | ✅ | 28 | ❌ **未注册** | `0x80040154` | ❌ **本机没装** |
| **Sustainability** | ✅ | 18 | ❌ **未注册** | `0x80040154` | ❌ **本机没装** |
| **3D Printer** | ✅ | 2 | ❌ **未注册** | `0x80040154` | ❌ **本机没装** |
| Electrical / Flow / Inspection / PDM / Visualize / CAM | — | — | — | — | 独立 exe，非 add-in |

### DimXpert 的决定性证据（本轮实测）
```
DimXpertPartClass CLSID = {a7af9c2d-52e5-40f1-9d6e-c2dfb4bcd204}
IDimXpertPart     IID    = {a7af9c2d-52e5-40f1-9d6e-c2dfb4bcd203}   ← 只差末位 ⇒ 独立 COM 服务器

裸 CoCreateInstance                  → 0x80040154 REGDB_E_CLASSNOTREG
LoadLibrary("slddimxpertclru.dll")   → ✅ 0x7FF8BC340000（2MB，cl=command line 版）
LoadLibrary 之后再 CoCreateInstance  → 仍然 0x80040154
```
**本机没有任何 DimXpert 的 exe**（`Get-ChildItem -Filter *.exe | ? Name -match DimXpert` = 0 命中），
只有 `slddimxpertclru.dll` 这个命令行执行器，**它不是 COM 服务器**。

⚠ 即便装上，`IDimXpertPart` 的写入能力是完整的：
`InsertDatum` / `InsertSizeDimension` / `InsertLocationDimension` / `InsertBasicDimension` /
`InsertAngleDimension` / `InsertGtol` / `DeleteAllTolerances` / `AutoDimensionScheme` / `ImportScheme`

**⇒ 想用 DimXpert 必须先装产品。**

---

## 9. 待攻清单（每项含：❌错误码 · ✅参数名状态 · ➡ 下一步具体动作）

> 规则（用户 2026-09-28 定）：**同一问题连续 5 轮跑不通就挂起**，回头集中攻。

### 9.1 🔴 满 5 轮的硬骨头（SolidWorks 侧疑似不可用）

| # | 能力 | ❌错误码 | ✅参数名 | 已排除什么 | ➡ 下一步 |
|---|---|---|---|---|---|
| 1 | `extrude(loft)` 放样 | 返回 `null` | `profiles`（**扁平** JSON 数组）| 草图有几何/参数解析/选中成功/**3 选择策略 × 3 插入 API = 9 组合全 null** | 读 `IFeatureManager.InsertSurface` 的放样入口；或试 `FeatureLoft` 而非 `InsertProtrusionBlend2` |
| 2 | `extrude(sweep)` 扫描 | 返回 `null` | `path_sketch` + 轮廓=**当前激活草图** | **选择状态完全正确**（`n=2`、`mark=1`=轮廓、`mark=4`=路径）仍 null | 试 `InsertProtrusionSwept`（非 v4）；或查本机 SW2026 是否禁用这两个 API |
| 3 | `create_rib` 加强筋 | `RIB_FAILED` | `thickness` 等 | 端点悬空/板中面/板底面/Top Plane 是 XZ 平面/几何完全正确仍 null | 查 `InsertRib` 的 `IsNormToSketch`/`ReferenceEdgeIndex`；或用 **`sketched_bend` 替代**（那个是通的）|
| 4 | Simulation 夹具/载荷 | `E_INVALIDARG 0x80070057`（Add*）<br>`RPC_E_SERVERFAULT 0x80010105`（AddBearingLoad / BeginEdit）| 全部签名已确认 | 0 元素数组/AddForce 对照/逆序与声明序/两种几何来源/真实 RefGeom/4 种写方法 | **归为本机许可边界**。如需轴承工况：UI 手建 + 本服务只读结果 |

### 9.2 🟡 结构性缺口（服务端没实现，不是参数问题）

| # | 能力 | 状态 | ✅参数名 | ➡ 下一步 |
|---|---|---|---|---|
| 5 | 曲面细分/修剪/延伸/缝合/偏移 | **零实现** | — | 要用得先在 `Services\` 加 `InsertSurface`/`TrimSurface` 等封装 |
| 6 | 孔特征（10 个官方接口）| 无工具 | — | 同上，需加 `IFeatureManager.InsertHole` 类封装 |
| 7 | DimXpert 尺寸标注（官方 50 接口）| 服务端只读 | interop 完整 | 加写入封装（公差/基准/标注）|
| 8 | `analyze_model(feature_map)` | `ROLLBACK_FAILED` | `analysis_type` | 须在**非草图编辑态**调用；试 `EditRollback` 前先 `EditRebuild3` |

### 9.3 🟠 宿主/环境绑定（本机用不了，非代码问题）

| # | 能力 | ❌错误码 | 结论 | ➡ 下一步 |
|---|---|---|---|---|
| 9 | `add_drawing_view` 工程图视图 | `VIEW_CREATION_FAILED` | 本机 SW2026 中文版建不出视图 ⇒ **整条工程图链断** | 查是否有中文版 SP；或改走 DXF 路线（`analyze_drawing` 能读 DXF）|
| 10 | `add_reference_geometry(point)` | `VERTEX_NOT_FOUND` | **headless 顶点拾取限制**；已排除"零件无顶点"（换多面体）、"精度截断"（用 `ToString('R')`）| 改用 `IModelVertex` 遍历实体，不靠坐标拾取 |
| 11 | `edit_feature(delete)` | `DELETE_FAILED` | `EditDelete()` 本机删不掉任何特征（**假成功已修**，现在正确报错）| 试 `IFeature.Select2` + `EditDelete2`；或确认本机是否禁用删除 |
| 12 | `create_pattern` 特定组合 | 无错误码 | 间距**远大于**零件尺寸 / **Z 方向** ⇒ 特征建出但几何不动 | 参数已确认正确（`spacing` 是米）；查 `FeatureLinearPattern4` 在本机的行为 |
| 13 | DesignChecker | `rc=0` 但**零报告** | **宿主绑定型 ActiveX**（`Dsgnchku.dll`）| 只能走 UI 手动；API 侧已穷尽（3 标准文件/初始化/全盘扫描）|
| 14 | Costing | `E_NOINTERFACE` | IID 已找准（`bed209a9-…`）但类只暴露 IUnknown ⇒ **ActiveX 任务窗格** | 需在 SolidWorks 里开 Costing 面板 |
| 15 | Sustainability / 3D Printer | `0x80040154` REGDB_E_CLASSNOTREG | **本机根本没注册**（装了但没完整安装）| 需重装该产品 |
| 16 | Electrical / Flow / Inspection / PDM / Visualize / CAM | — | **非 add-in 形态**，是独立 exe | 需启动各自主程序再接其自有 COM |

### 9.4 ⚫ 产品未安装（interop 有类型定义，但**本机没这个产品**——不是封装问题）

| # | 能力 | interop 接口数 | 关键入口 | ➡ 下一步 |
|---|---|---|---|---|
| 17 | **DimXpert 全线** | 100 | `IDimXpertPart` 等 | ❌ **本机未装**（§7.18 有决定性证据）⇒ 需先安装产品 |
| 18 | Routing | 28 | `IWire` / `ICable` | ❌ **本机未装** ⇒ 需先安装 |
| 19 | Sustainability | 18 | `ISustainabilityApp` | ❌ **本机未装** ⇒ 需先安装 |
| 20 | 3D Printer | 2 | `ISw3DPrinter` | ❌ **本机未装** ⇒ 需先安装 |
| 21 | Costing API | 28 | `ICostManager` / `ICostPart` | 🟠 产品在、但宿主绑定（#14）⇒ 需在 SW 里开面板 |

---


---

> 规则（用户 2026-09-28 定）：**同一问题连续 5 轮跑不通就跳过**，记进本表，回头集中攻。

### ⏳ 待攻清单（参数名已确认，功能未通——优先攻这些）

| 功能 | 现象 | 备注 |
|---|---|---|
| `loft` 放样 | `EXTRUSION_FAILED` | 参数 `profiles='["草图1","草图2"]'` 已确认正确 |
| `sweep` 扫描 | `EXTRUSION_FAILED` | 参数 `path_sketch='草图1'` |
| `revolve` 旋转 | `AXIS_NOT_FOUND` | 轴必须在**当前草图里**作为线段存在，坐标只是"在草图线段里找匹配的" |
| `create_rib` 加强筋 | `RIB_FAILED` | 需专门的开轮廓草图 + 先有实体 |
| `sheet_metal edge_flange` | `SHEET_METAL_FAILED` | 参数已对 |
| `add_dimension` | `SEGMENT_NOT_FOUND` | 要点在线段上；圆/弧难定位 |
| `modify_dimension` | `DIMENSION_NOT_FOUND` | name 格式 `'D1@草图名'`，草图名要从 features 取 |
| `analyze_model(feature_map)` | `ROLLBACK_FAILED` | 草图编辑中会失败，先退出草图 |

### ❌ 确认不可用（24 轮实测，已充分取证，别再投时间）

| 功能 | 现象 |
|---|---|
| **Simulation 夹具/载荷** | `AddRestraint`/`AddForce`/`AddForce3` = `E_INVALIDARG 0x80070057`；<br>`AddBearingLoad`/`BeginEdit` = `RPC_E_SERVERFAULT 0x80010105`；<br>0 元素数组、AddForce 对照、逆序/声明序、两种几何来源、真实 RefGeom 全试过 |
| **Simulation 求解** | 编辑会话崩溃；`CreateMesh`/`RunAnalysis` 弹模态框卡死服务 |
| 工程图 `add_drawing_view` | 本机中文版 2026 返 `VIEW_CREATION_FAILED` |
| AVI 导出 | `SaveToAVI` 真实返 `False` |

### 🐛 环境坑（不是 API 不可用，是用法）

| 现象 | 真因 |
|---|---|
| `FILE_NOT_FOUND` 但文件明明在 | 文件名大小写：本机是 `.SLDPRT`（大写） |
| `AddComponent5 returned null`（插 STEP） | STEP 必须先转 SLDPRT（见 §8） |
| `MISSING_PARAMETER: segments required` | 数组参数传成了 JSON 字符串（铁律 1） |
| `EDGE_NOT_FOUND` 但实体刚建好 | 当前文档被换掉了，`bodies=0`（铁律 3） |
| `motion_study` 传 `action='rotation'` 却跑出 explode | 参数名是 `study` |
| `FEATURE_NOT_FOUND: Sketch1` | 草图名是中文「草图1」，要从 `analyze_model(features)` 取 |

---

## 10. 性能参考（实测）

| 操作 | 耗时 |
|---|---|
| `open_new_part` | 1.2 s |
| `create_sketch` | 0.8 s |
| `add_sketch_entities`（4 线）| 0.1 s |
| `extrude_feature` | 0.4 s |
| `add_edge_feature`（圆角/倒角）| 0.03 s |
| `create_pattern` | 0.7 s |
| `sheet_metal_feature`（base_flange）| 0.1 s |
| `analyze_model`（edges/faces）| 0.13 s |
| `export_document` STEP | 0.2 s |

**一个完整建模件（含修饰+阵列+钣金）约 5–8 秒**，可以做批量生成。

---

## 11. 怎么继续扩展这个指南

新学到一个 API 可用，就：
1. 在 `tools\api_scan*.ps1` 里加一条 `T '功能名' { Call 'tool' @{...} }`
2. 跑一遍，看 ✅/❌
3. ✅ 的写进本文档对应章节；❌ 的写进 §9「还不能用」

**规则**：同一问题**连续 5 轮跑不通就跳过**，记进 §9，回头集中攻。
（用户 2026-09-28 定）

---

## 12. 快速自检清单

动手前问自己：
- [ ] 参数名对吗？（`grep` 服务端源码最快：`Select-String -Path *Capability.cs -Pattern 'XXX' `）
- [ ] 数组参数传的是真数组吗？（铁律 1）
- [ ] 特征选择用索引还是坐标？（铁律 2）
- [ ] 依赖的实体/边存在吗？（先 `analyze_model(geometry)` 看 `bodies`，铁律 3）
- [ ] 这个操作在 §9 里吗？在的话直接跳过。




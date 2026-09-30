# SolidWorks AI 建模操作手册

> **给 AI 读的操作手册**（不是给人读的）。
> 面向"通过 API / MCP 驱动 SolidWorks 建零件与装配体"的场景。
> 配套：[DSH-操作手册.md](DSH-操作手册.md)（MCP 接入与工具速查）、
> [swdoc.ps1](swdoc.ps1)（本机官方文档全文检索）
>
> 依据：**本机 SolidWorks 自带的完整离线 API 手册**（`D:\AI\SWhelp\`，29,650 页 / 243.6 MB）
> + 本机实测（2026-09-27）
> 日期：2026-09-27 ｜ 本机版本：SOLIDWORKS Design Premium 2026 SP0.0（`swVersion 34.0.0`）

---

## 0.0 先读这个：官方文档已经全在本机，别去网上爬

**SolidWorks 安装时自带完整离线 API 手册**（3 册 CHM）：

| 源文件（`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\`） | 大小 | 内容 |
|---|---|---|
| `sldworksapi.chm` | 26.5 MB | C#/.NET API 参考（11,579 页） |
| `swconst.chm` | 7.6 MB | **全部枚举常量**（1,353 页）——`swEndConditions_e`、`swStartConditions_e` 都在这 |
| `sldworksapivb6.chm` | 7.3 MB | VBA API 参考（16,718 页） |

**已解包到 `D:\AI\SWhelp\`：29,650 个文件 / 243.6 MB，可全文检索。**

> `help.solidworks.com` 与 `www.solidworks.com/support/resource-center` **都抓不动**
> （403 Access Denied / fetch failed），且页面 JS 渲染，爬下来是空壳。**别浪费时间爬网。**

### 检索工具

```powershell
C:\Users\Zegel\solidpilot-mcp\swdoc.ps1 -List                    # 三册概况
C:\Users\Zegel\solidpilot-mcp\swdoc.ps1 -Q 'component center'   # 全文关键词检索
C:\Users\Zegel\solidpilot-mcp\swdoc.ps1 -File 'FeatureCut4'     # 按页面名读全文（HTML→纯文本）
```

### 重新解包 CHM（换 SolidWorks 版本时）

```powershell
# 关键：输出目录必须【不存在】且路径不能带空格，否则 hh.exe -decompile 静默失败（返回 0 个文件）
Remove-Item $dst -Recurse -Force
Start-Process C:\Windows\hh.exe -ArgumentList @("-decompile", $dst, $chm) -Wait
```

> ⚠️ **7-Zip 25.01 已移除 CHM 解码器**（`7zr`/`7za` 均报 "Cannot open the file as archive"，
> 尽管文件头是合法 `ITSF`）。**只有 `hh.exe -decompile` 可用。**

---

## 0.1 心智模型：界面里看到的 ≠ API 参数

---

## 0. 心智模型：界面里看到的 ≠ API 参数

SolidWorks 界面上的"拉伸凸台/拉伸切除"对话框有十几个选项，但 API 里它们**不是同名参数**。
**把界面选项直接翻译成 API 参数，是 AI 建模最常见的错误来源。**

界面上一个"反向"按钮，API 里可能是 `Dir`、也可能是 `Flip`、还可能是 `Sd`——**三者完全不同**。

**唯一可靠的办法：读官方方法签名，逐个参数对照官方定义。** 别猜。

---

## 1. 三个必须先记住的陷阱

### 陷阱 1：方向是 `Dir`，不是 `Reverse`

`FeatureExtrusion3` / `FeatureCut4` 的**第 3 个参数**才是方向：

```vb
FeatureCut4(Sd, Flip, Dir, T1, T2, D1, D2, ...)
                 ▲     ▲    ▲
                 │     │    └── Dir: True = Direction 1 与默认方向相反  ← 真正的方向开关
                 │     └─────── Flip: True = 切 flip 侧轮廓【外】的材料
                 └───────────── Sd: True = 单端, False = 双端
```

| 参数 | 官方定义 | 不是什么 |
|---|---|---|
| `Sd` | True=单端切除，False=双端 | **不是方向** |
| `Flip` | True=切除轮廓**外侧**的材料 | **不是方向** |
| **`Dir`** | **True = 方向 1 与默认方向相反** | ✅ **这才是方向** |

> **实测（本机）**：MCP 的 `extrude_feature(reverse=true/false)` 对切除**完全无影响**——
> 同一圆柱切两次，`reverse` 取 True 和 False 体积一模一样。
> 因为该 `reverse` 映射的不是 `Dir`。**这个坑实测踩过，不要再踩。**

### 陷阱 2：切除边界靠 `T0` + `StartOffset`，不靠 `D1`

`D1` 只是**盲孔深度**。想让切除从某个位置起、到某处止，要用**起始条件**：

```vb
swStartConditions_e:
  swStartSketchPlane    = 0   从草图平面起
  swStartSurface        = 1   从指定面起
  swStartVertex         = 2   从指定顶点起
  swStartOffset         = 3   从草图平面偏移 StartOffset 起  ← 真正的边界控制
                           + FlipStartOffset: True = 反方向偏移
```

`T0=swStartOffset(3)` + `StartOffset=<米>` + `FlipStartOffset` 组合，
才能表达"从草图面往回 5mm 开始切"这类边界。

### 陷阱 3：草图关系不是自动的

`ISketchManager.CreateCornerRectangle` / `CreateCircle` 这类**高层构造函数会自动加关系**，
但用**原始坐标逐点建线段**（很多 AI 工具的做法）**一条关系都不会加**——
草图从"零关系、全部欠定义"开始，此时任何后续约束/尺寸都可能把几何推歪。

---

## 2. 草图关系完整词汇表

### 2.0 ⭐ 优先用"会自动加关系"的建图函数

**这是本节最重要的一条。** 高层构造函数**建出来就是带关系的**，
不要用 `CreateLine` 手拼再补关系——那正是本项目踩过的所有坑的根源。

| 函数 | 自动加的关系 |
|---|---|
| `CreateCornerRectangle(x1,y1,x2,y2)` | 4×coincident + 2×horizontal + 2×vertical **（共 8 个）** |
| `CreateCenterRectangle(cx,cy,w,h)` | 同上 + 对原点对称 |
| `Create3PointCornerRectangle` / `Create3PointCenterRectangle` | 同上 |
| `CreateCircle` / `CreateCircleByRadius` | 圆心自动与光标/原点推断重合 |
| `CreatePolygon(n, cx, cy, r, rot)` | n×coincident + n×equal + 角度 |
| **`MakeSketchChain(segCount, UseRelations)`** | **把已有线段串成链并补 coincident** ← 手工连线的正解 |
| `CreateSketchSlot` | 自动含两端圆弧 + tangent + 尺寸 |
| `AddAlongXDimension` / `AddAlongYDimension` / `AddAlongZDimension` | 直接加定位尺寸（省掉手工定位） |

> `MakeSketchChain(segCount, UseRelations)` 的存在意义就是：
> **可以先按坐标建线，再一次性把链连起来并自动上关系**，比重心点选相邻线段可靠得多。

### 2.0b 关系相关开关

| 属性/方法 | 用途 |
|---|---|
| `SketchManager.AutoInference` (True/False) | **开关自动推断**——先关掉再手工控制，避免系统乱加关系 |
| `SketchManager.InferenceMode` | 细粒度推断控制 |
| `SketchManager.AutoSolve` | 关掉自动求解，加完关系再统一求解（避免每加一个就抖一次） |
| `SketchRelationManager.GetAllowedRelations` | **先问 SolidWorks"这个选择上可以加哪些关系"**，别猜 |
| `SketchRelationManager.DeleteAllRelations` | 推歪了要重来时的清理 |

**推荐建图节奏**：
```
AutoInference = False          ' 先关自动推断
AutoSolve     = False          ' 再关自动求解
... 建几何 / MakeSketchChain ...
... 加 H/V / 加尺寸 ...
AutoSolve     = True           ' 最后统一求解
```

### 2.0c 选实体：按对象，不按坐标

**坐标拾取是"选不中"的根本原因。** 正解是拿实体对象直接选：

| 做法 | 说明 |
|---|---|
| `Sketch.GetSketchSegments` / `IEnumSketchSegments.Next` | 拿到每条线段的 `SketchSegment` 对象 |
| `SketchSegment.Select2/Select3/Select4(Append, ...)` | **选对象本身** |
| `SketchSegment.SelectByMark(mark)` | 按 mark 批量选 |
| `SketchSegment.SelectChain(Append)` | **选整条链**——画矩形时的正解 |
| `SketchSegment.GetRelations` / `GetRelationsCount` | 查这条线已经有哪些关系 |
| `SketchSegment.GetName` / `GetID` | 稳定标识 |

**`swSketchRelationEntityTypes_e`（关系目标类型）**：

```
SubSketch=1  Point=2  Line=3  Arc=4  Ellipse=5  Parabola=6  Spline=7
Hatch=8  Plane=10  Cylinder=11  Sphere=12  Dimension=14
```

> ⚠️ **选关系目标时用的类型是 `swSketchRelationEntityType_Point`（=2），
> 不是字符串 `"SKETCHPOINT"`**。两者在不同接口上不通用
> （`SelectByID2` 收字符串，`SketchRelationManager.AddRelation` 收枚举）。
> **混淆这两者是"关系加不上"的头号原因。**

### 2.1 关系名对照（`SketchAddConstraints` 字符串）

| 关系 | API 字符串 | 选择类型 |
|---|---|---|
| 重合 | `sgCOINCIDENT` | `swSketchRelationEntityType_Point`×2 |
| 水平 | `sgHORIZONTAL2D` | `swSketchRelationEntityType_Line` |
| 竖直 | `sgVERTICAL2D` | `swSketchRelationEntityType_Line` |
| 中点 | `sgATMIDDLE` | Point + Line |
| 共线 | `sgCOLINEAR` | Line×2 |
| 垂直 | `sgPERPENDICULAR` | Line×2 |
| 平行 | `sgPARALLEL` | Line×2 |
| 相切 | `sgTANGENT` | Line/Arc×2 |
| 等长 | `sgSAMECURVELENGTH` | Line/Arc×2 |
| 同心 | `sgCONCENTRIC` | Arc×2 |
| 共径 | `sgCORADIAL` | Arc×2 |
| 固定 | `sgFIXED` | 任意 | **慎用**（放弃参数化） |

**加法**：

```vb
swDoc.Extension.SelectByID2("Line1", "SKETCHSEGMENT", 0,0,0, True, 0, Nothing, swSelectOptionDefault)
swDoc.SketchAddConstraints("sgHORIZONTAL2D")
swDoc.ClearSelection2 True
```

`IModelDoc2.AddRelation(RelationType, Entity1, Entity2)` 是对象版，更稳。

---

## 3. 草图"完全定义"：自由度会计

一条线 4 个自由度；一个圆 3 个（cx, cy, r）。完全定义 = **自由度恰好为 0**。

**例：矩形（4 条线，16 DoF）**

| 动作 | 消掉 | 剩余 |
|---|---|---|
| 4 个端点自动重合（或手动 4 个 `sgCOINCIDENT`） | 8 | 8 |
| 2 个 `sgHORIZONTAL2D` + 2 个 `sgVERTICAL2D` | 4 | 4 |
| 宽尺寸 + 高尺寸 | 2 | 2 |
| 一个角点 `sgCOINCIDENT` 到 `Point1@Origin` | 2 | **0** ✅ |

**例：圆（3 DoF）**
- 圆心 `sgCOINCIDENT` 到原点 → 2
- 直径尺寸 → 1
- 合计 **0** ✅

**判据**：状态栏必须显示"草图已完全定义"，**欠定义数字哪怕只有 1 个就是没做完**。

### 3.1 一次性完全定义：官方有现成方法

`ISketchManager.FullyDefineSketch` —— 官方示例（Fully Define Underdefined Sketch）：

```vb
' 先用不同 mark 选中原点的水平/垂直基准
lMarkHorizontal = 2 : lMarkVertical = 4
swModelExtension.SelectByID2("Point1@Origin", "EXTSKETCHPOINT", 0,0,0, False, _
                             lMarkHorizontal Or lMarkVertical, Nothing, 0)
lStatus = swSketchManager.FullyDefineSketch( _
    True, True, _
    swSketchFullyDefineRelationType_Vertical Or swSketchFullyDefineRelationType_Horizontal, _
    True, 1, Nothing, 1, Nothing, 1, 1)
```

**优先用这个，而不是手写一长串关系**——它会自己补齐缺的、去掉冗余的。

### 3.2 建线顺序（AI 特有坑）

**必须"建一条线 → 立刻给它加 H/V → 再建下一条"**。

因为关系工具靠"离 (px,py) 最近的图元"选目标：
先批量画 12 条再回头批量加关系，在密集轮廓上会选错线
（**实测：6 条水平只成 3 条、6 条垂直 0 条全错**，相邻台阶径向只差 1 mm）。

---

## 4. 凸台 / 切除：完整参数表

```vb
FeatureExtrusion3(Sd, Flip, Dir, T1, T2, D1, D2, Dchk1, Dchk2, Ddir1, Ddir2,
                  Dang1, Dang2, OffsetReverse1, OffsetReverse2,
                  TranslateSurface1, TranslateSurface2, Merge,
                  UseFeatScope, UseAutoSelect, T0, StartOffset, FlipStartOffset)

FeatureCut4(Sd, Flip, Dir, T1, T2, D1, D2, Dchk1, Dchk2, Ddir1, Ddir2,
            Dang1, Dang2, OffsetReverse1, OffsetReverse2,
            TranslateSurface1, TranslateSurface2, NormalCut,
            UseFeatScope, UseAutoSelect, AssemblyFeatureScope,
            AutoSelectComponents, PropagateFeatureToParts,
            T0, StartOffset, FlipStartOffset, OptimizeGeometry)
```

| 参数 | 官方定义 |
|---|---|
| `Sd` | True=单端，False=双端 |
| `Flip` | True=切轮廓外侧材料 |
| **`Dir`** | **True=方向1 与默认相反（方向开关）** |
| `T1`/`T2` | 端条件，见下表 |
| `D1`/`D2` | 深度（米）；`T1=OffsetFromSurface` 时 D1 是偏移量 |
| `Dchk1/2` | True=允许拔模 |
| `Dang1/2` | 拔模角（度） |
| `OffsetReverse1/2` | True=向远离草图方向偏移 |
| `TranslateSurface1/2` | True=端面是参考面的平移（真偏置 vs 假偏置） |
| `Merge` | True=与已有实体合并（**多段堆叠必开**） |
| `NormalCut` | True=钣金法向切 |
| `T0`/`StartOffset`/`FlipStartOffset` | 起始条件，见 §1 陷阱 2 |

### 4.1 `swEndConditions_e` 完整枚举

| 成员 | 值 | 备注 |
|---|---|---|
| `swEndCondBlind` | 0 | 盲端，用 D1/D2 |
| `swEndCondThroughAll` | 1 | **单向通孔** |
| `swEndCondThroughNext` | 2 | 穿透下一个实体 |
| `swEndCondUpToVertex` | 3 | ⚠️ **官方标注 "Do not use"**，已被 UpToSelection 取代 |
| `swEndCondUpToSurface` | 4 | ⚠️ **官方标注 "Do not use"**，已被 UpToSelection 取代 |
| `swEndCondOffsetFromSurface` | 5 | 相对面偏移，D1 作偏移量 |
| `swEndCondMidPlane` | 6 | **对称，D1 是总宽**（不是单边） |
| `swEndCondUpToBody` | 7 | 到指定实体 |
| `swEndCondThroughAllBoth` | 9 | **双向通孔** |
| `swEndCondUpToSelection` | 10 | **切到指定选择面 ← 官方推荐** |
| `swEndCondUpToNext` | 11 | 到下一个面 |

### 4.2 表达"切到哪里"的三种正确做法

| 需求 | 正确参数组合 |
|---|---|
| 切穿整个实体 | `T1=swEndCondThroughAll(1)`，`D1` 随便给个非零值（官方示例给 0.01） |
| 从某个位置才开始切 | `T0=swStartOffset(3)` + `StartOffset` + `FlipStartOffset` |
| 切到某个面为止 | `T1=swEndCondUpToSelection(10)` + `SelectByID2(..., "FACE", ...)` |
| 双向对称切 | `Sd=False` 或 `T1=swEndCondThroughAllBoth(9)` |
| 中面对称拉伸 | `T1=swEndCondMidPlane(6)`，`D1` = **总宽** |

> **不要**用 `UpToSurface(4)` / `UpToVertex(3)`——官方已标 "Do not use"。

---

## 5. 选择集：名字与类型

`SelectByID2(Name, Type, X, Y, Z, Append, Mark, Callout, SelectOption)`：

| 目标 | Name | Type |
|---|---|---|
| 草图线段 | `"Line1"` | `"SKETCHSEGMENT"` |
| 草图圆心点 | `"Point2"` | `"SKETCHPOINT"` |
| **草图原点** | `"Point1@Origin"` | `"EXTSKETCHPOINT"` |
| 实体面 | `"Face<1>"` | `"FACE"` |
| 实体边 | `"Edge<1>"` | `"EDGE"` |
| 基准面 | `"Front Plane"` | `"PLANE"` |
| 尺寸 | `"D1@Boss-Extrude1@Part.Part"` | `"DIMENSION"` |

**Mark 位**（同一次选择里区分不同用途，官方示例：水平 2 / 垂直 4）：

```vb
lMarkHorizontal = 2 : lMarkVertical = 4
SelectByID2("Point1@Origin","EXTSKETCHPOINT",0,0,0,False, _
            lMarkHorizontal Or lMarkVertical, Nothing, 0)
```
> 官方注释：**同一个点不能被选两次配不同 mark**。

**索引 vs 坐标**：能用索引就别用坐标。坐标拾取在复杂件上"会成功但选错"。

---

## 6. 尺寸

- `add_dimension` 类接口在**圆**上给**直径**，在**线段**上给**长度**。
  ⚠️ **实测**：同一数值语义在两种图元上不同——圆给 `d` 正确，线给 `d` 会被当成**半径**处理，
  把轮廓撑大好几倍。**给线段尺寸时先想清楚你要的是长度还是直径。**
- 尺寸要**命名**（`D1`/`D2`…）。`modify_dimension` 靠**完整尺寸名**驱动：
  `name` 必须来自 `analyze_model(features)` 的原样输出，**自己拼一定错**。
- `modify_dimension` 的**角度用弧度**，其他工具的角度用度。

---

## 7. 验证闭环（不验证 = 没做完）

**每个特征后至少验一次**，`analyze_model(mass_properties)` 是最有效的单一判据：

```
理论体积 = 手算；实测体积 = analyze_model(mass_properties)
吻合 = 几何正确；不吻合 = 一定错了，别猜为什么，先查参数
```

实测有效率：
- 圆 boss + 圆 cut：**精确吻合**（碟簧 3.14523e-6 vs 理论 3.1453e-6）
- 矩形 boss（带 H/V 关系）+ 圆 cut：**偏差 50%**（切除没按预期走）
- 多段 boss 堆叠（各自偏置面）：**吻合到 0.9%**

> **堆叠要点**：多段实体用**各自的偏置基准面**分别长，别全画在同一张图上——
> 同一张图上多段会互相吞掉（台阶全被埋在最大那段里）。

---

## 8. 本机 MCP 工具的能力边界（实测，别重复踩）

工具：`mcp__solidworks__*`（底层 `SolidworksExecution.exe` + `dsh-mcp-client`）

### 8.1 可用 ✅

| 能力 | 实测 |
|---|---|
| 圆 boss / 圆 cut（单平面） | 精确 |
| 偏置基准面 + 单圆 + boss 堆叠 | 0.9% |
| 矩形：逐条 H/V + 尺寸 | 几何守住，体积精确 |
| `add_reference_geometry` 偏置面 | 可用（**面名在 `cadState.features[-1]`，不在 `result`**） |
| `analyze_model` / `analyze_assembly` / `insert_component` / 导出 | 可用 |

### 8.2 不可用 / 有缺陷 ❌

| 能力 | 实测表现 |
|---|---|
| **`extrude_feature(reverse=)` 控制方向** | **对切除完全无效**（True/False 体积相同）——不映射到 `Dir` |
| **`submit_feature_graph`（IR 路径）** | `400 Unknown tool`，这版执行层没编译降级器 |
| **`add_sketch_constraint` 在 Right Plane** | 任何取点都 `ENTITY_NOT_FOUND`（前视面/上视面正常） |
| **`add_sketch_constraint` 的点类关系**（coincident/midpoint，SKETCHPOINT） | `ENTITY_NOT_FOUND`，**永远选不到草图点** |
| **矩形 boss + 圆 cut** | 切除只吃掉部分料；`up_to_face_index` 也无效 |
| **同轴多次切除** | 后一次会污染前一次的结果 |
| **`add_drawing_view`** | `VIEW_CREATION_FAILED`（SW2026 中文版，官方已知问题） |
| **材质名** | `'1045'/'45'/'AISI 1045'/'碳钢'` 全 `MATERIAL_NOT_FOUND`（中文版要用中文名，见 DSH-操作手册 §7-2） |
| **IR 里的尺寸** | `schema://feature-graph` 的 `node_types` **没有 dimension 节点**，走 IR 无法自动标尺寸 |

### 8.3 因此的绕行方案

| 想要 | 做不到 | 绕行 |
|---|---|---|
| 控制切除方向 | 无 `Dir` 参数 | **把要切的料建成 boss 的一半**，或让切除方向自然落在有料的一侧 |
| 切到某个面 | `up_to_face_index` 无效 | 用偏置基准面定位草图 + 盲孔深度 |
| 草图完全定义（定位） | 点关系不可用 | **把定位交给基准面**（偏置量是尺寸），草图内只留 H/V + 尺寸 |
| 一次补齐所有关系 | 无 `FullyDefineSketch` | 逐条 H/V（安全）+ 尺寸；**绝不用 midpoint/equal**（会毁几何） |

---

## 9. 零件建模标准作业流程（SOP）

```
0. 读 analyze_model，确认当前状态（盲目建模 = 盲目出错）
1. open_new_part
2. 选基准面策略：
     单段          → 直接用 Front Plane
     多段/台阶     → 每段一个 add_reference_geometry 偏置面（面名取 cadState.features[-1]）
3. 画轮廓：
     圆   → add_sketch_entity(circle) + add_dimension(直径)
     直线 → add_sketch_entity(line) → 【立刻】add_sketch_constraint(H/V) → 下一条
4. add_dimension 标大小（圆=直径，线=长度）
5. extrude_feature，验证 COMPLETED
6. analyze_model(mass_properties) 与理论体积比对  ← 不吻合就地停，不要往下走
7. 重复 3–6 做下一段
8. save_document → export_document(STEP)
```

**红线**：
- 绝不在无关系草图上加 midpoint / equal / 点约束（会毁几何，实测）
- 绝不靠 `reverse` 控制切除方向（无效）
- 绝不跳过体积验证（尺寸对了不代表几何对了，反之亦然）

---

## 10. 装配

### 10.1 ⚠️ `AddComponent5` 的 x/y/z 是**零件中心**，不是原点

官方原文（`IAssemblyDoc.AddComponent5`）：

```
X | X coordinate of the component center
Y | Y coordinate of the component center
Z | Z coordinate of the component center
```

**这是装配体"位置全错"的头号原因。** 你想让零件的**原点**落到 `want`，
就得把它的**中心**放到：

```
中心 = want + (局部 lo + 局部 hi) / 2
```

**实测校验**（110mm 长的壳体，want=0）：传 0 → 回读 −55mm（中心归零，原点跑到 −55）；
传 0.055 → 回读 **0mm** ✅。差值正好是半长，和官方定义完全吻合。

| 我想要的 | 错的做法 | 对的做法 |
|---|---|---|
| 110mm 长的壳体底面落在 z=0 | `z=0` | `z=0.055` |
| 碟簧（厚 1.5）底面落在 z=50 | `z=50` | `z=50.75` |
| 300mm 长扳手端面落在 z=115 | `z=115` | `z=265` |

**`transform_json`（13 个数）才是权威位姿**（3x3 旋转行主序 + xyz 平移 + 缩放），
`x/y/z` 是便捷入口，走的是 AddComponent5 的"中心"语义。**两者不要混用。**

### 10.1b ✅ 已推翻：三步顺序其实是多余的（2026-09-27 修正）

> **本节旧结论是错的，已被实测推翻。** 当时记的是"必须三步：预加载 → 切回装配体 → 插入，
> 且仍有间歇性失败"。真实根因见 §14 状态表：传给 `AddComponent5` 的
> `swAddComponentConfigOptions` 误写成了 `2`（`NewConfigWithAsmStructure`）而不是
> `0`（`CurrentSelectedConfig`）。**改成 0 之后，直接插入即可，预加载与切回都不需要。**

对照实验（同一份 `flange bolt.sldprt`）：

| 场景 | 修 0 之前 | 修 0 之后 |
|---|---|---|
| 不预加载，直接插入 | 0/5 | **5/5 ✅** |
| 预加载 + 切回 + 插入 | 0/5 | **5/5 ✅** |

**结论：`open_document` + `activate_document` 那套三步流程是多余的**，
所谓"间歇性失败"只是错误枚举值导致的表现差异，不是时序问题。
另外 `x/y/z` 传的是**零件中心**不是原点，见 §10.1。

保留旧三步写法也不会出错（5/5 仍然通过），但没必要。

### 10.2 零件命名规范：`中文名_英文名.扩展名`

**所有创建的零件/装配体必须命名为 `中文名_英文名` 格式。**

| ✅ 正确 | ❌ 错误 |
|---|---|
| `主轴壳体_Housing.sldprt` | `Housing.sldprt`（无中文） |
| `长柄扳手_LeverWrench.sldprt` | `长柄扳手.sldprt`（无英文） |
| `换刀主轴装配_BT30_ATC_Assembly.sldasm` | `装配体5.sldasm`（默认名） |

**为什么用 `_` 而不是 `/`**：`/` 在 Windows 是路径分隔符，**不能出现在文件名里**，
所以概念上的"中文名/英文名"落到文件系统时用 `_`。

**中文名要能看懂**：`主轴壳体` 好，`零件1` / `零件5` / `Assembly1` 不合格。
默认名（`零件1`、`装配体5`）**永远要改掉**。

**重命名时机**：必须先 `close_document(close_all=true)`，
SolidWorks 打开的文件被锁着，移动/重命名会失败
（实测：8 个成功、2 个报 "used by another process"）。
**重命名后必须重建装配体**——`.sldasm` 内部存的是零件的绝对路径。

**配合前必查 `suppressed`**：配合被压缩时 `analyze_model(features)` 会带 `"suppressed":true`，
**不解除就改，怎么改都没表现**——这是"改了不生效"类故障的头号嫌疑。

---

## 10.4 ⚠️ 三处常见 API 名错误（反射本机 interop DLL 实测，2026-09-27）

| 常见误写 | 实际 | 说明 |
|---|---|---|
| `swMateAlignments_e` | **`swMateAlign_e`** | 前者**不存在**。`ALIGNED=0 / ANTI_ALIGNED=1 / CLOSEST=2` |
| `CWSimuManager` | **`IModelDocExtension.GetMotionStudyManager()`** | `CWSimuManager` 在 SW2026 interop 里**不存在** |
| `AssemblyDoc.GetBOMTable()` | **不存在** | 真实入口：`ISheet.GetBomTable()` / `IView.GetBomTable()`（仅工程图）、`IModelDocExtension.InsertBomTable1~4`（任意文档） |

## 10.5 `swMateType_e` 实测 26 种，MCP 只暴露 8 种

```
COINCIDENT 0  CONCENTRIC 1  PERPENDICULAR 2  PARALLEL 3  TANGENT 4
DISTANCE 5  ANGLE 6  UNKNOWN 7  SYMMETRIC 8  CAMFOLLOWER 9  GEAR 10
WIDTH 11  LOCKTOSKETCH 12  RACKPINION 13  MAXMATES 14  PATH 15  LOCK 16
SCREW 17  LINEARCOUPLER 18  UNIVERSALJOINT 19  COORDINATE 20  SLOT 21
HINGE 22  SLIDER 23  PROFILECENTER 24  MAGNETIC 25
```

**缺的正好是机械装配最常用的**：`SYMMETRIC(8) GEAR(10) WIDTH(11) PATH(15) LOCK(16)
SCREW(17) COORDINATE(20) HINGE(22) SLIDER(23)`。

`AddMate5` 最后一个 `out ErrorStatus`（`swAddMateError_e`）**当前没被透出**：

```
0 ErrorUnknown  1 NoError  2 IncorrectMateType  3 IncorrectAlignment
4 IncorrectSelections  5 OverDefinedAssembly ← 「你少删了一个配合」，不是 bug
6 IncorrectGearRatios
```

**暴露 ErrorStatus 的价值 > 加功能**：一旦返回 `5` 就知道是过定义。
另可用 `IAssemblyDoc.AutoMateRepair(out MateError, out FeatureError)` 让 SW 自动删冗余。

## 10.6 BOM 导出

**通道 A — 遍历组件（推荐，100% 可脚本、列自定义、无需工程图）**：
```python
asm.ResolveAllLightWeightComponents(False)   # 轻量化件必须先展开，否则会漏
comps = asm.GetComponents(True)              # top-level
mgr   = c.GetCustomPropertyManager3(config) # 读自定义属性
```
**通道 B — 官方表直出 xlsx**：
```csharp
ann = model.Extension.InsertBomTable3("", X, Y, swTableAnnotationType_BillOfMaterials, ...);
ann.SaveAsExcel(path, IncludeHidden, IncludeFileImages);   // 官方直出 .xlsx
```
- ⚠️ **没有官方 `SaveAsCsv`**；要 CSV 得 `SaveAsExcel` 后用 openpyxl 转
- ⚠️ `GetRowCount()` 与 **`GetTotalRowCount()`** 不同，跨页时前者会漏（网上教程最常见的坑）

**本机现状**：`analyze_assembly(components)` 已给 `i/name/path/config/fixed/transform`，
**实测已能拼出 BOM CSV**（见 `设计/换刀主轴装配_BOM.csv`）。
要数量/重量/自定义属性，需给 C# 加 `bom_from_assembly` 工具（约 1 天）。

⚠️ **Python 直连 COM 走不通**（实测）：`win32com.GetActiveObject` 能连上 SW，
但 late-bound 下 **`GetFirstDocument2` 之类带参方法解析不了**（`AttributeError`），
主 typelib 未注册导致 `makepy` 失败。**只有无参属性 getter 能用。**
所以 COM 脚本只适合当"反射 interop DLL 查参数名"的工具，不能当建模通道。

## 10.7 仿真（Motion，不是有限元）

```csharp
ISimulationManager mgr = model.Extension.GetMotionStudyManager();
mgr.CreateMotionStudy(name);
study.CreateDefinition(type);   // 运动分析 / 爆炸图 / 旋转
study.Calculate();  study.SaveToAVI(path);     // ← 最实用：出动画
```
- 实测能做：**运动/爆炸/旋转分析 + 碰撞接触 + 外载 + AVI 视频**
- ⚠️ **没有有限元应力/疲劳**——那是 SOLIDWORKS Simulation，完全另一套 API
- 类型在 `SolidWorks.Interop.swmotionstudy.dll`

## 10.8 标准件来源

**本机实测** `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library\`：
215 个 `.sldprt`，但 `parts/` **只有 18 个**（模具顶针/扣环/齿轮/嵌件/旋钮/钣金）。
**ISO/DIN/GB/ANSI 紧固件库没有安装。**

| 来源 | 覆盖 | 许可 | 备注 |
|---|---|---|---|
| **SolidWorks Toolbox Design Library** | 最全 | 随 SW | ⚠️ **需先安装**；装上后是原生参数化 `.sldprt`，质量最高 |
| **bd_warehouse**（`pip install bd-warehouse`） | fastener/flange/pipe/thread(ISO·Acme·Plastic) | **Apache-2.0** ✅ 干净 | 参数化生成 STEP → 导入 SW。**推荐** |
| FreeCAD_FastenersWB | 大 | ⚠️ **GPL-2.0 会传染** | 慎用 |
| 嘉立创/LCSC 3D | **机械件≈0** | 模型不可再分发 | 见 §10.9 |

**Toolbox 没有"按规格检索"的 COM API**（只有 `ExportToolboxItem`/`ImportToolboxItem`）。
正解：**自己扫 `design library\**\*.sldprt` 建索引**（读文件名 + 自定义属性 + 配置表），
再按路径调 `AddComponent5`。索引是自己的，不用改 SW。

## 10.9 嘉立创 3D 库：对机械装配**价值≈0**（实测）

三段式端点确实通了（无鉴权）：搜索 → `searchByNumbers` 取 `step` → `modules.easyeda.com/.../{step}`
（C50950 实测 1.9 MB AP214）。**但覆盖是 PCB 器件库**：

| 关键词 | 结果 |
|---|---|
| ball bearing | 115 个货，**5/5 抽样全无 3D 模型** |
| linear guide（导轨） | **根本没有这个类目** |
| standoff / M3 铜柱 | 4/4 全无模型 |
| M3 screw | 搜出来全是二极管（重名噪音） |
| heatsink / PCB 隔离柱 | ✅ 有（因为本身就是电子件形态） |

⚠️ `api/products/...` 里的 `uuid_3d` **不能**喂给 STEP 端点（404），必须用 `searchByNumbers` 的 `step`。
⚠️ 三端点都是未公开内部接口，无 SLA/限流条款。**仅在"PCB+外壳一体装配"场景值得做。**

---

## 12. 拓扑优化与仿真（SOLIDWORKS Simulation / COSMOSWorks）

> 本章全部结论来自**反射本机 `SolidWorks.Interop.cosworks.dll`（615 个导出类型）**。
> ⚠️ 调研纪律：**只做本地文件反射（`Assembly::LoadFrom` + `System.Reflection`），
> 不联网、不调用任何许可/激活/注册接口。** 运行许可证由 SolidWorks 自身启动时处理，
> 本项目全程不介入。

### 12.0 本机状态

| 项 | 状态 |
|---|---|
| `SolidWorks.Interop.cosworks.dll` | ✅ 在 redist，513 KB |
| Simulation 插件目录 | ✅ `Simulation\`（含 `CWLang` / `CWResearch` / `CWWizard` / `cwreports`） |
| COM 注册项 | ✅ **已查明**（旧记录"未查到"是查错了地方）：不是 `HKLM\SOFTWARE\SolidWorks\AddIns` 下的 add-in，而是独立 InProcServer32——CLSID `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}` → `Simulation\cosworks.dll`，ProgID `SldWorks.Simulation.19` |
| **实跑** | ⚠ **四控制已按顺序建出（含带面的保留区），夹具/求解仍受阻**：`Create*Control` 的 `err=17` 已修（须在 `BeginEdit/EndEdit` 内 + 先 `CreateGoal(2)`）；`err=13` 已修（`GetStudy` 1-based + 每次用唯一 study 名）；**headless 选面已解决**（`SelectByID2("", "FACE", GetClosestPointOn 投影点)`，校验 `swSelFACES=2`），保留区 `SelectFaces(2 faces) -> 0` 成功。仍卡在 `AddRestraint`/`AddForce` 夹具 ⇒ **未验证"求解出设计结果"**（见 §14.1b） |

### 12.1 调用链路（⚠ 本节旧版写错，已按实测更正）

```vb
' ❌ 旧版写的（实测：不建任何东西，返回 0 = NoError，属假成功）
' ICWModelDoc.AddDefaultOptimizationStudyPlot(0)

' ✅ 实测可行（官方示例写法）
ICWModelDoc.StudyManager.CreateNewStudy3(name, 13, 0, out err)   ' 13 = Topology_Static
ICWModelDoc.StudyManager.GetStudy(1)                            ' ⚠ 1-based
ICWStudy.TopologyStudyManager   → ICWTopologyStudyManager        ' 目标/约束/控制
ICWStudy.TopologyStudyOptions   → ICWTopologyStudyOptions        ' 迭代/收敛/保留区
' 建约束必须在 TopologyStudyManager.BeginEdit()/EndEdit() 会话内，且先 CreateGoal(2=MinimizeMass)
' ICwAddincallback.OptimizationStudyUpdate() 是 add-in 自己的回调，API 侧不用它
```

完整可跑代码见 `AI操作手册_SolidWorks.md` §6；踩坑与边界见 §14.1b/14.1e。

### 12.2 `ICWTopologyStudyManager`（反射签名，2026-09-27）

```csharp
Void   BeginEdit();  Int32  EndEdit();
Int32  CreateGoal(Int32 NGoalType);                  // 研究目标
CWTopologyMassConstraint            CreateMassConstraint(out Int32 ErrorCode);
CWTopologyDisplacementConstraint    CreateDisplacementConstraint(out Int32 ErrorCode);
Int32  RemoveConstraint(String SConstraintName);
CWTopologyMassConstraint            GetMassConstraint(String Name, out Int32 ErrorCode);
CWTopologyThicknessControl          CreateThicknessControl(out Int32 ErrorCode);
CWTopologyPreservedRegion           CreatePreservedRegionControl(out Int32 ErrorCode);
CWTopologyDemoldControl             CreateDemoldControl(out Int32 ErrorCode);
CWTopologySymmetryControl           CreateSymmetryControl(out Int32 ErrorCode);
Int32  RemoveControl(String SControlName);
CWTopologyThicknessControl          GetThicknessControl(String Name, out Int32 ErrorCode);
```

### 12.3 约束对象（都以 `BeginEdit()` / `SetXxx()` / `EndEdit()` 三段式配置）

| 接口 | 可配项 |
|---|---|
| `ICWTopologyMinimizeMaximumDisplacementGoal` | 目标：最小最大位移 |
| `ICWTopologyMassConstraint` | `SetMassPreference(Int32)` / `SetValue(Double)` / `SetUnit(Int32)` / `SetName` |
| `ICWTopologyDisplacementConstraint` | 位移约束（含坐标系/分量/比较符选项） |
| `ICWTopologyStressConstraint` | 应力约束（Von Mises 等） |
| `ICWTopologyFactorOfSafetyConstraint` | 安全系数 |
| `ICWTopologyFrequencyConstraint` | 频率（**避免颤振**，机构件必设） |
| `ICWTopologyThicknessControl` | 最小梁宽 → **决定能不能铣出来** |
| `ICWTopologyPreservedRegionControl` | 保留区（轴承位/螺纹孔/密封面不能动） |
| `ICWTopologySymmetryControl` | 对称（避免左右不对称导致装不进去） |
| `ICWTopologyDemoldControl` | 脱模方向 → **决定能不能开模** |

### 12.4 `ICWTopologyStudyOptions`（反射签名）

```csharp
Void SetStaticStudyPreRun(Int32 NPreRun);
Void SetPreservedRegionSetting(Int32 N);
Void SetPreservedContactConnectorSetting(Int32 N);
Void SetMinMaxFormulationForLoadCases(Int32 N);
Void SetConvergenceCheck(Int32 N);
Void SetIterationOption(Int32 N);
Void SetIterationLimit(Int32 N);
```

### 12.5 枚举（`swsTopology*_e`，反射到 40+ 个）

`swsTopologyStudyGoalType_e` `swsTopologyStudyConstraintType_e`
`swsTopologyStudyConstraintComparator_e` `swsTopologyStudyConstraintValuationOption_e`
`swsTopologyIterationOption_e` `swsTopologyActivationOption_e`
`swsTopologySymmetryControlOption_e` `swsTopologyDemoldDirectionOption_e`
`swsTopologyPreservedRegionOption_e` `swsTopologyStudyDisplacementCoordinateSysOption_e`
`…_DisplacementComponentType_e` `…_StressComponentType_e` `…_FactorOfSafetyComponentType_e`
`…_MassConstraintOption_e` `…_DisplacementConstraintLocationOption_e`
以及每类约束/控制的 `_Errors_e`

### 12.6 工程判断：**先建控制再加约束**

拓扑优化跑通几乎总差三步，按顺序补：

1. **厚度控制**（`CreateThicknessControl`）——不设会给你一堆 0.5mm 薄肋，铣不动
2. **保留区**（`CreatePreservedRegionControl`）——轴承位、螺纹、密封面必须锁住
3. **频率约束**（机构件必设）——否则解出来一抖就废

### 12.7 对本项目（BT30 主轴）的具体建议

| 零件 | 值不值得做拓扑优化 | 理由 |
|---|---|---|
| **主轴壳体** Ø80×110 | ✅ **最值得** | 想减重又不损失刚度，典型的载荷路径优化场景 |
| 长柄扳手 20×20×300 | ⚠️ 收益小 | 受力明确（杠杆），20×20 方钢在 80N 手力下已经够用 |
| 拉钉 | ❌ 不值得 | 细长受拉，拓扑优化对拉伸杆件没优势 |
| 碟簧 | ❌ 不值得 | 已经是最优的碟簧几何（GB/T 1972 标准件） |

---

## 14. 本执行层新增能力与实测状态（2026-09-27）

> 📌 **AI 请优先读 `AI操作手册_SolidWorks.md`**（同目录）——那份按"要做 X 查这张表"组织，
> 包含本节全部内容且更全。本节保留人类可读的详细论证与数据。

新增源文件 `Services/SolidWorksService.Capability.cs`（约 1500 行），
注册在 `Controllers/ToolController.Dispatch`。**直连 `POST /api/tool/execute` 可用，
重启 DSH 宿主后才出现在 MCP 的工具 schema 里。**

| 工具 | 状态 | 实测证据 / 阻塞 |
|---|---|---|
| `bom_from_assembly` | ✅ **可用** | 8 个组件 → JSON + CSV 落盘，含 `suppressed` / `excluded_from_bom` |
| `list_standard_parts` | ✅ **可用** | 全库 215 个 sldprt，按分类统计 |
| `lcsc_fetch_step` | ✅ **可用** | 返回真实 LCSC 料号（**必须先设 TLS 1.2**，见 §14.1） |
| `motion_study` | ✅ **可用**（AVI 除外） | 4 处签名按本机官方 CHM 修正后：`explode -> True`、`rotate 2 turn(s) about X (CW) -> True`、`ActivateMotionStudy -> True`、`Calculate() -> True`。**AVI 导出仍失败**：`SaveToAVI()` 真实返回 `False` 且不产生文件——参数已全部设对（`OutputType=1`/`SaveEntireAnimation=True`/`RendererType=0`），前置条件也全绿，故属 SolidWorks 渲染侧在本机不可用，**不是调用方式错**。现在如实回报 `save_to_avi_returned:false` + `file_on_disk:false`，不再静默假成功 |
| `insert_standard_part` | ✅ **已修复** | 根因：`swAddComponentConfigOptions` 误传 `2`（= `NewConfigWithAsmStructure`）而非 `0`（= `CurrentSelectedConfig`）。修 0 后 **15/15 成功**（修复前 0/15）。附带结论：**零件根本不需要预加载**，旧错误信息里 "requires the part to be ALREADY OPEN" 是错的 |
| `topology_optimize` | ⚠ **目标+四控制+位移约束全通，无解** | `action=probe` 全链路 ✅。**已修六处**：(a) `Create*Control` 原返 `err=17`——须在 `TopologyStudyManager.BeginEdit()/EndEdit()` 内且先 `CreateGoal(2)`；(b) `err=13`——`GetStudy` **1-based** + 唯一 study 名；(c) **headless 选面已解决**——`SelectByID2("", "FACE", GetClosestPointOn 投影点)`，保留区 `SelectFaces(2 faces) -> 0`；(d) `add_fixture`/`run_solve` opt-in 化；(e) **位移约束可建**（绕开夹具）`create err=0` + 回取 `err=0`；(f) 顶点选择三路全败。**硬边界**：夹具（11 形态全拒）与 headless 顶点选择都不可用 ⇒ 求解器拿不到实际约束 ⇒ **本机无法求解出拓扑结果**（详见 §14.1b） |

### 14.1 已踩并修掉的坑（都写进源码注释了）

0. **启动 SolidWorks / 执行服务必须用 WMI 派发**，否则活不过 DSH 宿主重启：
   ```powershell
   Invoke-CimMethod -ClassName Win32_Process -MethodName Create `
                    -Arguments @{ CommandLine = '"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"' }
   ```
   `Start-Process` 派生的进程落在宿主的 kill-on-close Job object 里，宿主一重启就被一起带走
   （本项目已因此白跑两次）。
0b. **PowerShell 做不了这里的 COM 活**：`pwsh` 7 已移除 `-ComObject` 与
   `Marshal.GetActiveObject`；Windows PowerShell 5.1 虽能连上，但 late-bound 调用返回
   `0x8002802B TYPE_E_ELEMENTNOTFOUND`（主 typelib 未注册），且 `[ISldWorks]$com` 转型抛
   `InvalidCastException`。**这些活只能写在 C# 执行层里**（C# 编译期转型才 work）。
1. **.NET 4.x `HttpClient` 默认只到 TLS 1.0** → 所有 HTTPS 调用报
   "发生一个或多个错误"。必须先：
   ```csharp
   System.Net.ServicePointManager.SecurityProtocol = SecurityProtocolType.Tls12;
   ```
2. **`_solidWorks` 是服务启动时缓存的 RCW**。SolidWorks 进程一旦被重启，
   这个引用就失效，`IActiveDoc2` 返回 null，报成 `NO_ACTIVE_DOCUMENT`（极具误导性）。
   修法：`Marshal.GetActiveObject("SldWorks.Application")` 从 ROT 重新获取并回写字段。
3. **工具不需要 SolidWorks 时绝不能碰 `_solidWorks`**——进程没开就是 `NullReferenceException`。
   用 §14 的 `SafeActiveDoc()` 安全探测。
4. **`AddComponent5` 的配置选项要用 `0`**（`swAddComponentConfigOptions_CurrentSelectedConfig`），
   传 `2`（`NewConfigWithAsmStructure`）会**间歇性返回 null**——根因已查明并修复（见 §14 状态表），
   修复后 15/15。**零件也不需要预加载**（`open_document` 那套三步顺序是多余的）。
5. **回转轴必须按端点精确匹配**，不能坐标拾取 —— 见 §4，错误会静默产生 5 倍体积的错误零件。

### 14.1b 拓扑优化：加载 Simulation 的唯一可行办法（2026-09-27 实测）

`ISldWorks.LoadAddIn("...\Simulation\cosworks.dll")` **恒返 `swUnknownError(-1)`**，
`GetAddInObject("SldWorks.Simulation")` 恒 `null`。原因：Simulation **不是 `.sldaddon`**
（整个安装树一个 `.sldaddon` 都没有；`HKLM\SOFTWARE\SolidWorks\AddInsStartup` 里原本
只有 SOLIDWORKS Inspection），而它是独立 COM InProcServer32，**必须加载进 SLDWORKS.exe 进程内**。

✅ **可行的办法**：让它随 SolidWorks 启动自己加载——

```powershell
New-ItemProperty -Path 'HKCU:\Software\SolidWorks\AddinsStartup' `
                 -Name 'SldWorks.Simulation.19' -Value 1 -PropertyType DWord -Force
# 回滚 = 删掉这个值
```

注册信息：CLSID `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}` → `Simulation\cosworks.dll`，
ProgID `SldWorks.Simulation.19`，无版本 ProgID `SldWorks.Simulation`，ThreadingModel `Apartment`。

⚠ **顺序铁律**：执行服务一重启，SW 侧 add-in 就失联（`GetAddInObject` 返 null、
`LoadAddIn` 返 -1）。所以跑拓扑必须**先重启服务、再重启 SolidWorks**，顺序不能反。

**建 study 必须用** `StudyManager.CreateNewStudy3(name, 13, 0, out err)`
（`13` = `swsAnalysisStudyTypeTopology_Static`）。
`AddDefaultOptimizationStudyPlot(0)` 会返回 `0 = swsOptimizationDesignResultNoError`
却**什么都不建**（`StudyCount` 仍 0、`GetStudy(0)` 为 null）——**典型的假成功**。

**建约束/控制必须在 manager 自己的编辑会话内，且先有 Goal**（这条是 `err=17` 的真因）：

```csharp
topo.BeginEdit();                      // ICWTopologyStudyManager 自带 BeginEdit/EndEdit，
                                       // 与各对象自己的三段式是两回事
topo.CreateGoal(2);                    // 2 = swsTopologyGoalType_MinimizeMass
topo.CreateThicknessControl(out err);  // 之后所有 Create* 才返回 err=0
topo.CreatePreservedRegionControl(out err);
topo.CreateSymmetryControl(out err);
topo.CreateDemoldControl(out err);
topo.CreateMassConstraint(out err);
topo.EndEdit();
```

实测：放在编辑会话外时四个 `Create*Control` **一律 `err=17`**
（`swsTopoErrCode_SetOperationNotSupported`）；放进会话并先建 Goal 后**全部 `err=0`**。
`swsTopologyStudyGoalType_e`：`0` MaximizeStiffness / `1` MinimizeMaximumDisplacement /
`2` MinimizeMass。

**设材料必须先选中实体**：`IPartDoc.GetBodies2(swSolidBody, true)` 取实体名 →
`modelDoc.Extension.SelectByID2(name, "SOLIDBODY", …)`（返回 `bool`）→
`study.SolidManager.SetLibraryMaterialToSelectedEntities(lib, mat)`。
⚠ `SelectByID2` 在 `IModelDocExtension` 上，**不在** `IModelDoc2`/`IPartDoc`；
`ISelectionMgr` **没有** `ClearSelection2`/`AddSelection2`（只有 `DeSelect`/`AddSelectionListObjects`，
但后者实测选不中实体）。

**官方示例是权威答案（`Create Topology Study Example (VBA)`，抓取方式见下）**：
`https://help.solidworks.com/2019/English/api/swsimulationapi/Create_Topology_Study_Example_VB.htm`
本机直连该站 **403**，用 Jina Reader 绕过：
```powershell
(Invoke-WebRequest "https://r.jina.ai/https://help.solidworks.com/..." -UseBasicParsing).Content
```
（Exa MCP 免费额度已耗尽返 429，改用内置 `web_search` 找链接 + Jina 读正文。）

官方示例给出的、与本机实现对不上的关键点：

| 官方写法 | 本机曾写成 | 后果 |
|---|---|---|
| `GetAddInObject("CosmosWorks.CosmosWorks")` | `"SldWorks.Simulation"` | 后者也能拿到对象，但不是官方 id |
| `StudyManager.CreateNewStudy3(name, 13, 0, ErrorCodeObj)` | 同 | ✅ 一致，`13` 确认 |
| `StudyManagerObj.GetStudy(1)` | `GetStudy(0)` | **`GetStudy` 是 1-based** |
| 每次建新 study | 固定名 `MCP_Topology` | `CreateNewStudy3` 同名返 `err=2`，且 `DeleteStudy` 删不干净 ⇒ 旧 study 残留，`GetStudy(0)` 拿到旧的那个 ⇒ 四个 `Create*Control` 全部返回 **`err=13`**（`OnlyOneThicknessControlCanBeDefined` 等）而不是 0 |
| `Array(SelectionManager.GetSelectedObject6(i, -1))` | 直接传 `IBody2.GetFaces()` 拿的面 | 报 COM 封送错误（见下） |
| `SetMassPreference(1)` → `SetValue(60)` → `EndEdit()` → **再 `GetMassConstraint(name)` 回取校验** | `SetValue(0.5)` | 值没落到约束上；官方是先设 preference 再设整数**百分数** |

**修好后实测（一次干净运行）**：
`thickness/preserved/symmetry/demold 全部 err=0`、`mass constraint err=0`、
`GetMassConstraint('MCP_target_mass') -> err=0 (round-trip OK)`、`EndEdit() -> 0`、
`SetLibraryMaterialToSelectedEntities('AISI 1020') -> 0`。
⇒ **唯一 study 名 + 官方质量约束写法，是控制项能全通的两个必要条件。**

**✅ 面级选择不需要 UI 预选（headless 可行，实测）**——官方示例里的面是用户先在 UI 选好的，
那是示例上下文，不是 API 限制。三条路都实测过：

| 方式 | 结果 |
|---|---|
| `ISelectionMgr.AddSelectionListObject(face)` / `AddSelectionListObjects` | ❌ 对 `IFace2` **选不中**（返 false / 0） |
| `ILoop2.Select(null, false, null)` | ⚠ **选中了但是边**——`GetSelectedObjectType2` 返回 `1 = swSelEDGES`，不是 `2 = swSelFACES`。静默选错类型，最坑的一个 |
| `Extension.SelectByID2("", "FACE", x, y, z, …)` + `IFace2.GetClosestPointOn(px,py,pz)` | ✅ **成功**，`GetSelectedObjectType2` 返回 `2 = swSelFACES` |

要点：
- `SelectByID2` 的坐标必须**真的落在面上**。包围盒中心只对**平面**成立，所以用
  `GetClosestPointOn` 把任意探针点投影到面上，保证得到面上一点。
- `IFace2.GetBox()` 返回 `object`（SafeArray），要 `as double[]` 才能索引。
- **务必用 `GetSelectedObjectType2(i)` 校验**选中的到底是什么：`Select()` 返回 true
  不代表选对了类型。`swSelectType_e`：`0` None / `1` Edges / `2` Faces / `3` Vertices /
  `4` DatumPlanes / `5` DatumAxes。
- `ISelectionMgr.DeSelect` 的索引参数是 **`Object`** 不是 `int`；传 int 会封送失败，
  异常被空 catch 吞掉 ⇒ **选择从未被清空**，材料步骤残留的 SOLIDBODY 会混进面数组
  （表现：selection count 比预期多 1）。要传 `(object)si`，索引从 `GetSelectedObjectCount()`
  递减到 1（**1-based**）。

**✅ 拓扑优化【不一定要夹具】——位移约束可建（绕开 `AddRestraint`）**
标准做法是"最小质量 + 位移约束"，而位移约束建在**同一个已可用的** `TopologyStudyManager` 上。
实测：`CreateDisplacementConstraint(out err) -> err=0`、`EndEdit=0`、
`GetDisplacementConstraint` 回取 `err=0`。配置：`SetCoordinateSystemPreference(0=Global)`、
`SetComponent(3=URES)`、`SetComparator(0=IsLessThan)`、`SetValue(位移/1000)`（**单位是米**）。

⚠ **它也必须在 `BeginEdit/EndEdit` 会话内创建**——放在 `EndEdit` 之后同样返 `err=17`
（与四个控制项同一规律）。

枚举：
`swsTopologyStudyConstraintComparator_e` `0` IsLessThan / `1` IsGreaterThan / `2` IsInBetween；
`swsTopologyStudyDisplacementComponentType_e` `0` UX / `1` UY / `2` UZ / `3` URES / `4-6` `_ABS`；
`swsTopologyStudyDisplacementConstraintLocationOption_e` `0` Auto / `1` UserDefine。

**⛔ 两个决定性陷阱**：
1. **`SetLocationPreference(Auto=0)` 不等于"求解器自动选点"**——它让约束**没有位置**，
   求解器直接忽略整个 study：`MeshAndRun` 约 13 秒返回、`Results` 为 `null`、CPU 零消耗。
   必须用 `SetVertices(Object VerticesDispArray)` 给真实顶点。
⛔ **headless 选顶点本机不可用**。三条路都试过：
- `ISelectionMgr.AddSelectionListObject(vertex)` —— 无效
- `Extension.SelectByID2("", "VERTEX", x, y, z)` —— 返回 false
  （**`SelectByID2` 按"点所在的实体"选择**：能稳定选中**面**（配合 `GetClosestPointOn` 投影点），
  但**顶点是零维实体**，只有拾取点精确落在顶点上才命中，浮点坐标做不到精确。）
- **`IModelDoc2.SelectAt(Flags, X, Y, Z)` —— 永久阻塞服务** ⚠ 见下

⚠⚠ **`SelectAt` 是本项目最阴险的一个调用**：它是 SolidWorks 自己的 ATOM 命中测试器
（`Flags` 传 `swSelectOption_e`），看起来正是"无窗口也要点选"该用的工具。实际在无图形窗口时
**不返回 false、而是永久阻塞**：`/health` 超过 5 分钟无响应、SLDWORKS 内存掉到 140MB、
CPU 恒定 22s、`stateVersion` 永不前进。**之前"顶点选不中"其实是被它误导的。**

**真顶点坐标从哪来**：不要用 `analyze_model(edges)` 的**边中点 `mid`**（我踩过），
要用同一条边的 **`start` / `end`**。整圆柱的闭合圆边 `start == end`（如
`[0.04, 0, 0.11]`），那一个点就是该圆的**缝合顶点**——注意只有**一个**，不是四个。

⇒ **对比记忆**：**面可以 headless 选中**（`SelectByID2` + `GetClosestPointOn` 投影 +
校验 `swSelFACES=2`），**顶点不行**。这是本机 headless 路径的确认天花板。

**顶点为什么不行——根因（不是"方法没试对"）**：
`SelectByID2` 是"光标下是什么"的**命中测试**。面有**面积**，把探针点用
`GetClosestPointOn` 投影到面上就必然命中；**顶点是零维的**，要求探针点与其
**精确重合**，浮点坐标做不到 ⇒ 永远返回 `false`。

绕开命中测试的三条路也都不通：
`AddSelectionListObject(vertex, SelectData)` → false；
`SelectByID2("", "VERTEX", …)` → false；
**取活顶点对象**（`IEdge.GetStartVertex()` → `IVertex` → `AddSelectionListObject`）
→ **扫遍所有边，产出的顶点坐标列表为空**。

⚠ **两个 interop 类型陷阱**：
1. `GetStartVertex()` 返回 `object`，**必须转 `IVertex` 而非 `Vertex`**——两者都是接口，
   但 **`Vertex` 是空标记接口（`GetMethods()`→0）**，`IVertex` 才有 18 个成员（含 `GetPoint()`），
   转错会静默得到空壳。
2. ⚠ **纯回转体零件可能根本没有顶点**：主轴壳体 Ø80×110 = 2 平面 + 2 圆柱面 / 4 条闭合圆边，
   这种几何 `GetStartVertex()/GetEndVertex()` 全返回空。**对回转类零件别指望顶点路径。**

### 14.1c 同步 COM 调用会弹模态框 → 永久卡死服务（本项目最隐蔽的一个坑）

`CreateMesh()` / `RunAnalysis()` 是**同步 COM 调用**。一旦 study 真的走到划网格/求解，
Simulation 会弹一个**模态对话框**（枚举 SLDWORKS 顶层窗口可见：
`class='#32770' vis=True title=''`，标准对话框类、可见但无标题），
于是**服务线程被无限期挂起**：`/health` 不再响应，SolidWorks 自身 CPU 恒定不涨，
也不 spawn `star.exe` 之类的网格器子进程。

⚠ 隐蔽之处：**在能真正开始求解之前**所有调用都是毫秒级返回错误码、不弹框，
所以这个挂死**只有在管线走得足够远之后才出现**——很容易误判成"服务崩了"或"机器卡了"。
诊断手段：`GetWindowThreadProcessId` + `EnumWindows` 枚举目标进程窗口，找 `vis=True` 的 `#32770`。
处置：这类同步调用一律 opt-in（本项目为 `run_solve=true`），且必须有人盯着 SolidWorks 窗口点掉提示。

### 14.1d 标准件来源：bd-warehouse 已验证可用（2026-09-27）

`build123d 0.13.0` + `bd-warehouse 0.3.0`（Apache-2.0，干净）已装进
`adapters\claude\.venv`。生成 ISO 标准件 STEP → 导入 SolidWorks，与 build123d 侧体积交叉验证：

| 件 | build123d | SolidWorks | 偏差 |
|---|---|---|---|
| 六角螺母 M12 ISO4032 | 1803.1 mm³ | 1803.1 mm³ | 0.002% |
| 平垫圈 M12 ISO7089 | 863.1 mm³ | 863.1 mm³ | 0.003% |
| 内六角螺钉 M12×40 ISO4762 | 5824.8 mm³ | 5824.8 mm³ | 0.001% |

两个**独立内核**（OCCT / SolidWorks）体积一致到 0.003% ⇒ STEP 通路可靠。
⚠ API 细节：`HexNut`/`SocketHeadCapScrew` 的 size 要带螺距（`"M12-1.75"`），
`PlainWasher` 不要带（`"M12"`）。

### 14.1e 「求解没出结果」怎么快速定位（先看网格，再看约束）

`ICWStudy.MeshAndRun()` 返回 `void` 且**"正常返回"也说明不了任何事**——它不抛异常、
`Results` 照样是 `null`。所以判断失败点要靠**自己问 study 要网格**：

```csharp
dynamic m = study.Mesh;          // 为 null 就是没网格
int meshType = (int)study.MeshType;
```

本机实测（2026-07-27）：

```
post-solve mesh check: MeshType=0, mesh=PRESENT
result: {"mesh_return":0,"run_return":0,"mesh_type":0,"mesh_present":true}
ICWStudy.Results is null
```

⇒ **网格已经建出来了**（`mesh_present=true`），`MeshAndRun` 也"正常"跑完，
但求解器不产出结果 —— 失败点被精确定位到**"求解器拿不到可用约束去启动迭代"**，
既不是网格问题也不是建模问题。

**排查顺序（比读一堆 `swsRunAnalysisError` 码快得多）**：

| `mesh_present` | `Results` | 结论 |
|---|---|---|
| `false` | `null` | 网格问题 |
| `true` | `null` | **约束问题**（本机属于这种） |
| `true` | 有值 | 成功，可读结果 |

⚠ `CWMesh` 在这个 interop 上**没有任何导出成员**（`GetMembers()` 返回空，成员在 `ICWMesh` 上），
所以节点数/单元数读不到，只能判断 `Mesh` 是否为 `null` —— 这已经够用。

**目标第 ③ 条的完整证据链**：
1. ✅ 目标 + 四控制（厚度/保留区带真面/对称/脱模）+ 质量约束 + 位移约束，全部 `err=0`
2. ✅ 网格，`mesh_present=true`
3. ❌ 求解器可用的实际约束：夹具（`AddRestraint` 被拒）或带顶点的位移约束（顶点选不中）
4. ⚠ 实际求解调用本身会弹模态框楔死服务（opt-in `run_solve`）

第 3 条在本机无解。

**⛔ `AddRestraint` / `AddForce` —— 本机不可用，不要再试。**
共实测 **11 种调用形态**全部被拒：
`dynamic` 晚绑定 / 强类型早绑定（`GetTypedObjectForIUnknown`）/ 显式 IDispatch（`Type.InvokeMember`）
× 传**面**或传**实体**（`SolidBody`）× 数组形态 `object[]` / `System.Array` / `Array.CreateInstance` SafeArray / `IFace2[]`
× `RefGeom` 传 `null` / `Type.Missing` / `DBNull.Value` × 保留或丢弃返回值。

**唯一有信息量的是失败的【深度】**：

| `RefGeom` | 结果 | 是否挂死 |
|---|---|---|
| C# `null` | `ArgumentException`（封送层就失败） | **会**——`/health` 无响应、SW CPU 恒定、内存从 1.2GB 掉到 229MB |
| `Type.Missing` / `DBNull.Value` | `调用的目标发生了异常`（**已进 cosworks 内部**） | 不会 |

⇒ ①C# `null` **不是**根因（只是最容易触发挂死的那种）；②面 vs 实体**不是**根因（行为完全一致）；
③所有非 `null` 变体都稳定死在 cosworks 内部 ⇒ **这是许可/模块层面的边界，不是封送 bug**。
（另外 `ICWLoadsAndRestraintsManager` 带 `TypeLibTypeAttribute` + `DispIdAttribute`（`AddRestraint=3`、
`AddForce=5`）+ `ComImport`，是 dual 接口；`AddRestraint` 参数 1 是 `Int32`，
"无法转换参数 1" 只是 .NET COM 封送层的通用兜底消息。）

⚠ **`AddRestraint` / `AddForce` / `CreateMesh` / `RunAnalysis` 四者都把 `add_fixture` /
`run_solve` 设为默认 `false` 的 opt-in**——headless 调用方不能因为要个夹具就把服务拖死。

⚠ **变体扫描的操作纪律**：第一次扫描时把**已知会挂死的 `null` 变体放在第一位**，
整个请求楔死、后面三个变体根本没机会执行，扫描报告全空。
**"会挂死的变体"必须排除或放最后**，否则一次挂死就废掉整轮实测。

**楔死后的恢复流程**：两个进程都 `Stop-Process`，等 6~10s
（若残留 0MB 僵尸 `SLDWORKS` 要单独清掉，否则新实例会卡在 `splash` 不加载），
再用 `Invoke-CimMethod` 两者拉起，约 24~40s 后 `comAttached` 恢复为 `true`。
恢复后 `open_document` + `analyze_model` 体积与基线一致（主轴壳体 220823 mm³），模型状态没被搞坏。

**其它已确认的 API 细节**：`ICWForce` 没有 `SetForceValue`，是
`ForceBeginEdit()` → `set_Unit` → `SetForceComponentValues(B1,B2,B3,D1,D2,D3)` → `EndEdit()`；
`ICWModelDoc` 上没有 `Solid` 成员，`SolidManager` 在 `ICWStudy` 上。

`swsRunAnalysisError_e` 实测出现：`19` MaterialNotDefined、`22` AuthorizationFailed、`23` MeshNotFound。
`swsTopologyStudyError_e` 重要值：`2` 重名、`3` NoGoalHasBeenSet、`13` OnlyOneThicknessControl、
`14` OnlyOneDemold、`15` OnlyOneSymmetry、`17` SetOperationNotSupported。

### 14.2 构建方式（本机）

**没有安装任何东西。** MSBuild 路径手册写错了（实为 BuildTools 非 Community），
且缺 .NET 4.8 目标包，因此**直接用 Roslyn 编译器**：

```powershell
$csc = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\Roslyn\csc.exe"
& $csc /nologo /target:exe /platform:anycpu /debug:full /langversion:latest `
  /out:$new /r:System.dll /r:System.Core.dll /r:System.Net.Http.dll /r:Microsoft.CSharp.dll `
  /r:"$bin\Microsoft.Owin.dll" ... /r:"$ref\SolidWorks.Interop.sldworks.dll" ... `
  <全部 .cs>
# 依赖 DLL 直接引用 bin\Debug 里已有的（NuGet packages 目录已丢失）
```

⚠️ **`bin\Debug\SolidWorks.Interop.sldworks.dll` 曾经是 34.3.2.3 的旧残留，
遮蔽了程序需要的 34.0.0.5070**，新编译的 exe 一启动就报程序集不匹配。
已统一并备份为 `.3432.bak`。**改 interop 版本前先确认两份的版本号。**

---

## 13. 参考

- [FeatureCut4 (IFeatureManager) — 官方](https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~FeatureCut4.html)
- [FeatureExtrusion2/3 (IFeatureManager) — 官方](https://help.solidworks.com/2026/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~FeatureExtrusion2.html)
- [swEndConditions_e 枚举 — 官方](https://help.solidworks.com/2024/English/api/swconst/SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swEndConditions_e.html)
- [FullyDefineSketch (ISketchManager) — 官方](https://help.solidworks.com/2024/english/api/sldworksapi/SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ISketchManager~FullyDefineSketch.html)
- [Fully Define Underdefined Sketch 示例 (VB.NET) — 官方](https://help.solidworks.com/2023/english/api/sldworksapi/fully_define_underdefined_sketch_example_vbnet.htm)
- [AddRelation (ISketchRelationManager) — 官方](https://help.solidworks.com/2015/english/api/sldworksapi/SOLIDWORKS.Interop.sldworks~SOLIDWORKS.Interop.sldworks.ISketchRelationManager~AddRelation.html)
- [草图关系图标（官方图解）](https://help.solidworks.com/2026/japanese/SolidWorks/sldworks/c_Sketch_Relations_Icons.htm)
- [FeatureCut4 逐参数表 + 可运行宏 — CAD Coder](https://thecadcoder.com/solidworks-macros/create-extrude-cut-feature/)
- [FeatureExtrusion3 逐参数表 + 可运行宏 — CAD Coder](https://thecadcoder.com/solidworks-macros/create-extrude-feature/)
- [草图关系宏示例全集 — CAD Coder](https://thecadcoder.com/solidworks-macros/add-sketch-relations/)
- [DSH-操作手册.md](DSH-操作手册.md) — MCP 接入、46 个工具速查、本机运维信息

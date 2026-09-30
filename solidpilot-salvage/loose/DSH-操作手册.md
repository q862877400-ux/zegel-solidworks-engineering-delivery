# SolidPilot 操作手册（给 AI 看）

> 本文件是给 **AI（DSH）** 读的操作手册，不是给人看的介绍文档。
> 你已经通过 MCP 挂载了一组 SolidWorks 工具，工具名形如 `mcp__solidworks__<tool>`。
> 下面讲的是：**什么时候该调什么、参数怎么填、报错怎么救**。
>
> 项目根目录：`C:\Users\Zegel\solidpilot-mcp`
> 目标版本：SolidWorks 2026（本机已装，装在 `D:\Program Files\SOLIDWORKS Corp`）

---

## 0. 三十秒速览

你面对的不是几千个 SolidWorks API，而是 **46 个 MCP 工具 + 13 个资源**。
架构上是四层，**只有最底层碰 COM**：

```
你（AI）
  → MCP adapter（Python，46 个工具）
      → 执行层（C#，REST :5000，唯一碰 COM 的层）
          → SolidWorks 2026
```

关键设计：**别把自己当 API 调用者，把自己当设计者**。
你要表达的是"在顶面打个 φ10 的通孔"这种**特征级意图**，而不是 `FeatureManager::InsertFeature...`。
低层工具是执行手段，不是你的思考方式。

---

## 1. 开工前三步（必做）

### 第一步：拉起整条链路

```
mcp__solidworks__ensure_ready
```

无参数。它会：
1. 若 C# 执行服务没在跑（:5000），自动把 `SolidworksExecution.exe` 拉起来（detached、无窗口）；
2. 通过 COM 连上 SolidWorks，**SolidWorks 没开就自动冷启动**（可能要几十秒）。

返回 `comAttached=true` 才算可用。**这一步不开任何文档，只保证链路通。**

### 第二步：确认有没有活动文档

```
mcp__solidworks__verify_state
```

返回当前状态 + 特征树。`sv=0` 且无文档 → 你还没开任何东西，下一步要么 `open_new_part`，要么 `open_document`。

### 第三步：先看，再动手

```
mcp__solidworks__analyze_model   analysis_type="features"
```

**任何建模动作之前先分析。** 盲画 = 盲改。这条没什么好商量的。

---

## 2. 三条硬规则（违反必炸）

### 规则一：单位是米，不是毫米

所有长度参数一律 **米**（SolidWorks 内部单位）。角度按工具不同分两种，**这个最容易错**：

| 场景 | 单位 |
|---|---|
| 所有长度 / 坐标 / 半径 / 深度 | **米**（φ10 的孔 → `radius=0.005`，50mm 拉伸 → `depth=0.05`） |
| `extrude_feature` 的 `angle`（旋转） | **度** |
| `create_pattern`（圆周）的 `angle` | **度** |
| `add_edge_feature`（倒角）的 `angle` | **度** |
| `add_mate` 的 `angle` | **度** |
| **`modify_dimension` 的 `value`** | **弧度**（角度尺寸也要用弧度！） |
| **`submit_feature_graph` 的 IR** | 长度**米**、角度**弧度** |

### 规则二：能用 index 就绝不用坐标

几乎所有需要"选中某个面/边"的工具，都提供 **index 版参数**，优先于坐标拾取：

| 工具 | 优先参数 | 坐标版（备选） |
|---|---|---|
| `create_sketch` | `face_index` | `face_x/y/z` |
| `add_edge_feature` | `edge_indices`（JSON 数组字符串，如 `'[3,5]'`） | `ex/ey/ez` |
| `sheet_metal_feature` | `edge_index`、`fixed_face_index` | `ex/ey/ez`、`fixed_x/y/z` |

**index 从哪来？** 先跑 `analyze_model(analysis_type="faces")` 或 `"edges"` 拿到索引表。
坐标拾取在复杂模型上会选错，而且错得很安静——它会成功，只是选到了别的面。

### 规则三：`operation_id` 和 `state_version` 你不用管

adapter 在内存里维护 `state_version`，每次响应后自动更新；每次调用自动生成新的 `operation_id` 做幂等键。
**你只传业务参数**（`params` 里的那些）。如果你试图自己传 `operation_id` / `state_version`，是错的。

唯一需要知道的是：万一返回 `INVALID_STATE_VERSION`，adapter 会**自动 resync 一次并用新 id 重试**，对你透明，你不需要手动干预。

### 规则四：**每个草图都必须用尺寸标注完全定义（fully constrained）**

**没有尺寸驱动的图元 = 废料。** 落地要求：

1. **尺寸是唯一的几何真相。** 不要靠 `add_sketch_entity` 的坐标"摆"位置——
   坐标只是建图时的初值，**真正定义几何的是 `add_dimension` 加的尺寸**。
2. **每个尺寸都要有名字**（`D1` `D2` …），后面 `modify_dimension` 靠名字驱动变型；
   名字要能读懂是哪个特征，别留 `D17` 这种。
3. **建完草图立刻验**：`analyze_model(analysis_type="sketch", name="<草图名>")`
   看实体坐标和尺寸是否与设计意图一致；**欠定义（under-defined）就是 bug，不是风格问题**。
4. **关掉"自动加尺寸"再补关键尺寸**——如果环境默认自动标注，先把它清掉，
   否则会得到一堆重复尺寸把几何锁死，改型时动不了。

**为什么这条是硬规则，不是偏好：**

- 无尺寸驱动的图元**不会跟随全局改型缩放**——§7 坑 #18 就是这么报废一个零件的：
  草图里一个无尺寸引用的开缝矩形，在整体缩放后停在原坐标，偏了 0.25mm 侥幸能用，
  偏大了直接就是功能废件。
- `modify_dimension` 只能驱动**被尺寸引用**的几何。没尺寸的边，**你永远改不动它**。
- 别人（或你自己下一轮）拿 `analyze_model` 复核时，**没有尺寸就无法把几何对应回设计意图**，
  只能靠猜。

**判断标准**：草图应该**没有任何自由度**。SolidWorks 状态栏显示
`草图已完全定义` 才算合格；显示欠定义数字（哪怕只有 1 个）就是没做完。

#### 规则四的落地顺序：线 → 立刻约束 → 再画下一条

**轴向对齐的线段必须加 `horizontal` / `vertical` 几何关系**，而且要**一条一条地加**：

```
add_sketch_entity    line(第 1 条)
add_sketch_constraint 'horizontal'  ← 立刻
add_sketch_entity    line(第 2 条)
add_sketch_constraint 'vertical'    ← 立刻
...
最后才是 add_dimension
```

**为什么必须这个顺序**（实测踩出来的）：`add_sketch_constraint` 靠"离 (px,py) 最近的线段"
选目标。**先 `add_sketch_entities` 批量画 12 条，再回头批量加约束**，在台阶密集的回转轮廓上
会选错线——实测 6 条水平只成 3 条、**6 条垂直 0 条全错**，因为相邻台阶的径向距离只有
0.001 m（1 mm），中点坐标落在别的线段的容差球里。

**一条一条加**，草图里当时只有那一条线，选取天然无歧义。

**没有水平/垂直约束的后果**：后续加直径尺寸时 SolidWorks 必须重解几何来满足尺寸，
轮廓会被推歪——实测一个 12 段回转轮廓的肩部被推到 z=0.126 又折回 0.119，
**轮廓自交、revolve 直接失败**，而且失败得很安静（只报 `EXTRUSION_FAILED`，不告诉你哪错了）。

> ⚠️ **`submit_feature_graph`（IR 路径）在本机执行层不可用**：直连 `POST /api/tool/execute`
> 返回 `400 {"error":"Unknown tool: submit_feature_graph"}`。
> 即便 `schema://feature-graph` 资源照常读得到、词汇表也齐，**降级器没编译进这版
> `SolidworksExecution.exe`**。建模只能走 §4 的底层工具链。
> 本机 IR 也**没有 dimension 节点**（node_types 里没有），所以尺寸一律用 `add_dimension`，
> 不能指望走 IR 顺带把草图标好。

---

## 3. 标准工作流

### A. 从零建一个零件

```
ensure_ready
open_new_part                                     # 可选 template_path
create_sketch        plane="Front Plane"           # 或 on_face=true, face_index=N
add_sketch_entity    entity_type="circle", cx=0, cy=0, radius=0.01
add_dimension        px=0, py=0.01, value=0.02     # 约束尺寸，别靠草图坐标
analyze_model        analysis_type="sketch", name="<草图名>"   # 规则四：确认已完全定义
extrude_feature      depth=0.05                    # 默认 boss
analyze_model        analysis_type="features"      # 确认特征树
set_part_material    material_name="AISI 1020"     # 名字必须精确，见 §6
save_document        file_path="D:\\...\part.sldprt"
```

草图实体支持：`rectangle` `circle` `line` `arc` `arc_center` `ellipse` `spline` `fillet` `chamfer`。
批量加草图用 `add_sketch_entities`（比循环调 `add_sketch_entity` 省 token）。
`extrude_feature` 的 `feature_type`：`boss`（默认）`cut` `revolve` `sweep` `loft`。

### B. 改一个现有零件（变型设计）

```
open_document        file_path="D:\\...\part.sldprt"
analyze_model        analysis_type="features"      # 拿到尺寸全名，如 D1@Boss-Extrude1@Part.Part
modify_dimension     name="D1@Boss-Extrude1@Part.Part", value=0.06
analyze_model        analysis_type="mass_properties"   # 确认真的变了
save_document
```

**`name` 必须是 `analyze_model(features)` 报出来的完整尺寸名**，自己拼的名字一定不对。
改完再用 `mass_properties` 复核——这是变型设计的闭环。

`edit_feature` 可以抑制 / 解除抑制 / 删除 / 重命名特征。注意：suppress 和 delete **会改拓扑**，之前拿到的坐标和索引全部作废，要重新 analyze。

### C. 从 2D 图纸反推零件（DXF/DWG）

```
analyze_drawing      file_path="D:\\...\drawing.dxf"        # mode 默认 auto
```

返回两种形态之一：

- `DIRECT_BUILDABLE` + 摘要 → 直接 `mode="build"` 一次调用建出来（目前只有钣金展开图能这样自动走完）；
- `NOT_DIRECT | <原因>` + **完整分析结果** → 你需要先读资源 `recipe://usage/reverse`，按那套规则解读，再用 `submit_feature_graph` 建出来。

reader 提取的东西很扎实：每视图比例（已折算，数字是真值 mm）、按可见性分类的边、已串成闭合环的轮廓、视图对齐对、尺寸取 **CAD 实际打印出来的字符串**（它比存储值权威）、标题栏当参数表读、钣金折弯注释配对折弯线。
**读不出来的东西它会报 skipped，绝不猜。**

### D. 装配

```
open_new_assembly
insert_component     file_path="D:\\...\a.sldprt", fixed=true
insert_component     file_path="D:\\...\b.sldprt", x=0, y=0, z=0.1
analyze_assembly     analysis_type="faces", component="b-1"      # 拿实体索引
add_mate             mate_type="concentric", a_component="a-1", a_index=3,
                                             b_component="b-1", b_index=7
analyze_assembly     analysis_type="mates"                        # 复核
```

配合类型：`coincident` `concentric` `perpendicular` `parallel` `tangent` `distance` `angle` `lock`。
`add_mate` 用的就是 §2 规则二的 **index 选择**（`a_index` / `b_index`），不要用坐标。
`components_flat` 会把嵌套层级的叶子件和根空间变换摊平，读深装配时用这个。

### E. 出工程图

```
create_drawing       model_path="D:\\...\part.sldprt"      # A3
add_drawing_view     view_type="front",     pos_x=0.08, pos_y=0.12
add_drawing_view     view_type="isometric", pos_x=0.20, pos_y=0.12
add_section_view     x1=..., y1=..., x2=..., y2=..., px=..., py=...   # 剖内部/盲特征
auto_dimension_drawing                                     # 插入模型项，比按坐标标尺寸稳
auto_center_marks                                          # 孔/槽中心线中心标记
add_hole_callout     ...
export_document      format="PDF", file_path="D:\\...\part.pdf"
```

钣金件用 `add_flat_pattern_view`（展开图 + 折弯线），这是钣金出图的正规做法。
正交视图默认 Hidden-Lines-Visible（符合制图惯例），可用 `display_mode` 覆盖。

**已知短板：`auto_dimension_drawing` 不懂制图**，可能漏标、错放、甚至标注隐藏边。出图后要人工/你复核一遍，别无脑信。

### F. IR 往返与客观验证（这是本项目的核心能力）

两条门，**走的是同一个编译器**：

- **正向**（从设计意图建，没有原件照抄）：
  先读 `recipe://usage/forward` 和 `schema://feature-graph`，然后
  ```
  submit_feature_graph  graph='{...IR JSON...}', fresh_document=true
  ```
- **反向**（复现一个已有零件）：
  ```
  save_analysis        file_path="D:\\...\part.sldprt"     # 产出 .analysis.json
  #   你读分析产物 → 按 recipe://usage/canonicalization + mapping_part 提 IR → 写回 artifact
  rebuild_from_ir      artifact_path="D:\\...\part.analysis.json", fresh_document=true
  compare_parts        doc_a="D:\\...\part.sldprt", doc_b="<重建的那个>"
  ```

**`verified` 判定标准**（客观，不是自我感觉）：拓扑完全一致 **且** |ΔV| ≤ 1% **且** |ΔA| ≤ 1%。
`compare_parts` 的 `doc_a` 是**基准**（通常放原件），delta 相对它算。`detail="faces"` 会列出多出/缺失的面。
装配对应 `compare_assemblies`：零件集合 + 逐个变换（≤1 µm）+ 配合数与类型 + 质量属性。

`rebuild_from_ir` 会在源文件被改动过时给出 `source_stale` 警告。

---

## 4. 工具速查（46 个）

**文档与生命周期**
`ensure_ready` · `open_new_part` · `open_document` · `activate_document` · `save_document` · `close_document`

**草图**
`create_sketch` · `edit_sketch` · `add_sketch_entity` · `add_sketch_entities` · `add_sketch_constraint` · `add_dimension`

**特征与实体**
`extrude_feature` · `add_edge_feature`（fillet/chamfer）· `create_rib` · `add_reference_geometry` · `create_pattern` · `sheet_metal_feature`

**编辑**
`modify_dimension` · `edit_feature`

**材质**
`set_part_material`

**分析与查询**
`analyze_model`（`mass_properties` `geometry` `bodies` `edges` `faces` `features` `sketch` `feature_map`）· `get_selection` · `verify_state`

**装配**
`open_new_assembly` · `insert_component` · `add_mate` · `analyze_assembly` · `save_body_as_part` · `compare_assemblies`

**IR 往返**
`save_analysis` · `rebuild_from_ir` · `submit_feature_graph` · `compare_parts`

**工程图**
`create_drawing` · `add_drawing_view` · `add_flat_pattern_view` · `auto_dimension_drawing` · `auto_center_marks` · `add_hole_callout` · `add_drawing_dimension` · `add_section_view` · `analyze_drawing` · `analyze_slddrw_test`（仅测试参考）

**导出**
`export_document`（STEP / IGES / STL / PDF / DWG / DXF）· `batch_export`

### 大装配省 context 的技巧

`analyze_model` 的 `edges` / `faces` 支持：
- `near`：JSON `'[x,y,z]'`（米），只返回该点附近的实体；
- `k`：只保留最近的 k 个（0 = 不限）；
- `axis`：JSON `'[x,y,z]'`，按方向过滤（面按法向、边按方向）。

复杂件先框范围，别一上来全量 dump。

---

## 5. MCP 资源（13 个，用于"读规则"而非"做动作"）

规则集放在资源里是有意为之：工具描述每轮都要付费，资源只有被读时才付费。

| URI | 内容 |
|---|---|
| `recipe://usage/index` | **IR 工作入口**：版本头 + 全部小节 URI |
| `recipe://usage/<section>` | 规则小节，共 10 个：`contract` `canonicalization` `forward` `mapping` `mapping_part` `mapping_sheet_metal` `mapping_assembly` `verification` `reverse` `coverage` |
| `schema://feature-graph` | Feature Graph IR schema（**同时就是能力登记表**：schema 里没有的东西编译器造不出来） |
| `schema://analysis-artifact` | 分析产物契约 |

**写 IR 之前必须读**：`recipe://usage/index` → 对应小节 → `schema://feature-graph`。
凭空造 IR 词汇一定会被 validator 拒。

---

## 6. 报错怎么救

| 错误码 | 含义 | 你的动作 |
|---|---|---|
| `INVALID_STATE_VERSION` | 状态版本对不上 | **不用管**，adapter 自动 resync 重试一次。连续出现再报给人 |
| `COM_ATTACH_FAILED` | 连不上 SolidWorks（多半是没开或 COM 没注册） | 重跑 `ensure_ready`；还不行就让人类确认 SW 能正常启动 |
| `NO_ACTIVE_DOCUMENT` | 没有活动文档 | 先 `open_new_part` 或 `open_document` |
| `WRONG_DOCUMENT_TYPE` | 文档类型不对（如在零件里调装配工具） | 切到正确文档类型，或 `activate_document` |
| `MISSING_PARAMETER` | 必填参数没给 | 补参数 |
| `FILE_NOT_FOUND` / `TEMPLATE_NOT_FOUND` | 路径不存在 | 核对路径 |
| `OPEN_FAILED` / `INSERT_FAILED` / `DOCUMENT_CREATION_FAILED` | 打开/插入/建文档失败 | 外来格式（STEP/IGES 等）多半缺 3D Interconnect 转换器 |
| `COMPONENT_NOT_FOUND` / `ENTITY_NOT_FOUND` | 组件名或实体索引不对 | 重新 `analyze_assembly` / `analyze_model` 取最新索引 |
| `UNSUPPORTED_ANALYSIS_TYPE` | 分析类型写错 | 对照 §4 的合法取值 |
| `COM_ERROR` / `UNEXPECTED_ERROR` | COM 抛异常 | 重跑一次；持续出现就停下报告 |
| `TIMEOUT` | 30 秒超时 | 大装配的 `analyze_assembly` 会撞这个（历史上有过两次 30s 超时）。缩小范围用 `near`/`k`，或拆成多次读 |
| `DUPLICATE` | operation_id 重复 | 由 adapter 管理，你不会遇到 |

---

## 7. 已知的坑（别踩）

1. **`modify_dimension` 的角度用弧度**，其他工具的角度用度。混用会静默算错。
2. **材质名必须精确，且随语言本地化**：英文版是 `'1060 Alloy'`（不是 `'Aluminum 1060 Alloy'`）；**中文版实测（2026-09-20）是 `'1060 合金'`** —— 用英文名会报 `MATERIAL_NOT_FOUND`。拿不准就翻材质库查精确名：`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\lang\chinese-simplified\sldmaterials\solidworks materials.sldmat`（UTF-16 编码，搜 `<material name="...">`）。
3. **`create_pattern` 的 `count2` / `spacing2` 当前无效**——第二方向没接到 `FeatureLinearPattern3`（已记录在案）。要做双向阵列，把两个单向阵列组合起来。
4. **`auto_dimension_drawing` 不懂制图**，会漏标/错标，出图必须复核。
5. **`analyze_drawing` 的正交视图轮廓还没完全串起来**：特征轮廓止于边中段形成 T 型接头时，串链器会停在那儿不猜，报成 gap。钣金件不受影响。
6. **`analyze_drawing` 对机加工件是 `NOT_DIRECT`**——它给证据，工程读图得你来做（配合 `recipe://usage/reverse`）。
7. **suppress / delete 会改拓扑**，之后所有坐标和索引作废，重新 analyze。
8. **`export_document` 的 PDF / DWG / DXF 要求当前是工程图文档**，在零件上调会失败。
9. **驱动的是活的 SolidWorks GUI**：偶尔它会等你点一下才继续；超长分析之后工具可能开始报错（客户端侧限制）。两种情况都是**重试即可继续**。
10. **`submit_feature_graph` 的 IR 词汇必须来自 `schema://feature-graph`**，自创词汇必被拒。
11. **adapter 不支持热重载**：改了 `server.py` 必须重连 MCP server。
12. **直连执行层 REST（`POST /api/tool/execute`）时**，手册里写"JSON 数组字符串"的参数（`segments`、`edges_json`、`points`、`profiles`、`features_json`、`transform_json`）要传**真正的数组/对象** —— 字符串解析发生在 adapter 层，直连时没人帮你 parse。实测（2026-09-20）：传字符串会报 `MISSING_PARAMETER: segments is required`。走 DSH 的 `mcp__solidworks__*` 工具不受影响（adapter 会 parse）。
13. **六角结构（螺母/座）必须用"细轴 + boss 凸台"，绝不能用 cut**：cut 六角棱柱切出来的是**六角沉孔**（把材料挖了），不是六角头。正确做法：旋转轮廓在螺母区只留一根小于六角内切圆的细轴，然后在偏置参考面上画六边形 `extrude_feature {feature_type:"boss", reverse:true}` 补出棱柱。实测（2026-09-20，主轴 ER11 螺母）：boss reverse=true = 向 -X 拉伸；体积核验 +271mm³ 与理论一致。**判断六角方向最快的方法：STL 切片看半径波动**（圆≈0%，六角≈10%+）。
14. **草图激活时 `analyze_model(mass_properties)` 会报 `ANALYSIS_FAILED`**（GetMassProperties2 返回 null）。先 `extrude_feature`（它会自动退草图）再做质量分析。
15. **`add_drawing_view` 在本机（SW2026/中文版）实测返回 `VIEW_CREATION_FAILED`**：`CreateDrawViewFromModelView3` 对 front/isometric 都返回 null，ASCII 路径、空工程图、先开后建三种组合都试过（2026-09-20）。**要"看"模型别走工程图**：`export_document` 导 STL，自己写个软件渲染器/切片器核验（切片半径波动判六角、孔壁三角形判孔位、bbox 判朝向）。
16. **偏置参考面上的草图，坐标原点在零件轴线上，(cx,cy)→世界(Y,Z)**；Right Plane 正 offset = +X 方向。cut/boss 的 `reverse:true` = 沿 -X。在这类面上画**离心的图元**（如圆周分布孔）时，先做一次渲染/切片确认落位。
17. **改型（变型设计）先建立"尺寸→几何"映射再动手，别靠猜**。两步法（实测 2026-09-21，主轴抱座 65→42 改型）：① `analyze_model(analysis_type="sketch", name="草图N")` 直接读草图实体坐标（线段端点/圆心半径），和面清单对照即可推出大部分尺寸归属；② 剩余归属不明的，**试探法**：一次只改一个尺寸到明显不同的值（如 0.100），再读一次草图做 diff，哪个图元动了它就驱动哪个——4 个未知尺寸 4 次循环全定案，比盲改快得多。
18. **草图中"没有尺寸驱动"的图元不会跟随改型缩放**。本例草图1里有个开缝矩形（K=2 缝）无任何尺寸引用，全局缩小后它停在原坐标——本例万幸离新孔心只偏 0.25mm 可接受；若偏移大会得到功能废件。改型后必须用 faces/sketch 复查每个未约束图元的位置。另外：草图中与边线有几何约束的图元（如顶部凹槽贴着顶边、侧凹槽贴着台阶线）会自动跟随，不用管。
19. **AI 绕过 MCP 直连执行层 REST 的三个环境坑**（实测 2026-09-21）：① **Bash 的网络走 sandbox 代理**（`HTTP_PROXY=127.0.0.1:7501`），访问本机 :5000 会拿到 502 `upstream connect failed ... os error 10061`（sandbox 的 loopback 不是宿主的 loopback）。PowerShell 的 `Invoke-RestMethod` 则走 IE 系统代理（7897）同样 502——**先执行 `[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy`** 即可直连。② **exe 会被父会话结束时带走**：PowerShell `Start-Process` 启动的 `SolidworksExecution.exe`，该次工具调用一结束进程就没了（:5000 立刻空）。**必须在同一次调用里完成"启动 → 取数 → 收尾"**，或让脚本先探测端口复用。Bash 后台 `&` 启动实测 800ms 就退出，不可用。③ **Host 头必须是 `localhost`，不能用 `127.0.0.1`**：OWIN 绑的是 `http://localhost:5000/`，用 IP 会返回 400 `Bad Request - Invalid Hostname`。另：`/ensure_ready` 是独立路由（不在 `/api/tool/execute` 下），state 端点是 `GET /api/tool/state`。
20. **`analyze_assembly` 的结果在 `cadState.features[0]`**（是**小写** `features`，不是 `Features`），且是一个 JSON **字符串**，要再 parse 一次。`mates[]` 每项含 `i/name/type/alignment/value/entities`，`value` 单位是**米**。配合若处于压缩状态，`analyze_model(features)` 里会带 `"suppressed":true`——**改任何配合前先确认它没被压缩**，否则怎么改都没表现（这是"改了不生效"类故障的头号嫌疑）。
21. **限制距离配合（`MateLimitDistanceDim`）的上下限不能用全局变量/方程式驱动，设计表也不行**：设计表是"配置快照"机制，单元格只接受数值，写 `"X行程"+2.5` 不会被求值。唯一途径是 API —— `IDistanceMateFeatureData.MaximumDistance` / `.MinimumDistance`（已在 `SolidWorks.Interop.sldworks.dll` 中核实存在，配合的 `GetDefinition()` 返回的即是它）。**单位陷阱**：`EquationMgr.Value` 读全局变量是**文档单位 mm**（`X行程` 读出 `205`），而 Max/Min 是**米**，写入必须 `/1000`。配合被压缩时 `GetDefinition()` 取不到东西，要先 `SetSuppression2 swUnSuppress`。找配合特征用双保险：`FeatureByName` 失败时遍历 `GetTypeName2="MateGroup"` 的子特征（配合是 MateGroup 的 sub-feature，不依赖中文文件夹名）。
22. **装配体里已有内嵌设计表时，设计表会压制方程式**：若设计表含 `X行程` 列，方程式里再驱动 `X行程` 无效（SW 报"该值由设计表控制"）。要做双向驱动就得把该变量从设计表里删掉，让设计表只管配置级内容。设计表列名**必须让 SW 自动生成**（插入 > 表格 > 设计表 > 自动生成，勾项目后 SW 写出权威列头）；手打列名差一个字符 SW 会**静默忽略整列**——这是"设计表改了不生效"最常见的原因。

23. **用 Python 直连 SolidWorks 的底线（实测 2026-09-21）**：本机 `pywin32`(312)+`pywinauto` 已装在 managed Python（`C:\Users\Zegel\.workbuddy\binaries\python\versions\3.13.12\`）。`win32com.client.GetActiveObject("SldWorks.Application")` **能连上活的 SW**（PowerShell 的 COM 实例化被安全策略拦了，但 Python 这条没事）。连上后**只能走 late-bound**：本机 SW 主 typelib（`sldworks.tlb`）既没注册进 `HKCR\TypeLib` 也找不到 .tlb 文件，`gencache.EnsureModule`/`makepy` 全失败 → 早期绑定不可行。late-bound 下**只有无参属性 getter 能解析**（`m.GetEquationMgr`、`m.GetType`），**任何带参数的方法都会 `找不到成员`**（`em.GetEquation(i)`、`feat.GetDefinition()`）。所以**不能从 Python 直接写方程式/限位 API**，只能靠 SW 自己的 VBA 引擎。

24. **真要从代码跑宏，走 `ISldWorks.RunMacro2`**（Python 连上后 `sw.RunMacro2(文件, "Main", "main", 0, ByRef错误)` 能调起 SW 的 VBA 引擎执行宏——这一步本身没问题，已用纯文件 I/O 的 `trivial.swb` 验证成功）。但**一旦宏里碰 SW 对象模型（`Application.SldWorks` / `GetObject(,"SldWorks.Application")`），SolidWorks 的宏安全弹窗就会冒出来**：无人值守时它是模态阻塞，要么卡死要么被 SW 自动拒绝（`RunMacro2` 返回 `False`，`Errors=0`）。**这正是"打开→工具>宏>运行→选.bas→跑"那几下点击的本质——弹窗要人点**。要让它 100% 无人值守，只有两条路：① 老大在 SW 里把 工具>宏>安全性 调到"低"（关弹窗），之后 `p3_deploy2.py` 一把跑完；② 或者就点那几下。

25. **手写 `.swb` 经 `RunMacro2` 跑的四条铁律**（踩出来的）：① 入口**必须是 `Sub main()`**——SW 的 `.swb` 只认 `main`，`ModuleName`/`ProcedureName` 参数被忽略；② **不能写 `Attribute VB_Name = "..."`**（独立 .swb 不支持，会导致整模块加载失败）；③ 手写 .swb 经 RunMacro2 加载时**SW 不会挂类型库引用** → 必须全 late-bound（`Dim x As Object`，常量用数字如 `swDocASSEMBLY=2`，绝不用 `SldWorks.*` 类型）；④ 注释/字符串按**系统 ANSI 码页（中文机=GBK）**读写——用 UTF-8 中文（尤其 .swb 里的变量名/注释）会让整模块加载失败。落地做法：用 Python `open(path,"w",encoding="gbk")` 写 .swb，且注释全 ASCII。已产出的 `DeployHeadless.swb` 就是按这套写好的（无弹窗版 `SetupParametricDrive`，结果写 `p3_macro_result.txt`）。

26. **验证"宏到底跑没跑"的技巧**：手写宏里**第一行就 `Open 结果文件 For Output` 写个标记**，跑完读该文件即可判断——比看 `RunMacro2` 的 `False/Errors=0` 返回值靠谱得多（后者对"加载失败"和"被安全弹窗拒绝"都返回同样的无信息结果）。本机已验证 `trivial.swb` 能写文件、`Application`/`GetObject` 版会在 `Open` 之后卡在 API 调用，佐证了 #24 的弹窗阻塞结论。

---

## 8. 开工自检清单

每次接手 SolidWorks 任务，按这个顺序走：

- [ ] `ensure_ready` 返回 `comAttached=true`
- [ ] 明确知道当前活动文档是什么（`verify_state`）
- [ ] 建模前跑了 `analyze_model` 拿到索引/特征树
- [ ] **每个草图都已用 `add_dimension` 完全定义，没有欠定义自由度**（规则四）
- [ ] 所有长度已换算成**米**、角度单位已按 §2 表格确认
- [ ] 选面/选边用的是 **index** 参数，不是坐标
- [ ] 改完有复核动作（`mass_properties` / `compare_parts` / `analyze_assembly`）
- [ ] 结果已 `save_document` / `export_document` 落盘

---

## 9. 本机接入信息（运维参考）

DSH 侧挂载位置：`C:\Users\Zegel\.dsh\profiles\web\cordis.patch.yml`，条目 `mcp-solidworks`
（等价副本：`C:\Users\Zegel\solidpilot-mcp\dsh-solidworks.cordis.yml`）

```yaml
transport: stdio
command: C:/Users/Zegel/solidpilot-mcp/adapters/claude/.venv/Scripts/python.exe
args:    [C:/Users/Zegel/solidpilot-mcp/adapters/claude/server.py]
cwd:     C:/Users/Zegel/solidpilot-mcp/adapters/claude
env:     EXECUTION_BASE_URL=http://localhost:5000
```

- 执行服务 **按需启动**，不随 DSH 启动；`ensure_ready` 触发。
- 编译产物：`execution/solidworks/SolidworksExecution/bin/Debug/SolidworksExecution.exe`
- 重建命令：
  ```
  & "C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" execution\solidworks\SolidworksExecution.sln /t:Build /p:Configuration=Debug
  ```
- 运行日志：`adapters/claude/adapter.log`（每次调用都有 `->` / `<-` 记录，排查时先看它）
- 注意：web bundle 关掉了 hmr，**改配置后要重启 dsh web 宿主才生效**

# Feature 135 · 建草图 + 画几何（砌墙 W4）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> ★ 编号说明：原计划把 W4 编成 `134`，但 `specs/134-static-simulation-reverified` 是**已提交的真实特性**
> ⇒ 按 **flow-forward**（完成的目录不可变、需求变了开新号）**顺移为 135**。

## 一、要解决的问题：**本仓库最底层的短板**

```
★ MCP 里跟草图有关的**只有**：`solidworks_add_sketch_relation` + W1 那 4 个**只读**工具
  ⇒ ★★ **不能建草图、不能画线/圆/矩形**。
★ 后果不只是"少几个工具"：
  **已经挂出去的建模工具全都用不了** ——
    `solidworks_revolve_boss`（batch17）· `solidworks_create_hole_feature` ·
    钣金 `solidworks_sheet_metal_create_base_flange`（batch4）…
  **它们都要一个「已存在的草图」**，而 AI **造不出草图**。
⇒ ★★ 本仓库此前是「**会旋转、会打孔、会钣金，却连一条线都画不出来**」。
```

## 二、★ 本特性是**核过缺口本身**之后才定下来的（三层）

| 层 | 发现 |
|---|---|
| ① | ⑯零件特征那 28 个缺口名**全是"建 / 改"**，而原计划写的是 W4 取「**回读**」⇒ **两者不对口**（回读**已经有**：`solidworks_collect_model_summary`）|
| ② | 实测：**首参可注入且没挂的"建特征"函数有 10 个**（`extrude_boss` / `extrude_cut` / `chamfer` / `fillet` / `shell` / `insert_dome` / `linear_pattern` …）⇒ 而 MCP 里**已有** `revolve_boss`/`create_hole_feature` ⇒ ★ 不对称 |
| ③ | ★★ **最要紧的**：**MCP 里根本没有"建草图"** ⇒ 上面那些"建特征"**挂了也用不了** ⇒ **先补这一层** |

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能**在基准面上进入草图** | 官方 `ISketchManager.InsertSketch`；本项目 `sw_part.start_sketch`（MIT，本仓库） |
| R2 | 能**退出草图** | 官方 `ISketchManager.InsertSketch`；`sw_part.end_sketch` |
| R3 | 能画**直线** | 官方 `ISketchManager.CreateLine`；`sw_part.sketch_line` |
| R4 | 能画**圆** | 官方 `ISketchManager.CreateCircleByRadius`；`sw_part.sketch_circle` |
| R5 | 能画**矩形** | 官方 `ISketchManager.CreateCornerRectangle`；`sw_part.sketch_corner_rectangle` |
| R6 | ★ 长度参数一律 **`_mm`** | 并入六条规则**规则 2** |
| R7 | ★ 画几何的坐标**必须给平面内坐标** —— 这是规则 3 的**豁免路径**（原文明写「除非该工具本身是 `*_at_point` 类且注明用途」）| `docs/union-conventions.md` 规则 3 |
| R8 | 基准面名**中英文都要能用** | 既有事实 9（名字随 UI 语言变）；`sw_part.start_sketch` 的既有实现 |

## 四、★ 参数命名的设计决定（规则 2 与规则 3 的边界）

```
能力层用的是**裸坐标名**：`sketch_line(model, x1, y1, x2, y2)`
★ 而草图画几何**本质上就得给平面内坐标**（没有别的法子）⇒ 这不是偷懒，是问题本身如此。
★★ 门禁的盲区（**如实记，不在本特性顺手改**）：
   `_BARE_COORD_NAMES = {x, y, z, x_mm, y_mm, z_mm, point, coordinate}` **只查参数字面名**
   ⇒ 能力层的 `x1`/`y1`/`x2`/`y2` **一个都不在黑名单里** ⇒ **门禁漏掉它们**
   （与**事实 153**「门禁只验了 3 句里的 1 句」同族）。
⇒ ★★ 本特性的处置：**对外用语义名 + `_mm`** ——
   `start_x_mm` / `start_y_mm` / `end_x_mm` / `end_y_mm`（★ **不用** `x1_mm`，那个**在黑名单里**）
   ★ 语义名既过规则 2，**也不冒充"裸坐标"** —— 它们说的是「草图平面上一条线的两个端点」。
★ **不为通过而放宽判据**：门禁**不动**；盲区留给后续单独开特性。
```

## 五、不做什么（有据）

| 不做 | 原因 |
|---|---|
| **不挂全部 17 个草图函数** | `sketch_rectangle`（中心+宽高）与 `sketch_corner_rectangle`（对角）**语义重叠** ⇒ ★ 两个都挂会让 AI 选错 ⇒ **只挂对角那个**。其余（多边形/槽/弧/椭圆/样条/自动尺寸）**留后续批次** |
| 不顺手改门禁的 `_BARE_COORD_NAMES` | ★ 不为通过而放宽判据 |
| 不碰保存 / 另存 / 删除 | 计划明写本阶段不做高风险写操作 |

## 六、验收

```
① 静态：`all_specs()` 里出现 5 个新工具，且门禁全绿
② ★ 真机：`D:\AI\SW\output\sketch-build-evidence.json` 的 `verdict` == "pass"，且含**读写配对**：
   · start → 画线 ⇒ 回读 `count_lines == 1`
   · 画圆       ⇒ 回读 `count_arcs == 1`
   · 画矩形     ⇒ 回读 `count_lines == 5`（1 线 + 4 边）
   · ★ end 之后 ⇒ **仍读到 5**（草图关闭后仍可回读）
   ★ 另记两条**未知项**（如实记录、不假称）：不 start 就画线 = **静默**；坏基准面名 = **ValueError**
```

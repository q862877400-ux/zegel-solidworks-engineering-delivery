# S3 T008 真机核查 · 交付板件**零个驱动尺寸、草图欠约束**

**日期**: 2026-10-25

**探针**: `tools/probe_s3_dimensions_exist.py`

**依据**: `docs/ENGINEERING-PATH.md` 第六节 S3 第 1 条

> 用已有板/孔组路径改成**尺寸与关系驱动**的方法：位置、方向、大小完整约束；
> **不得全固定，不得仅用初始坐标画对**。

---

## 一、结论（真机实测）

现在这条路建出来的板件，**一条驱动尺寸都没有**，且**草图是欠约束的**。

证据（`output/s3-dimensions-exist.json` 逐字）：

```json
{
  "sketch_status_before_fix": 2,
  "dimension_count": 0,
  "dimensions": [],
  "has_driving_dimension": false,
  "features": ["前视基准面","上视基准面","右视基准面","原点","Tables","草图1","凸台-拉伸1"],
  "conclusion": "★★ 一个尺寸都没有 ⇒ 交付板件不是尺寸驱动，T011「改板宽」无从下手"
}
```

两个读数都很关键：

| 读数 | 值 | 含义 |
|---|---|---|
| `GetConstrainedStatus()` | **2** | `swUnderConstrained` —— 草图**欠约束**（E1 直接判 fail） |
| 驱动尺寸数 | **0** | 没有任何可改的参数 |

## 二、为什么（不是实现 bug，是方法本身如此）

`tools/run_stage2_plate.py:build_plan()` 建板用的是**坐标参数**：

```
sketch_add_rectangle(x1_mm=0, y1_mm=0, x2_mm=w, y2_mm=h)              ← 坐标
sketch_add_circle(center_x_mm=hx, center_y_mm=hy, radius_mm=dia/2)     ← 坐标
```

⇒ 每一轮都用**新的数字重画一遍**，模型里不留下任何尺寸。
   这正是 S3 第 1 条点名的「**仅用初始坐标画对**」。

## 三、两个直接后果

### 后果 1：T011「改板宽 100→120」**做不到**

T011 要求「在**已交付件副本**上改板宽 100→120，孔位联动」。

而模型里**没有宽度尺寸**可改 ⇒ 无从下手。

`tools/run_stage2_plate.py:run_change()` 现在做的是
`sw_connect.new_document()` 后按新参数**重新生成**（`R-engineering-path.md` R-10 已记为替代品）。
那不是「改已交付件」，是「另做一件」。

### 后果 2：E1 现在就是不合格

草图读数 2（欠约束）⇒ 按 `judge_sketch_constraint` 直接判 **fail**。

⇒ 不是「将来要改」，是**当前交付物不满足 E1**。

## 四、所以顺序要调整：T008 必须在 T011 之前

| 原任务号 | 内容 | 依赖 |
|---|---|---|
| **T008** | 板件改为尺寸与关系驱动 | ✅ 可独立做（改生成路径） |
| T009 ① ② ③ | 三源互证 + 采集器 + 语义选择器 | ✅ 已完成 |
| T009 ④ ⑤ | 三处 `index:0` 换语义选择器 | ⏸ 需先定「倒哪条边」 |
| **T011** | 已交付件副本改板宽 | ❌ **依赖 T008**（没有尺寸就无从改） |
| T010 | 孔型/孔位逐项回读 | ✅ 判据已建 |
| T012 | E1–E3 三态全绿 | ❌ 依赖 T008 |
| T013 | E5 标注小验证 | 独立 |

⇒ **T008 是 S3 的真正瓶颈**。T011/T012 都排在它后面。

## 五、T008 要做什么（做法已清楚）

最小改动：把板外形的两个方向改成**草图驱动尺寸**，孔位用尺寸或约束表达。

需要的官方能力（都已在仓库里用过，不需新查）：

| 要什么 | 用什么 | 依据 |
|---|---|---|
| 加水平尺寸 | `IModelDoc2.AddHorizontalDimension2(X, Y, Z)` | `scripts/sw_sketch_dimensions.add_horizontal_dimension`（既有） |
| 加竖直尺寸 | 同上（`AddVerticalDimension2`） | `scripts/sw_sketch_dimensions.add_vertical_dimension`（既有） |
| 改尺寸值 | `model.Parameter(name)` + `SetSystemValue3` | `scripts/sw_document_data.update_dimension_mm`（既有，R-02 记的「本已可做」） |
| 全约束 | `sgFIXED` 之外的关系 | `scripts/sw_sketch_dimensions.fully_define_sketch`（既有） |

★ 也就是说：**能力都已具备，缺的是把生成路径改成用它。**

## 六、本轮没做 T008 的原因（如实）

T008 要改 `build_plan()` 的步骤序列（从「坐标参数」改成「画 + 加尺寸 + 改值」），
这会影响：

- `tools/run_stage2_plate.py` 的 `run_case` / `run_change`
- `specs/317-stage2-real-holes/acceptance.md` 的历史结论
- 阶段 322 的 `FinalDod` 判定（案例与证据）

⇒ 属「改共享生成路径」，需要单独一轮做，并重新跑真机验收。
**本轮只交付核查结论**，把「现状是零尺寸、欠约束」这件事钉成证据。

## 七、可重跑

```powershell
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_dimensions_exist.py
```

探针只读：建临时零件、读数、收尾关掉**自己开的**文档。

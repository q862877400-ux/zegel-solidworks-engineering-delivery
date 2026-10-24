# S3 T011 · 在已交付件副本上改板宽 —— 真机验成

**日期**: 2026-10-25

**探针**: `tools/probe_t011_edit_delivered_plate.py`

**对应任务**: `specs/350-first-part-delivery/tasks.md` T011

**依据**: `docs/ENGINEERING-PATH.md` 第六节 S3 第 4 条

> 在同一个**交付件副本**上改已有主参数，检查下游联动、特征错误和引用；
> 保存重开、配置切换后复查。

---

## 一、结论

**成立。** 在已交付件的副本上把板宽从 100 mm 改成 120 mm：

```
① 复制交付件副本 → 板1_rev-1_copy.SLDPRT
③ 打开时：尺寸 1 个 · 包围盒 100.0 · 错误 0
④ 改宽度 → 120mm：ok
⑤ 改后：包围盒 X = 120.0 mm · 错误 0
⑥ 保存重开后：包围盒 X = 120.0 mm

★ 在交付件副本上改板宽成功：包围盒 X 100.0 → 120.0 → 120.0 mm，保存重开仍成立
```

| 判据 | 结果 |
|---|---|
| 交付件有驱动尺寸 | ✅ 1 个 |
| 改主参数生效 | ✅ 包围盒 100.0 → 120.0 mm |
| 无特征错误 | ✅ 错误数 0 |
| 保存真的落盘 | ✅ 文件 sha256 变了、大小变了 |
| 保存重开仍成立 | ✅ 重开后仍是 120.0 mm |

## 二、为什么这条重要

`tools/run_stage2_plate.py` 的 `run_change()` 现在是 `new_document()` 后按新参数
**重新生成**（`R-engineering-path.md` R-10 已记为「替代品」）。那不叫改已交付件。

本探针走的是**另一条路**：打开既有文件 → 改既有驱动尺寸 → 重建 → 保存 → 重开。
这才是 E2「参数化可重建」真正要求的东西。

## 三、前置：生成路径补上了「加驱动尺寸」这一步

第 7 轮真机量到：按原步骤建出的板件**零个驱动尺寸**、草图状态 2（欠约束）。
⇒ 本轮在**两处**补上 `auto_dimension_sketch` 步骤（时点必须在 `sketch_end` 之前）：

| 落点 | 说明 |
|---|---|
| `scripts/engineering/compiler.py` 的 `METHOD_LIBRARY["plate"]` | 方法包的正确定义处；`postconditions` 也加了「草图有驱动尺寸」 |
| `tools/run_stage2_plate.py` 的 `build_plan()` | 该工具手写步骤序列，与方法库是两份，必须同步 |

补完之后真机跑 `--case 1`：

```
用例 1：compile=True auth=True exec=True 孔=4/4 bbox=[100.0, 60.0, 20.0]
        体积=117738.053/117738.053 pass=True
```

⇒ 加这一步**没有破坏**板件生成（尺寸、孔数、体积全对）。

## 四、★★ 我差点记下一个错的结论

第一次跑本探针时，读到「改值生效但**保存重开后变回 100**」，
我一度准备记成「`save_document` 报成功却不落盘」的缺陷。

继续测下去才发现真因是**测量被沙盒改了路径**：

```
文档实际路径：...\output\sandbox\inputs\板1_rev-1_copy__7.SLDPRT
```

`tools/sw_guard.py` 会把输入文件复制到 `output/sandbox/inputs/` 下再交给子进程。
⇒ SolidWorks 打开的是**沙盒副本**，保存也写在那里；
  而我「重开」时又传了**自己那份原始副本**的路径 ⇒ 又拿到一份新沙盒副本（`__N`）
  ⇒ 读到的是**原始内容**，不是保存结果。

**修法**：重开时用 `IModelDoc2.GetPathName()` 读到的**实际路径**，不是我自己传的路径。

修完再跑：`bbox_x: 100.0 → 120.0 → 120.0`、`persisted_after_reopen: True`、
`sha_changed: True`（文件内容真的变了）。

★ 教训：**在沙盒里做「保存 + 重开」这类跨进程验证时，必须用文档自己报告的实际路径，
  不能用调用方传进去的路径**。否则读到的可能是另一份文件。

## 五、只读纪律

| 项 | 做法 |
|---|---|
| 交付件 `output/stage2/板1_rev-1.SLDPRT` | **不动**（跑完核对：76.50 KB、mtime 未变） |
| 操作对象 | 复制一份到 `output/t011-copy/` 再改 |
| 弹窗 | `CommandInProgress = True`（铁律 2），收尾恢复 |
| 文档 | 收尾只关**自己开的** |

## 六、还没验的（如实）

| 项 | 为什么 |
|---|---|
| **孔位联动** | 本轮验的是「板变宽」，孔位是否随之移动**没验** |
| 配置切换后复查 | S3 第 4 条要求，本轮未做 |
| 引用/父子依赖检查 | 本轮只看了「特征错误数 0」，没逐条核引用 |
| 高度方向是否参数化 | 真机上只找到 **1** 个尺寸（宽度），高度不是参数 |

★ 第 1 项是 S3 的下一个关键问题：**板宽变了，四个孔有没有跟着走**。
  这需要先把孔位也用尺寸/约束表达（当前是坐标画圆），否则孔不会联动。

## 七、可重跑

```powershell
# 前置：先生成交付件（会写 output/stage2/）
python -B tools\sw_guard.py --timeout 420 -- python tools\run_stage2_plate.py --case 1
# 本探针
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_t011_edit_delivered_plate.py
```

证据：`output/t011-edit-delivered-plate.json`（`output/` 在 `.gitignore` 里，
关键读数已抄进本文件）。

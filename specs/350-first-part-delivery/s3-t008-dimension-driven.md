# S3 T008 真机验证 · 尺寸驱动可行，但 `update_dimension_mm` 有单位缺陷

**日期**: 2026-10-25

**探针**: `tools/probe_s3_t008_dimension_driven.py`

**对应任务**: `specs/350-first-part-delivery/tasks.md` T008

---

## 一、三句话结论

1. **可行性已证**：`ISketch.AutoDimension2(1, 1, -1, 1, -1)` 能给板件加上**驱动尺寸**，
   草图从读数 **2（欠约束）** 变成 **3（完全定义）**。
2. **改尺寸这条路有缺陷**：`update_dimension_mm` 把 120 mm 写成了放大约 **1000 倍**的值
   （`SystemValue` `0.1` → `120.0`，比例 **1200**，期望 **0.12**）。
3. **所以「改板宽 → 孔位联动」这一步还没验成** —— 不是做不到，是**改值这一步的换算错**。

## 二、读数（真机实测）

### ① 现状（上一轮已记，本轮复核）

| 项 | 值 |
|---|---|
| `GetConstrainedStatus()` | **2**（`swUnderConstrained`） |
| 驱动尺寸数 | **0** |

### ② 加尺寸：两条入口，一条死一条通

| 入口 | 结果 |
|---|---|
| ❌ `IModelDoc2.AddHorizontalDimension2` | **把 SolidWorks 崩掉**（`com_error: RPC 服务器不可用`） |
| ✅ `ISketch.AutoDimension2(1, 1, -1, 1, -1)` | 回 `0`（success），建成 `D1@草图1` = 100 mm，`GetConstrainedStatus` **2 → 3** |
| ❌ `ISketchManager.FullyDefineSketch`（10 参） | 第 6 参（`HorizontalDatumDisp`，`object`）报 `类型不匹配` |

`AutoDimension2` 的参数按官方枚举取值：

| 参数 | 值 | 枚举 |
|---|---:|---|
| `EntitiesToDimension` | 1 | `swAutodimEntitiesAll` |
| `HorizontalScheme` | 1 | `swAutodimSchemeBaseline` |
| `HorizontalPlacement` | -1 | 既有证据用的值 |
| `VerticalScheme` | 1 | 同上 |
| `VerticalPlacement` | -1 | 同上 |

### ③ 改尺寸：单位放大 1000 倍

请求把 `D1@草图1` 从 **100 mm** 改成 **120 mm**（×1.2）：

| 读数 | 值 |
|---|---|
| `IDimension.SystemValue` **改前** | `0.1`（= 100 mm，米制，正确） |
| `IDimension.SystemValue` **改后** | **`120.0`**（应为 `0.12`） |
| 期望值 | `0.12` |
| 比例 | **1200**（期望 1.2） |
| `update_dimension_mm` 自报 | `success: True`，`after_mm: 120.0` |

★★ **它的自我报告不能当证据**：正因为 `after_mm` 与请求一致，
  才掩盖了 `SystemValue` 被放大 1000 倍这件事。

## 三、★ 我这一轮犯的一个流程错误

`docs/dead-ends.md` **早就记着** `AddDimension2` 是死路（轮 400 / 153 / 154 / 155，
6 种选法全败）。而我从 `AddHorizontalDimension2` 开始试，
**花了 3 次真机运行才发现它会把 SolidWorks 崩掉**。

`AGENTS.md` 第十三节逐字：

> 动手核一条路之前：先扫「已走死的路」`docs/dead-ends.md`

⇒ 我这轮没扫就动手，是流程错误。教训：**查"某能力是否可行"之前先扫 dead-ends。**

## 四、这两个缺陷的性质

### 缺陷 1：`update_dimension_mm` 的单位换算

`scripts/sw_document_data.py` 的实现（逐字）：

```python
_scale = _document_length_unit_scale(model)
...
dimension.SetSystemValue3(float(value_mm) / _scale, ...)
```

它自己在上方注释里写：

> ★★★★ 2026-10-04（接手轮）**修正换算 —— 两处一起改**：
> **病灶**：`_dimension_value_mm` 硬编码 `× 1000`、而这里硬编码 `/ 1000` ⇒
> **两个相反方向的错、互相掩盖**（读回来的值**看起来对**）

⇒ 本轮实测表明：**同类错误仍在**，只是换了位置 ——
   `SetSystemValue3` 收到的是 `120.0`，而米制下应为 `0.12`。

**⚠ 未查明**：是 `_document_length_unit_scale` 求错（回了 1 而不是 1000），
还是 `SetSystemValue3` 在本机吃米制。两种解释**都未被证据排除**。

### 缺陷 2：`AddHorizontalDimension2` 崩进程

比 dead-ends 记的更重：那几轮记的是「回 None」，本轮是**进程崩**。
⇒ dead-ends 该补这条症状。

## 五、还没验成的（如实）

「改板宽 100 → 120 后**孔位联动**」**没验成**，因为：

| 原因 | 细节 |
|---|---|
| 改值换算错 | 见上，`SystemValue` 放大 1000 倍 |
| 没有独立读数能证实几何变宽 | `IPartDoc.GetBodies2(True)` 报「非选择性的参数」；`IModelDocExtension.GetBox` 不存在 |
| 尺寸遍历只拿到 1 个 | `AutoDimension2` 只加了宽度（100 mm）；高度没加 ⇒ 改宽度后「孔位联动」无从观察 |

★ 所以本节**不写**「尺寸驱动已验成」。写的是：
  **加尺寸这一步验成了；改尺寸这一步因单位缺陷未验成。**

## 六、下一步（按依赖顺序）

| # | 做什么 | 前置 |
|---|---|---|
| 1 | 查明 `SetSystemValue3` 到底吃米制还是文档单位（**测量，不是猜**） | 无 |
| 2 | 按查明结果修 `update_dimension_mm` 的换算 | 1 |
| 3 | 查明 `GetSystemValue3` 的正确调用形状（本轮传 `(0, None)` 回 `null`） | 无 |
| 4 | 找到可用的包围盒读法（三条都不通：`GetBodies2` / `Extension.GetBox` / `IBody2.GetBodyBox`） | 无 |
| 5 | 让 `AutoDimension2` 同时加高度尺寸（或查明为何只加了 1 个） | 无 |
| 6 | 孔位也用尺寸/约束表达，然后验「改板宽 → 孔位联动」 | 2 + 5 |
| 7 | 把 `build_plan()` 从坐标参数改成「画 + 加尺寸」 | 6 |

★ 第 1、3、4 项都是**测量**，不需要决策，可以下一轮直接做。

## 七、可重跑

```powershell
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_dimensions_exist.py
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_t008_dimension_driven.py
```

★ 探针已设 `sw.CommandInProgress = True`（铁律 2），收尾恢复并只关**自己开的**文档。

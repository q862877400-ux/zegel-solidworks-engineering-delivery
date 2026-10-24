# S3 T008 真机验证 · 尺寸驱动已验成，`update_dimension_mm` 单位缺陷已修

**日期**: 2026-10-25

**探针**: `tools/probe_s3_dimensions_exist.py` · `tools/probe_s3_dimension_units.py` ·
`tools/probe_s3_t008_dimension_driven.py`

**对应任务**: `specs/350-first-part-delivery/tasks.md` T008

---

## 一、结论

**尺寸驱动这条路走通了，而且改尺寸真的改了几何。**

| 判据 | 结果 |
|---|---|
| 原状草图欠约束 | ✅ `GetConstrainedStatus()` = 2 |
| 能加上驱动尺寸 | ✅ `AutoDimension2(1,1,-1,1,-1)` 建成 `D1@草图1` |
| 加完变全约束 | ✅ 读数 **2 → 3** |
| 改尺寸能改几何 | ✅ 包围盒 X 跨度 **100.0 → 120.0 mm** |
| 改动有独立读数证实 | ✅ `SystemValue` `0.1 → 0.12`（正好 ×1.2） |

探针结论逐字：

```
★ 板件可做成尺寸驱动：用 AutoDimension2 加了 1 个尺寸，约束状态 3；
  改宽度后 X 跨度 100.0 → 120.0 mm
```

## 二、三个入口：一条死、一条通、一条没查明

| 入口 | 结果 |
|---|---|
| ❌ `IModelDoc2.AddHorizontalDimension2` | **不可调用** —— 直接崩进程（`RPC 服务器不可用`，需重启） |
| ✅ `ISketch.AutoDimension2(1, 1, -1, 1, -1)` | 回 `0`（success），建成驱动尺寸，草图转全约束 |
| ❌ `ISketchManager.FullyDefineSketch`（官方 10 参） | 第 6 参（`HorizontalDatumDisp`，`object`）报「类型不匹配」 |

`AutoDimension2` 参数按官方枚举取值：

| 参数 | 值 | 枚举 |
|---|---:|---|
| `EntitiesToDimension` | 1 | `swAutodimEntitiesAll` |
| `HorizontalScheme` | 1 | `swAutodimSchemeBaseline` |
| `HorizontalPlacement` | -1 | 既有证据用的值 |
| `VerticalScheme` / `VerticalPlacement` | 1 / -1 | 同上 |

## 三、★ 修掉的那个真缺陷：`update_dimension_mm` 的单位

### 原来错在哪

`scripts/sw_document_data.py` 原按 `GetUnits()` 推倍数：

- 毫米文档（`swLengthUnit_e = 0`）⇒ 倍数 **1.0**
- **读**：`GetSystemValue3` 回的 `0.1`（米）`× 1.0` = `0.1` ⇒ 100 mm 的尺寸读成 `0.1`
- **写**：`SetSystemValue3(120 / 1.0)` = `120` ⇒ 当成 **120 米**

读写两侧都差 **1000 倍**，而测试里的假文档特意声明自己是米文档（倍数 1000），
两边相消 ⇒ **测试全绿，真实默认（毫米）从没被测过**。

### 怎么定案的

在**毫米**文档上做几何测量（`tools/probe_s3_dimension_units.py`）：

```
文档：GetUnits() = [0, 1, 8, 2, 0]        ← swLengthUnit_e = 0 = swMM
一条 100 mm 宽的驱动尺寸：SystemValue = 0.1 · GetSystemValue3(1, None) = [0.1]
SetSystemValue3(0.15, 1, None) → 返回 0（success）
  改后：SystemValue = 0.15 · GetSystemValue3 = [0.15]
  ★ 包围盒 X 跨度：100.0 mm → 150.0 mm     ← 几何证实
```

⇒ 写 `0.15` 得到 **150 mm** ⇒ 单位是**米**，与文档单位无关。
官方 `SetSystemValue3.md` 逐字也是这么写的：「system units (**meters**)」。

### 修法

1. 新增常量 `SYSTEM_UNIT_MM = 1000.0`（并注明它是**定义**，不是从文档探出来的）
2. `_dimension_value_mm`：`return float(raw) * SYSTEM_UNIT_MM`
3. `update_dimension_mm`：`SetSystemValue3(float(value_mm) / SYSTEM_UNIT_MM, ...)`
4. `_document_length_unit_scale` **保留**（另有测试直接测它），但**本路径不再用**
5. 新增 `tests/test_system_value_units.py`（6 条）钉住这条契约，含
   「毫米 / 厘米 / 米三种文档单位读数必须一致」与「不再把文档单位接回系统值换算」

### 修完的读数

```
SystemValue:        0.1  →  0.12     （正好 ×1.2）
update_width:       before_mm 100.0 → after_mm 120.0
包围盒 X 跨度:       100.0 mm → 120.0 mm
unit_defect_suspected: false
```

## 四、顺带查清的：可用的包围盒读法

```
IPartDoc.GetBodies2(swSolidBody=0, BVisibleOnly=True) → IBody2.GetBodyBox()
⇒ 6 个 double，单位米
```

三条走不通的旧写法（别再试）：

| 写法 | 症状 |
|---|---|
| `GetBodies2(True)` | 只传一个参数 ⇒ 「非选择性的参数」（官方要**两个必填**） |
| `IModelDocExtension.GetBox` | **不存在** |
| 只有草图没实体时读 | `GetBodies2` 回 `None` ⇒ **要先拉伸** |

## 五、我这一轮的流程错误

`docs/dead-ends.md` **早就记着** `AddDimension2` 是死路（轮 400 / 153 / 154 / 155，
6 种选法全败）。我没先扫就动手，**花了 3 次真机运行**才发现 `AddHorizontalDimension2`
会把 SolidWorks 崩掉。

`AGENTS.md` 第十三节逐字要求「动手核一条路之前：先扫『已走死的路』」。
⇒ 已把「不可调用（崩进程）」补进 `capabilities.yaml` 并重生成 `dead-ends.md`（75 → 76 条）。

## 六、还没做的

| # | 事情 | 为什么 |
|---|---|---|
| 1 | `AutoDimension2` 只加了 **1** 个尺寸（宽度），高度没加 | **未查明**为何只加一个；全约束靠什么达成也未查明 |
| 2 | 孔位也用尺寸/约束表达 | 依赖 `build_plan()` 改造 |
| 3 | 把 `build_plan()` 从坐标参数改成「画 + 加尺寸」 | 依赖 2，且会牵动 `run_case` / `run_change` / `specs/317` / 阶段 322 |
| 4 | 「改板宽 → **孔位联动**」 | 依赖 2；本轮验的是「改板宽 → 板变宽」，**孔位联动还没验** |

★ 第 1 项是 S3 下一步最该查的：**只有 1 个尺寸却能全约束**，说明还有关系在起作用，
  那意味着「尺寸驱动」可能不完整 —— 需要单独量。

## 七、一个尚未查清的疑点

`extrude_boss(model, name, 20.0)` 建出的实体，`GetBodyBox` 原始 z 跨度是 **20 米**
（`z = -20 → 0`），而 `sketch_corner_rectangle(0,0,100,60)` 建出的 X 跨度是 **100 mm**。

⇒ **同一个仓库里两个生成函数的单位口径似乎不一致**（一个按米、一个按毫米）。
   本轮**未逐个体查清**，只记录现象。这条会影响 T008 后续与 S4 的装配尺寸。

## 八、可重跑

```powershell
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_dimensions_exist.py
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_dimension_units.py
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_t008_dimension_driven.py
```

★ 三个探针都设 `sw.CommandInProgress = True`（铁律 2），收尾恢复并只关**自己开的**文档。
★ 共用的 `try_call` 在 `scripts/sw_connect.py`（同一段 `try/except` 不在多处各写一份）。

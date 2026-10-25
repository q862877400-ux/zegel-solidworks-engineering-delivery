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

## 九、★ 查「只加 1 个尺寸却全约束」时，抓到自己判据的一个洞

### 量到了什么

	ools/probe_s3_autodim_why_fully_defined.py（真机）：

| 时点 | 状态 | 尺寸（路线一 GetNext2） | 尺寸（路线二 EnumDisplayDimensions） | 关系数 |
|---|---|---|---|---|
| 矩形 100×60 | **2** | 0 | 取不到 | 0 |
| 加 AutoDimension2 后 | **3** | **1** | 取不到 | **0** |

**这份读数内部不自洽**：一个 100×60 矩形只被宽度尺寸驱动、
一条关系都没有，按理高度仍自由 ⇒ 应为欠约束（2），可它报了 3。

⚠ **本项未查清**：是关系读数不可靠（GetRelationsCount(-1) 回 0）、
   还是 AutoDimension2 以某种方式同时定住了两个方向、还是
   GetConstrainedStatus() 在「有基线尺寸」时语义与我想的不同 —— **三种解释都未被排除**。
   已按「三次失败就停下质疑」的纪律停止继续试，记为未查明。

### ★★★ 但这一轮抓到了我自己判据的一个真洞

上面那个读数提示了一件事：**「状态 3」不等于「尺寸驱动」**。

于是做了一个离线验证（不连真机）：

`
把草图的每一段都加 sgFIXED、一条驱动尺寸都不加 ⇒ 真机 GetConstrainedStatus() 回 3
喂给 judge_sketch_constraint ⇒ 判 **pass**
`

而 docs/ENGINEERING-PATH.md 第四节 E1 的负例**明令包含**
「**全部固定却无驱动参数**」；1_sketch.py 自己的 docstring 也把它列为必拒。

⇒ **第 4 轮我加枚举路径时，把这条负例绕过去了**：枚举说 3 就直接 pass，
   不再看有没有驱动尺寸。这正是 S1 要防的那类洞，而我自己漏了一个。

### 修法

采集器新增 driving_dimensions: int | None；判定器在状态 3 时**再看它**：

| driving_dimensions | 结论 |
|---|---|
| >= 1 | pass（尺寸在驱动） |
| == 0 | **fail**（全固定，不是尺寸驱动） |
| None | **unknown**（没数过；按「unknown ≠ pass」不得判绿） |

新增测试与样件：
- samples.bad_e1_all_fixed_by_relation（3 + 0 尺寸）→ 期望 fail
- samples.bad_e1_status3_no_dimension_count（3 + 没数过）→ 期望 unknown
- 	est_全固定且零驱动尺寸必须判fail · 	est_状态3但没数过尺寸必须判unknown
- 原来那 5 条把「状态 3 即 pass」写死的测试**按新契约更新**（它们编码了那个洞）

⇒ E1 三态样件从 80 条增到 85 条，全部通过。

## 十、收紧契约后，把调用方都补齐了（第 10 轮）

第 9 轮给 E1 加了 `driving_dimensions` 之后，**所有调用方都必须补这个字段**，
否则状态 3 会被判成 `unknown`（没数过）。这一轮把三处补齐。

### 新增共用能力：`sw_sketch_dimensions.count_sketch_dimensions`

`-1`（没数到）与 `0`（确实零个）**必须分开** —— 否则调用方会把「没测」当成「全固定」。
实现走 `IFeature.GetFirstDisplayDimension` + `IDisplayDimension.GetNext2`。

`tests/test_sketch_dimension_count.py`（9 条）钉住这条契约，含
「有草图无尺寸回 0」「无草图特征回 -1」「取不到特征名回 -1」。

★ 写测试时自己踩了一个坑并记在注释里：`get_com_member` 对**无实参**成员是
  「先无参调一次」的语义，替身若只 `getattr` 不调用，`GetNext2` 会回**方法对象**，
  计数全错。替身已照正式语义写。

### E1 真机探针改了两处

`tools/probe_s3_e1_real_machine.py`：

| 改动 | 原因 |
|---|---|
| 两处 `collect_sketch_constraint` 补 `driving_dimensions` | 契约收紧 |
| 「加 sgFIXED 造全约束」从**好样件**改成**坏样件** | 它正是被堵掉的那个洞 |

新读数：

```
① 欠约束草图：GetConstrainedStatus = 2 · 驱动尺寸 = 0 → 判据 fail
③ 全固定后（sgFIXED，零驱动尺寸）：GetConstrainedStatus = 3 · 驱动尺寸 = 0 → 判据 fail
★ 真机两种坏样件都被拒
```

★ 改造前的探针把 ③ 当「好样件、应判 pass」—— **探针自己也编码了那个洞**。
  现在它成了第二个真实坏样件，读数更有信息量。

## 十一、★★ 更正第九节的一个读数：那次的「关系 0 → 0」是**测量错误**

第九节记的真机读数是「状态 2→3 · 尺寸 0→1 · **关系 0→0**」，
并据此列出三种未排除的解释。

**「关系 0→0」这个读数是错的。** 真因在 filter 参数：

`ISketchRelationManager.GetRelationsCount(Filter)` 的官方枚举
`swSketchRelationFilterType_e` 逐字：

| 成员 | 值 |
|---|---|
| **swAll** | **0** |
| swDangling | 1 |
| swOverDefining | 2 |
| swExternal | 3 |
| swDefinedInContext | 4 |
| swLocked | 5 |
| swBroken | 6 |
| swSelectedEntities | 7 |

⇒ **`-1` 不在枚举里**。传它时 SolidWorks **回 0 而不报错**。
⇒ 当时探针传的是 `-1`，所以「0 条关系」是**假读数**。

### 正确的读数（同一张矩形 + 4 孔的草图）

| 时点 | `GetRelationsCount(-1)` | `GetRelationsCount(0)` |
|---|---|---|
| 加关系前 | 0（非法值） | **5** |
| `FullyDefineSketch`（全关系+全尺寸）后 | 0 | **21** |
| `FullyDefineSketch`（只加尺寸）后 | 0 | **19** |

### ★★ 由此得到两个结论

**① `FullyDefineSketch` 主要靠「加关系」把草图定死，只加 1 个尺寸。**

8 个实体（4 边 + 4 圆）→ 关系 5 → **21**，尺寸 0 → **1**，状态 2 → 3。

⇒ 这正是 E1 要拒绝的形态（「关系堆出来」而非「尺寸驱动」）。
  所以**它不能作为「让孔位参数化」的方案** —— 孔位并没有得到尺寸。

**② 修掉了仓库里一个「永远回 0」的真缺陷。**

`scripts/sw_sketch_dimensions.count_sketch_relations` 原默认 `filter=-1`
⇒ 函数与它挂的工具 `solidworks_count_sketch_relations` **每次都报「0 条关系」**。

修法：默认改 **0**（`swAll`），工具 `Param` 默认同步改，两个既有调用方
（`tools/prove_b5_sketch_dimensions.py`）里显式传的 `-1` 也改 0。

`tests/test_relation_filter_contract.py`（4 条）钉住：默认必须是 0、
函数如实把 filter 传下去、工具声明同步、源码里不再把 -1 当全数。

### 本节同时确认的好消息

`ISketchManager.FullyDefineSketch` **现在能调通了**（第 6 轮那次失败是参数错）：

| 参数 | 第 6 轮传的（错） | 正确值 |
|---|---|---|
| `HorizontalDimPlacement` | -1 | **0 = Above**（1 = Below） |
| `VerticalDimPlacement` | -1 | **0 = Right**（1 = Left） |
| `RelationsToApply` | -1 | `swSketchFullyDefineRelationType_e` **位掩码**（10 种全取 = 1023） |
| `HorizontalDatumDisp` / `VerticalDatumDisp` | Python `None` | **VARIANT Nothing**（`create_empty_dispatch_variant()`） |

两组参数都 `call_ok=True`、状态 2→3。
但**尺寸仍只有 1 个** ⇒ 对「孔位参数化」没有帮助（见上）。

---

## 十、第 53 轮勘察：孔位联动的地形（只读，不动模型）

**探针**：`tools/probe_e2_hole_sketch_survey.py`（只读：不建尺寸、不改模型、不保存）
**证据**：`output/e2-hole-sketch-survey.json`

### 实测结构

```
包围盒(mm)：{'ok': True, 'x_mm': 100.0, 'y_mm': 60.0, 'z_mm': 20.0}
顶层特征 11 个：
  前视基准面 · 上视基准面 · 右视基准面 · 原点 · Tables
  草图1 · 凸台-拉伸1 · M6 间隙孔1 · M6 间隙孔2 · M6 间隙孔3 · M6 间隙孔4
```

⇒ 三个要点：

| 事实 | 含义 |
|---|---|
| 板宽尺寸是 `D1@草图1`（第六节已验：100 → 120 mm 改得动） | **改宽这条路是通的** |
| 四个孔是 **HoleWizard 特征**（`M6 间隙孔1..4`），不是普通草图 | 孔心在各孔特征**自己的定位草图**里 |
| 孔心目前**没有与板边建尺寸** | 所以改宽时孔心位移 = 0（E2.rebuild fail 的直接原因） |

### 为什么这条现在才可能做

第 52 轮（事实 567）找到可用的建尺寸入口 `IModelDocExtension.AddDimension`：

```
before            0
select_Select2    {'ret': True, 'selected': 1}    ← 只有 Select2 选得中草图段
call              {'ok': True, 'dim_none': False}
after             1                               ← ★ 尺寸 0 → 1
```

★ 它会弹 SolidWorks 的「修改」属性框并**同步阻塞** ⇒ 必须**另一个进程按 ESC** 才返回。
★ 第 53 轮又排除一条：`SetAddToDB(True)` **不能**省掉这个框（实测仍需 ESC，尺寸照样 0 → 1）。

### 下一步（有明确判据）

1. 进 `M6 间隙孔N` 的定位草图，把孔心与**右板边**建一个水平尺寸
2. 四个孔各一次（每次一个尺寸；ESC 由伴跑进程发）
3. 改 `D1`（板宽 100 → 120），量四个孔心的 X 位移
4. **判据**：位移 ≈ **+20.0 mm**（`E2.rebuild` 现在的读数是 `[0,0,0,0]`）
   ⇒ 只有读到非零位移，`E2.rebuild` 才可能从 `fail` 变 `pass`

### 明确没做的

- **没有**在本轮建任何尺寸（本轮只勘察）
- **没有**声称孔位联动已成立 —— 现状仍是 **fail**
- **没有**降低判据：位移必须真的 ≈ 20mm，不接受"看起来动了"

---

## 十一、第 54 轮：孔心联动**机制验证成功**（副本上）

**探针**：`tools/probe_e2_hole_dimension_link.py --hv`
**证据**：`output/e2-hole-dimension-link.json`

### 读数

```
板宽            100.0 mm
四个孔心        (10,10) (90,10) (10,50) (90,50) mm
建尺寸          四个孔全部 dims 0 → 1
改板宽          100 → 120 · ok=True · 改后板宽 120.0 mm
孔心 X 位移     [20.0, 20.0, 20.0, 20.0] mm      ← 判据要求的 ≈ +20
```

### 三步缺一不可

| # | 做法 | 关键点 |
|---|---|---|
| ① | 进孔的位置草图 | `M6 间隙孔N`（`HoleWzd`）的**子特征**里，只含 1 个点的那张 |
| ② | 选孔心点 + 右板边 | `SelectByID2` 的 `Callout` **必须传空 Dispatch**（事实 33），传 `None` 报「类型不匹配」 |
| ③ | `IModelDoc2.AddHorizontalDimension2(X, Y, Z)` | 事实 560 记它「会崩」——**实际是被「修改」属性框阻塞**；同进程 ESC 线程清掉即可 |

★ ESC 线程用 `PostMessage`（**不需要 COM**）⇒ 线程里发安全，不必另起进程。

### 两个入口的适用面不同（实测对比）

| 入口 | 点 + 边 | 一条草图线段 |
|---|---|---|
| `IModelDocExtension.AddDimension`（事实 567） | `add_ok=True` 但返 None、尺寸 **0→0** | ✅ 0 → 1 |
| `IModelDoc2.AddHorizontalDimension2` | ✅ **0 → 1** | — |

### 仍未完成（**不许写成熟了**）

上述全部在 `output/link54/板1_link.SLDPRT`（**副本**）上验成。
**交付件 `output/stage2/板1_rev-1.SLDPRT` 还没加这四个尺寸**
⇒ `specs/350-first-part-delivery/s3-acceptance.md` 里 `E2.rebuild` **仍是 fail**。

下一步：把同一套三步落到交付件，再跑 `tools/run_s3_acceptance.py` 复核。

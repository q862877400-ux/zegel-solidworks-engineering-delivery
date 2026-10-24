# S3 官方源核查记录 · E1/E4 真机采集所需的成员名

**日期**: 2026-10-25

**对应任务**: `specs/350-first-part-delivery/tasks.md` T007

**依据**: `AGENTS.md` 铁律 4（签名三源互证，冲突以出厂类型库为准）+ 铁律 5（查不到就说查不到）

---

## 一、结论先说

| 要查什么 | 查到了吗 | 关键读数 |
|---|---|---|
| E1 草图求解状态 | ✅ 查到 | `ISketch.GetConstrainedStatus()` → **返回状态枚举，不是数值自由度** |
| E4 干涉检查 | ✅ 查到 | `IAssemblyDoc.InterferenceDetectionManager` → `IInterferenceDetectionMgr.GetInterferenceCount()` |
| E4 配合剩余自由度 | ❌ **没查到** | 见第四节 |

★★ **最重要的发现**：SolidWorks 的草图约束状态 API **只给状态枚举、不给数值 DOF**。
这直接改变了 E1 采集器的设计（见第三节）。

## 二、E1 草图求解状态

### 第一源：`C:\swapi`（结构化 markdown）

查询命令：

```powershell
python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" member ISketch GetConstrainedStatus
python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" enum swConstrainedStatus_e
```

签名逐字：

```
System.int GetConstrainedStatus()
```

Returns 段逐字：「Constrained status as defined in `swConstrainedStatus_e`」

枚举 `swConstrainedStatus_e` 的七个成员（逐字）：

| 成员 | 值 |
|---|---:|
| `swUnknownConstraint` | 1 |
| `swUnderConstrained` | 2 |
| `swFullyConstrained` | 3 |
| `swOverConstrained` | 4 |
| `swNoSolution` | 5 |
| `swInvalidSolution` | 6 |
| `swAutosolveOff` | 7 |

### 第二源：官方 CHM 解包

`AI Solidworks\官方文档\SWhelp\sldworksapi\` 存在（`sw_know verify` 的「草图」域 `[OK]`），
但**未逐页比对** —— 本次只核了 `C:\swapi` 与反射两源。如实记录为「未做第二源比对」。

### 第三源：出厂类型库反射

**⚠ 缺失。** `_raw\reflect\` 下有 12 个次要程序集的转储
（`cosworks` / `sldcostingapi` / `swdocumentmgr` / `SWRoutingLib` / `swdimxpert` 等），
**没有主程序集 `sldworks`** 的 `iface_sldworks.txt`。

实测命令：

```powershell
Get-ChildItem _raw\reflect | Select-Object Name
# 结果：无 iface_sldworks.txt
Select-String -Path _raw\reflect\*.txt -Pattern "GetConstrainedStatus" -List
# 结果：无命中
```

⇒ **本项只有单一来源支撑**，不满足铁律 4 的「三源互证」。
按铁律 5，这必须如实标注，不能当成已确认签名。

## 三、★ 这个发现怎么影响 E1 采集器

`scripts/engineering/acceptance/e1_sketch.py` 的判定器吃的是
`entities / relations / dimensions` 三个**数值**，用来算 `2E − R − D`。

而真机 API **给不出这三个数** —— 它只给一个状态枚举。

**⇒ 真机采集器不能按现在的合成模型取数。** 正确做法是分两层：

| 场景 | 用什么判 | 状态 |
|---|---|---|
| 只要「是否全约束」 | `GetConstrainedStatus() == swFullyConstrained (3)` | ✅ 可直接取 |
| 要「剩几个自由度」 | 无单一 API —— 需组合诊断（枚举草图实体与关系对象自己算） | ⚠ **技术风险** |
| 要「有意保留的自由度」 | 同上 | ⚠ **技术风险** |

按 `AGENTS.md` 环节条件第 7 条：

> 某项 E 判据没有可验证的采集方式 → 列为技术风险，**不能先把返回值填上**。

⇒ S3 的真机采集器只能实现**第一层**（状态枚举判全约束）；
第二层（数值 DOF）在拿到可靠诊断方法之前，必须返回 `unknown`，**不得填 0**。

这与 `docs/ENGINEERING-PATH.md` 第四节的预留条款一致，逐字：

> 具体 API 是否支持数值 DOF、仅支持状态枚举或需要组合诊断，
> 在首个真机技术验证中确认；本文件不杜撰成员名。

**本次核查给出的答案就是：仅支持状态枚举。**

## 四、E4 装配

### 干涉检查（✅ 查到）

```
IAssemblyDoc.InterferenceDetectionManager  → IInterferenceDetectionMgr
IInterferenceDetectionMgr.GetInterferenceCount()
```

同族还有 `GetInterferences()` / `GetInterferenceComponents()` / `IgnoreHiddenBodies` /
`IncludeMultibodyPartInterferences` / `TreatCoincidenceAsInterference`。

⚠ `TreatCoincidenceAsInterference` 的默认值**未核** —— 它决定「面重合」算不算干涉，
直接影响 E4 的判定。**S4 开工前必须先查清它的默认值与语义。**

### 配合剩余自由度（❌ 没查到）

`IAssemblyDoc` 有大量配合相关成员（`AddMate5` / `EditMate4` / `CollectAllSupportiveMates` /
`IsSupportedMatesAvailable`），但**没有**「读剩余自由度」的成员。

⇒ E4 的 DOF 判定与 E1 同病：**只能判「配合对象够不够」，判不了「剩几个自由度」**。
本项列为技术风险，采集器返回 `unknown`。

## 五、这批发现怎么落到代码

| 落点 | 要改什么 |
|---|---|
| `e1_sketch.collect_sketch_constraint` | 真机版只填 `solver_state`；`entities/relations/dimensions` 取不到时留空并标 `complete=False` |
| `e1_sketch.judge_sketch_constraint` | 已支持 `solver_state` 分支前先判枚举；数值 DOF 分支仅在三个数都真取到时走 |
| `e4_assembly.collect_assembly` | 干涉数可填真值；DOF 相关字段取不到时标 `complete=False` |

⚠ **本次未改这三个采集器** —— 改它们必须同时有真机证据，
否则就是「先填返回值」（`AGENTS.md` 环节条件第 7 条明确禁止）。

## 六、未做的事（如实）

1. **未做第二源（CHM）逐页比对** —— 只核了 `C:\swapi` 与反射（后者缺主程序集）
2. **未查 `TreatCoincidenceAsInterference` 的默认值** —— S4 开工前必须补
3. **未改任何采集器** —— 见第五节
4. **未接真机** —— 本记录全部是离线查源

## 七、下一步（S3 真机部分的停线条件）

按 `docs/ENGINEERING-PATH.md` 第六节 S3 的停线条件：

> 约束状态取不到、主参数改动不联动、只能导入实体而无编辑历史、必需图样绑定不可实现。

本次核查表明**「约束状态取得到」**（枚举可取），**但「数值 DOF 取不到」**。
后者不构成 S3 停线（S3 的 E1 判定可以用枚举），
但它使「有意保留自由度」这一子项无法验证 —— 记为遗留，不是阻断。

S3 真机工作可以开始，前置是 `specs/350-first-part-delivery/requirements.md`
的八项冻结（目前八项全未定）。

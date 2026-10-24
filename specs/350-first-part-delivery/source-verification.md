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

#### `TreatCoincidenceAsInterference` 的默认值：**官方没写**

签名：`System.bool TreatCoincidenceAsInterference {get; set;}`

Returns 段逐字：「True to treat coincident entities as interference, false to not」

`## Remarks` 逐字（只讲生命周期，**不讲默认值**）：

> Currently, the value set for this property:
> - exists only while the InterferenceDetectionMgr object is in scope; i.e., setting this property is temporary.
> - does not persist across SOLIDWORKS Design sessions.
> - does not persist into the next invocation of interference detection in the user interface.

★★ **结论**：默认值**查不到**（铁律 5：查不到就说查不到）。

★★ **但这不影响正确做法** —— 正因为它是「临时、不跨会话、不进下一次 UI 调用」，
S4 的采集器**必须显式设置它**，不能依赖默认值。设成哪个值要由需求定：
- 「面重合」算不算干涉，决定了 `GetInterferenceCount()` 的读数含义
- 若按默认（未知）取数，同一个模型在不同会话里可能给出不同计数

⇒ 列入 S4 开工前的必做项：**显式设置并记录该属性的取值**，且把取值写进 E4 的证据链。

### 配合剩余自由度（❌ 没查到）

`IAssemblyDoc` 有大量配合相关成员（`AddMate5` / `EditMate4` / `CollectAllSupportiveMates` /
`IsSupportedMatesAvailable`），但**没有**「读剩余自由度」的成员。

⇒ E4 的 DOF 判定与 E1 同病：**只能判「配合对象够不够」，判不了「剩几个自由度」**。
本项列为技术风险，采集器返回 `unknown`。

## 五、这批发现怎么落到代码

| 落点 | 改了什么 | 状态 |
|---|---|---|
| `e1_sketch.collect_sketch_constraint` | 新增 `solver_status_int` 参数；`complete` 改为「枚举或数值任一可得」 | ✅ 已改 |
| `e1_sketch.judge_sketch_constraint` | 新增枚举分支：有枚举**只信枚举**，无枚举才退回数值 | ✅ 已改 |
| `sw_sketch_status.py` | 取值表 `CONSTRAINED_STATUS` + `status_meaning()` 归口于此；COM 依赖改为函数内 import | ✅ 已改 |
| `sw_sketch_relations.py` | 删除本地复制的取值表，改为复用 `sw_sketch_status` | ✅ 已改 |
| `e4_assembly.collect_assembly` | 干涉数可填真值；DOF 相关字段取不到时标 `complete=False` | ⬜ 留 S4 |

### ★★ 为什么这不算「先填返回值」

`AGENTS.md` 环节条件第 7 条禁止「某项 E 判据没有可验证的采集方式时先把返回值填上」。
本次改的是**采集方式本身**：枚举路径是 API **真支持**的信号，
所以按枚举判定是**正确采集**，不是填返回值。

相反，数值 DOF 路径在真机上取不到 —— 它保留给合成与诊断场景，
**且只在没有枚举时才走**（有测试钉住 `test_有枚举时不信数值`）。

## 五之二、顺带修掉的一处「同一事实两个说法」

`sw_sketch_status.py` 原写「查不到官方取值表」，
而 `sw_sketch_relations.py` 里**照录着** `swConstrainedStatus_e` 的 7 个成员，
还带真机铁证（读出 `status = 4` 时截图有红「项目无法解出」+ 黄「项目冲突」）。

⇒ 同一件事在两个模块里说法相反。已**归口**到 `sw_sketch_status.CONSTRAINED_STATUS`，
`sw_sketch_relations.py` 改为复用。

★ 附带收获：`sw_sketch_status.py` 早先的真机读数（未约束 = 2、全加 `sgFIXED` = 3）
现在**可以解释了** —— 与官方表的 `2 = swUnderConstrained`、`3 = swFullyConstrained`
完全吻合，构成**交叉验证**而非猜测。

## 六、未做的事（如实）

1. **未做第二源（CHM）逐页比对** —— 只核了 `C:\swapi` 与反射（后者缺主程序集）
2. **`TreatCoincidenceAsInterference` 的默认值查不到** —— 已改为「S4 必须显式设置」
3. **未接真机** —— 本记录全部是离线查源
4. **`e4_assembly` 未改** —— 干涉读取留 S4（需要真机才能验证读数含义）

## 七、下一步（S3 真机部分的停线条件）

按 `docs/ENGINEERING-PATH.md` 第六节 S3 的停线条件：

> 约束状态取不到、主参数改动不联动、只能导入实体而无编辑历史、必需图样绑定不可实现。

本次核查表明**「约束状态取得到」**（枚举可取），**但「数值 DOF 取不到」**。
后者不构成 S3 停线（S3 的 E1 判定可以用枚举），
但它使「有意保留自由度」这一子项无法验证 —— 记为遗留，不是阻断。

S3 真机工作可以开始，前置是 `specs/350-first-part-delivery/requirements.md`
的八项冻结（目前八项全未定）。

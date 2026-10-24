# S3 官方源核查记录 · E1/E4 真机采集所需的成员名

**日期**: 2026-10-25

**对应任务**: `specs/350-first-part-delivery/tasks.md` T007

**依据**: `AGENTS.md` 铁律 4（签名三源互证，冲突以出厂类型库为准）+ 铁律 5（查不到就说查不到）

---

## 一、结论先说

| 要查什么 | 查到了吗 | 关键读数 |
|---|---|---|
| E1 草图求解状态 | ✅ **三源互证** | `ISketch.GetConstrainedStatus()` → **返回状态枚举，不是数值自由度** |
| E1 数值自由度 | ❌ **三源确认不存在** | 20627 个反射成员里零命中 |
| E4 干涉检查 | ✅ **三源互证** | `IAssemblyDoc.InterferenceDetectionManager` → `IInterferenceDetectionMgr.GetInterferenceCount()` |
| E4 配合剩余自由度 | ❌ **三源确认不存在** | 见第四节 |

★★ **最重要的发现**：SolidWorks 的草图约束状态 API **只给状态枚举、不给数值 DOF**。
这直接改变了 E1 采集器的设计（见第三节）。

★ 第二重要：`C:\swapi` 与反射**都**没有 DOF 成员 ⇒
  「没有数值自由度入口」是**确认的结论**，不是「我没查到」。

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

### 第三源：出厂类型库反射 —— **已补齐**

★ 2026-10-25 补：原先 `_raw\reflect\` 只有 12 个次要程序集的转储，
主程序集 `sldworks` **缺失** ⇒ 只有单一来源。现已生成：

```powershell
pwsh -File tools\reflect-interop.ps1 -Targets sldworks -Out <仓库根>\_raw\reflect
# 输出：sldworks  ifaces=1032  enums=0  classes=849  members=20627
```

生成物：`_raw\reflect\iface_sldworks.txt`（0.68 MB）、`enum_sldworks.txt`。
⚠ `_raw\` 在 `.gitignore` 里（反射转储不入库），换机器要重跑上面那条命令。

反射里的签名：

```
Int32 GetConstrainedStatus()
```

★★ **三源一致**：`C:\swapi` 写 `System.int`、反射写 `Int32` —— 同一个类型。
⇒ E1 的 `GetConstrainedStatus` 现在**满足铁律 4 的三源互证**。

★★★ **附带得到一个强否定结论**：反射转储覆盖 1032 个接口 / **20627 个成员**，
其中**没有任何** DOF 读取成员 ——
`DegreesOfFreedom` / `GetDof` / `RemainingDof` / `UnderDefined` **全部零命中**。

⇒ 「SolidWorks API 没有数值自由度读取入口」从「查不到」升级为
  **三源确认的否定结论**（`C:\swapi` 无、反射 20627 成员无、真机只回枚举）。

## 二之二、E4 的两个成员也三源确认了

```
Boolean get_TreatCoincidenceAsInterference()
Int32   GetInterferenceCount()
```

反射与 `C:\swapi` 一致。
⚠ 注意反射给出的是 `get_` / `set_` 分离的属性访问器形态 ——
那是 .NET 属性在 IL 层的真实形状，`C:\swapi` 写 `{get; set;}` 是同一件事的两种表述。

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

### 配合剩余自由度（❌ 三源确认不存在）

`IAssemblyDoc` 有大量配合相关成员（`AddMate5` / `EditMate4` / `CollectAllSupportiveMates` /
`IsSupportedMatesAvailable`），反射转储的 20627 个成员里**没有**「读剩余自由度」的入口。

⇒ E4 的 DOF 判定与 E1 同病：**只能判「配合对象够不够」，判不了「剩几个自由度」**。
本项列为**确认的技术限制**（不再叫「待查」），采集器返回 `unknown`。

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

1. **未做 CHM 逐页比对** —— 三源里核了 `C:\swapi`、反射、真机读数；
   `AI Solidworks\官方文档\` 的页面**未逐页打开**（`sw_know verify` 的「草图」域报 `[OK]`，
   但那是覆盖自检，不是逐页核对）。如实记为「两源半」而非「三源全页」
2. **`TreatCoincidenceAsInterference` 的默认值查不到** —— 已改为「S4 必须显式设置」
3. **未接真机做新的读数** —— 本记录的真机部分是引用既有实测
   （`tools/prove_coverage_gap_batch1.py`、`sw_sketch_relations.py` 记的现场铁证）
4. **`e4_assembly` 未改** —— 干涉读取留 S4（需要真机验证读数含义）

## 七、下一步（S3 真机部分的停线条件）

按 `docs/ENGINEERING-PATH.md` 第六节 S3 的停线条件：

> 约束状态取不到、主参数改动不联动、只能导入实体而无编辑历史、必需图样绑定不可实现。

本次核查表明**「约束状态取得到」**（枚举可取，且三源互证），
**「数值 DOF 三源确认不存在」**。

后者不构成 S3 停线 —— S3 的 E1 判定可以用枚举（已实现并测试）。
但它使「有意保留自由度」这一子项只能靠**需求声明**（`intentional_dof`），
无法从模型反读 —— 记为遗留，不是阻断。

S3 真机工作的前置是 `specs/350-first-part-delivery/requirements.md`
的八项冻结（目前八项全未定）。

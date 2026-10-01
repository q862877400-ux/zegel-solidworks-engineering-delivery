# 099 · `verified` 条目的验收命令**现在跑不了** —— 原因是**环境**，不是代码退化

**Status**: Implemented（轮 179）

## 一、背景
objective ② 要求「**拓扑优化闭环并升 `verified`**」⇒ ★ **那条早已做完**
（`topology_optimization` 的 `level` 就是 **`verified`**，`evidence` 两条、限度 18 条）。
⇒ 本轮做的是 objective ③ 的「**跑该阶段验收命令确认真绿**」⇒ **结果它是红的**。

## 二、验收命令的实际输出
```
python tools/capture_topology_evidence.py
  steps: part ✓（100×60×20 mm 单实体板）· material ✓（AISI 1020）
  verdict: fail
  error: RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None：
         Simulation 加载项未加载或本机未安装（需 Simulation 许可证）
```

## 三、★★ 分辨两种可能（探针，不猜）
```
① 加载前 GetAddInObject('SldWorks.Simulation') ⇒ **None**
② LoadAddIn(<5 个候选名>) ⇒ **全部返回 3**（⚠ 官方**未给返回码枚举** ⇒ **不猜它是什么**）
③ 加载后 ⇒ **仍 None**
⇒ ★ **不是「程序没加载」（那类可修），而是许可 / 安装层面（环境性）**
```

## 四、★★★ 为什么不因此把 `level` 降级
```
`verified` 的定义是「**有我们自己的运行证据**」，而**证据在** ——
`output/topology-evidence.json` 记着当时的完整闭环
（`verdict: pass`：建研究 `AnalysisType == 13`、目标+质量约束 `EndEdit == 0`、
 夹具选区计数 1、`study.Results` 非空）。
★ **但必须在条目里写明「当前环境复跑不了」** —— 否则下一个人会以为**随时能跑**。
⇒ ★ 这正是「**报告要写明仍空缺什么、为什么**」那条验收判据（A8）的**实例**。
```

## 五、恢复办法（属「只有用户能提供的东西」）
```
① 在 SolidWorks 里确认「**Simulation**」加载项已启用；
② 在 SolidNetWork License Manager 里确认 `Simulation Professional/Premium` 可用。
⚠ 本轮**没有**动任何许可设置（红线：不碰系统层 / 只有用户能提供的东西）。
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-9901 | ★★ **跑了**该阶段的验收命令（objective ③ 的直接要求）|
| SC-9902 | ★★★ **分辨**「没加载」与「没许可」两种可能（探针，不猜）|
| SC-9903 | ★★ **不降级** `level`（历史证据仍在），但**写明当前复跑不了** |
| SC-9904 | ★ 给出**可执行的恢复办法**，并说明它属「只有用户能提供的东西」|
| SC-9905 | ⚠ **如实记**：`LoadAddIn` 返回 3 而**官方不给枚举** ⇒ 不知道 3 是什么 |

## ⚠ 明确记下的限度
* ⚠ **拓扑闭环本轮没能复跑**（环境缺 Simulation 加载项/许可）⇒ **无法独立复核**它的历史结论；
* ⚠ `LoadAddIn` 的返回码 **3 的语义未知**（官方无枚举）；
* ⚠ 本轮**没有**改任何许可 / 加载项设置（红线）；
* ⚠ 只跑了**这一条**验收命令；其余条目各自的验收命令**未逐条跑**。

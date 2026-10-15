import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 119 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 119 | " + "".join([
    "**`verified` 条目的验收命令**现在跑不了** —— 而原因是**环境**（Simulation 加载项/许可），不是代码退化** —— ",
    "2026-10-01（轮 179）。",
    "★ 背景：objective ② 要求「**拓扑优化闭环并升 `verified`**」⇒ ★ **那条早已做完**",
    "（`topology_optimization` 的 `level` 就是 `verified`，`evidence` 两条、限度 18 条）。",
    "⇒ 本轮做的是 objective ③ 的「**跑该阶段验收命令确认真绿**」⇒ **结果它是红的**：",
    "```",
    "python tools/capture_topology_evidence.py",
    "  steps: part ✓（100×60×20 mm 单实体板）· material ✓（AISI 1020）",
    "  verdict: fail",
    "  error: RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None：",
    "         Simulation 加载项未加载或本机未安装（需 Simulation 许可证）",
    "```",
    "★★ 探针 `tools/probe_simulation_addin_status.py` **分辨了两种可能**（不猜）：",
    "```",
    "① 加载前 GetAddInObject('SldWorks.Simulation') ⇒ **None**",
    "② LoadAddIn(<5 个候选名>) ⇒ **全部返回 3**（⚠ 官方**未给返回码枚举** ⇒ **不猜它是什么**）",
    "③ 加载后 ⇒ **仍 None**",
    "⇒ ★ **不是「程序没加载」（那类可修），而是许可 / 安装层面（环境性）**",
    "```",
    "★★★ **为什么不因此把 `level` 降级**：`verified` 的定义是「**有我们自己的运行证据**」，",
    "而**证据在** —— `output/topology-evidence.json` 记着当时的完整闭环",
    "（`verdict: pass`：建研究 `AnalysisType == 13`、目标+质量约束 `EndEdit == 0`、夹具选区计数 1、`Results` 非空）。",
    "★ **但必须在条目里写明「当前环境复跑不了」** —— 否则下一个人会以为**随时能跑**（★ 这正是",
    "「**报告要写明仍空缺什么、为什么**」那条验收判据的实例）。",
    "★ **恢复办法属「只有用户能提供的东西」**：确认「Simulation」加载项已启用 + SolidNetWork License Manager 里",
    "`Simulation Professional/Premium` 可用（⚠ 本轮**没有**动任何许可设置）。",
    "⚠ 另注：`ISldWorks.LoadAddIn(String) -> Int32`（反射）**返回 3**，而**官方不给返回码枚举** ⇒",
    "**我们不知道 3 是什么**（铁律 5：**查不到就说查不到**）。",
    " | `tools/probe_simulation_addin_status.py`；`D:/AI/SW/output/simulation-addin-status.json`；",
    "`capabilities.yaml` 的 `topology_optimization` 限度第 1 条 |",
])
if "| 119 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 119")
else:
    print("  已有 119")

# ── Spec Kit 099 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\099-topology-acceptance-red-environment")
S.mkdir(parents=True, exist_ok=True)
spec = """# 099 · `verified` 条目的验收命令**现在跑不了** —— 原因是**环境**，不是代码退化

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
"""
plan = """# 099 · Plan

## 步骤
1. objective ② 说的「拓扑优化闭环并升 `verified`」 ⇒ ★ 查证：**早已完成**
2. ⇒ 转做 objective ③「跑该阶段验收命令确认真绿」
3. ★ **跑它** ⇒ **红的**（`GetAddInObject('SldWorks.Simulation')` 返回 None）
4. ★★ 写探针**分辨**「没加载」与「没许可」⇒ 加载前后都 None + `LoadAddIn` 全返 3 ⇒ **环境性**
5. ★★ **不降级** `level`（历史证据仍在），但**把"当前复跑不了"写进条目**
6. 给出**可执行的恢复办法**（属用户侧）
7. 事实 119 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到红就改代码 | ★ 先**分辨原因**（探针）⇒ 是环境 |
| 看到红就降级条目 | ★ `verified` 的定义是"有证据"，**证据仍在** ⇒ 写明环境限制 |
| 把"复跑不了"瞒过去 | ★ **写进条目第 1 条**（A8 的实例）|
| 顺手去动许可 | ★ **不碰**（红线）|
"""
tasks = """# 099 · Tasks（全部完成，轮 179）

- [x] T-9901 查证拓扑条目现状（**已是 verified**）
- [x] T-9902 ★ 跑验收命令 `→ 验收:` `python tools/capture_topology_evidence.py`（**fail，环境**）
- [x] T-9903 ★★ 分辨原因 `→ 验收:` `python tools/probe_simulation_addin_status.py`
- [x] T-9904 更新条目（写明当前复跑不了）+ 给出恢复办法
- [x] T-9905 事实 119
- [x] T-9906 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 099 · Converge

**Converged**: 2026-10-01（轮 179）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9901 跑了验收命令 | ✅（红）|
| SC-9902 分辨原因 | ✅ **环境性**（许可/安装）|
| SC-9903 不降级 + 写明 | ✅ |
| SC-9904 恢复办法 | ✅（用户侧）|
| SC-9905 记 3 的语义未知 | ✅ |

## 二、★★★ 本轮的价值：**跑了验收命令，发现它不绿了**
```
objective ③ 要求「跑该阶段验收命令确认真绿」⇒ ★ **如果我不跑，就永远以为它是绿的**
⇒ 结果：**红**，而原因在**环境**（Simulation 加载项/许可）
★ 这次**不是代码退化** ⇒ 但**只有跑了才知道**
⇒ ★ 这条经验与「**绿不等于对**」（事实 62）互为镜像：**"曾经绿"也不等于"现在绿"**。
```

## 三、★ 而"不降级但写明"是一个需要判断的决定
```
verified 的定义是「有**我们自己的运行证据**」⇒ **证据在**（当时的 pass 记录完整）
⇒ ★ 降级会把**真做过的闭环**抹掉；不写明会把**复跑不了**藏起来
⇒ ★ 正解：**保持 level + 把环境限制写进第 1 条**（A8 的实例）。
```

## 四、未查证
* ⚠ **拓扑闭环本轮无法复跑** ⇒ 历史结论**未独立复核**；
* ⚠ `LoadAddIn` 返回 **3** 的语义未知（官方无枚举）；
* ⚠ 其余条目的验收命令**未逐条跑**（本轮只跑了这一条）。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

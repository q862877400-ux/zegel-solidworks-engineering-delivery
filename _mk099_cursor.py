import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           560 🎯 **Spec Kit `099`：`verified` 条目的验收命令****现在跑不了**** —— 原因是****环境****（Simulation 加载项/许可），不是代码退化**（轮 179）——
               背景：objective ② 要求「**拓扑优化闭环并升 `verified`**」⇒ ★ **查证后：那条早已做完**
               （`topology_optimization` 的 `level` **就是 `verified`**，`evidence` 两条、限度 18 条）
               ⇒ 转做 objective ③ 的「**跑该阶段验收命令确认真绿**」⇒ **结果它是红的**。
            561 ★ **验收命令的实际输出**：
               ```
               python tools/capture_topology_evidence.py
                 steps: part ✓（100×60×20 mm 单实体板）· material ✓（AISI 1020）
                 verdict: fail
                 error: RuntimeError: GetAddInObject('SldWorks.Simulation') 返回 None：
                        Simulation 加载项未加载或本机未安装（需 Simulation 许可证）
               ```
            562 ★★ **探针分辨了两种可能**（`tools/probe_simulation_addin_status.py`，**不猜**）：
               ```
               ① 加载前 GetAddInObject('SldWorks.Simulation') ⇒ **None**
               ② LoadAddIn(<5 个候选名>) ⇒ **全部返回 3**（⚠ 官方**未给返回码枚举** ⇒ **不猜它是什么**）
               ③ 加载后 ⇒ **仍 None**
               ⇒ ★ **不是「程序没加载」（那类可修），而是许可 / 安装层面（环境性）**
               ```
            563 ★★★ **为什么不因此把 `level` 降级**：`verified` 的定义是「**有我们自己的运行证据**」，
               而**证据在** —— `output/topology-evidence.json` 记着当时的完整闭环
               （`verdict: pass`：建研究 `AnalysisType == 13`、目标+质量约束 `EndEdit == 0`、
                夹具选区计数 1、`study.Results` 非空）。
               ★ **但必须在条目里写明「当前环境复跑不了」** —— 否则下一个人会以为**随时能跑**
                 ⇒ ★ 这正是「**报告要写明仍空缺什么、为什么**」那条验收判据（**A8**）的**实例**。
            564 ★★★ **本轮的价值：跑了验收命令，发现它不绿了** ——
               ```
               objective ③ 要求「跑该阶段验收命令确认真绿」⇒ ★ **如果我不跑，就永远以为它是绿的**
               ⇒ 结果：**红**，而原因在**环境**
               ⇒ ★ 与「**绿不等于对**」（事实 62）**互为镜像**：**"曾经绿"也不等于"现在绿"**。
               ```
               ★ **恢复办法（属「只有用户能提供的东西」）**：确认「Simulation」加载项已启用 +
                 SolidNetWork License Manager 里 `Simulation Professional/Premium` 可用
                 （⚠ 本轮**没有**动任何许可设置 —— 红线）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ **拓扑闭环本轮无法复跑** ⇒ 它的历史结论**未独立复核**；
                 ⚠ `LoadAddIn` 返回 **3** 的语义**未知**（官方无枚举 ⇒ 按铁律 5 写"查不到"）；
                 ⚠ 只跑了**这一条**验收命令，其余条目各自的**未逐条跑**。
               下轮候选：① 逐条跑其余 `verified` 条目的验收命令（**"曾经绿"要重新确认为"现在绿"**）；
               ② 查那 47 处未检查项；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+560 ", before, re.M):
    print("  游标 560 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+564 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 564 行已存在 ✓")

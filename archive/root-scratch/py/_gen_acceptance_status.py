import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

R = Path(r"C:\swprojects\sw-skill-fork")
d = json.loads(Path(r"D:\AI\SW\output\verified-acceptance-run.json").read_text(encoding="utf-8"))
rows = d["rows"]
KNOWN = {
    "tools/verify_gtol_smoke.py": "事实 166：`IGtolFrame.AddIndicator` border×tol **20 组全不成**",
    "tools/verify_in_context_reference_smoke.py": "事实 162：**在上下文编辑链**未打通（`SketchUseEdge3` 静默无效）",
    "tools/verify_composite_curve_smoke.py":
        "★ **本轮（轮 180）查清**：失败那条是「**前提未满足，属应然**」（草图数 = 2）"
        "⇒ ⚠ **是这条 smoke 把「应然的失败」当成了 `fail`**（判据问题），**不是退化**；"
        "⚠ 它被 `part_and_features` 当 evidence ⇒ **那条 evidence 是红的**",
    "tools/capture_topology_evidence.py": "事实 119：环境缺 Simulation 加载项/许可（轮 179）",
    "tools/capture_simulation_evidence.py": "事实 119 同族：环境缺 Simulation 加载项/许可",
}

def tag(r):
    v, ex = r.get("verdict"), r.get("exit")
    if r.get("status") in ("MISSING", "TIMEOUT"):
        return "⚠ 没跑成"
    if v == "pass":
        return "★ 绿"
    if v == "fail":
        return "**红**"
    #: 无 verdict：看是探针还是验收脚本
    name = r["cmd"].split("/")[-1]
    if name.startswith("probe_") or name.startswith("audit_") or name.startswith("diag_"):
        return "— 探针（不设 verdict，正常）" + ("　⚠ 但 exit=1" if ex else "")
    return "⚠ 验收脚本却**无 verdict**" + ("　⚠ exit=1" if ex else "")

lines = [
    "# 验收命令现状（`verified` 条目声明的那 31 条真机脚本）",
    "",
    "> 生成：`python tools/run_verified_acceptance_commands.py`"
    "（**每跑一次都会刷新 `output/verified-acceptance-run.json`**）。",
    "> ⚠ 本表是 **2026-10-01（轮 180）** 的快照 —— ★ **「曾经绿」不等于「现在绿」**（事实 119），",
    "> 所以**每次改完都要重跑**这张表，别拿它当**永久**结论。",
    "",
    "| 命令 | 结果 | 定性 |",
    "|---|---|---|",
]
n_pass = n_fail = 0
for r in sorted(rows, key=lambda x: x["cmd"]):
    t = tag(r)
    if r.get("verdict") == "pass":
        n_pass += 1
    if r.get("verdict") == "fail":
        n_fail += 1
    res = ("%s/%s" % (r.get("passed"), r.get("total"))
           if r.get("passed") is not None else
           ("verdict=%s" % r["verdict"] if r.get("verdict") else "（无 verdict）"))
    lines.append("| `%s` | %s | %s |" % (r["cmd"], res, KNOWN.get(r["cmd"], t)))
lines += [
    "",
    "## 汇总",
    "",
    "```",
    "绿   **%d**" % n_pass,
    "红   **%d**（两条**已知**：事实 166 / 162；一条**本轮查清**：`composite_curve` 把「应然的失败」当成了 fail）" % n_fail,
    "探针 **13**（`probe_*` / `audit_*` —— **不设 verdict 是它们的正常形态**）",
    "```",
    "",
    "## ⚠ 本轮（轮 180）的两个发现",
    "",
    "1. ★★ **`verify_composite_curve_smoke` 6/7 是红的**，而它被 `part_and_features` 当作 evidence ⇒",
    "   **那条 evidence 本身是红的**；★ 失败那条是「**前提未满足，属应然**」⇒",
    "   ⚠ **是 smoke 的判据把「应然」当成了「失败」**（判据问题，不是退化）。",
    "2. ⚠ **我的跑器第一版判据太窄**：本仓库的验收脚本有**三种**输出格式",
    "   （`── N/M · verdict: x ──` / `── N/M 项通过 · verdict: x ──` / 单独一行 `verdict: x`），",
    "   我只认第一种 ⇒ **把 4 个 pass 误报成「无 verdict」**。",
    "   ⇒ ★ 又一次「**判据要与实现的实际形态对齐**」（事实 51 那一族）。",
    "",
]
out = R / "docs" / "acceptance-status.md"
out.write_text("\n".join(lines), encoding="utf-8")
print("  已写 %s（%d 字节 / %d 行）" % (out.name, len("\n".join(lines)), len(lines)))
print("  绿 %d · 红 %d" % (n_pass, n_fail))

"""★ 一次性：把 B5-2b 的进展写进 goal-bar 与 tasks。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── tasks ────────────────────────────────────────────────────────────────
t = ROOT / "specs/210-declarative-effects/tasks.md"
lines = t.read_text(encoding="utf-8").splitlines()
out, done, i = [], False, 0
while i < len(lines):
    if lines[i].startswith("- [ ] **B5-2b"):
        out += [
            "- [x] **B5-2b** 把预检**接进护栏**（**已交付**：`precheck_before_run` 点名两次 · "
            "`--skip-precheck` 开关 · 拒绝时退出码 **2**）",
            "      ★★ **真机验证**：两次点名都真的发生（标题路 + COM 路，各读到 0 个文档）⇒ 放行 ⇒ 探针跑通 ✓",
            "      ★★★ **最强负例**：拒绝时 `subprocess.run` **一次都不许被调用**"
            "（★ 若「先启动再拦」，探针早把 SW 拉起来甚至写了文档 ⇒ 那不是保护，是事后告警）✓",
        ]
        done = True
        i += 1
        while i < len(lines) and not lines[i].startswith("- [ ] "):
            i += 1
        continue
    out.append(lines[i]); i += 1
assert done, "没找到 B5-2b 那一格"
t.write_text("\n".join(out) + "\n", encoding="utf-8")
print("tasks B5-2b 已勾:", done)

# ── goal-bar ─────────────────────────────────────────────────────────────
g = ROOT / "specs/210-declarative-effects/goal-bar.md"
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：**B5 进行中** —— **B5-1 已交付** · **B5-2 的「提共用助手」已完成**；下一步 = **B5-2b 接进护栏**",
              "阶段：**B5 进行中** —— B5-1 · B5-2 · **B5-2b 全部已交付**；下一步 = **B5-3 `copy-in / run / copy-out`**")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★ **B5-2b 已交付（预检接进护栏）**：",
    "- `tools/sw_guard.py` 新增 `precheck_before_run` —— ★★ **点名两次**（评审的设计点）：",
    "  `roll=1` **启动之前**走**窗口标题路**（★ 不需 COM ⇒ 连没启动也能问）·",
    "  `roll=2` **连上之后**走 **COM 路**（准，读路径与官方未保存标记）✓",
    "- ★ 判决**一律保守**：非我方文档 ⇒ 拒绝；★ **进程在却两条路都读不出 ⇒ 也拒绝**；",
    "  ★ **唯一放行例外：根本没有 SLDWORKS 进程**（会话必然是空的）✓",
    "- ★ CLI：默认**开**预检 · `--skip-precheck` 才跳过 · `--allow-path` 声明我方路径 ·",
    "  ★ 拒绝时**退出码 2**（★ 与「探针失败=1」分开，免得读错）✓",
    "- ★ 默认**关**的只有库函数 `run_guarded(precheck=False)` —— ★ 免得每次单测都去起 PowerShell/COM ✓",
    "",
    "★★ **真机验证（已做，只读）**：`-- python -c \"print(...)\"` 跑一次 ⇒",
    "  第1次点名放行（0 个文档）· 第2次点名放行（0 个文档）· 探针 `ok: true` · `sw_alive: true` ✓",
    "  ⇒ ★ **两次点名都真的发生了**（不只是单测里成立）✓",
    "",
    "★★★ **本轮修掉一个会把门禁变成路障的语义错**：★ 我第一版把「**没在运行**」与「**探不通**」",
    "  混成同一种失败 ⇒ ★ **护栏会拒绝每一次跑**（★ 而探针常常正是要先拉起 SolidWorks 的那些）✗",
    "  ⇒ ★ 已分开：没进程 ⇒ 放行（会话必然是空的）· 进程在却读不出 ⇒ 拒绝（停下问人）✓",
    "  ★ 并配了一条专门的测试钉住它 ✓",
    "",
    "**B5-3 · `copy-in / run / copy-out`**：所有会打开文档的入口**只接受沙盒内路径**",
    "（外部路径**自动复制进来再用副本**）；跑完由我们把结果拷到**配置的输出根目录**（带 run id 防重名）✓",
    "★ 判据：★ 一条可跑的命令证明「给定沙盒外路径会被**复制进来**而不是被**打开**」✓",
    "",
]
lines_g, i2, hit = s.splitlines(), 0, False
out2 = []
while i2 < len(lines_g):
    if lines_g[i2].startswith("## 下一个动作"):
        hit = True
        out2 += NEW
        i2 += 1
        while i2 < len(lines_g) and not lines_g[i2].startswith("## "):
            i2 += 1
        continue
    out2.append(lines_g[i2]); i2 += 1
assert hit, "没找到「下一个动作」段"
s2 = "\n".join(out2) + "\n"
s2 = s2.replace("- **B5 隔离与预检**：进行中（B5-1 完成 · B5-2 的提助手完成；"
                "**B5-2b 接线** / B5-3 / B5-4 / B5-5 未开始）",
                "- **B5 隔离与预检**：进行中（B5-1 · B5-2 · **B5-2b 完成**；B5-3 / B5-4 / B5-5 未开始）")
g.write_text(s2, encoding="utf-8")
print("goal-bar 已更新:", "B5-2b 已交付" in s2)

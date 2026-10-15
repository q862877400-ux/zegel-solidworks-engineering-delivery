"""★ 一次性：把 B5-4 的进展写进 goal-bar 与 tasks（★ 字符串里一律用「」，避免引号嵌套）。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

t = ROOT / "specs/210-declarative-effects/tasks.md"
lines = t.read_text(encoding="utf-8").splitlines()
out, done, i = [], False, 0
while i < len(lines):
    if lines[i].startswith("- [ ] **B5-4**"):
        out += [
            "- [x] **B5-4** ★ **输出根目录独立配置** + **产品模式进明确命名子目录** + **返回值里报路径**",
            "      （**已交付**：`output_root()` 带 run id、可用 `SW_OUTPUT_ROOT` 覆盖；"
            "★ 产品模式 `product_output_dir` / `tidy_outputs` / `output_report`）",
            "      ⚠ **限度如实写**：★ 分析产物的**落点由 SolidWorks 自己决定**、那一步**不经过我们的调用**",
            "      （评审确认过）⇒ ★ 我们不假装能控制它，★ 只保证「**产物有名字、有去处、能被报出来**」✓",
            "      ★ 可达性：护栏跑前拍沙盒快照、跑后**报出「多出来什么」**（真机验过：报出 1 个）✓",
            "      ★★ 三条安全负例：**只搬点名的那些**（不做目录级清理）· **目标已存在不覆盖** · "
            "**搬不动如实报** ✓",
        ]
        done = True
        i += 1
        while i < len(lines) and not lines[i].startswith("- [ ] "):
            i += 1
        continue
    out.append(lines[i]); i += 1
assert done, "没找到 B5-4 那一格"
t.write_text("\n".join(out) + "\n", encoding="utf-8")
print("tasks B5-4 已勾:", done)

g = ROOT / "specs/210-declarative-effects/goal-bar.md"
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：**B5 进行中** —— B5-1 · B5-2 · B5-2b · **B5-3 全部已交付**；"
              "下一步 = **B5-4 输出根独立配置 + 产品模式子目录**（★ B5-3 已把它做了一半）",
              "阶段：**B5 进行中** —— B5-1 · B5-2 · B5-2b · B5-3 · **B5-4 全部已交付**；"
              "下一步 = **B5-5 夹具一次性快照 + 哈希清单**")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★ **B5-4 已交付**（输出落点）：",
    "- `output_root()`（**带 run id** · 可用 `SW_OUTPUT_ROOT` 覆盖）✓",
    "- **产品模式**：`policy()`（`sandbox` / `product`）· `product_output_dir()`（"
    "★ **明确命名的子目录** `<零件名>_MCP_output/`）· `tidy_outputs()` · `output_report()`（"
    "★ **把实际路径写进返回值** —— 业主拍板的那一条）✓",
    "",
    "⚠⚠ **一处必须说清的限度**（写进 plan 与 tasks，不许含糊）：",
    "  ★ 分析类产物的**落点是 SolidWorks 自己决定的**，★ 那一步**不经过我们的调用**",
    "  （评审原话：「内部写不经过你们的调用，所以应用层守卫对它无效」）⇒",
    "  ★★ 所以本批**不假装能控制它**，★ 只保证「**产物有名字、有去处、能被报出来**」——",
    "  ★ 做法是：**跑前拍沙盒快照 → 跑后算出「多出来什么」→ 报出来** ✓",
    "  ★ **可达性已接**：护栏跑完会打印「★ 跑完多出 N 个文件」——★ **真机验过**（报出 1 个）✓",
    "",
    "★★ **本轮我又自己引入并修掉了一个真回归**（如实记）：",
    "  ★ 我把 `sandbox_before = snapshot_sandbox()` 写进了 `run_guarded`、却在 `main` 里用它 ⇒",
    "  ★★ **每次跑完护栏都 `NameError` 崩掉**（真机退出码 **1**）✗ —— ★ 而它**只在真机跑时才暴露**；",
    "  ★ 已修作用域，★ 并加了一条**专门钉住这条路径**的回归测试 ✓",
    "",
    "**B5-5 · 夹具一次性快照 + 哈希清单**：把那 31 个真实件**一次性复制**到测试专用夹具库、",
    "  **冻结哈希清单**；★ 此后测试**不再引用原目录**（★ 原件不需要任何 ACL —— 没人再碰它）✓",
    "  判据：★ 一条测试证明「夹具库里有一份完整副本 + 哈希清单」；★ 一条证明「测试读的是**夹具库**、",
    "  不是原目录」✓",
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
s2 = s2.replace("- **B5 隔离与预检**：进行中（B5-1 · B5-2 · B5-2b · **B5-3 完成**；B5-4 / B5-5 未开始）",
                "- **B5 隔离与预检**：进行中（B5-1 · B5-2 · B5-2b · B5-3 · **B5-4 完成**；B5-5 未开始）")
g.write_text(s2, encoding="utf-8")
print("goal-bar 已更新:", "B5-4 已交付" in s2)

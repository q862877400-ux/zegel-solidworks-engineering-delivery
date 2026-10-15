"""★ 一次性：把 B5-2 的进展写进 goal-bar（按行定位，避开引号形态不一致）。"""
from pathlib import Path

g = Path(r"D:\AI\SW\specs\210-declarative-effects\goal-bar.md")
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：**B5 进行中** —— **B5-1 预检门禁已交付**；下一步 = **B5-2 提共用助手 + 接进护栏**",
              "阶段：**B5 进行中** —— **B5-1 已交付** · **B5-2 的「提共用助手」已完成**；下一步 = **B5-2b 接进护栏**")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★ **B5-2（「提共用助手」这一半）已交付**：",
    "- 新 `tools/session_verdict.py` —— ★★ **两条探路、一个裁决**（这是它存在的全部理由）：",
    "  ① **COM 路**（准）：`GetDocuments` + `GetPathName` + ★ **官方 `IModelDoc2.GetSaveFlag`**",
    "     （原文 Gets whether the document is currently dirty and needs to be saved）",
    "  ② **标题路**（糙，但 **COM 已卡死时仍可用**）：PowerShell 取 `MainWindowTitle` 抠 `[...]`",
    "  ⇒ ★★ **为什么不能只用 COM**：回收脚本的使用场景**正是 COM 可能已经卡死**，那时连接建不起来 ✓",
    "- ★ 裁决**必报 `path_used`**；★ **两条都探不通 ⇒ `ok=False` 且说清是「探不通」**，",
    "  ★ **绝不是「会话干净」**（这两种含义完全不同）✓",
    "- ★ 回收脚本已**委托**：`_OURS` 就是共用的那个正则（★ 测试专门钉住「不是又写了一份」）✓",
    "- ★ 过程中修掉**两个我自己的漏**：`*` 在**括号外且隔空格**的形态被漏掉两次",
    "  ⇒ ★ 未保存标记丢失**是危险方向**（会让人以为杀进程安全）⇒ 已补，并配 3 条测试 ✓",
    "- 测试：**18 passed**（本文件 10 条 + 预检 8 条）",
    "",
    "**B5-2b · 把预检接进护栏**：`tools/sw_guard.py` 在**放行探针之前**先跑 `session_verdict`，",
    "★ 有非我方文档就**拒绝开始**；★ 并处理评审点的设计点 ——",
    "「**启动 SolidWorks 之前先问一次、连上之后再问一次**」（★ 前者区分「没在运行」与「在运行但没文档」）✓",
    "判据：★ 一条测试证明「会话不干净时护栏**不放行**」；★ 一条证明两次点名都真的发生 ✓",
    "",
]

lines = s.splitlines()
out, i, hit = [], 0, False
while i < len(lines):
    if lines[i].startswith("## 下一个动作"):
        hit = True
        out += NEW
        i += 1
        while i < len(lines) and not lines[i].startswith("## "):
            i += 1
        continue
    out.append(lines[i])
    i += 1
assert hit, "没找到「下一个动作」段"
s2 = "\n".join(out) + "\n"
s2 = s2.replace("- **B5 隔离与预检**：进行中（B5-1 完成；B5-2..B5-5 未开始）",
                "- **B5 隔离与预检**：进行中（B5-1 完成 · B5-2 的提助手完成；"
                "**B5-2b 接线** / B5-3 / B5-4 / B5-5 未开始）")
s2 = s2.replace("## 调整（计划变更记在这里）",
                "## 调整（计划变更记在这里）\n\n"
                "- 2026-10-06：★ 本轮我的更新脚本**又栽在引号嵌套上**（把中文引号套进 ASCII 引号里 ⇒ SyntaxError，"
                "⇒ 目标栏与任务表**没被改写**，我一度以为写了；★ 而且 PowerShell **不支持 heredoc**）"
                "⇒ ★ **长文本一律走独立脚本文件**（事实 48 定则①）✓\n")
g.write_text(s2, encoding="utf-8")
print("goal-bar 已更新:", "B5-2b" in s2)
print("阶段行已改:", "B5-2 的「提共用助手」已完成" in s2)

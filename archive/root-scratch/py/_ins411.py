import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           411 🎯 **Spec Kit `067`：查一个「守了每轮收尾」的检查 —— 它在****漏检约 98%******（轮 148）——
               起因：`066` 留的「未查明」（BMP 1460 vs PNG 1232）⇒ 第一步去**找 SolidWorks 主窗口**
               量 `GetWindowRect` ⇒ ★★ **一找就发现**：
               ```
               PID 20456 的顶层窗口 **49 个，可见的只有 1 个（159x27）**
               ⇒ **主框架窗口不可见**（而 SolidWorks 照常工作：能建模、能截图）
               ```
            412 ★★★ **由此查出一个真问题**：
               ```
               我每轮收尾都跑的「查残留模态框」判据是：
                   EnumWindows + **IsWindowVisible(h)** + 类名 == "#32770"
               ⇒ **49 个窗口里只有 1 个可见** ⇒ 那个过滤**漏掉 48 个（约 98%）**
               ```
               ⚠ **精确说法不是**「它从未验证过任何东西」——★ **我第一时间的判断过重了**，
                 量完两个口径的对比后改正：
               ```
               默认（不过滤可见性）: #32770 = 0 · 扫到窗口 **49**
               旧口径（只可见）    : #32770 = 0 · 扫到窗口 **1**
               ⇒ 它**确实扫到那 1 个**，但**漏掉了 48 个**
               ```
               ⇒ **风险面**：那条检查守的是**每轮收尾的安全底线**（模态框会把会话**永久挂起**，
                 铁律 2 的头号风险）⇒ **漏检 98% 意味着这条底线基本没兜住。**
            413 ★ **同族的第三种载体：「同一个检查被复制 21 份」** ——
               `tools/` 下有 **21 个文件**各复制了一份 `def modal_dialogs(...)` ⇒
               ★ **没有单一真源**，而 21 份里的**每一份都带着同一个错误口径**
               ⇒ 与事实 74/78/79 的「同义词没有单一真源」**同族**，只是载体从"名字"变成"**被复制的代码**"。
            414 ★ **处置**：抽成共享 `sw_connect.residual_dialogs(pid, *, only_visible=False)`：
               ① **默认不过滤可见性** · ② ★★ **返回 `(dialogs, all_windows)` 两元组**
               （空列表只有在 `all_windows > 0` 时才有意义，否则分不清「没有」与「没扫到」）。
               ⇒ 新口径实测扫到 **49** 个窗口 ⇒ **判据不再空转** ✓
               ⚠ **21 份的全量迁移本轮未做**（只做示范 + 4 条测试）。
            415 ★★★ **本轮的形状：去解一个「未查明」，解出了一个真问题** ——
               ★ 与 `051`/`062`/`064`/`065` **同一个形状**（为了补一格而去看，看到的往往不止那一格）
                 —— **这是本会话第 5 次。**
               ★ 而这次我**没有把话说重**：先去量两个口径的对比，再决定怎么说
                 （按事实 82/142 的纪律）。
               ⚑ **未查证**：⚠ **21 份只迁移了示范**；⚠ **没有**构造真模态框验证新判据能抓到
                 （只证了"扫到的窗口数 1 → 49"）；⚠ 「窗口 vs 绘图区」**仍未查明**
                 （本轮只发现**前提站不住**）；⚠ SolidWorks 为何主窗口不可见**未查**。
               已知事实 **88** 入库 · 回归 **1224 passed** · `release_check` exit 0。
               下轮候选：① **把 21 份复制全量换成共享函数**（本轮只做了示范）；
               ② 查 SolidWorks 主窗口为何不可见；③ 回到「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+411 ", before, re.M):
    print("  游标 411 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+415 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 415 行已存在 ✓")

import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/probe_window_vs_graphics.py + `_list_sw_windows_all.py`（**真机**，轮 148）："
      "SolidWorks PID 的顶层窗口 **49 个，其中可见的只有 1 个（159x27）** ⇒ "
      "`sw_connect.residual_dialogs` 的**两个口径对比**：默认扫到 **49** 个窗口、"
      "旧口径（`IsWindowVisible`）只扫到 **1** 个 ⇒ **漏检 48/49**")
L = ("★★★ **2026-10-01（轮 148）查出一个"守了每轮收尾"的检查在**漏检**：此前 **21 个工具**"
     "各复制了一份"查残留模态框"的代码，**每份都带 `IsWindowVisible` 过滤**；"
     "而实测 SolidWorks 的 **49 个顶层窗口里只有 1 个可见** ⇒ **那个过滤漏掉 48 个（≈98%）**。"
     "⚠ 精确说法**不是**"它从未验证过任何东西"（它确实扫到那 1 个），而是"**它漏掉了 48 个**" ——"
     "⇒ 它**可能漏掉真正的模态框**，而模态框会把会话**永久挂起**（铁律 2 的头号风险）。"
     "⇒ 处置：抽成**共享**函数 `sw_connect.residual_dialogs(pid, only_visible=False)`，"
     "**默认不过滤可见性**，并**把扫到的窗口总数一并返回**（空列表才能与"没扫到"区分开）。"
     "⚠ **21 份复制的迁移本轮只做了示范**（未全量替换）⇒ 其余仍带旧过滤。")
for c in d["capabilities"]:
    if c.get("id") in ("part_and_features",):
        c["limitations"].insert(0, L)
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        print("  ok %s 已更新" % c["id"])
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 88 | " + "".join([
    "**「查残留模态框」这个检查在**漏检 98%** —— 因为 21 份复制都带了 `IsWindowVisible` 过滤** —— ",
    "2026-10-01（轮 148）实测：SolidWorks PID 的顶层窗口 **49 个，可见的只有 1 个（159x27）** ⇒ ",
    "`EnumWindows` + `IsWindowVisible` 的旧口径**只扫到 1 个**，漏掉 48 个。",
    "⚠⚠ 精确说法**不是**「它从未验证过任何东西」（它确实扫到那 1 个），而是「**它漏掉了 48 个**」——",
    "★ 我第一时间的判断过重了，**查完两个口径的对比数字后改正**（事实 82/142 的同一纪律）。",
    "⇒ 风险面：那条检查守的是**每轮收尾的安全底线**（模态框会把会话**永久挂起**，铁律 2 的头号风险）",
    "⇒ 处置：抽成**共享**函数 `sw_connect.residual_dialogs(pid, only_visible=False)`：",
    "**默认不过滤可见性** + **返回 `(dialogs, all_windows)` 两元组**",
    "（★ 空列表只有在 `all_windows > 0` 时才有意义 —— 否则分不清"没有"与"没扫到"）。",
    "★★ 这与事实 74/78/79 的「同义词没有单一真源」**同族**：这次的形态是",
    "「**同一个检查被复制 21 份，于是没有单一真源**」—— 而 21 份里的**每一份都带着同一个错误口径**。",
    "⚠ 21 份的**全量迁移本轮未做**（只做了示范 + 测试）⇒ 其余仍带旧过滤。 | ",
    "`scripts/sw_connect.py` 的 `residual_dialogs`；`tests/test_residual_dialogs.py`（4 条）；",
    "`tools/probe_window_vs_graphics.py`；事实 62 / 79 / 81 / 84 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "漏检 98%" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 88")
else:
    print("  已有 88")

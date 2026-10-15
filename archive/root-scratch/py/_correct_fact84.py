import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 就地更正事实 84 的定性（轮 143 我写的是"危险设计"）────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
MARK = "**★★★ `sw_connect.get_com_member` 在「取」一个 COM 方法时会真的把它调一次"
CORRECT = ("〔⚠⚠ **2026-10-01 轮 144 就地更正定性**：本条轮 143 标题写的是「**危险设计**」——"
           "审完 **471** 个无实参调用点后**改判**：**这不是缺陷，是被依赖的特性**"
           "（`get_com_member(study, RunAnalysis)` 拿返回码 · `get_com_member(view, Activate)` "
           "就是要激活 · `get_com_member(fm, InsertMoldShutOffSurface)` 就是要建面 —— "
           "**作者是故意这么用的**）。⇒ ★ 已把它写成 **「取或调」** 的正式语义 + 加了 "
           "`get_com_member_raw`（**只取不调**）作安全替代。"
           "⇒ 真正的风险**不是**"它会调"，而是「**名字读不出来它在调**」："
           "471 个无实参站点里 **193** 处的成员在反射里有**零参重载**（探测调用**会执行**），"
           "其中绝大多数是**只读 getter**（无害 ✓），**24** 处名字像「改东西」"
           "（`Insert*`/`Run*`/`Mesh*`/`Scale`/`Update*`…）⇒ **需人工确认作者是不是故意的**；"
           "⚠ 我只逐条看了其中 **8** 处。〕 ")
if MARK in tk and "轮 144 就地更正定性" not in tk:
    tk = tk.replace(MARK, CORRECT + MARK, 1)
    K.write_text(tk, encoding="utf-8")
    print("  ok 事实 84 的定性已就地更正")
else:
    print("  事实 84 已有更正或锚点不符: %s" % (MARK in tk))

# ── ② 已知事实 85 ────────────────────────────────────────────────
FACT = "| 85 | " + "".join([
    "**「取即调」的审计方法与影响面量化** —— 2026-10-01（轮 144）：",
    "用**结构**判据审 `get_com_member` 的语义（`tools/audit_get_com_member_semantics.py` + ",
    "零参重载对照）：**471** 个无实参调用点 ⇒ **193** 处的成员在出厂反射里**有零参重载**",
    "（⇒ 探测调用**会成功执行**），其中绝大多数是**只读 getter**（无害 ✓）；",
    "按「名字像改东西」的前缀缩清单得 **24** 处（`Insert*`/`Run*`/`Mesh*`/`Scale`/`Update*`…）。",
    "★★ **逐条读过 8 处后改判**：**这不是缺陷，是被依赖的特性**（作者故意用「取」来「调」）。",
    "⇒ ★ 处置：把它写成正式的 **「取或调」** 语义 + 新增 `get_com_member_raw`（**只取不调**）；",
    "**没有**改成「永不调用」（那会打断 193 处依赖）。",
    "★★ 教训：**「一个函数做了名字没写的事」≠「这个函数是错的」** —— ",
    "判它之前必须**先看调用点的意图**；本会话在轮 143 先判成「危险设计」，",
    "轮 144 审完 **471** 处后**改判**（与事实 70 / 事实 82 的"自我更正"同族）。",
    " | `tools/audit_get_com_member_semantics.py`；`scripts/sw_connect.py` 的 `get_com_member` ",
    "docstring + `get_com_member_raw`；事实 84（已就地更正定性）|",
])
if "「取即调」的审计方法与影响面量化" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 85")
else:
    print("  已有 85")

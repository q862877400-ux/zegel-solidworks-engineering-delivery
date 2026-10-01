import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# 能力条目：把两条新测的加进 evidence
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/probe_slot_and_point_shapes.py（**真机**，SW 2026 SP4.1 / 34.4.1）："
      "★ **推翻轮 141 的一概而论** —— `get_sketch_slots` 画 1/2 个 ⇒ **1/2** 个 `CDispatch`；"
      "`get_sketch_points` 画 1/2 条直线 ⇒ **2/4** 个（**每条线两个端点**）"
      "⇒ **这两条返回对象列表**，而 `get_lines`/`get_arcs`/`get_ellipses` 返回数值数组")
for c in d["capabilities"]:
    if c.get("id") in ("part_and_features", "sketch_query"):
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        print("  ok %s 已加证据" % c["id"])
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# 已知事实 83：更正的**方法**教训
FACT = ("| 83 | **「更正一处过度概括」时，判据必须区分「引用」与「主张」** —— 2026-10-01（轮 142）："
        "轮 141 我写过「`get_*` 系列**都**返回数值数组」，本轮实测**推翻**它"
        "（`get_sketch_slots` 画 1/2 个 ⇒ **1/2** 个 `CDispatch`；`get_sketch_points` 画 1/2 条直线 ⇒ "
        "**2/4** 个，每条线两个端点 ⇒ **这两条是对象列表**）⇒ 在 **7 处**（能力条目 ×2 · docstring ×2 · "
        "契约测试注释 · 已知事实 82 · ROADMAP 日志）就地更正。"
        "⚠⚠ 而写「不许再一概而论」的判据时**第一版就红了** —— 因为**更正文字本身引用了那句错话**"
        "（\"此处原写「…」——那是错的\"）⇒ ★ **一个'禁词'判据，必须先能区分「引用」与「主张」**，"
        "否则它会把'记录错误'当成'犯错'。修法：每一处出现，**必须在它前面 40 字内**有「原写」或「更正」。"
        "★ 规律**候选**（⚠ n=5，当假设不当定则）：**曲线类取法 ⇒ 数值数组；点/实体类取法 ⇒ 对象列表**。"
        "★ 日志（ROADMAP 游标）**不重写**，而是在当场加一条**指向更正的标记**。 | "
        "`tools/probe_slot_and_point_shapes.py`；`tests/test_sw_sketch_contract.py`（**20 条**，含"
        "「区分引用与主张」的判据）；事实 81 / 82 |")

K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "「更正一处过度概括」时" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 83")
else:
    print("  已有 83")

import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python -m pytest tests/test_modal_dialogs_can_fire.py（**2 passed**）：起一个**真的 `#32770`**"
      "（`tools/fake_modal_dialog.py`，**故意不置 `WS_VISIBLE`**）作靶子 ⇒ "
      "★ 新口径**抓得到**它、★ 旧口径（`only_visible=True`）**确实漏掉**它 "
      "⇒ **「漏检」从说法变成了可复现的演示**")
L = "".join([
    "★★★ **2026-10-01（轮 150）补上了轮 149 缺的那一步**：",
    "轮 149 只证明了判据「**在扫**」（窗口数 1 → 49），**没有**证明它**真能抓到一个模态框**",
    " ⇒ 本轮起了个**真的 `#32770`** 当靶子：新口径抓得到、旧口径漏掉 ⇒ **可复现**。",
    "⚠ 靶子与测试都在仓库里（`tools/fake_modal_dialog.py` + ",
    "`tests/test_modal_dialogs_can_fire.py`），**不连 COM**、只在被测进程里建一个窗口。",
])

for c in d["capabilities"]:
    if c.get("id") == "part_and_features":
        c["limitations"].insert(0, L)
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        print("  ok part_and_features 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 90 | " + "".join([
    "**判据「能不能响」要拿**真靶子**证 —— 本轮做到了：造一个真 `#32770`，新口径抓得到、旧口径漏掉** —— ",
    "2026-10-01（轮 150）：`tools/fake_modal_dialog.py` 用 Win32 预定义对话框类 `#32770` 造窗口，",
    "**故意不置 `WS_VISIBLE`** ⇒ `tests/test_modal_dialogs_can_fire.py`（**2 passed**）：",
    "① 新口径（不过滤可见性）**抓得到**它；② 旧口径（`only_visible=True`）**确实漏掉**它。",
    "★ 这把事实 88 的「漏检 48/49」从一个**说法**变成了**可复现的演示**（事实 62 的正向落点）。",
    "⚠⚠ 本轮踩了两个坑，都记下：① **`0x10000000` 就是 `WS_VISIBLE`**（我把它当成了 `WS_OVERLAPPED`，",
    "而后者的值是 `0x00000000`）⇒ 第一版靶子窗口**是可见的** ⇒ 对照不成立 ⇒ 去掉即修；",
    "② ★ **`Stop-Process -Name python` 会杀掉所有 python 进程**（我用它清理靶子 ⇒ 险些误伤），",
    "**必须按具体 PID 杀**（已确认本次没弄坏环境：SolidWorks 仍连得上、COM 正常）。",
    " | `tools/fake_modal_dialog.py`；`tests/test_modal_dialogs_can_fire.py`（2 条）；事实 62 / 88 / 89 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "能不能响" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 90")
else:
    print("  已有 90")

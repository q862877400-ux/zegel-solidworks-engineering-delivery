import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

EV = ("python tools/verify_interference_smoke.py（**真机**，轮 159，两个 40×40×20 的块沿 X 偏 20mm ⇒ "
      "重叠区 **20×40×20**）：**6/6** —— 干涉数 = **1**；★★★ **干涉体积读回 15999.999999999998**"
      "（期望 **16000 mm³** ⇒ **算得出来、对得上**）；`GetComponentCount = [2]`")
L = ("★★★ **2026-10-01（轮 159）`get_interference_detection` 三处成员名全错，已修**"
     "（① `asm_model.InterferenceDetection` ⇒ 官方 **`InterferenceDetectionManager`**；"
     "② `GetInterference(index)` ⇒ 官方 **`GetInterferences()`**（复数）；"
     "③ `item.Name` ⇒ `IInterference` 上**没有 `Name`**，改用 **`Volume` / `GetComponentCount`**）。"
     "⚠⚠ **三处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）。"
     "★★ 修后真机 **6/6**，且有一条**极强的定量判据**：两块的干涉体积读回 "
     "**15999.999999999998 mm³** 对上 **20×40×20 = 16000** —— **算得出来、对得上**。"
     "★ 怎么查出来的：新探针 `tools/probe_direct_member_access.py`（**直接属性访问**那一类，"
     "正是 `check_member_names.py` 的盲区）—— 对象名**从 `get_com_member(<OBJ>, …)` 的第一个实参推导**"
     "（不是猜），把 323 处收窄到 12 处，**命中了这 2 个真缺陷**。")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "assembly":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok assembly 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 99 | " + "".join([
    "**`get_interference_detection` 三处成员名全错 ⇒ 此前**静默降级**；修后**体积定量**对上 16000 mm³** —— ",
    "2026-10-01（轮 159）由**新探针** `tools/probe_direct_member_access.py` 查出：",
    "① `asm_model.InterferenceDetection` ⇒ 官方（出厂反射 `get_InterferenceDetectionManager()`）是 **`InterferenceDetectionManager`**（**带 Manager**）；",
    "② `GetInterference(index)` ⇒ 官方是 **`GetInterferences()`**（**复数**，无单数版）；",
    "③ `item.Name` ⇒ **`IInterference` 上根本没有 `Name`**（成员是 `Components` / `GetComponentCount` / ",
    "`GetInterferenceBody` / `IGetComponents` / `Ignore` / `IsFastener` / `IsPossibleInterference` / **`Volume`**）。",
    "⚠⚠ **三处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）—— ",
    "★ 与事实 62/79/88 同族（**「不报错的失败」最危险**）。",
    "★★★ 修后真机 **6/6**（`tools/verify_interference_smoke.py`，两个 40×40×20 的块沿 X 偏 20mm）：",
    "干涉数 = **1**；**干涉体积读回 `15999.999999999998`**，对上 **20×40×20 = 16000 mm³** ⇒ ",
    "**一个能独立算出来的物理量，读回来数值吻合** —— 这是本会话**最强的证据形态**（事实 86/87/96 那一族的升级版）。",
    "★★ **怎么找到的（可复用手法）**：`check_member_names.py` 只认 `get_com_member` 那一族**包装形态**，",
    "⇒ **直接属性访问**（`obj.Member(...)`）**是它的盲区** —— 而 `GetSldWorksObject`（事实 98）正是这个形态。",
    "★ 新探针的判据**有依据、不是猜**：把对象名**限定到「被当作 COM 对象用过」的那些** ",
    "（即 `get_com_member(<OBJ>, …)` 的**第一个实参标识符**）⇒ 323 处收窄到 **12 处**，**命中 2 个真缺陷**。",
    "⚠⚠ **反例也要记**：第一版判据「大驼峰 + 不在反射里」⇒ **假阳性率 ≈100%**（323 处全是 ",
    "`argparse` / `pywin32` / OCP / `winreg` 的对象）⇒ **已弃用**（事实 74 那一族）。",
    " | `tools/probe_direct_member_access.py`；`tools/verify_interference_smoke.py`（**6/6**）；",
    "`tests/test_interference_member_names.py`（4 条）；`C:\\swapi\\types\\IInterference\\`；事实 74 / 98 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "| 99 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 99")
else:
    print("  已有 99")

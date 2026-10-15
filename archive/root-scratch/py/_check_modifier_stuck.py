"""一锤定音：查**此刻**修饰键（Ctrl / Alt / Shift / Win）是不是卡在"按下"状态。

## 为什么这条能定案
`keybd_event(VK_CONTROL, 按下)` 之后**必须**有配对的 `KEYEVENTF_KEYUP`。
若中途抛异常（或进程被杀）⇒ **KEYUP 永远到不了** ⇒ 修饰键**卡在按下态**。
后果（**完全吻合用户报告**）：
* **Ctrl 卡住** ⇒ 按 `A` 变成 `Ctrl+A` = **全选（蓝底）**；按 `C` 变复制；点鼠标变 Ctrl+点击
* **Alt 卡住** ⇒ 菜单栏被激活、按键被吃掉
* ⚠ **它不需要周期性** —— 一次事故就够，持续到用户**单独按一下那个修饰键**为止

判据：`GetAsyncKeyState(vk) & 0x8000` 为真 = **此刻物理/逻辑上处于按下态**。
⚠ 读之前用户必须**没有**按着任何键（否则是我的读数在反映真实按键）。

# ── 来源 ──
# 仓库:   本项目自身（真机诊断）
# 文件:   D:\AI\SW\_check_modifier_stuck.py
# 定位:   定位「忽然 Ctrl / 忽然全选 / 忽然回车」是否为**修饰键卡住**。
# 官方依据: Win32 `GetAsyncKeyState`（Virtual-Key Codes：VK_SHIFT 0x10 / VK_CONTROL 0x11 /
#         VK_MENU 0x12 / VK_LWIN 0x5B / VK_RWIN 0x5C / VK_RETURN 0x0D）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 只读；不注入任何输入。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import sys

sys.stdout.reconfigure(encoding="utf-8")

user32 = ctypes.WinDLL("user32", use_last_error=True)
user32.GetAsyncKeyState.restype = ctypes.c_short
user32.GetAsyncKeyState.argtypes = [ctypes.c_int]

KEYS = [
    (0x10, "Shift（通用）"),
    (0xA0, "左 Shift"),
    (0xA1, "右 Shift"),
    (0x11, "Ctrl（通用）"),
    (0xA2, "左 Ctrl"),
    (0xA3, "右 Ctrl"),
    (0x12, "Alt（通用）"),
    (0xA4, "左 Alt"),
    (0xA5, "右 Alt"),
    (0x5B, "左 Win"),
    (0x5C, "右 Win"),
    (0x0D, "**Enter（回车）**"),
    (0x1B, "Esc"),
    (0x09, "Tab"),
]

print("此刻各修饰键的状态（GetAsyncKeyState & 0x8000 = 处于按下态）")
print("⚠ 读数前请**不要**按着任何键\n")
stuck = []
for vk, name in KEYS:
    s = user32.GetAsyncKeyState(vk)
    down = bool(s & 0x8000)
    if down:
        stuck.append(name)
    print("   0x%02X  %-18s %s" % (vk, name, "**按下** ← 卡住了？" if down else "抬起"))

print()
if stuck:
    print("🔴 **有 %d 个键此刻处于按下态**：%s" % (len(stuck), " · ".join(stuck)))
    print("   ⇒ 若你**此刻并没有**按着它们 ⇒ **就是这个在作怪**")
    print("   ⇒ 逐**单独按一下**每个卡住的键（只按它、别按别的）⇒ 再看现象是否消失")
else:
    print("✅ 此刻**没有**修饰键卡住（全为抬起）")
    print("   ⇒ 说明「卡住」不是当前状态。若有症状，是**每次被某个程序临时卡住**，")
    print("     或另有来源 ⇒ 需要在症状**正在发生的那一刻**再跑一次本脚本（对比读数）。")

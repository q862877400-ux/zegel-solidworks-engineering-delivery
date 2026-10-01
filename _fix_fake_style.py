import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\fake_modal_dialog.py")
t = P.read_text(encoding="utf-8")
OLD = '''#: ⚠ **故意不置 `WS_VISIBLE`** —— 复现旧判据的失效模式。
STYLE = 0x80000000 | 0x10000000          # WS_POPUP | WS_OVERLAPPED（**无 WS_VISIBLE**）'''
NEW = '''#: ⚠ **故意不置 `WS_VISIBLE`** —— 复现旧判据的失效模式。
#: ⚠⚠ **第一版这里写错了**：`0x10000000` **就是 `WS_VISIBLE`**（不是 `WS_OVERLAPPED`，
#:    后者是 `0x00000000`）⇒ 结果窗口**可见**（实测 `visible=1`）⇒ 对照不成立。
#: ⇒ 只用 `WS_POPUP`。
WS_POPUP = 0x80000000
WS_VISIBLE = 0x10000000          #: 本夹具**故意不置**它
STYLE = WS_POPUP'''
assert OLD in t, "样式锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 样式已修（去掉误写的 WS_VISIBLE）")

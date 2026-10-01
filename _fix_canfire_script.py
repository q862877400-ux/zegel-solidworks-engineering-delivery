import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\_add_canfire_evidence.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
#: 把 L12-L14 那三段坏掉的长字符串重写成**每行都闭合**的形式
start = next(i for i, l in enumerate(lines) if l.strip().startswith('L = ("★★★'))
end = next(i for i in range(start, len(lines)) if lines[i].rstrip().endswith(')'))
NEW = [
    'L = "".join([\n',
    '    "★★★ **2026-10-01（轮 150）补上了轮 149 缺的那一步**：",\n',
    '    "轮 149 只证明了判据「**在扫**」（窗口数 1 → 49），**没有**证明它**真能抓到一个模态框**",\n',
    '    " ⇒ 本轮起了个**真的 `#32770`** 当靶子：新口径抓得到、旧口径漏掉 ⇒ **可复现**。",\n',
    '    "⚠ 靶子与测试都在仓库里（`tools/fake_modal_dialog.py` + ",\n',
    '    "`tests/test_modal_dialogs_can_fire.py`），**不连 COM**、只在被测进程里建一个窗口。",\n',
    '])\n',
]
lines[start:end + 1] = NEW
t = "".join(lines)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")

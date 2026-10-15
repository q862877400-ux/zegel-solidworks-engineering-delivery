import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_no_uncalled_helpers.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)

a = next(i for i, l in enumerate(lines) if l.startswith("def _suspects() -> list:"))
b = next(i for i, l in enumerate(lines) if l.startswith("def test_no_uncalled_helpers_in_gates_and_tools():"))
lines[a:b] = [
    "def _suspects() -> list:\n",
    '    """调**探针自己的** `find_uncalled`（不重写逻辑 —— 否则测的不是工具）。"""\n',
    "    _checked, suspects = probe.find_uncalled()\n",
    "    return [s for s in suspects if s[2] not in UNCALLED_EXEMPT]\n",
    "\n",
    "\n",
]
c = next(i for i, l in enumerate(lines) if l.startswith("def _fake_suspects(root: Path) -> list:"))
lines[c:] = [
    "def _fake_suspects(root: Path) -> list:\n",
    '    """在**指定的 root** 上跑**同一个** `find_uncalled`（给负例用）。"""\n',
    "    _checked, suspects = probe.find_uncalled(\n",
    '        root, search_dirs=("tools",), patterns=("tools/check_*.py",))\n',
    "    return list(suspects)\n",
]
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 测试已改为调真函数（不再自己重写逻辑）")

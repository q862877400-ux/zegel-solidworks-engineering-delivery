import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_uncalled_helpers.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)

start = next(i for i, l in enumerate(lines) if l.startswith("def main() -> int:"))
mark = next(i for i in range(start, len(lines)) if "扫过的" in lines[i])

Q = chr(34)      # 双引号
NEW = [
    "def find_uncalled(root=None, *, search_dirs=None, patterns=None):\n",
    '    """返回 `(checked, suspects)` —— `suspects` 是 `[(相对路径, 行号, 函数名), …]`。\n',
    "\n",
    "    ⚑ **把判法抽出来**，让 `main()` 与测试**跑同一份代码** ——\n",
    "    否则负例测的是「测试自己重写的一份」，那不叫测到了工具（事实 62 的精神）。\n",
    '    """\n',
    "    root = Path(root) if root is not None else ROOT\n",
    "    dirs = tuple(search_dirs) if search_dirs else SEARCH_DIRS\n",
    "    pats = tuple(patterns) if patterns else PATTERNS\n",
    "\n",
    "    corpus = {}\n",
    "    for d in dirs:\n",
    "        for p in (root / d).rglob(" + Q + "*.py" + Q + "):\n",
    "            corpus[p] = p.read_text(encoding=" + Q + "utf-8" + Q + ", errors=" + Q + "replace" + Q + ")\n",
    "\n",
    "    targets = []\n",
    "    for pat in pats:\n",
    "        targets.extend(sorted(root.glob(pat)))\n",
    "\n",
    "    suspects, checked = [], 0\n",
    "    for p in targets:\n",
    "        for name, lineno in module_defs(p):\n",
    "            if name in ENTRY_POINTS:\n",
    "                continue\n",
    "            checked += 1\n",
    "            word = re.compile(r" + Q + "\\b%s\\b" + Q + " % re.escape(name))\n",
    "            hits = 0\n",
    "            for q, text in corpus.items():\n",
    "                for i, line in enumerate(text.splitlines(), 1):\n",
    "                    if not word.search(line):\n",
    "                        continue\n",
    "                    if q == p and i == lineno:\n",
    "                        continue\n",
    "                    if line.strip().startswith(" + Q + "#" + Q + "):\n",
    "                        continue\n",
    "                    hits += 1\n",
    "            if hits == 0:\n",
    "                try:\n",
    "                    rel = str(p.relative_to(root))\n",
    "                except ValueError:\n",
    "                    rel = str(p)\n",
    "                suspects.append((rel, lineno, name))\n",
    "    return checked, suspects\n",
    "\n",
    "\n",
    "def main() -> int:\n",
    "    checked, suspects = find_uncalled()\n",
]
lines[start:mark] = NEW
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 探针已抽出 find_uncalled(root)")

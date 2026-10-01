import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 探针：把判法抽成 find_uncalled(root)，main() 与测试都用它
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_uncalled_helpers.py")
t = P.read_text(encoding="utf-8")

OLD_MAIN = '''def main() -> int:
    corpus: dict[Path, str] = {}
    for d in SEARCH_DIRS:
        for p in (ROOT / d).rglob("*.py"):
            corpus[p] = p.read_text(encoding="utf-8", errors="replace")

    targets: list[Path] = []
    for pat in PATTERNS:
        targets.extend(sorted(ROOT.glob(pat)))

    suspects, checked = [], 0
    for p in targets:
        own = p.read_text(encoding="utf-8", errors="replace")
        for name, lineno in module_defs(p):
            if name in ENTRY_POINTS:
                continue
            checked += 1
            word = re.compile(r"\\b%s\\b" % re.escape(name))
            hits = 0
            for q, text in corpus.items():
                for i, line in enumerate(text.splitlines(), 1):
                    if not word.search(line):
                        continue
                    if q == p and i == lineno:
                        continue
                    if line.strip().startswith("#"):
                        continue
                    hits += 1
            if hits == 0:
                suspects.append((str(p.relative_to(ROOT)), lineno, name))
'''
NEW_MAIN = '''def find_uncalled(root: Path = None, *, search_dirs=None, patterns=None):
    """返回 `(checked, suspects)` —— `suspects` 是 `[(相对路径, 行号, 函数名), …]`。

    ⚑ **把判法抽出来**，让 `main()` 与测试**跑同一份代码**
    （否则负例测的是"测试自己重写的一份"，那不叫测到了工具 —— 事实 62 的精神）。
    """
    root = Path(root) if root is not None else ROOT
    dirs = tuple(search_dirs) if search_dirs else SEARCH_DIRS
    pats = tuple(patterns) if patterns else PATTERNS

    corpus: dict[Path, str] = {}
    for d in dirs:
        for p in (root / d).rglob("*.py"):
            corpus[p] = p.read_text(encoding="utf-8", errors="replace")

    targets: list[Path] = []
    for pat in pats:
        targets.extend(sorted(root.glob(pat)))

    suspects, checked = [], 0
    for p in targets:
        for name, lineno in module_defs(p):
            if name in ENTRY_POINTS:
                continue
            checked += 1
            word = re.compile(r"\\b%s\\b" % re.escape(name))
            hits = 0
            for q, text in corpus.items():
                for i, line in enumerate(text.splitlines(), 1):
                    if not word.search(line):
                        continue
                    if q == p and i == lineno:
                        continue
                    if line.strip().startswith("#"):
                        continue
                    hits += 1
            if hits == 0:
                try:
                    rel = str(p.relative_to(root))
                except ValueError:
                    rel = str(p)
                suspects.append((rel, lineno, name))
    return checked, suspects


def main() -> int:
    checked, suspects = find_uncalled()
'''
assert OLD_MAIN in t, "main 锚点不符"
t = t.replace(OLD_MAIN, NEW_MAIN, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 探针已抽出 find_uncalled(root)")

# ② 测试：改成调真函数
Q = Path(r"C:\swprojects\sw-skill-fork\tests\test_no_uncalled_helpers.py")
tq = Q.read_text(encoding="utf-8")
i = tq.index("def _suspects() -> list:")
j = tq.index("def test_no_uncalled_helpers_in_gates_and_tools():")
tq = tq[:i] + '''def _suspects() -> list:
    """调**探针自己的** `find_uncalled`（不重写逻辑 —— 否则测的不是工具）。"""
    _checked, suspects = probe.find_uncalled()
    return [s for s in suspects if s[2] not in UNCALLED_EXEMPT]


''' + tq[j:]

#: 负例也改成调真函数
k = tq.index("def _fake_suspects(root: Path) -> list:")
tq = tq[:k] + '''def _fake_suspects(root: Path) -> list:
    """在**指定的 root** 上跑**同一个** `find_uncalled`（给负例用）。"""
    _checked, suspects = probe.find_uncalled(root, search_dirs=("tools",),
                                            patterns=("tools/check_*.py",))
    return list(suspects)
'''
Q.write_text(tq, encoding="utf-8")
ast.parse(tq)
print("  ok 测试已改为调真函数（不再自己重写逻辑）")

"""★ 补上「用了 _ROOT_S 却没定义它」的文件（修我上一个脚本的 bug）。"""

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\AI\SW")
DIRS = ("scripts", "tools", "tests", "mcp-server", "apps", "agents", "subskills")
USE = "_ROOT_S"
DEF = re.compile(r"^_ROOT_S\s*=", re.M)


def main() -> int:
    files = []
    for d in DIRS:
        b = ROOT / d
        if b.is_dir():
            files += [p for p in b.rglob("*.py") if p.is_file()]
    need, fixed, bad = [], [], []
    for p in files:
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:                                      # noqa: BLE001
            continue
        if USE not in t or DEF.search(t):
            continue
        need.append(str(p.relative_to(ROOT)))
        d = len(p.relative_to(ROOT).parts) - 1
        lines = t.splitlines()
        #: ★ \u63d2\u5728\u6700\u540e\u4e00\u4e2a\u9876\u5c42 import \u4e4b\u540e\uff1b\u627e\u4e0d\u5230\u5c31\u63d2\u5728\u6e90\u7801\u5757\u4e4b\u540e\u7684\u7b2c\u4e00\u4e2a\u7a7a\u884c\u5904
        last = -1
        for i, l in enumerate(lines[:120]):
            if re.match(r"^(import |from )", l.rstrip()):
                last = i
        if last < 0:
            for i, l in enumerate(lines[:80]):
                if l.startswith("from __future__"):
                    last = i
        if last < 0:
            bad.append(str(p.relative_to(ROOT)))
            continue
        j = last + 1
        guard = 0
        while j < len(lines) and guard < 40:
            s = lines[j]
            if s.strip() and not s.startswith((" ", "\t", ")")) and not s.startswith("#"):
                break
            j += 1
            guard += 1
        ins = ["", "#: \u2605 \u672c\u4ed3\u5e93\u6839\uff08\u2605 2026-10-03 \u5408\u5e76\u540e\u81ea\u5b9a\u4f4d\uff09",
               "%s = str(Path(__file__).resolve().parents[%d])" % (USE, d)]
        new = "\n".join(lines[:j] + ins + lines[j:]) + "\n"
        new = new.replace("import ast\n", "import ast\n", 1)
        if "from pathlib import Path" not in new and "import pathlib" not in new:
            new = new.replace("from __future__ import annotations\n",
                              "from __future__ import annotations\n\nfrom pathlib import Path\n", 1)
        try:
            ast.parse(new)
        except SyntaxError as exc:
            bad.append("%s: %s" % (p.relative_to(ROOT), exc))
            continue
        p.write_text(new, encoding="utf-8")
        fixed.append((str(p.relative_to(ROOT)), d))
    print("  ★ \u9700\u8865\u5b9a\u4e49\uff1a**%d** \u4e2a\u6587\u4ef6" % len(need))
    for f, d in fixed:
        print("      \u2713 %-56s parents[%d]" % (f, d))
    if need and not fixed:
        print("      \uff08\u4e00\u4e2a\u90fd\u6ca1\u4fee\u6210\uff09")
    if bad:
        print("  **\u4fee\u4e0d\u4e86\uff1a%d**" % len(bad))
        for b in bad[:10]:
            print("      " + b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

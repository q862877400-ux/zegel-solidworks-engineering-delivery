"""★ 把 specs 里「验收命令」行上的旧代码仓绝对路径，改成仓库内相对路径。

★ 只改含 `→ 验收:` 的行 —— 那些是**可执行命令**，必须能再跑；
  叙述里出现的绝对路径**保留**（那是当时的历史记录，改了反而失真）。
"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
LIT = "C:\\swprojects\\sw-skill-fork"

#: ★ 顺序：长的先替换（否则 `\scripts` 会被裸前缀先吃掉）
REPS = [
    ("r'%s\\scripts'" % LIT, "'scripts'"),
    ("r'%s\\mcp-server'" % LIT, "'mcp-server'"),
    ("r'%s\\tools'" % LIT, "'tools'"),
    ("r'%s'" % LIT, "'.'"),
    ('r"%s\\scripts"' % LIT, '"scripts"'),
    ('r"%s\\mcp-server"' % LIT, '"mcp-server"'),
    ('r"%s"' % LIT, '"."'),
    (LIT + "\\", ""),          #: ★ 裸路径（如 PowerShell 的 -Path）
    (LIT, "."),
]

changed = []
for md in sorted((R / "specs").rglob("*.md")):
    raw = md.read_text(encoding="utf-8")
    if LIT not in raw:
        continue
    out, n = [], 0
    for line in raw.splitlines():
        if "→ 验收:" in line and LIT in line:
            for a, b in REPS:
                if a in line:
                    line = line.replace(a, b)
            n += 1
        out.append(line)
    if n:
        md.write_text("\n".join(out) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
        changed.append((str(md.relative_to(R)), n))

print("  ★ 改了 **%d** 个文件的验收行，共 **%d** 行" % (len(changed), sum(c for _, c in changed)))
for rel, c in changed:
    print("      %-58s %d 行" % (rel, c))
print()
#: ★ \u56de\u8bfb\uff08\u4e8b\u5b9e 48 \u5b9a\u5219\u2461\uff1a\u4e0d\u80fd\u53ea\u770b stdout\uff09
rem = []
for md in sorted((R / "specs").rglob("*.md")):
    for i, line in enumerate(md.read_text(encoding="utf-8").splitlines()):
        if "→ 验收:" in line and LIT in line:
            rem.append("%s:%d" % (md.relative_to(R), i + 1))
print("  ★ 回读：验收行里仍含旧路径的 **%d** 处 %s" % (len(rem), rem[:6]))

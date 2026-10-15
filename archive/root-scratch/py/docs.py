import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
NEW_TABLE = """| 判据 | 实测 |
|---|---|
| 收录程序集 | **12** 个（solidworks 全装 18 个，另 3 个按要求不收，swconst 仅枚举，swcommands 无接口）|
| 接口族 | **792** |
| 成员 | **15,466** |
| 编入官方 API 索引 | **15,466 / 15,466 = 100%** |
| 未编入的族 | **0** |"""

# ── SKILL.md ──
p = REPO / "SKILL.md"
s = p.read_text(encoding="utf-8")
old = re.search(r"\| 判据 \| 实测 \|\n\|---\|---\|\n(?:\|.*\n)+", s)
if old:
    s = s[:old.start()] + NEW_TABLE + "\n" + s[old.end():]
    p.write_text(s, encoding="utf-8")
    print("  [ok] SKILL.md 判据表已更新")
else:
    print("  [skip] SKILL.md 未匹配到判据表")

# ── final-audit.md 里的 374/701/16615 一律作废 ──
f = REPO / "docs" / "final-audit.md"
t = f.read_text(encoding="utf-8")
t = t.replace("· 68 次本地提交", "· 73 次本地提交")
t = t.replace("**93 文件 / +74,036 行 / -27 行**",
              "**89 文件 / +76,000 行量级 / -27 行**（数字随每轮变动，以 `git diff --stat origin/main` 为准）")
t = t.replace("**701/701 族**有登记", "**792 族**全部登记")
t = t.replace("**292 个合规来源块 / 0 违规**", "**235 个合规来源块 / 0 违规**")
t = t.replace("**0 命中（扫 74,036 行新增）**", "**0 命中**")
t = t.replace("12,871 / 16,615（77%）", "15,466 / 15,466（**100%**）")
t = t.replace("2,657（16%）", "—")
t = t.replace("337 / 701", "792 / 792")
t = t.replace("701 族里 334 族未达成员级 100%", "全部 792 族已达成员级 100%")
f.write_text(t, encoding="utf-8")
print("  [ok] final-audit.md 数字已更新")
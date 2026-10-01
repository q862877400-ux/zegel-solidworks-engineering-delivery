import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\final-audit.md")
t = P.read_text(encoding="utf-8")

FIXES = [
    # ① 提交数：215 -> 245（相对 origin/main 的增量）
    ("> · **215 次本地提交** · **零次远程写**",
     "> · **245 次本地提交**（相对 `origin/main` 的增量；本仓库总提交 **246**）· **零次远程写**\n"
     "> ⚑ 2026-10-01（轮 131）更正：此前写 **215**，已过时 —— 数字随提交增长，**改这一行时请重新数**：\n"
     "> `git rev-list --count origin/main..HEAD`"),
    # ② 能力条数：31 -> 36
    ("`docs/union-level-audit.md` 逐条列出 31 条能力的 `level`",
     "`docs/union-level-audit.md` 逐条列出 **36** 条能力的 `level`（⚑ 轮 131 更正：此前写 31）"),
]
for old, new in FIXES:
    if old in t:
        t = t.replace(old, new, 1)
        print("  ok 已更正: %s" % old[:44])
    else:
        print("  ⚠ 未命中: %s" % old[:44])
P.write_text(t, encoding="utf-8")
print("  现在 %d 行" % len(t.splitlines()))

# ③ 记一笔：审计报告的"刷新"意味着什么
print()
print("  ⚠ 提醒：'31 条存疑未定口径'那句是 **A3 口径**的另一回事，本轮**不动**（不是过时）")

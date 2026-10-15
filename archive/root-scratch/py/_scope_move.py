import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW\tools")
REPO = Path(r"C:\swprojects\sw-skill-fork")

#: 判据：脚本里**真的有 write 动作**，且目标路径拼到 REPO 下
WRITE = re.compile(r"\.write_text\(|\.write_bytes\(|open\([^)]*[\"']w|shutil\.copy|\.save\(")

print("  ── 工作区 tools/*.py：谁**真的写盘到代码仓库** ──")
move, keep = [], []
for p in sorted(WS.glob("*.py")):
    t = p.read_text(encoding="utf-8", errors="replace")
    mentions_repo = "sw-skill-fork" in t
    writes = bool(WRITE.search(t))
    #: 更强的判据：代码里出现 REPO/root 变量并用于写
    repo_path_var = bool(re.search(r'(REPO|ROOT|DEST|OUT)\w*\s*=\s*.*sw-skill-fork', t))
    verdict = "★ 产物落代码仓库 ⇒ 该搬" if (mentions_repo and writes) else "产物在工作区或纯读 ⇒ 留"
    (move if (mentions_repo and writes) else keep).append(p.name)
    print("  %-34s 写到仓库=%-5s 有写动作=%-5s %s" % (p.name, mentions_repo, writes, verdict))

print("")
print("  ⇒ 该搬的: %d 个" % len(move))
for n in move:
    print("      %s" % n)
print("  ⇒ 留工作区的: %d 个（产物在工作区仓库 ⇒ 同仓，无需搬）" % len(keep))
for n in keep:
    print("      %s" % n)

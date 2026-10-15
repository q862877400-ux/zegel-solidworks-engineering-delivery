import sys
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
import check_provenance as cp

p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part.py")
text = p.read_text(encoding="utf-8")
for s, e, f in cp._source_blocks(text):
    print("  块 L%d..L%d  文件=%s" % (s, e, str(f.get('文件'))[:40]))
print()
for n in (840, 875):
    hit = [ (s,e) for s,e,_f in cp._source_blocks(text) if s <= n <= e ]
    print("  L%d 被覆盖? %s" % (n, hit or "**否**"))

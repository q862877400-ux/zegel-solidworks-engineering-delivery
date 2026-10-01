import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\_measure_bbox_units.py")
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
out = [l for l in lines
       if "GetUserPreference" not in l and "未查文档单位设定" not in l and "对照：文档单位设定" not in l]
p.write_text("".join(out), encoding="utf-8")
print("  行数 %d -> %d" % (len(lines), len(out)))

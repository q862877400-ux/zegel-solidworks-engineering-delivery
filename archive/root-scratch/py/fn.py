import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
t = Path(r"D:\AI\SW\_raw\reflect\iface_swmotionstudy.txt").read_text(encoding="utf-8", errors="replace")
for l in t.splitlines():
    if "ForceOutputTimeStepChangeNotify" in l: print("  反射原文:", l.strip())
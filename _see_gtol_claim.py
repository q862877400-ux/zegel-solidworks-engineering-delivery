import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "scripts" / "sw_gtol.py").read_text(encoding="utf-8")
i = t.find("add_gtol_indicator     ❌")
print("  ── 那段「到不了」的原文 ──")
print(t[i:i + 1200])
print()
print("  ── 冒烟里的判据 ──")
s = (R / "tools" / "verify_gtol_smoke.py").read_text(encoding="utf-8")
for k, l in enumerate(s.splitlines(), 1):
    if "chk(" in l or "add_gtol_indicator" in l:
        print("    L%-4d %s" % (k, l.strip()[:100]))

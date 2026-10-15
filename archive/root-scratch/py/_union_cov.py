import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
NOT = re.compile(r"sw_api_|^sw_com_traps|^sw_connect|^sw_automation_knowledge|^sw_preflight")
caps = (ROOT / "capabilities.yaml").read_text(encoding="utf-8", errors="replace")

mods = sorted(p.stem for p in (ROOT / "scripts").glob("sw_*.py") if not NOT.search(p.stem))
never = []
for m in mods:
    t = (ROOT / "scripts" / (m + ".py")).read_text(encoding="utf-8", errors="replace")
    pub = [f for f in re.findall(r"^def (\w+)\(", t, re.M) if not f.startswith("_")]
    by_mod = bool(re.search(r"\b%s\b" % re.escape(m), caps))
    by_fn = any(re.search(r"\b%s\b" % re.escape(f), caps) for f in pub)
    if not (by_mod or by_fn):
        never.append((m, len(pub), pub[:5]))

print("模块 %d 个 ⇒ **两个信号都没有**的：**%d** 个" % (len(mods), len(never)))
print()
for m, n, ex in never:
    print("  **%s**（%d 个公开函数）" % (m, n))
    print("      %s" % ", ".join(ex))

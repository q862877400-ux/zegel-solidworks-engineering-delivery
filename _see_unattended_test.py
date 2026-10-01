import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
t = (R / "tests" / "test_unattended_equivalence.py").read_text(encoding="utf-8")
print("  ── 测试怎么拿基线 ──")
for m in re.finditer(r"(?m)^.*(baseline|BASELINE|json|load).*$", t):
    s = m.group(0).strip()
    if len(s) < 130:
        print("    %s" % s[:120])
print()
print("  ── 断言长什么样 ──")
i = t.find("def test_path1_unattended_allowed_set_matches_baseline")
print(t[i:i + 700])

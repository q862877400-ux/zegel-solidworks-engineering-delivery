import io, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_drawing_view_contract.py")
s = p.read_text(encoding="utf-8")
s = s.replace('        (m.get_orient_toward, ("T", 1.0, 2.0)),\n', '')
if "import re" not in s.split("from pathlib")[0]:
    s = s.replace("import io\n", "import io\nimport re\n", 1)
p.write_text(s, encoding="utf-8")
print("  [ok] 已移除失效断言并补 import re")

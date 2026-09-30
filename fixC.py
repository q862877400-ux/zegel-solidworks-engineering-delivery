import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
# 先从原来的位置拿掉
t = t.replace("    _dedupe_domains()\n    _assert_no_duplicate_families()",
              "    _assert_no_duplicate_families()", 1)
# 放到 unmapped 计算之后
old = "    unmapped = _unmapped_sldworks()"
assert old in t, "未找到 unmapped 计算点"
idx = t.index(old)
eol = t.index("\n", idx)
t = t[:eol+1] + "    _dedupe_domains()   # ⚑ 必须在**所有**族加进来之后去重\n" + t[eol+1:]
g.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  [ok] 去重已挪到所有族加入之后")
import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\merge_dims.py")
s = p.read_text(encoding="utf-8")
# 每张表后要闭合 —— 原来把条目和表头拼在一起，字典没闭合
s = s.replace('''            blocks.append("    %r: (" % f + "".join("        %r,\\n" % x for x in a) + "    ),")
            total["READONLY"] += len(a)
            blocks.append("    %r: (" % f + "".join("        %r,\\n" % x for x in b) + "    ),")
            total["WRITEONLY"] += len(b)
            blocks.append("    %r: (" % f + "".join("        %r,\\n" % x for x in h) + "    ),")
            total["HIDDEN"] += len(h)''',
'''            for tbl, items, key in (("READONLY", a, "READONLY"),
                                     ("WRITEONLY", b, "WRITEONLY"),
                                     ("HIDDEN", h, "HIDDEN")):
                body = "".join("    %r: (" % f + "".join("        %r,\\n" % x for x in items) + "    ),\\n")
                blocks.append("### %s\\n%s}\\n" % (tbl, body))
                total[key] += len(items)''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  脚本已修")
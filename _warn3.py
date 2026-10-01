import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch7.py")
tq = Q.read_text(encoding="utf-8")
warn = " \u26a0 May mark the document as modified (view/selection state changes count)."
D = '"'
ods = [
    "Activate the model for preview/review (prepares the document for capture).",
    "Clear the selection so the preview does not show highlighted entities.",
    "Refresh the graphics/scene graph, e.g. after an appearance change.",
]
n = 0
for o in ods:
    if o + warn + D in tq:
        continue
    if o + D in tq:
        tq = tq.replace(o + D, o + warn + D, 1)
        n += 1
Q.write_text(tq, encoding="utf-8")
print("  ok 本轮补了 %d 条（现在应 3 条都带警告）" % n)
print("  校验: 警告出现 %d 次" % tq.count(warn))
import ast
ast.parse(tq)
print("  语法 OK")

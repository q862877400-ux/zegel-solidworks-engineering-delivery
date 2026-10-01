import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_com_member_helpers.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if "assert \"就是去调它\" in doc" in l:
        lines[i] = '    assert "就是去调它" in doc, "要写明它是「就是去调它」"\n'
        print("  L%d 已修" % (i + 1))
    if "assert \"get_com_member_raw\" in doc" in l:
        lines[i] = '    assert "get_com_member_raw" in doc, "要指向「只取不调」那个替代"\n'
        print("  L%d 已修" % (i + 1))
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

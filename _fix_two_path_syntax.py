import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_mcp_protocol_layer.py")
lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
for i, l in enumerate(lines):
    if "钉死数量" in l:
        lines[i] = ('        "两条路径合计 %d 条，而协议层此前实测 86 条 ⇒ 数字变了就说明有人加了东西"\n'
                    '        "（**本测试是「钉死数量」的守卫，加了就要同时改这里**）" % n)\n')
        print("  L%d 已修" % (i + 1))
        break
P.write_text("".join(lines), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

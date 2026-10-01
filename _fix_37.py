import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_server_wiring.py")
t = P.read_text(encoding="utf-8")
OLD = "    assert len(all_specs()) == 37"
NEW = "    assert len(all_specs()) == 41"
assert OLD in t, "断言锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 断言 37 -> 41（docstring 里那句历史说明保留）")
# 核对：docstring 里的 "37" 是历史说明，不该改
print("  文件里还剩 %d 处 37（应为历史说明那 1 处）" % t.count("37"))

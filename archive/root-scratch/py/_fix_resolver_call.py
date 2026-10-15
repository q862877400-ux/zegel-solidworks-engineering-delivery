import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_batch10_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = "            host = resolver()          # ★ 走**真实**解析器"
NEW = ("            # ⚠ 解析器收一个 `_params`（调用方实参）—— 空 dict 即可，\n"
       "            #   因为本批 4 条的**宿主对象不需要从实参里推**\n"
       "            host = resolver({})        # ★ 走**真实**解析器")
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已给解析器传空实参 dict")

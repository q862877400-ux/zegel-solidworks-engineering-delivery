import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_gtol_contract.py")
t = P.read_text(encoding="utf-8")
n1 = t.count("tol_type=23")
n2 = t.count('GTOL_GEOM_SYMBOL["position"]')
t = t.replace("tol_type=23", "tol_type=22")
t = t.replace('GTOL_GEOM_SYMBOL["position"]', 'GTOL_GEOM_SYMBOL["parallelism"]')
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  tol_type=23 → 22：%d 处 · position → parallelism：%d 处" % (n1, n2))

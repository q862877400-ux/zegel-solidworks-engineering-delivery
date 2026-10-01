import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_export_bmp_contract.py")
t = P.read_text(encoding="utf-8")
OLD = '''    i = src.index("def export_to_bmp(")
    doc = src[i:i + 2200]'''
NEW = '''    i = src.index("def export_to_bmp(")
    #: ⚠ 判据窗口要**包含紧邻的来源块**（轮次标注在本仓的惯例是写在来源块里，
    #: 不是写在函数 docstring 里）⇒ 往前多取 2000 字。
    doc = src[max(0, i - 2000):i + 2200]'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据窗口已含来源块")

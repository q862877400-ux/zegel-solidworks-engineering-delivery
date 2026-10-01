import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_export_image_contract.py")
t = P.read_text(encoding="utf-8")
OLD = '''    _name, args = calls[-1]
    assert args[4] != None and args[5] != None, "两个 Object 入参不能是 None"  # noqa: E711
    assert args[4] == "EMPTY" and args[5] == "EMPTY", args[4:6]'''
NEW = '''    _name, args = calls[-1]
    #: ⚠ 下标要对：0=路径 1=Version 2=Options **3=ExportData 4=AdvancedSaveAsOptions**
    #: 5/6=两个 `out Int32`（出参占位）。**第一版我把 3/4 写成了 4/5** ⇒ 断言错。
    assert args[3] != None and args[4] != None, "两个 Object 入参不能是 None"  # noqa: E711
    assert args[3] == "EMPTY" and args[4] == "EMPTY", args[3:5]
    assert args[5] == ("OUT", 0) and args[6] == ("OUT", 0), args[5:7]'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 下标已修正")

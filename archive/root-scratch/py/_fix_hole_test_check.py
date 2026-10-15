import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features.py")
t = P.read_text(encoding="utf-8")

OLD = '''    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def _out_container")
    body = t[i:t.index("def _out_value", i)]
    assert "VT_BYREF" in body and "VT_VARIANT" in body
    assert "VT_DISPATCH" not in body, "VT_BYREF|VT_DISPATCH 是已知不可用的形态"
    assert "win32com.client" in body, "VARIANT 在 win32com.client 里，**不是** pythoncom.VARIANT"'''

NEW = '''    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def _out_container")
    body = t[i:t.index("def _out_value", i)]
    # ⚠ 查**实际构造那一行**，不查整段 ——
    #   文档串里**必须**提到 `VT_BYREF|VT_DISPATCH`（解释为什么不用它），
    #   查整段会被自己的说明文字误伤（**轮 119 踩过同一个坑**）。
    ctor = [l for l in body.splitlines()
            if "VARIANT(" in l and not l.strip().startswith("#")]
    assert ctor, "找不到构造出参容器的那一行"
    line = ctor[-1]
    assert "VT_BYREF" in line and "VT_VARIANT" in line, line
    assert "VT_DISPATCH" not in line, "VT_BYREF|VT_DISPATCH 是已知不可用的形态"
    assert "win32com.client" in body, "VARIANT 在 win32com.client 里，**不是** pythoncom.VARIANT"'''

assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改为查构造行；语法 OK")

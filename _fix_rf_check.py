import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_mcp_protocol_layer.py")
t = P.read_text(encoding="utf-8")
OLD = '''    assert "response_format" in inner, "框架应当补 response_format"
    assert set(inner["response_format"].get("enum") or []) == {"json", "markdown"}'''
NEW = '''    assert "response_format" in inner, "框架应当补 response_format"
    # ⚠ 它也是**一个 `$ref`**（指向 `$defs.ResponseFormat`），枚举在那边 ——
    #   不在 `inner["response_format"]` 里（**第一版又爬错了一层**）。
    rf_ref = inner["response_format"].get("$ref")
    assert rf_ref, "response_format 应当是一个 $ref"
    rf = schema["$defs"][rf_ref.rsplit("/", 1)[-1]]
    assert set(rf.get("enum") or []) == {"json", "markdown"}'''
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据已跟随 $ref 再进一层")

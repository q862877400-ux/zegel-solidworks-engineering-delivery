import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
t = T.read_text(encoding="utf-8")

OLD = '''    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for bad in ("`get_*` 系列都返回**数值数组**", "`get_*` 系列**都**返回数值数组"):
        assert bad not in src, "又出现一概而论的说法：%r" % bad
    #: ✓ 反过来：更正说明必须在
    assert "两种形状都有" in src, "要写明「两种形状都有」"'''

NEW = '''    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    bad = "get_*` 系列**都**返回数值数组"
    #: ⚠⚠ **判据要区分「引用」与「主张」**：更正文字**本身会引用那句错话**
    #:（"此处原写「…」——那是错的"）⇒ 不能一见到就报。
    #: 判据：每一处出现，**必须在它前面 40 字内**有「原写」或「更正」。
    idx = 0
    occurrences = 0
    while True:
        idx = src.find(bad, idx)
        if idx < 0:
            break
        occurrences += 1
        ctx = src[max(0, idx - 40):idx]
        assert ("原写" in ctx) or ("更正" in ctx), (
            "又出现**主张式**的一概而论（不是引用）：…%s…" % src[max(0, idx - 40):idx + len(bad) + 10])
        idx += len(bad)
    assert occurrences >= 1, "更正说明里应当**引用**那句错话（作为'原写'）"
    #: ✓ 反过来：更正说明必须在
    assert "两种形状都有" in src, "要写明「两种形状都有」"'''

assert OLD in t, "锚点不符"
T.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(T.read_text(encoding="utf-8"))
print("  ok 判据已改成「区分引用与主张」")

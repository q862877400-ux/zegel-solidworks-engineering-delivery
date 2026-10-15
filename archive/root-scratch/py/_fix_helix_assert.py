import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_helix_contract.py")
t = P.read_text(encoding="utf-8")

OLD = '''    m = _FakeModel(feature_name=None)
    with pytest.raises(RuntimeError) as ei:
        sw_helix.insert_helix(m, height_mm=10.0)
    msg = str(ei.value)
    assert "圆" in msg, msg
    assert "InsertHelix" in msg, msg'''

NEW = '''    m = _FakeModel(feature_name=None)
    with pytest.raises(RuntimeError) as ei:
        sw_helix.insert_helix(m, height_mm=10.0)
    msg = str(ei.value)
    assert "圆" in msg, msg
    # ⚑ 轮 121：取"最后加的特征"的成员从 `FirstFeature` 改成了
    #   `IModelDocExtension.GetLastFeatureAdded` ⇒ 错误信息里的成员名**跟着变**。
    assert "GetLastFeatureAdded" in msg, msg'''

if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 断言已跟着成员名更新")
else:
    print("  ⚠ 锚点不符")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

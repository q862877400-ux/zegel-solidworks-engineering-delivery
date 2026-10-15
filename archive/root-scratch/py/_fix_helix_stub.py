import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_helix_contract.py")
t = P.read_text(encoding="utf-8")

OLD = '''class _FakeModel:
    """桩：记下 10 个实参，并给一个"已建成"的特征。"""

    def __init__(self, feature_name="Helix1"):
        self.calls = []
        self._feat = _FakeFeature(feature_name) if feature_name else None

    def InsertHelix(self, *args):      # noqa: N802
        self.calls.append(args)

    @property
    def FirstFeature(self):
        return self._feat
'''

NEW = '''class _FakeExtension:
    """桩：`GetLastFeatureAdded()`（轮 121 改用它，不再用 `FirstFeature`）。"""

    def __init__(self, feat):
        self._feat = feat

    def GetLastFeatureAdded(self):      # noqa: N802
        return self._feat


class _FakeModel:
    """桩：记下 10 个实参，并给一个"刚加进去"的特征。"""

    def __init__(self, feature_name="Helix1"):
        self.calls = []
        self._feat = _FakeFeature(feature_name) if feature_name else None

    def InsertHelix(self, *args):      # noqa: N802
        self.calls.append(args)

    @property
    def Extension(self):      # noqa: N802
        return _FakeExtension(self._feat)
'''

if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 桩已改为 Extension.GetLastFeatureAdded")
else:
    print("  ⚠ 桩锚点不符")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

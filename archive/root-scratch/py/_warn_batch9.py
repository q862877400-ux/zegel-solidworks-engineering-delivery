import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch9.py")
t = P.read_text(encoding="utf-8")
old = 'doc="Detect mold undercuts along a direction."'
new = (
    'doc="Detect mold undercuts along a direction. '
    '\u26a0 The underlying IFeatureManager.MoldUndercutDetect is marked Obsolete by '
    'SOLIDWORKS (successor: MoldUndercutDetect2); kept deliberately until the successor '
    'shape is verified. See docs/obsolete-member-candidates.md."'
)
if "is marked Obsolete" in t:
    print("  已有警示")
else:
    assert old in t, "锚点不符"
    t = t.replace(old, new, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok batch9 的 mold_undercut_detect 已加废弃警示")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
print("  出现次数: %d" % P.read_text(encoding="utf-8").count("is marked Obsolete"))

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_loads.py")
src = p.read_text(encoding="utf-8")

NAMES = [
    "AddBearingConnector", "AddBearingLoad", "AddBoltConnector", "AddCable",
    "AddCentrifugalForce", "AddConvection", "AddCyclicSymmetryRestraint", "AddDistributedMass",
    "AddEdgeWeldConnector", "AddElasticConnector", "AddForce", "AddForce2", "AddForce3",
    "AddGeneralSpringConnector", "AddGravity", "AddHeatFlux", "AddHeatPower",
    "AddInitialConditionForDynamicStudy", "AddInitialConditionForDynamicStudy2", "AddLinkageRod",
    "AddLinkConnector", "AddPinConnector", "AddPrescribedDisplacement", "AddPressure",
    "AddRadiation", "AddRemoteLoad", "AddRestraint", "AddRigidConnector",
    "AddSelectedBaseExcitation", "AddSelectedBaseExcitation2", "AddSpotWeldConnector",
    "AddSpringConnector", "AddTemperature", "AddUniformBaseExcitation",
    "AddUniformBaseExcitation2",
]

#: \u2605 \u628a\u540d\u5355\u6574\u4f53\u6362\u6210\u51fa\u5382\u7c7b\u578b\u5e93\u7ed9\u7684\u90a3 35 \u4e2a\uff08\u2605 \u6bcf\u884c 3 \u4e2a\uff0c\u4fbf\u4e8e\u5bf9\u8bfb\uff09
lines = []
for i in range(0, len(NAMES), 3):
    lines.append("        " + ", ".join('"%s"' % n for n in NAMES[i:i + 3]) + ",")
BODY = "_ERRORCODE_MEMBERS = frozenset({\n" + "\n".join(lines) + "\n    })"

#: \u2605 \u628a\u65e7\u7684\u5757\uff08\u4ece `_ERRORCODE_MEMBERS = frozenset({` \u5230\u5339\u914d\u7684 `})`\uff09\u6574\u4f53\u6362\u6389
i = src.find("    _ERRORCODE_MEMBERS = frozenset({")
if i < 0:
    print("  **\u672a\u627e\u5230\u65e7\u5757**")
else:
    j = src.find("})", i) + 2
    src = src[:i] + "    " + BODY + src[j:]
    #: \u2605 \u8bf4\u660e\u4f9d\u636e\uff08\u2605 \u5199\u5728\u540d\u5355\u4e0a\u65b9\u7684\u6ce8\u91ca\u91cc\uff09
    pat = "#: \u2605\u2605 \u9700\u8981\u672b\u5c3e `ByRef ErrorCode` \u7684\u6210\u5458"
    k = src.find(pat)
    if k >= 0:
        ins = ("    #: \u2605\u2605\u2605\u2605\u2605 2026-10-03\uff08\u8f6e 415\uff09**\u672c\u540d\u5355\u5df2\u6539\u4e3a\u4ee5\u300c\u51fa\u5382\u7c7b\u578b\u5e93\u300d\u4e3a\u51c6\uff08\u94c1\u5f8b 4\uff09**\uff1a\n"
               "    #:   \u2605 \u771f\u673a\u4e0a `AddTemperature` \u4e0e `AddRemoteLoad` \u62a5\n"
               "    #:     `com_error(-2147352561, '\u975e\u9009\u62e9\u6027\u7684\u53c2\u6570')`\uff08= **\u7f3a `ByRef ErrorCode`**\uff09\uff0c\n"
               "    #:     \u2605 \u800c**\u65e7\u540d\u5355\u91cc\u6070\u597d\u6ca1\u6709\u8fd9\u4e24\u4e2a\u540d\u5b57** \u21d2 \u4e8e\u662f\u4e0d\u8865 `out_i4()` \u21d2 \u62a5\u9519\u3002\n"
               "    #:   \u2605 \u800c\u51fa\u5382\u7c7b\u578b\u5e93\uff08`SolidWorks.Interop.cosworks.dll` **34.4.1.1011**\uff0c\n"
               "    #:     \u7eaf\u5143\u6570\u636e\u53cd\u5c04\uff09\u7ed9\u51fa\uff1a\u2605\u2605 **\u5168\u90e8 35 \u4e2a `Add*` \u90fd\u5e26 `ErrorCode:Int32&`**\uff08\u4e0d\u5e26\u7684 **0** \u4e2a\uff09\u3002\n"
               "    #:   \u21d2 \u2605 \u672c\u540d\u5355\u73b0\u4e3a\u90a3 35 \u4e2a\u3002\u2605 \u800c\u8fd9\u4e5f\u662f\u672c\u4ed3\u300c\u5b81\u53ef\u62a5\u9519\u4e5f\u4e0d\u4e71\u8865\u53c2\u6570\u300d\u7eaa\u5f8b\u7684**\u6b63\u5f53\u5347\u7ea7**\uff1a\n"
               "    #:     \u2605 \u4e4b\u524d\u662f\u300c\u624b\u6284 CHM\u300d\uff08**2021 \u7248**\uff09\uff0c\u2605 \u73b0\u5728\u662f**\u672c\u673a\u51fa\u5382\u7c7b\u578b\u5e93**\u3002\n")
        src = src[:k] + ins + src[k:]
    p.write_text(src, encoding="utf-8")
    print("  \u5df2\u628a _ERRORCODE_MEMBERS \u6362\u6210\u51fa\u5382\u7c7b\u578b\u5e93\u7684 %d \u4e2a" % len(NAMES))
try:
    compile(src, str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:74]))

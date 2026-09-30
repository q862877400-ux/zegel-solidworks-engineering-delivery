import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_registry.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
fams = [k for k in reg if k in reg]
ST = ["ICWStudyManager", "ICWStudy", "ICWLoadsAndRestraintsManager"]
ML = ["ICWMesh", "ICWResults", "ICWMaterial"]
SO = [k for k in fams if k.endswith("StudyOptions")]
L = ["# ── 来源 ─────────────────────────────────────────────────────────────",
     "# 仓库:   本项目自身（本任务新增的能力层）",
     "# 文件:   scripts/sw_simulation_registry.py —— 本文件自身",
     "# 定位:   cosworks 19 族的成员登记表 {族: {能力名: 实参个数}}。",
     "#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，",
     "#         对 iface_cosworks.txt 的逐行解析，机械生成不手抄。",
     "# ⚑ 编号成员**未折叠**。",
     "# ⚠ cosworks 的 CHM 册**只覆盖 ICWLoadsAndRestraintsManager 一族** ⇒",
     "#   只有该族有官方参数语义说明；其余 18 族本模块**只登记名字与参数个数**，",
     "#   **不解释任何一项的语义**。",
     "# 取值:   能力数 —— 逐族："]
for k in fams: L.append("#     %-34s %4d" % (k, reg[k]["distinct_capabilities"]))
L += ["# 覆盖:   后续同级定义",
      "# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）",
      "# ────────────────────────────────────────────────────────────────────",
      "SIM_FAMILIES: tuple[str, ...] = ("]
for k in fams: L.append("    %r," % k)
L += [")", "", "STUDY_AND_LOADS_FAMILIES: tuple[str, ...] = ("]
for k in ST: L.append("    %r," % k)
L += [")", "", "MESH_AND_RESULTS_FAMILIES: tuple[str, ...] = ("]
for k in ML: L.append("    %r," % k)
L += [")", "", "SOLVER_OPTION_FAMILIES: tuple[str, ...] = ("]
for k in SO: L.append("    %r," % k)
L += [")", "", "SIM_ARITY: dict[str, dict[str, int]] = {"]
n = 0
for k in fams:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]: L.append("        %r: %d," % (it["name"], it["arity"])); n += 1
    L.append("    },")
L += ["}", "", "SIM_PROPERTIES: dict[str, tuple[str, ...]] = {"]
p = 0
for k in fams:
    L.append("    %r: (" % k)
    for x in reg[k]["properties"]: L.append("        %r," % x); p += 1
    L.append("    ),")
L += ["}", ""]
anchor = "\n\ndef _require(obj"
assert anchor in src
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("注入：%d 族 / 能力 %d / 属性 %d（求解器设置族 %d）" % (len(fams), n, p, len(SO)))

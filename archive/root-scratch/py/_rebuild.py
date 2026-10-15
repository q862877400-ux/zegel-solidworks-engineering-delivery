import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
tpl = Path(r"D:\AI\SW\_sim_module.md").read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
fams = [k for k in reg if k in reg]
ST = ["ICWStudyManager", "ICWStudy", "ICWLoadsAndRestraintsManager",
      "ICWForce", "ICWPressure", "ICWHeatFlux", "ICWContactSet"]
ML = ["ICWMesh", "ICWResults", "ICWMaterial"]
SO = [k for k in fams if k.endswith("StudyOptions")]
L = []
L.append("# ── 来源 ─────────────────────────────────────────────────────────────")
L.append("# 仓库:   本项目自身（本任务新增的能力层）")
L.append("# 文件:   scripts/sw_simulation_registry.py —— 本文件自身")
L.append("# 定位:   本轮登记的 19 个 cosworks 族的成员登记表 {族: {能力名: 实参个数}}。")
L.append("#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。")
L.append("# ⚑ 这 19 族**不是 cosworks 全库** —— 反射里有成员的接口段实测 84 个，")
L.append("#   本轮取的是 family-coverage.md 里已列出的那 19 个。")
L.append("# ⚑ 编号成员**未折叠**。")
L.append("# ⚠ cosworks 的 CHM 册只覆盖 ICWLoadsAndRestraintsManager 一族 ⇒")
L.append("#   只有该族有官方参数语义说明；其余 18 族本模块**只登记名字与参数个数**，")
L.append("#   **不解释任何一项的语义**。")
L.append("# 取值:   能力数 —— 逐族：")
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
assert anchor in tpl
out = tpl.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
Path(r"C:\swprojects\sw-skill-fork\scripts\sw_simulation_registry.py").write_text(out, encoding="utf-8")
print("重建：%d 族 / 能力 %d / 属性 %d" % (len(fams), n, p))

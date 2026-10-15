import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
tpl = Path(r"D:\AI\SW\_sim_module.md").read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
fams = list(reg.keys())
ST = ["ICWStudyManager", "ICWStudy", "ICWLoadsAndRestraintsManager",
      "ICWForce", "ICWPressure", "ICWHeatFlux", "ICWContactSet"]
ML = ["ICWMesh", "ICWResults", "ICWMaterial"]
SO = ["ICWStaticStudyOptions", "ICWFrequencyStudyOptions", "ICWBucklingStudyOptions",
      "ICWNonLinearStudyOptions", "ICWThermalStudyOptions", "ICWDynamicStudyOptions",
      "ICWFatigueStudyOptions", "ICWDropTestStudyOptions", "ICWCompositeShellOptions"]
# 完整性自检：三个组必须恰好划分 19 族
covered = ST + ML + SO
assert sorted(covered) == sorted(fams), (
    "分组未恰好划分全部族，多: %s 少: %s" % (
        sorted(set(covered) - set(fams)), sorted(set(fams) - set(covered))))
L = ["# ── 来源 ─────────────────────────────────────────────────────────────",
     "# 仓库:   本项目自身（本任务新增的能力层）",
     "# 文件:   scripts/sw_simulation_registry.py —— 本文件自身",
     "# 定位:   本轮登记的 19 个 cosworks 族的成员登记表 {族: {能力名: 实参个数}}。",
     "#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。",
     "# ⚑ 这 19 族**不是 cosworks 全库** —— 反射里有成员的接口段实测 84 个，",
     "#   本轮取的是 family-coverage.md 里已列出的那 19 个。",
     "# ⚑ 编号成员**未折叠**。",
     "# ⚠ cosworks 的 CHM 册只覆盖 ICWLoadsAndRestraintsManager 一族 ⇒",
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
L += [")", "", "SOLVER_OPTION_FAMILIES: tuple[str, ...] = (",
      "    # ⚑ ICWCompositeShellOptions 名字**不以** StudyOptions 结尾，",
      "    #   但它同样是求解器设置族 —— 早先按后缀筛把它漏掉了。"]
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
print("重建 OK：%d 族 / 能力 %d / 属性 %d / 三组自检通过" % (len(fams), n, p))

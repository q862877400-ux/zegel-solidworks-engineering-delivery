import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_part_features.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
FD = ["ISweepFeatureData","ILoftFeatureData","IBoundaryBossFeatureData",
      "IMidSurface3","IRevolveFeatureData2","IChainPatternFeatureData"]
GE = ["IFace2","IBody2"]
SEL = ["ISweepFeatureData","ILoftFeatureData","IBoundaryBossFeatureData",
       "IRevolveFeatureData2","IChainPatternFeatureData"]
L = []
L.append("# ── 来源 ─────────────────────────────────────────────────────────────")
L.append("# 仓库:   本项目自身（本任务新增的能力层）")
L.append("# 文件:   scripts/sw_part_features.py —— 本文件自身")
L.append("# 定位:   八族能力登记表（**特征参数族**与**几何遍历族**分两张表）。")
L.append("#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。")
L.append("# ⚑ 编号成员**未折叠**（SolidWorks 的编号不是重载，是不同版本的不同操作）。")
L.append("# 取值:   原始 / I前缀 / 属性 / 方法 —— 逐族：")
for k in FD + GE:
    i = reg[k]
    L.append("#     %-30s %4d / %3d / %3d / %4d" % (
        k, i["raw_members"], i["internal_dispatch"], i["property_count"],
        i["method_count"]))
L.append("# 覆盖:   后续同级定义")
L.append("# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）")
L.append("# ────────────────────────────────────────────────────────────────────")
L.append("FEATURE_DATA_FAMILIES: tuple[str, ...] = (")
for k in FD: L.append("    %r," % k)
L.append(")")
L.append("")
L.append("GEOMETRY_ENTITY_FAMILIES: tuple[str, ...] = (")
for k in GE: L.append("    %r," % k)
L.append(")")
L.append("")
L.append("#: 特征参数族的能力登记表 {族: {能力名: 实参个数}}")
L.append("FEATURE_DATA_ARITY: dict[str, dict[str, int]] = {")
n1 = 0
for k in FD:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]:
        L.append("        %r: %d," % (it["name"], it["arity"])); n1 += 1
    L.append("    },")
L.append("}")
L.append("")
L.append("#: 几何遍历族的能力登记表（与上表**刻意分开**，避免「用错族」静默通过）")
L.append("GEOMETRY_ENTITY_ARITY: dict[str, dict[str, int]] = {")
n2 = 0
for k in GE:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]:
        L.append("        %r: %d," % (it["name"], it["arity"])); n2 += 1
    L.append("    },")
L.append("}")
L.append("")
L.append("#: 特征参数族的属性名（反射里是 get_/set_，**不是方法**）")
L.append("FEATURE_DATA_PROPERTIES: dict[str, tuple[str, ...]] = {")
n3 = 0
for k in FD:
    L.append("    %r: (" % k)
    for p in reg[k]["properties"]: L.append("        %r," % p); n3 += 1
    L.append("    ),")
L.append("}")
L.append("")
L.append("#: **有**选区事务（AccessSelections 2 参 + ReleaseSelectionAccess 零参）的族。")
L.append("# ⚑ 这 6 族同形可共用；IFace2 / IBody2 / IMidSurface3 **没有**，")
L.append("#   对它们调 edit_feature_selection 会得到 KeyError —— 那是正确行为。")
L.append("SELECTION_FAMILIES: tuple[str, ...] = (")
for k in SEL: L.append("    %r," % k)
L.append(")")
L.append("")
anchor = "\n\ndef _require(obj"
assert anchor in src
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("已注入：特征参数 %d + 几何遍历 %d 能力 / %d 属性 / 事务族 %d" % (n1, n2, n3, len(SEL)))

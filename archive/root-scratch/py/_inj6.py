import json, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
f = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch_sheetmetal.py")
src = f.read_text(encoding="utf-8")
reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
SK = ["ISketchManager","ISketch","ISketchSegment","ISketchSpline","ISketchPoint",
      "ISketchArc","ISketchHatch","ISketchText","ISketchRelation","ISketchContour",
      "ISketchPatternFeatureData","ISketchedBendFeatureData","ISketchLine",
      "ISketchRelationManager","ISketchSlot"]
SM = ["IBaseFlangeFeatureData","ISheetMetalFeatureData","IEdgeFlangeFeatureData",
      "ISweptFlangeFeatureData","IDraftFeatureData2","IOneBendFeatureData",
      "IHemFeatureData","IMiterFlangeFeatureData","IGussetFeatureData",
      "ILoftedBendsFeatureData","ISMGussetFeatureData","ISheetMetalFolder"]
SK = [k for k in SK if k in reg]
SM = [k for k in SM if k in reg]
L = ["# ── 来源 ─────────────────────────────────────────────────────────────",
     "# 仓库:   本项目自身（本任务新增的能力层）",
     "# 文件:   scripts/sw_sketch_sheetmetal.py —— 本文件自身",
     "# 定位:   草图 14 族 + 钣金 13 族的登记表（**分两张表**）。",
     "#         生成器 D:\\AI\\SW\\tools\\gen_member_registry.py，机械生成不手抄。",
     "# ⚑ 编号成员**未折叠**（SolidWorks 的编号不是重载，是不同版本的不同操作）。",
     "# ⚑ 两域成员名会重名（GetSketchSegments 在 ISketch 上、AccessSelections",
     "#   在几乎所有钣金 FeatureData 上）⇒ 合成一张表会让「用错域」静默通过。",
     "# 取值:   能力数 —— 草图域：",
     ]
for k in SK: L.append("#     %-30s %4d" % (k, reg[k]["distinct_capabilities"]))
L.append("#         能力数 —— 钣金域：")
for k in SM: L.append("#     %-30s %4d" % (k, reg[k]["distinct_capabilities"]))
L += ["# 覆盖:   后续同级定义",
      "# ⚠ 本组为静态照录，未在本机实测（见 AGENTS.md 铁律 2）",
      "# ────────────────────────────────────────────────────────────────────",
      "SKETCH_FAMILIES: tuple[str, ...] = ("]
for k in SK: L.append("    %r," % k)
L += [")", "", "SHEET_METAL_FAMILIES: tuple[str, ...] = ("]
for k in SM: L.append("    %r," % k)
L += [")", "", "SKETCH_ARITY: dict[str, dict[str, int]] = {"]
n = 0
for k in SK:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]: L.append("        %r: %d," % (it["name"], it["arity"])); n += 1
    L.append("    },")
L += ["}", "", "#: 钣金族的能力登记表（与草图**刻意分开**）", "SHEET_METAL_ARITY: dict[str, dict[str, int]] = {"]
for k in SM:
    L.append("    %r: {" % k)
    for it in reg[k]["members"]: L.append("        %r: %d," % (it["name"], it["arity"])); n += 1
    L.append("    },")
L += ["}", "", "SKETCH_PROPERTIES: dict[str, tuple[str, ...]] = {"]
p = 0
for k in SK:
    L.append("    %r: (" % k)
    for x in reg[k]["properties"]: L.append("        %r," % x); p += 1
    L.append("    ),")
L += ["}", "", "SHEET_METAL_PROPERTIES: dict[str, tuple[str, ...]] = {"]
for k in SM:
    L.append("    %r: (" % k)
    for x in reg[k]["properties"]: L.append("        %r," % x); p += 1
    L.append("    ),")
L += ["}", ""]
# 有选区事务的钣金族
sel = [k for k in SM if reg[k]["members"] and
       any(x["name"] == "AccessSelections" for x in reg[k]["members"]) and
       any(x["name"] == "ReleaseSelectionAccess" for x in reg[k]["members"])]
L.append("#: **有**选区事务的钣金族（两成员同形：2 参 + 0 参）")
L.append("SHEET_METAL_SELECTION_FAMILIES: tuple[str, ...] = (")
for k in sel: L.append("    %r," % k)
L += [")", ""]
anchor = "\n\ndef _require(obj"
assert anchor in src
src = src.replace(anchor, "\n\n" + "\n".join(L) + anchor, 1)
f.write_text(src, encoding="utf-8")
print("注入：草图 %d 族 / 钣金 %d 族 / 能力 %d / 属性 %d / 事务族 %d" % (len(SK), len(SM), n, p, len(sel)))

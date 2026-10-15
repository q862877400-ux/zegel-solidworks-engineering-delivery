import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
REGISTRY = {"sw_api_sldworks.py", "sw_api_cosworks.py", "sw_api_swconst.py"}
src = {p.name: p.read_text(encoding="utf-8", errors="ignore")
       for p in (R / "scripts").glob("sw_*.py") if p.name not in REGISTRY}
alltext = "\n".join(src.values())
print("参与比对的实现文件: %d 个（⚠ 已排除 API 名登记表 %s）\n" % (len(src), sorted(REGISTRY)))

CHECKS = [
    ("save_as", ["SaveAs3", "SaveAs2", "SaveAs("]),
    ("sheets", ["GetSheetNames", "ActivateSheet", "sheet_names"]),
    ("sketch_chamfer", ["SketchChamfer", "sketch_chamfer"]),
    ("sketch_mirror", ["SketchMirror", "sketch_mirror", "mirror_sketch"]),
    ("measure", ["collect_geometry_measurements"]),
    ("recording", ["RecordMacro", "StopRecordingMacro", "start_recording"]),
    ("stop_native_macro_recording", ["StopRecordingMacro", "stop_recording"]),
    ("tooling_split", ["insert_core_cavity_solids"]),
    ("gdt", ["Gtol", "IGtol", "AddGtol"]),
    ("helix", ["InsertHelix", "create_helix"]),
    ("jog", ["InsertJog", "create_jog", "jog_bend"]),
    ("equation", ["EquationMgr", "AddEquation"]),
    ("convert_entities", ["SketchUseEdge", "convert_entities"]),
    ("activate_sheet", ["ActivateSheet", "activate_sheet"]),
    ("pattern_component_circular", ["CircularPattern", "circular_pattern"]),
]
real, fake = [], []
for op, pats in CHECKS:
    hits = []
    for pat in pats:
        for m, t in src.items():
            if pat in t:
                hits.append("%s@%s" % (pat, m[:-3]))
    (real if hits else fake).append(op)
    print("  %-30s %s" % (op, ("命中: " + ", ".join(hits[:2])) if hits else "**没有实现**"))
print()
print("  ⇒ 我们**确实有**的: %s" % real)
print("  ⇒ 确实没有的: %s" % fake)
print("  命中率 = %d/%d = %.0f%%" % (len(real), len(CHECKS), 100.0 * len(real) / len(CHECKS)))

import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
src = {p.name: p.read_text(encoding="utf-8", errors="ignore") for p in (R / "scripts").glob("sw_*.py")}
alltext = "\n".join(src.values())

CHECKS = [
    ("save_as", ["SaveAs", "SaveAs3", "save_as", "SaveAs2"]),
    ("sheets", ["GetSheetNames", "SheetName", "sheet_names", "ISheet", "ActivateSheet"]),
    ("sketch_chamfer", ["sketch_chamfer", "SketchChamfer", "create_sketch_chamfer"]),
    ("sketch_mirror", ["sketch_mirror", "SketchMirror", "mirror_sketch"]),
    ("measure", ["collect_geometry_measurements", "GetMassProperties", "measure"]),
    ("recording", ["RecordMacro", "recording", "start_recording"]),
    ("stop_native_macro_recording", ["StopRecordingMacro", "stop_recording"]),
    ("tooling_split", ["insert_core_cavity_solids", "CoreCavitySplit", "ToolingSplit"]),
    ("gdt", ["Gtol", "IGtol", "gdt", "datum"]),
    ("helix", ["helix", "Helix", "InsertHelix"]),
    ("jog", ["jog", "Jog", "insert_jog"]),
    ("equation", ["EquationMgr", "equation", "Equation"]),
    ("convert_entities", ["SketchUseEdge", "convert_entit", "use_edge"]),
    ("activate_sheet", ["ActivateSheet", "activate_sheet"]),
    ("pattern_component_circular", ["circular_pattern", "CircularPattern", "pattern_component"]),
]
for op, pats in CHECKS:
    hits = []
    for pat in pats:
        if re.search(re.escape(pat), alltext):
            mods = [m for m, t in src.items() if pat in t]
            hits.append("%s@%s" % (pat, mods[0][:-3] if mods else "?"))
    print("  %-30s %s" % (op, ("**命中**: " + ", ".join(hits[:3])) if hits else "**全都找不到**"))

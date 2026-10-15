import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
EXCLUDE = re.compile(r"sw_api_|sw_com_traps")
impl = {p.name: p.read_text(encoding="utf-8", errors="ignore")
        for p in (R / "scripts").glob("sw_*.py") if not EXCLUDE.search(p.name)}
print("实现文件 %d 个（已排除 API 登记表与 COM 陷阱表）\n" % len(impl))

# ★ 无偏样本：真缺 132 条的**每 6 取 1**（与轮 101 的抽样规则一致）
SAMPLE = [
    ("activate_sheet", ["ActivateSheet"]),
    ("assembly_mates", ["mate_feature", "collect_mate", "list_mates", "GetMates"]),
    ("batch_operations", ["batch_export", "batch_"]),
    ("check_drawing_compliance", ["compliance", "check_drawing"]),
    ("convert_entities", ["SketchUseEdge", "convert_entit"]),
    ("drawing_dimensions", ["drawing_dimension", "Dimension("]),
    ("equation", ["EquationMgr", "AddEquation", "equation"]),
    ("export_vba", ["export_vba", "SaveAs.*vba", "vba"]),
    ("gdt", ["Gtol", "AddGtol", "datum"]),
    ("generate_vba_file_operations", ["generate_vba", "file_operations"]),
    ("helix", ["Helix", "helix"]),
    ("jog", ["Jog", "jog"]),
    ("measure", ["collect_geometry_measurements"]),
    ("pattern_component_circular", ["circular_pattern", "CircularPattern"]),
    ("recording", ["RecordMacro", "recording"]),
    ("save_as", ["SaveAs"]),
    ("sheets", ["GetSheetNames", "ActivateSheet", "sheet_names"]),
    ("sketch_chamfer", ["SketchChamfer", "sketch_chamfer"]),
    ("sketch_mirror", ["SketchMirror", "sketch_mirror", "mirror_sketch"]),
    ("stop_native_macro_recording", ["StopRecordingMacro", "stop_recording"]),
    ("tooling_split", ["insert_core_cavity_solids"]),
    ("validate_drawing_completeness", ["drawing_completeness", "validate_drawing"]),
]
real, fake = [], []
for op, pats in SAMPLE:
    hits = []
    for pat in pats:
        for m, t in impl.items():
            if re.search(r"(def\s+%s\b|\b%s\s*\(|\.%s\b|\b%s\b)" % ((re.escape(pat),) * 4), t):
                hits.append("%s@%s" % (pat, m[:-3]))
    (real if hits else fake).append(op)
    print("  %-32s %s" % (op, ("命中: " + ", ".join(sorted(set(hits))[:2])) if hits else "没有实现"))
print()
print("  ⇒ 确实有 %d 条: %s" % (len(real), real))
print("  ⇒ 确实没有 %d 条" % len(fake))
print("  ⇒ **反向错误率 = %d/%d ≈ %.0f%%**" % (len(real), len(SAMPLE), 100.0 * len(real) / len(SAMPLE)))

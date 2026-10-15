import ast, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

# ⚠ 严格口径：只比对「**函数定义**」与「**函数体内的真实调用/属性访问**」，
#   还要排除 API 名登记表与 COM 陷阱表 —— 它们只是**字符串表**，不是实现。
EXCLUDE = re.compile(r"sw_api_|sw_com_traps|sw_api_swconst")
impl = {}
for p in (R / "scripts").glob("sw_*.py"):
    if EXCLUDE.search(p.name):
        continue
    impl[p.name] = p.read_text(encoding="utf-8", errors="ignore")
print("参与比对的**实现**文件: %d 个（排除 API 登记表与 COM 陷阱表）\n" % len(impl))

CHECKS = [
    ("save_as", ["SaveAs", "save_document"]),
    ("sheets", ["GetSheetNames", "ActivateSheet", "sheet_names"]),
    ("sketch_chamfer", ["SketchChamfer"]),
    ("sketch_mirror", ["SketchMirror"]),
    ("measure", ["collect_geometry_measurements", "GetMassProperties"]),
    ("recording", ["RecordMacro", "StopRecordingMacro"]),
    ("stop_native_macro_recording", ["StopRecordingMacro"]),
    ("tooling_split", ["insert_core_cavity_solids", "InsertMoldCoreCavitySolids"]),
    ("gdt", ["Gtol", "IGtol", "AddGtol"]),
    ("helix", ["InsertHelix", "Helix"]),
    ("jog", ["Jog"]),
    ("equation", ["EquationMgr", "AddEquation"]),
    ("convert_entities", ["SketchUseEdge"]),
    ("activate_sheet", ["ActivateSheet"]),
    ("pattern_component_circular", ["CircularPattern", "circular_pattern"]),
]
real, fake = [], []
for op, pats in CHECKS:
    hits = []
    for pat in pats:
        for m, t in impl.items():
            # ⚠ 必须是**定义**或**调用形态**（`X(` 或 `.X`），不是随便出现的字符串
            if re.search(r"(def\s+%s\b|\b%s\s*\(|\.%s\b)" % (re.escape(pat), re.escape(pat), re.escape(pat)), t):
                hits.append("%s@%s" % (pat, m[:-3]))
    (real if hits else fake).append(op)
    print("  %-30s %s" % (op, ("命中: " + ", ".join(sorted(set(hits))[:2])) if hits else "**没有实现**"))
print()
print("  ⇒ 确实有: %s  （%d 条）" % (real, len(real)))
print("  ⇒ 确实没有: %s  （%d 条）" % (fake, len(fake)))
print("  ⇒ **反向错误率 = %d/%d = %.0f%%**（「真缺」里其实我们有的比例）"
      % (len(real), len(CHECKS), 100.0 * len(real) / len(CHECKS)))

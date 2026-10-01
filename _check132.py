import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
funcs = {}
for p in (R / "scripts").glob("sw_*.py"):
    for n in re.findall(r"^def (\w+)\(", p.read_text(encoding="utf-8", errors="ignore"), re.M):
        funcs.setdefault(n, p.name)

SAMPLE = [
    "activate_sheet", "assembly_mates", "batch_operations", "check_drawing_compliance",
    "convert_entities", "drawing_dimensions", "equation", "export_vba", "gdt",
    "generate_vba_file_operations", "helix", "jog", "measure",
    "pattern_component_circular", "recording", "save_as", "sheets", "sketch_chamfer",
    "sketch_mirror", "stop_native_macro_recording", "tooling_split",
    "validate_drawing_completeness",
]
print("对每条缺口操作，按**关键词**在 %d 个函数名里找（不是精确名）：\n" % len(funcs))
for op in SAMPLE:
    toks = [t for t in op.split("_") if len(t) > 2]
    hits = []
    for n, mod in funcs.items():
        nl = n.lower()
        # 至少命中一个关键词
        if any(t in nl for t in toks):
            hits.append("%s(%s)" % (n, mod[:-3]))
    tag = "找不到" if not hits else "%d 个候选" % len(hits)
    print("  %-32s %s" % (op, tag))
    for h in hits[:4]:
        print("        %s" % h)

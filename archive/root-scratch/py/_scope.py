import re, io, sys
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
KEEP = {
 "call_hub","call_annotation","call_feature_data","call_entity","call_member",
 "call_sim","call_sheet_metal","call_sketch","call_geometry",
 "edit_feature_selection","edit_sheet_metal_selection",
 "select_by_id",  # 转发上游 _select_by_id，带「面名随语言变」候选机制
}
funcs = set()
for p in sorted((REPO/"scripts").glob("sw_*.py")):
    src = p.read_text(encoding="utf-8")
    for m in re.finditer(r"^def (\w+)\s*\(", src, re.M):
        if m.group(1) not in KEEP and not m.group(1).startswith("_"):
            funcs.add(m.group(1))
tests = sorted((REPO/"tests").glob("test_*.py"))
hit = {}
for t in tests:
    s = t.read_text(encoding="utf-8")
    used = sorted(f for f in funcs if re.search(rf"\b{f}\b", s))
    if used: hit[t.name] = used
print("将被删的公开函数：%d 个" % len(funcs))
print("受影响的测试文件：%d 个" % len(hit))
for k, v in sorted(hit.items(), key=lambda x: -len(x[1])):
    print("  %-44s %d" % (k, len(v)))

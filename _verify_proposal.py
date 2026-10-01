import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
#: ⚠ 排除**名字登记表** —— 那是「任何官方成员名都命中」的地方，会把判据全污染
SKIP = {"sw_api_sldworks.py"}
NAMES = ["EditPart2", "InsertNewPart2", "InsertNewVirtualPart", "EditAssembly",
         "AddRelation", "GetRelationsCount", "GetRelations",
         "ListExternalFileReferences", "ListExternalFileReferencesCount",
         "GetDefinitionEntities2", "GetRelationType", "RelationManager",
         "convert_entities", "SketchUseEdge3", "sw_toolbox_index"]
print("  文件存在性:")
for f in ("sw_sketch_edit.py", "sw_sketch.py", "sw_toolbox_index.py", "sw_in_context.py"):
    print("    %-24s %s" % (f, "**有**" if (R / "scripts" / f).is_file() else "**没有**"))
print()
print("  成员名在 scripts/ 的命中（**排除 %s**）:" % "、".join(SKIP))
for n in NAMES:
    hits = []
    for p in sorted((R / "scripts").glob("*.py")):
        if p.name in SKIP:
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if n in line:
                hits.append("%s:%d" % (p.name, i))
    print("    %-32s %2d 处  %s" % (n, len(hits), " · ".join(hits[:3])))

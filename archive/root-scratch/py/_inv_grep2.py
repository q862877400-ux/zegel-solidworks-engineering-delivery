import re, io
from pathlib import Path
ROOT = Path(r"D:\AI\SW")
Q = {
 "LIST_SOLID_BODIES": r"GetBodies2|list_solid_bodies|solid_body",
 "FEATURE_TREE_CLASSIFY": r"feature_tree|classify|feature_type_name|type_name",
 "PLANE_VISIBILITY": r"HideFeature|ShowFeature|plane.*show|show.*plane|blank",
 "PROJECTED_CURVE": r"InsertProjected|projected|ProjectCurve",
 "MACRO_TEMPLATES": r"macro_select_template|FALLBACK_TEMPLATE|TEMPLATES\s*=|template_key",
 "MACRO_SECURITY": r"MacroSecurity|SecurityLevel|swMacroSecurity|macro_security",
 "TITLE_BLOCK_WRITE": r"title_block|TitleBlock|SetProperties.*sheet|sheet.*properties",
 "PDM_MODULE": r"sw_pdm|PDM_EXPORT|IEdm",
 "GRAYSCALE": r"gray|grey",
 "RENAME_FEATURE": r"rename_feature|SetFeatureName|feature_name\s*=",
 "DOC_UNITS_SET": r"SetUnits|set_units",
 "WORKFLOW_EXEC": r"execute_workflow|run_workflow|step_runner",
 "PERF_OPTS": r"optimize_performance|performance_options|swPerformance",
}
targets = list(sorted((ROOT/"mcp-server").glob("tool_specs_*.py"))) + [ROOT/"mcp-server"/"server.py"] + sorted((ROOT/"scripts").glob("sw_*.py")) + [ROOT/"capabilities.yaml", ROOT/"docs"/"dead-ends.md"]
o = io.StringIO()
for k, pat in Q.items():
    rx = re.compile(pat)
    hits = []
    for p in targets:
        if not p.is_file(): continue
        for i, ln in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if rx.search(ln):
                hits.append("%s:%d: %s" % (p.name, i, ln.strip()[:160]))
    o.write("\n"+"="*90+"\n### %s  hits=%d\n" % (k, len(hits)))
    for h in hits[:16]: o.write("  "+h+"\n")
    if len(hits)>16: o.write("  ... (+%d)\n" % (len(hits)-16))
open(r"D:\AI\SW\_inv_grep2.txt","w",encoding="utf-8").write(o.getvalue())
print("ok")

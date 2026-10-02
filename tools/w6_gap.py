import inspect
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"" + _ROOT_S + r"")
sys.path[:0] = [str(REPO / "mcp-server"), str(REPO), str(REPO / "scripts")]
import register_capabilities as rc

GAP = ["assembly", "assembly_analysis", "assembly_components", "assembly_mates", "assembly_tree",
       "component", "component_fixed", "components", "explode_assembly", "fix_component",
       "hide_component", "interference", "load_assembly", "mirror_component", "move_component",
       "pack_and_go_assembly", "pattern_component_circular", "pattern_component_linear",
       "replace_component", "save_assembly", "suppress_component"]

#: ① MCP 已有（我们的 + 上游的）
srv = (REPO / "mcp-server" / "server.py").read_text(encoding="utf-8")
tool_names = [x.name for x in rc.all_specs()] + re.findall(
    r'name="((?:solidworks|cadstudio)_[a-z0-9_]+)"', srv)
print("  ══ ① MCP 里跟装配有关的工具 ══")
for n in sorted(set(tool_names)):
    if re.search(r"assembl|component|mate|bom|pack_and_go", n, re.I):
        print("    %s" % n)

#: ② 能力层里的装配函数（首参可注入的）
print()
print("  ══ ② 能力层里跟装配/干涉有关的函数 ══")
for p in sorted((REPO / "scripts").glob("sw_*.py")):
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"(?m)^def ([a-z]\w*)\s*\(", t):
        n = m.group(1)
        if re.search(r"assembl|component|mate|interfer|collision|clash|explode|pattern_comp", n, re.I):
            print("    %-18s %s" % (p.stem, n))

#: ③ 逐个缺口名核"我们有没有"
print()
print("  ══ ③ 21 个缺口名逐个核 ══")
allfn = {}
for p in sorted((REPO / "scripts").glob("sw_*.py")):
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"(?m)^def ([a-z]\w*)\s*\(", t):
        allfn.setdefault(m.group(1), p.stem)
for g in GAP:
    words = [w for w in g.split("_") if len(w) > 2]
    hit_tool = [n for n in tool_names if all(w in n for w in words)]
    hit_fn = [n for n in allfn if all(w in n for w in words)]
    if hit_tool:
        print("    %-26s ⇒ ★ **已有工具**: %s" % (g, sorted(hit_tool)[:2]))
    elif hit_fn:
        print("    %-26s ⇒ 能力层有: %s（**没挂**）" % (g, sorted(hit_fn)[:3]))
    else:
        print("    %-26s ⇒ ⚠ **都没有**" % g)

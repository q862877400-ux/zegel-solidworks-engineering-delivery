import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
proj = {
 "Slacker-LLC": r"C:\swprojects",   # 不在本地，用 README 已抄
 "vespo92 TS": r"C:\swprojects\SolidworksMCP-TS",
 "SolidPilot": r"C:\swprojects\mcp-server-solidworks",
 "alisamsam": r"C:\swprojects\Solidworks-MCP",
 "q3ds": r"C:\swprojects\q3ds-solidworks-mcp",
}
keys = {
 "仿真 Simulation": r"simulation|cosworks|study|CWModel|Simulation",
 "动画/运动 Motion": r"motion|animation|animate|MotionStudy",
 "拓扑优化": r"topolog|topology optim",
 "钣金 SheetMetal": r"sheet.?metal|SheetMetal|flange|bend",
 "焊件 Weldment": r"weldment|weld|gusset|structural member",
 "曲面 Surface": r"surface|loft|sweep",
 "方程/设计表": r"equation|design.?table|DesignTable",
 "成本 Costing": r"costing|cost\b|ICostBody",
 "PDM": r"\bPDM\b|SwDM|documentmgr",
 "路由 Routing": r"routing|SWRouting|pipe|tube",
 "DFM": r"\bDFM\b|manufactur",
 "DimXpert/公差": r"dimxpert|tolerance|\bGD&T\b",
}
print("%-18s %s" % ("项目", " ".join("%-9s" % k.split()[0] for k in keys)))
for name, path in proj.items():
    p = Path(path)
    if not p.exists(): print("%-18s (不在本地)" % name); continue
    txt = ""
    for f in p.rglob("*"):
        if f.is_file() and f.suffix in (".py",".ts",".cs",".md") and not any(x in str(f) for x in (".venv","node_modules","site-packages",".git","__pycache__")):
            try: txt += f.read_text(encoding="utf-8", errors="ignore")
            except Exception: pass
    row = []
    for k, rx in keys.items():
        row.append("  ✓      " if re.search(rx, txt, re.I) else "  ·      ")
    print("%-18s %s" % (name, " ".join(row)))
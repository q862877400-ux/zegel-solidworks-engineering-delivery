import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
MIT = ["codestack","CSharpAndSolidWorks","solidworks-api","solidworks-auto-modeling",
       "Solidworks-MCP","solidworks-skills","sw-api-skill","sw-ai-bridge",
       "solidworks-com-automation-skill","SolidworksMCP-TS","sw-automation-skill",
       "solidworks-skills"]
BUCKETS = {
 "A 错误码/HResult": re.compile(r"0x[0-9A-Fa-f]{4,8}"),
 "B 弹窗/对话框":    re.compile(r"(弹窗|对话框|dialog|Dialog|MessageBox|警告窗|提示框|"
                            r"Message Bar|GetMessageBar|警告)", re.I),
 "C 选区/选中":      re.compile(r"(SelectByID2|AddSelectionListObject|GetSelectedObjectCount|"
                            r"GetSelectedObjectTypeNames2|选区)", re.I),
 "D by-ref/变体":    re.compile(r"(VARIANT\(|Nothing|Empty|by-?ref|out param|"
                            r"DumbDispatch|VT_DISPATCH)", re.I),
 "E 许可/连接":      re.compile(r"(not licensed|ProgID|0x80040112|Could not load|"
                            r"COM 类|未许可)", re.I),
 "F 诊断/状态回读":  re.compile(r"(GetLastError|GetErrorMessages|诊断|diagnos|"
                            r"GetWhatsWrong|NeedsRebuild|GetProcessID)", re.I),
}
for label, pat in BUCKETS.items():
    n = 0
    for repo in MIT:
        d = R / repo
        if not d.is_dir(): continue
        for f in d.rglob("*"):
            if f.suffix.lower() not in (".md",".py",".cs",".vba",".ts",".js"): continue
            if ".git" in f.parts or "node_modules" in f.parts: continue
            try: txt = f.read_text(encoding="utf-8", errors="replace")
            except Exception: continue
            for i, l in enumerate(txt.splitlines()):
                l = l.strip()
                if pat.search(l) and 14 < len(l) < 190:
                    n += 1
                    break
    print("  %-16s 命中文件 %3d 个" % (label, n))
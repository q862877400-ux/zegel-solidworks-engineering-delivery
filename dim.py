import os, re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
MIT = ["codestack","CSharpAndSolidWorks","solidworks-api","solidworks-auto-modeling",
       "Solidworks-MCP","solidworks-skills","sw-api-skill","sw-ai-bridge",
       "solidworks-com-automation-skill","SolidworksMCP-TS","sw-automation-skill",
       "solidworks-automation-skill"]
PAT = re.compile(r"(CanWrite|CanRead|GetSetMethod|GetGetMethod|propget|propput|"
                 r"TypeLibFunc|FHidden|IsOptional|OutAttribute|ParameterInfo|"
                 r"write.?only|read.?only|只读|只写)", re.I)
for repo in MIT:
    d = R / repo
    if not d.is_dir(): continue
    hits = []
    for f in d.rglob("*"):
        if f.suffix.lower() not in (".cs",".py",".ts",".js",".md",".ps1"): continue
        if ".git" in f.parts or "node_modules" in f.parts: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        n = len(PAT.findall(txt))
        if n >= 3:
            hits.append((f.relative_to(d).as_posix(), n))
    hits.sort(key=lambda x: -x[1])
    if hits:
        print("  %-34s %d 文件" % (repo, len(hits)))
        for path, n in hits[:3]:
            print("      %-52s %d 处" % (path[:52], n))
    else:
        print("  %-34s 无" % repo)
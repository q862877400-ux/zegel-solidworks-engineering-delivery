import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
MIT = ["codestack","CSharpAndSolidWorks","solidworks-api","solidworks-auto-modeling",
       "Solidworks-MCP","solidworks-skills","sw-api-skill","sw-ai-bridge",
       "solidworks-com-automation-skill","SolidworksMCP-TS","sw-automation-skill"]
# ① HRESULT / 错误码  ② 参数个数纠正  ③ 许可/ProgID 问题
PATS = {
 "HRESULT/错误码": re.compile(r"0x[0-9A-Fa-f]{8}"),
 "参数个数纠正":   re.compile(r"(不是|需要|应为|实际是|错的是)\s*\d+\s*(个)?参数|"
                             r"\d+\s*参数(?!的)|第\s*\d+\s*个参数"),
 "许可/ProgID":    re.compile(r"not licensed|未许可|没有许可|ProgID|progid|注册|"
                             r"未安装|Could not load|无法连接|连接失败"),
}
for label, pat in PATS.items():
    print("=== %s ===" % label)
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
                if pat.search(l) and 10 < len(l) < 170:
                    print("  [%s] %s:%d" % (repo, f.relative_to(d).as_posix()[:52], i+1))
                    print("     " + l[:150])
                    n += 1
                    if n >= 12: break
            if n >= 12: break
        if n >= 12: break
    print()
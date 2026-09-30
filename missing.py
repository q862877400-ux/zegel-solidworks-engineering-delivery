import sys, subprocess, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")
DONE = {"sldworks","cosworks","swdocumentmgr","SWRoutingLib","sldcostingapi","fworks","swconst"}
out = Path(r"D:\AI\SW\_raw\reflect"); out.mkdir(parents=True, exist_ok=True)
tot_fam = tot_mem = 0
for dll in sorted(R.glob("SolidWorks.Interop.*.dll")):
    asm = dll.stem.replace("SolidWorks.Interop.", "")
    if asm in DONE: continue
    dest = out / f"iface_{asm}.txt"
    if not dest.is_file():
        subprocess.run(["pwsh","-NoProfile","-File",r"D:\AI\SW\tools\reflect-interop.ps1",
                        "-Dll", str(dll), "-Out", str(dest)],
                       capture_output=True)
    if not dest.is_file() or dest.stat().st_size < 200:
        print("  %-28s no-interface" % asm); continue
    txt = dest.read_text(encoding="utf-8", errors="replace")
    fams=set(); cur=None; mem=0
    for l in txt.splitlines():
        if l.startswith("## "): cur=l[3:].strip()
        elif cur and l.strip() and re.match(r"^\S+\s+\w+\s*\(", l.strip()):
            fams.add(cur); mem+=1
    print("  %-28s %4d families / %5d members" % (asm, len(fams), mem))
    tot_fam+=len(fams); tot_mem+=mem
print("  ---- NOT COVERED: %d families / %d members" % (tot_fam, tot_mem))
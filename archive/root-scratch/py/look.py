import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
def look(path, pat, n=7):
    f = R / path
    if not f.is_file(): print("  缺:", path); return
    txt = f.read_text(encoding="utf-8", errors="replace")
    print("  --- %s ---" % path)
    k = 0
    for i, l in enumerate(txt.splitlines(), 1):
        if pat.search(l):
            print("    %5d| %s" % (i, l.strip()[:118])); k += 1
            if k >= n: break
    print()
print("=== SolidworksMCP-TS core-abstractions.ts（33 处，最像模型）===")
look("SolidworksMCP-TS/src/core/interfaces/core-abstractions.ts",
     re.compile(r"(CanWrite|CanRead|readOnly|writeOnly|writable|readonly)", re.I))
print("=== codestack 维度页 ===")
look("codestack/solidworks-api/document/dimensions/set-read-only/index.md",
     re.compile(r"(read.?only|只读|readonly)", re.I), 6)
print("=== solidworks-skills Probe_Sig.cs（探测签名的工具？）===")
look("solidworks-skills/src/probes/Probe_Sig.cs",
     re.compile(r"(Parameter|Property|Method|GetType|Invoke)", re.I), 8)
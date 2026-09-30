import sys, re, json, base64, subprocess
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
OUT = Path(r"C:\swprojects\_tmp_mcp"); OUT.mkdir(exist_ok=True)
def get(path):
    r = subprocess.run(["gh","api","repos/andrewbartels1/SolidworksMCP-python/contents/"+path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    j = json.loads(r.stdout)
    return base64.b64decode(j["content"]).decode("utf-8", errors="replace")
src = get("src/solidworks_mcp/adapters/pywin32_adapter.py")
(OUT/"pywin32_adapter.py").write_text(src, encoding="utf-8")
print("  拉到 %d 字节 / %d 行" % (len(src), src.count(chr(10))))
PAT = re.compile(r"(#.*(must|note|注意|坑|workaround|careful|gotcha|issue|bug|"
                  r"fails?|broke|wrong|instead|avoid)|"
                  r"except\s+\w+Error|DumbDispatch|VARIANT|Dispatch|"
                  r"pywintypes|com_error|0x800)", re.I)
n = 0
for i, l in enumerate(src.splitlines(), 1):
    if PAT.search(l) and 24 < len(l.strip()) < 200:
        print("  %5d| %s" % (i, l.strip()[:175]))
        n += 1
        if n >= 28: break
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
p = B / "fa-open-biz-toolkit-3.0-SNAPSHOT.dll"
raw = p.read_bytes()
print("=== Java 类名（toolkit 业务包）===")
cls = set()
for m in re.findall(rb"L?com/szjlc/fa/toolkit/[A-Za-z0-9_/$]+", raw):
    s = m.decode().replace("L", "", 1)
    s = s.split(";")[0].split("(")[0]
    if len(s) < 80: cls.add(s)
for s in sorted(cls)[:40]:
    print("   ", s)
print()
print("=== 含 model/file/zip/download/export 的类与方法 ===")
hits = set()
for m in re.findall(rb"(?:[ -~]\x00){5,90}", raw):
    try: t = m.decode("utf-16le").strip()
    except Exception: continue
    if re.search(r"(model|download|export|build|translate|file|zip)", t, re.I) and len(t) < 90:
        hits.add(t)
for t in sorted(hits)[:36]:
    print("   ", t)
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
for dll in ("ForfaceSwDriverCoreOffline.dll", "fa-open-biz-toolkit-3.0-SNAPSHOT.dll", "DotNetZip.dll"):
    p = B / dll
    if not p.is_file(): continue
    raw = p.read_bytes()
    # UTF-16LE 与 ASCII 的可打印串
    asc = set(re.findall(rb"[ -~]{4,40}", raw))
    u16 = set(x.decode("utf-16le", "ignore") for x in re.findall(rb"(?:[ -~]\x00){4,40}", raw))
    cands = [s.decode() for s in asc if re.search(rb"(pass|pwd|key|zip|crypt|secret|forface|jlc)", s, re.I)]
    u16 = [u for u in u16 if re.search(r"(pass|pwd|key|zip|crypt|secret|forface|jlc)", u, re.I)]
    print("### %s (%.1f MB)" % (dll, len(raw)/1e6))
    for c in sorted(set(cands))[:10]: print("   ascii:", c[:44])
    for c in sorted(set(u16))[:10]: print("   utf16:", c[:44])
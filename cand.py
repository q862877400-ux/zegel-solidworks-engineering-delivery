import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
pat = re.compile(rb"(?:[ -~]\x00){4,64}")
# 短、可作密码的字面量（4-24 字符，无空格无斜杠）
cands = set()
for dll in sorted(B.glob("*.dll")):
    if dll.stat().st_size > 3_000_000: continue     # 跳过 IKVM 运行时
    raw = dll.read_bytes()
    for m in pat.findall(raw):
        try: s = m.decode("utf-16le").strip()
        except Exception: continue
        if 4 <= len(s) <= 24 and re.fullmatch(r"[A-Za-z0-9_\-!@#$%^&*.]{4,24}", s):
            cands.add(s)
    # ASCII 同样
    for m in re.findall(rb"[A-Za-z0-9_\-!@#$%^&*.]{4,24}", raw):
        cands.add(m.decode())
print("  候选短串:", len(cands))
# 优先挑像密钥/口令的
KEYY = re.compile(r"(key|pass|pwd|secret|zip|sw|forface|jlc|open|fa_|sdk|202)", re.I)
hot = sorted(c for c in cands if KEYY.search(c))
print("  命中关键词的 %d 个:" % len(hot))
for c in hot[:40]:
    print("    ", c)
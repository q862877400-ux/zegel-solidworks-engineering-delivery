import sys, zipfile, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1")
z = sorted((B/"ForFaceSelector"/"model").glob("*.zip"))[0]
zf = zipfile.ZipFile(z)
i = zf.infolist()[0]
print("  compress_type:", i.compress_type, "(99=AES/WinZipAes, 传统=8)")
print("  flag_bits   : 0x%x" % i.flag_bits, "(bit0=加密, bit6=强加密)")
print("  create_system:", i.create_system)
print()
print("  ★ 插件里找密钥/配置线索：")
for p in sorted((B/"ForFaceSelector").glob("*.config")):
    print("   ", p.name)
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.search(r"(pass|key|secret|crypt|token|auth|zip)", l, re.I):
            print("      " + l.strip()[:110])
for name in ("dbpath.xml",):
    p = B/"ForFaceSelector"/name
    if p.is_file():
        print("  ", name, "->", p.read_text(encoding="utf-8", errors="replace")[:220].replace("\n"," "))
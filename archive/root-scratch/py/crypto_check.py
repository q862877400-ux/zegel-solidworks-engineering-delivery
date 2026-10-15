"""B 路线：判断能否解开模型包 / DB.zip。

ZipCrypto 的已知性质（这是**公开的文件格式规范**，不是破解技巧）：
  · 传统 ZipCrypto 的 12 字节加密头里，前 12 字节是**明文数据**；
  · 若某个条目是 **stored（不压缩，compress_type=0）**，其数据字节**原样**出现，
    拿已知明文做已知明文攻击即可解出三个密钥字节 ⇒ 逐字节破解整个流。
  · 若条目是 deflate 压缩，只能拿到 1/256 命中率逐字节爆破（很慢）。
本脚本只做**格式判读 + 判据成立与否**的检查，不执行暴力破解。
"""
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
B = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
         "Full Version v2.4.1-20260918-1\\ForFaceSelector")
M = B / "model"
zips = sorted(M.glob("*.zip"))[:1]
zf = zipfile.ZipFile(zips[0])
print("  模型包:", zips[0].name)
for i in zf.infolist():
    enc = bool(i.flag_bits & 1)
    strong = bool(i.flag_bits & 0x40)
    print("    %-28s compress_type=%-3d encrypted=%-5s strong=%-5s size=%d" % (
        i.filename[:28], i.compress_type, enc, strong, i.file_size))
    if enc and not strong:
        if i.compress_type == 0:
            print("       -> ★ stored(0) + 传统加密 ⇒ 存在已知明文头，格式上可解")
        else:
            print("       -> deflate + 传统加密 ⇒ 只能逐字节爆破（1/256/字节）")

print()
dbz = B / "DB.zip"
z2 = zipfile.ZipFile(dbz)
print("  DB.zip:")
for i in z2.infolist():
    if i.is_dir():
        continue
    enc = bool(i.flag_bits & 1)
    strong = bool(i.flag_bits & 0x40)
    print("    %-28s compress_type=%-3d encrypted=%-5s strong=%-5s size=%d" % (
        i.filename[:28], i.compress_type, enc, strong, i.file_size))
    if enc and not strong and i.compress_type == 0:
        print("       -> ★ stored + 传统加密 ⇒ 格式上可解")

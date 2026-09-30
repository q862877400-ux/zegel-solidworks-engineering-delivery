import sys, zipfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
B = Path(r"D:\Program Files\SOLIDWORKS Corp\JLCFA Parts Library Plugin Full Version v2.4.1-20260918-1\ForFaceSelector")
zf = zipfile.ZipFile(B / "DB.zip")
for i in zf.infolist():
    kind = "DIR " if i.is_dir() else "FILE"
    print("  %s %-30s %10.1f MB  compress_type=%d flag=0x%x" % (
        kind, i.filename, i.file_size/1e6, i.compress_type, i.flag_bits))
print()
print("  ★ DB 里那两个无扩展名的是什么？（可能是 SQLite）")
for n in ("DB/sw-fa-prod-builder", "DB/sw-fa-prod-selector"):
    try:
        with zf.open(n) as f:
            head = f.read(32)
        print("    %-24s 头 32 字节: %r" % (n.split("/")[-1], head[:32]))
        if head[:15] == b"SQLite format 3":
            print("       -> ★ 是 SQLite 数据库")
    except Exception as e:
        print("    %-24s 读失败(加密?): %s" % (n.split("/")[-1], str(e)[:60]))
print()
print("  ★ 试读第一个字节（传统 zip 密码校验）")
for pw in (b"", b"jlc", b"forface", b"123456", b"jlc123"):
    try:
        with zipfile.ZipFile(B / "DB.zip") as z2:
            z2.setpassword(pw)
            data = z2.read("DB/sw-fa-prod-selector")
        print("    密码 %-10r -> 成功! %d bytes, 头 %r" % (pw, len(data), data[:24]))
        break
    except Exception as e:
        print("    密码 %-10r -> %s" % (pw, str(e)[:52]))
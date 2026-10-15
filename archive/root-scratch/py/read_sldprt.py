# -*- coding: utf-8 -*-
"""不启动 SolidWorks，直接读 .SLDPRT 文件头 —— 判断是否参数化、配置叫什么。

⚠ SolidWorks 零件文件是复合文档（OLE2），配置名与参数以明文存在其中。
⚠ 本脚本**只读文件字节**，不碰 COM、不启动 SolidWorks。
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BF = Path("D:\\Program Files\\SOLIDWORKS Corp\\JLCFA Parts Library Plugin "
          "Full Version v2.4.1-20260918-1\\ForFaceSelector\\BuildFile")

for p in sorted(BF.iterdir()):
    if not p.is_file() or p.name.startswith("~$"):
        continue
    raw = p.read_bytes()
    print("=== %s  (%.0f KB)" % (p.name[:64], len(raw) / 1024))
    print("    头:", raw[:8], " 复合文档" if raw[:8] == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" else " 非 OLE2")
    # ASCII 与 UTF-16LE 的可读串
    asc = re.findall(rb"[ -~]{5,70}", raw)
    u16 = [m.decode("utf-16le", "ignore") for m in re.findall(rb"(?:[ -~]\x00){5,70}", raw)]
    # 配置名：SolidWorks 配置文件通常形如 MGW12CZ0C / Default / 自定义名
    cands = [s.decode() for s in asc]
    cands += u16
    keys = ("configuration", "Config", "config", "Default", "size", "Size",
            "equation", "Equation", "Global", "variable", "param", "Param")
    hit = [c for c in cands if any(k in c for k in keys)]
    print("    含配置/参数关键词的串 %d 条（样例）:" % len(hit))
    seen = set()
    for h in hit:
        if h in seen:
            continue
        seen.add(h)
        print("      ", h[:66])
        if len(seen) >= 10:
            break
    # 文件名里的型号往往就是配置名，单独找一遍
    stem = p.stem
    m = re.search(r"\(([^()]+)\)", stem)
    if m:
        code = m.group(1)
        exact = [c for c in cands if code in c]
        print("    文件名里的型号 %r 在文件内出现 %d 次" % (code[:40], len(exact)))
    print()

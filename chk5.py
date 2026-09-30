import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
print("=== 第三方说法 vs 我的反射 ===")
claims = [
  ("ISldWorks", "GetErrorMessages", "三个全是 [out]，调用方一个不传"),
  ("ISldWorks", "OpenDoc6",      "errors/warnings 是 by-ref 需 VARIANT"),
  ("IModelDocExtension", "RunMacro2", "nRetval 是 ByRef Long"),
]
for iface, mem, claim in claims:
    m = re.search(r"(?ms)^## %s\s*\r?\n(.*?)(?=\r?\n## |\Z)" % iface, SW)
    if not m:
        print("  %s.%s —— **反射里没有这个接口 **" % (iface, mem)); continue
    found = [l.strip() for l in m.group(1).splitlines()
             if re.match(r"^\s*\S+\s+%s\d?\s*\(" % re.escape(mem), l.strip())]
    print("  %s.%s" % (iface, mem))
    print("     第三方说: %s" % claim)
    for l in found[:3]:
        sig = re.match(r"^\s*\S+\s+(\w+)\s*\((.*)\)\s*$", l)
        ps = [a.strip() for a in sig.group(2).split(",") if a.strip()]
        byref = [a for a in ps if a.endswith("&")]
        print("     反射:     %-14s 共%2d参 / by-ref %d 个 -> %s"
              % (sig.group(1), len(ps), len(byref), byref or "无"))
import re, sys, html
sys.stdout.reconfigure(encoding="utf-8")
s = open(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks\SOLIDWORKS.Interop.cosworks~SOLIDWORKS.Interop.cosworks.ICWLoadsAndRestraintsManager_members.html", encoding="utf-8", errors="replace").read()
for m in re.finditer(r"[^<>]*[Tt]opolog[^<>]*", s):
    print("  ", html.unescape(m.group(0)).strip())
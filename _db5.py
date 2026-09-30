import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
cur = None
for raw in text.splitlines():
    if raw.startswith("## "):
        cur = raw[3:].strip()
    elif cur and "SetCallout" in raw:
        print("  SetCallout 属于 %s  ->  %s" % (cur, raw.strip()))

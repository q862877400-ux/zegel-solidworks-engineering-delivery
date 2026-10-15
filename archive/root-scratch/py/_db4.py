import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
# 逐行解析，不用正则截断
cur, blocks = None, {}
for raw in text.splitlines():
    if raw.startswith("## "):
        cur = raw[3:].strip()
        blocks[cur] = []
    elif cur and raw.strip():
        blocks[cur].append(raw.strip())
blk = blocks.get("IModelView", [])
print("  IModelView 逐行解析成员数 =", len(blk))
for m in ("SetCallout","CreateCallout","GetMouse","Activate","ZoomByFactor"):
    print("  %-16s 在 IModelView = %s" % (m, any(x.startswith(("Boolean ","Void ","Object ","Int32 ","Callout ","ModelDoc ","Mouse ","Double ")) and m+"(" in x for x in blk)))

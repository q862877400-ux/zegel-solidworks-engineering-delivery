import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
text = open(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt", encoding="utf-8", errors="replace").read()
block = re.search(r"(?ms)^## IModelView\s*\r?\n(.*?)(?=\r?\n## |\Z)", text)
print("  取到段长度 =", len(block.group(1)) if block else "None")
for m in ("SetCallout","CreateCallout","GetMouse"):
    print("  %-16s in block = %s" % (m, bool(re.search(rf"\b{m}\s*\(", block.group(1)))))

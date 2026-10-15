import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sw = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
for name in ("MinValue", "MaxValue", "MinType", "ToleranceName", "MateType",
             "GetAdjacentFace", "DisplayFormat", "EnableFeatureScope"):
    hits = re.findall(r"\b(\w*%s\w*)\s*\(" % name, sw)
    uniq = sorted(set(hits))[:4]
    print("  %-22s -> %s" % (name, uniq if uniq else "** 反射里没有 **"))

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"D:\AI\SW\AI Solidworks\官方文档")
WANT = ("AddElasticConnector", "AddConvection", "AddHeatFlux", "AddHeatPower",
        "AddTemperature", "AddRadiation")


def page_text(p: Path) -> str:
    raw = p.read_text(encoding="utf-8", errors="replace")
    #: \u2605 \u6b63\u6587\u5728 JSON \u7684 `helpText` \u91cc\uff08\u8f6c\u4e49\u8fc7\u7684 XML\uff09
    m = re.search(r'"helpText"\s*:\s*"(.*?)"\s*,\s*"', raw, re.S)
    seg = m.group(1) if m else raw
    seg = (seg.replace("\\u003c", "<").replace("\\u003e", ">")
              .replace('\\"', '"').replace("\\n", "\n").replace("\\/", "/"))
    seg = re.sub(r"<[^>]+>", " ", seg)
    seg = seg.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"[ \t]+", " ", seg)


for w in WANT:
    hits = list(BASE.rglob("*%s.html" % w))
    if not hits:
        print("  **%s\uff1a\u65e0\u9875**" % w); continue
    txt = re.sub(r"\n{2,}", "\n", page_text(hits[0]))
    print("  ---- %s ----" % w)
    m = re.search(r"(Function\s+%s\s*\([^)]*\))" % w, txt)
    print("     VB\uff1a%s" % (m.group(1).strip()[:320] if m else "**\u672a\u627e\u5230 Function \u884c**"))
    i = txt.find("Parameters")
    if i >= 0:
        seg = txt[i:i + 700].splitlines()
        shown = 0
        for l in seg[1:]:
            l = l.strip()
            if not l or l.startswith("Return") or shown >= 8:
                continue
            print("       " + l[:118]); shown += 1

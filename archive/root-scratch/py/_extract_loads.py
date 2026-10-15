import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(r"D:\AI\SW\AI Solidworks\官方文档")
WANT = ("AddElasticConnector", "AddConvection", "AddHeatFlux", "AddHeatPower",
        "AddTemperature", "AddRadiation")


def strip_html(s: str) -> str:
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return re.sub(r"[ \t]+", " ", s)


for w in WANT:
    hits = list(BASE.rglob("*%s.html" % w))
    if not hits:
        print("  **%s: \u65e0\u9875**" % w)
        continue
    txt = strip_html(hits[0].read_text(encoding="utf-8", errors="replace"))
    txt = re.sub(r"\n{2,}", "\n", txt)
    #: \u2605 VB \u58f0\u660e\u90a3\u4e00\u884c\uff08\u5b83\u957f\u5f97\u50cf "Function AddXxx(...) As ..."\uff09
    m = re.search(r"(Function\s+%s\s*\([^)]*\)[^\n]{0,60})" % w, txt)
    print("  ---- %s ----" % w)
    print("     \u58f0\u660e\uff1a%s" % (m.group(1).strip()[:300] if m else "**\u672a\u627e\u5230**"))
    #: \u2605 \u53c2\u6570\u8868\uff08\u9010\u884c "Name  Description" \u5f62\u6001\uff09
    i = txt.find("Parameters")
    if i >= 0:
        seg = txt[i:i + 900]
        for l in seg.splitlines()[:16]:
            l = l.strip()
            if l and l not in ("Parameters",):
                print("       " + l[:120])

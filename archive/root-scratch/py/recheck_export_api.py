import sys, urllib.request, re, json
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.stdout.reconfigure(encoding="utf-8")
from tools.fetch_api_signature import _system_proxy, _unescape
p = _system_proxy()
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http":p,"https":p}))

# ① 官方帮助站的**搜索接口**（Help 站常带 search）
cands = [
  "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~CWResults~ExportSmoothedMesh.html",
  "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~ICWResults~ExportSmoothedMesh.html",
  "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~CWResults~SaveSmoothedMesh.html",
  "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~ICWResults~GetSmoothedMesh.html",
]
print("=== ① 直接猜 URL（判据：页面真有 pagetitle + Syntax）===")
for u in cands:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with op.open(req, timeout=20) as r:
            t = _unescape(r.read().decode("utf-8", errors="replace"))
        good = ('id="pagetitle"' in t) and ("Syntax" in t)
        m = re.search(r'id="pagetitle"[^>]*>([^<]{0,80})', t)
        print("  %-6s %s  标题=%r" % ("✓真页" if good else "✗通用页", u.split('/api/')[1][:72], (m.group(1) if m else "")))
    except Exception as e:
        print("  ✗ 取不到 %s" % u.split('/api/')[1][:60])

print()
print("=== ② 用官方帮助站自带的搜索（若可用）===")
for q in ["ExportSmoothedMesh","SmoothedMesh","ViewConvergenceData","MaterialMass"]:
    for su in [f"https://help.solidworks.com/2026/english/api/Search.aspx?q={q}",
               f"https://help.solidworks.com/search?q={q}&version=2026"]:
        try:
            req = urllib.request.Request(su, headers={"User-Agent":"Mozilla/5.0"})
            with op.open(req, timeout=15) as r:
                t = r.read().decode("utf-8", errors="replace")
            print("  %-22s %s → HTTP200 len=%d" % (q, su.split('/')[-1][:30], len(t)))
            break
        except Exception as e:
            pass
    else:
        print("  %-22s 两个搜索端点都取不到" % q)
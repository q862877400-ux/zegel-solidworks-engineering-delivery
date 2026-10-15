import sys, urllib.request
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.stdout.reconfigure(encoding="utf-8")
from tools.fetch_api_signature import _system_proxy, _unescape
p = _system_proxy()
print("  系统代理 = %r" % p)
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http":p,"https":p}) if p else urllib.request.ProxyHandler({}))
cands = [
 "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~CosmosWorksLib.CWStudy~CreateMesh.html",
 "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~CWStudy~CreateMesh.html",
 "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~CosmosWorksLib.ICWStudy~CreateMesh.html",
 "https://help.solidworks.com/2026/english/api/cosworksapi/CosmosWorksLib~ICWStudy~CreateMesh.html",
]
for u in cands:
    try:
        req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
        with op.open(req, timeout=20) as r:
            raw = r.read().decode("utf-8", errors="replace")
        t = _unescape(raw)
        has_m = "CreateMesh" in t
        has_s = "Syntax" in t
        # 看标题
        import re
        m = re.search(r'id="pagetitle"[^>]*>([^<]{0,80})', t)
        title = m.group(1) if m else "(无 pagetitle)"
        print("  HTTP200 len=%-7d CreateMesh=%-5s Syntax=%-5s 标题=%r" % (len(raw), has_m, has_s, title))
        print("      %s" % u.split('/api/')[1])
    except Exception as e:
        print("  ✗ %s → %s" % (u.split('/api/')[1][:60], str(e)[:50]))
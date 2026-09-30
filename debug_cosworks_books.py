import sys, urllib.request, re
sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.stdout.reconfigure(encoding="utf-8")
from tools.fetch_api_signature import _system_proxy, _unescape
p = _system_proxy()
op = urllib.request.build_opener(urllib.request.ProxyHandler({"http":p,"https":p}))
books = ["cosworksapi","simulationapi","cworksapi","cwapi","simulation"]
libs  = ["CosmosWorksLib","SolidWorks.Interop.cosworks"]
ok = []
for b in books:
    for l in libs:
        for form in (f"{l}~CWStudy~CreateMesh", f"{l}~{l}.CWStudy~CreateMesh"):
            u = f"https://help.solidworks.com/2026/english/api/{b}/{form}.html"
            try:
                req = urllib.request.Request(u, headers={"User-Agent":"Mozilla/5.0"})
                with op.open(req, timeout=12) as r:
                    t = _unescape(r.read().decode("utf-8", errors="replace"))
                good = "Syntax" in t and 'id="pagetitle"' in t
                if good:
                    ok.append(u)
                    m = re.search(r'id="pagetitle"[^>]*>([^<]{0,70})', t)
                    print("  ✓✓ 命中! %s" % u.split('/api/')[1])
                    print("      标题=%r" % (m.group(1) if m else "?"))
            except Exception:
                pass
if not ok:
    print("  以上册名/形态均无「真有内容」的页 ⇒ **cosworks 不在线可查**")
    print("  ⇒ 本地 VB6 CHM（C:\\cworks_vb6）是 Simulation 签名的唯一来源")
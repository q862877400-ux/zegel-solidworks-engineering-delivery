import re, sys, io, json, subprocess
sys.stdout.reconfigure(encoding="utf-8")
def get(path):
    r = subprocess.run(["gh","api","repos/uPesy/easyeda2kicad.py/contents/"+path],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    import base64
    return base64.b64decode(json.loads(r.stdout)["content"]).decode("utf-8", errors="replace")
for p in ("easyeda/__init__.py", "easyeda/api.py", "easyeda/footprint.py", "README.md"):
    try:
        t = get(p)
    except Exception as e:
        print("  缺", p); continue
    urls = sorted(set(re.findall(r"https?://[a-z0-9.\-]+/api[^'\"\s)]*", t, re.I)))
    fmt = sorted(set(re.findall(r"\.(step|stp|wrl|vrml|fcstd|kicad_\w+|json|obj|3ds|igs|sldprt)\b", t, re.I)))
    print("  %-24s 端点 %d  格式 %s" % (p, len(urls), sorted(set(fmt))[:6]))
    for u in urls[:5]: print("        " + u)
import re, sys, io, json, base64, subprocess
sys.stdout.reconfigure(encoding="utf-8")
def tree(repo):
    r = subprocess.run(["gh","api",f"repos/{repo}/git/trees/HEAD?recursive=1"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [t["path"] for t in json.loads(r.stdout)["tree"] if t.get("size",0) > 0]
def get(repo, path):
    r = subprocess.run(["gh","api",f"repos/{repo}/contents/{path}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    return base64.b64decode(json.loads(r.stdout)["content"]).decode("utf-8", errors="replace")
for repo in ("uPesy/easyeda2kicad.py", "TousstNicolas/JLC2KiCad_lib"):
    print("###", repo)
    files = [p for p in tree(repo) if p.endswith(".py")][:40]
    api = set(); fmt = set()
    for p in files:
        try: t = get(repo, p)
        except Exception: continue
        api |= set(re.findall(r"https?://[a-z0-9.\-]+/[a-z0-9/_.\-]*api[a-z0-9/_.\-]*", t, re.I))
        fmt |= set(re.findall(r"\.(step|stp|wrl|vrml|fcstd|obj|3ds|igs|sldprt)\b", t, re.I))
    print("  API 端点:")
    for u in sorted(api)[:8]: print("    " + u)
    print("  3D 格式:", sorted(fmt))
    print()
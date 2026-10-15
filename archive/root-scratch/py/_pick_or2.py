"""找签名兼容现有注入（model / 无参）的孤立能力 —— 试点用，不用新解析器。"""
import inspect, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, str(R)); sys.path.insert(0, str(R / "scripts"))

DEF = re.compile(r"^def ([a-z_]\w*)\(", re.M)
funcs = {}
for p in sorted((R / "scripts").glob("sw_*.py")):
    for fn in DEF.findall(p.read_text(encoding="utf-8", errors="ignore")):
        funcs.setdefault(fn, p.name)

srv = (R / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
disp = {fn for _, _, fn in re.findall(r'"(\w+)":\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*,', srv)}
spec = set()
for p in (R / "mcp-server").glob("tool_specs_*.py"):
    spec |= set(re.findall(r'function="([\w]+)"', p.read_text(encoding="utf-8", errors="ignore")))
exposed = disp | spec

prod, tests = set(), set()
for d, b in (("scripts", prod), ("subskills", prod), ("examples", prod), ("mcp-server", prod), ("tests", tests)):
    base = R / d
    if not base.is_dir():
        continue
    for p in base.rglob("*.py"):
        src = p.read_text(encoding="utf-8", errors="ignore")
        others = {f for f, o in funcs.items() if o != p.name}
        for m in re.finditer(r"\b(\w+)\s*\(", src):
            if m.group(1) in others:
                b.add(m.group(1))

INTERNAL = re.compile(r"(_to_|_from_|^parse|^normalize|^empty|^variant|^callout|^pump|^_|^get_com|^coerce|^make_empty)")
cands = []
for f, mod in funcs.items():
    if f in exposed or INTERNAL.search(f) or f in prod or f in tests:
        continue
    try:
        mod_obj = __import__("scripts." + mod[:-3], fromlist=["x"])
        sig = inspect.signature(getattr(mod_obj, f))
    except Exception:
        continue
    ps = list(sig.parameters.values())
    # 兼容性：第一个参数名叫 model，或完全无参
    ok = (not ps) or (ps[0].name == "model" and all(
        p.default is not inspect.Parameter.empty or p.kind in (p.KEYWORD_ONLY, p.VAR_KEYWORD)
        for p in ps[1:]))
    if ok:
        cands.append((mod, f, str(sig)))

from collections import defaultdict
by = defaultdict(list)
for mod, f, sig in cands:
    by[mod].append((f, sig))
print("签名兼容（`model` 或无参）的孤立能力：**%d** 个，跨 %d 个模块" % (len(cands), len(by)))
for mod in sorted(by, key=lambda m: -len(by[m]))[:8]:
    print("  ── %s（%d）" % (mod, len(by[mod])))
    for f, sig in by[mod][:5]:
        print("       %-38s %s" % (f, sig[:64]))

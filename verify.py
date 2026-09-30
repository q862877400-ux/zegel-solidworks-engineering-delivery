import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# 逐条核实：这些说法与我反射抄到的签名对不对得上
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(
    encoding="utf-8", errors="replace")
def sig(iface, member):
    m = re.search(r"(?ms)^## %s\s*\r?\n(.*?)(?=\r?\n## |\Z)" % iface, SW)
    if not m: return None
    out = []
    for l in m.group(1).splitlines():
        mm = re.match(r"^\s*\S+\s+(%s)\s*\((.*)\)\s*$" % re.escape(member), l.strip())
        if mm:
            ps = [a.strip() for a in mm.group(2).split(",") if a.strip()]
            real = [a for a in ps if not a.endswith("&")]
            out.append((len(ps), len(real), mm.group(2)[:70]))
    return out
print("=== 仓库的说法 vs 我反射抄到的 ===")
for iface, mem, claim in (
    ("IModelDocExtension", "SelectByID2", "第8参数必须 VARIANT(VT_DISPATCH,None)"),
    ("IFeatureManager", "FeatureExtrusion2", "23 参数"),
    ("IFeatureManager", "FeatureExtrusion3", "23 参数"),
    ("IFeatureManager", "FeatureCut4", "27 参数"),
    ("IMate2", "AddMate5", "15 参数"),
):
    s = sig(iface, mem)
    print("  %s.%s" % (iface, mem))
    print("     仓库称: %s" % claim)
    print("     反射:   %s" % (s if s else "** 反射里没有这个成员 **"))
print()
print("=== FeatureCut 全版本（仓库称 20/23/26/27）===")
for l in re.findall(r"^\s*\S+\s+(FeatureCut\d?)\s*\((.*)\)\s*$",
                    re.search(r"(?ms)^## IFeatureManager\s*\r?\n(.*?)(?=\r?\n## |\Z)",
                              SW).group(1), re.M):
    ps = [a.strip() for a in l[1].split(",") if a.strip()]
    real = [a for a in ps if not a.endswith("&")]
    print("    %-14s 整行 %2d 参 / 非 by-ref %2d 参" % (l[0], len(ps), len(real)))
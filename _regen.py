import json, re, sys, io, subprocess
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
REFL = {
 "sldworks": r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt",
 "cosworks": r"D:\AI\SW\_raw\reflect\iface_cosworks.txt",
 "swdocumentmgr": r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt",
 "SWRoutingLib": r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt",
 "sldcostingapi": r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt",
}
# 每个模块 → (族正则, 反射文件, 登记表路径)
JOBS = [
 ("sw_hubs",              r"'(I\w+)': \{",                    "sldworks", None),
 ("sw_drawing_annotations", r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_part_features",      r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_sketch_sheetmetal",  r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_geometry",           r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_simulation_registry", r"'(ICW\w+)': \{",               "cosworks", None),
 ("sw_simulation_full",    r"'(ICW\w+)': \{",                "cosworks", None),
 ("sw_pdm_full",           r"'(ISwDM\w+)': \{",              "swdocumentmgr", None),
 ("sw_sldworks_remaining", r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_sldworks_lastgap",   r"'(I\w+)': \{",                  "sldworks", None),
 ("sw_routing_costing_full", r"'(I(?:Route|Cost|Wire|Cable|Covering|Ribbon|Electrical|Advanced)\w*)': \{", "SWRoutingLib", None),
]
for mod, pat, refl, out in JOBS:
    p = REPO / "scripts" / f"{mod}.py"
    if not p.is_file(): continue
    src = p.read_text(encoding="utf-8")
    fams = sorted(set(re.findall(pat, src)))
    if not fams:
        print("  [skip] %s 未取到族名单" % mod); continue
    r = subprocess.run([sys.executable, r"D:\AI\SW\tools\gen_member_registry.py",
                        *fams, "--reflect", REFL[refl]],
                       capture_output=True, text=True, encoding="utf-8")
    reg = json.loads(Path(r"D:\AI\SW\_raw\member_registry.json").read_text(encoding="utf-8"))
    n = sum(len(v["members"]) for v in reg.values())
    old = len(fams)
    print("  %-26s 族 %3d / 能力 %5d" % (mod, len(reg), n))
    Path(r"D:\AI\SW\_regen_%s.json" % mod).write_text(
        json.dumps(reg, ensure_ascii=False), encoding="utf-8")

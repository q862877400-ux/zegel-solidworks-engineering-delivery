import json, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\interop-dimension-census.json")
if not p.is_file():
    print("  普查文件不存在"); raise SystemExit(1)
d = json.loads(p.read_text(encoding="utf-8"))
print("  顶层键:", list(d.keys())[:12])
def show(k, v, ind="    "):
    if isinstance(v, dict):
        print(f"{ind}{k}: " + ", ".join(f"{kk}={vv}" for kk, vv in list(v.items())[:10]))
    elif isinstance(v, list):
        print(f"{ind}{k}: {len(v)} 条  例: {v[:3]}")
    else:
        print(f"{ind}{k}: {str(v)[:70]}")
for k, v in d.items():
    show(k, v)
import json
import sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
d = json.loads(Path(r"D:\AI\SW\output\member-owner-interface.json").read_text(encoding="utf-8"))
rows = d.get("unchecked_indirect") or []
print("  未检查项共 **%d** 处" % len(rows))
by_file = Counter(r["file"] for r in rows)
print()
print("  ── 按文件 ──")
for f, n in by_file.most_common():
    kind = "★ 生成的注册表（通用转发，非手写）" if f.startswith("sw_api_") else "手写模块"
    print("    %-36s %2d 处  %s" % (f, n, kind))
hand = [r for r in rows if not r["file"].startswith("sw_api_")]
print()
print("  ★★ **手写模块里**的未检查项: **%d** 处（这些才值得逐条看）" % len(hand))
for r in hand:
    print("    %-30s L%-5d get_com_member(%s, **%s**)" % (r["file"], r["line"], r["owner"], r["arg"]))

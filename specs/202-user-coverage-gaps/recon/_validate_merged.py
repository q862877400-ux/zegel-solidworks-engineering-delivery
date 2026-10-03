"""★ 校验合并总表与 AST 真值逐条一致。"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

RECON = Path(r"D:\AI\SW\specs\202-user-coverage-gaps\recon")

PAT = re.compile(
    r"^\| (\d+) \| `([a-z0-9_]+)` \| (b\d+) \| `([a-z0-9_]+)\.([a-z0-9_]+)` \| "
    r"(.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|$",
    re.M)

txt = (RECON / "preselect-family-merged.md").read_text(encoding="utf-8")
rows = PAT.findall(txt)
specs = json.loads((RECON / "_all_specs.json").read_text(encoding="utf-8"))["specs"]
truth = {s["name"]: s for s in specs}

names = [r[1] for r in rows]
print("main-table rows parsed :", len(rows))
print("distinct tool names    :", len(set(names)))
print("AST ground truth count :", len(truth))
print("missing from table     :", sorted(set(truth) - set(names)) or "none")
print("extra in table         :", sorted(set(names) - set(truth)) or "none")

bad = []
for r in rows:
    s = truth.get(r[1])
    if not s:
        bad.append((r[1], "not in AST"))
        continue
    if r[3] != s["module"] or r[4] != s["function"]:
        bad.append((r[1], f"{r[3]}.{r[4]} != {s['module']}.{s['function']}"))
    bn = int(re.search(r"batch(\d+)", s["file"]).group(1))
    if r[2] != f"b{bn}":
        bad.append((r[1], f"batch {r[2]} != b{bn}"))
print("row mismatches         :", bad or "none")

# 排序检查
print("sorted by tool name    :", names == sorted(names))
# 编号连续
print("index 1..N contiguous  :", [int(r[0]) for r in rows] == list(range(1, len(rows) + 1)))

print()
print("grade tally:")
for k, v in sorted(Counter(r[7] for r in rows).items(), key=lambda x: -x[1]):
    print(f"  {v:4}  {k}")

danger = [r for r in rows if r[7].startswith("真危险")]
safe = [r for r in rows if r[7] == "安全"]
print()
print("真危险 total :", len(danger))
print("安全   total :", len(safe))
print("无关   total :", len(rows) - len(danger) - len(safe))
print("reconcile    :", len(danger) + len(safe) + (len(rows) - len(danger) - len(safe)) == 277)
print()
print("待补依据 rows :", sum(1 for r in rows if "官方依据缺失" in r[9] or "依据链**比同表其它条弱一档" in r[9]))
print("经复核改正 rows:", sum(1 for r in rows if "经复核改正" in r[9] or "经复核改正" in r[7]))
print("路线归属 tally:", sorted(Counter(r[8] for r in rows).items()))
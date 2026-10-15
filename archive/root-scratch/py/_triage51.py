import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

roots = [Path(r"C:\swprojects") / d for d in
         ("Eduardof0nt", "andrewbartels1", "vespo92", "Slacker-LLC", "sw-automation-skill")]
blob = []
for r in roots:
    if not r.is_dir():
        continue
    for ext in ("*.py", "*.cs", "*.vb", "*.md"):
        for p in r.rglob(ext):
            if ".git" in str(p):
                continue
            try:
                blob.append(p.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                pass
TEXT = "\n".join(blob)
print("  来源语料 %.1f MB" % (len(TEXT) / 1e6))

rows = json.loads(
    Path(r"C:\swprojects\sw-skill-fork\docs\family-coverage.json").read_text(encoding="utf-8"))
z = [r for r in rows if (r.get("used") or 0) == 0]
MOTION = ("Feature Interfaces", "Sketch", "Assembly Interfaces", "Drawing Interfaces",
          "Annotation Interfaces", "Model Interfaces", "Motion Studies")
pool = [r for r in z if r.get("official_category", "").split("/")[0] in MOTION]
hit = [r for r in pool if r["family"] in TEXT]
miss = [r for r in pool if r["family"] not in TEXT]

print("")
print("  ── 51 个候选池按那个特征切开 ──")
print("    有现成来源可抄的: **%d 个**   ← 这就是「优先做」的那一档" % len(hit))
for r in hit:
    print("      %-46s %-30s %2d 成员" % (r["family"], r["official_category"][:30], r["members"]))
print("")
print("    没有现成来源（只能照官方文档自建，更贵）: **%d 个**" % len(miss))
for r in miss[:14]:
    print("      %-46s %-30s %2d 成员" % (r["family"], r["official_category"][:30], r["members"]))
if len(miss) > 14:
    print("      …（还有 %d 个）" % (len(miss) - 14))

#: 落盘，供后续特性用
OUT = Path(r"D:\AI\SW\output\candidate-51.json")
OUT.write_text(json.dumps(
    {"with_source": hit, "without_source": miss}, ensure_ascii=False, indent=2), encoding="utf-8")
print("")
print("  产物:", OUT)

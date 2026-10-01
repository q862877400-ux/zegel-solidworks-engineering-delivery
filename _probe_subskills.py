import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
SUB = ROOT / "subskills"

dirs = sorted(d for d in SUB.iterdir() if d.is_dir())
print("  subskills/ 目录: %d" % len(dirs))
for d in dirs:
    man = d / "manifest.yaml"
    ok = "✓" if man.is_file() else "**✗ 没有 manifest.yaml**"
    print("    %-34s %s" % (d.name, ok))
print()

#: 每个 manifest 里声明的 name / 目录名对不对得上
for d in dirs:
    man = d / "manifest.yaml"
    if not man.is_file():
        continue
    t = man.read_text(encoding="utf-8")
    m = re.search(r"(?m)^\s*name\s*:\s*(.+?)\s*$", t)
    declared = m.group(1).strip().strip('"\'') if m else "(无 name)"
    mark = "✓" if declared == d.name else "⚠ 不一致"
    print("    %-34s manifest.name=%-30s %s" % (d.name, declared, mark))

print()
#: 有没有"注册表"提到它们（除了 bundle 同步）
print("  谁提到 subskills/（前 12 处）:")
hits = 0
for p in list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.json")) + list(ROOT.rglob("*.toml")):
    if ".git" in p.parts or "node_modules" in p.parts:
        continue
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    if "subskills" in t:
        hits += 1
        if hits <= 12:
            print("    %s" % str(p.relative_to(ROOT)))
print("    …共 %d 个文件提到" % hits)

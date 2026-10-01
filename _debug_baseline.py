"""查基线里哪条已不存在（fz_fixed）。"""
import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
spec = importlib.util.spec_from_file_location("cep", REPO / "scripts" / "check_env_pitfalls.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["cep"] = mod
spec.loader.exec_module(mod)

baseline = mod.load_falsy_zero_baseline()
now = set()
for d in mod.FALSY_ZERO_DIRS:
    dd = REPO / d
    if not dd.is_dir():
        continue
    for f in sorted(dd.rglob("*.py")):
        if ".git" in f.parts:
            continue
        rel = f.relative_to(REPO).as_posix()
        for _ln, member, _default in mod.find_falsy_zero_default(f):
            now.add("%s:%s" % (rel, member))

print("  基线键数 = %d · 代码里现有 = %d" % (len(baseline), len(now)))
stale = sorted(baseline - now)
print("  基线里**已不存在**的（%d 条）：" % len(stale))
for k in stale:
    print("    %s" % k)
extra = sorted(now - baseline)
print("  代码里有但**基线没有**的（%d 条）：" % len(extra))
for k in extra:
    print("    %s" % k)

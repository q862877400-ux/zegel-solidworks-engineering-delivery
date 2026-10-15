import os
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
VICTIM = ROOT / "subskills" / "solidworks-vibecad" / "manifest.yaml"
BACKUP = VICTIM.read_text(encoding="utf-8")


def run(expr=None):
    args = [sys.executable, "-m", "pytest", "tests/test_subskills_wiring.py",
            "-q", "--no-header", "-p", "no:cacheprovider"]
    if expr:
        args += ["-k", expr]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(ROOT),
                       env={**os.environ,
                            "PYTHONPATH": "%s;%s\\scripts;%s\\mcp-server" % (ROOT, ROOT, ROOT)})
    out = (r.stdout or "") + (r.stderr or "")
    last = [l for l in out.splitlines() if "passed" in l or "failed" in l]
    return r.returncode, (last[-1].strip() if last else out.strip()[-140:])


def show(label, expr=None):
    code, line = run(expr)
    flag = "★ 红" if code != 0 else "绿"
    print("  %-30s exit=%d · %s · %s" % (label, code, flag, line))


show("① 基线（无故障）")
try:
    VICTIM.write_text(BACKUP.replace("name: solidworks-vibecad",
                                     "name: solidworks-vibecad-WRONG", 1), encoding="utf-8")
    show("② 注入 manifest.name 不符", "manifest_name")
finally:
    VICTIM.write_text(BACKUP, encoding="utf-8")
try:
    VICTIM.unlink()
    show("③ 注入 缺 manifest", "has_a_manifest")
finally:
    VICTIM.write_text(BACKUP, encoding="utf-8")
GHOST = ROOT / "subskills" / "solidworks-vibecad" / "examples" / "ZZ_probe_ghost.md"
try:
    GHOST.write_text("临时故障注入：源里有、快照无（非缓存）。\n", encoding="utf-8")
    show("④ 注入 源多一个真文件", "differs_only_by_caches")
finally:
    GHOST.unlink()
print()
show("⑤ 复原后")
print("  精确复原: %s" % (VICTIM.read_text(encoding="utf-8") == BACKUP and not GHOST.exists()))

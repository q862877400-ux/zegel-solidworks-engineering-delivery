import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
GHOST = ROOT / "mcp-server" / "tool_specs_batch99.py"


def run_tests():
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_registry_wiring.py",
         "-q", "--no-header", "-p", "no:cacheprovider"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT),
        env={**__import__("os").environ,
             "PYTHONPATH": "%s;%s\\scripts;%s\\mcp-server" % (ROOT, ROOT, ROOT)})
    out = (r.stdout or "") + (r.stderr or "")
    last = [l for l in out.splitlines() if "passed" in l or "failed" in l]
    return r.returncode, (last[-1] if last else out.strip()[-160:])


# ── 基线 ────────────────────────────────────────────────────────────
rc0, line0 = run_tests()
print("  ① 基线（无故障）      : exit=%d · %s" % (rc0, line0.strip()))

# ── 造故障：放一个**没登记**的批次文件 ──────────────────────────────
GHOST.write_text(
    '"""临时假故障：模拟"文件在、却没登记进 BATCH_MODULES"。"""\n\n'
    "from tool_registry import ToolSpec\n\n"
    "SPECS_BATCH99 = [\n"
    "    ToolSpec(name=\"solidworks_ghost_probe\", title=\"Ghost\",\n"
    "             module=\"sw_part\", function=\"get_bounding_box\",\n"
    "             inject=\"model\", read_only=True, doc=\"假故障\", param_alias={},\n"
    "             params=[]),\n"
    "]\n",
    encoding="utf-8")
try:
    rc1, line1 = run_tests()
    print("  ② 造故障（假批次文件）: exit=%d · %s" % (rc1, line1.strip()))
    print()
    print("  ⇒ ★ %s" % ("**测试确实会红** —— 判据有效（事实 62）" if rc1 != 0
                        else "**测试仍然是绿的** ⇒ 这条判据没在尽职！"))
finally:
    GHOST.unlink()
    rc2, line2 = run_tests()
    print("  ③ 复原后              : exit=%d · %s" % (rc2, line2.strip()))
    print("  假文件已删除: %s" % (not GHOST.exists()))

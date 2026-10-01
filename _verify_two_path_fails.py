import os
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TARGET = ROOT / "mcp-server" / "tool_specs_batch10.py"
BACKUP = TARGET.read_text(encoding="utf-8")


def run():
    r = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_mcp_protocol_layer.py",
         "-q", "--no-header", "-p", "no:cacheprovider", "-k", "declared_in_both"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(ROOT),
        env={**os.environ,
             "PYTHONPATH": "%s;%s\\scripts;%s\\mcp-server" % (ROOT, ROOT, ROOT)})
    out = (r.stdout or "") + (r.stderr or "")
    last = [l for l in out.splitlines() if "passed" in l or "failed" in l]
    return r.returncode, (last[-1] if last else out.strip()[-140:])


rc0, line0 = run()
print("  ① 基线（无故障）                    : exit=%d · %s" % (rc0, line0.strip()))

# ── 注入：往 batch10 加一个**与 server.py 重名**的工具 ──────────────
try:
    TARGET.write_text(BACKUP + '''

# ⚠⚠ 临时故障注入（跑完立刻复原）：与 server.py 里已有的名字**重名**
SPECS_BATCH10.append(
    ToolSpec(
        name="solidworks_current_selection",     # ← server.py 里已有这个
        title="Duplicate probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="临时故障注入：与 server.py 重名。",
        param_alias={}, params=[],
    )
)
''', encoding="utf-8")
    rc1, line1 = run()
    print("  ② 注入重名（batch10 加 server.py 的名字）: exit=%d · %s" % (rc1, line1.strip()))
    print()
    print("  ⇒ ★ %s" % ("**测试确实会红** —— 判据有效（事实 62）" if rc1 != 0
                        else "**仍是绿的** ⇒ 这条判据没在尽职！"))
finally:
    TARGET.write_text(BACKUP, encoding="utf-8")
    rc2, line2 = run()
    print("  ③ 复原后                            : exit=%d · %s" % (rc2, line2.strip()))
    print("  文件精确复原: %s" % (TARGET.read_text(encoding="utf-8") == BACKUP))

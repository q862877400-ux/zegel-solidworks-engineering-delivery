import os
import re
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TARGET = ROOT / "mcp-server" / "tool_specs_batch10.py"
BACKUP = TARGET.read_text(encoding="utf-8")

#: ★ 取一个**真在 server.py 里**的名字（跨路径重复才算）
NAME = re.compile(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')
srv = NAME.findall((ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8"))
DUP = "solidworks_collect_model_summary" if "solidworks_collect_model_summary" in srv else srv[0]
print("  用一个**真在 server.py 里**的名字做注入: %s" % DUP)


def run(expr=None):
    args = [sys.executable, "-m", "pytest", "tests/test_mcp_protocol_layer.py",
            "-q", "--no-header", "-p", "no:cacheprovider"]
    if expr:
        args += ["-k", expr]
    r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(ROOT),
                       env={**os.environ,
                            "PYTHONPATH": "%s;%s\\scripts;%s\\mcp-server" % (ROOT, ROOT, ROOT)})
    out = (r.stdout or "") + (r.stderr or "")
    last = [l for l in out.splitlines() if "passed" in l or "failed" in l]
    return r.returncode, (last[-1] if last else out.strip()[-140:])


INJECT = '''

SPECS_BATCH10.append(
    ToolSpec(
        name="%s",          # ← 与 server.py 重名
        title="Duplicate probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="临时故障注入：与 server.py 重名。",
        param_alias={}, params=[],
    )
)
''' % DUP

try:
    rc0, l0 = run("declared_in_both or duplicate_declarations")
    print("  ① 基线（无故障）      : exit=%d · %s" % (rc0, l0.strip()))
    TARGET.write_text(BACKUP + INJECT, encoding="utf-8")
    rc1, l1 = run("declared_in_both or duplicate_declarations")
    print("  ② 注入**跨路径重名**  : exit=%d · %s" % (rc1, l1.strip()))
    print()
    print("  ⇒ ★ %s" % ("**判据确实会红** —— 有效（事实 62）" if rc1 != 0
                        else "**仍是绿的** ⇒ 没在尽职！"))
finally:
    TARGET.write_text(BACKUP, encoding="utf-8")
    rc2, l2 = run("declared_in_both or duplicate_declarations")
    print("  ③ 复原后              : exit=%d · %s" % (rc2, l2.strip()))
    print("  精确复原: %s" % (TARGET.read_text(encoding="utf-8") == BACKUP))

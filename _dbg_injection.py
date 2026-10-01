import os
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
TARGET = ROOT / "mcp-server" / "tool_specs_batch10.py"
BACKUP = TARGET.read_text(encoding="utf-8")

INJECT = '''

SPECS_BATCH10.append(
    ToolSpec(
        name="solidworks_current_selection",
        title="Duplicate probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="临时故障注入：与 server.py 重名。",
        param_alias={}, params=[],
    )
)
'''

CHECK = '''
import sys
sys.path.insert(0, r"C:\\swprojects\\sw-skill-fork\\mcp-server")
sys.stdout.reconfigure(encoding="utf-8")
import register_capabilities as rc
names = [s.name for s in rc.all_specs()]
print("  all_specs(): %d 条" % len(names))
print("  含 solidworks_current_selection? %s" % ("solidworks_current_selection" in names))
print("  重复项: %s" % [n for n in set(names) if names.count(n) > 1])
'''
try:
    TARGET.write_text(BACKUP + INJECT, encoding="utf-8")
    r = subprocess.run([sys.executable, "-c", CHECK], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT),
                       env={**os.environ, "PYTHONPATH": "%s;%s\\mcp-server" % (ROOT, ROOT)})
    print("  ── 注入后直接查 all_specs() ──")
    print((r.stdout or "").strip() or (r.stderr or "").strip()[-300:])
finally:
    TARGET.write_text(BACKUP, encoding="utf-8")
    print("  已复原: %s" % (TARGET.read_text(encoding="utf-8") == BACKUP))

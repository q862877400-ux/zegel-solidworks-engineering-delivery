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
import re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\\swprojects\\sw-skill-fork")
sys.path.insert(0, str(REPO / "mcp-server"))
NAME = re.compile(r'name\\s*=\\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"')
srv = NAME.findall((REPO / "mcp-server" / "server.py").read_text(encoding="utf-8"))
import register_capabilities as rc
bat = [s.name for s in rc.all_specs()]
print("  server.py: %d 条 · batch: %d 条" % (len(srv), len(bat)))
ov = sorted(set(srv) & set(bat))
print("  ★ 交集: %d %s" % (len(ov), ov[:5]))
'''
try:
    TARGET.write_text(BACKUP + INJECT, encoding="utf-8")
    r = subprocess.run([sys.executable, "-c", CHECK], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(ROOT),
                       env={**os.environ, "PYTHONPATH": "%s;%s\\mcp-server" % (ROOT, ROOT)})
    print("  ── 注入后直接算交集 ──")
    print((r.stdout or "").strip() or (r.stderr or "").strip()[-400:])
finally:
    TARGET.write_text(BACKUP, encoding="utf-8")
    print("  已复原: %s" % (TARGET.read_text(encoding="utf-8") == BACKUP))

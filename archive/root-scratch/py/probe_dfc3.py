import json, subprocess, sys, tempfile
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
tmp = Path(tempfile.mkdtemp())
doc = tmp / "d.cadstudio.json"
doc.write_text(json.dumps({"process":"machining","material":"Al6061","wallThickness":3}), encoding="utf-8")
prof = tmp / "p.json"
prof.write_text(json.dumps({"schema":"cadstudio.dfm-profile","id":"cli-profile","limits":{"minimumWallThickness":2.5}}), encoding="utf-8")
r = subprocess.run([sys.executable, "scripts/dfm_review.py", "--input", str(doc), "--output", str(tmp/"o.json"), "--profile", str(prof)],
                   capture_output=True, cwd=".")
try:
    p = json.loads(r.stdout.decode("utf-8", "replace"))
    print("  status =", p.get("status"))
    for k in ("blockedReasons", "reviewFindings", "missingInputs", "error", "errors", "diagnostics", "capabilitySnapshot"):
        v = p.get(k)
        if v: print("  %s = %s" % (k, json.dumps(v, ensure_ascii=False)[:700]))
    print("  全部键:", sorted(p.keys()))
except Exception as e:
    print("  解析失败:", e)
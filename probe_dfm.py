import json, subprocess, sys, tempfile, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
tmp = Path(tempfile.mkdtemp())
doc = tmp / "d.cadstudio.json"
doc.write_text(json.dumps({"process":"machining","material":"Al6061","wallThickness":3}), encoding="utf-8")
prof = tmp / "p.json"
prof.write_text(json.dumps({"schema":"cadstudio.dfm-profile","id":"cli-profile","limits":{"minimumWallThickness":2.5}}), encoding="utf-8")
out = tmp / "o.json"
r = subprocess.run([sys.executable, "scripts/dfm_review.py", "--input", str(doc), "--output", str(out), "--profile", str(prof)],
                   capture_output=True, cwd=".")
print("  returncode =", r.returncode)
raw = r.stdout
print("  stdout 长度 =", len(raw))
print("  第 259 字节附近（字节级）:")
print("   ", raw[240:300])
try:
    raw.decode("gbk"); print("  ✓ GBK 可解")
except Exception as e:
    print("  ✗ GBK 不可解:", e)
    print("  ← 该位置上下文（UTF-8 解）:", raw[200:340].decode("utf-8", "replace"))
print("  stderr:", r.stderr[:300].decode("utf-8", "replace"))
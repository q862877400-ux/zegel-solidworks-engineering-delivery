"""查为什么 main() 在测试里返 1 而手动跑返 0。"""
import importlib.util
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
spec = importlib.util.spec_from_file_location("cep", REPO / "scripts" / "check_env_pitfalls.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["cep"] = mod
spec.loader.exec_module(mod)

print("  ROOT                   = %s" % mod.ROOT)
print("  FALSY_ZERO_BASELINE    = %s" % mod.FALSY_ZERO_BASELINE)
print("  基线文件存在           = %s" % mod.FALSY_ZERO_BASELINE.is_file())
bl = mod.load_falsy_zero_baseline()
print("  基线键数               = %d" % len(bl))

buf = io.StringIO()
with redirect_stdout(buf):
    rc = mod.main(["--root", str(mod.ROOT)])
print("  main() 返回            = %d" % rc)
print()
print("  ── main 的输出 ──")
for line in buf.getvalue().splitlines():
    print("    %s" % line)

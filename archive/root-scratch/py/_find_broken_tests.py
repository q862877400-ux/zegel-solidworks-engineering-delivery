import ast
import subprocess
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")
bad = []
for p in sorted((ROOT / "tests").glob("*.py")):
    try:
        ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError as e:
        bad.append((p, e.lineno, (e.text or "").strip()[:80]))
print("  语法坏掉的测试文件: %d" % len(bad))
for p, ln, txt in bad:
    print("     %s L%s: %s" % (p.name, ln, txt))
    #: 用 git 恢复**这一个**文件，然后只用安全形态补
    r = subprocess.run(["git", "checkout", "--", "tests/" + p.name],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(ROOT))
    print("       已 git 恢复: %s" % (r.returncode == 0))

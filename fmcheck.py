import re, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\SKILL.md")
s = p.read_text(encoding="utf-8")
m = re.match(r"^---\n(.*?)\n---\n", s, re.S)
fm = m.group(1) if m else ""
print("=== ① frontmatter 合规检查 ===")
for k in ("name", "description", "disable-model-invocation", "user-invocable", "whenToUse", "when_to_use", "allowed-tools"):
    hit = re.search(r"^%s\s*:" % re.escape(k), fm, re.M)
    print("   %-26s %s" % (k, "有" if hit else "—"))
# 名字 kebab-case?
nm = re.search(r'^name\s*:\s*["\']?([^"\'\n]+)', fm, re.M)
name = nm.group(1).strip() if nm else ""
import re as _re
ok = bool(_re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", name))
print("   name=%r  kebab-case=%s" % (name, "✓" if ok else "✗"))
# description 长度（规范：会话目录上限默认 500）
dm = re.search(r'^description\s*:\s*["\']?(.*)', fm, re.M | re.S)
desc = dm.group(1).split("\n")[0].strip().strip('"\'') if dm else ""
print("   description 长度=%d（上限 500）%s" % (len(desc), "✓" if len(desc)<=500 else "✗ 超长"))
print()
print("=== ② 主 SKILL.md 是否引用 subskills ===")
for i, line in enumerate(s.splitlines(), 1):
    if "subskills/" in line:
        print("   L%-5d %s" % (i, line.strip()[:96]))
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
t = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_names.py").read_text(encoding="utf-8")
print("  check_member_names.py 的规模: %d 行" % t.count("\n"))
print()
print("  ── 它抓哪些形态（找正则/模式定义）──")
for m in re.finditer(r"(?m)^\s*(?:RE|PAT|WRAPPER|_RE\w*|\w*_PATTERN)\w*\s*=.*$", t):
    print("    %s" % m.group(0).strip()[:118])
print()
print("  ── 关键短语在不在 ──")
for kw in ("getattr", "ast.", "get_com_member", "call_com_member", "safe_get_com_member",
           "GetSldWorksObject", "Attribute", "直接"):
    print("    %-24s %s" % (kw, kw in t))
print()
print("  ── 它扫哪些文件 ──")
for m in re.finditer(r"(?m)^.*(glob|rglob|iterdir|walk)\b.*$", t):
    print("    %s" % m.group(0).strip()[:118])

import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
WRAP = re.compile(r"\b(?:get_com_member|_safe_member)\s*\(\s*[^,()]+,\s*[\"']([A-Z]\w+)[\"']")
GUARD = re.compile(r"_checked\s*\(\s*[^,()]+,\s*[^,()]+,\s*[\"']([A-Z]\w+)[\"']")
CALL  = re.compile(r"[.\s]([A-Z]\w+)\s*\(")
LIT   = re.compile(r"[\"']([A-Z]\w{2,})[\"']\s*[,:}]")
SKIP  = re.compile(r"^\s*(#|\"\"\"|''')")
called, catalogued = set(), set()
for pat in ("scripts/*.py", "subskills/**/*.py"):
    for p in sorted(REPO.glob(pat)):
        if p.name == "__init__.py": continue
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if SKIP.match(line): continue
            called |= set(WRAP.findall(line)) | set(GUARD.findall(line)) | set(CALL.findall(line))
            catalogued |= set(LIT.findall(line))
print("  代码里真的调用/点调用的成员名 =", len(called))
print("  登记表里列出的成员名       =", len(catalogued))
print("  只在登记表（未真调用）     =", len(catalogued - called))
sample = sorted(catalogued - called)[:12]
print("  样例:", ", ".join(sample))

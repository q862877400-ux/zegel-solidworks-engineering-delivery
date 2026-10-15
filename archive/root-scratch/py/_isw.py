import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
c = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
m = re.search(r"(?ms)^## ISldWorks\r?\n(.*?)(?=\r?\n## |\z)", c)
lines = [l.strip() for l in m.group(1).splitlines()
         if l.strip() and not re.search(r"\bI[A-Z][a-z]", l) and re.match(r"^\S+\s+\w+\s*\(", l.strip())]
print("ISldWorks 非属性方法 =", len(lines))
groups = {
    "连接/文档": r"Connect|GetFirstDoc|GetDocuments|CloseDoc|ActivateDoc|OpenDoc|NewDocument|ExitApp|GetProcessID|FrameState",
    "用户首选项": r"UserPreference",
    "路径/环境": r"Directory|Path|File|Template|Revision|Build|Version|AddIns|CommandInProgress|Idle|ActiveDoc",
    "选择/拾取": r"Select|Pick|Selection",
    "错误/日志": r"Error|Warning|Message|SetErrorNotification|GetLastCommand",
    "单位/语言": r"Unit|Language|Locale|Configure",
}
seen = set()
for g, pat in groups.items():
    hits = [l for l in lines if re.search(pat, l, re.I)]
    for h in hits: seen.add(h)
    print("\n### %s (%d)" % (g, len(hits)))
    for l in hits[:12]:
        print("   ", l)
rest = [l for l in lines if l not in seen]
print("\n### 其余 %d 个（不在上面六类）" % len(rest))
for l in rest[:10]:
    print("   ", l)

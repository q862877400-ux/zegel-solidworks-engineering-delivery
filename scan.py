import sys, re, json
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
MIT = ["codestack","CSharpAndSolidWorks","solidworks-api","solidworks-auto-modeling",
       "Solidworks-MCP","solidworks-skills","sw-api-skill","sw-ai-bridge",
       "solidworks-com-automation-skill"]
# 官方清单里已知的成员（用来判断「这个调用是不是新东西」）
official = set()
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\S+\s+(\w+)\s*\(", l.strip())
        if m: official.add(m.group(1))
print("官方成员池 %d 个" % len(official))
# 实操写法的特征：报错信息、注意事项、"注意"、"坑"、Nothing/Empty、TypeError
PAT = re.compile(r"(Nothing\b|Empty\b|VARIANT\(|DumbDispatch|TypeError|0x800|"
                 r"trick|workaround|gotcha|注意|坑|必须|失败|报错|无法|不要|"
                 r"为空时|不可用)", re.I)
hits = {}
for repo in MIT:
    d = R / repo
    if not d.is_dir(): continue
    n = 0
    for f in d.rglob("*"):
        if f.suffix.lower() not in (".py", ".cs", ".vba", ".bas", ".js", ".ts", ".md"): continue
        if ".git" in f.parts or "node_modules" in f.parts: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        if not PAT.search(txt): continue
        for l in txt.splitlines():
            if PAT.search(l) and 12 < len(l.strip()) < 160:
                n += 1
                if n <= 40:
                    hits.setdefault(repo, []).append(
                        (f.relative_to(d).as_posix(), l.strip()))
print()
print("=== 各仓库命中的实操线索条数 ===")
for repo, v in hits.items():
    print("  %-42s %d 条" % (repo, len(v)))
import pickle
pickle.dump(hits, open(r"D:\AI\SW\_hits.pkl","wb"))
import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# ① 官方 API 里真正管「关弹窗」的成员
KEY = re.compile(r"(CommandInProgress|SetErrorNotification|GetErrorNotification|"
                 r"EnableFileMenu|FrameState|IsCommandInProgress|"
                 r"SetUserPreferenceToggle|GetUserPreferenceToggle|"
                 r"SendMsgToUser)", re.I)
found = {}
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    cur = None
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "): cur = l[3:].strip()
        elif cur and l.strip():
            m = re.match(r"^\s*(\S+)\s+(\w+)\s*\((.*)\)\s*$", l.strip())
            if m and KEY.search(m.group(2)):
                ps = [a.strip() for a in m.group(3).split(",") if a.strip()]
                real = [a for a in ps if not a.endswith("&")]
                found.setdefault(cur, []).append(
                    (m.group(2), len(ps), len(real), m.group(3)[:60]))
print("=== ① 反射里管「关弹窗 / 静默执行」的官方成员 ===")
for iface, items in sorted(found.items()):
    print("  %s" % iface)
    for n, tot, real, ps in sorted(set(items))[:8]:
        print("     %-32s 整行%2d / 非by-ref%2d  (%s)" % (n, tot, real, ps))
print()
# ② 仓库里有没有讲怎么点掉弹窗
R = Path(r"C:\swprojects")
PAT = re.compile(r"(CommandInProgress|SetErrorNotification|swInputDimValOnCreate|"
                 r"silent|Silent|无人值守|headless|不弹窗|禁止弹窗)", re.I)
print("=== ② 仓库里讲「怎么不弹窗 / 静默跑」的 ===")
n = 0
for repo in ("codestack","solidworks-skills","sw-ai-bridge","SolidworksMCP-TS",
             "sw-api-skill","solidworks-auto-modeling","Solidworks-MCP",
             "solidworks-com-automation-skill","solidworks-api"):
    d = R/repo
    if not d.is_dir(): continue
    for f in d.rglob("*"):
        if f.suffix.lower() not in (".md",".py",".cs",".vba"): continue
        if ".git" in f.parts or "node_modules" in f.parts: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        for i,l in enumerate(txt.splitlines()):
            l=l.strip()
            if PAT.search(l) and 18 < len(l) < 200:
                print("  [%s] %s" % (repo, f.relative_to(d).as_posix()[:56]))
                print("     " + l[:180]); n+=1
                if n>=10: break
        if n>=10: break
    if n>=10: break
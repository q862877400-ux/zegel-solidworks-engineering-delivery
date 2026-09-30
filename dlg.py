import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
R = Path(r"C:\swprojects")
# ① 弹窗怎么关/怎么点 —— 官方 API 里对应的成员
DIALOG = re.compile(r"(GetMessageBar|MessageBar|关闭.*(对话框|弹窗|窗口)|"
                    r"dismiss|Dismiss|suppress|Suppress|SetErrorNotification|"
                    r"swDialog|swMessageBox|CloseDialog|GetDialog)", re.I)
print("=== ① 弹窗 / 对话框 / 消息栏 ===")
n=0
for repo in ("codestack","solidworks-api","solidworks-skills","SolidworksMCP-TS",
             "sw-ai-bridge","solidworks-auto-modeling","Solidworks-MCP","sw-api-skill"):
    d = R/repo
    if not d.is_dir(): continue
    for f in d.rglob("*"):
        if f.suffix.lower() not in (".md",".py",".cs",".vba"): continue
        if ".git" in f.parts or "node_modules" in f.parts: continue
        try: txt = f.read_text(encoding="utf-8", errors="replace")
        except Exception: continue
        for i,l in enumerate(txt.splitlines()):
            l=l.strip()
            if DIALOG.search(l) and 16 < len(l) < 180:
                print("  [%s] %s" % (repo, f.relative_to(d).as_posix()[:58]))
                print("     " + l[:160]); n+=1
                if n>=14: break
        if n>=14: break
    if n>=14: break
print()
# ② 反射里跟「弹窗/错误/诊断」相关的官方成员
SW = Path(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt").read_text(encoding="utf-8", errors="replace")
print("=== ② 反射里相关的官方成员（可直接调）===")
cur=None; seen=set()
for l in SW.splitlines():
    if l.startswith("## "): cur=l[3:].strip()
    elif cur and l.strip():
        m = re.match(r"^\s*\S+\s+(\w*(?:Message|Error|Dialog|Warning|WhatsWrong|"
                     r"Rebuild|Alert|Notify|Status)\w*)\s*\(", l.strip())
        if m and m.group(1) not in seen:
            seen.add(m.group(1))
for x in sorted(seen)[:26]:
    print("    " + x)
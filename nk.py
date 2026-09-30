import sys, re
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# ① 模块里声称存在的成员，逐个回反射核
SRC = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_automation_knowledge.py").read_text(encoding="utf-8")
claimed = set(re.findall(r'get_com_member\([^,]+,\s*"(\w+)"', SRC))
print("模块里直接调用的成员 %d 个: %s" % (len(claimed), ", ".join(sorted(claimed))))
off = set()
for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
    cur=None
    for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if l.startswith("## "): cur=l[3:].strip()
        elif cur and l.strip():
            m = re.match(r"^\s*(\S+)\s+(\w+)\s*\(", l.strip())
            if m: off.add(m.group(2))
bad = sorted(claimed - off)
print()
print("反射里查不到的: %s" % (bad if bad else "无 —— 全部真实存在"))
# ② arity 是否对
print()
for mem, claim in (("CommandInProgress", "set 1 参 / get 0 参"),
                   ("SetUserPreferenceToggle", "ISldWorks 2 参"),
                   ("GetUserPreferenceToggle", "ISldWorks 1 参"),
                   ("SendMsgToUser2", "3 参"),
                   ("GetErrorNotification", "0 参"),
                   ("SetErrorNotification", "1 参")):
    hit = False
    for p in Path(r"D:\AI\SW\_raw").rglob("iface_*.txt"):
        cur=None
        for l in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if l.startswith("## "): cur=l[3:].strip()
            elif cur=="ISldWorks" and l.strip():
                m = re.match(r"^\s*(\S+)\s+%s\s*\((.*)\)\s*$" % re.escape(mem), l.strip())
                if m:
                    ps=[a.strip() for a in m.group(2).split(",") if a.strip()]
                    print("  ISldWorks.%-28s 整行%2d / 非by-ref%2d   (模块称: %s)" % (mem, len(ps), len([a for a in ps if not a.endswith("&")]), claim))
                    hit=True; break
        if hit: break
    if not hit: print("  ISldWorks.%-28s ** ISldWorks 上没有 **" % mem)
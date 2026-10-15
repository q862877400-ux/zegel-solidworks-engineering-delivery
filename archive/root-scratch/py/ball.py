import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect()
S.cache_drop()
print("locate('返回') -> %s" % (L.rect_of(w, "返回"),))
print("所有「返回」:")
for c in L.locate_all(w, "返回"):
    r=c.rectangle()
    print("   %-6s (%d,%d,%d,%d)" % (c.element_info.control_type[:5], r.left,r.top,r.right,r.bottom))
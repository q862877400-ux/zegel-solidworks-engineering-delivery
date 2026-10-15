import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
h, w = L.connect()
cr = L.container_rect(w)
print("容器:", cr)
print()
print("★ 结果卡里的型号代码能否按名字读到：")
for code in ("HGH20HAZC","HGW15CCZOC","EGH25SAZOC","HGH20HAZC"):
    hit=None
    for c in L._controls(w):
        try:
            if (c.window_text() or "").strip()==code and L._overlaps(c.rectangle(),cr):
                hit=c; break
        except Exception: continue
    print("   %-12s %s" % (code, ("✓ %s %s" % (hit.element_info.control_type,
          (hit.rectangle().left,hit.rectangle().top,hit.rectangle().right,hit.rectangle().bottom))) if hit else "✗ 读不到"))
print()
print("★ 型号附近还有什么可读的元素（前 30 个非结构文字）：")
SKIP=("swCmdMgr","swCaption","SearchBox","关闭","任务窗格","Task Pane","EM Frame","header",
      "taskPaneConfig","expandCollapse","pin","swInnerFrame","数据同步进度")
n=0
for c in L._controls(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
    except Exception: continue
    if not t or t in SKIP or not L._overlaps(r,cr): continue
    if r.top > cr.top+700: continue
    n+=1
    print("   %-10s %-26s y=%d" % (c.element_info.control_type[:9], t[:24], r.top))
    if n>=28: break
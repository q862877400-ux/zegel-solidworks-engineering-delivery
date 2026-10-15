import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
import win32api, win32con
warnings.filterwarnings("ignore")
def key(vk, p=0.25):
    win32api.keybd_event(vk,0,0,0); time.sleep(0.06)
    win32api.keybd_event(vk,0,win32con.KEYEVENTF_KEYUP,0); time.sleep(p)
h, w = L.connect()
S.ensure_front(h)
allc = S.controls_cached(w); cr = S._container_from(allc)
cb=None; lab=None
for c in allc:
    try:
        t=(c.window_text() or "").strip()
        if t=="滑块类型":
            if c.element_info.control_type=="ComboBox": cb=c
            elif c.element_info.control_type in ("Pane","Text") and c.rectangle().width()>100: lab=c.rectangle()
    except Exception: continue
r = cb.rectangle()
print("combo %s 选项=%s" % ((r.left,r.top,r.right,r.bottom), cb.texts()))
print("label %s" % (lab,))
if lab: S.click((lab.left+lab.right)//2, (lab.top+lab.bottom)//2, 0.4)
cb.click_input(); time.sleep(0.8)
print("展开后模态=%d" % L._modal().modal_report(h)["count"])
key(win32con.VK_DOWN); key(win32con.VK_RETURN, 0.8)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("结果: 滑块类型=%r 进度=%s%%" % (st["combos"].get("滑块类型"), st["pct"]))
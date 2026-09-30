import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
import win32gui, win32process
warnings.filterwarnings("ignore")
h, w = L.connect()
S.ensure_front(h)
allc = S.controls_cached(w)
cb=None
for c in allc:
    try:
        if (c.window_text() or "").strip()=="滑块类型" and c.element_info.control_type=="ComboBox":
            cb=c; break
    except Exception: continue
items = cb.texts()
print("选项: %s" % items)
cb.click_input(); time.sleep(1.0)
pid = win32process.GetWindowThreadProcessId(h)[1]
lb=None
def cbw(hh,_):
    global lb
    if win32gui.IsWindowVisible(hh) and win32gui.GetClassName(hh)=="ComboLBox" \
       and win32process.GetWindowThreadProcessId(hh)[1]==pid:
        lb=win32gui.GetWindowRect(hh)
win32gui.EnumWindows(cbw,None)
print("ComboLBox: %s" % (lb,))
n=len(items); idx=1   # 选第 2 个「短型」
row=(lb[3]-lb[1])/n
x=(lb[0]+lb[2])//2; y=int(lb[1]+row*(idx+0.5))
print("点第%d项「%s」at (%d,%d) 行高%.1f" % (idx, items[idx], x, y, row))
S.click(x,y,1.0)
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
print("结果: 滑块类型=%r 进度=%s%%" % (st["combos"].get("滑块类型"), st["pct"]))
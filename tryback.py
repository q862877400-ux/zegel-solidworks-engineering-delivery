import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_click as K
import win32api, win32con
warnings.filterwarnings("ignore")

def kind():
    S.cache_drop(); h,w = L.connect()
    return S.page_kind(S.read_state(w)), h, w

k0, h, w = kind()
print("初始 %s" % k0)
cands = L.locate_all(w, "返回")
print("候选 %d 个:" % len(cands))
for c in cands:
    r = c.rectangle()
    try: en = c.is_enabled()
    except Exception: en = "?"
    print("   %-6s (%d,%d,%d,%d) enabled=%s" % (c.element_info.control_type[:5], r.left,r.top,r.right,r.bottom, en))
print()
for i, c in enumerate(cands):
    r = c.rectangle()
    cx, cy = (r.left+r.right)//2, (r.top+r.bottom)//2
    print("试 #%d %s @(%d,%d)" % (i, c.element_info.control_type[:5], cx, cy))
    # 方式 A: click_input
    K.click_control(c, 1.2)
    k1, h1, w1 = kind()
    if k1 != k0:
        print("   ✓ click_input 生效: %s -> %s" % (k0, k1)); break
    # 方式 B: 坐标点击
    K.click_point(cx, cy, 1.2)
    k2, h2, w2 = kind()
    if k2 != k0:
        print("   ✓ 坐标点击生效: %s -> %s" % (k0, k2)); break
    print("   ✗ 无效（仍 %s）" % k2)
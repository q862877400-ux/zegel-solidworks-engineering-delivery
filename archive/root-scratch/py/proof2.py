import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
def P(*a): print(*a, flush=True)
h, w = L.connect(); S.cache_drop()
lab, val = F.model_row(w)
P("型号行标签=%r 值=%r" % (lab.window_text() if lab else None, val.window_text() if val else None))
P("未填=%d" % F.unfilled(w))
P()
P("★ 用『清除』按钮真正取消 L 参数")
row = F.row_for_label(w, "L")
P("  L 行: 值=%r 范围=%s @%s" % (row[1].get_value(), row[3], (row[2].left,row[2].top)))
# 找该行右侧的「清除」Text
cleared = False
for c in S.controls_cached(w):
    try:
        t=(c.window_text() or "").strip(); r=c.rectangle()
        if t == "清除" and abs(r.top - row[2].top) <= 14 and r.left > row[2].right:
            P("  点清除 @(%d,%d)" % (r.left,r.top))
            S.ensure_front(h); S.click((r.left+r.right)//2, (r.top+r.bottom)//2, 1.2)
            cleared = True; break
    except Exception: continue
time.sleep(2.5)
S.cache_drop(); h,w = L.connect()
P("清除后 未填=%d 型号行=%r" % (F.unfilled(w), F.model_line(w)))
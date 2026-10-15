import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
eb, er = SR.search_box(w); sb, sr = SR.search_button(w)
print("① 搜索框(结构): %s" % ((er.left,er.top,er.right,er.bottom) if er else None,))
print("② 搜索按钮(名字): %s" % ((sr.left,sr.top,sr.right,sr.bottom) if sr else None,))
print("③ 结果卡(结构): %s" % SR.result_cards(w)[:3])
print()
print("④ 搜 EGH25SAZ0C 并定位结果卡（**零坐标阈值**）")
SR.search(h, w, "EGH25SAZ0C")
for i in range(8):
    time.sleep(1.5); S.cache_drop(); h,w = L.connect()
    pt = SR.first_result_point(w)
    if pt: print("   ✓ %s" % (pt,)); break
else:
    print("   ✗ 未定位到；卡片列表=%s" % SR.result_cards(w)[:3])
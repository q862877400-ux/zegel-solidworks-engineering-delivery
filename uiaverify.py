import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("① 搜索框(纯UIA): %s" % (SR.search_box(w)[1],))
print("② 搜索按钮(纯UIA): %s" % (SR.search_button(w)[1],))
print()
print("③ 执行搜索 EGH25SAZ0C（纯 UIA，无截图）")
ok = SR.search(h, w, "EGH25SAZ0C")
print("   search() = %s" % ok)
time.sleep(4)
for i in range(8):
    S.cache_drop(); h,w = L.connect()
    pt = SR.first_result_point(w)
    if pt:
        print("   ✓ 结果卡定位（纯UIA） = %s" % (pt,))
        break
    time.sleep(1.5)
else:
    print("   ✗ 未定位到结果卡")
    print("   卡片标签: %s" % SR.result_cards(w)[:3])
import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F, sw_jlcfa_search as SR
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
print("page_kind=%s" % S.page_kind(S.read_state(w)))
print("model_line=%r  unfilled=%d" % (F.model_line(w), F.unfilled(w)))
lab, val = F.model_row(w)
print("model_row: 标签=%r 值=%r" % (lab.window_text() if lab else None, val.window_text() if val else None))
if lab is not None and val is None:
    print()
    print("★ 父 Pane 的子女（看为什么取不到值）:")
    try:
        for k in lab.parent().children():
            r=k.rectangle()
            print("   %-9s %-28r cjk=%s" % (k.element_info.control_type, (k.window_text() or '')[:26], F._has_cjk((k.window_text() or ''))))
    except Exception as e: print("   失败 %s" % str(e)[:50])
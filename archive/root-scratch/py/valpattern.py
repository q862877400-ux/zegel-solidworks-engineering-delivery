import sys, time, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_select as SEL
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
eds = SEL.pending_edits(w)
print("待填: %s" % [(e[0], e[3]) for e in eds])
if not eds: raise SystemExit(0)
name, ctl, r, hint = eds[0]
print("目标「%s」范围 %s  get_value=%r" % (name, hint, ctl.get_value()))
# ★ 用 UIA ValuePattern 直接设值（不碰键盘）
for meth in ("set_edit_text","set_text"):
    try:
        getattr(ctl, meth)("195")
        print("  %s('195') 调用成功" % meth)
        break
    except Exception as e:
        print("  %s 失败: %s" % (meth, str(e)[:60]))
time.sleep(0.8)
print("  设置后 get_value=%r" % (ctl.get_value(),))
S.cache_drop(); h,w = L.connect()
st = S.read_state(w)
eds2 = SEL.pending_edits(w)
print("  重读待填 %s  进度 %s%%" % ([e[0] for e in eds2], st["pct"]))
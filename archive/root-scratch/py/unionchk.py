import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
allc = L._controls(w)
print("并集遍历 节点数 = %d" % len(allc))
print()
print("★ locate('生成预览','Button') 现在能拿到吗：")
c = L.locate(w, "生成预览", "Button")
if c is not None:
    r = c.rectangle()
    print("   ✓ 拿到 Button (%d,%d,%d,%d)" % (r.left,r.top,r.right,r.bottom))
else:
    print("   ✗ 仍然拿不到")
print()
print("★ 所有名为「生成预览」的控件:")
n=0
for cc in allc:
    try:
        if (cc.window_text() or "").strip() == "生成预览":
            r=cc.rectangle(); n+=1
            print("   %-8s (%d,%d,%d,%d)" % (cc.element_info.control_type, r.left,r.top,r.right,r.bottom))
    except Exception: continue
print("   共 %d" % n)
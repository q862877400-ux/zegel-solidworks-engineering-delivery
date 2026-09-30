import sys, re, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_locate as L, sw_jlcfa_steps as S, sw_jlcfa_fill as F
warnings.filterwarnings("ignore")
h, w = L.connect(); S.cache_drop()
# 先关掉可能残留的模态框
n = L._modal().modal_report(h)["count"]
print("残留模态框: %d" % n)
if n: L._modal().close_modals(h, rounds=3); S.cache_drop(); h,w=L.connect()
# ★ 取范围提示的**原始字符**，确认分隔符到底是什么
allc = S.controls_cached(w); cr = S._container_from(allc)
for c in allc:
    try:
        t = (c.window_text() or "").strip()
        if t.startswith("[") and "]" in t and "/" in t:
            print("原始提示 = %r" % t)
            print("  逐字符码位: %s" % [(ch, hex(ord(ch))) for ch in t[:8]])
            break
    except Exception: continue
print()
print("行结构（树）:")
for row in F.param_rows(w):
    print("   %-14s 范围=%-16r lo=%s hi=%s step=%s -> 应填 %s"
          % (row[0][:12], row[3], row[4], row[5], row[6],
             F._fmt_value(row[4], row[5], row[6]) if row[4] is not None else "?"))
import sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
import sw_jlcfa_fill as F
CASES = [
    ("[0.5~20]/0.001",  "0.5"),      # ★ 用户报的那件（齿轮 L 最小 0.5）
    ("[195~1500]/1",    "195"),
    ("[3~200]/1",       "3"),
    ("[55~500]/1",      "55"),
    ("[27~45]/1",       "27"),
    ("[10~15]/1",       "10"),
    ("[0.1~2]/0.01",    "0.1"),
    ("[100~5000]/10",   "100"),
]
bad = 0
for hint, want in CASES:
    rg = F.SEL._parse_hint(hint)
    step = F._parse_step(hint)
    got = F._fmt_value(rg[0], rg[1], step) if rg else "?"
    ok = (got == want)
    if not ok: bad += 1
    print("  %-18s 范围=%-14s step=%-7s -> %-7s %s"
          % (hint, str(rg), str(step), got, "✓" if ok else "✗ 期望 "+want))
# 旧写法对照
print()
print("旧写法对照 str(int(rg[0])):")
for hint, _ in CASES[:1] + CASES[6:7]:
    rg = F.SEL._parse_hint(hint)
    print("  %-18s -> %r  ← 低于下限，插件拒收" % (hint, str(int(rg[0]))))
print()
print("结果: %s" % ("全部正确" if bad == 0 else "%d 个不符" % bad))
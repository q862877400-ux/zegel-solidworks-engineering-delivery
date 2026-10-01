import re, sys
from pathlib import Path
kf = Path(r"D:\AI\SW\docs\known-facts.md").read_text(encoding="utf-8", errors="replace")
BAD = ("到不了", "不可达", "一直返回 False", "返回 False", "全 False", "失败", "Obsolete", "本来就坏", "打不通", "未打通", "查不到")
# 拆事实行：以 "| NNN |" 开头的行 + 其后直到下一个 "| NNN |" 的续行
rows = []
cur = None
for line in kf.splitlines():
    m = re.match(r"\|\s*(\d+)\s*\|", line)
    if m:
        cur = int(m.group(1)); rows.append([cur, []])
    if rows:
        rows[-1][1].append(line)
bad_names = {}
for num, lines in rows:
    body = "\n".join(lines)
    for mark in BAD:
        if mark in body:
            for name in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", body):
                bad_names.setdefault(name, set()).add(num)
            break
print("known-facts 里带'失败类'标记的函数名共 %d 个（跨 %d 条事实）" % (len(bad_names), len(rows)))
# 收集实际挂出去的函数名
import importlib, sys as _s
_s.path.insert(0, "mcp-server")
import register_capabilities as rc
specs = rc.all_specs()
hooked = {}
for s in specs:
    if s.function:
        hooked.setdefault(s.function, []).append((s.name, s.module))
print("注册的函数名共 %d 个" % len(hooked))
print()
print("=== 命中：known-facts 记着坏，却被挂成工具 ===")
n = 0
for fn, facts in sorted(bad_names.items()):
    if fn in hooked:
        n += 1
        for tool, mod in hooked[fn]:
            print("  %-34s (事实 %s)  ->  %s  [%s.%s]" % (fn, sorted(facts), tool, mod, fn))
print("命中数：%d" % n)

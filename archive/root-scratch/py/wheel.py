import subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"C:\swprojects\sw-skill-fork")
new = subprocess.run(["git","-C",str(root),"diff","origin/main","--name-status","--diff-filter=A"],
                     capture_output=True, text=True, encoding="utf-8").stdout
mods = []
for l in new.splitlines():
    p = l.split("\t")[-1]
    if p.startswith("scripts/") and p.endswith(".py"):
        f = root / p
        mods.append((Path(p).stem, len(f.read_text(encoding="utf-8", errors="ignore").splitlines())))
mods.sort(key=lambda x: -x[1])
print("我们新增的 %d 个模块，共 %d 行" % (len(mods), sum(n for _, n in mods)))
print()
# 分类
CAT = {
 "① API 索引（Slacker 没有）": lambda s: s.startswith("sw_api_"),
 "② 门禁/审计（Slacker 没有）": lambda s: s.startswith(("check_","audit_","refresh_")),
 "③ 数据源（Slacker 没有）": lambda s: s.startswith(("sw_jlcfa_index","sw_misumi","sw_toolbox_index")),
 "④ GUI 自动化（Slacker 没有）": lambda s: s.startswith(("sw_jlcfa_locate","sw_jlcfa_cards","sw_jlcfa_click","sw_jlcfa_fill","sw_jlcfa_grid","sw_jlcfa_search","sw_jlcfa_select","sw_jlcfa_steps","sw_jlcfa_batch","sw_jlcfa_audit","sw_jlcfa_gui","sw_gui_","sw_capture")),
 "⑤ 陷阱/知识（Slacker README 有类似）": lambda s: s in ("sw_com_traps","sw_automation_knowledge","sw_selection_tx","sw_selection"),
 "⑥ 能力域封装（Slacker 有重叠）": lambda s: True,
}
groups = {k: [] for k in CAT}
for s, n in mods:
    for k, f in CAT.items():
        if f(s):
            groups[k].append((s, n)); break
for k, items in groups.items():
    tot = sum(n for _, n in items)
    print("%-40s %2d 个 / %5d 行" % (k, len(items), tot))
    if items and len(items) <= 22:
        print("     %s" % ", ".join(s for s, _ in items))
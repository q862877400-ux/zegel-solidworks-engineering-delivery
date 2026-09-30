import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
old = '''                "hit": len(hit), "hit_members": hit[:10],'''
new = '''                "hit": len(hit), "hit_members": hit[:10],
                # ⚑ **列出未命中的成员名** —— 没有它，覆盖表只说「差 N 个」，
                #   没法据此去补。补上之后「还缺什么」是可执行的。
                "missing_members": sorted(
                    m for m in mems
                    if m not in catalogued)[:60],'''
assert old in t, "未匹配 hit 行"
t = t.replace(old, new, 1)
# markdown 表尾也输出一个「未命中明细」小节
old2 = '''    for dom, fams in DOMAIN_FAMILIES.items():'''
assert old2 in t
g.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  [ok] 覆盖表已补 missing_members 字段")
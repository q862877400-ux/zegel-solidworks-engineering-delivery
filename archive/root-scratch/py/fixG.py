import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
# 1) 登记表字面量：允许 add_/remove_ 这类小写开头的成员
old = '''LITERAL = re.compile(r"["']([A-Z]\\w{2,})["']\\s*[,:}]")'''
new = '''# ⚑⚑ 成员名**不都以大写开头** —— 事件委托类上是 ``add_XxxNotify`` /
#   ``remove_XxxNotify``（本机实测 333 + 333 个）。早先用 ``[A-Z]`` 开头，
#   那 666 个**全部漏计**，覆盖表因此虚报 693 个「缺口」——
#   而索引里其实早就抄全了。**指标错了，数据没错。**
LITERAL = re.compile(r"""["']([A-Za-z_]\\w{2,})["']\\s*[,:}]""")'''
assert old in t, "未匹配 LITERAL"
t = t.replace(old, new, 1)
g.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  [ok] LITERAL 已允许小写开头的成员名")
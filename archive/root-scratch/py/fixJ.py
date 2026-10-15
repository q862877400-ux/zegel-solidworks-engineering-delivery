import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
# 在 _reflect_members 里过滤 COM 内部分发口
m = re.search(r"(def _reflect_members\(.*?\n)(.*?)(\n\ndef )", t, re.S)
assert m, "未找到 _reflect_members"
body = m.group(2)
if "INTERNAL" not in body:
    add = '''
    # ⚑⚑ 排除 COM 内部分发口（``IGetXxx`` / ``IUpdateYyy`` / ``ICreateZzz``）。
    #   反射清单把它们和真方法混在一起，本机实测 51 个未命中里绝大多数是这类
    #   （`IGetSubFeatures` / `IUpdateCostForAllBodies` / `ICreateRouteThrough…`）。
    #   它们是**同一能力的内部变体**，索引（build_complete_index.py）已刻意不收，
    #   分母也必须同样不收，否则覆盖表永远差这一截。
    _INTERNAL = re.compile(r"^I[A-Z][a-z]")
    out = [n for n in out if not _INTERNAL.match(n)]'''
    body2 = body + add
    t = t[:m.start(2)] + body2 + t[m.end(2):]
    g.write_text(t, encoding="utf-8")
    import ast; ast.parse(t)
    print("  [ok] _reflect_members 已排除 COM 内部分发口")
else:
    print("  [SKIP] 已有过滤")
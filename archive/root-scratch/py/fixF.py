import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
old = '''    d = SWAPI / iface
    if d.is_dir():
        return sorted(p.stem for p in d.glob("*.md")
                      if p.stem != "_overview" and not INTERNAL.match(p.stem))'''
new = '''    # ⚑⚑⚑ **反射才是成员清单的权威**（AGENTS.md 铁律 4：两套源都要用，
    #   但用途不同）。
    #   `C:\\swapi` 是按**帮助站的文档页**收录的，里面混着两类**非成员**条目：
    #     ① COM 内部分发口 `IGetXxx`      —— 同一能力的内部变体
    #     ② 属性的**返回值描述** `X`/`Y`/`Z`/`ID` —— 形如 `Point get_X()` 的说明
    #   本机实测 `ISketchEllipse`：swapi 21 个 / 反射 方法 11 + 属性 10，
    #   差的 10 个全是 `IGet*`；`ISketchPoint` 差的是 `X`/`Y`/`Z`。
    #   ⇒ 若以 swapi 为分母，覆盖表会**凭空多出 36% 的「缺口」**。
    for path in REFLECT.values():
        members = _reflect_members(path, iface)
        if members:
            return members

    d = SWAPI / iface
    if d.is_dir():
        return sorted(p.stem for p in d.glob("*.md")
                      if p.stem != "_overview" and not INTERNAL.match(p.stem))'''
assert old in t, "未匹配 swapi 分支"
t = t.replace(old, new, 1)
g.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  [ok] family_members 改为「反射优先，swapi 兜底」")
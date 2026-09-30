import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\merge_final.py")
s = p.read_text(encoding="utf-8")
old = '''        lines = []
        for f in fams:
            d = disp.get(f)
            if not d:
                continue
            lines.append("    %r: {" % f)'''
new = '''        # ⚑⚑ DISPID 只能是**补充信息**，不能当成新成员来源 ——
        #   普查里有 COM 内部分发口（`IGetXxx`）与 coclass 重复项，
        #   全收进来会凭空多出几千个「已登记成员」，门禁直接红。
        #   ⇒ 只收**本索引已经有的**成员。
        known: dict[str, set] = {}
        for f in fams:
            blk = re.search(r"^    '%s': \\{\\n(.*?)\\n    \\}," % re.escape(f),
                            src, re.M | re.S)
            if not blk:
                continue
            known[f] = (set(re.findall(r"^        '(\\w+)': \\d+,$", blk.group(1), re.M))
                        | set(re.findall(r"^        '(\\w+)',$", blk.group(1), re.M)))
        lines = []
        for f in fams:
            d = {k: v for k, v in disp.get(f, {}).items() if k in known.get(f, set())}
            if not d:
                continue
            lines.append("    %r: {" % f)'''
assert old in s
p.write_text(s.replace(old, new, 1), encoding="utf-8")
import ast; ast.parse(s.replace(old, new, 1))
print("  DISPID 范围已限定为「索引里已有的成员」")
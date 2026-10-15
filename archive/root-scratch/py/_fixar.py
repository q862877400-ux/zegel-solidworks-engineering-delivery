import re
from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\tests\test_app_and_section_contract.py")
s = p.read_text(encoding="utf-8")
# 反射侧 arity 计数：排除 by-ref 出参（`Xxx&`）—— 本项目 arity 表的口径是「调用方实参」
old = '''        arities.setdefault(cn, []).append(
            len([a for a in hit.group(2).split(",") if a.strip()]))'''
new = '''        # ⚑ 本项目 arity 表的口径是「**调用方要传的实参**」⇒ 排除 by-ref 出参
        #   （反射里的 `String&` / `Int32&` / `Object&`）。口径不一致会误报。
        params = [a.strip() for a in hit.group(2).split(",") if a.strip()]
        arities.setdefault(cn, []).append(
            len([a for a in params if not a.endswith("&")]))'''
assert old in s
p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("  [ok] 测试的反射 arity 口径已改为「不含 by-ref」")

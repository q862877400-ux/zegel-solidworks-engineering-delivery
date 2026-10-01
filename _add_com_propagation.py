import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_direct_member_access.py")
t = P.read_text(encoding="utf-8")

OLD = '''        if not com_objs:
            continue'''
NEW = '''        #: ★★★ **传播**（轮 160 补）：从 COM 对象**属性派生**出来的变量也算 COM 对象。
        #: ⚠ 少了这一步就会**漏检**真实代码里最常见的形态：
        #: `interference = asm_model.InterferenceDetectionManager`
        #: 然后 `interference.GetInterference(0)` ——
        #: ★ 这正是 `159` 那个真缺陷的形态，而**「能响测试」当场把它抓了出来**
        #:   （收窄修掉了假阳性，却引入了一个漏检 —— 靠负例才发现）。
        for _ in range(3):      #: 传三层足够（属性链不会很深）
            grew = False
            for sub in ast.walk(fn):
                if isinstance(sub, ast.Assign) and len(sub.targets) == 1 \\
                        and isinstance(sub.targets[0], ast.Name) \\
                        and isinstance(sub.value, (ast.Attribute, ast.Call)):
                    src_obj = sub.value
                    if isinstance(src_obj, ast.Call):
                        src_obj = src_obj.func
                    base = src_obj
                    while isinstance(base, ast.Attribute):
                        base = base.value
                    if isinstance(base, ast.Name) and base.id in com_objs \\
                            and sub.targets[0].id not in com_objs:
                        com_objs.add(sub.targets[0].id)
                        grew = True
            if not grew:
                break
        if not com_objs:
            continue'''
assert OLD in t, "作用域锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已加「从 COM 对象属性派生」的传播")

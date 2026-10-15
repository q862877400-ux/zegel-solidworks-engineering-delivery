import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_in_context_reference_smoke.py")
t = P.read_text(encoding="utf-8")

OLD = '''        sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        sw_assembly.add_component(asm, paths[1], x=140, y=0, z=0)   #: 挨着但不重叠
        comps = asm.GetComponents(True)
        comps = list(comps) if comps else []
        chk("装配里 2 个组件", len(comps) >= 2, "组件数 %d" % len(comps))
        if len(comps) < 2:
            raise RuntimeError("组件不够，无法继续")'''
NEW = '''        #: ★★ **`sw_assembly.add_component` 本身就返回 `IComponent2`**（它的 docstring 明写）
        #: ⇒ 直接用它，**别去 `asm.GetComponents(True)` 再猜返回的是哪个接口族**
        #: （轮 161 就是这么卡住的：那批对象上**没有 `GetBody2`**）。
        c0 = sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        c1 = sw_assembly.add_component(asm, paths[1], x=140, y=0, z=0)   #: 挨着但不重叠
        comps = [c for c in (c0, c1) if c is not None]
        chk("装配里 2 个组件（**用 add_component 的返回值**）", len(comps) >= 2,
            "组件对象 %d 个" % len(comps))
        if len(comps) < 2:
            raise RuntimeError("组件不够，无法继续")'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改用 add_component 的返回值")

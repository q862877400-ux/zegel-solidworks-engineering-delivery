import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_com_traps.py")
s = p.read_text(encoding="utf-8")
old = '''def byref_long(initial: int = 0) -> Any:
    """造一个 ``VT_BYREF | VT_I4`` 的 VARIANT，供**单个** ByRef Long 出参用。"""'''
new = '''def byref_long(initial: int = 0) -> Any:
    """造一个 ``VT_BYREF | VT_I4`` 的 VARIANT，供**单个** ByRef Long 出参用。

    >>> 本机实跑已确认这条规则是必需的（SolidWorks 2026 SP4.1，撤销铁律 2 后）：
        OpenDoc6(path, type, opt, argstr) —— 4 参（另 2 个是 Int32& 出参）
          只传 4 参            -> -2147352561 DISP_E_PARAMNOTOPTIONAL（参数太少）
          传 6 参、末两个 None -> -2147352571（类型不匹配）
          传 6 参、末两个本函数造的 VARIANT -> 成功打开零件
    由此得到一条索引层面的规则：
        **arity 表排除 by-ref 是「文档口径」，不是「调用口径」**
        —— 调用时必须为每个 by-ref 出参补一个占位实参。
    """'''
assert old in s
p.write_text(s.replace(old, new, 1), encoding="utf-8")
import ast; ast.parse(s.replace(old, new, 1))
print("  已把实跑确认的 byref 规则写进 docstring")
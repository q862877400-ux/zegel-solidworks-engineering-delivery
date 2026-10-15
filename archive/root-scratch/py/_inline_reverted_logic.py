import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\recheck_param_iface_inference.py")
t = P.read_text(encoding="utf-8")

INLINE = '''

def param_ifaces_from_docstring(fn, iface_names: set) -> dict:
    """★ **被回退的那条推断逻辑**（轮 174）—— **本脚本把它内联在这里，只为复算它为何错**。

    ⚠ 它**不在** `check_member_owner_interface.py` 里（那条退路**已回退**，事实 114）。
    ⇒ 本函数是**反面教材的可执行版本**，**不要**把它搬回检查器。
    """
    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}
    blocks = re.split(r"(?m)^\\s*:(?:param|return|returns|raises)\\b", doc)
    for b in blocks:
        m = re.match(r"\\s*(\\w+)\\s*:", b)
        if not m:
            continue
        pname = m.group(1)
        for cand in sorted(iface_names, key=len, reverse=True):
            if re.search(r"(?<![A-Za-z0-9_])" + re.escape(cand) + r"(?![A-Za-z0-9_])", b):
                out[pname] = cand
                break
    #: ⚠ 那条退路：没有 `:param` 时，若**恰好 1 个形参**且 docstring 里接口名**恰好 1 个** ⇒ 采纳
    args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
    if len(args) == 1:
        found = sorted({c for c in iface_names
                        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?![A-Za-z0-9_])", doc)})
        if len(found) == 1:
            out[args[0]] = found[0]
    return out
'''
if "def param_ifaces_from_docstring(" not in t:
    t = t.replace("EXPECT = {", INLINE.strip() + "\n\n\nEXPECT = {", 1)
    #: 把对 C.param_ifaces_from_docstring 的调用改成调本地那个
    t = t.replace("pi = C.param_ifaces_from_docstring(fn, names)",
                  "pi = param_ifaces_from_docstring(fn, names)", 1)
    P.write_text(t, encoding="utf-8")
    ast.parse(t)
    print("  ok 已内联被回退的逻辑 + 改调用")
else:
    print("  已有")

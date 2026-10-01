import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

OLD = '''    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}'''
NEW = '''    doc = ast.get_docstring(fn) or ""
    if not doc:
        return {}
    out: dict = {}
    #: ★★ 2026-10-01（轮 174）：**没有 `:param` 段时**的保守退路 ——
    #: ⚠ 本仓库有些 docstring 是**散文**（如 `mold_evidence`），里面**提了接口名**却没有 `:param`
    #: ⇒ 那时若 **① 函数恰好 1 个形参** 且 **② docstring 里出现的**反射接口名**恰好 1 个**
    #: ⇒ 采纳它（**两个"恰好 1"** 是这条判据的全部依据 —— **不猜、不兜底**）。
    args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
    if len(args) == 1:
        found = [c for c in sorted(iface_names, key=len, reverse=True)
                 if re.search(r"(?<![A-Za-z0-9_])" + re.escape(c) + r"(?![A-Za-z0-9_])", doc)]
        #: ⚠ 只认**最长**的那一个若它唯一；多个不同接口名 ⇒ **放弃**（不判）
        uniq = sorted({f for f in found})
        if len(uniq) == 1:
            out[args[0]] = uniq[0]
            return out
        return {}'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 保守退路已加（两个「恰好 1」）")

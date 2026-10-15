import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_com_member_helpers.py")
t = P.read_text(encoding="utf-8")

i = t.index("def test_no_mutating_zero_arg_call_still_uses_get_com_member():")
NEW = '''def _reflection_zero_arg_methods() -> set:
    """出厂反射里**有零参重载**的方法名。

    ⚠ 这是**结构**判据（名字在反射里是方法、且参数表为空）——
    ⚠⚠ 第一版我用的是**名字前缀**（`Insert*` / `Select*` / `Load*` …），
    它立刻产出 **5 个假阳性**：`SelectionManager` / `LoadsAndRestraintsManager`
    **是属性**，只是名字撞了前缀（事实 74 那一族的**第五次**）。
    """
    out = set()
    raw = Path(r"D:\\AI\\SW\\_raw")
    if not raw.is_dir():
        return out
    for p in raw.rglob("iface_*.txt"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^[\\w.\\[\\]]+\\s+(\\w+)\\s*\\((.*)\\)\\s*$", line.strip())
            if m and m.group(2).strip() == "":
                out.add(m.group(1))
    return out


def test_no_mutating_zero_arg_call_still_uses_get_com_member():
    """@brief ★★ 「反射里有**零参重载**的方法」**不许**再用 `get_com_member`（名字要表态）。

    ★ 判据与 `tools/audit_get_com_member_semantics.py` **同一套**（结构）：
    调用形态是**零参**、且成员在反射里**有零参重载** ⇒ 那个调用**会真的执行**它
    ⇒ 该用 `call_com_member`（名字即意图）。
    ⚠ **不做**任何名字前缀猜测（那是假阳性来源，见 `_reflection_zero_arg_methods` 的注释）。
    """
    zero_arg = _reflection_zero_arg_methods()
    pat = re.compile(r"(?<![\\w.])get_com_member\\(\\s*[\\w.\\[\\]'\\"]+\\s*,\\s*[\\"'](\\w+)[\\"']\\s*\\)")
    bad = []
    for p in sorted((REPO_ROOT / "scripts").glob("sw_*.py")):
        if p.stem == "sw_connect":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8",
                                            errors="replace").splitlines(), 1):
            if line.strip().startswith("#"):
                continue
            m = pat.search(line)
            if m and m.group(1) in zero_arg:
                bad.append("%s:%d %s" % (p.name, i, m.group(1)))
    assert not bad, ("这些零参调用会在**取**的时候**执行**那个方法，却仍用 `get_com_member`"
                     "（应当用 `call_com_member`）：\\n  " + "\\n  ".join(bad))
'''
P.write_text(t[:i] + NEW, encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 判据已改成结构式（反射零参重载）")

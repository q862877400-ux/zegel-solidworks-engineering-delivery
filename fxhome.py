from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_audit.py")
s = p.read_text(encoding="utf-8")
old = '''    # ① 先无条件回到首页 —— 抽查每件之间**必须**从 HOME 起步，
    #    否则 resume/goto 会拿当前的 SELECT 页去当分类页用。
    got = goto("HOME", "返回", h, w)
    if got is None:'''
new = '''    # ① 先无条件回到首页 —— 抽查每件之间**必须**从 HOME 起步。
    # ⚑⚑「返回」只**退一级**（实测 SELECT --返回--> RESULT，不是回首页）：
    #    我此前只点一次就当到家，于是一路拿着 RESULT 页去找分类卡，
    #    12 次全卡在同一处。必须**反复点到达标页为止**。
    for _ in range(8):
        st0 = S.read_state(w)
        if S.page_kind(st0) == "HOME":
            break
        got = goto("HOME", "返回", h, w)
        if got is None:
            break
        h, w = got
    got = (h, w)
    if S.page_kind(S.read_state(w)) != "HOME":'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已修：「返回」改为反复点到 HOME 为止")
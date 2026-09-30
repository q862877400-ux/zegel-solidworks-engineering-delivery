from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_audit.py")
s = p.read_text(encoding="utf-8")
old = '''    # ① 分类页
    if S.page_kind(st) != "CATEGORY":
        r = goto("HOME", "返回", h, w)
        if r is None:
            h, w = L.connect()
        got = goto("CATEGORY", cat, h, w)
        if got is None:
            rec["stage"] = "进分类失败"
            return rec
        h, w = got'''
new = '''    # ① 先无条件回到首页 —— 抽查每件之间**必须**从 HOME 起步，
    #    否则 resume/goto 会拿当前的 SELECT 页去当分类页用。
    got = goto("HOME", "返回", h, w)
    if got is None:
        rec["stage"] = "回首页失败"
        S.evidence("FAIL_home_%s" % code, h, w, st, note="回首页失败")
        return rec
    h, w = got
    rec["stage"] = "HOME"
    S.log("      已回首页")

    # ② 分类页
    got = goto("CATEGORY", cat, h, w)
    if got is None:
        rec["stage"] = "进分类失败(%s)" % cat
        S.evidence("FAIL_cat_%s" % code, h, w, S.read_state(w), note=rec["stage"])
        return rec
    h, w = got'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已修：每件先无条件回首页")
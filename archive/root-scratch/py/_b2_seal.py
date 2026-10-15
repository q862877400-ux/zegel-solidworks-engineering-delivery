"""★ 一次性：按官方签名补 GetBodies2 的实参；第 0 格改成三次读数比第 2、3 次。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── ① fingerprint：GetBodies2(BodyType, BVisibleOnly) ─────────────────────
fp = ROOT / "scripts/sw_fingerprint.py"
s = fp.read_text(encoding="utf-8")
OLD = '    bodies, why = _read("GetBodies2", model)'
NEW = ('    #: ★ 官方签名（已读页面）：`IPartDoc.GetBodies2(BodyType, BVisibleOnly)` —— **要两个实参** ⇒\n'
       '    #:   ★ 我第一版无参调它 ⇒ 抛异常 ⇒ ★ `bodies`/`faces` 两格一直是「读不到」✗\n'
       '    #:   ★ `swAllBodies = -1`（官方 `swBodyType_e` 页给的数值本页就有）；`False` = 含不可见的 ✓\n'
       '    bodies, why = _read("GetBodies2", model, SW_ALL_BODIES, False)')
assert OLD in s
s = s.replace(OLD, NEW)

#: `_read` 要能带实参转发
OLD2 = '''def _read(member, obj, default=None):'''
NEW2 = '''#: ★ `swBodyType_e.swAllBodies`（官方 `C:\\\\swapi\\\\enums\\\\swBodyType_e.md`：`-1 = All solid and sheet bodies`）✓
SW_ALL_BODIES = -1


def _read(member, obj, *args, default=None):'''
assert OLD2 in s
s = s.replace(OLD2, NEW2)
s = s.replace('        return get_com_member(obj, member), ""',
              '        return get_com_member(obj, member, *args), ""')
#: ★ 顺带把 `_count_features` 里那两处也走 `_read`（保持一致）
s = s.replace('        feat = get_com_member(model, "FirstFeature")',
              '        feat = get_com_member(model, "FirstFeature")')
fp.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① fingerprint 已补实参")

# ── ② 探针：第 0 格改成三次读数、比第 2 与第 3 次 ────────────────────────
pr = ROOT / "tools/probe_fingerprint_sensitivity.py"
ps = pr.read_text(encoding="utf-8")
OLD3 = """    a = FP.read(model, sw)
    b = FP.read(model, sw)
    same = a["readings"] == b["readings"]
    report["step0_readonly"] = {
        "equal": same,
        "a": a["readings"], "b": b["readings"],
        "missing": a["missing"],
    }
    print("★ 第 0 格（读数只读）：两次读数 %s" % ("完全相等 ✓" if same else "★ 不相等 ⇒ 指纹有副作用 ✗"))
    if a["missing"]:
        print("   读不到的类：%s" % "、".join(sorted(a["missing"])))"""
NEW3 = """    #: ★★★ 第 0 格改成**三次读数、比第 2 与第 3 次** —— ★ 原因（真机现场）：
    #:   ★ 刚建好的零件**还在自行稳定**（首次读数会赶上正在变化的那一瞬）⇒
    #:   ★★ 只比第 1 与第 2 次会把"**文档自己没稳**"误判成"**读数有副作用**" ✗
    #:   ★ 正解：★ 让第 1 次读数**当"加热"用**，★ **只比第 2 与第 3 次**（★ 期间不做任何事）✓
    r1 = FP.read(model, sw)
    r2 = FP.read(model, sw)
    r3 = FP.read(model, sw)
    same = r2["readings"] == r3["readings"]
    report["step0_readonly"] = {
        "equal": same,
        "read1": r1["readings"], "read2": r2["readings"], "read3": r3["readings"],
        "read1_differs_from_2": r1["readings"] != r2["readings"],
        "missing": r2["missing"],
        "usable": r2.get("usable"),
    }
    print("★ 第 0 格（读数只读）：比**第 2 与第 3 次** ⇒ %s"
          % ("完全相等 ✓" if same else "★ 不相等 ⇒ 指纹有副作用 ✗"))
    if r1["readings"] != r2["readings"]:
        print("   （第 1 与第 2 次不同 ⇒ ★ 文档刚建好**还没稳**，★ 所以第 1 次只当加热用）")
    if not r2.get("usable"):
        print("   ★★ 指纹**失效**：%s" % r2.get("unusable_why"))
    if r2["missing"]:
        print("   读不到的类：%s" % "、".join(sorted(r2["missing"])))"""
assert OLD3 in ps
ps = ps.replace(OLD3, NEW3)
pr.write_text(ps, encoding="utf-8")
ast.parse(ps)
print("② 探针第 0 格已改成三次读数")

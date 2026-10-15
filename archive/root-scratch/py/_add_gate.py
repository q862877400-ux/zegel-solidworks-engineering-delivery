"""★ 给"环境坑"门禁加第 4 条：`get_com_member(...)` 里误传 `default=`（★ 真机踩过，后果严重）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\scripts\check_env_pitfalls.py")
s = p.read_text(encoding="utf-8")

FUNC = '''def find_get_com_member_default(path: Path) -> list:
    """★ 找 `get_com_member(obj, attr, default=...)` —— ★ 这是个**静默致哑**的坑（真机踩过）✓

    ★★★ 2026-10-06 现场：★ 本仓的签名是 `get_com_member(obj, attr_name, *args)` ——
      ★ **没有 `default=` 这个关键字** ⇒ ★ 传 `default=None` 会被当成**位置实参** ⇒
      ★★ 变成「**用 `None` 去调那个成员**」⇒ 成员抛异常 ⇒ 外层拿到的全是 `None` ✓
    ★★ 它为什么特别坏：★ 读出全 `None` **不会报错** ⇒ ★ 上层把「读不到」当成「没变 / 没有」⇒
      ★ 于是 **B5 的门禁曾整整一轮"瞎着放行"**（SolidWorks 明明开着文档，而它读到 0 个）✗
    ★ 正解：★ 直接 `get_com_member(obj, attr)` —— ★ 该函数**本来就**会"先无参调一次、
      失败了再把成员本身返回" ⇒ ★ 属性和方法**都能读**（★ 真机实测：`GetDocumentCount` 是**属性**）✓
    """
    hits = []
    for ln, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if "get_com_member(" not in line or "default=" not in line:
            continue
        #: ★ 按**括号配对**切出整段调用（★ 事实 58 的教训：不能按第一个 `)` 截）✓
        idx = line.find("get_com_member(")
        while idx != -1:
            seg = balanced_call(line, idx)
            if "default=" in seg:
                hits.append((ln, seg.strip()[:120]))
            idx = line.find("get_com_member(", idx + 1)
    return hits


'''
anchor = "def main(argv=None) -> int:"
assert anchor in s
s = s.replace(anchor, FUNC + anchor, 1)

OLD = """    enc_bad, drv_bad = [], []
    for f in files:
        for ln, seg in find_missing_encoding(f):
            enc_bad.append((f.relative_to(root), ln, seg))
        for ln, raw in find_drive_only_root(f):
            drv_bad.append((f.relative_to(root), ln, raw))"""
NEW = """    enc_bad, drv_bad, gcm_bad = [], [], []
    for f in files:
        for ln, seg in find_missing_encoding(f):
            enc_bad.append((f.relative_to(root), ln, seg))
        for ln, raw in find_drive_only_root(f):
            drv_bad.append((f.relative_to(root), ln, raw))
        for ln, seg in find_get_com_member_default(f):
            gcm_bad.append((f.relative_to(root), ln, seg))"""
assert OLD in s
s = s.replace(OLD, NEW)

OLD2 = """    print("环境坑静态检查 · 扫 %d 个 .py" % len(files))"""
NEW2 = """    print("环境坑静态检查 · 扫 %d 个 .py" % len(files))
    print()
    print("④ `get_com_member(...)` 里误传 `default=`（★ 会被当位置实参 ⇒ **读出全是 None 而不报错**）")
    if gcm_bad:
        print("   [FAIL] %d 处：" % len(gcm_bad))
        for f, ln, seg in gcm_bad[:20]:
            print("     %s:%d  %s" % (f, ln, seg))
    else:
        print("   [PASS] 0 处")"""
assert OLD2 in s
s = s.replace(OLD2, NEW2, 1)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("门禁第 4 条已加")

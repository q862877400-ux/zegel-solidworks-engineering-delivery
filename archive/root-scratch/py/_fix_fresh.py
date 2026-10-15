"""★ 一次性：每一类标定**各用一个新零件**（★ 修"顺序依赖"这个更根本的设计错）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\probe_fingerprint_sensitivity.py")
s = p.read_text(encoding="utf-8")

OLD = """        before = FP.read(model, sw)
        ok, note = act(sw, model, writer, cls)"""
NEW = """        #: ★★★ 2026-10-06 **真机暴露的更根本的设计错**：★ 我原来把九类**在同一个文档上顺序标定**
        #:   ⇒ ★★ 前面的类改过文档之后，**后面的类就"没得变了"** —— 现场：
        #:     · `features` 的前置把文档弄脏 ⇒ ★ 轮到 `dirty` 时它**已经是脏的** ⇒ 记 `not_detected` ✗
        #:     · `features` 用掉了 `Sketch1` ⇒ ★ 轮到 `bodies`/`faces` 时 `extrude` 没东西可拉 ⇒ 也没动 ✗
        #:   ★ 这两条**都不是**"读数瞎" —— ★ 是**我的标定顺序污染了后面的样本** ✓
        #:   ⇒ ★★ 修法：★ **每一类各用一个新零件**（★ 前置也在新零件上重建）✓
        fresh = _new_part(sw)
        if fresh is None:
            report["classes"][cls] = {"verdict": "untested", "why": "★ 建不了新零件"}
            print("   %-10s ⇒ ★ untested（建不了新零件）" % cls)
            continue
        model = fresh
        before = FP.read(model, sw)
        ok, note = act(sw, model, writer, cls)"""
assert OLD in s, "标定块没匹配上"
s = s.replace(OLD, NEW)

#: ★ 补一个建新零件的小助手（★ 用本仓能力层的公开函数 —— ★ 它只是"造个空文档"，不是被测的写操作）
HELPER = '''def _new_part(sw):
    """★ 建一个**新的空零件**（★ 每一类标定都从干净状态出发）✓

    ⚠ 说明：★ 这里用的是**能力层**的建文档函数 —— ★ 它**不是被测的写操作**，
      ★ 只是**搭舞台**；★ 被测的写操作一律按 `ToolSpec` 契约调 ✓
    """
    import sw_connect
    try:
        return sw_connect.new_document(sw, "part")
    except Exception:                                                   # noqa: BLE001
        return None


'''
s = s.replace("def act(sw, model, name, cls=\"\"):", HELPER + "def act(sw, model, name, cls=\"\"):")

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("每一类改用新零件")

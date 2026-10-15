"""★ 一次性：机械初推 `needs`（编辑态/实体）—— ★ 只追加，不做区域替换。"""
from pathlib import Path

# ── ① effect_rules：追加 derive_needs（★ 纯追加 ✓）────────────────────
p = Path(r"D:\AI\SW\mcp-server\effect_rules.py")
s = p.read_text(encoding="utf-8")
assert "def derive_needs(" not in s, "★ 已经有了"
ADD = '''

#: ★★★ **`needs` 的机械初推规则**（★ 规格 210 · B3 的第三次拆解产物）。
#:   ★★ 起因（真机）：★ 存活普查里那几条 `sketch_*` 报
#:     `没有活动草图` / `不在草图编辑态`，★ 而 `part_bounding_box` 报 `零件里可能没有实体` ✗
#:   ⇒ ★★ 它们要的**不是"宿主对象"**，★ 而是**宿主处于某种状态** ——
#:     ★ **编辑态（草图中）** 或 ★ **有实体** ✓
#:   ★ 判据：★ 从**工具源码（含被调函数）里的报错话与成员名**反推 ——
#:     ★ 读的是**工具自己写的检查**，★ 不是我猜的 ✓
#:   ★★ 为什么值得推：★ 推出来之后，★ 普查就能**先把状态推到位**再调它们 ✓
#:   ★⚠ 限度：★ 只认**文本里出现的说法**；★ 认不出 ⇒ **空元组**（★ 不许瞎猜）✓
_NEEDS_MARKERS = (
    ("edit:sketch", ("没有活动草图", "不在草图编辑态", "ActiveSketch", "GetActiveSketch",
                     "ActiveSketch 为 None")),
    ("body", ("没有实体", "零件里可能没有实体", "GetBodies2(0", "GetBodies2(-1")),
    ("selection", ("__current_selection__", "必须已选中", "没有选中")),
)


def derive_needs(source: str) -> tuple:
    """★ 从**工具源码**推它需要宿主**处于什么状态**；★ 认不出 ⇒ `()`（★ 不许瞎猜）✓"""
    text = str(source or "")
    out = []
    for token, marks in _NEEDS_MARKERS:
        if any(m in text for m in marks):
            out.append(token)
    return tuple(out)
'''
p.write_text(s.rstrip() + ADD + "\n", encoding="utf-8")
import ast
ast.parse(p.read_text(encoding="utf-8"))
print("① effect_rules 已追加 derive_needs")

# ── ② 生成器：追加 needs 字段（★ 只插一行，不动别的 ✓）────────────────
g = Path(r"D:\AI\SW\tools\gen_effect_declarations.py")
gs = g.read_text(encoding="utf-8")
gs = gs.replace("from effect_rules import (STATE_CLASSES, classify_members, derive_doc_type,\n"
                "                          derive_requires, load_kind_index)",
                "from effect_rules import (STATE_CLASSES, classify_members, derive_doc_type,\n"
                "                          derive_needs, derive_requires, load_kind_index)")
old = '            "doc_type": derive_doc_type(_src_deep(fn, mod)),'
assert old in gs, "★ doc_type 那一行没找到"
gs = gs.replace(old, old + '\n'
                '            #: ★★ `needs` —— ★ 宿主要处于什么**状态**（★ 编辑态/实体/选区）✓\n'
                '            "needs": list(derive_needs(_src_deep(fn, mod))),', 1)
g.write_text(gs, encoding="utf-8")
ast.parse(gs)
print("② 生成器已插 needs 字段")

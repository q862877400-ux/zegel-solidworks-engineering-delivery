"""★ 一次性：机械初推 doc_type（★ 从工具源码里的"文档类型检查"反推）。"""
from pathlib import Path

# ── ① effect_rules：加 doc_type 的推导 ───────────────────────────────────
p = Path(r"D:\AI\SW\mcp-server\effect_rules.py")
s = p.read_text(encoding="utf-8")
ADD = '''

#: ★★★ **`doc_type` 的机械初推规则**（★ 规格 210 · B3 的第二次拆解产物）。
#:   ★★ 起因（真机）：★ 存活普查里 **7 条 `drawing_*`** 报
#:     `当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 …）` ✗
#:     ⇒ ★★ 而它们的 `inject` 声明是 **`model`** —— ★ `inject` **没表达"文档类型"这一维** ✓
#:   ★ 判据：★ **从工具源码里"文档类型检查"的那句话反推**（★ 这是**机械的**，
#:     ★ 因为它读的是**工具自己写的检查**，★ 不是我猜的）✓
#:   ★★ 为什么值得推：★ 推出来之后，★ 普查就能**建对类型的文档**给它们，
#:     ★ 而 B4 的预检也能**提前**报 `wrong_doc_type`（★ 而不是等工具内部抛）✓
#:   ★⚠ 限度：★ 只认**文本里出现的那几种说法**；★ 认不出 ⇒ `None`（★ 不许瞎猜）✓
_DOC_TYPE_MARKERS = (
    ("drawing", ("不是工程图", "swDocDRAWING", "swDocDRAWING", "GetType()=3", "GetType() = 3")),
    ("assembly", ("不是装配体", "swDocASSEMBLY", "GetType()=2", "GetType() = 2")),
    ("part", ("不是零件", "swDocPART", "GetType()=1", "GetType() = 1")),
)


def derive_doc_type(source: str) -> Optional[str]:
    """★ 从**工具源码**推它要哪种文档；★ 认不出 ⇒ `None`（★ 不许瞎猜）✓

    ★ 判序：★ 先看"不是 X"这类**直白说法**，★ 再看枚举名 —— ★ 两者都是**工具自己写的** ✓
    """
    text = str(source or "")
    for kind, marks in _DOC_TYPE_MARKERS:
        if any(m in text for m in marks):
            return kind
    return None
'''
s = s.rstrip() + ADD
if "Optional" not in s.split("\n\n")[0] and "from typing import" not in s:
    #: ★ 需要 `Optional` ⇒ 确保有导入 ✓
    s = s.replace("from __future__ import annotations",
                  "from __future__ import annotations\n\nfrom typing import Optional", 1)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① effect_rules 已加 derive_doc_type")

# ── ② 生成器：把 doc_type 写进表 ─────────────────────────────────────────
g = Path(r"D:\AI\SW\tools\gen_effect_declarations.py")
gs = g.read_text(encoding="utf-8")
gs = gs.replace("from effect_rules import (STATE_CLASSES, classify_members, derive_requires,\n                          load_kind_index)",
                "from effect_rules import (STATE_CLASSES, classify_members, derive_doc_type,\n"
                "                          derive_requires, load_kind_index)")
if "derive_doc_type" not in gs:
    gs = gs.replace("import tool_registry as _tr", "import tool_registry as _tr")
lines = gs.splitlines()
out = []
for ln in lines:
    out.append(ln)
    if ln.strip() == '"requires": derive_requires(_inj),':
        out.append('            #: ★★ `doc_type` —— ★ 从**工具源码里的类型检查**机械初推 ✓')
        out.append('            "doc_type": derive_doc_type(_src_of(fn)),')
gs = "\n".join(out) + "\n"
if "_src_of" not in gs:
    gs = gs.replace("def main()", '''def _src_of(fn) -> str:
    """★ 取函数的**源码文本**（★ `doc_type` 从它里面反推）✓"""
    try:
        import inspect
        return inspect.getsource(fn)
    except Exception:                                                   # noqa: BLE001
        return ""


def main()''', 1)
g.write_text(gs, encoding="utf-8")
ast.parse(gs)
print("② 生成器已写 doc_type")

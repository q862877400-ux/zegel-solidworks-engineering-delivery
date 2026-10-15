"""★ 一次性：指纹永远读在**文档**上（★ 不是读在宿主对象上 —— 真机查出的 sweep bug）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

# ── ① build_host 连"文档"一起回 ─────────────────────────────────────────
s = s.replace('''    name = str(inject_name or "")
    if name in ("", "none"):
        return {"sw": sw}, ""''',
'''    name = str(inject_name or "")
    #: ★★★ 2026-10-06 **真机查出的 sweep bug**：★ 我把**视图/应用对象当文档**去抓指纹 ⇒
    #:   ★★ 六格全读不到（`selection`/`edit_mode`/`dirty`/`features`/`config`/`rebuild`）✗
    #:   ★ 真机证据：★ `empty` 组里 **13 行**各 6 格未判定（= 78），★ 而 **13 正好等于**
    #:     那些"宿主不是文档"的行数（`view` 3 + `sw` 3 + `sw_app` 3 + `manager` 2 + `sldworks` 1 + `none` 1）✓
    #:   ⇒ ★ 正解：★ **指纹永远读在"文档"上** ⇒ ★ `build_host` 把文档一起回，★ 用 `_doc` 键带走 ✓
    if name in ("", "none"):
        return {"sw": sw}, ""''')

s = s.replace('''    if name in ("sldworks", "sw_app", "sw", "manager", "defaults", "options", "sw_app"):
        return {name: sw, "sw": sw}, ""''',
'''    if name in ("sldworks", "sw_app", "sw", "manager", "defaults", "options"):
        #: ★ 应用对象类：★ 宿主是 `sw` 本身，★ **但指纹要读在活动文档上** ✓
        try:
            doc = sw.ActiveDoc
        except Exception:                                               # noqa: BLE001
            doc = None
        return {name: sw, "sw": sw, "_doc": doc}, ""''')

s = s.replace('''    if kind:
        try:
            return {name: sw_connect.new_document(sw, kind), "sw": sw}, ""''',
'''    if kind:
        try:
            doc = sw_connect.new_document(sw, kind)
            return {name: doc, "sw": sw, "_doc": doc}, ""''')

s = s.replace('''            host = _sc.get_com_member(doc, attr)
            if host is None:
                return {}, "★ 零件建好了，但 `%s` 取不到（★ 返回 None）" % attr
            return {name: host, "sw": sw}, ""''',
'''            host = _sc.get_com_member(doc, attr)
            if host is None:
                return {}, "★ 零件建好了，但 `%s` 取不到（★ 返回 None）" % attr
            #: ★ `selection`/`view` 的宿主**不是文档** ⇒ ★ 但**指纹仍读在文档上** ✓
            return {name: host, "sw": sw, "_doc": doc}, ""''')

# ── ② 抓指纹：一律用 `_doc` ──────────────────────────────────────────────
s = s.replace('            before = FP.read(injects.get(req) or injects.get("sw"), sw)',
              '            #: ★★ 指纹一律读**文档**（★ 见 `build_host` 的说明）✓\n'
              '            _doc = injects.get("_doc")\n'
              '            before = FP.read(_doc, sw) if _doc is not None else {"readings": {}, "usable": False}')
s = s.replace('            after = FP.read(injects.get(req) or injects.get("sw"), sw)',
              '            after = FP.read(_doc, sw) if _doc is not None else {"readings": {}, "usable": False}')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("指纹已改成一律读文档")

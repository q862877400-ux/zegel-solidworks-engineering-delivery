"""★ 一次性：B2 最后三条 —— selection/rebuild 加前置；display 给写操作以便"明写不可见"。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\probe_fingerprint_sensitivity.py")
s = p.read_text(encoding="utf-8")

# ── ① 三条的写操作与前 ───────────────────────────────────────────────────
s = s.replace('    "selection": "solidworks_clear_selection",',
              '    #: ★ 写操作：清空选区 ⇒ ★ 要**先有选区**才清得掉（★ 前置见下）✓\n'
              '    "selection": "solidworks_clear_selection",')
s = s.replace('    "display": "",              # ★ 没有"改显示状态"的现成工具 ⇒ 记 untested',
              '    #: ★ `display` 这一格读的是**显示状态的名字**（配置级）；本仓**没有**"改显示状态"的工具 ⇒\n'
              '    #:   ★ 用一个**视图**写操作去试（★ `set_standard_view`）—— ★ **预期它不会动这一格** ⇒\n'
              '    #:   ★★ 于是我们得到一条**明确的"这一类当前不可见"记录**（★ 比 `untested` 强）✓\n'
              '    "display": "solidworks_set_standard_view",')
s = s.replace('    "solidworks_session_rebuild": {},',
              '    "solidworks_session_rebuild": {},\n'
              '    "solidworks_set_standard_view": {},')

# ── ② 前置链：selection 要"先有体、再选一个实体"；rebuild 要"先有需要重建的改动" ──
OLD = '''WRITER_PRECONDITION = {
    #: ★ 画一个矩形 ⇒ 草图里**有选中对象**（★ 于是 `clear_selection` 才清得掉东西）✓
    "selection": [("solidworks_sketch_start", {}),
                  ("solidworks_sketch_add_rectangle", _RECT)],'''
NEW = '''#: ★ 造一个实体（★ 后续「选实体」与"重建"都要它）✓
_BODY_CHAIN = (("solidworks_sketch_start", {}),
               ("solidworks_sketch_add_rectangle", _RECT),
               ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 10.0}))

#: ★ `select_by_selector` 的 `selector` 支持 `index:<n>`（★ 读该工具的声明描述得知）✓
_SELECT_ONE = ("solidworks_select_by_selector",
               {"selector": "index:0", "kind": "EDGE", "body_index": 0})

WRITER_PRECONDITION = {
    #: ★★ 真机查明：★ **画矩形并不会留下选中** ⇒ 选区仍是 0 ⇒ `clear_selection` 清不掉东西 ✗
    #:   ⇒ ★ 前置改成：★ **先造体 → 再选一个实体**（★ 选区变成 1）⇒ 再清就有得清 ✓
    "selection": list(_BODY_CHAIN) + [_SELECT_ONE],'''
assert OLD in s, "前置表头没匹配上"
s = s.replace(OLD, NEW)
s = s.replace('''    "features": [("solidworks_sketch_start", {}),
                 ("solidworks_sketch_add_rectangle", _RECT)],
    "bodies": [("solidworks_sketch_start", {}),
               ("solidworks_sketch_add_rectangle", _RECT)],
    "faces": [("solidworks_sketch_start", {}),
              ("solidworks_sketch_add_rectangle", _RECT)],
}''',
'''    "features": [("solidworks_sketch_start", {}),
                 ("solidworks_sketch_add_rectangle", _RECT)],
    "bodies": [("solidworks_sketch_start", {}),
               ("solidworks_sketch_add_rectangle", _RECT)],
    "faces": [("solidworks_sketch_start", {}),
              ("solidworks_sketch_add_rectangle", _RECT)],
    #: ★★ 真机查明：★ **新零件本来就是重建好的** ⇒ `session_rebuild` 不改变那个布尔 ✗
    #:   ⇒ ★ 前置改成：★ **先造一个实体的改动**（★ 那会留下「需要重建」）⇒ 再重建就有得变 ✓
    "rebuild": list(_BODY_CHAIN),
}''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("三条已改：selection 加「选实体」前置 · rebuild 加「造体」前置 · display 给视图写操作")

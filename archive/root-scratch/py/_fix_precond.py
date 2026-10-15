"""★ 一次性：给写操作加前置链（★ 让它们"从一个变得了的状态出发"）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\probe_fingerprint_sensitivity.py")
s = p.read_text(encoding="utf-8")

# ── ① 前置链表 ───────────────────────────────────────────────────────────
anchor = "#: ★ 每个写操作要传的形参"
PRECOND = '''#: ★★★ 2026-10-06 **本轮最重要的认识**：★ `not_detected` 大多**不是"读数瞎"**，
#:   而是 ★ **"那个写操作没有真的改变任何东西"** —— ★ 真机返回体坐实了三条：
#:     · `config` ⇒ `{"created": false, "reused": true}`（配置**本来就存在**）
#:     · `rebuild` ⇒ `needs_rebuild_before=0 · after=0`（文档**本来就是重建好的**）
#:     · `selection` ⇒ 选区**本来就是空的**
#:   ⇒ ★★ 正解：★ **给每一类配前置**，★ 让它**从一个「变得了」的状态出发** ✓
#:   ★ 前置也**按契约调**（★ 同一个 `tool_caller`），★ 且**前置失败 ⇒ 该类记 `untested`** ✓
#:   ★★ 这正好与 B3 的「每组只建一次状态」是同一件事 —— ★ 两批在这里**接上**了 ✓
_RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 40.0, "y2_mm": 30.0}
WRITER_PRECONDITION = {
    #: ★ 画一个矩形 ⇒ 草图里**有选中对象**（★ 于是 `clear_selection` 才清得掉东西）✓
    "selection": [("solidworks_sketch_start", {}),
                  ("solidworks_sketch_add_rectangle", _RECT)],
    #: ★ 先建草图、画矩形 ⇒ `extrude_boss` 才有 `Sketch1` 可拉 ✓
    "features": [("solidworks_sketch_start", {}),
                 ("solidworks_sketch_add_rectangle", _RECT)],
    "bodies": [("solidworks_sketch_start", {}),
               ("solidworks_sketch_add_rectangle", _RECT)],
    "faces": [("solidworks_sketch_start", {}),
              ("solidworks_sketch_add_rectangle", _RECT)],
}

#: ★ 每个写操作要传的形参'''
assert anchor in s, "写操作形参表的锚点没找到"
s = s.replace(anchor, PRECOND, 1)

# ── ② act() 先跑前置 ─────────────────────────────────────────────────────
OLD_ACT = '''    import tool_caller
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects={"model": model, "sw": sw}, **params)'''
NEW_ACT = '''    import tool_caller
    inj = {"model": model, "sw": sw}
    #: ★★ 先跑**前置链**（★ 让写操作"从一个变得了的状态出发"）✓
    for step_name, step_params in (WRITER_PRECONDITION.get(cls) or []):
        ok_step, note_step = tool_caller.call(step_name, inject_objects=inj, **step_params)
        if not ok_step:
            return False, "★ 前置 %s 没成：%s" % (step_name, note_step[:90])
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects=inj, **params)'''
assert OLD_ACT in s, "act() 没匹配上"
s = s.replace(OLD_ACT, NEW_ACT)
#: act 需要知道是**哪一类**（前置按类查表）
s = s.replace("def act(sw, model, name):", "def act(sw, model, name, cls=\"\"):")
s = s.replace("ok, note = act(sw, model, writer)", "ok, note = act(sw, model, writer, cls)")

# ── ③ config 用**唯一名字**（★ 别复用已有的）─────────────────────────────
s = s.replace('"solidworks_config_create": {"configuration_name": "标定用配置"},',
              '#: ★★ 用**唯一名字** —— 真机踩过：★ 复用同名 ⇒ `{"created": false, "reused": true}`\n'
              '    #:   ⇒ ★ 写操作"成功"却**什么都没改** ⇒ 被记成 `not_detected`（★ 那是假结论）✗\n'
              '    "solidworks_config_create": {"configuration_name": "MCP_CALIB_%d" % __import__("time").time_ns()},')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("前置链已加；config 改成唯一名")

"""★ 一次性：把 bodies/faces 的"空值"与"读不到"分开（★ 真机查明：空零件就是 None）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\scripts\sw_fingerprint.py")
s = p.read_text(encoding="utf-8")

OLD = """    bodies, why = _read("GetBodies2", model, SW_ALL_BODIES, False)
    if bodies is None:
        put("bodies", None, why or "★ GetBodies2 返回 None（★ 装配体上这个成员不存在）")
        put("faces", None, "★ 体都读不到 ⇒ 面也数不了")"""
NEW = """    bodies, why = _read("GetBodies2", model, SW_ALL_BODIES, False)
    if bodies is None:
        #: ★★★ 2026-10-06 **真机查明（这条很值）**：★ 在**空零件**上 `GetBodies2(-1, False)`
        #:   返回 **`None`** —— ★★ 那**不是"读不到"，是"本来就没有实体"** ✓
        #:   （★ 真机对照：★ 建出一个实体之后同一调用 ⇒ **`tuple(len=1)`** ✓）
        #:   ★★ 而我把两者混成了「读不到」⇒ `bodies`/`faces` 两格**一直 unreadable** ✗
        #:   ⇒ ★ 处置：★ **按 0 计**，★ 但把这条不确定**写进 `notes`**（★ 不假装分得清）✓
        #:   ★ 同族教训（本仓老话）：★「**选不上**」与「**选了也没用**」是两件事 ——
        #:     ★ 这里就是「**没有**」与「**读不到**」被混成了一件 ✓
        notes_add("bodies", "★ GetBodies2 返回 None ⇒ 按「**没有实体**」计 0；"
                            "★ 与「读不到」在此调用形状下**无法区分**（★ 已记此注，不假装）")
        put("bodies", 0)
        put("faces", 0)
        notes_add("faces", "★ 由 bodies=0 推出 0（同上，无法与「读不到」区分）")"""
assert OLD in s, "bodies 块没匹配上"
s = s.replace(OLD, NEW)

#: ★ 加一个 notes 容器与写入助手
OLD2 = """    readings, missing = {}, {}

    def put(cls, value, why=\"\"):"""
NEW2 = """    readings, missing, notes = {}, {}, {}

    def notes_add(cls, text):
        notes.setdefault(cls, []).append(text)

    def put(cls, value, why=\"\"):"""
assert OLD2 in s
s = s.replace(OLD2, NEW2)

s = s.replace("""    return {"readings": readings, "missing": missing, "official": dict(OFFICIAL),""",
              """    return {"readings": readings, "missing": missing, "notes": notes,
            "official": dict(OFFICIAL),""")

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("bodies/faces 已按「没有实体」= 0 计，并把不确定写进 notes")

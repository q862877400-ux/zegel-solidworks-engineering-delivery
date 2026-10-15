"""★ 一次性：修 display 读数（要 Option 实参，且读它里面的 Names 而不是对象本身）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\scripts\sw_fingerprint.py")
s = p.read_text(encoding="utf-8")

OLD = """    ext, why = _read("Extension", model)
    if ext is None:
        put("display", None, "Extension 取不到：%s" % (why or "返回 None"))
    else:
        v, why2 = _read("GetDisplayStateSetting", ext)
        put("display", v, why2 or "★ GetDisplayStateSetting 返回 None")"""

NEW = """    ext, why = _read("Extension", model)
    if ext is None:
        put("display", None, "Extension 取不到：%s" % (why or "返回 None"))
    else:
        #: ★★★ 真机踩过（与 `selection` **同一个坑**）：★ `GetDisplayStateSetting` 是**方法、
        #:   要吃一个 `swDisplayStateOpts_e` 实参** ⇒ ★ 我无参调它 ⇒ 拿到的是
        #:   ★★ **`<bound method ...>`**（★ 再被 `jsonable` 变成字符串）✗
        #:   ★ 官方签名（已读）：`DisplayStateSetting GetDisplayStateSetting(int Option)`；
        #:     ★ `swAllDisplayState = 2`（官方 `swDisplayStateOpts_e` 页给了数值）✓
        #:   ★ 而且要读的是它里面的**标量** —— ★ 返回的是 `IDisplayStateSetting` **对象**，
        #:     ★ 直接存对象又会落回"不可比的字符串" ✗ ⇒ ★ 取它的 `Names` ✓
        setting, why2 = _read("GetDisplayStateSetting", ext, SW_ALL_DISPLAY_STATE)
        if setting is None:
            put("display", None, why2 or "★ GetDisplayStateSetting(2) 返回 None")
        else:
            names, why3 = _read("Names", setting)
            if names is None:
                put("display", None, why3 or "★ IDisplayStateSetting.Names 返回 None")
            else:
                #: ★ 归成一个**可比、稳定**的表示：排序后的名字元组 ✓
                seq = names if isinstance(names, (list, tuple)) else [names]
                put("display", tuple(sorted(str(n) for n in seq if n is not None)))"""
assert OLD in s, "display 块没匹配上"
s = s.replace(OLD, NEW)

s = s.replace('''#: ★ `swBodyType_e.swAllBodies`（官方 `C:\\\\swapi\\\\enums\\\\swBodyType_e.md`：`-1 = All solid and sheet bodies`）✓
SW_ALL_BODIES = -1''',
'''#: ★ `swBodyType_e.swAllBodies`（官方 `C:\\\\swapi\\\\enums\\\\swBodyType_e.md`：`-1 = All solid and sheet bodies`）✓
SW_ALL_BODIES = -1
#: ★ `swDisplayStateOpts_e.swAllDisplayState`（官方同页：`2 = All display states`）✓
SW_ALL_DISPLAY_STATE = 2''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("display 读数已修（补 Option 实参 + 读 Names）")

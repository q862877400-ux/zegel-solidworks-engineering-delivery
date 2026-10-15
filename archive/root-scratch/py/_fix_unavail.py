"""★ 一次性：把"已知不可用"的类单独成桶（★ 不让 display 拖垮每一条判定）。"""
from pathlib import Path

fp = Path(r"D:\AI\SW\scripts\sw_fingerprint.py")
s = fp.read_text(encoding="utf-8")

# ── ① 声明"已知不可用"的类（★ 带依据与错误码）────────────────────────────
anchor = "#: ★ 特征遍历的**上限**"
CONST = '''#: ★★★ **已知不可用**的状态类（★ 有依据、有错误码 —— ★ 不是"还没试"）：
#:   ★ `display`：★ `IModelDocExtension.GetDisplayStateSetting(1|2|3)` **三种 Option 全部**抛
#:     `com_error (-2147417851, '服务器出现意外情况')` ⇒ ★ 与**事实 47**（`AccessSelections`）
#:     **同一个错误族**（服务端故障 / RPC）⇒ ★ 该成员在**本后端**上**不可用** ✓
#:   ★★ 处置：★ 它**不该**把每一条差分都拖成"未判定" ——
#:     那是**把"量具的盲区"当成"被测对象的未知"** ✗（★ 与"选不上当成能力不行"同族）
#:   ⇒ ★ 单独成桶 `unavailable`，★ 并在每条判定里**如实报出"这一次排除了哪几类"** ✓
KNOWN_UNAVAILABLE = {
    "display": "★★ 后端限定：GetDisplayStateSetting 三种 Option 全抛 com_error -2147417851（与事实 47 同族）",
}

#: ★ 特征遍历的**上限**'''
assert anchor in s, "上限注释锚点没找到"
s = s.replace(anchor, CONST, 1)

# ── ② compare_detailed 加 `unavailable` 桶 ───────────────────────────────
OLD = """    changed, unknown, same = [], [], []
    rb, ra = (before or {}).get("readings", {}), (after or {}).get("readings", {})
    for cls in STATE_CLASSES:
        #: ★ 双保险：★ 即便上游没归一，这里也按归一后的值比 ✓
        b, a = jsonable(rb.get(cls)), jsonable(ra.get(cls))
        if b is None or a is None:
            unknown.append({"class": cls, "before": b, "after": a})
        elif b != a:
            changed.append({"class": cls, "before": b, "after": a})
        else:
            same.append(cls)
    return {"changed": changed, "unknown": unknown, "same": same}"""
NEW = """    changed, unknown, same, unavailable = [], [], [], []
    rb, ra = (before or {}).get("readings", {}), (after or {}).get("readings", {})
    for cls in STATE_CLASSES:
        #: ★★ **先分流"已知不可用"** —— ★ 它**不属于"未知"**（★ 前者是量具的盲区、
        #:   后者是被测对象的未知）⇒ ★ 混在一起会让**每一条**都变成"未判定" ✗
        #:   ★（★ 真机踩过：`display` 一直读不到 ⇒ 整个普查 6/6 全 `undecided` ✓）
        if cls in KNOWN_UNAVAILABLE:
            unavailable.append({"class": cls, "why": KNOWN_UNAVAILABLE[cls]})
            continue
        #: ★ 双保险：★ 即便上游没归一，这里也按归一后的值比 ✓
        b, a = jsonable(rb.get(cls)), jsonable(ra.get(cls))
        if b is None or a is None:
            unknown.append({"class": cls, "before": b, "after": a})
        elif b != a:
            changed.append({"class": cls, "before": b, "after": a})
        else:
            same.append(cls)
    return {"changed": changed, "unknown": unknown, "same": same,
            "unavailable": unavailable}"""
assert OLD in s, "compare_detailed 没匹配上"
s = s.replace(OLD, NEW)

# ── ③ compare() 说明同步 ─────────────────────────────────────────────────
s = s.replace('''      ★ 记进 `unknown` 而不是当成"没变" ✗ —— ★ 见 `compare_detailed` ✓
    """''',
'''      ★ 记进 `unknown` 而不是当成"没变" ✗ —— ★ 见 `compare_detailed` ✓
    ★ `KNOWN_UNAVAILABLE` 里的类**单独成桶**（★ 不当"未知"，★ 也不当"没变"）✓
    """''')

fp.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① 已知不可用成常量 ② compare_detailed 加 unavailable 桶")

"""★ 一次性：read() 把读数归一成 JSON 安全标量（★ 修第 0 格的虚警）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\scripts\sw_fingerprint.py")
s = p.read_text(encoding="utf-8")

# ── ① 加归一函数 ─────────────────────────────────────────────────────────
anchor = "def _read(member, obj, *args, default=None):"
helper = '''def jsonable(value):
    """★ 把读数**归一成 JSON 安全标量**（`None` / `bool` / `int` / `float` / `str`）✓

    ★★★ 2026-10-06 真机踩过（★ 它让第 0 格**虚警**了一整轮）：
      ★ 指纹里某些读数是 **COM 对象** ⇒ ★ `dict.__eq__` 对它们的比较**不成立** ⇒
      ★★ 于是"两次读数相等"被判成**不相等** ⇒ ★ 我一度以为**读数有副作用** ✗
      ★ 而逐字段 `%r` 打印**看起来一模一样** ⇒ ★ 靠肉眼看是发现不了的 ✓
    ⇒ ★ 所以**在 read() 里就归一**：★ COM 对象 ⇒ `str()`；★ 其余标量原样 ✓
      ★★ 好处：★ 第 0 格与 B3 的差分都建立在**可比、可序列化**的值上 ✓
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    try:
        return str(value)
    except Exception:                                                   # noqa: BLE001
        return "<unprintable>"


'''
assert anchor in s
s = s.replace(anchor, helper + anchor, 1)

# ── ② put() 里归一 ───────────────────────────────────────────────────────
old_put = """    def put(cls, value, why=""):
        readings[cls] = value
        if value is None:
            missing[cls] = why or "★ 读不到（值就是 None）\""""
new_put = """    def put(cls, value, why=""):
        #: ★★ **在出口归一**（★ 见 `jsonable` 的说明：COM 对象会让比较虚警）✓
        value = jsonable(value)
        readings[cls] = value
        if value is None:
            missing[cls] = why or "★ 读不到（值就是 None）\""""
assert old_put in s, "put() 没匹配上"
s = s.replace(old_put, new_put)

# ── ③ 比较也走归一（★ 双保险）─────────────────────────────────────────────
old_cmp = """    for cls in STATE_CLASSES:
        b, a = rb.get(cls), ra.get(cls)"""
new_cmp = """    for cls in STATE_CLASSES:
        #: ★ 双保险：★ 即便上游没归一，这里也按归一后的值比 ✓
        b, a = jsonable(rb.get(cls)), jsonable(ra.get(cls))"""
assert old_cmp in s
s = s.replace(old_cmp, new_cmp)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("read() 已在出口归一 + 比较双保险")

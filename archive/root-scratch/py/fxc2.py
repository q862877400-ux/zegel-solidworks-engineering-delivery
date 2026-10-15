from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")

# 1) 加控件缓存
cache_doc = '''

# ── 控件缓存（性能）─────────────────────────────────────────────
# ⚑ 实测（本机，2026-09-30）：
#     win.descendants()   9.8 秒 / 202 节点   ← 慢在**递归遍历**
#     win.children()      0.0 秒 / 6 节点
#     拿到控件后读三个属性 0.03 秒
# ⇒ **慢的不是读属性，是每次都重新遍历**。
# ⇒ 缓存**控件对象列表**，只重读 text/rect（0.03s 级）⇒ 快约 100 倍。
# ⚠ 缓存对象**不缓存属性** —— 坐标/文字每次重读，避免用过期矩形点空。
_CACHE: dict[str, Any] = {"win": None, "allc": None, "t": 0.0}
CACHE_TTL = 25.0     # 秒；超过就重新遍历


def controls_cached(w) -> list:
    """拿控件对象列表（带 TTL 缓存）。属性仍每次重读。"""
    now = time.time()
    if _CACHE["win"] is w and _CACHE["allc"] is not None \\
            and now - _CACHE["t"] < CACHE_TTL:
        return _CACHE["allc"]
    allc = L._controls(w)
    _CACHE.update({"win": w, "allc": allc, "t": now})
    log("   (缓存刷新: %d 个控件)" % len(allc))
    return allc


def cache_drop() -> None:
    """动作之后**必须**丢缓存 —— 界面变了，控件对象会失效。"""
    _CACHE.update({"win": None, "allc": None, "t": 0.0})
'''
s = s.replace("\n\n# ── 焦点守卫（用户指正 ②）", cache_doc + "\n\n# ── 焦点守卫（用户指正 ②）", 1)

# 2) read_state 用缓存
s = s.replace("    allc = L._controls(w)                 # ★ 只走一次",
              "    allc = controls_cached(w)             # ★ 缓存控件对象（属性仍重读）")

# 3) run_step 动作后丢缓存
s = s.replace("""        try:
            if act:
                act(h, w)
        except Exception:""",
"""        try:
            if act:
                act(h, w)
        except Exception:""")
s = s.replace("""            try:
                h2, w2 = L.connect()
            except Exception:
                continue
            st = read_state(w2)""",
"""            cache_drop()                    # ★ 界面可能已变，重新遍历
            try:
                h2, w2 = L.connect()
            except Exception:
                continue
            st = read_state(w2)""")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已加控件缓存 (TTL 25s) + 动作后失效")
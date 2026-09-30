from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")

# read_state: 先取控件列表，再从同一份里找容器 —— 只走一遍
a = s.index("def read_state(w)")
b = s.index("def page_kind(")
new = '''def _container_from(allc):
    """从**已取好的**控件列表里找插件容器（面积最大的结构名 Pane）。"""
    best = None
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            if t not in L.CONTAINER_NAMES:
                continue
            r = c.rectangle()
        except Exception:
            continue
        if r.width() < 40 or r.height() < 40:
            continue
        area = r.width() * r.height()
        if best is None or area > best[1]:
            best = (r, area)
    return best[0] if best else None


def read_state(w) -> dict[str, Any]:
    """读当前界面的全部可判定特征。**只读，且只遍历一次**。

    ⚑⚑⚑ 性能（本机实测 2026-09-30）
    ``win.descendants()`` 走 202 个 UIA 节点要 **10~29 秒**。
    此前的写法一次 read_state 走**两遍**（``container_rect`` 自己一遍 +
    ``controls_cached`` 再一遍）⇒ 一步动作要等 90 秒。
    ⇒ 现在**取一次控件列表**，容器和三类特征都从这同一份里算。
    ⇒ 控件**对象**有 TTL 缓存，属性（text/rect）每次重读，避免用过期坐标。
    """
    st: dict[str, Any] = {"container": None, "codes": [], "combos": {},
                          "buttons": {}, "pct": None, "categories": []}
    allc = controls_cached(w)
    if not allc:
        return st
    cr = _container_from(allc)
    st["container"] = cr
    if cr is None:
        return st
    names = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            ct = c.element_info.control_type
        except Exception:
            continue
        if not t or not L._overlaps(r, cr):
            continue
        if ct == "ComboBox":
            try:
                st["combos"][t] = c.selected_text().strip()
            except Exception:
                pass
        elif ct == "Button":
            st["buttons"][t] = (r.left, r.top, r.right, r.bottom)
        names.append(t)
        if t.startswith(C.CODE_PREFIX):
            st["codes"].append(t[len(C.CODE_PREFIX):].strip())
        elif (r.top >= cr.top + 120 and r.bottom <= cr.bottom - 20
              and r.width() >= 40 and r.height() >= 20
              and t not in C.SKIP_NAMES):
            st["categories"].append(t)
    st["codes"].sort()
    st["categories"].sort()
    m = re.search(r"(\\d+)%", " ".join(names))
    if m:
        st["pct"] = int(m.group(1))
    return st


'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("read_state 现在只走一遍")
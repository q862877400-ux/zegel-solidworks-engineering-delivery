from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")
a = s.index("def read_state(w)")
b = s.index("def page_kind(")
new = '''def read_state(w) -> dict[str, Any]:
    """读当前界面的全部可判定特征。**只读，且只遍历一次**。

    ⚑⚑⚑ 性能（本机实测）：``win.descendants()`` 要走 500+ 个 UIA 节点，
       单次约 3-6 秒。此前 ``read_state`` 里 ``_controls`` / ``code_labels``
       / ``category_cards`` **各走一遍** ⇒ **一次读状态遍历 3 遍**，
       一步动作要等 90 秒。
    ⇒ 现在**只遍历一次**，在同一个循环里把三类特征（代码标签 / 分类卡 /
      ComboBox / Button）**全部**收齐。
    """
    cr = L.container_rect(w)
    st: dict[str, Any] = {"container": cr, "codes": [], "combos": {},
                          "buttons": {}, "pct": None, "categories": []}
    if cr is None:
        return st
    allc = L._controls(w)                 # ★ 只走一次
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
              and r.width() >= 40 and r.height() >= 20 and t not in C.SKIP_NAMES):
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
print("read_state 已改为单次遍历")
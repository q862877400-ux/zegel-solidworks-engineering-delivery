from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
s = p.read_text(encoding="utf-8")
old = '''def locate(win, name: str, ctype: str | None = None):
    """★ 第 1 层：按**控件名**取控件对象。找不到返回 None —— 不猜。"""
    for c in _controls(win):
        try:
            if (c.window_text() or "").strip() != name:
                continue
            if ctype and c.element_info.control_type != ctype:
                continue
            r = c.rectangle()
        except Exception:
            continue
        cr = container_rect(win)
        if cr and _overlaps(r, cr):
            return c
    return None'''
new = '''def locate(win, name: str, ctype: str | None = None):
    """★ 第 1 层：按**控件名**取控件对象。找不到返回 None —— 不猜。

    ⚑⚑⚑ 同名多控件（实测「返回」有 5 个，本机 2026-09-30）
    一个名字会同时命中**容器 Pane / 图标 / 真正的链接**。
    取第一个就会点到 568x46 的页脚空壳 ⇒ 「点了没反应」。
    ⇒ 取规则：**可见 + 在插件容器内 + 同名里面积最小**。
    """
    cr = container_rect(win)
    best = None
    for c in _controls(win):
        try:
            if (c.window_text() or "").strip() != name:
                continue
            if ctype and c.element_info.control_type != ctype:
                continue
            r = c.rectangle()
            if r.width() <= 0 or r.height() <= 0:
                continue
            if cr and not _overlaps(r, cr):
                continue
            try:
                if not c.is_visible():
                    continue
            except Exception:
                pass
        except Exception:
            continue
        area = r.width() * r.height()
        if best is None or area < best[0]:
            best = (area, c)
    return best[1] if best else None'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("locate 已改为「可见 + 同名取最小」")
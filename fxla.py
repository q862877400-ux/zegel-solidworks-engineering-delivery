from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_locate.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''    ⚑⚑⚑ 同名多控件（实测「返回」有 5 个，本机 2026-09-30）
    一个名字会同时命中**容器 Pane / 图标 / 真正的链接**。
    取第一个就会点到 568x46 的页脚空壳 ⇒ 「点了没反应」。
    ⇒ 取规则：**可见 + 在插件容器内 + 同名里面积最小**。
    """''',
'''    ⚑⚑⚑ 同名多控件（实测「返回」有 5 个，本机 2026-09-30）
    一个名字会同时命中**容器 Pane / 图标 / 真正的链接**。
    取第一个 ⇒ 点到 568x46 的页脚空壳。
    取面积最小 ⇒ 也错：20x19 的**页脚图标**比 24x30 的**左上角真链接**还小。
    ⚠ **按形状猜哪个才是对的，第三次还是猜错了。**
    ⇒ 正确做法在 ``locate_all()`` + 调用方「**逐个试、用页面变化验收**」。
    本函数只做**确定性**选取：可见 + 在容器内 + **类型为 Text/Button 优先**。
    """''')
s = s.replace('''        area = r.width() * r.height()
        if best is None or area < best[0]:
            best = (area, c)
    return best[1] if best else None''',
'''        # Text/Button 是**可点标签/按钮**；Pane 多半是容器外壳
        rank = (0 if c.element_info.control_type in ("Text", "Button") else 1,
                r.width() * r.height())
        if best is None or rank < best[0]:
            best = (rank, c)
    return best[1] if best else None


def locate_all(win, name: str, ctype: str | None = None):
    """返回所有同名且可见、在插件容器内的控件（**按 y 排序，左上优先**）。

    ⚑ 用法：同名元素有多个且**无法靠形状分辨**时，**逐个试 + 验收**，
      而不是猜哪个对（我连猜三次都错了）。
    """
    cr = container_rect(win)
    out = []
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
        out.append((r.top, r.left, c))
    out.sort()
    return [c for _, _, c in out]''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("locate 改为「Text/Button 优先」，并新增 locate_all")
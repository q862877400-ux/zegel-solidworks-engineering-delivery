from pathlib import Path
p = Path(r"D:\AI\SW\audit_run.py")
s = p.read_text(encoding="utf-8")
s = s.replace("import sw_jlcfa_locate as L",
              "import sw_jlcfa_locate as L\nimport draw_loc as D")
s = s.replace('''def search_box(win):
    """搜索框 = 插件区顶部、横向较宽的无标题 Edit。"""
    cr = L.container_rect(win)
    if not cr:
        return None
    for c in L._controls(win):
        try:
            if c.element_info.control_type != "Edit":
                continue
            r = c.rectangle()
        except Exception:
            continue
        if r.width() > 200 and r.top < cr.top + 260 and L._overlaps(r, cr):
            return c
    return None''',
'''def search_box_xy(hwnd, win):
    """★ 搜索框是**自绘 Pane**，UIA 树里不是 Edit ⇒ 用形状定位（第 2 层）。
    ⚠ 实测 598px 窄侧边栏下，Edit 类控件在插件区**一个都没有**。"""
    pts = D.locate_all(hwnd, win, log=lambda m: None)
    return pts.get("search_box")''')
s = s.replace('''    sb = search_box(win)
    if sb is None:
        return hwnd, win, "找不到搜索框"
    sb.click_input()
    time.sleep(0.35)''',
'''    pt = search_box_xy(hwnd, win)
    if pt is None:
        return hwnd, win, "找不到搜索框"
    click(pt[0], pt[1], 0.4)          # 点搜索框
    time.sleep(0.35)''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("search_box 改为形状定位")
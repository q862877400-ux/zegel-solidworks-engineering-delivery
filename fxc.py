from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_cards.py")
s = p.read_text(encoding="utf-8")
old = '''# 覆盖:   后续同级定义
# ⚠ 本模块只做定位；点击由调用方发起。
# ────────────────────────────────────────────────────────────────────
"""'''
new = '''# ⚑ 分类卡同理：名字由 UIA 给，**不靠截图抄**（我曾照截图手抄成
#    「导向轴支架」，实际是「导向轴支座」，于是 6/19 假失败）
# ⚑ 实测（容器 569px / 1495px 两种宽度，10 列 / 3 列两种排布）：
#     19 张分类卡**全部**能按名字读到坐标，100x100 大小一致
#       转轴(477,355) 导向轴(605,355) 导向轴支座(733,355) …
#     ⇒ **宽度/列数完全不影响** —— 因为坐标是「问控件树要」的。

# 覆盖:   后续同级定义
# ⚠ 本模块只做定位；点击由调用方发起。
# ────────────────────────────────────────────────────────────────────
"""'''
assert old in s
s = s.replace(old, new, 1)
# 加分类卡定位函数
s = s.replace("if __name__ == \"__main__\":", '''def category_cards(win) -> list[tuple[str, Any]]:
    """列出**分类页**上的所有卡（按名字 → 矩形）。

    ⚠ 不筛控件类型/大小 —— 实测分类卡是 100x100 的 Pane，但尺寸可能随宽度变。
      只按「在插件区内 + 有名字 + 不是结构名」收。
    """
    cr = L.container_rect(win)
    if cr is None:
        return []
    SKIP = {"swCaption", "SearchBox", "swCmdMgr", "swMenu", "任务窗格",
            "EM Frame", "header", "taskPaneConfig", "expandCollapse", "pin",
            "swInnerFrame", "Task Pane Tabs Wnd", "工作区", "设置"}
    out = []
    seen = set()
    for c in L._controls(win):
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if not t or t in SKIP or t in seen:
            continue
        if not L._overlaps(r, cr) or r.width() < 40 or r.height() < 20:
            continue
        if r.top < cr.top + 120 or r.bottom > cr.bottom - 20:
            continue
        seen.add(t)
        out.append((t, r))
    out.sort(key=lambda d: (d[1].top, d[1].left))
    return out


def locate_category(win, name: str):
    """按名字定位一张分类卡。找不到返回 None。"""
    for t, r in category_cards(win):
        if t == name or t.startswith(name):
            return r
    return None


if __name__ == "__main__":''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已补 category_cards / locate_category")
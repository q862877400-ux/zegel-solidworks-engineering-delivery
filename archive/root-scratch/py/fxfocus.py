from pathlib import Path

# ① steps: ensure_front 不再阻断
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")
old = '''def ensure_front(h: int) -> bool:
    """确认前台是 SolidWorks；不是就取回。**取不回就返回 False**。

    ⚠ 用户中途动一下鼠标就会让焦点跑掉 —— 此时若继续发按键，
      事件全发给别的窗口（实测后果：打字进了聊天框）。
    ⇒ **焦点不明时必须停下**，而不是硬发。
    """
    import win32gui
    if win32gui.GetForegroundWindow() == h:
        return True
    ok = L.focus_solidworks(h)
    return win32gui.GetForegroundWindow() == h if ok else False'''
new = '''def ensure_front(h: int) -> bool:
    """尽量把 SolidWorks 置前。**不再阻断动作**（用户 2026-09-30 关闭焦点守护）。

    ⚑⚑⚑ 为什么取消阻断
    原实现在取不回焦点时让调用方 ``return None``，于是「点返回」**根本没发生**，
    抽查 12 件全部报「回首页失败」——**守卫把主流程掐死了**。
    实测该页面下 ``GetForegroundWindow()`` 常常不等于 SolidWorks（用户在用电脑、
    或 DSH 窗口在前），而**鼠标点击其实照样落到目标控件上**。
    ⇒ 现在只**尽力置前**并记录，返回 True 恒成立；真正判定「有没有生效」的
      责任交给**动作之后的页面判据**（那才是可靠证据）。
    """
    import win32gui
    try:
        if win32gui.GetForegroundWindow() == h:
            return True
        L.focus_solidworks(h)
        if win32gui.GetForegroundWindow() != h:
            log("   (焦点未取得，仍继续 —— 由点击后的页面判据验收)")
    except Exception:
        pass
    return True'''
assert old in s
s = s.replace(old, new, 1)
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("① steps.ensure_front 已改为不阻断")

# ② audit: goto 不再因焦点返回 None
p2 = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_audit.py")
s2 = p2.read_text(encoding="utf-8")
s2 = s2.replace('''    for _ in range(tries):
        if not S.ensure_front(h):
            return None
        S.cache_drop()''',
'''    for _ in range(tries):
        S.ensure_front(h)          # 只尽力置前，**不再阻断**
        S.cache_drop()''')
s2 = s2.replace('''    if not S.ensure_front(h):
        rec["stage"] = "焦点拿不回"
        return rec
    btn = L.locate(w, "生成预览", "Button")''',
'''    S.ensure_front(h)
    btn = L.locate(w, "生成预览", "Button")''')
p2.write_text(s2, encoding="utf-8")
ast.parse(s2)
print("② audit 不再因焦点中止")

# ③ select: fill_to_100 里的焦点中止也去掉
p3 = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_select.py")
s3 = p3.read_text(encoding="utf-8")
s3 = s3.replace('''        if not S.ensure_front(h):
            S.log("  焦点不在 SolidWorks，中止")
            break
''', '''        S.ensure_front(h)          # 尽力置前，不中止
''')
p3.write_text(s3, encoding="utf-8")
ast.parse(s3)
print("③ select 不再因焦点中止")
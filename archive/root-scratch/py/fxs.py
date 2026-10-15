from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")
old = '''# ⚑ 判据怎么定（全部用「可读到的界面状态」，不用截图判断）'''
new = '''# ⚑⚑⚑ 用户第二次指正（2026-09-30，同一晚）
# ------------------------------------------------------------------
# ① 「你还要每次开始前检测插件现在在什么界面啊，插件不是每次都在首页等着你」
#    ⇒ **每次 connect 后必须先判定当前页面类型**，再决定下一步点哪里。
#      我此前的脚本假设「永远从首页开始」，一旦停在别处就整条链错位。
#      ⇒ ``resume()``：按当前页面类型**续跑**而不是从头点。
# ② 「每一步操作前的焦点检测也没有了，人玩意刚好动了一下鼠标你就报错」
#    ⇒ Windows 只把键盘/鼠标事件投给**前台窗口**；用户碰一下鼠标，
#      我的按键就发去了别处。
#      ⇒ **每个动作之前**都要确认前台是 SolidWorks，不是就直接取回；
#      确认不了就**跳过这一步并留证**，绝不在焦点不明时发按键。
#      另：SetCursorPos 会**抢用户鼠标** ⇒ 动作之间必须让回，
#      并在动作前重新确认坐标没有被别人移动。

# ⚑ 判据怎么定（全部用「可读到的界面状态」，不用截图判断）'''
assert old in s
s = s.replace(old, new, 1)

add = '''

# ── 焦点守卫（用户指正 ②）────────────────────────────────────────
def ensure_front(h: int) -> bool:
    """确认前台是 SolidWorks；不是就取回。**取不回就返回 False**。

    ⚠ 用户中途动一下鼠标就会让焦点跑掉 —— 此时若继续发按键，
      事件全发给别的窗口（实测后果：打字进了聊天框）。
    ⇒ **焦点不明时必须停下**，而不是硬发。
    """
    import win32gui
    if win32gui.GetForegroundWindow() == h:
        return True
    ok = L.focus_solidworks(h)
    return win32gui.GetForegroundWindow() == h if ok else False


def act_with_focus(h: int, fn: Callable[[], None], what: str) -> bool:
    """执行一个动作，但**前后都验焦点**；焦点跑掉就中止并留证。"""
    if not ensure_front(h):
        log("   ⚠ 焦点拿不回来，放弃动作「%s」" % what)
        return False
    try:
        fn()
    except Exception:
        log("   动作「%s」异常:\\n%s" % (what, traceback.format_exc()[-300:]))
        return False
    return True


# ── 断点续跑（用户指正 ①）────────────────────────────────────────
def resume(h: int, w, targets: list[tuple[str, str, Callable[[int, Any], None]]]):
    """按**当前页面**决定从哪一步继续，而不是假设在首页。

    targets: [(页类型, 步骤名, 动作), ...]  —— 按顺序
    找到第一个「当前页类型 == 判据类型」的步骤，从那里继续。
    """
    st = read_state(w)
    cur = page_kind(st)
    log("当前在 %s" % cur)
    for i, (kind, name, act) in enumerate(targets):
        if kind == cur:
            log("从第 %d 步「%s」继续" % (i + 1, name))
            return i, name, act
    log("没有与 %s 匹配的步骤，从头开始" % cur)
    return 0, targets[0][1], targets[0][2] if targets else (0, "", None)
'''
s = s.replace("if __name__ == \"__main__\":", add + "\n\nif __name__ == \"__main__\":", 1) if "__main__" in s else s + add
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("已加 ensure_front / act_with_focus / resume")
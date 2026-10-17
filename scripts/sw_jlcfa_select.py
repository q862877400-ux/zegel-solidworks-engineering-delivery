r"""嘉立创 FA 选型流程：把参数填到 100% 再生成预览。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测驱动）
# 定位:   补齐 sw_jlcfa_gui 的后半程 —— **填参数 -> 100% -> 生成**。

# ⚑⚑⚑ 本轮四次的误判，全部是同一个病
# ----------------------------------------------
# 我把「代码执行了」当成了「操作生效了」。四次都是：
#   我说「滚轮无效 / 面板不动」，用户说「要点空白处才能滚」。
#   我扫了一眼截图觉得没变就下结论 —— **其实应该比哈希**：
#       md5(截图) 相同 ⇒ 真没变；不同 ⇒ 变了。
# ⚑ **纪律：任何「操作无效」的判断，必须先比对截图哈希**，
#   不许靠肉眼看。代码写了不等于生效了。
#
# ⚑⚑⚑ 正确动作序列（用户口述 + 本机实测，2026-09-30）
# ----------------------------------------------
#   ① 点**参数筛选器框内部**的空白处  → 焦点落到该控件
#      ⚠ 点在框外 / 框底 / 控件上都不行，这是四次失败里最隐蔽的一个
#   ② 滚轮（MOUSEEVENTF_WHEEL）或拖右侧竖滑块  → 才能翻页
#   ③ 点「请选择」下拉 → Alt+↓ 展开 → ↓ 选值
#   ④ 参数区右侧有一条竖滚动条，**滑块位置反映滚动量**
#   ⑤ 顶部进度条百分比 = 已填比例；**100% 时「生成预览」才可点**
#
# ⚑ 速度（用户要求「还要速度快」）
# ----------------------------------------------
# · 每步截图一次是**必要的**，但**只在需要判定时**截；
#   连续动作（点下拉→选值）之间不截，靠「填完后统一验一次进度条」。
# · 等待时间按「状态变化」判定，而不是固定 sleep：
#   截进度条区域一小块，比哈希，变了就停等 ⇒ 比 sleep 3 秒快且更可靠。

# ⚠ 已知不足（未解决）
# ----------------------------------------------
# · 进度条百分比如何解析未验证（截图里是纯色条，需按像素宽度比例算）
# · 参数下拉的选项列表**读不到文字**（自绘控件），只能按序号选

# 覆盖:   后续同级定义
# ⚠ 本模块会驱动 GUI 并操作 SolidWorks。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SHOTS = Path(Path(__file__).resolve().parents[1] / "shots")


def md5_png(img) -> str:
    """截图指纹 —— 判断「界面到底变了没」的**唯一可靠依据**。"""
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return hashlib.md5(buf.getvalue()).hexdigest()[:12]


def crop_region(img, rect, dx, dy, w, h):
    """裁一块（相对标签列的偏移），用于「只截变化区域 ⇒ 快且好比对」。"""
    x0 = max(rect.right + dx, 0)
    y0 = max(rect.top + dy, 0)
    return img.crop((x0, y0, min(x0 + w, img.width), min(y0 + h, img.height)))


def fill_blank(hwnd, rect, gui) -> str:
    """① 点参数筛选器框内部空白处取焦点。返回点击坐标。"""
    x = rect.right - 4 + 310
    y = rect.top - 16 + 690
    gui.click(x, y, pause=0.6)
    return f"({x},{y})"


def scroll(gui, rect, amount=-3):
    """② 翻页：滚轮（调用方须先 fill_blank）。"""
    gui.wheel(rect.right + 200, rect.top + 300, amount, pause=0.5)


def pick_first(gui) -> None:
    """③ 下拉选第一项：Alt+↓ 展开，↓ 选中，Enter 确认。

    ⚠⚠ **2026-10-01 轮 62 重写**：原实现是**九段裸 `keybd_event`**（按下 → `sleep` → 抬起），
    而 `sleep` **可被中断** ⇒ 中途异常会让 **Alt / ↓ / Enter 卡在按下态**。
    后果与用户报告逐一吻合（Ctrl 卡住 ⇒ 按 A 变全选；**Enter 卡住 ⇒ 忽然回车**）。
    ⇒ 现在**全部**走 `sw_gui_input` 的异常安全原语（`_hold` / `_press`，抬起在 `finally` 里）。
    """
    from scripts import sw_gui_input as _gi
    import win32con
    _gi._hold([win32con.VK_MENU], win32con.VK_DOWN, pause=0.25)   # Alt+↓ 展开
    _gi._press(win32con.VK_DOWN, pause=0.3)                       # ↓ 到第一项
    _gi._press(win32con.VK_RETURN, pause=0.35)                    # Enter 确认（一定被抬起）


def wait_until_changed(gui, probe, max_wait=12.0, step=0.6):
    """等界面变化：反复截**小区域**比哈希，变了就返回，**不用固定 sleep**。"""
    import shot
    base = md5_png(probe())
    t0 = time.time()
    while time.time() - t0 < max_wait:
        time.sleep(step)
        cur = md5_png(probe())
        if cur != base:
            return time.time() - t0, cur
    return None, base


# ════════════════════════════════════════════════════════════════════
# ★ 宽侧边栏重写（2026-09-30）：按 ComboLBox 实际几何点选
# ════════════════════════════════════════════════════════════════════
# ⚑⚑⚑ 窄侧边栏（容器 569px）能用的「下拉框底部 + 14 + 30」偏移，
#    在**宽侧边栏（容器 1495px）会偏** —— 宽布局参数区行距变了，
#    那一点落在**下一行参数**上 ⇒ 「点了等于没点」，进度恒为 70%。
#
# ⚑ 三条本机实测事实
#   ① 下拉列表是独立顶层窗口，类名 ``ComboLBox``（伴随一个 SysShadow），
#      ``owner == 0``、类名不是 ``#32770`` ⇒ **不是模态框**；
#      但按「同进程 + 有 owner 或类是 #32770」的粗判据会**被误报成模态**。
#   ② 选项列表**不用展开就能读**：``ComboBox.texts()`` → ['请选择','短型','标准型']。
#   ③ ``ComboBox.select(i)`` **不可用**：
#      报 ``There is no ExpandCollapsePattern and no "Open" button``。
#
# ⚑ 填完控件会被重建，**按名字再读可能读不到** ⇒ 判据用**进度百分比**。

#: 下拉列表窗口类名（实测）
COMBO_LIST_CLASS = "ComboLBox"


def _sw_pid(hwnd):
    import win32process
    return win32process.GetWindowThreadProcessId(hwnd)[1]


def combo_list_rect(hwnd):
    """找当前**已展开**的下拉列表矩形。找不到返回 None。"""
    import win32gui
    pid = _sw_pid(hwnd)
    found = None

    def _cb(hh, _):
        nonlocal found
        if found is not None or not win32gui.IsWindowVisible(hh):
            return
        if win32gui.GetClassName(hh) != COMBO_LIST_CLASS or _sw_pid(hh) != pid:
            return
        found = win32gui.GetWindowRect(hh)

    win32gui.EnumWindows(_cb, None)
    return found


def select_index(h, w, combo, items, idx):
    """展开下拉并点第 ``idx`` 项（idx 按 combo.texts() 顺序，0 常是占位）。"""
    import sw_jlcfa_steps as S
    combo.click_input()
    time.sleep(0.9)
    lb = combo_list_rect(h)
    if lb is None:
        S.log("      没找到 ComboLBox（没展开，或被真模态挡住）")
        return False
    n = max(1, len(items))
    row = (lb[3] - lb[1]) / float(n)
    x = (lb[0] + lb[2]) // 2
    y = int(lb[1] + row * (idx + 0.5))
    S.log("      ComboLBox%s %d项 行高%.1f -> 点第%d项「%s」(%d,%d)"
          % (lb, n, row, idx, items[idx] if idx < len(items) else "?", x, y))
    S.click(x, y, 0.6)
    return True


def pending_edits(w):
    """参数区里**值为空**的 Edit 字段，附带右侧的 ``[min~max]`` 范围提示。

    ⚑⚑ 为什么必须有它（2026-09-30 实测）
    参数行**不只有下拉**，还有**自由输入框**（如「花键轴长度（L）」）。
    我此前只填 ComboBox ⇒ 那些行永远空着 ⇒ 抽查里 7 件卡在 66~91%
    报「无待填项」，其实是**有项没填**。
    实测结构：``Edit (2225,937,2430,961)`` 右侧同行有
    ``Text '[55~500]/1'`` ⇒ **范围可读，据此选值**。
    """
    import sw_jlcfa_locate as L
    import sw_jlcfa_steps as S
    allc = S.controls_cached(w)
    cr = S._container_from(allc)
    if cr is None:
        return []
    edits, hints = [], []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            ct = c.element_info.control_type
            if not L._overlaps(r, cr):
                continue
            if ct == "Edit" and t and "请输入产品型号" not in t:
                val = ""
                try:
                    val = c.get_value() or ""
                except Exception:
                    val = ""
                if not str(val).strip():
                    edits.append((t, c, r))
            elif ct == "Text" and t.startswith("[") and "~" in t:
                hints.append((r.top, r.left, t))
        except Exception:
            continue
    out = []
    for t, c, r in edits:
        hint = None
        for htop, hleft, htxt in hints:
            if abs(htop - r.top) <= 14 and hleft >= r.left - 10:
                hint = htxt
                break
        out.append((t, c, r, hint))
    return out


def _parse_hint(hint):
    """``'[55~500]/1'`` → ``(55, 500)``；解析不了返回 ``None``。"""
    import re
    if not hint:
        return None
    m = re.match(r"\[\s*([\d.]+)\s*[~\-]\s*([\d.]+)", hint)
    if not m:
        return None
    try:
        return (float(m.group(1)), float(m.group(2)))
    except Exception:
        return None


def fill_edit(h, w, edit, r, hint, log=None):
    """往一个空 Edit 里填值。

    ⚑⚑⚑ **必须用 UIA ValuePattern，不能走键盘**（2026-09-30 实测）
    鼠标点击是**位置性**的（点哪算哪），但 **Ctrl+V / 按键是焦点性的** ——
    只有**拥有键盘焦点**的窗口才收得到。
    SolidWorks 没焦点时（用户在用电脑 / DSH 在前），
    粘贴会**跑到别的窗口**，于是字段一直是空的，
    而进度自然不动（实测连填 3 次 72% 不动）。
    ⇒ 改用 ``set_edit_text()``（UIA ValuePattern）**直接设值**：
      实测 ``get_value()`` 立刻从 ``''`` 变成 ``'195'``，
      且不再出现在待填列表里。**与焦点无关。**
    """
    import time as _t
    import sw_jlcfa_steps as S
    rg = _parse_hint(hint)
    val = str(int(rg[0])) if rg else "100"
    ok = False
    err = ""
    for meth in ("set_edit_text", "set_text"):
        try:
            getattr(edit, meth)(val)
            ok = True
            break
        except Exception as exc:
            err = "%s: %s" % (meth, str(exc)[:70])
            continue
    if not ok:
        if log:
            log("      Edit「%s」设值失败 %s（类型 %s）"
                % (edit, err, type(edit).__name__))
        return False
    _t.sleep(0.6)
    # 尽量提交（有焦点才有用；没有也不影响，ValuePattern 已写入）
    # ⚠ 2026-10-01 轮 62：原先是裸 `keybd_event(TAB, 按下) → sleep → 抬起`，
    #   中途异常会让 **Tab 卡在按下态**（外层还是 `except: pass` ⇒ 没人收尾）。
    #   ⇒ 改走 `sw_gui_input._press`（抬起在 `finally` 里）。
    try:
        from scripts import sw_gui_input as _gi
        import win32con
        _gi._press(win32con.VK_TAB, pause=0.4)
    except Exception:
        pass
    if log:
        log("      Edit「%s」= %s（范围 %s，ValuePattern）" % (edit, val,
                                                        hint or "无"))
    return True


def pending_params(w):
    """选型页里还没定的参数下拉。排除只读的「代码」「每页」。"""
    import sw_jlcfa_steps as S          # ★ 同上：本函数内导入
    out = []
    for c in S.controls_cached(w):
        try:
            t = (c.window_text() or "").strip()
            if c.element_info.control_type != "ComboBox" or not t:
                continue
            if t == "每页":          # 分页，不是选型参数
                continue
            items = c.texts()
            cur = c.selected_text().strip()
            # ⚠「代码」**也是必填下拉**（实测：只剩它时进度 84% → 100%），
            #   不能当只读排除 —— 我先前排除了它，导致永远到不了 100%。
            # 判据：还停在**第 0 项**（占位「请选择」）就算待填。
            if items and len(items) > 1 and cur == items[0]:
                out.append((t, c, items, cur))
        except Exception:
            continue
    return out


def fill_to_100(h, w, max_rounds=12, pick=1):
    """把选型页参数填到 100%。返回 (h, w, 进度)。

    ⚑ 两类参数都要填：**ComboBox**（点选）与 **Edit**（自由输入）。
      只填 ComboBox 会让带输入框的型号永远卡在 66~91%（实测 7/12 因此失败）。
    ⚑ ``pct`` 可能是 ``None``（部分页面没有进度条）⇒ 此时**不按 100 判**，
      由调用方以「建模完成！」为最终判据。
    """
    import sw_jlcfa_locate as L
    import sw_jlcfa_steps as S          # ★ 本文件的旧版没导入 steps
    stall = 0
    for rnd in range(1, max_rounds + 1):
        # ⚑⚑ 每轮**必须丢缓存重连**：填过一轮后界面会重建控件，
        #   缓存里的旧对象**失去 ValuePattern**（实测报「无 ValuePattern」，
        #   而同一控件在重连后立刻可设值）⇒ 宁可慢也要新对象。
        S.cache_drop()
        try:
            h, w = L.connect()
        except Exception:
            pass
        st = S.read_state(w)
        before = st["pct"]
        if before == 100:
            S.log("  ★ 100%%")
            return h, w, 100
        pend = pending_params(w)
        if pend:
            S.log("  轮%d 进度=%s%% 待填下拉=%s"
                  % (rnd, before, [p[0] for p in pend]))
            name, cb, items, cur = pend[0]
            S.ensure_front(h)          # 尽力置前，不中止
            if L._modal().modal_report(h)["count"]:
                L._modal().close_modals(h, rounds=2)
                h, w = L.connect()
                continue
            if not select_index(h, w, cb, items, pick):
                continue
            S.cache_drop()
            h, w = L.connect()
            after = S.read_state(w)["pct"]
            S.log("      「%s」%r -> %r  进度 %s%% -> %s%%"
                  % (name, cur, items[pick], before, after))
            stall = stall + 1 if after == before else 0
            if stall >= 3:
                S.log("      连 3 次进度不动，停下")
                break
            continue
        # 没有待填下拉 → 看有没有空输入框
        eds = pending_edits(w)
        if eds:
            S.log("  轮%d 进度=%s%% 待填输入框=%s"
                  % (rnd, before, [e[0] for e in eds]))
            name, ctl, r, hint = eds[0]
            S.ensure_front(h)
            if L._modal().modal_report(h)["count"]:
                L._modal().close_modals(h, rounds=2)
                h, w = L.connect()
                continue
            # ⚠ 传 ctl（控件对象），不是 name —— 传错过一次，
            #   报 ``'str' object has no attribute 'set_text'``。
            if not fill_edit(h, w, ctl, r, hint, log=S.log):
                break
            S.cache_drop()
            h, w = L.connect()
            after = S.read_state(w)["pct"]
            S.log("      进度 %s%% -> %s%%" % (before, after))
            stall = stall + 1 if after == before else 0
            if stall >= 3:
                S.log("      连 3 次进度不动，停下")
                break
            continue
        S.log("  轮%d: 下拉与输入框都无待填（进度 %s%%）" % (rnd, before))
        # ⚑ 进度是**异步**的：实测填完最后一个字段时读到的还是 90%，
        #   几秒后同一页面已是 100%（插件在后台重算备选型号数）。
        #   ⇒ 无待填项后**再等一轮**，别急着判失败。
        for _ in range(6):
            import time as _t2
            _t2.sleep(1.0)
            S.cache_drop()
            try:
                h, w = L.connect()
            except Exception:
                continue
            p2 = S.read_state(w)["pct"]
            if p2 is None or p2 >= 100:
                S.log("  ★ 等到了 %s%%" % p2)
                return h, w, p2
        break
    return h, w, S.read_state(w)["pct"]
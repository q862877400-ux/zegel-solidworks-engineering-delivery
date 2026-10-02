r"""参数完整性 —— 以**插件自己的型号行**为准，不看输入框有没有字。

# ── 来源 ─────────────────────────────────────────────────────────────
# 文件:   嘉立创 FA 选型插件 v2.4.1-20260918-1（本机实测）
# 定位:   判断「参数是否都已登记」，以及用**真键盘**补填。

# ⚑⚑⚑ 为什么不能用「输入框非空」当判据（2026-09-30 实测）
# ------------------------------------------------------------------
#   页面上「产品型号」行写着：``BSGY-C7-25-5-L195-F27-P【去填写】``
#   而同一个 P 输入框里 **明明有 '10'**。
# ⇒ ``set_edit_text()``（UIA ValuePattern）只把**文字**写进框，
#   **插件没有把它登记成参数值** ⇒ 进度卡在 90%、点生成无反应。
# ⇒ 判据必须用**插件自己吐出的型号行**：
#     型号行里没有 ``【去填写】`` == 参数齐了。
#   这与「框里有没有字」是两回事 —— 我先前用后者，被假象骗过。

# ⚑ 补填必须走**真键盘**（剪贴板粘贴 + Tab 提交），
#   而键盘事件**只发给拥有焦点的窗口** ⇒ 必须在焦点确认后再打。
#   焦点拿不到时**明确报错**，不假装成功。

# 覆盖:   后续同级定义
# ⚠ 会驱动鼠标键盘。
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from pathlib import Path

import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"" + _ROOT_S + r"\scripts")

import sw_jlcfa_locate as L
import sw_jlcfa_select as SEL
import sw_jlcfa_steps as S


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
warnings.filterwarnings("ignore")

PLACEHOLDER = "【去填写】"


def _container_texts(win) -> list[str]:
    """插件容器内所有控件的文字（去空）。"""
    allc = S.controls_cached(win)
    cr = S._container_from(allc)
    if cr is None:
        return []
    out = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if t and L._overlaps(r, cr):
            out.append(t)
    return out


def _has_cjk(s: str) -> bool:
    """含**中文说明**字符？（用于把「型号值」与「中文描述/标签」分开）

    ⚑⚑ 必须**先剥掉占位符 ``【去填写】```**（2026-09-30 实测教训）
    未填参数的型号行长这样：
        ``CPDH-A9-W【去填写】-L【去填写】``
    占位符本身是中文，若不剥掉，整个型号值会被判成「中文说明」而丢弃
    ⇒ ``model_row()`` 取不到值 ⇒ 判据链断掉。
    """
    s = s.replace(PLACEHOLDER, "")
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def model_row(win):
    """定位「产品型号」行 —— 返回 ``(标签控件, 值控件)``。**结构 + 内容判据，零坐标阈值**。

    ⚑⚑⚑ 实测结构（2026-09-30）
        Pane 'EGH25SAZ0C'                          ← 父 Pane
         ├─ Text '品牌：'                           ← 标签（以「：」结尾）
         ├─ Text 'EGH25SAZ0C'                     ← ★ 型号值
         ├─ Text '购买地址'                          ← 中文
         ├─ Text '产品型号：'                         ← 标签
         └─ Text '上银(HIWIN) EGH系列…'               ← 中文

    ⇒ 判据：**同一父 Pane 下**，值控件 =
      「不以 ``：`` 结尾」且「不含中日韩字符」的那个 ``Text``。
      **完全不看坐标** —— 我此前写 ``abs(r.top - lr.top) <= 8``（同一行 8px 内），
      侧边栏拉宽或 DPI 一变就可能配错行或配不到。
    """
    allc = S.controls_cached(win)
    cr = S._container_from(allc)
    if cr is None:
        return None, None
    label = None
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if t in ("产品型号：", "产品型号:") and L._overlaps(r, cr):
            label = c
            break
    if label is None:
        return None, None
    try:
        kids = list(label.parent().children())
    except Exception:
        return label, None
    # ① 同父 Pane 内：非标签、非中文 ⇒ 型号值（纯内容判据）
    for k in kids:
        try:
            t = (k.window_text() or "").strip()
            ct = k.element_info.control_type
        except Exception:
            continue
        if not t or t.endswith("：") or t.endswith(":"):
            continue
        if _has_cjk(t):
            continue
        if ct not in ("Text", "Edit", "Pane"):
            continue
        return label, k
    # ② 退化：同父 Pane 内**非标签、非中文**的 Text/Edit/Pane
    #    ⚠ 原来这里「取任何非标签文字」，结果抓到了 ``选型PDF`` 这个按钮
    #      ⇒ ``model_line()`` 返回 ``选型PDF`` ⇒ ``unfilled()`` 恒为 0
    #      ⇒ **误判「参数齐了」**（CPDH-A9 就是这么挂的）。
    #    ⇒ 退化分支**同样排除中文**；再找不到就返回 None，
    #      让调用方按「读不到」处理（``unfilled() == -1``），而不是误判。
    for k in kids:
        try:
            t = (k.window_text() or "").strip()
            ct = k.element_info.control_type
        except Exception:
            continue
        if not t or t.endswith("：") or t.endswith(":"):
            continue
        if _has_cjk(t):
            continue
        if ct not in ("Text", "Edit", "Pane"):
            continue
        return label, k
    return label, None


def model_line(win) -> str:
    """「产品型号」的值文字（插件对参数是否齐了的**自述**）。"""
    _lab, val = model_row(win)
    if val is not None:
        try:
            return (val.window_text() or "").strip()
        except Exception:
            return ""
    # 退化：找不到标签时，退回扫容器里含占位符的文字
    for t in _container_texts(win):
        if PLACEHOLDER in t:
            return t
    return ""


def code_present(win, code: str) -> bool:
    """型号行里是否出现目标型号（前 8 位，宽松匹配）。"""
    key = (code or "").split("-")[0][:8].lower()
    if not key:
        return False
    line = model_line(win)
    if key in line.lower():
        return True
    return any(key in t.lower() for t in _container_texts(win))


def unfilled(win) -> int:
    """型号行里 ``【去填写】`` 的个数 == 还差几个参数。

    返回 **-1 表示「读不到型号行」** —— 那是**未知**，不是「齐了」。

    ⚑⚑⚑ 这条区分是必须的（2026-09-30 实测教训）
    插件在重绘的瞬间，``产品型号：`` 标签会短暂读不到，
    此时若把「读不到」当成 0（齐了），就会**误判完成**、
    接着去找「生成预览」按钮（页面上还没渲染）⇒ 报「无生成按钮」。
    抽查里 3 件就是这么挂的。
    ⇒ **读不到就返回 -1**，调用方必须当作「还没齐、再等等」。
    ⚑ 只看**型号行的值控件**：那是插件唯一权威的「哪些参数还没定」的声明。
      ⚠ 不要看「输入框里有没有字」——``set_edit_text`` 能让框里有字而插件不登记。
    """
    line = model_line(win)
    if not line:
        return -1
    return line.count(PLACEHOLDER)


def set_front(hwnd: int, tries: int = 5) -> bool:
    """★ 确保 SolidWorks 拿到**键盘焦点**；拿不到返回 False。

    ⚑ 与 ``ensure_front`` 的区别：那个是「尽力而为不阻断」，
      用于**鼠标**操作（位置性，无所谓焦点）。
      本函数用于**键盘**操作 —— 焦点拿不到就**必须停**，
      否则按键会打进别的窗口，看起来「填了没反应」。
    """
    import win32gui
    for _ in range(tries):
        if win32gui.GetForegroundWindow() == hwnd:
            return True
        L.focus_solidworks(hwnd)
        time.sleep(0.4)
    return win32gui.GetForegroundWindow() == hwnd


def _clip(text: str) -> bool:
    import subprocess
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Set-Clipboard -Value '%s'" % text],
                       check=False, capture_output=True, timeout=20)
        return True
    except Exception:
        return False


def _keys(*seq):
    """seq 元素: (vk, ctrl) 或 vk。

    ⚠⚠ **2026-10-01 轮 62 重写**：原实现是裸 `keybd_event`（按下 → `sleep` → 抬起），
    且 **Ctrl 的按下与抬起分列在 `sleep` 两侧、没有 `finally`** ⇒ 中断即 **Ctrl 卡在按下态**
    （后果：之后按 `A` 就是**全选（蓝底）**）。⇒ 现在全部走 `sw_gui_input` 的异常安全原语。
    """
    from scripts import sw_gui_input as _gi
    import win32con
    for item in seq:
        vk, ctrl = item if isinstance(item, tuple) else (item, False)
        if ctrl:
            _gi._hold([win32con.VK_CONTROL], vk, pause=0.25)
        else:
            _gi._press(vk, pause=0.25)


VK_DIGIT = {c: 0x30 + i for i, c in enumerate("0123456789")}


def _tap(vk: int, pause: float = 0.07) -> None:
    """按一下某键 ⇒ 走 `sw_gui_input._press`（**抬起由 `finally` 保证**）。"""
    from scripts import sw_gui_input as _gi
    _gi._press(vk, pause=pause)


def type_into(hwnd: int, ctl, rect, value: str, log=S.log) -> bool:
    """把 ``value`` 打进 ``ctl`` 并提交。**实现委托给 ``sw_gui_input``**。

    ⚑⚑⚑ 为什么要委托（2026-09-30）
    输入方式/提交键/间隔此前**硬编码在本函数里**，改一次要动代码。
    现在做成配置（``sw_gui_input.CONFIG``）—— 该设计借自 microsoft/UFO (MIT)
    的同名配置项（``input_text_api`` / ``input_text_enter`` /
    ``input_text_inter_key_pause``），但**实现是自己写的，零依赖 UFO**。

    ⚑ 本函数只负责**焦点与点击**（界面层），输入本身交给 ``sw_gui_input``。
    ⚠ 该插件实测：ValuePattern 写了字但**不登记**，Ctrl+V 也不行 ——
      它监听**逐键 KeyPress**，所以 ``CONFIG["input_api"]`` 必须保持 ``type_keys``。
    """
    import sw_gui_input as GI
    # ① 先清模态（弹窗在时，下面的点击会打在弹窗上）
    try:
        if L._modal().modal_report(hwnd)["count"]:
            log("      ⚠ 有模态框（可能是「请输入指定范围内的数字」），先关")
            L._modal().close_modals(hwnd, rounds=2)
            time.sleep(0.5)
    except Exception:
        pass
    # ② 键盘输入必须**确认焦点**（鼠标点击是位置性的，键盘是焦点性的）
    if not set_front(hwnd):
        log("      ✗ 拿不到键盘焦点，放弃键盘输入（不假装成功）")
        return False
    # ③ 点中目标（唯一用坐标的地方 —— 界面层职责）
    S.click((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2, 0.8)
    # ④ 交给输入层
    if log:
        log("      目标 %s" % GI.label(ctl))
    return GI.type_text(ctl, value, log=log)


def first_missing_label(win):
    """型号行里**第一个** ``【去填写】`` 前面的参数标签。

    ⚑⚑ 为什么必须这样定位（2026-09-30 实测）
    原实现每轮都取 ``_all_edits()[0]`` —— 但**第一个字段登记成功后它仍是 [0]**，
    于是我一直重打第一个字段（还会拼成超范围值），
    **永远走不到第二个** ⇒ 抽查里两件停在「缺 1」，
    而且**时好时坏**（哪一件缺取决于顺序）。
    型号行自带标签（``BMHA-0.4-L【去填写】-X15-W【去填写】``），
    取第一个缺口的标签即可**逐字段自推进**。
    """
    import re
    line = model_line(win)
    m = re.search(r"([A-Za-z][A-Za-z0-9_]*)【去填写】", line)
    return m.group(1) if m else None


def find_edit_by_label(win, label: str):
    """按标签找对应的 Edit（名字以前缀匹配，如 ``X`` → ``X（折高）``）。"""
    if not label:
        return None
    for e in _all_edits(win):
        nm = (e[0] or "").strip()
        if nm == label or nm.startswith(label):
            return e
    return None


def _fmt_value(lo: float, hi: float, step: float | None) -> str:
    """按范围算一个**必在区间内**的值，并保留必要小数位。

    ⚑⚑⚑ 这是用户抓到的一个真 bug（2026-09-30）
    原实现写 ``str(int(rg[0]))`` —— 对范围 ``[0.5~20]/0.001``
    取 ``int(0.5) == 0``，而 **0 低于下限 0.5** ⇒ 插件拒收 ⇒
    ``【去填写】`` 不消失 ⇒ 循环**一直重打「0」**，用户看到的就是「重复输入 0」。
    ⚑ 正确做法：
      · 取**下限**（最保险，必在区间内）
      · **不截断小数** —— 按 step 决定小数位；step 未知时按下限自身的小数位
    """
    import decimal
    v = decimal.Decimal(str(lo))
    if step:
        d = decimal.Decimal(str(step))
        places = max(0, -d.as_tuple().exponent)
    else:
        places = max(0, -v.as_tuple().exponent)
    s = ("%%.%df" % places) % v
    if "." in s:
        s = s.rstrip("0").rstrip(".")      # 去掉无意义的尾随零
    if not s or s == "-":
        s = "%g" % lo
    return s


def _probe_candidates(ctl) -> list[str]:
    """**没有范围提示**时的候选值序列。

    ⚑ 绝不猜一个固定值就反复重打（用户报过「一直重复输入 0」）。
      改为一组**由小到大**的候选，配合「未填数是否减少」的判据逐个试；
      试不中就记为失败，不无限循环。
    ⚑ 候选刻意含**小数**（有些字段下限是 0.5 / 0.1，整数 0 会被拒）。
    """
    cands = ["1", "0.5", "5", "10", "0.1", "2", "20", "50", "100", "0.01"]
    # 若框里已有旧值，把它也当候选（可能是合理默认）
    try:
        cur = str(ctl.get_value() or "").strip()
        if cur and cur not in cands:
            cands.insert(0, cur)
    except Exception:
        pass
    return cands


def fill_all(hwnd: int, win, max_rounds: int = 14, pick: int = 1, log=S.log):
    """把参数填到**型号行没有 ``【去填写】```。返回 (h, w, 剩余未填数)。

    ⚑ 判据是**型号行**，不是进度百分比也不是输入框内容。
    ⚑ 每轮按**第一个缺口的标签**定位字段 ⇒ 逐字段自推进，不会卡在同一个。
    ⚑ **同一字段连续失败 3 次就放弃**，不再无限重打（见用户报的「重复输入 0」）。
    """
    fails: dict[str, int] = {}
    for rnd in range(1, max_rounds + 1):
        S.cache_drop()
        try:
            hwnd, win = L.connect()
        except Exception:
            pass
        left = unfilled(win)
        line = model_line(win)
        log("  轮%d 未填=%s 型号=%s" % (rnd, left, line[:60]))
        if left < 0:
            # ⚑ 读不到型号行 = 未知，**不是齐了**。等它渲染出来再判。
            log("      型号行读不到（可能正在重绘），等 1 秒重试")
            time.sleep(1.0)
            continue
        if left == 0 and line:
            log("  ★ 参数齐了")
            return hwnd, win, 0
        # 先补下拉
        pend = SEL.pending_params(win)
        if pend:
            name, cb, items, cur = pend[0]
            if L._modal().modal_report(hwnd)["count"]:
                L._modal().close_modals(hwnd, rounds=2)
                continue
            SEL.select_index(hwnd, win, cb, items, pick)
            continue
        # 再补**第一个缺口**对应的输入框
        # ⚑ 进 Edit 分支前也要清模态：实测插件在超范围输入后会弹
        #   「请输入指定范围内的数字!」，**挡掉之后所有点击**
        #   （连打 3 次都不生效，因为点全落在弹窗上）。此前只在
        #   下拉分支查模态，Edit 分支漏了 —— 这就是「重复输入 0」的真凶。
        if L._modal().modal_report(hwnd)["count"]:
            log("      ⚠ 关闭模态框后继续")
            L._modal().close_modals(hwnd, rounds=2)
            time.sleep(0.6)
            continue
        label = first_missing_label(win)
        ent = find_edit_by_label(win, label)
        if ent is None:
            ent = (SEL.pending_edits(win) or [None])[0]
        if ent is None:
            log("      找不到缺口「%s」对应的输入框" % label)
            break
        name, ctl, r, hint = ent
        # ★ 范围优先用**树结构配对**得到的（与坐标无关）
        row = row_for_label(win, label) or row_for_label(win, name)
        if row and row[4] is not None:
            lo, hi, step = row[4], row[5], row[6]
            val = _fmt_value(lo, hi, step)
        else:
            rg = SEL._parse_hint(hint)
            if rg:
                val = _fmt_value(rg[0], rg[1], _parse_step(hint))
            else:
                # ⚑ 没有范围提示的字段：**不能瞎猜一个固定值**。
                #   用「探测」——依次试若干候选，哪个让「未填」减少就用哪个。
                val = None
        key = label or name
        if fails.get(key, 0) >= 3:
            log("      「%s」已连续失败 3 次，放弃该字段" % key)
            break
        before_left = left
        if val is None:
            cands = _probe_candidates(ctl)
            log("      「%s」无范围提示，探测候选 %s" % (key, cands))
            for cv in cands:
                type_into(hwnd, ctl, r, cv, log=log)
                S.cache_drop()
                try:
                    hwnd, win = L.connect()
                    if unfilled(win) < before_left:
                        val = cv
                        break
                except Exception:
                    pass
            else:
                fails[key] = fails.get(key, 0) + 1
                continue
        else:
            if not type_into(hwnd, ctl, r, val, log=log):
                break
        # 记录是否推进
        S.cache_drop()
        try:
            hwnd, win = L.connect()
            now_left = unfilled(win)
        except Exception:
            now_left = before_left
        if now_left >= before_left:
            fails[key] = fails.get(key, 0) + 1
            log("      「%s」未推进（%d/%d），值=%s"
                % (key, fails[key], 3, val))
        else:
            fails[key] = 0
    S.cache_drop()
    try:
        hwnd, win = L.connect()
    except Exception:
        pass
    return hwnd, win, unfilled(win)


def _parse_step(hint):
    """``'[55~500]/1'`` → ``1.0``；``'[0.5~20]/0.001'`` → ``0.001``。无则 None。"""
    import re
    if not hint:
        return None
    m = re.search(r"\]\s*/\s*([\d.]+)", hint)
    if not m:
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None


#: 插件自报的范围格式：``[195~1500]/1``、``[0.5~20]/0.001``
HINT_PAT = None


def _hint_re():
    global HINT_PAT
    if HINT_PAT is None:
        import re
        HINT_PAT = re.compile(r"^\[\s*([\d.]+)\s*~\s*([\d.]+)\s*\]\s*/?\s*([\d.]*)$")
    return HINT_PAT


def param_rows(win):
    """按**控件树结构**列出参数行。

    返回 ``[(label, ctl, rect, hint, lo, hi, step)]``。

    ⚑⚑⚑ 为什么用树结构而不是坐标（2026-09-30 本机实测）
    实测一行的结构是：

        Pane  'L(总长度）'                 ← 一行一个 Pane
         ├─ Edit  'L(总长度）'            ← 输入框
         ├─ Text  '[195~1500]/1'         ← **插件自报的范围**
         └─ Text  '清除'

    输入框与其范围提示是**同一 Pane 下的兄弟**。
    ⇒ 按父子关系配对，**与 DPI / 侧边栏宽度 / 行距无关**；
      按坐标邻近配对（我此前的做法）在换显示器或拉窗口后会错配。
    ⚑ **范围不用记，也不用猜** —— 插件把它印在每一行上。
    """
    import re
    out = []
    for c in list(S.controls_cached(win)):
        try:
            if c.element_info.control_type != "Edit":
                continue
            label = (c.window_text() or "").strip()
            if not label or "请输入产品型号" in label:
                continue
            r = c.rectangle()
            par = c.parent()
            hint = None
            for sib in par.children():
                t = (sib.window_text() or "").strip()
                m = _hint_re().match(t)
                if m:
                    hint = t
                    break
            lo = hi = step = None
            if hint:
                m = _hint_re().match(hint)
                lo, hi = float(m.group(1)), float(m.group(2))
                step = float(m.group(3)) if m.group(3) else None
            out.append((label, c, r, hint, lo, hi, step))
        except Exception:
            continue
    return out


def row_for_label(win, label: str):
    """按标签找参数行（名字取前缀匹配，如 ``X`` → ``X（折高）``）。"""
    if not label:
        return None
    rows = param_rows(win)
    for row in rows:
        nm = (row[0] or "").strip()
        if nm == label or nm.startswith(label):
            return row
    return None


def _all_edits(win):
    """参数区**所有** Edit（含已有文字的），供「重打一遍」用。"""
    out = []
    allc = S.controls_cached(win)
    cr = S._container_from(allc)
    if cr is None:
        return []
    hints = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            ct = c.element_info.control_type
            if not L._overlaps(r, cr):
                continue
            if ct == "Text" and t.startswith("[") and "~" in t:
                hints.append((r.top, r.left, t))
        except Exception:
            continue
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
            if c.element_info.control_type != "Edit":
                continue
            if not L._overlaps(r, cr) or not t:
                continue
            if "请输入产品型号" in t:
                continue
            hint = None
            for htop, hleft, htxt in hints:
                if abs(htop - r.top) <= 14 and hleft >= r.left - 10:
                    hint = htxt
                    break
            out.append((t, c, r, hint))
        except Exception:
            continue
    return out

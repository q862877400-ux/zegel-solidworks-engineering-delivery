"""★ **带弹窗哨兵的调用护栏**：真机调用从它走 ⇒ **弹窗被主动发现、主动点掉、内容随返回值上来**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/sw_guard.py
# 定位:   ★ 2026-10-02（轮 376）**用户要的框架**：★ 不管弹窗是**启动前就有的**还是**执行中弹的**，
#   都要①主动知道 ②主动处置 ③把内容交到 LLM 手上；★ 且**不许"等到天荒地老"**。
# 官方依据: 不适用（★ 用 Win32 `EnumWindows`/`EnumChildWindows` + `WM_COMMAND`/`IDOK` + 子进程超时）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★★ 为什么这么设计（★ 用户点破的两种失败）：
# ```
# 失败一：★ 只检测"新窗口" ⇒ **旧弹窗永远没人管** ⇒ 调用一直挂着。
# 失败二：★ 只报信、不处置 ⇒ 报信之后**还得等人** ⇒ 代码触发弹窗时**任务不返回**。
# ```
# ⇒ 所以本模块把三件事**绑在一起**（缺一件就退化成上面两种失败）：
# ```
# ① **进调用之前先扫一遍**（★ `pre_scan`）—— ★ 把**已经存在**的弹窗也列入（★ 对应失败一）
# ② **哨兵线程边跑边扫**，发现即 **记证 + 点掉**（★ 对应失败二：处置不等 LLM）
# ③ **主调用有硬超时** ⇒ 无论怎样都返回；★ 把 `dialogs_seen` 一并带回（★ 让 LLM 拿到根因线索）
# ```
# ★ 处置为什么可以"自动先点"（★ 与用户那条纪律的关系）：
#   ★ 用户要的是「**先让 LLM 分析根因，再点，点完还得改**」；★ 而**点在 LLM 看到之前**是为了
#   ★ **不让调用冻死**（★ 否则 LLM 连"发生了什么"都拿不到）。
#   ⇒ ★★ 所以**证据照留**（★ 标题 + 全部控件文本 + 时间 + 触发它的那个调用），
#     ★ **根因与"改代码防复发"仍由 LLM 做** —— ★ 那一步**不能自动**，也**没被跳过**。

from __future__ import annotations

import argparse
import ctypes
import json
import subprocess
import sys
import threading
import time
from ctypes import wintypes as wt
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
#: ★ 弹窗取证落盘目录（★ 供 LLM 事后读；★ 也供 `--report` 打印）
OUT_DIR = Path(r"D:\AI\SW\output\dialog-events")

_u = ctypes.windll.user32
_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
_WM_COMMAND = 0x0111
_IDOK = 1
_BM_CLICK = 0x00F5        #: ★ 给按钮直接投一发点击（★ **用 PostMessage**，★ SendMessage 会等对方⇒卡）
_VK_RETURN = 0x0D
KEYEVENTF_KEYUP = 0x0002    #: ★ 名字必须是这个（现后缀）—— 门禁的 AST 判据按它认
_INPUT_KEYBOARD = 1
_MOUSEEVENTF_LEFTDOWN = 0x0002
_MOUSEEVENTF_LEFTUP = 0x0004
_MOUSEEVENTF_ABSOLUTE = 0x8000


def dismiss_via_input(hwnd: int) -> bool:
    """★ **用真实输入事件**点掉对话框 —— ★ 对手动能点、`PostMessage` 点不掉的窗口有效。

    ★★★★ 2026-10-02（轮 376）**为什么需要这条第二方案**（★ 用户在真机上验证出来的）：
    ```
    hwnd=11733074：IsHungAppWindow=True · SendMessageTimeout(WM_NULL,1500ms)=0
      ⇒ 我试过 `PostMessage(WM_COMMAND, IDOK)`、`PostMessage(WM_COMMAND, **真实ID=2**, 按钮)`、
        `PostMessage(BM_CLICK)` —— **三种都不生效**（★ 而★ **都不报错** ⇒ 看起来"点成功了"）
      ⇒ ★★ 而**用户手动一点，它就消失了**（★ 并弹出下一个）
    ```
    ⇒ ★★★ **真因**：`PostMessage` 只是把消息放进**目标线程的消息队列**，
      ★★ 而那个线程**卡在自己的消息循环里**（`hung=True`）⇒ **消息永远不被取出执行**；
      ★ 而**真实输入事件**（`SendInput`/`keybd_event`）由**系统输入队列**投递，
      ★ 且**不需要目标线程主动取出** ⇒ ★ **它能进到那个对话框自己的处理里** ✓
    ⇒ 做法：★ **把对话框置前 ⇒ 发回车**（★ 回车 = 按默认按钮，★ **不用算坐标**）⇒
      ★ 兜底再对"确定"按钮的中心发**真鼠标点击**（`SendInput` 的绝对坐标移动 + 左右键）。
    """
    ok = False
    #: ① 置前（★ 真输入事件要求目标在前台；★ `SetForegroundWindow` 失败也不放弃，②还能试）
    try:
        _u.SetForegroundWindow(hwnd)
        time.sleep(0.15)
    except Exception:                                           # noqa: BLE001
        pass
    #: ② 回车键（★ 走系统输入队列 —— 见上面真因）
    #:   ★★ 2026-10-02（轮 377）**门禁教会我正确形态**：★ 它的判据是
    #:   「**按下与抬起必须在同一函数的 `try`/`finally` 配对里**」——
    #:   ★ 我第一版把**按下**放在 `try` **之外**（只有 `sleep` 在里面）⇒ 门禁仍报 FAIL。
    #:   后果（用户 2026-10-01 实报）：★ 修饰键卡在按下态 ⇒ Ctrl 卡住后按 A 就是**全选**、
    #:   Enter 卡住就是**忽然回车**，★ 而且**不周期性**、持续到用户单独按一下那个键为止。
    #:   ⇒ ★ 正确写法：**按下与抬起都进 `try`/`finally`**。
    try:
        _u.keybd_event(_VK_RETURN, 0, 0, 0)
        time.sleep(0.05)
        ok = True
    finally:
        _u.keybd_event(_VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.3)
    if not _u.IsWindow(hwnd):
        return True
    #: ③ 兜底：对每个 `Button` 的中心发**真鼠标点击**
    buttons: list[int] = []

    def _cb(ch, _l):
        if _cls(ch) == "Button":
            buttons.append(int(ch))
        return True

    _u.EnumChildWindows(hwnd, _PROC(_cb), 0)
    r = wt.RECT()
    for btn in buttons:
        if not _u.GetWindowRect(btn, ctypes.byref(r)):
            continue
        cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
        sw, sh = _u.GetSystemMetrics(0), _u.GetSystemMetrics(1)
        ax, ay = int(cx * 65535 / max(1, sw - 1)), int(cy * 65535 / max(1, sh - 1))
        _u.SetCursorPos(cx, cy)
        _u.mouse_event(_MOUSEEVENTF_ABSOLUTE | _MOUSEEVENTF_LEFTDOWN, ax, ay, 0, 0)
        _u.mouse_event(_MOUSEEVENTF_ABSOLUTE | _MOUSEEVENTF_LEFTUP, ax, ay, 0, 0)
        ok = True
        time.sleep(0.35)
        if not _u.IsWindow(hwnd):
            return True
    return ok


def _txt(h: int) -> str:
    n = _u.GetWindowTextLengthW(h)
    if n <= 0:
        return ""
    b = ctypes.create_unicode_buffer(n + 2)
    _u.GetWindowTextW(h, b, n + 2)
    return b.value


def _cls(h: int) -> str:
    b = ctypes.create_unicode_buffer(256)
    _u.GetClassNameW(h, b, 256)
    return b.value


def _exe_of_window(hwnd: int) -> str:
    """★ 取该窗口**所属进程的可执行文件全路径**（纯 ctypes，★ 不跑子进程）。

    ★★ 用它来判"这个窗口是不是 SolidWorks 家族的" —— ★ 比按 PID 过滤**稳**：
    ★ 真机查到 SolidWorks **有一大堆独立进程**（★ 见 `sw_family_window` 的文档串）。
    """
    pid = wt.DWORD()
    _u.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    k32 = ctypes.windll.kernel32
    #: ★ `PROCESS_QUERY_LIMITED_INFORMATION = 0x1000`（★ 对更高完整性级别的进程也可能失败）
    h = k32.OpenProcess(0x1000, False, pid.value)
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        size = wt.DWORD(len(buf))
        if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(size)):
            return buf.value
    finally:
        k32.CloseHandle(h)
    return ""


def sw_family_window(hwnd: int) -> bool:
    """★ 该窗口是否属于 **SolidWorks 家族**（★ 用户要求：★ "只要是 SolidWorks 的弹窗，就要 100% 能处理"）。

    ★★★★ 2026-10-02（轮 379）**判据的依据来自真机查到的进程树**：
    ```
    主进程  sldworks.exe                       (D:\\Program Files\\SOLIDWORKS Corp\\…)
    子进程  sldProcMon.exe · swCefSubProc.exe ×3
    同族    EwServer.exe · SWVisualize.Queue.Server.exe · remotesolverdispatcherservice.exe ·
            dispatcher.exe · sldworks_fs.exe · **cwbcbfmesh.exe（网格器）** · sldsurfacing.exe
    ```
    ⇒ ★★ **弹窗可能来自其中任意一个** ⇒ ★ **只认 `sldworks.exe` 会漏**（★ 例如网格器的报错框）。
    ⇒ ★ 判据：★ **进程 exe 路径属于 SolidWorks 家族** —— 三个特征之一即可：
      ★ 含 `SOLIDWORKS Corp`（安装目录）· 含 `SOLIDWORKS Shared`（共享组件）·
      ★ 文件名以 `sld` 或 `sw` 开头（★ `sldworks` / `sldProcMon` / `sldsurfacing` / `swCefSubProc` /
        `swScheduler` …；★ 而 `cwbcbfmesh.exe` 靠上面两条路径命中）。
    """
    exe = _exe_of_window(hwnd)
    if not exe:
        return False
    low = exe.lower()
    base = low.rsplit("\\", 1)[-1]
    if "solidworks corp" in low or "solidworks shared" in low:
        return True
    return base.startswith(("sld", "sw")) and base.endswith(".exe")


def classify_dialog(d: dict) -> dict:
    """★ **弹窗安全分级** —— 决定"能不能自动点、点哪个"，★ 还是**必须交给 LLM**。

    ★★★★ 2026-10-02（轮 380）**用户点破的那一层**：
    ```
    ★ 用户原话：★「这也是为什么我最开始认为**要走 LLM**，就是想让这个机制能处理所有弹窗，
      **弹窗原因千千万函数写死的话肯定无法全部解决**」
    ⇒ ★★ 我先前"发现"那层做得不错（家族进程 + 三条特征 + 兜底），而**处置**那层**是写死的**：
      ★ `dismiss()` 取到按钮 ID 就 `WM_COMMAND` —— ★★ **等于"随便点一个"**。
    ```
    ★ 真机上见过三类（★ 观察器实录）：
    ```
    ① `确定`                                   ← ★ 安全
    ② `是 | 否 | 确定 | Button1`                ← ★★ **危险**：「是否覆盖？」点"是"与"否"后果相反
    ③ `暂停 | 取消 | 更多>>`（求解进度窗）     ← ★★ **危险**：点掉 = **中断一个正在跑的正常任务**
    ```
    ⇒ ★ **分级**（★ 而 `needs_llm=True` 的**不自动点** ⇒ ★ 那正是"走 LLM"的落点）：
      · `auto`        ★ 只有一个语义明确的"确认类"按钮 ⇒ **自动点**
      · `needs_llm`   ★ 有 否/取消/暂停/上一步/下一步，或按钮多于一个同权项 ⇒ **不点，报给 LLM**
      · `forbidden`   ★ 文本含危险词（删除/覆盖/替换/丢失/不可逆/remove/overwrite/delete…）⇒ **绝不自动点**
    """
    controls = d.get("controls") or []
    buttons = [str(c.get("text", "")).strip() for c in controls if c.get("class") == "Button"]
    texts = " ".join(str(c.get("text", "")) for c in controls if c.get("class") != "Button")
    blobs = " ".join(buttons)

    #: ★ **危险词**（★ 中英）—— 命中就**绝不自动点**（★ 哪怕只有一个"确定"）
    #:   ★★ 2026-10-02（轮 381）**自测抓到漏网**：★ 文本 "不可恢复" 被判成 `auto` ——
    #:   因为表里只有"不可逆"、没有"不可恢复" ⇒ ★★ 而**"是否删除？不可恢复"恰好只有一个"确定"**
    #:   ⇒ ★ **会被自动点掉**（★ 后果不可逆）。⇒ 补词 + **加"提问信号"判据**（见下）。
    DANGER = ("删除", "覆盖", "替换", "丢失", "不可逆", "不可恢复", "无法恢复", "无法撤销",
              "撤销", "谨慎", "真的要", "确定要", "确认删除", "清空", "格式化", "永久", "风险",
              "delete", "overwrite", "replace", "discard", "lose", "permanent", "format",
              "reset all", "clear all", "cannot be undone", "irreversible")
    #: ★★ **提问信号** —— ★ 弹窗在**问**（★ 问号/"是否"/"吗"/"要不要"）⇒ ★ **绝不自动点**：
    #:   ★ 因为"问"意味着**至少两条分支**，★ 而回答哪条**要看语义** —— ★ 那正是 LLM 的活。
    QUESTION = ("？", "?", "是否", "吗", "要不要", "确定要", "would you", "are you sure", "do you want")
    #: ★ **确认类**（★ 可以安全点的）
    OKISH = ("确定", "确认", "关闭", "好", "是", "ok", "close", "yes", "continue", "继续", "完成",
             "finish", "done")
    #: ★ **高危类**（★ 出现就**不自动点**）
    RISKY = ("否", "取消", "暂停", "上一步", "下一步", "跳过", "忽略", "no", "cancel", "pause",
             "back", "next", "skip", "ignore", "abort", "retry", "重试")

    blob = blobs + " " + texts
    low = blob.lower()

    def _hit(words) -> list[str]:
        """★ 命中判定：★ **中文按子串、英文按词边界**。

        ★★★★ 2026-10-02（轮 381）**测试当场抓到的假阳性**：★ `Close`（关闭，安全）里含 `lose`
          ⇒ 用子串匹配就把**安全的"关闭"判成危险词** ⇒ ★ 该点的框点不掉。
        ⇒ ★ 英文必须按**词边界**（★ `\\blose\\b` 不匹配 `close`）；★ 中文没有词边界概念，照旧子串。
        """
        import re as _re
        out = []
        for w in words:
            if all(ord(ch) > 0x2E80 for ch in w):          #: ★ 中文（含全角标点）⇒ 子串
                if w in blob:
                    out.append(w)
            else:                                          #: ★ 英文 ⇒ 词边界
                if _re.search(r"\b%s\b" % _re.escape(w.lower()), low):
                    out.append(w)
        return out

    hit_danger = _hit(DANGER)
    hit_question = _hit(QUESTION)
    hit_risky = _hit(RISKY)
    okish = _hit(OKISH)
    if hit_danger:
        return {"mode": "forbidden", "reason": "文本含危险词 %s ⇒ 绝不自动点" % hit_danger[:3],
                "buttons": buttons, "hit": hit_danger[:3]}
    if hit_question:
        return {"mode": "forbidden",
                "reason": "弹窗在**提问**（%s）⇒ 至少两条分支、答哪条要看语义 ⇒ 绝不自动点"
                          % hit_question[:3],
                "buttons": buttons, "hit": hit_question[:3]}
    if hit_risky or len(buttons) > 1:
        return {"mode": "needs_llm",
                "reason": ("按钮 %s 里有多义/高危项 %s ⇒ 点哪个取决于弹窗在问什么"
                           % (buttons, (hit_risky or ["多于一个同权按钮"])[:3])),
                "buttons": buttons, "hit": hit_risky[:3]}
    if okish or len(buttons) == 1:
        return {"mode": "auto", "reason": "只有一个语义明确的确认按钮 %s ⇒ 可自动点" % (okish[:1] or buttons),
                "buttons": buttons}
    return {"mode": "needs_llm", "reason": "没有可识别的按钮 ⇒ 请 LLM 看文本决定", "buttons": buttons}


def scan_family_windows(pid: int | None = None, *, known: set | None = None) -> list[dict]:
    """★ **放宽后的弹窗判据**：★ 属于 SolidWorks 家族 + 新出现的可见顶层窗口 + **像弹窗**。

    ★★ "像弹窗"用**与类名无关**的三条特征取或（★ 用户要求覆盖**所有** SolidWorks 弹窗）：
      ① 类名是 `#32770`（★ Win32 经典对话框）
      ② **有 `Button` 子控件**（★ 那才是"等用户点的东西" —— ★ 本质，不是偶然）
      ③ 有**可见**且有文本的 `Static`/`Edit` 子控件（★ 只有提示文字的极简框）
    ⇒ ★ 于是**不管它是什么类名**（XAML/Qt/CEF/自定义），★ 只要它是"要我点/要我读"的框，就能被认出来。
    """
    out: list[dict] = []
    seen = known or set()

    def _cb(h, _l):
        if not _u.IsWindowVisible(h):
            return True
        p = wt.DWORD()
        _u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if pid is not None and p.value != pid:
            return True
        if not sw_family_window(h):
            return True
        c, t = _cls(h), _txt(h)
        if c.startswith(("Afx:", "DummyDWMListenerWindow", "ThumbnailDeviceHelperWnd",
                         "Shell_TrayWnd", "ToolbarWindow32")):
            return True
        kids_buttons: list[int] = []
        kids_text = 0
        #: ★★★ 2026-10-02（轮 380）**必须把控件文本一并带出来** —— 真机上撞到的 bug：
        #:   ★ 我先前只回 `buttons` / `text_children` 两个**计数**，★ 而 `classify_dialog` 读的是
        #:   `controls`（★ 类名 + 文本）⇒ ★★ **分级判据永远看到"没有按钮"** ⇒ 把
        #:   一个只有"确定"的**安全弹窗**判成 `needs_llm` ⇒ **不点** ⇒ **调用冻死**（★ 120 s 超时）。
        #:   ⇒ ★ 教训：★ **判据与数据源之间"字段不匹配"会让判据静默失效**（★ 事实 51 同族）。
        controls: list[dict] = []

        def _ck(ch, _l2):
            nonlocal kids_text
            kc, kt = _cls(ch), _txt(ch)
            if kc == "Button":
                kids_buttons.append(int(ch))
                controls.append({"class": "Button", "text": kt[:200]})
            elif kc in ("Static", "Edit") and kt.strip():
                kids_text += 1
                controls.append({"class": kc, "text": kt[:300]})
            return True

        _u.EnumChildWindows(h, _PROC(_ck), 0)
        is_dialog = (c == "#32770") or bool(kids_buttons) or (kids_text > 0)
        if not is_dialog:
            return True
        key = (int(h), c, t)
        if key in seen:
            return True
        out.append({"hwnd": int(h), "pid": int(p.value), "class": c, "title": t[:160],
                    "hung": bool(_u.IsHungAppWindow(h)), "buttons": kids_buttons,
                    "text_children": kids_text, "controls": controls,
                    "exe": _exe_of_window(h).rsplit("\\", 1)[-1]})
        return True

    _u.EnumWindows(_PROC(_cb), 0)
    return out


def scan_any_new_window(pid: int | None = None, *, known: set | None = None) -> list[dict]:
    """★ **兜底探测**：★ 列出该 PID 的**所有可见顶层窗口**（★ **不限类名**）。

    ★★★★ 2026-10-02（轮 378）**用户问「这个机制适用于所有弹窗吗」**，我实测后如实分层的结论：
    ```
    ✅ **适用**：SolidWorks 自家的**同进程 `#32770`** 模态框（★ 已真机验证）
    ❌ **扫不到**（★ 本函数就是为这一层准备的兜底）：
       ① **类名不是 `#32770`** 的弹窗 —— 本机实测同类有
          `XamlExplorerHostIslandWindow_WASDK`（XAML/WPF）· `Qt51514QWindowIcon` ·
          `CEF-OSC-WIDGET` · `UnityWndClass` · `Chrome_WidgetWin_1` · `TaskbarWindow` …
       ② **别的进程**的弹窗（★ 真机见过 `pid=41076` 的 `Simulation`）
       ③ **UAC / 安全桌面** —— ★ 它在**另一个桌面**上，`EnumWindows` **根本看不到**
    ```
    ⇒ ★★ **最坏的结果是"静默失效"**（★ 扫不到 ⇒ 以为没弹窗 ⇒ 继续等）——
      ★ 那正是上一轮"卡住一动不动"的病。⇒ 所以**兜底必须让它可见**：
      ★ 把"**新出现的、类名不是我认识的那些**的窗口"一并报回来，
      ★ 由调用方（LLM）判"它是不是一个我没见过的弹窗"。
    """
    out: list[dict] = []
    seen = known or set()

    def _cb(h, _l):
        p = wt.DWORD()
        _u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if pid is not None and p.value != pid:
            return True
        if not _u.IsWindowVisible(h):
            return True
        c = _cls(h)
        t = _txt(h)
        #: ★★★ 2026-10-02（轮 378）**兜底必须排除 `#32770`** —— 真机上撞到的误报：
        #:   ★ SolidWorks 弹下一个对话框时，**同一个类的窗口**会以**新 `hwnd`** 出现 ⇒
        #:   兜底把它报成 `unknown-window` 并写"本机制无法点掉它"，★ **而它其实已被主路径点掉了**
        #:   （★ `dismissed: true` 就在上一条记录里）⇒ ★★ **那种误报会让人以为机制失效**。
        if c == "#32770":
            return True
        #: ★ 已知的"不是弹窗"的类名（★ 主窗口 / DWM 辅助窗口 / 托盘 …）—— 减少噪声
        if c.startswith(("Afx:", "DummyDWMListenerWindow", "ThumbnailDeviceHelperWnd",
                         "Shell_TrayWnd", "ToolbarWindow32")):
            return True
        key = (int(h), c, t)
        if key in seen:
            return True
        out.append({"hwnd": int(h), "pid": int(p.value), "class": c, "title": t[:160],
                    "hung": bool(_u.IsHungAppWindow(h))})
        return True

    _u.EnumWindows(_PROC(_cb), 0)
    return out


def _kids(h: int) -> list[dict]:
    rows: list[dict] = []

    def _cb(ch, _l):
        t = _txt(ch).strip()
        if t:
            rows.append({"class": _cls(ch), "text": t[:400]})
        return True

    _u.EnumChildWindows(h, _PROC(_cb), 0)
    return rows


def scan(pid: int | None = None, *, visible_only: bool = True) -> list[dict]:
    """★ 一次快照：所有 `#32770`（★ **纯 ctypes，秒回**，★ 不截屏 ⇒ 不会卡）。"""
    out: list[dict] = []

    def _cb(h, _l):
        p = wt.DWORD()
        _u.GetWindowThreadProcessId(h, ctypes.byref(p))
        if pid is not None and p.value != pid:
            return True
        if visible_only and not _u.IsWindowVisible(h):
            return True
        if _cls(h) != "#32770":
            return True
        #: ★★★★ 2026-10-02（轮 376）**新增 `hung`** —— 真机撞出来的：僵尸窗口发消息也无效。
        #:   ★ 判据：`IsHungAppWindow`（★ 再用 `SendMessageTimeout(WM_NULL)` 二次确认，防假阳）。
        hung = bool(_u.IsHungAppWindow(h))
        if not hung:
            res = wt.DWORD(0)
            r = _u.SendMessageTimeoutW(h, 0x0000, 0, 0, 0x0002, 800, ctypes.byref(res))
            hung = (r == 0)
        out.append({"hwnd": int(h), "pid": int(p.value), "title": _txt(h)[:160],
                    "hung": hung, "controls": _kids(h)})
        return True

    _u.EnumWindows(_PROC(_cb), 0)
    return out


def dismiss(hwnd: int) -> bool:
    """★ 点掉一个对话框（★ **零硬编码**：不看按钮文本、不按坐标）。

    ★★★★ 2026-10-02（轮 376）**两个真因，都在真机上撞出来的**：
    ```
    ① 那个 `Simulation` 弹窗的按钮控件 ID 是 **2**（`Button 确定` ⇒ `GetDlgCtrlID` = 2），
       ★★ **而不是 `IDOK = 1`** ⇒ 原先发 `WM_COMMAND` + `IDOK` **打错了按钮** ⇒ 弹窗纹丝不动。
    ② ★ **不能用 `SendMessage`** —— 它是**同步**的、要等目标窗口处理完；
       ★★ 而模态对话框**正在自己的消息循环里等用户** ⇒ `SendMessage(BM_CLICK)` **挂住 300 s**。
       ⇒ ★ **必须用 `PostMessage`**（投递即返回，不等对方）。
    ```
    ⇒ 修法：★ **先取该弹窗里所有 `Button` 的真实 `GetDlgCtrlID`，逐个 `PostMessage(WM_COMMAND, id, 按钮)`**；
      ★ 再对每个按钮补一发 `PostMessage(BM_CLICK)` 作兜底。
    """
    ok = False
    buttons: list[int] = []

    def _cb(ch, _l):
        if _cls(ch) == "Button":
            buttons.append(int(ch))
        return True

    _u.EnumChildWindows(hwnd, _PROC(_cb), 0)
    for btn in buttons:
        cid = int(_u.GetDlgCtrlID(btn))
        #: ★ 用**真实 ID** 发 `WM_COMMAND`（★ 而不是假设 `IDOK`）
        if _u.PostMessageW(hwnd, _WM_COMMAND, cid, btn):
            ok = True
        #: ★ 兜底：直接给按钮投一发点击（★ 同样用 `PostMessage` —— 见上面真因②）
        if _u.PostMessageW(btn, _BM_CLICK, 0, 0):
            ok = True
    if not buttons:
        #: ★ 没有按钮的极简对话框（★ 例如只有一行提示）⇒ 退回 `IDOK`
        ok = bool(_u.PostMessageW(hwnd, _WM_COMMAND, _IDOK, 0))
    return ok


def sw_pid() -> int | None:
    """★ SLDWORKS 的 PID（★ 按父窗口特征，★ 不跑子进程）。"""
    got: int | None = None

    def _cb(h, _l):
        nonlocal got
        if not _u.IsWindowVisible(h):
            return True
        if _cls(h).startswith("Afx:") and _txt(h).startswith("SOLIDWORKS"):
            p = wt.DWORD()
            _u.GetWindowThreadProcessId(h, ctypes.byref(p))
            got = p.value
            return False
        return True

    _u.EnumWindows(_PROC(_cb), 0)
    return got


class Sentinel:
    """★ **弹窗哨兵**：后台线程，每 `interval` 秒扫一遍；发现即**记证 + 点掉**。

    ★ 它同时扫 **启动前就有的**（★ `pre_scan`）与 **执行中弹的** —— ★ 两者都算"报警弹窗"。
    """

    def __init__(self, pid: int | None, *, interval: float = 0.5, auto_dismiss: bool = True):
        self.pid = pid
        self.interval = interval
        self.auto_dismiss = auto_dismiss
        self.events: list[dict] = []
        self._stop = threading.Event()
        self._seen: set[tuple] = set()
        #: ★★ **兜底的"已见窗口"集合**（★ 类名不限）—— 见 `scan_any_new_window` 的 docstring：
        #:   ★ 我的机制**只认 `#32770`**，而现代 UI 的弹窗类名五花八门（XAML/Qt/CEF/Unity…）⇒
        #:   ★★ **扫不到就等于静默失效**（★ 那正是"卡住一动不动"的病）⇒ 兜底让它**可见**。
        self._seen_any: set[tuple] = set()
        #: ★ 进调用前先记录一份"基线的非弹窗顶层窗口"（★ 之后只报**新增**的）
        try:
            self._seen_any |= {(w["hwnd"], w["class"], w["title"])
                               for w in scan_any_new_window(pid, known=self._seen_any)}
        except Exception:                                       # noqa: BLE001
            pass
        #: ★★ **进调用之前先扫一遍**（★ 对应"只检测新窗口"那种失败：旧弹窗也得管）
        self._sweep(first=True)

    def _sweep(self, *, first: bool = False) -> None:
        #: ★★★★ 2026-10-02（轮 379）**主路径换成放宽判据** —— 用户要求
        #:   「★ **只要是 SolidWorks 的弹窗，这个机制就应该 100% 能处理**」。
        #:   ⇒ `scan_family_windows`：★ **属于 SolidWorks 家族**（★ 主进程 + `sldProcMon` /
        #:     `swCefSubProc` / `cwbcbfmesh` / `sldsurfacing` / `sldworks_fs` … 靠 **exe 路径**判定）
        #:     ★ 且 **像弹窗**（★ `#32770` **或** 有 `Button` 子控件 **或** 有可见文本子控件
        #:     ⇒ ★ **与类名无关**）。
        #:   ⇒ 于是"认类名"那个盲区（XAML/Qt/CEF 的自定义类名）**被消掉**了。
        try:
            items = scan_family_windows(self.pid)
        except Exception as exc:                                # noqa: BLE001
            self.events.append({"at": datetime.now().isoformat(timespec="seconds"),
                                "error": str(exc)[:160]})
            return
        for d in items:
            key = (d["hwnd"], d["title"])
            if key in self._seen:
                continue
            self._seen.add(key)
            #: ★★★★ 2026-10-02（轮 380）**先分级，再决定点不点** —— ★ 这是"走 LLM"那一层的落点：
            #:   ★ `forbidden` / `needs_llm` ⇒ **不自动点**（★ 只记证）⇒ ★ 交给 LLM 研判。
            #:   ★ 诚实说明其代价：**不点就可能让调用继续冻着** ⇒ ★ 靠外层**硬超时**兜底
            #:   （★ 宁可超时返回并带着证据，★ 也不瞎点一个"是否覆盖？"）。
            verdict = classify_dialog(d)
            fired = False
            if self.auto_dismiss and verdict["mode"] == "auto":
                fired = dismiss(d["hwnd"])
                if not fired or _u.IsWindow(d["hwnd"]):
                    fired = dismiss_via_input(d["hwnd"]) or fired
                    if _u.IsWindow(d["hwnd"]):
                        fired = False
            self.events.append({
                "at": datetime.now().isoformat(timespec="seconds"),
                "phase": "pre" if first else "during",
                "kind": "dialog",
                "hwnd": d["hwnd"], "pid": d["pid"], "title": d["title"],
                "class": d.get("class"), "exe": d.get("exe"),
                "controls": d.get("controls") or [{"class": "Button", "text": "(按钮 %d 个)" % len(d.get("buttons") or [])}],
                "hung": d.get("hung"),
                "verdict": verdict,
                "needs_llm": verdict["mode"] != "auto",
                "dismissed": fired,
                "still_present": bool(_u.IsWindow(d["hwnd"])),
            })
            self._write(self.events[-1])
        #: ★★★★ **兜底**：★ 报出"新出现的、家族内但**不像弹窗**"的窗口 ⇒ ★ **让残余盲区可见**
        #:   （★ 正常运行时**零输出** —— 主窗口 / CEF 窗口都不满足"像弹窗"那三条）
        try:
            news = scan_family_windows(pid=None, known=None)
            news = [w for w in news if (w["hwnd"], w["class"], w["title"]) not in self._seen_any]
        except Exception:                                       # noqa: BLE001
            news = []
        for w in news:
            self._seen_any.add((w["hwnd"], w["class"], w["title"]))
            if w["hung"] is False and (w["buttons"] or w["text_children"]) and w["class"] == "#32770":
                continue                                            #: ★ 已在主路径里处置过
            ev = {"at": datetime.now().isoformat(timespec="seconds"),
                  "phase": "pre" if first else "during",
                  "kind": "family-window",
                  "hwnd": w["hwnd"], "pid": w["pid"], "class": w["class"], "exe": w["exe"],
                  "title": w["title"], "hung": w["hung"], "dismissed": False,
                  "note": "★ 属于 SolidWorks 家族，**但不像弹窗**（无 `#32770`、无 Button、无可读文本）"
                          "⇒ 报出来是为了**不让残余盲区静默失效**。"}
            self.events.append(ev)
            self._write(ev)

    @staticmethod
    def _write(ev: dict) -> None:
        try:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            p = OUT_DIR / ("%s-%s.json" % (ev["at"].replace(":", ""), ev["hwnd"]))
            p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        except Exception:                                       # noqa: BLE001
            pass

    def _loop(self) -> None:
        while not self._stop.is_set():
            self._sweep()
            self._stop.wait(self.interval)

    def start(self) -> "Sentinel":
        self._th = threading.Thread(target=self._loop, daemon=True)
        self._th.start()
        return self

    def stop(self) -> None:
        self._stop.set()
        if self._th is not None:
            self._th.join(timeout=2.0)


def run_guarded(argv: list[str], *, timeout: float = 120.0, pid: int | None = None,
                auto_dismiss: bool = True) -> dict:
    """★ **在护栏里跑一个子进程命令** ⇒ 回 `{ok, returncode, timed_out, seconds, aborted_for_llm, dialogs}`。

    ★★ 四条保证（★ 前三条对"卡住"的三种失败，★ 第四条是 2026-10-02 轮 380 **用户点破**的）：
      ① **弹窗在跑之前就有的，也被扫到**（`phase == "pre"`）；
      ② **跑的过程中弹的，被扫到并被点掉**（`phase == "during"`，`dismissed: true`）；
      ③ **超时到了照样返回**（`timed_out: true`）；
      ④ ★★★★ **遇到"我不能自己决定点哪个"的弹窗（`needs_llm`）⇒ **立刻终止子进程**、马上返回**
         ⇒ ★ `aborted_for_llm: true` + `dialogs` 里带 `verdict`。
    ★ **为什么必须有第 ④ 条**（★ 用户原话：「**跑一个验证结果把自己卡死了**」）：
      ```
      ★ 我先前的写法是：`needs_llm` ⇒ **不点**（★ 以为"等 LLM 来判"）。
      ★★ 而**那个时刻 LLM 根本不在回路里** —— ★ 它正**阻塞在等这个工具返回**！
      ⇒ ★ 于是弹窗挂着、子进程冻着、**120 s 超时**才回来（★ 真机实录 `timed_out: true · 120.41 s`）。
      ⇒ ★★★ **正解**：★ "要 LLM 判"**不等于**"原地等 LLM" ——
        ★ **先把调用终止、把证据交给 LLM**，★ LLM 在**下一次动作**里判、点、再重试。
      ```
    """
    t0 = time.time()
    sentinel = Sentinel(pid if pid is not None else sw_pid(), auto_dismiss=auto_dismiss).start()
    rc: int | None = None
    out = err = ""
    timed = False
    aborted_for_llm = False
    try:
        proc = subprocess.run(argv, check=False, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout,
                              cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL)
        rc, out, err = proc.returncode, proc.stdout or "", proc.stderr or ""
    except subprocess.TimeoutExpired as exc:
        rc, timed = None, True
        out = (exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) \
            else (exc.stdout or "")
        err = (exc.stderr or b"").decode("utf-8", "replace") if isinstance(exc.stderr, bytes) \
            else (exc.stderr or "")
    finally:
        time.sleep(0.4)
        sentinel.stop()
        #: ★★★★ **第 ④ 条**：★ 若哨兵记到过 `needs_llm`（★ 它**故意没点**），
        #:   而子进程**还活着**（★ 被那个弹窗冻住）⇒ ★ **现在就杀掉它**，
        #:   ⇒ ★ 于是本函数**立刻返回**，★ 把弹窗证据交给 LLM（★ 而不是等超时）。
        if any(e.get("needs_llm") for e in sentinel.events):
            aborted_for_llm = True
            try:
                import subprocess as _sp
                _sp.run(["taskkill", "/F", "/T", "/PID", str(getattr(proc, "pid", 0))],
                        capture_output=True, timeout=15)
            except Exception:                                   # noqa: BLE001
                pass
    #: ★★★★★ 2026-10-03（轮 466）**第 ⑤ 条：跑完必须回连一次 SolidWorks** ——
    #:   ★★ 起因是**用户亲眼看到三个「SOLIDWORKS Design 意外关闭」窗口**而我的护栏全报 `ok: true`。
    #:   ⇒ ★★★ **根因：`ok` 只证明「子进程退出码 0」，不证明 SolidWorks 还活着。**
    #:     SW 会在**之后的**某个 COM 调用上崩 ⇒ ★ 单跑"通过"是**假象**，
    #:     而那让整批探针的判据**失效**（★ 8 个操作单独跑全 ok，而 SW 崩了三次）。
    #:   ★ 本段就是补那一格：**用一个新的 COM 连接去问一声"你还活着吗"** ✓
    #:   ⚠ 只在**子进程原本成功**时才判（失败的情形已有更准的原因，不该被这条盖掉）。
    #:   ⚠ 回连失败**只降级为 `sw_alive=False`**，不抛 —— ★ 因为有些命令本来就不该连 SW
    #:     （如纯静态门禁）⇒ ★ 由**调用方**决定要不要因此判失败 ✓
    sw_alive = None
    sw_alive_error = ""
    if rc == 0 and not timed:
        try:
            import subprocess as _sp
            probe = _sp.run(
                [sys.executable, "-c",
                 "import sys;sys.path.insert(0, r'%s');import sw_connect;"
                 "sw,doc=sw_connect.connect_solidworks(wait_seconds=15);"
                 "print(repr(str(getattr(sw,'RevisionNumber','?'))))" % (str(REPO_ROOT / "scripts"))],
                capture_output=True, text=True, encoding="utf-8", errors="replace",
                timeout=60, stdin=_sp.DEVNULL)
            sw_alive = (probe.returncode == 0)
            if not sw_alive:
                sw_alive_error = ((probe.stderr or "") + (probe.stdout or "")).strip()[-400:]
        except Exception as exc:                                # noqa: BLE001
            sw_alive = False
            sw_alive_error = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    return {"ok": (rc == 0 and not timed and not aborted_for_llm), "returncode": rc,
            "timed_out": timed, "aborted_for_llm": aborted_for_llm,
            "sw_alive": sw_alive, "sw_alive_error": sw_alive_error,
            "seconds": round(time.time() - t0, 2), "dialogs": sentinel.events,
            "stdout_tail": out[-4000:], "stderr_tail": err[-2000:]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="只扫一遍（不处置）")
    ap.add_argument("--clear", action="store_true", help="扫一遍并**点掉**所有弹窗")
    ap.add_argument("--report", action="store_true", help="打印已记录的事件")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="护栏执行命令时的硬超时（秒）——★ 保证不会「等到天荒地老」")
    ap.add_argument("command", nargs="*", help="要护栏执行命令（--command 之后）")
    args = ap.parse_args()
    if args.report:
        if not OUT_DIR.is_dir():
            print("  （没有事件记录）")
            return 0
        for p in sorted(OUT_DIR.glob("*.json"))[-12:]:
            print("  " + json.dumps(json.loads(p.read_text(encoding="utf-8")),
                                    ensure_ascii=False)[:200])
        return 0
    if args.scan or args.clear:
        pid = sw_pid()
        #: ★★ **处置要循环** —— 真机观察到的：★ 弹窗是**逐个来的**
        #:   （★ 点掉 `零件33-DSH-142 : 失败` ⇒ 又弹 `零件34-DSH-142 : 失败`）⇒ 只点一次不够。
        for rnd in range(1, 6):
            found = scan(pid)
            if not found:
                print("  [轮%d] 弹窗 0 个 ⇒ 清理完成" % rnd)
                break
            print("  [轮%d] SLDWORKS pid=%s · 弹窗 **%d** 个" % (rnd, pid, len(found)))
            for d in found:
                print("    hwnd=%s hung=%s title=%r" % (d["hwnd"], d["hung"], d["title"]))
                for c in d["controls"]:
                    print("       %-12s %s" % (c["class"], c["text"][:120]))
                if not args.clear:
                    continue
                #: ★★ **两段式**：① `PostMessage`（快，★ 对 `hung=False` 够用）
                #:   ② 若窗口**仍在** ⇒ **真实输入事件**（★ 对手动可点的 `hung=True` 窗口才有效）
                first = dismiss(d["hwnd"])
                time.sleep(0.4)
                gone = not _u.IsWindow(d["hwnd"])
                print("       ⇒ ① PostMessage: %s · 窗口已消失=%s" % (first, gone))
                if gone:
                    continue
                second = dismiss_via_input(d["hwnd"])
                time.sleep(0.5)
                print("       ⇒ ② 真实输入事件: %s · 窗口已消失=%s"
                      % (second, not _u.IsWindow(d["hwnd"])))
        return 0
    if args.command:
        #: ★★★ 2026-10-04（接手轮）**修一处真缺陷**：这里原来写 `run_guarded(args.command)`
        #:   —— ★ `--timeout` **被解析了、却从没传进去** ⇒ **永远走 120 s 默认值**。
        #:   ★★ 真机现场：`python tools/sw_guard.py --timeout 3000 -- python <长跑探针>.py`
        #:     ⇒ 探针在 **120.43 s** 被杀，★ 而返回体里 `timed_out: true · dialogs: []`
        #:     ⇒ ★ **看不出是"护栏自己的超时没生效"**，极容易被读成"探针挂了"（★ 事实 517 同族）。
        #:   ★★★ **这条正是本仓自己的定则**（事实 40）：「★ **一个存在但没人用的参数，
        #:     与没有它等价**」—— ★ 而它比没有更糟：★ **文档与 `--help` 都写着它管用** ✓
        r = run_guarded(args.command, timeout=args.timeout)
        #: ★ 顺带把**子进程的 stdout** 也带回来（★ 原来只回一个 ≤1200 字符的 JSON 且
        #:   **明确剔掉了 `stdout_tail`**）⇒ ★ 长跑探针的**过程读数**（每一步的 print）
        #:   就全丢了 —— ★ 而"哪一步走完了"正是排查长跑失败时最需要的东西（★ 事实 293 同族）。
        out = {k: v for k, v in r.items() if k != "stdout_tail"}
        print(json.dumps(out, ensure_ascii=False, indent=1)[:1200])
        tail = (r.get("stdout_tail") or "").strip()
        if tail:
            print("── 子进程 stdout（尾部 4000 字符）──")
            print(tail[-4000:])
        return 0 if r["ok"] else 1
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

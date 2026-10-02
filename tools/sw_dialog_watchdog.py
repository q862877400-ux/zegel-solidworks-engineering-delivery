r"""@brief SolidWorks 系窗口**看门狗** —— ⚠⚠⚠ 【已被否决 —— 不是正解】（见 known-facts 176）

## ⚠⚠⚠ **用户 2026-10-01 明确否决了这个方案，它不是正解**
```
用户原话：「**你不要使用任何看门狗，看门狗这个东西不可靠，你就从代码层面解决**」
★ 它不可靠的三条理由（★ 保留文件只为记录，**不要把它当方案捡起来**）：
  ① **轮询有窗口期** —— COM 可能在它扫到之前就挂住了（STA + 模态框 ⇒ 挂住即无解）
  ② **本机专属** —— 别人装了本 skill 并没有这个看门狗
  ③ **只是反应，不是阻止** —— 而且它必须"先看见框"才能动作
⇒ ★★ **正解见 known-facts 176**：**进程隔离**（把会弹框的调用放进可被杀的子进程）。
```
：自动检测并**安全**清掉模态框（★ 24h 计划的地基工具）。

## ★★★ 为什么需要它（用户 2026-10-01 的指令）
```
用户原话：「**你不能等我提醒你一次你就清理一次啊，你得能检测各种情况可能会弹出什么窗口
然后自己清理**」
⇒ ★ 在此之前我是**被动**的：出了框 → 用户截图 → 我才去点。
   ★ 而且第一次"一次清干净"时我用 `WM_CLOSE` 扫了**所有** `#32770`，
   ★★ 结果**把 SolidWorks 一起关掉了**（见 known-facts 175）。
⇒ ★★ 所以本工具要同时解决**两件事**：
     ① **自动**（不必等提醒 —— 能常驻、能扫全家）
     ② **安全**（★ 只做对话框**自己的语义**允许的动作，★ 绝不外部强加关闭）
```

## ★★★ 分类规则（这是本工具的核心，不是"见到 `#32770` 就点"）
```
对每一个顶层窗口，按**它自己拥有的子控件**判断它是什么：

● **主框架窗口**（SolidWorks 主体）：★ **绝不碰**。
  判据：★ 它有菜单栏（class `#32768`）或工具栏，而 `#32770` 对话框没有。
  ★ 保守做法：**只处理 `class == "#32770"` 的窗口** —— 主框架不是这个类。

● **可安全关闭的提示框**：★ 它有一个按钮，文字在**白名单**里 ——
  `确定 / OK / 关闭 / Close / 是 / 否 / Yes / No / 继续 / Continue / 重试 / Retry / 忽略 / Ignore`
  ⇒ ★ 动作 = **`BM_CLICK` 到那个按钮**（★ 这是**对话框自己的语义**：等于用户点了它）。

● ⚠ **必须停下来问人的框**：★ 出现**破坏性动作**的按钮 ——
  `保存 / Save / 另存 / Save As / 另存为 / 覆盖 / Overwrite / 删除 / Delete`
  ⇒ ★ **一个字都不点**，记录下来并报 `needs_human`。
  ★★ 理由：这类框是**数据安全闸门**；自动点是**不可逆**的。

● ⚠ **没有按钮的框**（模态等待 / 进度）：★ 不碰，只记录（★ 它可能自己在跑完）。

● ★★ **绝不使用** `WM_CLOSE` / `WM_DESTROY` / `EndTask` ——
  因为它们**不由对话框的语义决定**，而是外部强加 ⇒ ★ **上一次就是这么把 SolidWorks 关掉的**。
```

## ★★ 安全阀（每次动作前后都验）
```
① ★ 动作**前**：记录宿主的 PID 与"还活着"；
② ★ 动作**后**：★ **回读宿主是否还在** —— 若消失 ⇒ **立即停止并报 `host_died`**
   （★ 不许继续扫下一个，★ 因为已经出事了）。
③ ★ **每次只处理一个窗口**，处理完回读，再下一个。
④ ★ `--max-actions` 上限（默认 5）⇒ 防止"点了又弹、弹了又点"的死循环。
⑤ ⚠ 默认 **`--dry-run`**（只看不点）—— ★ 要真点必须显式给 `--apply`。
```

## 用法
```
#: ① 看一眼现在有哪些窗口（★ 只看不点，默认）
python tools/sw_dialog_watchdog.py

#: ② 清一次（点白名单按钮）
python tools/sw_dialog_watchdog.py --apply

#: ③ 常驻看门狗（每 3 秒扫一次，★ 真机脚本跑的时候挂在旁边）
python tools/sw_dialog_watchdog.py --apply --watch --interval 3 --duration 300

#: ④ 把结果落 JSON（★ 给证据脚本引用）
python tools/sw_dialog_watchdog.py --apply --json D:\AI\SW\output\dialog-watch.json
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机安全工具）
# 文件:   tools/sw_dialog_watchdog.py
# 定位:   24h 计划的**地基工具** —— 让"无人值守挂起"这一类事故**可自动收敛**。
# 官方依据: 不适用（纯 Win32 窗口枚举）；★ 判据来自本项目实测：
#          known-facts 174（模态框挂住 COM）· 175（`WM_CLOSE` 扫荡把关掉 SolidWorks）
# 许可:   本仓库 MIT。纯 ctypes，无第三方依赖。
# ⚠ 本工具**会点按钮** ⇒ 默认 dry-run；真点要显式 `--apply`。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wt
import json
import sys
import time
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)

#: ── 目标进程（★ 只扫这些进程拥有的窗口；别的一律不碰）──────────────────
TARGET_PROCESSES = ("SLDWORKS.exe", "star.exe", "swShell.exe", "sldBgDwld.exe")

#: ── 按钮白名单：★ "关闭它"是对话框**自己的语义** ──────────────────────
DISMISS_BUTTONS = {
    "确定", "确认", "关闭", "好", "继续", "是", "否", "重试", "忽略", "完成",
    "ok", "close", "yes", "no", "continue", "retry", "ignore", "dismiss", "cancel",
}
#: ── ⚠ 破坏性动作：★ 见到就**停下报人**，一个字都不点 ────────────────
DANGEROUS_BUTTONS = {
    "保存", "另存", "另存为", "覆盖", "删除", "移除", "放弃", "不保存",
    "save", "save as", "overwrite", "delete", "remove", "discard",
}

WM_CLICK = 0x00F5                      #: BM_CLICK
GW_OWNER = 4

EnumWindowsProc = ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)

#: ★ 测试开关（`--any-process`）：True 时不限制进程。★ 默认 False（只碰目标进程）。
ANY_PROCESS = [False]


def _text(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(512)
    user32.GetWindowTextW(wt.HWND(hwnd), buf, 512)
    return buf.value


def _cls(hwnd: int) -> str:
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(wt.HWND(hwnd), buf, 256)
    return buf.value


def _pid(hwnd: int) -> int:
    p = wt.DWORD()
    user32.GetWindowThreadProcessId(wt.HWND(hwnd), ctypes.byref(p))
    return int(p.value)


def _children(hwnd: int) -> list[dict]:
    out: list[dict] = []

    def cb(h, _l):
        out.append({"hwnd": int(h), "cls": _cls(h), "text": _text(h)})
        return True

    user32.EnumChildWindows(wt.HWND(hwnd), EnumWindowsProc(cb), 0)
    return out


def _proc_name(pid: int) -> str:
    try:
        import subprocess

        r = subprocess.run(["tasklist", "/FI", "PID eq %d" % pid, "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=10)
        line = (r.stdout or "").strip().splitlines()
        if line:
            return line[0].split(",")[0].strip('"')
    except Exception:                                          # noqa: BLE001
        pass
    return "?"


def survey() -> list[dict]:
    """**扫一遍**：列出目标进程拥有的顶层窗口 + 它们的子控件（★ 只看不动）。"""
    found: list[dict] = []

    def cb(h, _l):
        if not user32.IsWindowVisible(wt.HWND(h)):
            return True
        pid = _pid(h)
        pname = _proc_name(pid)
        if not ANY_PROCESS[0] and pname.lower() not in [p.lower() for p in TARGET_PROCESSES]:
            return True
        cls = _cls(h)
        kids = _children(h)
        buttons = [k for k in kids if k["cls"] == "Button" and k["text"].strip()]
        statics = [k["text"].strip() for k in kids
                   if k["cls"] in ("Static", "Edit") and k["text"].strip()]
        owner = user32.GetWindow(wt.HWND(h), GW_OWNER)
        #: ★ 分类
        if cls != "#32770":
            kind = "main_frame"                     #: ★ 主框架 ⇒ 绝不碰
        elif any(b["text"].strip().lower() in DANGEROUS_BUTTONS for b in buttons):
            kind = "dangerous"                      #: ⚠ 有破坏性按钮 ⇒ 报人
        elif any(b["text"].strip().lower() in DISMISS_BUTTONS for b in buttons):
            kind = "dismissable"                    #: ✓ 可安全关
        else:
            kind = "unknown"                        #: ⚠ 无白名单按钮 ⇒ 不碰
        found.append({
            "hwnd": int(h), "cls": cls, "title": _text(h), "pid": pid, "process": pname,
            "is_owned": bool(owner), "kind": kind,
            "buttons": [{"hwnd": b["hwnd"], "text": b["text"]} for b in buttons],
            "text": statics[:4],
        })
        return True

    user32.EnumWindows(EnumWindowsProc(cb), 0)
    return found


def _host_alive(pid: int) -> bool:
    """★ 安全阀：宿主进程还在吗（用 OpenProcess 探活，不用 tasklist，快）。"""
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    h = ctypes.WinDLL("kernel32", use_last_error=True).OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
    if not h:
        return False
    ctypes.WinDLL("kernel32").CloseHandle(h)
    return True


def handle(win: dict, apply: bool) -> dict:
    """处理**一个**窗口。★ 每次只处理一个，处理完由调用方回读宿主。"""
    res = dict(win)
    if win["kind"] == "main_frame":
        res["action"] = "skip（主框架 —— 绝不碰）"
        return res
    if win["kind"] == "unknown":
        res["action"] = "skip（没有白名单按钮 ⇒ 不碰，避免误关）"
        return res
    if win["kind"] == "dangerous":
        res["action"] = "★ needs_human（出现破坏性按钮如「保存/另存/删除」⇒ 一个字都不点）"
        return res
    #: dismissable
    target = None
    for b in win["buttons"]:
        if b["text"].strip().lower() in DISMISS_BUTTONS:
            target = b
            break
    if target is None:
        res["action"] = "skip（没找到可点的白名单按钮）"
        return res
    res["clicked"] = target["text"]
    if not apply:
        res["action"] = "dry-run（会点 '%s'）" % target["text"]
        return res
    pid_before = win["pid"]
    user32.SendMessageW(wt.HWND(target["hwnd"]), WM_CLICK, 0, 0)
    time.sleep(0.6)
    alive = _host_alive(pid_before)
    res["host_alive_after"] = alive
    res["action"] = ("点了 '%s'（★ 宿主仍在）" % target["text"] if alive
                     else "★★ 点了 '%s' 之后**宿主消失** ⇒ 停止并报 host_died" % target["text"])
    res["host_died"] = not alive
    return res


def watch_once(apply: bool, max_actions: int) -> dict:
    wins = survey()
    acted: list[dict] = []
    for w in wins:
        if len(acted) >= max_actions:
            break
        if w["kind"] not in ("dismissable", "dangerous"):
            continue
        r = handle(w, apply)
        acted.append(r)
        if r.get("host_died"):
            break                                    #: ★ 出事了就不再动第二个
    return {"surveyed": wins, "acted": acted}


def main() -> int:
    ap = argparse.ArgumentParser(description="SolidWorks 系窗口看门狗（★ 默认 dry-run）")
    ap.add_argument("--apply", action="store_true", help="真的点按钮（默认只看不点）")
    ap.add_argument("--watch", action="store_true", help="常驻循环")
    ap.add_argument("--interval", type=float, default=3.0, help="循环间隔秒")
    ap.add_argument("--duration", type=float, default=0.0, help="总时长秒（0=不限）")
    ap.add_argument("--max-actions", type=int, default=5, help="单轮最多点几次")
    ap.add_argument("--json", type=str, default="", help="把结果写到该 JSON 路径")
    #: ★★ 测试用：扫**所有**进程的 #32770 对话框（★ 默认关 —— 生产模式只碰目标进程）。
    #:   用途：造一个**真**对话框来验证"分类 + 点击"逻辑，而不必拿 SolidWorks 冒险。
    ap.add_argument("--any-process", action="store_true",
                    help="★ 测试用：不限制进程（会碰非 SolidWorks 的对话框！）")
    args = ap.parse_args()
    ANY_PROCESS[0] = bool(args.any_process)

    print("SolidWorks 窗口看门狗 · 目标进程 %s" % (", ".join(TARGET_PROCESSES),))
    print("  模式: %s%s" % ("APPLY（真点）" if args.apply else "dry-run（只看不点）",
                          " · watch" if args.watch else ""))
    log: list[dict] = []
    t0 = time.time()
    try:
        while True:
            r = watch_once(args.apply, args.max_actions)
            log.append({"at": time.strftime("%H:%M:%S"), **r})
            for w in r["surveyed"]:
                mark = {"main_frame": " ", "dismissable": "✓", "unknown": "?",
                        "dangerous": "⚠"}.get(w["kind"], " ")
                print("  %s [%s] %s%s · %s | 按钮=%s"
                      % (mark, w["process"], w["cls"], "",
                         (w["title"] or "")[:36], [b["text"] for b in w["buttons"]][:4]))
            for a in r["acted"]:
                print("     ⇒ %s" % a["action"])
            if not args.watch:
                break
            if args.duration and (time.time() - t0) >= args.duration:
                break
            time.sleep(max(0.5, args.interval))
    except KeyboardInterrupt:
        print("  （被打断）")

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
        print("  日志: %s" % args.json)
    n_dismiss = sum(1 for e in log for a in e["acted"] if a.get("kind") == "dismissable")
    n_danger = sum(1 for e in log for w in e["surveyed"] if w["kind"] == "dangerous")
    print("  小计：可关框 %d · ⚠ 需人工的框 %d · 轮次 %d" % (n_dismiss, n_danger, len(log)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

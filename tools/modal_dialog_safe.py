"""★ **不阻塞的弹窗检测**：在**有硬时限的子进程**里跑 `collect_dialogs`，超时也能报出"发现弹窗"。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/modal_dialog_safe.py
# 定位:   ★ 2026-10-02（轮 375）**用户当场撞见弹窗而自动化没发现** —— 先修这个。
# 官方依据: 不适用（★ 用 Win32 `EnumWindows` / `EnumChildWindows` / GDI `BitBlt` 与子进
#           程超时）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
# ★ 真机诊断（★ 弹窗在屏幕上时逐步计时，**每一步都快**）：
#   EnumWindows（列举 #32770）   ⇒ 0.00 s
#   GetWindowRect / GetWindowDC  ⇒ 0.00 s
#   BitBlt（★ 代替 PrintWindow） ⇒ **0.01 s** ✔
#   EnumChildWindows（子控件）   ⇒ 0.01 s · 9 个（含 `Button 是` / `Button 否`）
# ★★ **而 `collect_dialogs()` 整体挂过 >300 s**（★ 用户撞见那次）⇒
#   ★ 与其继续猜"卡在哪一行"，**正解是让"卡"在结构上不可能** ——
#   ★★ 放进子进程 + 硬时限：★ 枚举快 ⇒ 即使取证卡住，超时也能回"发现弹窗（取证超时）"，
#     ★ 而**不是一动不动**。★ 与事实 53 同族：★ 同一个不确定的阻塞点，
#     试第 N 种写法都不如**给一个外部时限**可靠。
# ★★ 另修一处**真因**：`modal_dialog_forensics._screenshot` 原来只用 `PrintWindow`，
#   而它**向目标窗口发消息**请其自绘 ⇒ ★ **模态对话框在自己的消息循环里等用户** ⇒ **挂住**。
#   ⇒ 已改用 **`BitBlt`（只从屏幕 DC 拷像素、不发消息）**，★ 实测 **0.01 s** 拿到内容。

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOLS = REPO_ROOT / "tools"

_CHILD = r"""
import json, sys
sys.path[:0] = [r"{tools}", r"{scripts}"]
import modal_dialog_forensics as MF
pack = MF.collect_dialogs()
print("@@RESULT@@" + json.dumps({{"count": pack.get("count"), "pid": pack.get("pid"),
      "dialogs": [{{"title": d.get("title"), "class": d.get("class"),
                    "controls": d.get("controls"),
                    "content_present": d.get("screenshot_content_present"),
                    "stats": d.get("screenshot_stats")}} for d in (pack.get("dialogs") or [])]}},
      ensure_ascii=False))
"""


def collect_dialogs_safe(timeout: float = 15.0, target=None) -> dict:
    """带硬时限的弹窗检测：回 `{count, pid, dialogs, timed_out, note}`，**永不阻塞调用方**。"""
    code = _CHILD.format(tools=TOOLS, scripts=REPO_ROOT / "scripts")
    try:
        proc = subprocess.run([sys.executable, "-u", "-c", code], check=False,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, cwd=str(REPO_ROOT),
                              stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"count": None, "pid": None, "dialogs": [], "timed_out": True,
                "note": "★ 取证超时（枚举本身是快的 ⇒ 卡的是截图/取控件那一步）；"
                        "★ 调用方应判定『有弹窗』并处置，而不是继续等。"}
    out = proc.stdout or ""
    marker = "@@RESULT@@"
    if marker not in out:
        return {"count": None, "pid": None, "dialogs": [], "timed_out": False,
                "note": "★ 子进程没给出结果（stderr: %s）" % (proc.stderr or "")[-160:]}
    data = json.loads(out.split(marker, 1)[1].splitlines()[0])
    data["timed_out"] = False
    return data


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=15.0)
    args = ap.parse_args()
    r = collect_dialogs_safe(timeout=args.timeout)
    print(json.dumps(r, ensure_ascii=False, indent=1)[:1500])
    print("  ⇒ %s" % ("没有弹窗" if r.get("count") == 0
                     else "★ **发现弹窗**（★ count=%s · timed_out=%s）"
                          % (r.get("count"), r.get("timed_out"))))
    return 0 if r.get("count") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

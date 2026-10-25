"""后台连拍：每隔几秒给 SolidWorks 窗口截一张 —— 录下用户人工操作的**过程**。

## 为什么连拍而不是只拍首尾

用户手动做一个配合时，中途可能出现：
- 「配合」PropertyManager 停在某个状态（能看出 SolidWorks 期待什么类型的实体）
- 一个我从未见过的弹框（`CommandInProgress=True` 时被我抑制掉了）
- 选中集里实际的实体类型

★ 只拍首尾会漏掉这些；连拍能事后一帧帧看。

用法：
```
python -B tools/sw_snapshot_loop.py --seconds 180 --interval 3
→ output/shots/seq/000.png 001.png ...
```
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R / "tools"))

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 连拍）
# 文件:   tools/sw_snapshot_loop.py
# 定位:   录下用户**人工操作过程**（每 N 秒一张），事后逐帧看界面状态。
#          起因：配合那条一直盲试返回值；`CommandInProgress=True` 会把弹框抑制掉，
#          等于把我唯一的现场证据也压掉了。
# 官方依据: 不适用（复用 `sw_screenshot.capture` 的 `PrintWindow`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from sw_screenshot import capture, find_sw_window  # noqa: E402


def main() -> int:
    seconds = 180.0
    interval = 3.0
    if "--seconds" in sys.argv:
        seconds = float(sys.argv[sys.argv.index("--seconds") + 1])
    if "--interval" in sys.argv:
        interval = float(sys.argv[sys.argv.index("--interval") + 1])

    out_dir = R / "output" / "shots" / "seq"
    out_dir.mkdir(parents=True, exist_ok=True)
    #: 清掉上一轮
    for old in out_dir.glob("*.png"):
        old.unlink()

    hwnd = find_sw_window()
    if not hwnd:
        print("★ 找不到 SolidWorks 主窗口")
        return 2
    print("开始连拍：hwnd=%s · %.0f 秒 · 每 %.0f 秒一张 → %s"
          % (hwnd, seconds, interval, out_dir))

    n = 0
    t0 = time.time()
    while time.time() - t0 < seconds:
        ok, w, h, err = capture(hwnd, out_dir / ("%03d.png" % n))
        if ok:
            n += 1
        else:
            print("  #%03d 失败：%s" % (n, err))
        time.sleep(interval)
    print("连拍结束：共 %d 张" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

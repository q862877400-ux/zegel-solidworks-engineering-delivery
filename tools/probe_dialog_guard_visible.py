"""把 SolidWorks 设为可见，然后再弹一次消息框 —— 这次它应该真的出现在屏幕上。

## 为什么

自测第一版 0.7 秒就返回 `ret=4`（`swMbHitOk`），而监控日志里**没有**这条文本
⇒ 不是监控点的 ⇒ 说明**框根本没显示**。

查到根因：`ISldWorks.Visible = False` —— 会话的 SolidWorks **被隐藏了**
（多半是之前某个后台跑法设的）。隐藏状态下 `SendMsgToUser2` 无法把框显示给用户，
SolidWorks 直接回 `OK`。

★ 这也解释了「为什么用户看到的只有 Rx 窗口」：Rx 是**独立进程**（`SLDEXITAPP.exe`），
  主窗口隐藏**管不住它**。

## 本脚本

① 读 `Visible` 原值 → ② 置 True → ③ 弹框（等监控点）→ ④ 复原原值。
★ 复原是纪律：**不要留下被改过的会话状态**。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 弹窗监控自测 · 可见版）
# 文件:   tools/probe_dialog_guard_visible.py
# 定位:   上一版自测 0.7 秒返回 `swMbHitOk`，而监控日志无该文本 ⇒ 框没显示。
#          查明 `ISldWorks.Visible = False`（会话被隐藏）⇒ 隐藏时消息框无法显示、自动回 OK。
#          本版先置可见再弹框，验监控能否真的点掉；跑完**复原** Visible。
# 官方依据: C:\swapi\types\ISldWorks\SendMsgToUser2.md（3 参，Returns 为
#          swMessageBoxResult_e 的按钮值）· enums\swMessageBoxResult_e.md（swMbHitOk = 4）·
#          enums\swMessageBoxIcon_e.md（swMbInformation = 2）·
#          enums\swMessageBoxBtn_e.md（swMbOk = 2）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

TEXT = "sw_guard 自测：这个框应当被常驻监控自动点掉"
SW_MB_INFORMATION = 2
SW_MB_OK = 2


def main() -> int:
    ev: dict = {"probe": "dialog-guard-visible", "text": TEXT}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn

        was_visible = bool(sw.Visible)
        ev["visible_before"] = was_visible
        print("① Visible 原值 = %s" % was_visible)

        if not was_visible:
            sw.Visible = True
            time.sleep(1.0)
        ev["visible_now"] = bool(sw.Visible)
        print("② Visible 现 = %s" % ev["visible_now"])

        print("③ 弹框（等常驻监控来点）…")
        t0 = time.time()
        ret = get_com_member(sw, "SendMsgToUser2", TEXT, SW_MB_INFORMATION, SW_MB_OK)
        dt = time.time() - t0
        ev["return"] = int(ret) if ret is not None else None
        ev["elapsed_s"] = round(dt, 1)
        #: `swMessageBoxResult_e`：4 = swMbHitOk
        ev["hit_ok"] = ev["return"] == 4
        print("④ 返回 %r（4=OK）· 耗时 %.1f 秒" % (ret, dt))

        ev["ok"] = bool(ev["hit_ok"] and dt >= 1.0)
        ev["conclusion"] = (
            "★ 框显示了并在 %.1f 秒被点掉（`swMbHitOk`）" % dt
            if ev["ok"]
            else "★ 结论不确定：ret=%r 耗时 %.1f 秒" % (ev["return"], dt)
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-800:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            try:
                if "was_visible" in ev and not ev["was_visible"]:
                    sw.Visible = False
                    ev["visible_restored"] = True
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        dest = R / "output" / "dialog-guard-visible.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())

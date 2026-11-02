"""★ 弹窗监控的自测：让 SolidWorks **自己弹一个真消息框**，看常驻监控能否点掉。

## 为什么要这个

用户报「一堆 `SOLIDWORKS Rx` 窗口被唤醒」。查证结果：

- 监控组件是 `tools/sw_dialog_watch.py`（常驻）+ `tools/sw_guard.py`（扫描/处置）
- 它**确实在跑**（PID 6120，已跑 10 小时）
- 它也**确实抓到了**那些窗口，判为 `mode=auto`（「只有一个语义明确的确认按钮 ['确定']」）
- 但日志里 `SLDEXITAPP.exe` 有 **135,011 行**，同一 PID 每 2 秒一次：
  `title=SOLIDWORKS Design 错误报告` / `在尝试发送客户体验改善计划数据时发生错误。`
  ⇒ **点掉 → 它立刻再弹**，循环了 13 万次。

⇒ 所以问题不是「没监控」，而是：
  ① 这类弹窗**会立刻重弹**（CEIP 遥测发送失败，网络不通）；
  ② 监控日志**没有去重**，同一弹窗每 2 秒写一行（254 MB）。

## 本脚本做什么

用官方 `ISldWorks.SendMsgToUser2(Message, Icon, Buttons)` 让 SolidWorks 弹一个**真消息框**
（`swMbInformation=2` + `swMbOk=2`），然后**阻塞等待**：

- 若常驻监控点掉了它 ⇒ 本脚本立即返回，`elapsed` 秒数小
- 若没人点 ⇒ 脚本会一直阻塞到 `sw_guard` 的硬超时

★ 这就是「触发一个弹窗 → 由监控关掉」的端到端证据，且**不必 crash SolidWorks**。

## 官方依据

`C:\\swapi\\types\\ISldWorks\\SendMsgToUser2.md`（3 参）·
`enums\\swMessageBoxIcon_e.md`（`swMbInformation = 2`）·
`enums\\swMessageBoxBtn_e.md`（`swMbOk = 2`）
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
# 仓库:   本项目自身（工具 · 弹窗监控自测）
# 文件:   tools/probe_dialog_guard_selftest.py
# 定位:   让 SolidWorks 自己弹一个真消息框，验证常驻弹窗监控能点掉它。
#          起因：用户报「一堆 SOLIDWORKS Rx 窗口」；查证发现监控在跑、也抓到了，
#          但 CEIP 遥测错误弹窗会**点掉即重弹**，且日志没去重。
# 官方依据: C:\swapi\types\ISldWorks\SendMsgToUser2.md（3 参）·
#          enums\swMessageBoxIcon_e.md（swMbInformation=2）·
#          enums\swMessageBoxBtn_e.md（swMbOk=2）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

TEXT = "sw_guard 自测：这个框应当被常驻监控自动点掉"
SW_MB_INFORMATION = 2
SW_MB_OK = 2


def main() -> int:
    ev: dict = {"probe": "dialog-guard-selftest", "text": TEXT}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        #: ★ 不能置 CommandInProgress=True —— 那会抑制这个框，就测不到了
        print("① 即将让 SolidWorks 弹一个真消息框（等监控来点掉）…")
        t0 = time.time()
        ret = get_com_member(sw, "SendMsgToUser2", TEXT, SW_MB_INFORMATION, SW_MB_OK)
        dt = time.time() - t0
        ev["return"] = str(ret)
        ev["elapsed_s"] = round(dt, 1)
        print("② 返回：%r · 耗时 %.1f 秒（★ 若很快返回，说明有东西点掉了它）" % (ret, dt))
        ev["dismissed_somewhere"] = dt < 20.0
        ev["ok"] = ev["dismissed_somewhere"]
        ev["conclusion"] = (
            "★ 消息框在 %.1f 秒内返回 ⇒ 被点掉了（监控或人手）" % dt
            if ev["dismissed_somewhere"]
            else "★ 消息框卡了 %.1f 秒 ⇒ 没人点它" % dt
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
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        dest = R / "output" / "dialog-guard-selftest.json"
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())

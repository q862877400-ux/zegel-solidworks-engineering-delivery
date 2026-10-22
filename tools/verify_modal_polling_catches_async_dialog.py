r"""@brief 证伪实验：证明**一次性**模态框检查**真的会漏**，而**轮询**能抓到。

## 为什么必须做这个实验（轮 168）
轮 167 把默认值改成了轮询（`settle_seconds=1.0`），但**"改了"不等于"改对了"**
（已知事实 62：负例测试是唯一的证明）。⇒ 本实验**制造出**那个盲区并**当场对比两种查法**：
```
① 后台起"会阻塞"的调用（空零件 + b_coord_input=False）⇒ 它会卡在模态框上
② 前台**立刻**用 `settle_seconds=0.0`（**一次性**，等价于改之前的 34 个调用点）查一次
③ 前台再用 `settle_seconds=1.5`（**轮询**，改之后的默认）查
⇒ ★ 预期：②报 **0**（**漏**），③报 **≥1**（**抓到**）
   ⚠ 若 ② 也报 ≥1 ⇒ 说明本实验**没造出盲区**（不是"修好了"）⇒ 要如实说
```

## ⚠ 安全
只在新零件上；收尾**轮询点掉**（兜底，防挂起）+ `CommandInProgress` 复位 + 关件不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机证伪实验）
# 文件:   tools/verify_modal_polling_catches_async_dialog.py
# 定位:   给 Spec Kit `088` 证明「轮询默认值」修掉的是**真实盲区**，不是纸面改动。
# 官方依据: Win32 `WC_DIALOG`；`ISldWorks.GetProcessID()`；`IFeatureManager.MoldUndercut
#           Detect` 的
#          `BCoordInput`（官方 md）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "modal-polling-catches.json"
)

TRIGGER = """import sys
sys.path.insert(0, r"{root}")
sys.path.insert(0, r"{root}\\scripts")
import sw_connect
from scripts import sw_mold
sys.stdout.reconfigure(encoding="utf-8")
sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
doc = sw_connect.new_document(sw, "part")
print("TRIGGER: 空零件已就绪 ⇒ 调 b_coord_input=False（会阻塞）", flush=True)
try:
    sw_mold.mold_undercut_detect(doc, b_coord_input=False, dx=0.0, dy=0.0, dz=1.0)
except Exception as exc:
    print("TRIGGER: 抛错 %s" % type(exc).__name__, flush=True)
print("TRIGGER: 调用已返回（阻塞解除）", flush=True)
try:
    t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
except Exception:
    pass
"""


def main() -> int:
    import sw_connect

    ev: dict = {}
    script = Path(Path(__file__).resolve().parents[1] / "output" / "_trigger_poll.py")
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(TRIGGER.format(root=str(ROOT)), encoding="utf-8")

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    sw_connect.dismiss_residual_dialogs(sw, settle_seconds=0.3)

    log = Path(Path(__file__).resolve().parents[1] / "output" / "_trigger_poll.log")
    proc = subprocess.Popen(
        [sys.executable, "-u", str(script)],
        stdout=log.open("w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
    )
    print("  ① 后台触发 PID=%d（会阻塞）" % proc.pid)

    #: ② **一次性**查 —— ⚠⚠ **只查一次**，而且**紧接触发之后**（不等）
    #: ⚠ 第一版这里写成"1.2 秒内循环查 19 次" ⇒ **那本身就是轮询**
    #: ⇒ 实验**没造出盲区**（命中 14/19）⇒ ★ 如实报并改成"真的只查一次"。
    #: ★ 这才是改之前那 34 个调用点的真实形态：**COM 调用返回后立即查一次**。
    d_once, w_once = sw_connect.residual_dialogs(settle_seconds=0.0)
    ev["one_shot_count"] = len(d_once)
    ev["one_shot_windows"] = w_once
    print(
        "  ② **只查一次**（紧接触发）⇒ **%d** 个框（扫了 %d 个窗口）"
        % (len(d_once), w_once)
    )

    #: ③ **轮询**查（改之后的默认）—— 也必须**制造一个只看一眼**的对照
    t0 = time.time()
    d, w = sw_connect.residual_dialogs(settle_seconds=0.0)
    ev["single_look_now"] = len(d)
    print("  ③ 此刻**只看一眼** ⇒ **%d** 个框" % len(d))
    d2, w2 = sw_connect.residual_dialogs(settle_seconds=1.5)
    ev["polled"] = len(d2)
    ev["polled_windows"] = w2
    print("  ③ **轮询 1.5 秒** ⇒ **%d** 个框（扫了 %d 个窗口）" % (len(d2), w2))

    #: ④ 点掉 + 解卡
    dismissed, _ = sw_connect.dismiss_residual_dialogs(sw, settle_seconds=1.0)
    ev["dismissed"] = dismissed
    try:
        rc = proc.wait(timeout=20)
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = None
    ev["trigger_exit"] = rc
    print("  ④ 点掉 %d 个 · 后台退出码 %s" % (dismissed, rc))

    tail = log.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-4:]
    ev["trigger_log_tail"] = tail
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── 触发进程输出 ──")
    for l in tail:
        print("    %s" % l[:96])
    print()
    #: ★ 判据：**一次性**必须**漏**（0），而**轮询**必须**抓到**（≥1）
    blind_missed = ev["one_shot_count"] == 0
    polling_caught = len(d2) >= 1
    ev["blind_missed"] = blind_missed
    ev["polling_caught"] = polling_caught
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        "  ★ 一次性漏掉: %s · 轮询抓到: %s ⇒ %s"
        % (
            blind_missed,
            polling_caught,
            "**盲区已证实，且轮询修掉了它**"
            if (blind_missed and polling_caught)
            else "⚠ 本实验**没造出盲区**（不是「修好了」）—— 如实报",
        )
    )
    print("  证据: %s" % OUT)
    return 0 if (blind_missed and polling_caught) else 1


if __name__ == "__main__":
    raise SystemExit(main())

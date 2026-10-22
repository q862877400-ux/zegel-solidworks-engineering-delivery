r"""@brief 端到端验证：**故意复现**模态框 ⇒ 验证「能发现」+「能点掉」，且**零硬编码**。

## 为什么要这么做（轮 167，用户要求）
用户原话：「**先排查为啥会触发，然后再重复看看如果又触发了怎么发现怎么点掉。禁止硬编码**」

## 三项设计（都不硬编码）
```
① 复现：用**已知根因**复现，而不是随便点 —— 根因是「第 3 参 BCoordInput=True 才用坐标输入；
   传 False 就退回『用模型已定义方向』，而空零件没定义 ⇒ 弹框」
   ⇒ 本轮**故意传 b_coord_input=False** 复现
② 发现：`sw_connect.dismiss_residual_dialogs(sw)` —— PID **由 `ISldWorks.GetProcessID()` 派生**
   （**不是**写死的 20456）· class 用 Win32 预定义对话框类 `#32770`（`WC_DIALOG`）
③ 点掉：给对话框发 `WM_COMMAND` + `IDOK`（Win32 标准命令）——
   **不看按钮叫什么（中文「确定」/ 英文 OK 都行）、不按坐标**
```

## 流程（关键：触发会**阻塞**，所以必须分进程）
```
① 后台进程：调 `mold_undercut_detect(b_coord_input=False)` ⇒ **会卡住**（模态框）
② 前台：轮询 `#32770` ⇒ 记录**第几秒**发现（证明"弹窗是异步的、一次性检查会漏"）
③ 前台：发 `WM_COMMAND(IDOK)` 点掉
④ 复核：`#32770` 归零，且**后台进程随之解卡**（证明阻塞被解除）
```

## ⚠ 安全
只在新零件上；收尾关件不保存；`CommandInProgress` 复位。

# ── 来源 ──
# 仓库:   本项目自身（真机端到端验证）
# 文件:   tools/verify_modal_dialog_lifecycle.py
# 定位:   给 Spec Kit `087` 证明「模态框能被发现并点掉」，且机制**不含硬编码**。
# 官方依据: `ISldWorks.GetProcessID()`（出厂反射）；Win32 `WC_DIALOG`/`WM_COMMAND`/`IDOK
#           `（公开常量）
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
    Path(__file__).resolve().parents[1] / "output" / "modal-dialog-lifecycle.json"
)

#: ★ **子进程脚本**（就是"故意复现"那一步）—— 写成独立文件，避免内联长文本（事实 48）
TRIGGER = """import sys, time
sys.path.insert(0, r"{root}")
sys.path.insert(0, r"{root}\\scripts")
import sw_connect
from scripts import sw_part, sw_mold
sys.stdout.reconfigure(encoding="utf-8")
sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
print("TRIGGER: 已连接", flush=True)
doc = sw_connect.new_document(sw, "part")
#: ⚠⚠⚠ **必须用空零件** —— 轮 167 实测：**有实体**的零件上 SolidWorks 能自己推断方向
#: ⇒ **不会弹框**（第一次复现因此失败：「竟然没弹框就返回了」）；
#: 而**空零件**上无方向可推断 ⇒ 才会弹「此拔模方向尚未定义。」
print("TRIGGER: 空零件已建好（**故意的**）", flush=True)
print("TRIGGER: 现在**故意**用 b_coord_input=False（退回『用模型已定义方向』）", flush=True)
try:
    #: ★ 故意触发：模型没有已定义的拔模方向 ⇒ 官方弹「此拔模方向尚未定义。」
    sw_mold.mold_undercut_detect(doc, b_coord_input=False, dx=0.0, dy=0.0, dz=1.0)
    print("TRIGGER: 竟然没弹框就返回了", flush=True)
except Exception as exc:
    print("TRIGGER: 抛错 %s: %s" % (type(exc).__name__, str(exc)[:80]), flush=True)
print("TRIGGER: 调用返回 ⇒ 阻塞已解除", flush=True)
try:
    t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
    if t:
        sw.CloseDoc(t)
except Exception:
    pass
"""


def main() -> int:
    ev: dict = {}
    script = Path(Path(__file__).resolve().parents[1] / "output" / "_trigger_dialog.py")
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text(TRIGGER.format(root=str(ROOT)), encoding="utf-8")

    #: ① 先清干净，保证从零开始
    import sw_connect

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    pre, _ = sw_connect.dismiss_residual_dialogs(sw, settle_seconds=0.3)
    print("  起手：先清一遍 ⇒ 点掉 %d 个" % pre)

    #: ② 后台起"故意触发"
    log = Path(Path(__file__).resolve().parents[1] / "output" / "_trigger_dialog.log")
    proc = subprocess.Popen(
        [sys.executable, "-u", str(script)],
        stdout=log.open("w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
    )
    print("  ② 后台触发进程 PID=%d（它会卡在模态框上）" % proc.pid)

    #: ③ **轮询**发现（记录第几秒）—— ★ 这正是「一次性检查会漏」的直接证据
    found_at = None
    t0 = time.time()
    while time.time() - t0 < 45.0:
        n_dlg, scanned = sw_connect.count_residual_dialogs(sw)  #: ★ **只读**，不点
        if n_dlg:
            found_at = time.time() - t0
            ev["found_after_seconds"] = round(found_at, 2)
            ev["found_count"] = n_dlg
            ev["scanned_windows"] = scanned
            print(
                "  ③ ★ 第 **%.2f 秒** **发现** %d 个模态框（扫了 %d 个窗口）"
                % (found_at, n_dlg, scanned)
            )
            break
        time.sleep(0.25)

    #: ④ 点掉（用同一套机制，`settle_seconds` 轮询把可能的后续弹窗也清掉）
    dismissed, scanned = sw_connect.dismiss_residual_dialogs(sw, settle_seconds=1.0)
    ev["dismissed"] = dismissed
    print("  ④ 点掉 %d 个（扫了 %d 个窗口）" % (dismissed, scanned))

    #: ⑤ 复核：对话框归零 + 后台进程解卡
    d2, _ = sw_connect.dismiss_residual_dialogs(sw, settle_seconds=0.3)
    ev["remaining_dialogs"] = d2
    try:
        rc = proc.wait(timeout=20)
        ev["trigger_exit"] = rc
        unblocked = True
    except subprocess.TimeoutExpired:
        proc.kill()
        rc = None
    ev["unblocked"] = unblocked if "unblocked" in dir() else False
    print(
        "  ⑤ 复核：剩余对话框 **%d** 个 · 后台进程退出码 %s ⇒ %s"
        % (d2, rc, "**阻塞已解除**" if rc is not None else "**仍在阻塞**")
    )

    out_txt = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
    print()
    print("  ── 触发进程的输出 ──")
    for l in out_txt.strip().splitlines()[-6:]:
        print("    %s" % l[:100])
    ev["trigger_log_tail"] = out_txt.strip().splitlines()[-6:]
    ev["pid"] = sw_connect.solidworks_process_id(sw)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  证据: %s" % OUT)
    ok = bool(found_at) and dismissed > 0 and d2 == 0 and rc is not None
    print(
        "  ── %s ──"
        % ("★ 全部成立：能复现 · 能发现 · 能点掉 · 能解卡" if ok else "⚠ 有环节没成立")
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

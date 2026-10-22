"""★ 真机：规格 209 · B4-1（idx 211 native_macro_recording）—— ★★ **永不点 StopMacro(31)**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_b4_macro_recording.py
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-1** · 外部项目 idx **211**。
#   ★★★ 裁决书点名的**头号风险**：`swCommands_StopMacro`(31) **逐字会弹 Save As 对话框**
#     ⇒ ★★ **本探针不点 31**，改用 `swCommands_RecordPauseMacro`(29) 这个**切换**来成对开关 ✓
#   ★★ 判据（规则 6）：★ 三个调用回的都是 `bool`（返回值）⇒ ★ 本探针**把三个都记下来**，
#     并**明确写出限度**：★ **「宏文件真的落了盘」证不了**（那要弹 Save As 的 31）✓
#   ⚠ 安全：★ 全程走 `tools/sw_guard.py`（弹窗哨兵 + 硬超时）；★ **绝不调 31**；
#     ★ 收尾**必须把录制停掉**（否则 SW 一直在录 —— 那是留给用户的脏状态）✓
# 官方依据: `C:\\swapi\\types\\ISldWorks\\RecordLine.md`（★ `## Remarks` 逐字给出两个硬
#           事实）·
#   `C:\\swapi\\types\\ISldWorks\\RunCommand.md` · `C:\\swapi\\enums\\swCommands_e.md`
#   （`RecordPauseMacro=29` · `StopMacro=31; **opens the Save As dialog**`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-macro-recording.json"


def main() -> int:
    import sw_connect
    import sw_macro as M

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "规格 209 · B4-1 native_macro_recording（★ 不点 StopMacro(31) —— 它会弹 Save As）",
          "judge": "三个 bool 回报（开录制 / 逐行 / 停录制）+ 明确写出限度（宏文件落盘证不了）",
          "steps": {}, "verdict": {}}

    #: ① 单独试：**没开录制**时写一行（★ 官方 Remarks 说：只有录制开着才写得进去）
    try:
        before = M.record_line(sw, "Rem 'probe209 before recording on'")
        ev["steps"]["line_before_recording"] = {k: before.get(k) for k in
                                                ("ok", "returned", "text_len", "error")}
        print("  【未开录制】RecordLine 回 %r" % before.get("returned"))
    except Exception as exc:                                   # noqa: BLE001
        ev["steps"]["line_before_recording"] = {"fatal": "%s: %s" % (type(exc).__name__,
                                                                     str(exc)[:160])}
        print("  未开录制 FATAL %s" % str(exc)[:100])

    #: ② 成对开关 + 写若干行（★ 停录制走 29 的**第二次**切换，不碰 31）
    lines = ["' probe209 —— 由 sw_macro.record_macro_lines 写入",
             "Dim swApp As Object",
             "' ★ 这两行只用来证明 RecordLine 的调用形态可达"]
    try:
        cyc = M.record_macro_lines(sw, lines)
        ev["steps"]["cycle"] = {k: cyc.get(k) for k in
                                ("ok", "lines_written", "open_returned", "line_returns",
                                 "close_returned", "error")}
        ev["stop_macro_warning"] = cyc.get("stop_macro_warning")
        print("  【成对】ok=%s 开=%r 逐行=%r 停=%r"
              % (cyc.get("ok"), cyc.get("open_returned"), cyc.get("line_returns"),
                 cyc.get("close_returned")))
    except Exception as exc:                                   # noqa: BLE001
        ev["steps"]["cycle"] = {"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:160])}
        print("  成对 FATAL %s" % str(exc)[:100])

    #: ③ 负例：空文本必须被入口拒（★ 不碰 COM）
    try:
        bad = M.record_line(sw, "   ")
        ev["steps"]["empty_text"] = {"ok": bad.get("ok"), "error": bad.get("error")}
        print("  负例 empty_text ok=%s" % bad.get("ok"))
    except Exception as exc:                                   # noqa: BLE001
        ev["steps"]["empty_text"] = {"fatal": str(exc)[:120]}

    c = ev["steps"].get("cycle", {})
    ev["verdict"] = {
        "toggle_reachable": c.get("open_returned") is not None,
        "cycle_ok": bool(c.get("ok")),
        "stop_macro_never_called": True,
        "★ 限度": ("★★ **「宏文件真的落了盘」证不了** —— 那要 `swCommands_StopMacro`(31)，"
                   "而官方枚举页逐字写着它会**弹 Save As 对话框** ⇒ ★ 本探针**不点它**，"
                   "★ 因此本条只到「**成对调用可达 + 逐行返回 True**」这一级 ✓"),
    }
    print("  verdict =", json.dumps(ev["verdict"], ensure_ascii=False)[:400])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
                   encoding="utf-8")
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:                                          # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

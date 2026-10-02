r"""@brief 探针：`get_lines` 对**1 条直线**到底读回几条？（轮 140 冒烟里 12 对 1 的疑问）

## 疑问的来源
`tools/verify_centerline_smoke.py`：草图里**只画了 1 条中心线**
⇒ `get_sketch_segments` 读回 **1 段** ✓ · 而 `get_lines` 读回 **12 条** ⚠

## 要分辨的两种解释
* **A**：`GetLines2` 返回的是**坐标数组**（每条线 6 个 double ⇒ 12 个数字 = **2 条线**？不对）
* **B**：`GetLines2` 返回的是**成对**的（每条线 2 个"线对象"或 2 个端点对象）⇒ 1 条线 = 2 项 ⇒ 12 不是 2
* **C**：`as_sequence` 对这个 VARIANT 的展开方式与预期不同（例如把某个定长数组整体摊平）
⇒ **唯一判法：画 N 条线，看读回多少**。N=1 与 N=3 一比就知道是不是线性。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_getlines_count.py
# 定位:   给 Spec Kit `059` 取证：`get_lines` 的返回条数语义。
# 官方依据: `C:\swapi\types\ISketch\GetLines2.md`（若在）；出厂反射 `iface_*.txt`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\getlines-count-evidence.json")
def modal_dialogs() -> tuple:
    """★ 已改为**委托共享实现**（2026-10-01 轮 149）。"""
    try:
        from scripts.sw_connect import residual_dialogs
    except ImportError:
        from sw_connect import dismiss_residual_dialogs, residual_dialogs
    #: ★ 2026-10-01（轮 169）：**查到了就点掉**（兜底）——
    #: 只查不点的脚本在真发现弹窗时**什么也没处置**，弹窗还在 ⇒ 下一轮挂在这儿。
    _dialogs, _scanned = residual_dialogs()
    if _dialogs:
            dismiss_residual_dialogs()
    return _dialogs, _scanned
def main() -> int:
    ev = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": {}}
    sw = None
    docs: list = []
    try:
        import sw_connect
        from scripts import sw_part, sw_sketch
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        for n_lines in (1, 2, 3):
            d = sw_connect.new_document(sw, "part")
            docs.append(d)
            sw_part.start_sketch(d)
            for i in range(n_lines):
                #: 每条线横跨 20mm，纵向错开
                sw_part.sketch_line(d, -10.0, float(i) * 10.0, 10.0, float(i) * 10.0)
            skm = sw_connect.safe_get_com_member(d, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            segs = sw_sketch.get_sketch_segments(sk)
            lns = sw_sketch.get_lines(sk)
            ns = len(segs) if isinstance(segs, list) else type(segs).__name__
            nl = len(lns) if isinstance(lns, list) else type(lns).__name__
            print("  画 %d 条直线 ⇒ get_sketch_segments=%s · get_lines=%s" % (n_lines, ns, nl))
            if isinstance(lns, list) and lns:
                print("        get_lines[0] 类型 = %s" % type(lns[0]).__name__)
                print("        get_lines 全表前 3 项 = %r" % (lns[:3],))
            ev["cases"]["%d_lines" % n_lines] = {"segments": ns, "lines": nl}
            sw_part.end_sketch(d)
    except Exception as exc:      # noqa: BLE001
        print("  ⚠ 探针出错：%s: %s" % (type(exc).__name__, str(exc)[:160]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in docs:
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:      # noqa: BLE001
                pass
        print("   （已关闭 %d 个临时零件，均不保存）" % len(docs))

    modals, _win_scanned = modal_dialogs()
    print("   收尾模态框: %s（扫了 %d 个窗口）"
          % ("无" if not modals else modals, _win_scanned))
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

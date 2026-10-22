r"""@brief 探针：`get_sketch_slots` / `get_sketch_points` 的形状（轮 142）。

## 为什么这两条能测
* `get_sketch_slots` —— `sw_part.sketch_slot` **存在**（`CreateSketchSlot`）⇒ 画得出。
* `get_sketch_points` —— ★ **不用新函数**：一条**直线**的**两个端点**本身就是草图点
  ⇒ 画 1 条直线 ⇒ `get_sketch_points` 应报出**端点**（正好也是"拿强判据量已有取法"的做法）。

## 判法（与 `060` 同一套：**定量**，不是"非空"）
```
画 N 个某类实体 ⇒ 该取法返回几个元素、元素什么类型
   count == N        ⇒ 对象列表
   count == N × k    ⇒ ★ 数值数组（每个 k 个 float）
   count == 0/None   ⇒ 取不到（另记）
```

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_slot_and_point_shapes.py
# 定位:   给 Spec Kit `061` 取证：`get_sketch_slots` / `get_sketch_points` 的返回形状。
# 官方依据: 出厂反射 `iface_*.txt` 的 `ISketch` 段；⚠ 官方文档**未写**返回结构
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "slot-point-shapes.json")


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


def measure(sw_sketch, sk, getter):
    fn = getattr(sw_sketch, getter, None)
    if fn is None:
        return None, "取法不存在"
    try:
        got = fn(sk)
    except Exception as exc:  # noqa: BLE001
        return None, "EXC: %s: %s" % (type(exc).__name__, str(exc)[:60])
    if isinstance(got, list):
        return len(got), (type(got[0]).__name__ if got else "—")
    return None, "返回类型 %s（不是 list）" % type(got).__name__


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": {}}
    sw = None
    docs: list = []
    try:
        import sw_connect
        from scripts import sw_part, sw_sketch

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        print(
            "  %-16s %-6s %-22s %-8s %s"
            % ("画了什么", "个数", "取法", "元素数", "元素类型/判定")
        )

        # ══ ① 槽口：画 1 个 / 2 个 ══════════════════════════════════
        for n in (1, 2):
            d = sw_connect.new_document(sw, "part")
            docs.append(d)
            sw_part.start_sketch(d)
            drawn = 0
            for i in range(n):
                y = float(i) * 30.0
                try:
                    sw_part.sketch_slot(d, -20.0, y, 20.0, y, 5.0)
                    drawn += 1
                except Exception as exc:  # noqa: BLE001
                    print("     ⚠ 第 %d 个槽口画不出: %s" % (i, str(exc)[:60]))
                    break
            skm = sw_connect.safe_get_com_member(d, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            segs = sw_sketch.get_sketch_segments(sk)
            truth = len(segs) if isinstance(segs, list) else -1
            cnt, et = measure(sw_sketch, sk, "get_sketch_slots")
            print(
                "  %-16s %-6d %-22s %-8s %s（真值 segments=%d）"
                % ("槽口", drawn, "get_sketch_slots", cnt, et, truth)
            )
            ev["cases"]["slot_n%d" % drawn] = {
                "drawn": drawn,
                "segments": truth,
                "count": cnt,
                "element": et,
            }
            sw_part.end_sketch(d)
            t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
            docs.remove(d)

        # ══ ② 草图点：用一条直线的两个端点（**不新增函数**）═════════
        for n in (1, 2):
            d = sw_connect.new_document(sw, "part")
            docs.append(d)
            sw_part.start_sketch(d)
            for i in range(n):
                y = float(i) * 30.0
                sw_part.sketch_line(d, -20.0, y, 20.0, y)
            skm = sw_connect.safe_get_com_member(d, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            segs = sw_sketch.get_sketch_segments(sk)
            truth = len(segs) if isinstance(segs, list) else -1
            cnt, et = measure(sw_sketch, sk, "get_sketch_points")
            print(
                "  %-16s %-6d %-22s %-8s %s（真值 segments=%d）"
                % ("直线(端点即草图点)", n, "get_sketch_points", cnt, et, truth)
            )
            ev["cases"]["point_from_%d_line" % n] = {
                "lines": n,
                "segments": truth,
                "count": cnt,
                "element": et,
            }
            sw_part.end_sketch(d)
            t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
            docs.remove(d)

        # ══ ③ 顺带：用户点 `get_user_points`（同样用直线端点）═══════
        d = sw_connect.new_document(sw, "part")
        docs.append(d)
        sw_part.start_sketch(d)
        sw_part.sketch_line(d, -20.0, 0.0, 20.0, 0.0)
        sk = sw_connect.safe_get_com_member(
            sw_connect.safe_get_com_member(d, "SketchManager"), "ActiveSketch"
        )
        for g in ("get_user_points", "get_polylines", "get_sketch_regions"):
            cnt, et = measure(sw_sketch, sk, g)
            print("  %-16s %-6d %-22s %-8s %s" % ("（顺带）", 1, g, cnt, et))
            ev["cases"]["misc_%s" % g] = {"count": cnt, "element": et}
        sw_part.end_sketch(d)
        t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
        if t:
            sw.CloseDoc(t)
        docs.remove(d)
    except Exception as exc:  # noqa: BLE001
        print("  ⚠ 探针出错：%s: %s" % (type(exc).__name__, str(exc)[:160]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        for d in docs:
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass

    modals, _win_scanned = modal_dialogs()
    print()
    print(
        "   收尾模态框: %s（扫了 %d 个窗口）"
        % ("无" if not modals else modals, _win_scanned)
    )
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

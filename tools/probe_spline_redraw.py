r"""@brief 探针：样条到底是"没建成"还是"建成了但没重绘"？（轮 141 的第二问）

## 官方的说法（`C:\swapi\types\ISketchManager\CreateSpline2.md`）
> This method does not work with `AddToDB` or `DisplayWhenAdded`.
> It **always adds the spline directly to the database** (as if `AddToDB(True)`),
> and **you must redraw your document window to see the entities** that you added.

⇒ ★ 那么 `get_sketch_segments` 返回 0 就**不该**发生（它在数据库里）——
**除非** ① `CreateSpline2` 真失败了，或 ② 需要**重绘**后 `GetSketchSegments` 才更新。

## 本探针做四件事
1. `CreateSpline2`（现状用的那个）⇒ 数段数；
2. **重绘**（`IModelView::GraphicsRedraw2` / `GraphicsRedraw`）⇒ **再数**；
3. 换 `CreateSpline`（**1 参**的旧版，未废弃标注）⇒ 数段数；
4. 对照直线（证明流程本身没问题）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_spline_redraw.py
# 定位:   给 Spec Kit `060` 取证：样条是"未建成"还是"未重绘"。
# 官方依据: `C:\swapi\types\ISketchManager\CreateSpline2.md`（Remarks 那段）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import array
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

OUT = Path(r"D:\AI\SW\output\spline-redraw-evidence.json")
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
def count(sw_sketch, sk):
    try:
        segs = sw_sketch.get_sketch_segments(sk)
        return len(segs) if isinstance(segs, list) else -1
    except Exception as exc:      # noqa: BLE001
        return "EXC:%s" % str(exc)[:40]


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": {}}
    sw = None
    docs: list = []
    pts = [(-20.0, 0.0), (-7.0, 8.0), (7.0, -8.0), (20.0, 0.0)]
    arr = array.array("d")
    for x, y in pts:
        arr.extend([x, y, 0.0])
    try:
        import sw_connect
        from scripts import sw_part, sw_sketch
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        d = sw_connect.new_document(sw, "part")
        docs.append(d)
        sw_part.start_sketch(d)
        skm = sw_connect.safe_get_com_member(d, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")

        #: ① CreateSpline2（现行模块用的）
        try:
            r2 = skm.CreateSpline2(arr, False)
            t2 = type(r2).__name__
        except Exception as exc:      # noqa: BLE001
            t2 = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:70])
        n_a = count(sw_sketch, sk)
        print("  ① CreateSpline2         返回=%-12s ⇒ 段数 = %s" % (t2, n_a))

        #: ② 重绘后再数（官方说"必须重绘才看得见"）
        redrawn = "—"
        try:
            #: ⚠ `ActiveView` 是**属性**（不是方法）—— 上一版当方法调，报
            #: `EXC:SldWorks.Application.ActiveView` ⇒ **那次重绘没发生**，
            #: 所以"官方说必须重绘"这条解释**当时并未被排除**。
            #: ⚠ `sw.ActiveView` 在迟到绑定下**没有**（`AttributeError`）⇒
            #: 按官方走 `IModelDoc2::ActiveView`（即 `ActiveDoc.ActiveView`）。
            #: ⚠ 这是**第二次**试（事实 53：同一处不试第三种）。
            mv = sw.ActiveDoc.ActiveView
            for meth in ("GraphicsRedraw2", "GraphicsRedraw"):
                f = getattr(mv, meth, None)
                if f is None:
                    continue
                f()
                redrawn = meth
                break
            if redrawn == "—":
                redrawn = "（两个重绘方法都没有）"
        except Exception as exc:      # noqa: BLE001
            redrawn = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:60])
        n_b = count(sw_sketch, sk)
        print("  ② 重绘（%s）后           ⇒ 段数 = %s" % (redrawn, n_b))

        #: ③ 换 `CreateSpline`（1 参的旧版）
        f1 = getattr(skm, "CreateSpline", None)
        if f1 is None:
            t1 = "**迟到绑定里没有这个成员**"
        else:
            try:
                r1 = f1(arr)
                t1 = type(r1).__name__
            except Exception as exc:      # noqa: BLE001
                t1 = "EXC: %s: %s" % (type(exc).__name__, str(exc)[:70])
        n_c = count(sw_sketch, sk)
        print("  ③ CreateSpline          返回=%-12s ⇒ 段数 = %s" % (t1, n_c))

        ev["cases"] = {"create_spline2": {"return": t2, "segments": n_a},
                       "after_redraw": {"method": redrawn, "segments": n_b},
                       "create_spline": {"return": t1, "segments": n_c}}

        #: 对照：直线（证明流程没问题）
        d2 = sw_connect.new_document(sw, "part")
        docs.append(d2)
        sw_part.start_sketch(d2)
        sw_part.sketch_line(d2, -10.0, 0.0, 10.0, 0.0)
        sk2 = sw_connect.safe_get_com_member(
            sw_connect.safe_get_com_member(d2, "SketchManager"), "ActiveSketch")
        print("  ④ 对照·直线                            ⇒ 段数 = %s" % count(sw_sketch, sk2))
        ev["cases"]["control_line"] = count(sw_sketch, sk2)
        sw_part.end_sketch(d2)
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
    print()
    print("   收尾模态框: %s（扫了 %d 个窗口）"
          % ("无" if not modals else modals, _win_scanned))
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

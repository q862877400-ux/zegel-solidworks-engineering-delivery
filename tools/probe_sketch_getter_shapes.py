r"""@brief 探针：**所有**按类型取法的返回形状 —— 是「对象列表」还是「数值数组」？

## 起因（2026-10-01 轮 140）
`get_lines` 的 docstring 写「直线」，实测却是**数值数组**（每条直线 **12 个 `float`**，
画 1/2/3 条 ⇒ 12/24/36）。★ 那是一个**孤例还是通例**？本轮**逐个量**。

## 判法（强判据，不是「非空」）
```
① 画 N 个某类实体（N = 1, 2）；
② `get_sketch_segments` 给出**真值**（几个实体）；
③ 该类型的取法返回**几个元素**、**元素是什么类型**；
④ 判：
     count == N            ⇒ **对象列表**（正常）
     count == N × k        ⇒ **数值数组**（每条 k 个数字）⇒ ★ 与 `get_lines` 同类
     count == 0 或 None    ⇒ 取法拿不到该类型（另记）
```

## ⚠ 安全
**只在新零件上跑**、只进草图、不拉伸；收尾**关件不保存** + **查模态框**（事实 64）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_sketch_getter_shapes.py
# 定位:   给 Spec Kit `060` 取证：`sw_sketch` 各按类型取法的返回形状。
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "sketch-getter-shapes.json")
#: 每种实体：怎么画第 i 个（i 从 0 起），以及要量哪几个取法
CASES = [
    ("line", ["get_lines"], lambda part, i: _line(part, i)),
    ("arc", ["get_arcs"], lambda part, i: _arc(part, i)),
    ("ellipse", ["get_ellipses"], lambda part, i: _ellipse(part, i)),
    ("spline", ["get_splines"], lambda part, i: _spline(part, i)),
    #: ⚠ **`point` 那一档去掉了**：`sw_part` 没有点构造函数
    #: （反射里 `ISketchManager.CreatePoint(Double,Double,Double) -> SketchPoint` 存在，
    #:  但**本模块尚未包装**）⇒ 强行测会得到"画不出来"，**不是取法的问题**。
]


def _line(part, i):
    from scripts import sw_part
    y = float(i) * 20.0
    return sw_part.sketch_line(part, -10.0, y, 10.0, y)


def _arc(part, i):
    from scripts import sw_part
    y = float(i) * 20.0
    #: 圆心 (0,y)、起点 (-10,y)、终点 (10,y)、逆时针
    return sw_part.sketch_arc(part, 0.0, y, -10.0, y, 10.0, y, 1)


def _ellipse(part, i):
    from scripts import sw_part
    y = float(i) * 20.0
    return sw_part.sketch_ellipse(part, 0.0, y, 20.0, y, 0.0, y + 10.0)


def _spline(part, i):
    from scripts import sw_part
    y = float(i) * 20.0
    #: 4 个控制点
    return sw_part.sketch_spline(part, [(-20.0, y), (-7.0, y + 8.0),
                                        (7.0, y - 8.0), (20.0, y)])


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
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": {}}
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

        print("  %-10s %-6s %-22s %-8s %-10s %s" % ("类型", "画了", "取法", "元素数", "元素类型", "判定"))
        for kind, getters, draw in CASES:
            for n in (1, 2):
                d = sw_connect.new_document(sw, "part")
                docs.append(d)
                drawn = 0
                sw_part.start_sketch(d)
                for i in range(n):
                    try:
                        draw(d, i)
                        drawn += 1
                    except Exception as exc:      # noqa: BLE001
                        print("  %-10s ⚠ 第 %d 个画不出来: %s" % (kind, i, str(exc)[:60]))
                        break
                skm = sw_connect.safe_get_com_member(d, "SketchManager")
                sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
                try:
                    segs = sw_sketch.get_sketch_segments(sk)
                    truth = len(segs) if isinstance(segs, list) else -1
                except Exception:      # noqa: BLE001
                    truth = -1
                for g in getters:
                    fn = getattr(sw_sketch, g, None)
                    try:
                        got = fn(sk) if fn else None
                    except Exception as exc:      # noqa: BLE001
                        got = "EXC:%s" % str(exc)[:40]
                    if isinstance(got, list):
                        cnt = len(got)
                        et = type(got[0]).__name__ if got else "—"
                    else:
                        cnt, et = (got if isinstance(got, int) else -1), str(type(got).__name__)
                    if cnt == drawn:
                        verdict = "**对象列表**（正常）"
                    elif drawn and isinstance(cnt, int) and cnt > 0 and cnt % drawn == 0:
                        verdict = "★ **数值数组**：每条 %d 个" % (cnt // drawn)
                    elif cnt == 0:
                        verdict = "⚠ 取不到该类型"
                    else:
                        verdict = "? 需人工看"
                    print("  %-10s %-6d %-22s %-8s %-10s %s"
                          % (kind, drawn, g, cnt, et, verdict))
                    ev["cases"]["%s_n%d_%s" % (kind, drawn, g)] = {
                        "drawn": drawn, "segments": truth, "count": cnt,
                        "element_type": et, "verdict": verdict}
                sw_part.end_sketch(d)
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
                docs.remove(d)
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

    modals, _win_scanned = modal_dialogs()
    print()
    print("   收尾模态框: %s（扫了 %d 个窗口）"
          % ("无" if not modals else modals, _win_scanned))
    ev["modal_dialogs"] = modals
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("   证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

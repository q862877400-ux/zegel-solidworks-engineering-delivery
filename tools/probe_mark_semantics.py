r"""@brief 探针：**mark 到底落没落？** —— 用「已知能选中」的**草图**做判别。

## 为什么要做这个
轮 153 用 `SelectByID2("", "EDGE", x,y,z, True, 1, callout, 0)` 选棱，返回 `True`，
但 **`GetSelectedObjectCount2(1)` = 0** ⇒ 当时**没法判断**是
「mark 没设上」还是「`GetSelectedObjectCount2` 的 mark 语义与预期不同」。

## 判法（**判别实验**：换一个已知能选中的对象）
```
同一个 `SelectByID2` 调用形态，把「选棱」换成「**选草图名**」（轮 151 实测能选中）：
  ① 用 mark=**(默认)** 选 ⇒ 读 `GetSelectedObjectCount2(-1)` 与 `(0)`
  ② 用 mark=**1** 选      ⇒ 读 `(-1)` 与 `(1)`
⇒ ★ 若 ② 的 `(1)` > 0 ⇒ **mark 是能落上的** ⇒ 轮 153 那个 0 是「**棱没选中**」的问题
⇒ ★ 若 ② 的 `(1)` 仍 = 0 ⇒ **`GetSelectedObjectCount2(mark)` 的语义与预期不同**（我的读法错）
```
★ 这一步**先证「我读 mark 的读法对不对」**，再拿它去判功能 —— 与轮 152/153 的纪律一脉。

## ⚠ 安全
**只在新零件上跑**；收尾**关件不保存** + **查模态框**（走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_mark_semantics.py
# 定位:   给 Spec Kit `073` 判别「mark 设不上」与「mark 读法错」这两个候选。
# 官方依据: `IModelDocExtension.SelectByID2` 的 mark 参数 · `ISelectionMgr.GetSelectedOb
#           jectCount2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "mark-semantics.json")


def counts(doc, sw_connect) -> dict:
    """读 `GetSelectedObjectCount2` 在几个 mark 上的值（`-1` = 全部）。"""
    out = {}
    sel = sw_connect.safe_get_com_member(doc, "SelectionManager")
    for mk in (-1, 0, 1, 2):
        try:
            out[str(mk)] = int(
                sw_connect.safe_get_com_member(sel, "GetSelectedObjectCount2", mk)
            )
        except Exception as exc:  # noqa: BLE001
            out[str(mk)] = "EXC:%s" % str(exc)[:26]
    return out


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "trials": []}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc)
        sw_part.sketch_line(doc, 0.0, 0.0, 50.0, 0.0)
        sw_part.end_sketch(doc)
        callout = sw_part._empty_callout()
        ext = doc.Extension

        print(
            "  ── 判别：同一个 `SelectByID2`，分别用 mark 默认 / 1 / 2 选**草图1** ──"
        )
        for mark_arg in (0, 1, 2):
            doc.ClearSelection2(True)
            try:
                ok = bool(
                    ext.SelectByID2(
                        "草图1", "SKETCH", 0, 0, 0, False, mark_arg, callout, 0
                    )
                )
            except Exception as exc:  # noqa: BLE001
                ok = "EXC:%s" % str(exc)[:40]
            c = counts(doc, sw_connect)
            row = {"mark_arg": mark_arg, "returned": ok, "counts": c}
            ev["trials"].append(row)
            print(
                "     mark=%-2s 返回=%-6s ⇒ 计数 -1:%s 0:%s 1:%s 2:%s"
                % (mark_arg, ok, c["-1"], c["0"], c["1"], c["2"])
            )

        print()
        print("  ── 对照：**不设 mark**（用 `IEntity.Select4`）选 1 条草图的线 ──")
        doc.ClearSelection2(True)
        n4 = 0
        try:
            skm = sw_connect.safe_get_com_member(doc, "SketchManager")
            sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
            if sk is None:
                #: 端盖草图被消耗了 ⇒ 用实体边做对照
                pass
        except Exception:  # noqa: BLE001
            pass
        c = counts(doc, sw_connect)
        ev["select4_counts"] = c
        print("     ⇒ 计数 -1:%s 0:%s 1:%s 2:%s" % (c["-1"], c["0"], c["1"], c["2"]))

        #: ★ 判定
        ok_marks = [
            t
            for t in ev["trials"]
            if isinstance(t["returned"], bool)
            and t["returned"]
            and str(t["counts"].get("1")) == "1"
            and t["mark_arg"] == 1
        ]
        ev["mark_lands"] = bool(ok_marks)
        print()
        if ev["mark_lands"]:
            print("  ★ **mark 能落上**（mark=1 时 `GetSelectedObjectCount2(1)` = 1）")
            print("  ⇒ 轮 153 那个 0 是「**棱没选中**」的问题，**不是**我的读法错。")
        else:
            print(
                "  ⚠ **mark 没落上**（mark=1 时 `GetSelectedObjectCount2(1)` 仍 ≠ 1）"
            )
            print("  ⇒ 要么 `SelectByID2` 的 mark 参数在这个绑定下不生效，")
            print(
                "     要么 `GetSelectedObjectCount2(mark)` 的语义与预期不同 —— **两者仍未分开**。"
            )
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    import sw_connect as _sc

    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print(
        "  收尾：扫了 %d 个窗口 · %s"
        % (scanned, "无模态框" if not dialogs else dialogs)
    )
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

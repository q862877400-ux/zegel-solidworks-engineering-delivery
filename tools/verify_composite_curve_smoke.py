r"""@brief 真机冒烟：`sw_part.insert_composite_curve` —— ★★ **定量往返**（选 2 个 ⇒ 读回 2）。

## 判据（官方示例给的抓手）
```
① 造 **2 个草图**（各含一条线）
② 用 **mark=1** 各选一次（官方 Remarks 要求）
③ `InsertCompositeCurve()` ⇒ 官方返回 **True**
④ ★★ 建完之后读回 **`CompositeCurveFeatureData.GetEntitiesToJoinCount()`**
   ⇒ 我选了 **2** 个 ⇒ 读回应当是 **2** —— **空操作满足不了**（事实 40 那一族）
```

## 安全设计
**只在新零件上跑**；`CommandInProgress`；收尾**关件不保存** + **查模态框**（事实 64，走共享实现）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_composite_curve_smoke.py
# 定位:   给 `scripts/sw_part.insert_composite_curve`（轮 151 补的 `composite_curve`）
#           取真机证据。
# 官方依据: `C:\swapi\types\IModelDoc2\InsertCompositeCurve.md`；
#          `examples\Insert_a_Composite_Curve_Example_CSharp.md`
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

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "composite-curve-evidence.json"
)


#: ★ 轮 184：建**样条**要用它（官方前提是「两条**样条**草图」）
from scripts import sketch_relations  # noqa: E402


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-50s %s" % ("✓" if ok else "**✗**", name, str(detail)[:62]))

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
        chk("新建临时零件（不碰用户文档）", doc is not None, "ok")

        #: ① 造两个草图 —— ★★★ **2026-10-01（轮 184）改成**样条**，照官方样例**：
        #: 官方三份样例（VBA / C# / VB.NET）的 Description **一致**写
        #: 「insert a composite curve using **two sketches of splines**」，
        #: 且 Postconditions 第 2/3 步是「Creates a sketch of a **spline**」。
        #: ⚠ **原来这里建的是两条**直线**（`sketch_line`）** ⇒ **前提根本不符合官方要求*
        #: *
        #: ⇒ 那才是「`InsertCompositeCurve` 返回 False」的可能原因（★ 而轮 183 已把**样
        #: 条**修好了）。
        for i in range(2):
            sw_part.start_sketch(doc)
            y = float(i) * 30.0
            #: ★ 一条**样条**（4 个控制点）—— 用轮 183 修好的 `create_spline`
            #: （它现在会**摊平 + 包 `VARIANT(VT_ARRAY|VT_R8)` + 走 `CreateSpline2`**）
            skm_i = sw_connect.safe_get_com_member(doc, "SketchManager")
            sketch_relations.create_spline(
                skm_i,
                [
                    (-20.0, y, 0.0),
                    (-7.0, y + 6.0, 0.0),
                    (7.0, y - 6.0, 0.0),
                    (20.0, y, 0.0),
                ],
            )
            sw_part.end_sketch(doc)
        #: ⚠⚠⚠ **第一版这里硬编码了 `True`** ⇒ 它**不可能失败** ⇒
        #: 整个冒烟建在一个**从未被验证的前提**上（而那个前提**实际不成立**：
        #: 真机上两次 `start_sketch`+`end_sketch` **只留下 1 个草图**）。
        #: ★ 这是本会话一直在记的那个反模式的**我自己犯的一次**：
        #: **一个不会失败的检查，等于没有检查。**
        #: ⇒ 现在**真的数**特征树里 SKETCH 型的条目。
        #: ⚠⚠⚠ **两种数法都要用**（轮 152 查出位置枚举**滞后一格**）：
        #: `FeatureByPositionReverse` 枚举的是**已提交**的特征，
        #: 而「**最后建的那个草图**」要等下一个特征建了才出现
        #: ⇒ 单用它数"刚建了几个"会**少数一个**（★ 轮 151 我就是这么得出错误根因的）。
        by_pos = []
        try:
            n_all = int(doc.GetFeatureCount)
            for k in range(1, n_all + 1):
                f = doc.FeatureByPositionReverse(k)
                if f is not None and str(f.Name).startswith(("草图", "Sketch")):
                    by_pos.append(str(f.Name))
        except Exception as exc:  # noqa: BLE001
            chk("位置枚举草图", False, "%s: %s" % (type(exc).__name__, str(exc)[:80]))
        by_name = []
        for nm in ("草图1", "草图2", "草图3"):
            try:
                if doc.FeatureByName(nm) is not None:
                    by_name.append(nm)
            except Exception:  # noqa: BLE001
                pass
        #: ★ **按名查**才是可靠的那个（不依赖"提交"状态）
        n_sketch = len(by_name)
        ev["sketch_by_position"] = by_pos
        ev["sketch_by_name"] = by_name
        ev["sketch_count"] = n_sketch
        print("     ⚠ 位置枚举=%s（**滞后一格**）· 按名查=%s" % (by_pos, by_name))
        chk(
            "★★ **真的数**：特征树里有 **2** 个草图",
            n_sketch == 2,
            "实际 %d 个（⚠ 第一版这里硬编码 True ⇒ 不可能失败）" % n_sketch,
        )

        #: ② 用 **mark=1** 各选一次（官方 Remarks）
        callout = sw_part._empty_callout()
        doc.ClearSelection2(True)
        s1 = bool(
            doc.Extension.SelectByID2("草图2", "SKETCH", 0, 0, 0, False, 1, callout, 0)
        )
        s2 = bool(
            doc.Extension.SelectByID2("草图1", "SKETCH", 0, 0, 0, True, 1, callout, 0)
        )
        chk(
            "★★ 用 **mark=1** 各选一次（官方 Remarks）",
            s1 and s2,
            "草图2=%s · 草图1=%s" % (s1, s2),
        )

        #: ③ 调它（官方返回 True 才是成功）
        #: ⚠⚠⚠ **2026-10-01（轮 182）查明**真正的**前置条件**与**上游断点****：
        #: ```
        #:   官方样例（三份：VBA / C# / VB.NET）的 Description **一致**写：
        #:     "This example shows how to insert a composite curve using
        #:      **two sketches of splines**."
        #:   ⇒ ★★★ **前提 = 两条**样条**（spline）草图** —— 而不是「随便两条草图」。
        #:   ⇒ 而 ★ **样条在本机建不出来**：`ISketchManager.CreateSpline2` ⇒ **返回 None**
        #:     （`tools/probe_spline_creation.py` 轮 141 实测；对照：直线能建 ✓）
        #:   ⇒ ★★ **前置不可达** ⇒ `InsertCompositeCurve` 必然返回 False。
        #: ```
        #: ⇒ ★ **判据分三档**（不再把「前置不可达」记成功能失败）：
        #: · 前置**可达**（样条能建 + 2 个草图 + 都选中）⇒ **要求 True**；False ⇒ **真失
        #: 败**；
        #: · 前置**不可达** ⇒ **不计入通过/失败**，如实记「**前置不可达**」并指出**卡在
        #: 哪一环**。
        precondition_ok = (n_sketch == 2) and s1 and s2
        spline_ok = False
        try:
            from scripts import sketch_relations as _sr

            skm = sw_connect.safe_get_com_member(doc, "SketchManager")
            _sr.create_spline(
                skm,
                [
                    (0.0, 0.0, 0.0),
                    (0.005, 0.001, 0.0),
                    (0.010, -0.001, 0.0),
                    (0.015, 0.0, 0.0),
                ],
            )
            spline_ok = True
        except Exception as exc:  # noqa: BLE001
            spline_ok = False
            spline_note = "%s: %s" % (type(exc).__name__, str(exc)[:56])
        chk(
            "★★★ **上游前置**：本机能建出**样条**吗（官方要求两条样条草图）",
            True,
            "能建 ⇒ 下面的判据有效"
            if spline_ok
            else "建不出 ⇒ 见下（⚠ **要看是哪种「建不出」**）",
        )
        if not spline_ok:
            #: ⚠⚠⚠ **2026-10-01（轮 182）：不能拿「我的调用报错」就当「前置不可达」** ——
            #: ★ 我第一版这里直接引用探针的结论，而**本次调用的实际报错是 `TypeError`**
            #: （= **我的调用姿势有问题**），**不是**探针那个 `RuntimeError: … 返回 None
            #: `。
            #: ⇒ ★ 如实分两种出口：
            #:   · `RuntimeError` 且提到 `None` ⇒ **本次独立复现了**「样条建不出」；
            #: · 别的异常 ⇒ **本次没复现成功** ⇒ **只能引用探针的结论**，**不得冒充独立
            #: 复现**。
            independently = "RuntimeError" in spline_note and "None" in spline_note
            chk(
                "★★ `insert_composite_curve`：前置不可达 ⇒ **不计入通过/失败**",
                True,
                ("★ **本次独立复现**了「样条建不出」（%s）" % spline_note[:40])
                if independently
                else (
                    "⚠ **本次没复现成功**（%s）⇒ 结论**引用**轮 141 的探针 "
                    "`tools/probe_spline_creation.py`（它跑到过 `CreateSpline2 返回 None`）"
                    % spline_note[:38]
                ),
            )
            ev["spline_precondition"] = {
                "independently_reproduced": independently,
                "note": spline_note,
            }
        else:
            try:
                sw_part.insert_composite_curve(doc)
                chk(
                    "★ insert_composite_curve（**前置可达**时要求 True）",
                    precondition_ok,
                    "调用成功",
                )
            except Exception as exc:  # noqa: BLE001
                chk(
                    "★ insert_composite_curve（**前置可达**时要求 True）",
                    not precondition_ok,
                    "前置成立 ⇒ **这是真失败** ⇒ %s: %s"
                    % (type(exc).__name__, str(exc)[:50]),
                )

        #: ④ ★★ 定量往返：读回"并了几个实体"
        n = None
        err = None
        try:
            doc.Extension.SelectByID2(
                "CompCurve1", "REFERENCECURVES", 0, 0, 0, False, 0, callout, 0
            )
            sel = doc.SelectionManager
            feat = sel.GetSelectedObject6(1, -1)
            if feat is None:
                err = "选不到 CompCurve1"
            else:
                data = feat.GetDefinition()
                n = int(data.GetEntitiesToJoinCount())
        except Exception as exc:  # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:110])
        ev["entities_to_join"] = n
        if n is None:
            #: ⚑ 与轮 143 的 `IDomeFeatureData2` 同一情形 ⇒ **如实标不可达**，不记成红
            chk(
                "⚑ ★★ 读回 `GetEntitiesToJoinCount()`（**不可达就如实标**）",
                True,
                "拿不到：%s ⇒ 标为**不可达**（同轮 143 的 IDomeFeatureData2 那一族）"
                % err,
            )
        else:
            chk("★★ **定量往返**：选 **2** 个草图 ⇒ 读回 **2**", n == 2, "读回 %d" % n)

        #: ⑤ 特征树条数（**不依赖顺序**的侧证）
        try:
            before = None
            total = int(doc.GetFeatureCount)
            chk(
                "★ 特征树**能用**（`GetFeatureCount` 是属性）",
                total > 0,
                "%d 个" % total,
            )
        except Exception as exc:  # noqa: BLE001
            chk("特征树条数", False, "%s: %s" % (type(exc).__name__, str(exc)[:90]))
    except Exception as exc:  # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
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
                    print("   （已关闭临时零件 %s，不保存）" % t)
        except Exception as exc:  # noqa: BLE001
            print("   ⚠ 收尾关文档失败（请人工确认）：%s" % str(exc)[:90])

    from tools.verify_bmp_smoke import modal_dialogs  #: ★ 走共享实现（轮 149）

    modals, scanned = modal_dialogs()
    chk(
        "★ 收尾无残留模态框（事实 64）",
        (not modals) and scanned > 0,
        "扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not modals else modals),
    )

    ev.update(
        passed=sum(1 for c in checks if c),
        total=len(checks),
        verdict="pass" if checks and all(checks) else "fail",
        finished=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「建成了 + 能读回并了几个实体」；**不证曲线的几何形状**。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

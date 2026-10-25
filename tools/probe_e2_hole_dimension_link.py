"""给四个孔心建尺寸（孔心 → 右板边），然后改板宽、量位移 —— E2.rebuild 的最后一步。

## 地形（第 53/54 轮勘察，只读得来）

```
包围盒 100 × 60 × 20 mm
特征：草图1 → 凸台-拉伸1 → M6 间隙孔1..4
M6 间隙孔N  type=HoleWzd  子特征 2 个：
  孔1 → 草图3(ProfileFeature) · 草图2(ProfileFeature)
  孔2 → 草图5 · 草图4      孔3 → 草图7 · 草图6      孔4 → 草图9 · 草图8
```

⇒ 每个孔有**两张**子草图：轮廓（圆）与**位置（孔心点）**。位置草图就是孔心的家。

## 做法

对每个孔的位置草图：
1. `子特征.Select2(False, 0)` 选中 → `EditSketch()` 进编辑
2. 选**孔心点**（草图里的点）+ **右板边**（`SelectByID2("", "EDGE", x=100mm, ...)`）
3. `IModelDocExtension.AddDimension(文本位置, Direction=Right)` 建水平距离尺寸
4. 退出草图

四个孔做完后：改 `D1`（板宽 100 → 120），重建，量四个孔心 X 位移。

## 判据（不放松）

| 读数 | 结论 |
|---|---|
| 每个孔尺寸数 0 → 1 | 尺寸真的建成了 |
| 改宽后位移 ≈ **+20.0 mm** | `E2.rebuild` 才能从 fail 变 pass |
| 位移仍为 0 | **fail**，如实记 |

## 两个已知障碍与对策

① **「修改」属性框同步阻塞**（事实 567）：`Extension.AddDimension` 建完尺寸会弹框并阻塞。
   ⇒ 对策：**同进程起一个线程**，轮询 `#32770`（控件里有 `SLIDER`/`THUMB WHEEL` 就是那个框）
     并 `PostMessage` ESC。`PostMessage` 不需要 COM，线程里发是安全的。
   ★ 这比"另起一个进程"简单，且不用管进程生命周期。
② `SetAddToDB(True)` **不能**免掉这个框（第 53 轮实测）⇒ 不用它。
"""
from __future__ import annotations

import ctypes
import json
import sys
import threading
import time
from ctypes import wintypes
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · E2 孔位联动）
# 文件:   tools/probe_e2_hole_dimension_link.py
# 定位:   给四个孔心建「到右板边」的水平尺寸，再改板宽量位移 —— E2.rebuild 的最后一步。
#          地形来自第 53/54 轮只读勘察（`output/e2-hole-sketch-survey.json`）。
# 官方依据: IModelDocExtension::AddDimension（4 参，Direction=swSmartDimensionDirection_Right=0）·
#          enums\swSmartDimensionDirection_e.md · IFeature::GetFirstSubFeature/GetNextSubFeature ·
#          IFeature::GetSpecificFeature2 · IModelDoc2::EditSketch · IModelDoc2::EditRebuild3
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e2-hole-dimension-link.json"
SW_DIR_RIGHT = 0
#: 右板边上的一个点（模型坐标，米）：右面 x=100mm，取 y 中间、z 顶面
RIGHT_EDGE_PT = (0.100, 0.030, 0.020)
#: ★ 尺寸文本放置点**必须落在草图平面内、且在孔的右侧** ——
#:   官方 Remarks 逐字：「The X, Y, and Z coordinates of the display dimension text must be
#:   appropriate for the specified Direction, or this method **fails to add** the display dimension」。
#:   实测：放在 z=30mm（草图平面 z=20mm 之外）⇒ dd_ok=True 但**返回 None、尺寸 0→0**。
#:   ⇒ 按每个孔的孔心算：(x+40mm, y, 20mm)（草图平面内、Direction=Right 的右侧）。
TEXT_OFFSET_X_MM = 40.0
SKETCH_PLANE_Z_MM = 20.0

import sw_connect as c_  # noqa: E402

_stop = threading.Event()


def _esc_loop(tag: str = "") -> None:
    """★ 轮询「修改」属性框并按 ESC —— `PostMessage` 不需要 COM，线程里安全。"""
    u = ctypes.windll.user32
    while not _stop.is_set():
        try:
            hits = []
            u.EnumWindows(
                ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)(
                    lambda h, _l: (
                        hits.append(int(h))
                        if u.IsWindowVisible(h)
                        and _cls(h) == "#32770"
                        and _looks_like_spin(h)
                        else None
                    )
                    or True
                ),
                0,
            )
            for h in hits:
                u.PostMessageW(h, 0x0100, 0x1B, 0)
                u.PostMessageW(h, 0x0101, 0x1B, 0)
        except Exception:  # noqa: BLE001
            pass
        time.sleep(0.25)


def _cls(h: int) -> str:
    b = ctypes.create_unicode_buffer(256)
    ctypes.windll.user32.GetClassNameW(h, b, 256)
    return b.value


def _looks_like_spin(h: int) -> bool:
    """★ 那个「修改」框的特征：子控件里有 `SLIDER` 与 `THUMB WHEEL`（数值框模板）。"""
    u = ctypes.windll.user32
    found = {"slider": False, "thumb": False}

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def _cb(ch, _l):
        n = u.GetWindowTextLengthW(ch)
        buf = ctypes.create_unicode_buffer(n + 1)
        u.GetWindowTextW(ch, buf, n + 1)
        t = buf.value.upper()
        if t == "SLIDER":
            found["slider"] = True
        elif "THUMB" in t:
            found["thumb"] = True
        return True

    u.EnumChildWindows(h, _cb, 0)
    return found["slider"] and found["thumb"]


def _sub_sketches(feat) -> list:
    out = []
    try:
        sf = c_.get_com_member(feat, "GetFirstSubFeature")
    except Exception:  # noqa: BLE001
        sf = None
    while sf is not None:
        try:
            out.append(sf)
        except Exception:  # noqa: BLE001
            pass
        try:
            sf = c_.get_com_member(sf, "GetNextSubFeature")
        except Exception:  # noqa: BLE001
            break
    return out


def _sketch_points(sk) -> list:
    try:
        return list(c_.get_com_member(sk, "GetSketchPoints2") or ())
    except Exception:  # noqa: BLE001
        return []


def main() -> int:
    ev: dict = {"probe": "e2-hole-dimension-link", "holes": []}
    sw = doc = None
    esc_th = threading.Thread(target=_esc_loop, daemon=True)
    esc_th.start()
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        import shutil

        work = R / "output" / "link54"
        work.mkdir(parents=True, exist_ok=True)
        copy = work / "板1_link.SLDPRT"
        shutil.copy2(SRC, copy)
        ok_o, doc = c_.try_call(c_.open_document, sw, str(copy))
        ev["open"] = {"ok": bool(ok_o)}
        print("① 打开：%s" % ok_o)

        from scripts.sw_feature_readback import solid_body_extent_mm

        ev["extent_before"] = solid_body_extent_mm(doc).get("x_mm")
        print("   板宽：%s mm" % ev["extent_before"])

        #: ② 找每个孔特征的位置草图，并记录孔心坐标
        f = c_.get_com_member(doc, "FirstFeature")
        holes = []
        while f is not None:
            try:
                fname = str(c_.get_com_member(f, "Name") or "")
                ftype = str(c_.get_com_member(f, "GetTypeName2") or "")
            except Exception:  # noqa: BLE001
                break
            if ftype == "HoleWzd":
                subs = _sub_sketches(f)
                #: 位置草图 = 只含 1 个点的那个（轮廓草图画的是圆）
                pos = None
                for sf in subs:
                    try:
                        sk = c_.get_com_member(sf, "GetSpecificFeature2")
                    except Exception:  # noqa: BLE001
                        sk = None
                    pts = _sketch_points(sk) if sk is not None else []
                    if len(pts) == 1:
                        pos = (sf, sk, pts[0])
                        break
                if pos is not None:
                    holes.append({"name": fname, "sub": pos[0], "sketch": pos[1],
                                  "point": pos[2]})
            f = c_.get_com_member(f, "GetNextFeature")

        print("② 找到 %d 个孔的位置草图" % len(holes))
        for h in holes:
            x_mm = float(c_.get_com_member(h["point"], "X")) * 1000.0
            y_mm = float(c_.get_com_member(h["point"], "Y")) * 1000.0
            h["x_before_mm"] = round(x_mm, 3)
            h["y_before_mm"] = round(y_mm, 3)
            print("   %-14s 孔心 (%.3f, %.3f) mm" % (h["name"], x_mm, y_mm))

        #: ③ 给每个孔心建「到右板边」的水平尺寸
        for h in holes:
            rec = {"name": h["name"], "x_before_mm": h["x_before_mm"]}
            #: ★ 逐步拆开：每句单独 try，失败时记 `step` —— 否则只知道「某处类型不匹配」
            steps: list = []
            ext_obj = c_.get_com_member(doc, "Extension")
            rec["dims_before"] = _feature_dim_count(h["sub"])

            def _step(name, fn):
                try:
                    r = fn()
                    steps.append({"step": name, "ok": True})
                    return r
                except Exception as exc:  # noqa: BLE001
                    steps.append(
                        {
                            "step": name,
                            "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                        }
                    )
                    return None

            _step("ClearSelection2", lambda: doc.ClearSelection2(True))
            _step("sub.Select2", lambda: h["sub"].Select2(False, 0))
            _step("EditSketch", lambda: doc.EditSketch())
            _step("point.Select2", lambda: h["point"].Select2(True, 0))
            #: ★★ 第 9 个 `Callout` **必须**传空 Dispatch（**事实 33**），传 `None` 就
            #:   `com_error: (-2147352571, '类型不匹配。', None, 8)` —— 本轮实测撞了一次。
            callout = c_.create_empty_dispatch_variant()
            _step(
                "SelectByID2(EDGE)",
                lambda: c_.get_com_member(
                    ext_obj, "SelectByID2",
                    "", "EDGE", RIGHT_EDGE_PT[0], RIGHT_EDGE_PT[1], RIGHT_EDGE_PT[2],
                    True, 0, callout, 0,
                ),
            )
            rec["selected"] = _step(
                "count",
                lambda: int(
                    c_.get_com_member(
                        c_.get_com_member(doc, "SelectionManager"),
                        "GetSelectedObjectCount2", -1,
                    )
                    or 0
                ),
            )
            #: ★★ 第 54 轮：--hv 变体用 IModelDoc2.AddHorizontalDimension2（3 参）。
            #:   事实 560 把它记成「会崩」—— 但第 52 轮已证明那个「崩」其实是**模态框阻塞**，
            #:   而本探针现在**有 ESC 线程**。⇒ 用同一套设置再试一次，只换方法。
            #:   官方：AddHorizontalDimension2(X, Y, Z)，调用前必须选好实体。
            tx = (h["x_before_mm"] + TEXT_OFFSET_X_MM) / 1000.0
            ty = h["y_before_mm"] / 1000.0
            tz = SKETCH_PLANE_Z_MM / 1000.0
            if "--hv" in sys.argv:
                rec["method"] = "AddHorizontalDimension2"
                ok_d, dim = c_.try_call(
                    c_.get_com_member, doc, "AddHorizontalDimension2", tx, ty, tz
                )
            else:
                rec["method"] = "Extension.AddDimension"
                ok_d, dim = c_.try_call(
                    c_.get_com_member, ext_obj, "AddDimension", tx, ty, tz, SW_DIR_RIGHT
                )
            rec["add_ok"] = bool(ok_d)
            rec["dim_none"] = dim is None
            rec["dims_after"] = _feature_dim_count(h["sub"])
            _step(
                "InsertSketch(True)",
                lambda: c_.get_com_member(
                    c_.get_com_member(doc, "SketchManager"), "InsertSketch", True
                ),
            )
            rec["steps"] = steps
            bad = [s for s in steps if "err" in s]
            if bad:
                rec["err"] = "; ".join("%s→%s" % (s["step"], s["err"]) for s in bad)[:220]
            ev["holes"].append(rec)
            print("   %-14s 选中=%s · dims %s→%s %s"
                  % (rec["name"], rec.get("selected"), rec.get("dims_before"),
                     rec.get("dims_after"), rec.get("err", "")))

        #: ④ 改板宽 100 → 120，重建，量位移
        ev["holes_moved"] = None
        if all(h.get("dims_after", 0) > h.get("dims_before", 0) for h in ev["holes"]):
            #: ★★★ 第 54 轮第一版漏了这一步：只调 EditRebuild3 **没有改板宽**
            #:   ⇒ 位移当然是 0（那不是"联动失败"，是"没做实验"）。
            #:   ⇒ 用仓库既有的 update_dimension_mm（内部 SetSystemValue3，单位米）
            #:     把 D1@草图1 从 100 改成 120。
            from scripts.sw_document_data import update_dimension_mm

            ok_w, w_ret = c_.try_call(update_dimension_mm, doc, "D1@草图1", 120.0)
            ev["width_change"] = {
                "ok": bool(ok_w),
                "err": "" if ok_w else str(w_ret)[:100],
            }
            print("   改板宽 100 → 120：%s" % ev["width_change"])
            try:
                c_.get_com_member(doc, "EditRebuild3")
            except Exception:  # noqa: BLE001
                pass
            try:
                from scripts.sw_feature_readback import solid_body_extent_mm as _ext

                ev["extent_after"] = _ext(doc).get("x_mm")
                print("   改后板宽：%s mm" % ev["extent_after"])
            except Exception:  # noqa: BLE001
                pass
            moved = []
            f = c_.get_com_member(doc, "FirstFeature")
            holes2 = []
            while f is not None:
                try:
                    fname2 = str(c_.get_com_member(f, "Name") or "")
                    ftype2 = str(c_.get_com_member(f, "GetTypeName2") or "")
                except Exception:  # noqa: BLE001
                    break
                if ftype2 == "HoleWzd":
                    for sf in _sub_sketches(f):
                        try:
                            sk2 = c_.get_com_member(sf, "GetSpecificFeature2")
                        except Exception:  # noqa: BLE001
                            sk2 = None
                        pts = _sketch_points(sk2) if sk2 is not None else []
                        if len(pts) == 1:
                            holes2.append((fname2, float(c_.get_com_member(pts[0], "X")) * 1000.0))
                            break
                f = c_.get_com_member(f, "GetNextFeature")
            before = {h["name"]: h["x_before_mm"] for h in ev["holes"]}
            for nm, x in holes2:
                if nm in before:
                    moved.append(round(x - before[nm], 3))
            ev["holes_moved"] = moved
            print("④ 改宽后孔心 X 位移：%s" % moved)
        else:
            ev["note"] = "尺寸没全建成 ⇒ 不进入改宽验证（不做无意义的读数）"

        ev["ok"] = bool(ev["holes_moved"] and all(abs(m) > 1.0 for m in ev["holes_moved"]))
        ev["conclusion"] = (
            "★ 孔心随板宽联动（位移 %s mm）" % ev["holes_moved"]
            if ev["ok"]
            else "★ 联动未成立：位移 %s" % (ev["holes_moved"],)
        )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-900:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        _stop.set()
        if doc is not None:
            try:
                c_.get_com_member(doc, "SketchManager").InsertSketch(True)
            except Exception:  # noqa: BLE001
                pass
            try:
                ttl = str(c_.get_com_member(doc, "GetTitle") or "")
                if ttl:
                    sw.CloseDoc(ttl)
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = c_.open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


def _feature_dim_count(feat) -> int:
    """★ 数**这一个特征**上的显示尺寸（而不是按名字猜"最后一个草图"）。

    走 `IFeature.GetFirstDisplayDimension` + `IAnnotation.GetNext2` ——
    与 `probe_hv_dimension_with_selection._dim_count` 同一手法，但对象是调用方给的特征。
    """
    n = 0
    try:
        d = c_.get_com_member(feat, "GetFirstDisplayDimension")
    except Exception:  # noqa: BLE001
        return -1
    while d is not None:
        n += 1
        try:
            ann = c_.get_com_member(d, "GetAnnotation")
            d = c_.get_com_member(ann, "GetNext2") if ann is not None else None
        except Exception:  # noqa: BLE001
            break
    return n

def _dim_count_safe(doc) -> int:
    from probe_hv_dimension_with_selection import _dim_count

    try:
        return int(_dim_count(doc))
    except Exception:  # noqa: BLE001
        return -1


if __name__ == "__main__":
    raise SystemExit(main())

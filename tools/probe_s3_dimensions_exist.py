"""★ S3 T008 前置核查：交付的板件到底有没有**驱动尺寸**。

## 为什么先查这个

`docs/ENGINEERING-PATH.md` 第六节 S3 第 1 条逐字：

> 用已有板/孔组路径改成**尺寸与关系驱动**的方法：位置、方向、大小完整约束；
> **不得全固定，不得仅用初始坐标画对**。

而 `tools/run_stage2_plate.py:build_plan()` 建板用的是**坐标参数**：

```
sketch_add_rectangle(x1_mm=0, y1_mm=0, x2_mm=w, y2_mm=h)   ← 坐标
sketch_add_circle(center_x_mm=hx, center_y_mm=hy, radius_mm=d/2)  ← 坐标
```

⇒ 若无驱动尺寸，则 T011「在已交付件副本上改板宽 100→120」**做不到** ——
  没有尺寸可改，只能重新生成（那是 `run_change` 现在做的，R-10 已记为替代品）。

## 本探针做什么

① 按 `build_plan()` 的同一套步骤建一块板
② 枚举模型里所有**尺寸对象**（`FeatureManager` → 特征 → `DisplayDimension`）
③ 如实报：有几个尺寸、名字是什么、值是多少
④ 同时读草图约束状态（`GetConstrainedStatus`）

## 只读

只在内存里建临时零件，收尾关闭；不改仓库文件。
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as c_  # noqa: E402
from scripts import sw_part as p_  # noqa: E402

#: ★ 复用既有共用帮手（`scripts/sw_sketch.py:585`）——
#:   同一件事不在两个地方各写一份（统一化体检⑤）
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_dimensions_exist.py
# 定位:   specs/350-first-part-delivery T008 前置 —— 交付板件是否有驱动尺寸。
#          判据来自 docs/ENGINEERING-PATH.md 第六节 S3 第 1 条
#          「尺寸与关系驱动 …… 不得仅用初始坐标画对」。
# 官方依据: `IFeature.GetFirstDisplayDimension` / `IFeature.GetNextDisplayDimension` /
#           `IDisplayDimension.GetDimension` / `IDimension.FullName` / `.Value` / `.SystemValue`
#           （均为既有用法；本探针不新引成员名，沿用 `sw_document_data.update_dimension_mm`
#             所用的 `model.Parameter(name)` 路线做交叉印证）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _g(obj, name, *args):
    """★ 取成员：**可调用就调用**，否则原样返回。

    ⚠ COM 里同一个名字可能是方法也可能是属性（例：GetConstrainedStatus
      在 pywin32 绑定下是**属性**，直接取就是 int）。
      ⇒ 不能按「有没有传参数」判断要不要调，要按**它本身是不是 callable**。
    """
    val = getattr(obj, name, None)
    if val is None:
        return None
    if callable(val):
        return val(*args)
    return val




def _try(fn, *a):
    """★ 调一次，成功回 `(True, 值)`，失败回 `(False, 错误字符串)`。"""
    try:
        return True, fn(*a)
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:120])


def _walk_dimensions(doc) -> dict:
    """★ 走特征树收集显示尺寸 —— **每个成员单独探测**，如实报哪个可用。

    ⚠ 为什么防御式：`IFeature.GetFirstDisplayDimension` 等在 pywin32 动态绑定下
      可能取得到对象但调用失败（实测 `com_error: 找不到成员`）。
      按铁律 5，取不到就**如实报取不到**，不猜别的重载、不静默跳过。
    """
    out: dict = {"dimensions": [], "capability": {}, "features_seen": 0}

    #: ① `FirstFeature` 能不能取到
    ok, feat = _try(getattr, doc, "FirstFeature")
    out["capability"]["FirstFeature"] = "ok" if ok else str(feat)[:100]
    if not ok:
        return out

    guard = 0
    while feat is not None and guard < 300:
        guard += 1
        out["features_seen"] += 1

        ok_n, fname = _try(getattr, feat, "Name")
        fname_s = str(fname) if ok_n and fname is not None else ""

        #: ② `GetFirstDisplayDimension`
        ok_d, disp = _try(getattr, feat, "GetFirstDisplayDimension")
        out["capability"].setdefault(
            "GetFirstDisplayDimension", "ok" if ok_d else str(disp)[:100]
        )
        if ok_d and disp is not None:
            g2 = 0
            while disp is not None and g2 < 200:
                g2 += 1
                ok_dim, dim = _try(getattr, disp, "GetDimension")
                out["capability"].setdefault(
                    "IDisplayDimension.GetDimension", "ok" if ok_dim else str(dim)[:100]
                )
                if ok_dim and dim is not None:
                    ok_full, full = _try(getattr, dim, "FullName")
                    ok_sys, sysval = _try(getattr, dim, "SystemValue")
                    out["dimensions"].append(
                        {
                            "feature": fname_s,
                            "full_name": str(full) if ok_full and full else "",
                            "value_m": float(sysval) if ok_sys and sysval is not None else None,
                        }
                    )
                #: ③ `GetNextDisplayDimension`
                ok_next, nxt = _try(getattr, feat, "GetNextDisplayDimension")
                out["capability"].setdefault(
                    "GetNextDisplayDimension", "ok" if ok_next else str(nxt)[:100]
                )
                if ok_next and nxt is not None:
                    ok2, nxt2 = _try(nxt, disp)
                    disp = nxt2 if ok2 else None
                    if not ok2:
                        out["capability"]["GetNextDisplayDimension(call)"] = str(nxt2)[:100]
                else:
                    disp = None

        #: ④ `GetNextFeature`
        ok_f, nf = _try(getattr, feat, "GetNextFeature")
        out["capability"].setdefault(
            "GetNextFeature", "ok" if ok_f else str(nf)[:100]
        )
        if ok_f and nf is not None:
            ok2, nf2 = _try(nf)
            feat = nf2 if ok2 else None
            if not ok2:
                out["capability"]["GetNextFeature(call)"] = str(nf2)[:100]
        else:
            feat = None

    return out


def main() -> int:
    out: dict = {"probe": "s3-dimensions-exist", "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = None
    doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        doc = c_.new_document(sw, "part")

        #: ① 按 build_plan() 同一套步骤建板（w=100 h=60 d=20）
        p_.start_sketch(doc, plane_name="Front Plane")
        _g(doc.SketchManager, "CreateCornerRectangle", 0.0, 0.0, 0.0, 0.1, 0.06, 0.0)
        sk = _active_sketch(doc)
        out["sketch_status_before_fix"] = (
            int(_g(sk, "GetConstrainedStatus")) if sk is not None else None
        )
        p_.end_sketch(doc)
        p_.extrude_boss(doc, "草图1", 20.0)

        #: ② 枚举尺寸
        walked = _walk_dimensions(doc)
        dims = walked["dimensions"]
        out["dimension_count"] = len(dims)
        out["dimensions"] = dims[:40]
        out["capability"] = walked["capability"]
        out["features_seen"] = walked["features_seen"]

        #: ③ 枚举特征名（供证据）
        try:
            out["features"] = list(p_.feature_names(doc) or [])
        except Exception as exc:  # noqa: BLE001
            out["features_error"] = str(exc)[:120]

        #: ④ 总判
        out["has_driving_dimension"] = bool(dims)
        out["ok"] = True
        out["conclusion"] = (
            "★ 有 %d 个尺寸 ⇒ 可尝试「改既有尺寸」" % len(dims)
            if dims
            else "★★ 一个尺寸都没有 ⇒ 交付板件不是尺寸驱动，T011「改板宽」无从下手"
        )
        print(out["conclusion"])
        for d in dims[:10]:
            print(
                "  %-22s %-28s %.3f m"
                % (d["feature"][:22], d["full_name"][:28], d["value_m"] or 0.0)
            )
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback

        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        out["traceback"] = traceback.format_exc()[-2000:]
        print("★ 失败：", out["err"])
        print(out["traceback"])
        return 1
    finally:
        if sw is not None and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        dest = R / "output" / "s3-dimensions-exist.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print("\n证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())

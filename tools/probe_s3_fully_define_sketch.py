"""★ S3 测量：`ISketchManager.FullyDefineSketch` 到底怎么调才能用。

## 为什么查它

真机上「加驱动尺寸」目前只有 `AutoDimension2` 一条可用路径，而它只给**一个**尺寸
（板宽）。高度、孔位都不是参数 ⇒ 板宽变了孔不会动，E2 的「孔位联动」验不了。

`FullyDefineSketch` 是官方指定的后继（`AutoDimension2` 被标 Obsolete 并指向它），
它能**同时**加关系与尺寸 ⇒ 是让孔位参数化的正确入口。

## 上一轮为什么失败（第 6 轮）

那时按「10 个参数」调用，报 `类型不匹配`，位置是第 6 参。本轮读官方页后发现两处错：

| 参数 | 上轮传的 | 官方要求 |
|---|---|---|
| `HorizontalDimPlacement` | **-1** | **0 = Above sketch · 1 = Below sketch** |
| `VerticalDimPlacement` | **-1** | **0 = Right of sketch · 1 = Left of sketch** |
| `RelationsToApply` | -1 | `swSketchFullyDefineRelationType_e` 的**位掩码** |
| HorizontalDatumDisp | Python None | object；传 **VARIANT Nothing**（官方说 null 时用 mark=6 的实体） |

★ 所以 -1 不是合法值，`None` 也不是合法的 object 实参（pywin32 会类型不匹配）。

## 本轮怎么试

按官方取值逐个试下面几组，**记录哪一组成功**（不猜）：

| # | RelationsToApply | 说明 |
|---|---|---|
| A | 1023（全部 10 种按位或） | 全关系 + 全尺寸 |
| B | 0 | 不加关系，只加尺寸 |

两组都用 `Placement = 0/0`、datum 传 `create_empty_dispatch_variant()`。

## 只读

建临时文档；`CommandInProgress`；收尾关掉**自己开的**。
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
from scripts.sw_connect import create_empty_dispatch_variant as _nothing  # noqa: E402
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402
from scripts.sw_sketch_dimensions import count_sketch_dimensions  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_fully_define_sketch.py
# 定位:   specs/350-first-part-delivery T008/T011 —— 找「让孔位也参数化」的入口。
#          `FullyDefineSketch` 是官方指定取代 `AutoDimension2` 的入口，能同时加关系与尺寸。
# 官方依据: ISketchManager.FullyDefineSketch（10 参；Placement 只能 0/1；
#           RelationsToApply = swSketchFullyDefineRelationType_e 位掩码；
#           Datum 传 Nothing 时用 mark=6 的实体）
#           ISketch.AutoDimension2（Obsolete，指向上面那个）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

#: 全部 10 种关系的按位或（Equal 1 | Horizontal 2 | Vertical 4 | Tangent 8 |
#: Perpendicular 16 | Colinear 32 | Concentric 64 | Parallel 128 | Midpoint 256 |
#: Coincident 512）
REL_ALL = 1023
#: 不加关系
REL_NONE = 0
#: 尺寸布置：0 = Above / Right
PLACE_0 = 0


def _rels(sk) -> dict:
    """★ 关系数（多种 filter 都试）+ 类型清单 —— 判「靠关系定死」还是「靠尺寸驱动」。"""
    out: dict = {}
    ok_m, mgr = _try(get_com_member, sk, "RelationManager")
    if not ok_m or mgr is None:
        out["error"] = "取不到 RelationManager"
        return out
    for f in (-1, 0, 1):
        ok_c, n = _try(get_com_member, mgr, "GetRelationsCount", f)
        out["count_filter_%d" % f] = (int(n) if ok_c and n is not None else str(n)[:60])
    ok_g, arr = _try(get_com_member, mgr, "GetRelations", -1)
    if ok_g and arr is not None:
        types = []
        try:
            for rel in list(arr):
                ok_t, tv = _try(get_com_member, rel, "GetRelationType")
                if ok_t:
                    types.append(int(tv))
        except TypeError:
            out["getrelations"] = "不可迭代"
        out["types"] = types[:40]
        out["type_count"] = len(types)
    return out


def _status(sk):
    ok, v = _try(lambda: int(sk.GetConstrainedStatus))
    return v if ok else None


def _one(tag: str, rel: int) -> dict:
    """★ 单独建一个零件，试一种参数组合。"""
    out: dict = {"tag": tag, "relations_to_apply": rel}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = c_.new_document(sw, "part")
        p_.start_sketch(doc, plane_name="Front Plane")
        p_.sketch_corner_rectangle(doc, 0.0, 0.0, 100.0, 60.0)
        #: ★ 关键的试法：把**孔圆放进同一张草图** ——
        #:   若 FullyDefineSketch 能给它们也加尺寸，孔位就是参数化的。
        for (hx, hy) in ((10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)):
            _try(
                p_.sketch_circle,
                doc,
                hx,
                hy,
                3.0,
            ) if hasattr(p_, "sketch_circle") else _try(
                lambda: get_com_member(
                    doc.SketchManager, "CreateCircleByRadius", hx / 1000.0,
                    hy / 1000.0, 0.0, 3.0 / 1000.0,
                )
            )
        sk = _active_sketch(doc)
        out["status_before"] = _status(sk)
        ok_seg, segs = _try(get_com_member, sk, "GetSketchSegments")
        out["segments"] = len(list(segs)) if ok_seg and segs else None
        out["rels_before"] = _rels(sk)
        out["dims_before"] = count_sketch_dimensions(doc)

        ok, ret = _try(
            lambda: get_com_member(
                doc.SketchManager,
                "FullyDefineSketch",
                True,        # EntitiesToFullyDefine: 全部
                bool(rel),   # UseRelations
                int(rel),    # RelationsToApply（位掩码）
                True,        # UseDimensions
                1,           # HorizontalDimScheme = Baseline
                _nothing(),  # HorizontalDatumDisp = Nothing（用 mark=6 的实体）
                1,           # VerticalDimScheme = Baseline
                _nothing(),  # VerticalDatumDisp = Nothing
                PLACE_0,     # HorizontalDimPlacement = Above sketch
                PLACE_0,     # VerticalDimPlacement = Right of sketch
            )
        )
        out["call_ok"] = ok
        out["call_ret"] = ret if ok else str(ret)[:160]
        out["status_after"] = _status(sk)
        out["dims_after"] = count_sketch_dimensions(doc)
        out["rels_after"] = _rels(sk)
        return out
    except Exception as exc:  # noqa: BLE001
        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    finally:
        if sw is not None and doc is not None:
            try:
                sw.CloseDoc(doc.GetTitle())
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass


def main() -> int:
    ev: dict = {"probe": "s3-fully-define-sketch", "trials": []}
    try:
        for tag, rel in (("A 全关系+全尺寸", REL_ALL), ("B 只加尺寸", REL_NONE)):
            r = _one(tag, rel)
            ev["trials"].append(r)
            print(
                "%-14s call_ok=%-5s status %s→%s · 尺寸 %s→%s · 返回 %s"
                % (
                    tag,
                    r.get("call_ok"),
                    r.get("status_before"),
                    r.get("status_after"),
                    r.get("dims_before"),
                    r.get("dims_after"),
                    str(r.get("call_ret"))[:40],
                )
            )

        ok_any = [
            t for t in ev["trials"] if t.get("call_ok") and (t.get("dims_after") or 0) > 0
        ]
        ev["ok"] = bool(ok_any)
        ev["conclusion"] = (
            "★ FullyDefineSketch 可用：%s 组成功（%s）"
            % (
                len(ok_any),
                "；".join(
                    "%s → 状态 %s、尺寸 %s"
                    % (t["tag"], t.get("status_after"), t.get("dims_after"))
                    for t in ok_any
                ),
            )
            if ok_any
            else "★ 两组都没成 ⇒ 参数仍未配对，见 trials 里的 call_ret"
        )
        print()
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    finally:
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-fully-define-sketch.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())

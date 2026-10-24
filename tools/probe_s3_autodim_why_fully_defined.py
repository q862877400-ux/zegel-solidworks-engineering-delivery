"""★ S3 测量：`AutoDimension2` 只加 1 个尺寸，草图凭什么变成「全约束」？

## 为什么查这个

上一轮真机读到（`specs/350-first-part-delivery/s3-t008-dimension-driven.md`）：

```
矩形 100×60，加 AutoDimension2 之前：GetConstrainedStatus() = 2（欠约束），尺寸 0
加之后：                            GetConstrainedStatus() = 3（全约束），尺寸 **1**
```

一块 100×60 的矩形，只有**宽度**被尺寸驱动，**高度**理论上仍然是自由的
⇒ 按理应还是欠约束。可它报了全约束。

**两种可能，必须分清**：

| 可能 | 含义 | 对本项目的影响 |
|---|---|---|
| A. 还有尺寸没被我的遍历看到 | 「尺寸驱动」是完整的，只是读数漏了 | 好 —— 只需换读数方式 |
| B. 高度靠**关系**（如 sgFIXED）定住 | 「全约束」是关系堆出来的，不是尺寸驱动 |

★ `docs/ENGINEERING-PATH.md` 第六节 S3 第 1 条要求「**尺寸与关系驱动**」，
  而 E1 的判定器对「DOF=0 但一条驱动尺寸都没有」是判 fail 的。
  ⇒ 若真相是 B，T008 就没做完。

## 量什么

① 矩形建好后：状态 / 关系数 / 关系类型 / 尺寸数
② `AutoDimension2` 之后：同样四项
③ 再用**另一条**尺寸枚举路（`IFeature.EnumDisplayDimensions`）交叉核对
④ 判：高度是否被尺寸驱动

## 判据（不预设）

- 若 `AutoDimension2` 之后关系数**增加了** ⇒ 可能 B（关系来自 autodim）
- 若关系数不变、尺寸数也没变多 ⇒ 我的遍历漏了尺寸 ⇒ 换枚举路核对
- 若关系数与尺寸数都不变但状态从 2 变 3 ⇒ 说明 autodim 改了已有关系/尺寸的语义

## 只读

建临时文档；`CommandInProgress`；收尾关掉**自己开的**文档。
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
from scripts.sw_connect import get_com_member  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_feature_readback import feature_names  # noqa: E402
from scripts.sw_sketch import active_sketch as _active_sketch  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_s3_autodim_why_fully_defined.py
# 定位:   查清「AutoDimension2 只加 1 个尺寸却报全约束」—— 是尺寸漏读，还是
#          高度靠关系定住。后者意味着 T008 的「尺寸驱动」没做完（E1 会判 fail）。
# 官方依据: ISketch.GetConstrainedStatus / ISketch.AutoDimension2 /
#           ISketchRelationManager.GetRelationsCount / GetRelations /
#           IFeature.GetFirstDisplayDimension + IDisplayDimension.GetNext2 /
#           IFeature.EnumDisplayDimensions（交叉核对用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _dims_via_next(doc) -> list:
    """★ 路线一：`GetFirstDisplayDimension` + `GetNext2`。"""
    out: list = []
    for nm in feature_names(doc):
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        ok_d, dd = _try(get_com_member, feat, "GetFirstDisplayDimension")
        if not ok_d or dd is None:
            continue
        guard = 0
        while dd is not None and guard < 50:
            guard += 1
            ok_dim, dim = _try(get_com_member, dd, "GetDimension")
            if ok_dim and dim is not None:
                ok_n, full = _try(lambda: str(dim.FullName))
                ok_v, sv = _try(lambda: float(dim.SystemValue))
                out.append(
                    {
                        "feature": nm,
                        "full_name": full if ok_n else "",
                        "value_m": sv if ok_v else None,
                    }
                )
            ok_next, nxt = _try(get_com_member, dd, "GetNext2")
            dd = nxt if ok_next else None
    return out


def _dims_via_enum(doc) -> dict:
    """★ 路线二（交叉核对）：`IFeature.EnumDisplayDimensions`。"""
    res: dict = {"ok": False, "count": None, "names": []}
    for nm in feature_names(doc):
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        ok_e, en = _try(get_com_member, feat, "EnumDisplayDimensions")
        res["ok"] = ok_e
        if not ok_e or en is None:
            res["error"] = str(en)[:120]
            continue
        try:
            items = list(en)
        except TypeError:
            res["error"] = "EnumDisplayDimensions 不可迭代"
            continue
        res["count"] = len(items)
        for it in items:
            ok_dim, dim = _try(get_com_member, it, "GetDimension")
            if ok_dim and dim is not None:
                ok_n, full = _try(lambda: str(dim.FullName))
                res["names"].append(full if ok_n else "")
    return res


def _relations(doc, sk) -> dict:
    """★ 关系数 + 类型清单。"""
    out: dict = {"count": None, "types": [], "error": None}
    ok_m, mgr = _try(get_com_member, sk, "RelationManager")
    if not ok_m or mgr is None:
        out["error"] = "取不到 ISketchRelationManager：%s" % str(mgr)[:80]
        return out
    ok_c, n = _try(get_com_member, mgr, "GetRelationsCount", -1)
    out["count"] = int(n) if ok_c and n is not None else None
    if not ok_c:
        out["error"] = "GetRelationsCount: %s" % str(n)[:100]
        return out
    ok_g, arr = _try(get_com_member, mgr, "GetRelations", -1)
    if ok_g and arr is not None:
        try:
            for rel in list(arr):
                ok_t, t = _try(get_com_member, rel, "GetRelationType")
                if ok_t:
                    out["types"].append(int(t))
        except TypeError:
            out["error"] = "GetRelations 不可迭代"
    return out


def _snapshot(doc, sk, label: str) -> dict:
    ok_s, st = _try(lambda: int(sk.GetConstrainedStatus))
    return {
        "label": label,
        "status": st if ok_s else None,
        "dims_next": _dims_via_next(doc),
        "dims_enum": _dims_via_enum(doc),
        "relations": _relations(doc, sk),
    }


def main() -> int:
    ev: dict = {"probe": "s3-autodim-why-fully-defined", "snapshots": []}
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
        sk = _active_sketch(doc)
        ev["snapshots"].append(_snapshot(doc, sk, "rectangle_100x60"))

        ok_ad, ret_ad = _try(
            lambda: get_com_member(sk, "AutoDimension2", 1, 1, -1, 1, -1)
        )
        ev["AutoDimension2"] = {"ok": ok_ad, "ret": str(ret_ad)[:60]}
        ev["snapshots"].append(_snapshot(doc, sk, "after_autodimension2"))

        #: 判读
        a, b = ev["snapshots"][0], ev["snapshots"][1]
        rel_a = a["relations"]["count"]
        rel_b = b["relations"]["count"]
        dim_a = len(a["dims_next"])
        dim_b = len(b["dims_next"])
        st_a, st_b = a["status"], b["status"]

        ev["verdict"] = {
            "status": "%s → %s" % (st_a, st_b),
            "dims_by_next": "%s → %s" % (dim_a, dim_b),
            "dims_by_enum": "%s → %s"
            % (
                (a["dims_enum"] or {}).get("count"),
                (b["dims_enum"] or {}).get("count"),
            ),
            "relations": "%s → %s" % (rel_a, rel_b),
            "relations_added": (rel_b or 0) - (rel_a or 0),
            "dims_added_by_next": dim_b - dim_a,
        }
        #: ★ 结论只在证据足够时下
        if st_b == 3 and dim_b == 1 and (rel_b or 0) <= (rel_a or 0):
            ev["conclusion"] = (
                "★ 关系没增加、尺寸只加了 1 个，状态却 2 → 3 ⇒ **尺寸遍历可能漏了**"
                "（路线二枚举若给出更多，以路线二为准）"
            )
        elif st_b == 3 and dim_b == 1 and (rel_b or 0) > (rel_a or 0):
            ev["conclusion"] = (
                "★★ **Autodim 同时加了关系**（+%d）⇒ 全约束有关系的份"
                " ⇒ 若靠 sgFIXED 堆出来，E1 会判 fail（「全固定但无驱动尺寸」）"
                % ((rel_b or 0) - (rel_a or 0))
            )
        else:
            ev["conclusion"] = "★ 读数见 snapshots，未归入已知两类"

        print("★ 结论：", ev["conclusion"])
        for k, v in ev["verdict"].items():
            print("  %-22s %s" % (k, v))
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1500:]
        print("★ 失败：", ev["err"])
        print(ev["traceback"])
        return 1
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
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-autodim-why-fully-defined.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())

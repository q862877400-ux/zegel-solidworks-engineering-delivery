"""★ B4 真机探针：在真零件上逐条跑「移动 / 旋转 / 缩放 / 伸展 / 镜像」。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_b4_sketch_modify.py
# 定位:   ★ 2026-10-03（轮 471）★ 给 `scripts/sw_sketch_modify_ops.py` 留真机证据。
#
#   ★★ **本探针的结构照抄 B1 的现成做法**（`tools/prove_b1_sketch_primitives.py`）——
#     那是本仓已被真机验证过的骨架：
#       · `sw, _ = connect_solidworks(wait_seconds=30)`（★ 它回**元组**）
#       · `new_document(sw, "part")` ⇒ **每个用例一个新文档**（★ 互不污染）
#       · `P.start_sketch(doc, plane_name="Front Plane")` / `P.end_sketch(doc)`
#         （★ 用本仓 `sw_part` 的包装，**不裸调** `SketchManager.InsertSketch`）
#       · **判据 = 几何读数**（B1 用段数增量；本探针用**草图点的 bbox**）
#
#   ★★ **为什么判据必须是几何读数**：★ 这 5 个成员里 **4 个的官方返回是 `void`**
#     （只有 `SketchModifyScale` 回 `bool`）⇒ ★ 光看"没抛异常"**证明不了几何动了**。
#     ⇒ ★ 本探针改量 **草图中所有点的包围盒**（`sw_sketch.get_sketch_segments` 取点）：
#       · 移动 ⇒ bbox **平移**（尺寸不变、中心变）
#       · 旋转 ⇒ bbox **变化**（角度变了包围盒就变）
#       · 缩放 ⇒ bbox **尺寸按比例变**
#       · 伸展 ⇒ bbox **某一维拉长**
#       · 镜像 ⇒ bbox **符号翻转**（★ 沿轴）
#   ⚠ 量不到就**如实写 `measured: false`**（★ 不假装量到了）。
# 官方依据: 见 `scripts/sw_sketch_modify_ops.py` 的模块头（三源逐条）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 每条回 `{"op","ok","verified_by","bbox_before","bbox_after"}`，产物落 `output/`。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                  # noqa: E402
from scripts import sw_part as P                                     # noqa: E402
from scripts import sw_sketch as SK                                  # noqa: E402
import scripts.sw_sketch_primitives as SP                            # noqa: E402
from scripts import sw_sketch_modify_ops as M                        # noqa: E402


def _transform(doc):
    """★ 量**草图坐标系在模型里的位姿**：`Sketch.ModelToSketchTransform.ArrayData`。

    ★★★ 2026-10-03（轮 472）**这才是移动/旋转/镜像的正确判据** ——
      官方对那三个成员的说明逐字是：
      > Translates / Rotates **the coordinate system** of the active or selected sketch.

      ⇒ ★★ **它们改的是**草图坐标系**，而**不改草图内点的坐标值****
        ⇒ ★★★ 故"草图内点的 bbox"（本探针第一版的判据）**根本测不出它们**
          —— ★ 那时 3 条记成 `geometry_unchanged`，★ **不是能力不行，是判据选错了** ⚠

    ★ 官方依据（`C:\\swapi\\types\\IMathTransform\\ArrayData.md`，逐字）：
      > Gets and sets the array of **16 doubles** for this transform.
      > The first **9** elements define the **3x3 rotation matrix**. The next **3** elements
      > define the **translation component**.
      ⇒ ★ 故 `[9:12]` = 平移 · `[0:9]` = 3×3 旋转 ✓

    ★★ 真机实测（矩形 `-20,-10 → 20,10`，本机）把这条判据**验穿了**：
      ```
      移动 5mm ⇒ 平移 [0,0,0] → [-0.005, -0.005, 0.0]     ★ 与传入 5mm 严格对得上
      旋转 30° ⇒ rot3 [1,0,0] → [0.866025, -0.500001, 0]   ★ 正是 cos30° / sin30°
      镜像     ⇒ rot3 [1,0,0] → [-1, 0, 0]                 ★ X 轴符号翻转
      ```
    ⚠ 取不到 ⇒ 回 `None`（★ 调用方写 `measured: false`，**不猜**）。
    """
    try:
        sk = C.get_com_member(C.get_com_member(doc, "SketchManager"), "ActiveSketch")
        if sk is None:
            return None
        tf = C.get_com_member(sk, "ModelToSketchTransform")
        if tf is None:
            return None
        arr = C.get_com_member(tf, "ArrayData")
        if arr is None:
            return None
        vals = [round(float(x), 6) for x in arr]
        if len(vals) < 12:
            return None
        return {"n": len(vals), "rot3x3": vals[:9], "trans": vals[9:12]}
    except Exception:                                                # noqa: BLE001
        return None


def _bbox(doc):
    """★ 量活动草图里**所有线段端点**的包围盒（★ 单位：**毫米**，原样，不换算）。

    ★★ 2026-10-03（轮 471）**形状是真机量出来的，不是读代码猜的** ——
      在真机上跑了一次诊断（矩形 `-20,-10 → 20,10`），`sw_sketch.get_lines(sk)` 回的是
      **`list[float]`**、**每 12 个数一条线**：
      ```
      [5.0, 2.0, 0.0, 0.0, -1.0, 31.0,  -20.0, -10.0, 0.0,  20.0, -10.0, 0.0]
       └──── 前 6 个：线段样式 / 类型 ────┘   └─ 点1 (x,y,z) ─┘   └─ 点2 (x,y,z) ─┘
      ```
      ⇒ ★ 后 6 个数**就是两个端点的坐标**，且**单位已经毫米**（`-20,-10,0` 正是那个角）。
    ⚠ 取不到 ⇒ 回 `None`（★ 调用方据此写 `measured: false`，**不猜**）。
    """
    try:
        sk = C.get_com_member(C.get_com_member(doc, "SketchManager"), "ActiveSketch")
        if sk is None:
            return None
        flats = SK.get_lines(sk) or []
        xs, ys = [], []
        for i in range(0, len(flats) - 11, 12):
            seg = flats[i:i + 12]
            xs.extend([float(seg[6]), float(seg[9])])
            ys.extend([float(seg[7]), float(seg[10])])
        if not xs:
            return None
        return {"x": [round(min(xs), 4), round(max(xs), 4)],
                "y": [round(min(ys), 4), round(max(ys), 4)],
                "n_lines": len(flats) // 12}
    except Exception:                                                # noqa: BLE001
        return None


def _changed(b, a):
    """★ 判据：包围盒**真的变了**吗（★ 变没变要比数，不比"有没有异常"）。"""
    if not b or not a:
        return None
    return b != a


def _one(sw, zh, fn):
    """★ 走 B1 现成的骨架：**每个用例一个新文档** ⇒ 互不污染、失败也不拖累。"""
    row = {"zh": zh, "verdict": "不能", "op": fn.__name__ if hasattr(fn, "__name__") else zh}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        #: ★ 一个矩形 ⇒ 有实体可操作（★ 用本仓现成的图元函数）
        SP.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)
        #: ★★★ 2026-10-03（轮 471）**量 bbox 必须在草图**打开**时** ——
        #:   官方对这几个成员的说明是 "Translates / Rotates … the coordinate system of the
        #:   **active or selected sketch**" ⇒ ★ 它们**要活动草图**。
        #:   ⚠ 我第一版把 `P.end_sketch(doc)` 放在量之前 ⇒ `ActiveSketch` 回 `None`
        #:     ⇒ 5 条全记成 `before=None / after=None`（★ 表现成"全都不能"，
        #:       而真因是**量错了时机** —— 不是能力不行）。
        #: ★★★ 两种判据**各管一半**（★ 这是轮 472 学到的）：
        #:   · **改坐标系**的（移动 / 旋转 / 镜像）⇒ 看 `ModelToSketchTransform.ArrayData`
        #:   · **改几何**的（缩放 / 伸展）      ⇒ 看草图点的 bbox
        #:   ★ 两个都量，然后**按"变没变"判** —— ★ 哪个变了算哪个（★ 不预设谁对）。
        bbox_before, tf_before = _bbox(doc), _transform(doc)
        r = fn(doc)
        bbox_after, tf_after = _bbox(doc), _transform(doc)
        P.end_sketch(doc)
        ch_bbox = _changed(bbox_before, bbox_after)
        ch_tf = _changed(tf_before, tf_after)
        row.update({"ret": r if isinstance(r, (dict, bool, type(None))) else str(type(r)),
                    "bbox_before": bbox_before, "bbox_after": bbox_after,
                    "tf_before": tf_before, "tf_after": tf_after,
                    "bbox_changed": ch_bbox, "transform_changed": ch_tf})
        #: ★★ 判据分级（★ 说清"凭什么说能"）：
        #:   · 量到了前后 **且变了**（bbox 或 变换）⇒ `geometry_changed` / `transform_changed`
        #:   · 量到了而**都没变** ⇒ ★ 如实记 `unchanged`（★ 那才可能是"真不能"）
        #:   · 量不到 ⇒ `no_exception`（★ 最弱，且写明）
        if ch_bbox:
            row["verified_by"] = "bbox_changed"
        elif ch_tf:
            row["verified_by"] = "transform_changed"
        elif ch_bbox is False or ch_tf is False:
            row["verified_by"] = "unchanged"
        else:
            row["verified_by"] = "no_exception"
        row["ok"] = bool(ch_bbox or ch_tf)
        row["verdict"] = "能" if row["ok"] else "不能"
    except Exception as exc:                                         # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    finally:
        if doc is not None:
            try:
                t = str(C.safe_get_com_member(doc, "GetTitle") or "") \
                    if hasattr(C, "safe_get_com_member") else ""
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:                                        # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"),
          "_": "B4 批：草图编辑·移动族 5 条逐个真机跑（specs/201-toolbar-gaps）",
          "judge": "草图点包围盒的前后变化（★ 因为 4/5 的官方返回是 void）",
          "items": []}
    ev["items"].append(_one(sw, "移动实体", lambda d: M.sketch_move(d, 0.0, 0.0, 5.0, 5.0)))
    ev["items"].append(_one(sw, "旋转实体", lambda d: M.sketch_rotate(d, 0.0, 0.0, 30.0)))
    ev["items"].append(_one(sw, "缩放实体比例", lambda d: M.sketch_scale(d, 1.5)))
    ev["items"].append(_one(sw, "伸展实体", lambda d: M.sketch_stretch(d, 0.0, 0.0, 3.0, 3.0, True)))
    ev["items"].append(_one(sw, "镜像（同族附带）", lambda d: M.sketch_flip(d, 1)))
    ev["passed"] = sum(1 for i in ev["items"] if i.get("ok"))
    ev["total"] = len(ev["items"])
    p = R / "output" / "b4-sketch-modify-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  \u8bda\u5b9e %s / %s" % (ev["passed"], ev["total"]))
    for i in ev["items"]:
        print("  %-18s %-4s %-18s %s" % (i.get("zh"), i.get("verdict"),
                                         i.get("verified_by") or "", (i.get("err") or "")[:52]))
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

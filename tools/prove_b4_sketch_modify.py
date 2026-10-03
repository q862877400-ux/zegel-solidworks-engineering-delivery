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
        before = _bbox(doc)
        r = fn(doc)
        after = _bbox(doc)
        P.end_sketch(doc)
        ch = _changed(before, after)
        row.update({"ret": r if isinstance(r, (dict, bool, type(None))) else str(type(r)),
                    "bbox_before": before, "bbox_after": after,
                    "measured": before is not None and after is not None,
                    "bbox_changed": ch})
        #: ★★ 判据分级（★ 说清"凭什么说能"）：
        #:   · 量到了前后 bbox **且变了** ⇒ `geometry_changed`（最强）
        #:   · 量到了而**没变** ⇒ ★ **如实记 `geometry_unchanged`**（★ 那可能是"没选中实体"）
        #:   · 量不到 ⇒ `no_exception`（★ 最弱，且写明）
        row["verified_by"] = ("geometry_changed" if ch else
                              ("geometry_unchanged" if ch is False else "no_exception"))
        row["ok"] = bool(ch)
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

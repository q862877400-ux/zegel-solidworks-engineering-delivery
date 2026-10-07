"""★ 探针：只读问清 `GetBodies2` / `GetFaces` / `GetBox` / `GetFeatureCount` 的形态。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/probe_spec220_member_shape.py
# 定位:   ★ 规格 220 **T-220-01 第 2 试**的**前置只读探针** —— ★ 上一轮两档都抛
#         `'tuple' object is not callable` ⇒ ★ 先问清成员形态再改代码（★ 不猜）✓
# 官方依据: ★ 官方页只说成员**存在**；★ "pywin32 迟到绑定下它暴露成属性还是方法"**只能实测** ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_connect                                                                  # noqa: E402
import tool_caller                                                                 # noqa: E402

RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}


def shape(obj, name: str) -> dict:
    """★ 问一个成员是"可调用的方法"还是"属性/元组" ✓"""
    attr = getattr(obj, name, "<没有这个成员>")
    info = {"repr_head": str(attr)[:70], "callable": callable(attr),
            "type": type(attr).__name__}
    if callable(attr):
        for args in ((), (0, False), (0,)):
            try:
                if args == ():
                    v = attr()
                elif args == (0, False):
                    v = attr(0, False)
                else:
                    v = attr(0)
                info["call%s" % (args,)] = "%s · len=%s" % (type(v).__name__,
                                                            len(v) if hasattr(v, "__len__") else "n/a")
                break
            except Exception as exc:                                               # noqa: BLE001
                info["call%s" % (args,)] = "✗ %s" % str(exc)[:60]
    return info


def main() -> int:
    out = {}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (("solidworks_sketch_start", {}),
                         ("solidworks_sketch_add_rectangle", RECT),
                         ("solidworks_extrude_boss", {"sketch_name": "Sketch1", "depth_mm": 20.0})):
        ok, note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建板没成：%s" % step)
            return 1

    out["model.GetFeatureCount"] = shape(model, "GetFeatureCount")
    out["model.GetBodies2"] = shape(model, "GetBodies2")
    bodies = None
    try:
        b = model.GetBodies2
        bodies = list(b) if hasattr(b, "__len__") else [b]
        out["bodies_len"] = len(bodies)
    except Exception as exc:                                                       # noqa: BLE001
        out["bodies_len"] = "✗ %s" % str(exc)[:70]
    if bodies:
        body = bodies[0]
        out["body.GetFaces"] = shape(body, "GetFaces")
        try:
            fs = body.GetFaces
            faces = list(fs) if hasattr(fs, "__len__") else [fs]
            out["faces_len"] = len(faces)
            if faces:
                f0 = faces[0]
                out["face.GetBox"] = shape(f0, "GetBox")
        except Exception as exc:                                                   # noqa: BLE001
            out["faces_len"] = "✗ %s" % str(exc)[:70]

    #: ★ 对照：本仓**已验证**的面选择助手在不在、签名是什么
    try:
        import inspect
        import sw_part
        out["sw_part.select_face_by_index_mark1"] = str(
            inspect.signature(sw_part.select_face_by_index_mark1))[:90]
    except Exception as exc:                                                       # noqa: BLE001
        out["sw_part.select_face_by_index_mark1"] = "✗ %s" % str(exc)[:70]

    for k, v in out.items():
        print("★ %-38s %s" % (k, json.dumps(v, ensure_ascii=False)[:150]))
    p = ROOT / "output" / "spec220-member-shape.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    try:
        sw.CloseAllDocuments(True)
        out["closed"] = True
    except Exception:                                                              # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

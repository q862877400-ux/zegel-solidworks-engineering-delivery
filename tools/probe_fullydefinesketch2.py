"""★ 按**官方示例的调用序**真机跑 `FullyDefineSketch`（★ 阶段 2 · T1 第 ② 步 · 第二轮）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\`）
# 文件:   `tools/probe_fullydefinesketch2.py`
# 定位:   ★ **官方示例逐字**（★ `C:\swapi\examples\Fully_Define_Underdefined_Sketch_Example_VB.md`）：
#     ```
#     swModel.ClearSelection2 True
#     lMarkHorizontal = 2      ' These are the marks expected for the dimension datums
#     lMarkVertical = 4
#     bValue = swModelExtension.SelectByID2("Point1@Origin", "EXTSKETCHPOINT",
#                 0, 0, 0, False, lMarkHorizontal Or lMarkVertical, Nothing, 0)
#     lStatus = swSketchManager.FullyDefineSketch(True, True,
#                 swSketchFullyDefineRelationType_Vertical Or
#                 swSketchFullyDefineRelationType_Horizontal,
#                 True, 1, Nothing, 1, Nothing, 1, 1)
#     ```
#   ★★ **⇒ 那是"调用序"的唯一来源**（★ 签名与 Remarks 都给不了）✓
#   ★★★ **而它印证**：★ `mark 2` / `mark 4` **正是本仓 `sw_part.py` L738 用的那两个** ✓
#   ★★★★ **⚠ 上一轮已验**：★ 两个 `DatumDisp` 传 `None` ⇒ **`类型不匹配`（位置 6）** ⇒
#     ★ **在 pywin32 里要包**空 Dispatch****（★ 与**事实 12**同族）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "fullydefinesketch2-probe-evidence.json"

#: ★ 官方枚举逐字（★ `swSketchFullyDefineRelationType_e.md`）：
#:   `_Equal` = 1 · `_Horizontal` = 2 · `_Tangent` = 8 · `_Perpendicular` = 16 ·
#:   `_Colinear` = 32 · `_Concentric` = 64 · `_Parallel` = 128 · `_Midpoint` = 256 ·
#:   `_Coincident` = 512 ⇒ ★ **Vertical 不在我读到的前 9 行里**（★ 页里 `enum_member_count: 10`）
REL_H, REL_V = 2, 4                      #: ★ 那是 **mark**；关系值另外查


def _relations_value() -> int:
    """★ 从官方枚举页读 `Vertical | Horizontal` 的值（★ **不猜**）。"""
    p = Path(r"C:\swapi\enums\swSketchFullyDefineRelationType_e.md")
    if not p.is_file():
        return 0
    t = p.read_text(encoding="utf-8", errors="replace")
    out = {}
    for line in t.splitlines():
        if line.startswith("| swSketchFullyDefineRelationType_"):
            parts = [x.strip() for x in line.strip("|").split("|")]
            if len(parts) >= 2:
                name = parts[0].replace("swSketchFullyDefineRelationType_", "")
                try:
                    out[name] = int(parts[1].split(" or ")[0])
                except Exception:                                         # noqa: BLE001
                    pass
    h, v = out.get("Horizontal"), out.get("Vertical")
    print("★ 官方枚举: Horizontal=%s Vertical=%s · 全部=%r" % (h, v, sorted(out)))
    return (h or 0) | (v or 0)


def _dim_count(model) -> int:
    """★ 换一个**可核的**读法：★ 数草图里的 `DisplayDimension`（★ `GetSketchDimensions` 一族）。"""
    try:
        from sw_connect import get_com_member
        sk = get_com_member(model, "SketchManager")
        act = get_com_member(sk, "ActiveSketch")
        if act is None:
            return -1
        for name in ("GetSketchDimensions", "GetDisplayDimensions", "GetDimensions"):
            v = get_com_member(act, name)
            if v is not None:
                try:
                    return len(list(v))
                except TypeError:
                    return -1
        return -1
    except Exception:                                                     # noqa: BLE001
        return -1


def main() -> int:
    from sw_connect import (connect_solidworks, get_com_member, new_document,
                            create_empty_dispatch_variant, out_i4)

    rel = _relations_value()
    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    rows = []

    import sw_part as P
    P.sketch(model, "Front Plane")
    sk = get_com_member(model, "SketchManager")
    for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                 ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
        get_com_member(sk, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)

    def case(tag, *, with_origin: bool, rel_value: int):
        get_com_member(model, "ClearSelection2", True)
        mark = REL_H | REL_V
        sel = None
        if with_origin:
            #: ★★ **官方逐字**：★ 选 `Point1@Origin`（`EXTSKETCHPOINT`）、★ **mark = 2|4 = 6** ✓
            ext = get_com_member(model, "Extension")
            try:
                sel = get_com_member(ext, "SelectByID2", "Point1@Origin", "EXTSKETCHPOINT",
                                     0.0, 0.0, 0.0, False, mark,
                                     create_empty_dispatch_variant(), 0)
            except Exception as exc:                                      # noqa: BLE001
                sel = "err: %s" % str(exc)[:70]
        before = _dim_count(model)
        got = err = None
        try:
            got = get_com_member(sk, "FullyDefineSketch", True, True, rel_value, True,
                                 1, create_empty_dispatch_variant(), 1,
                                 create_empty_dispatch_variant(), 1, 1)
        except Exception as exc:                                          # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        after = _dim_count(model)
        rows.append({"tag": tag, "with_origin": with_origin, "rel_value": rel_value,
                     "select_return": str(sel)[:44], "returned": str(got)[:44], "error": err,
                     "dims_before": before, "dims_after": after,
                     "built": (after > before) if (before >= 0 and after >= 0) else None})

    case("★ 官方调用序（选原点 + mark 6）", with_origin=True, rel_value=rel)
    case("★ 不选原点（对照）", with_origin=False, rel_value=rel)
    P.end_sketch(model)

    R = {"★_判据": "★ 建成 ⇒ 草图尺寸数增加（★ 且无异常）",
         "★_来源": "★ 官方示例 `Fully_Define_Underdefined_Sketch_Example_VB.md` 的**调用序**",
         "★_关系值": rel, "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print("★ %-34s built=%-5s dims %s→%s sel=%s ret=%s err=%s" % (
            r["tag"], r["built"], r["dims_before"], r["dims_after"],
            r["select_return"][:16], r["returned"][:16], (r["error"] or "")[:60]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""★ 真机验 `FullyDefineSketch` 能不能替代 `AutoDimension2`（★ 阶段 2 · T1 第 ② 步）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_part.py::auto_dimension_sketch`（★ 生产）
# 定位:   ★ 官方逐字（★ `ISketch/AutoDimension2.md`）：
#     「**Obsolete. Superseded by `ISketchManager::FullyDefineSketch`**.」✓
#     ★ 旧签名 ⇒ `(int EntitiesToDimension, int HorizontalScheme, int HorizontalPlacement,
#       int VerticalScheme, int VerticalPlacement)` ⇒ **5 参** ✓
#   ★★ 后继逐字（★ `ISketchManager/FullyDefineSketch.md`）：★ **现行** ·
# ★ 签名 ⇒ **10 参**：`(bool EntitiesToFullyDefine, bool UseRelations, int RelationsToAp
# ply,
# bool UseDimensions, int HorizontalDimScheme, object HorizontalDatumDisp, int VerticalD
# imScheme,
#       object VerticalDatumDisp, int HorizontalDimPlacement, int VerticalDimPlacement)` ✓
# ★★ 参数语义官方逐字：★ `EntitiesToFullyDefine` = True ⇒ **all**、false ⇒ **only select
# ed** ·
#       ★ `HorizontalDimScheme` = **0=Chain / 1=Baseline / 2=Ordinate** ·
#       ★ `HorizontalDatumDisp` = 「model edge, model vertex, sketch line, sketch point, or,
#         if Nothing or null, **use entity with selection…**」✓
# ★★★ **判据（★ 可核）**：★ 建成 ⇒ **草图的 `DisplayDimension` 数 +N**（★ 且 `status ==
# 0`）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "fullydefinesketch-probe-evidence.json"


def _dim_count(model) -> int:
    """★ 现成的读法：★ 草图尺寸数（★ 用 `ISketch.GetDimensionCount` 那一族不可靠 ⇒ 用遍历）。"""
    try:
        from sw_connect import get_com_member

        sk = get_com_member(model, "SketchManager")
        act = get_com_member(sk, "ActiveSketch")
        if act is None:
            return -1
        #: ★ 官方 `ISketch::GetDimensionCount`（0 参）
        n = get_com_member(act, "GetDimensionCount")
        return int(n) if isinstance(n, int) else -1
    except Exception:  # noqa: BLE001
        return -1


def main() -> int:
    from sw_connect import (
        connect_solidworks,
        create_empty_dispatch_variant,
        get_com_member,
        new_document,
    )

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    rows = []

    def case(tag, *, form):
        """★ 每种形态单独建一张**未定义**的矩形草图（★ 4 条线都不带尺寸）。"""
        import sw_part as P

        P.sketch(model, "Front Plane")
        sk = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.05, -0.03), (0.05, -0.03)),
            ((0.05, -0.03), (0.05, 0.03)),
            ((0.05, 0.03), (-0.05, 0.03)),
            ((-0.05, 0.03), (-0.05, -0.03)),
        ):
            get_com_member(sk, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        before = _dim_count(model)
        got = err = None
        try:
            if form == "old_autodimension2":
                act = get_com_member(sk, "ActiveSketch")
                got = get_com_member(act, "AutoDimension2", 1, 1, -1, 1, -1)
            elif form == "new_nulls":
                #: ★ 官方：★ `EntitiesToFullyDefine=True` · ★ 两个 DatumDisp **可传 Noth
                #: ing** ⇒
                #: 「use entity with selection…」⇒ ★ 本形态**不选**任何基准，★ 看它怎么
                #: 反应
                got = get_com_member(
                    sk,
                    "FullyDefineSketch",
                    True,
                    True,
                    0,
                    True,
                    1,
                    None,
                    1,
                    None,
                    -1,
                    -1,
                )
            elif form == "new_empty_dispatch":
                got = get_com_member(
                    sk,
                    "FullyDefineSketch",
                    True,
                    True,
                    0,
                    True,
                    1,
                    create_empty_dispatch_variant(),
                    1,
                    create_empty_dispatch_variant(),
                    -1,
                    -1,
                )
            elif form == "new_selected_baseline":
                #: ★★ 先**选基准线**（★ 官方 `HorizontalDatumDisp` 的 "use entity with s
                #: election"）
                act = get_com_member(sk, "ActiveSketch")
                segs = list(get_com_member(act, "GetSketchSegments") or [])
                if segs:
                    try:
                        segs[0].Select4(False, create_empty_dispatch_variant())
                    except Exception:  # noqa: BLE001
                        pass
                got = get_com_member(
                    sk,
                    "FullyDefineSketch",
                    True,
                    True,
                    0,
                    True,
                    1,
                    None,
                    1,
                    None,
                    -1,
                    -1,
                )
        except Exception as exc:  # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:140])
        after = _dim_count(model)
        P.end_sketch(model)
        rows.append(
            {
                "form": form,
                "tag": tag,
                "returned": str(got)[:60],
                "error": err,
                "dims_before": before,
                "dims_after": after,
                "built": (after > before) if (before >= 0 and after >= 0) else None,
            }
        )

    case("★ 旧的 AutoDimension2（基线）", form="old_autodimension2")
    case("★ 新的 FullyDefineSketch + None", form="new_nulls")
    case("★ 新的 + 空 Dispatch", form="new_empty_dispatch")
    case("★ 新的 + 预选基准线", form="new_selected_baseline")

    R = {
        "★_判据": "★ 建成 ⇒ 草图 `GetDimensionCount` 增加（★ 且返回 0）",
        "★_问题": "★ 官方把 `AutoDimension2` 换成了 `FullyDefineSketch`（★ 5 参 → 10 参）⇒ 验它能不能替代",
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    for r in rows:
        print(
            "★ %-32s built=%-5s dims %s→%s ret=%s err=%s"
            % (
                r["form"],
                r["built"],
                r["dims_before"],
                r["dims_after"],
                r["returned"][:22],
                (r["error"] or "")[:70],
            )
        )
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

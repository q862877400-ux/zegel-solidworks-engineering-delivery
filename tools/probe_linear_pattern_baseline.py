"""★ 按**官方示例的调用序**把「线性阵列」建成（★ 阶段 2 · T1 · 补基线）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\`）
# 文件:   `scripts/sw_part.py::linear_pattern`（★ 生产）
# 定位:   ★★★★ **官方示例逐字**（★ `C:\swapi\examples\Change_Linear_Pattern_Example_VB
#           .md`）：
#     ```
#     swModel.ClearSelection2 True
#     status = swModelDocExt.SelectByID2("", "EDGE", x, y, z, True, 1,   Nothing, 0)
#     status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY",
#                                        0, 0, 0, True, 256, Nothing, 0)
#     Set swFeature = swFeatureMgr.FeatureLinearPattern4(
#         3, 0.0254, 1, 0.00254, True, False, "NULL", "NULL", False, False,
#         False, False, False, False, True, True, False, False, 0, 0)
#     ```
#   ★★ **⇒ 调用序与两个 mark 都在示例里**（★ 签名与 Remarks 都给不全）✓
#   ★★★ **与 Remarks 的关系**：★ Remarks 说 `4 to mark the features to pattern`、
# ★★ **而示例对 `SOLIDBODY` 用 `256`** ⇒ ★ **两种 mark 都对、★ 取决于选的是特征还是体**
# ✓
#   ★★★★ **为什么要这个探针**：★ 上一轮真机上**四条形态全没建成**（★ **含基线**）⇒
#     ★★ **本仓的"阵列"这条链**从未真机验证过** ⇒ ★ **先补基线、★ 再谈换代** ✓
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

OUT = REPO / "output" / "linear-pattern-baseline-evidence.json"


def _feature_names(model):
    from sw_connect import get_com_member

    out, f = [], get_com_member(model, "FirstFeature")
    while f is not None and len(out) < 400:
        try:
            out.append(str(get_com_member(f, "Name")))
        except Exception:  # noqa: BLE001
            pass
        f = get_com_member(f, "GetNextFeature")
    return out


def _bodies(model):
    from sw_connect import get_com_member

    try:
        return list(get_com_member(model, "GetBodies2", 0, False) or [])
    except Exception:  # noqa: BLE001
        return []


def main() -> int:
    from sw_connect import (
        connect_solidworks,
        get_com_member,
        new_document,
        create_empty_dispatch_variant,
    )
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    rows = []

    def case(tag, *, form):
        model = new_document(app, "part")
        #: ★ 脚手架：★ 一块板（★ 用**上下文管理器** —— 上一轮的教训）
        with P.sketch(model, "Front Plane") as sk1:
            sm = get_com_member(model, "SketchManager")
            for a, b in (
                ((-0.05, -0.03), (0.05, -0.03)),
                ((0.05, -0.03), (0.05, 0.03)),
                ((0.05, 0.03), (-0.05, 0.03)),
                ((-0.05, 0.03), (-0.05, -0.03)),
            ):
                get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        P.extrude_boss(model, sk1, 10.0)
        body = (_bodies(model) or [None])[0]
        before = _feature_names(model)
        ext = get_com_member(model, "Extension")
        sel = {}
        got = err = None
        try:
            #: ★★★ 官方调用序第 1 步 ✓
            get_com_member(model, "ClearSelection2", True)
            #: ★★★★ 官方调用序第 2 步：★ **方向用 `mark=1`** ✓
            #: 示例用的是 `("", "EDGE", <点>)` —— ★ 本处换成**按面上的点选**（★ 事实 32
            #: ：
            #:   按名字选边**不行**）⇒ 但示例那样写在它那个模型上是成的 ⇒ **两种都试** ✓
            sel["dir_by_point"] = bool(
                get_com_member(
                    ext,
                    "SelectByID2",
                    "",
                    "EDGE",
                    -0.05,
                    0.0,
                    0.0,
                    True,
                    1,
                    create_empty_dispatch_variant(),
                    0,
                )
            )
        except Exception as exc:  # noqa: BLE001
            sel["dir_by_point"] = "err: %s" % str(exc)[:60]
        try:
            #: ★★★★★ 官方调用序第 3 步：★ **要阵列的体用 `mark=256`**（★ 示例逐字）✓
            #: ★★ 而 `SOLIDBODY` 的"名字"—— ★ 真机物没有名字 ⇒ ★ **按对象选**（★ 事实 32
            #: ）✓
            #:   ★★★ **⚠ 选实体的成员是 `IBody2::Select`、★ 不是 `Select4`** ——
            #:     ★ 官方逐字（★ `C:\swapi\types\IBody2\Select.md`）：
            #: ★ `System.bool Select( System.bool Append, System.int Mark )` ⇒ **2 参、
            #: 带 Mark** ✓
            #:     ★★ 而 `Select2(Append, SelectData)` 要一个 `SelectData` 对象 ✓
            #:     ⇒ ★★★ **我第一版写的 `Select4` 报 `err: GetBodies2.Select4`** ——
            #:       ★★ **那是"我调错了成员"、★ 不是"实体选不了"**（★ 事实 517 第 N 次）✓
            if body is not None:
                sel["body_Select(True,256)"] = bool(body.Select(True, 256))
            else:
                sel["body_Select(True,256)"] = "★ 没有实体"
        except Exception as exc:  # noqa: BLE001
            sel["body_Select(True,256)"] = "err: %s" % str(exc)[:60]
        try:
            sel["sel_count"] = int(
                get_com_member(
                    get_com_member(model, "SelectionManager"),
                    "GetSelectedObjectCount2",
                    -1,
                )
            )
        except Exception as exc:  # noqa: BLE001
            sel["sel_count"] = "err: %s" % str(exc)[:50]
        try:
            fm = get_com_member(model, "FeatureManager")
            if form == "linear4_20":
                #: ★ 官方示例**逐字**的 20 参（★ 只把方向改成真方向、★ 间距按本处尺度）✓
                got = get_com_member(
                    fm,
                    "FeatureLinearPattern4",
                    2,
                    0.02,
                    1,
                    0.0,
                    False,
                    False,
                    "NULL",
                    "NULL",
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    True,
                    True,
                    False,
                    False,
                    0.0,
                    0.0,
                )
            elif form == "linear3_10":
                got = get_com_member(
                    fm,
                    "FeatureLinearPattern3",
                    2,
                    0.02,
                    1,
                    0.0,
                    False,
                    False,
                    "",
                    "",
                    False,
                    False,
                )
            elif form == "linear5_22":
                got = get_com_member(
                    fm,
                    "FeatureLinearPattern5",
                    2,
                    0.02,
                    1,
                    0.0,
                    False,
                    False,
                    "NULL",
                    "NULL",
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    False,
                    0.0,
                    0.0,
                    False,
                    False,
                )
        except Exception as exc:  # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        after = _feature_names(model)
        new = [n for n in after if n not in before]
        rows.append(
            {
                "form": form,
                "tag": tag,
                "select": sel,
                "returned": str(got)[:40],
                "error": err,
                "features_before": len(before),
                "features_after": len(after),
                "new_features": new[:4],
                "built": bool(new),
            }
        )

    case("★ 官方示例的 20 参 `FeatureLinearPattern4`", form="linear4_20")
    case("★ 旧的 10 参 `FeatureLinearPattern3`", form="linear3_10")
    case("★ 新的 22 参 `FeatureLinearPattern5`", form="linear5_22")

    R = {
        "★_判据": "★ 建成 ⇒ 特征树多出新特征（★ 含 `LPattern` 一类）",
        "★_调用序来源": "★ 官方示例 `Change_Linear_Pattern_Example_VB.md`（★ 含两个 mark：方向 1 / 实体 256）",
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    for r in rows:
        print(
            "★ %-38s built=%-5s feats %s→%s"
            % (r["form"], r["built"], r["features_before"], r["features_after"])
        )
        print(
            "     sel=%s new=%s err=%s"
            % (
                json.dumps(r["select"], ensure_ascii=False)[:70],
                str(r["new_features"])[:30],
                (r["error"] or "")[:60],
            )
        )
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

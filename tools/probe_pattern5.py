"""★ 真机验 `FeatureLinearPattern5` / `FeatureCircularPattern5` 能不能替代 `3` / `4`。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeatureManager\`）
# 文件:   `scripts/sw_part.py::linear_pattern` / `circular_pattern`（★ 生产）
# 定位:   ★ **官方链**（★ 按接口限定地追 —— ★ 上轮的判据）：
#     ★ `FeatureLinearPattern3` 废弃 ⇒ `4` · ★ `4` 废弃 ⇒ `5` · ★★ **`5` 废弃、★ 后继空** ✓
#     ★ `FeatureCircularPattern4` 废弃 ⇒ `5` · ★★ **`5` 废弃、★ 后继空** ✓
#   ★★ **⇒ 按铁律 4 查反射裁决**（★ 最高代是哪个）：
#     ★ `FeatureLinearPattern` ⇒ 8/9/10/**20**/**22** ⇒ ★★ **`5` 是最高代（★ 无 `6`）** ✓
#     ★ `FeatureCircularPattern` ⇒ 4/5/6/7/**14** ⇒ ★★ **`5` 是最高代** ✓
#     ⇒ ★★★ **∴ "5 也废弃"是官方**没清状态标记**、★ 而它**就是现行可用那代**** ✓
#   ★★★ **参数对位**（★ 官方签名逐字）：★ `FeatureLinearPattern5` **22 参** ⇒
#     ★★ **前 10 参与 `3` 代逐字相同**、★ 新增 12 个是开关 ✓
#   ★★★★ **判据（★ 用本仓**已有**的那条）**：★ **特征树回读** ——
#     ★ `FeatureLinearPattern3` 那条注释逐字：★ 「**没抛错而特征树没变** ⇒ **阵列没建成**」✓
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

OUT = REPO / "output" / "pattern5-probe-evidence.json"


def _feature_names(model):
    """★ 特征名列表（★ 本仓一贯的判据）。"""
    from sw_connect import get_com_member
    out, f = [], get_com_member(model, "FirstFeature")
    while f is not None and len(out) < 400:
        try:
            out.append(str(get_com_member(f, "Name")))
        except Exception:                                                 # noqa: BLE001
            pass
        f = get_com_member(f, "GetNextFeature")
    return out


def _make_block(model, tag):
    """★ 脚手架：★ 建一块**带凸台的板**（★ 阵列需要有一个可阵的特征）。"""
    from sw_connect import get_com_member
    import sw_part as P
    with P.sketch(model, "Front Plane") as sk1:
        sm = get_com_member(model, "SketchManager")
        for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                     ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk1, 10.0)
    with P.sketch(model, "Front Plane") as sk2:
        sm = get_com_member(model, "SketchManager")
        get_com_member(sm, "CreateCircleByRadius", -0.03, 0.0, 0.0, 0.008)
    P.extrude_boss(model, sk2, 10.0)
    return tag, sk1, sk2


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document, out_i4

    app, _ = connect_solidworks(visible=True)
    rows = []

    def case(tag, *, form):
        model = new_document(app, "part")
        try:
            _make_block(model, tag)
        except Exception as exc:                                          # noqa: BLE001
            rows.append({"form": form, "tag": tag, "scaffold": "err: %s" % str(exc)[:110],
                         "built": None})
            return
        before = _feature_names(model)
        fm = get_com_member(model, "FeatureManager")
        #: ★★★★★ 官方 `FeatureLinearPattern3.md` 的 `## Remarks` **逐字给了 mark 表**：
        #: ★ 「Using `IModelDocExtension::SelectByID2` to select features and components
        #: ,
        #:      **ordered selection** of the features and components is required」
        #:   · ★ **`1 and 2 to mark the directions`** ⇒ **方向用 mark 1 / 2** ✓
        #:   · ★★ **`4 to mark the features to pattern`** ⇒ **要阵列的特征用 mark 4** ✓
        #:   · ★★★ 而直接选特征可用 `IFeature::Select2` ✓
        #:   ⇒ ★★★★ **⇒ 我第一版**漏了这一步**（★ 只读了签名、★ 没读 Remarks）⇒
        #:     ★ 而**基线也立不起来**就是它** ⇒ ★ 补上 `mark=4` 选那个凸台特征 ✓
        picked = None
        try:
            f = get_com_member(model, "FirstFeature")
            target = None
            while f is not None:
                nm = str(get_com_member(f, "Name"))
                if "凸台" in nm or "Boss" in nm:
                    target = f
                f = get_com_member(f, "GetNextFeature")
            if target is not None:
                #: ★ `IFeature::Select2(Append, Mark)` —— ★ 官方 Remarks 指的正是它 ✓
                picked = bool(get_com_member(target, "Select2", False, 4))
        except Exception as exc:                                          # noqa: BLE001
            picked = "err: %s" % str(exc)[:70]
        got = err = None
        try:
            if form == "linear3_10":
                got = get_com_member(fm, "FeatureLinearPattern3",
                                     2, 0.02, 1, 0.0, False, False, "", "", False, False)
            elif form == "linear5_22":
                #: ★★ **前 10 参**逐字同 `3` 代** + 12 个中性值 ✓
                got = get_com_member(fm, "FeatureLinearPattern5",
                                     2, 0.02, 1, 0.0, False, False, "", "", False, False,
                                     False, False, False, False, False, False,
                                     False, False, 0.0, 0.0, False, False)
            elif form == "circular4_7":
                got = get_com_member(fm, "FeatureCircularPattern4",
                                     4, 6.283185307179586, False, "", False, True, False)
            elif form == "circular5_14":
                #: ★ 官方 14 参：★ `(Number, Spacing, FlipDirection, DName, GeometryPatt
                #: ern,
                #:   EqualSpacing, VaryInstance, SyncSubAssemblies, BDir2, BSymmetric,
                #:   Number2, Spacing2, DName2, EqualSpacing2)` ✓
                got = get_com_member(fm, "FeatureCircularPattern5",
                                     4, 6.283185307179586, False, "", False, True, False,
                                     False, False, False, 1, 0.0, "", True)
        except Exception as exc:                                          # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:120])
        after = _feature_names(model)
        new = [n for n in after if n not in before]
        rows.append({"form": form, "tag": tag, "scaffold": "ok",
                     "returned": str(got)[:40], "error": err,
                     "features_before": len(before), "features_after": len(after),
                     "new_features": new[:4],
                     "built": bool(new)})

    case("★ 线性 · 旧的 10 参 `3`（基线）", form="linear3_10")
    case("★ 线性 · 新的 22 参 `5`", form="linear5_22")
    case("★ 圆周 · 旧的 7 参 `4`（基线）", form="circular4_7")
    case("★ 圆周 · 新的 14 参 `5`", form="circular5_14")

    R = {"★_判据": "★ 建成 ⇒ **特征树多出新特征**（★ 本仓原有判据：★ 没抛错而树没变 ⇒ 没建成）",
         "★_反射裁决": "★ `FeatureLinearPattern` 最高 22 参（5 代）· `FeatureCircularPattern` 最高 14 参（5 代）",
         "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print("★ %-34s built=%-5s feats %s→%s new=%s err=%s" % (
            r["form"], r.get("built"), r.get("features_before"), r.get("features_after"),
            str(r.get("new_features"))[:40], (r.get("error") or "")[:60]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

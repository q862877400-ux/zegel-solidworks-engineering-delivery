"""★ 真机验 `FeatureFillet3` 能不能替代 `FeatureFillet`（★ 阶段 2 · T1 第 ② 步）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeatureManager\FeatureFillet3.md`）
# 文件:   `scripts/sw_part.py::fillet`（★ 生产）
# 定位:   ★ **官方逐字**：★ `FeatureFillet` 废弃 ⇒ `2` · ★ `FeatureFillet2` 废弃 ⇒ `3` ·
#     ★★ **`FeatureFillet3` **不废弃**** ✓
#   ★★ **而 `IModelDoc2` 上还有另一族同名**（★ 5/7/9/13/7 参）⇒ ★★★ **按**铁律 4**查反射**：
#     ★ `IFeatureManager` 上 ⇒ `FeatureFillet`(7) / `2`(11) / **`3`(14)** ✓
#     ★★ **⚠ 那也正是本会话"环形链"的真因** —— ★ 跨族跳转（★ `IModelDoc2.FeatureFillet`
#       的后继写的是 `IFeatureManager::FeatureFillet`）✓
#   ★★★ **官方 14 参逐字**（★ `FeatureFillet3.md`）：
#     `(int Options, double R1, double R2, double Rho, int Ftyp, int OverflowType, int ConicRhoType,
#       object Radii, object Dist2Arr, object RhoArr, object SetBackDistances,
#       object PointRadiusArray, object PointDist2Array, object PointRhoArray)` ✓
#   ★★★★ **判据（★ 可核、★ 与 `FeatureCutThicken` 那次同法）**：★ 特征树**增量** ✓
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

OUT = REPO / "output" / "featurefillet3-probe-evidence.json"


def _body_count(model) -> int:
    """★ 实体数（★ `GetBodies2(swSolidBody=0, False)`）。"""
    try:
        from sw_connect import get_com_member
        v = get_com_member(model, "GetBodies2", 0, False)
        return len(list(v)) if v is not None else 0
    except Exception:                                                     # noqa: BLE001
        return -1


def _active_or_last_sketch(model) -> str:
    """★ 从特征树读**草图真名**（★ 中文 UI 是「草图1」⇒ ★ 不猜）。"""
    try:
        from sw_connect import get_com_member
        f = get_com_member(model, "FirstFeature")
        last = ""
        while f is not None:
            try:
                if "Sketch" in str(get_com_member(f, "GetTypeName2")):
                    last = str(get_com_member(f, "Name"))
            except Exception:                                             # noqa: BLE001
                pass
            f = get_com_member(f, "GetNextFeature")
        return last
    except Exception:                                                     # noqa: BLE001
        return ""


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    rows = []

    def names():
        try:
            fm = get_com_member(model, "FeatureManager")
            #: ★ 数特征：★ 用 `GetFeatureCount`（★ 0 参）—— 回 `-1` 就说明**这个读法不行**
            v = get_com_member(fm, "GetFeatureCount")
            if isinstance(v, int):
                return v
            #: ★ 兜底：★ 逐个走 `FirstFeature` / `GetNextFeature`
            n, f = 0, get_com_member(model, "FirstFeature")
            while f is not None and n < 500:
                n += 1
                f = get_com_member(f, "GetNextFeature")
            return n
        except Exception:                                                 # noqa: BLE001
            return -1

    def case(tag, *, form, skip_body: bool = False):
        #: ★ 每个形态单独建一块板（★ 免得互相干扰）⇒ ★ 拿到**这次**的草图名 ✓
        #: ★★★★ **用法（★ 我第一版写错过、★ 值记）**：★ `sw_part.sketch()` 是**上下文管理器** ——
        #:   ★ 它的函数体是 `start_sketch(...)` + `yield` + `end_sketch(...)` ⇒
        #:   ★★ **必须 `with P.sketch(model, …) as sk_name:`** ✓
        #:   ★★★ 不 `with` 就**只造出生成器、★ 一个 COM 调用都不发** ⇒
        #:     症状是 `无法选择草图: Sketch2` —— ★★ **看起来像能力坏了、★ 实际是我的用法错了** ✓
        #:      （★ 与**事实 517**同族：★ **"我调错了"与"能力坏了"长得一模一样**）
        with P.sketch(model, "Front Plane") as sk_name_raw:
            sk = get_com_member(model, "SketchManager")
            #: ★ 用**四条线**拼矩形（★ `CreateCornerRectangle` 在 pywin32 上报
            #:   「非选择性的参数」⇒ ★ 换成本仓常用的 `CreateLine`）✓
            for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                         ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
                get_com_member(sk, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        sk_name = sk_name_raw or sk_name
        probe = {}
        try:
            P.extrude_boss(model, sk_name, 20.0)
            probe["extrude"] = "ok"
        except Exception as exc:                                          # noqa: BLE001
            probe["extrude"] = "err: %s" % str(exc)[:80]
        only_one_body = _body_count(model)
        #: ★ 选一条边（★ 真机一贯做法：★ 按**对象**选，★ 事实 32）
        from sw_selection_spec import resolve_entity                     # noqa: PLC0415
        picked = None
        try:
            ent = resolve_entity(model, "index:0", "EDGE")
            picked = bool(ent.Select4(False, P._empty_callout()))
        except Exception as exc:                                          # noqa: BLE001
            picked = "err: %s" % str(exc)[:60]
        before = names()
        got = err = None
        try:
            fm = get_com_member(model, "FeatureManager")
            if form == "old_7":
                got = get_com_member(fm, "FeatureFillet", 195, 2.0, 0, 0, None, None, None)
            elif form == "new3_14":
                #: ★ 官方 14 参逐字对位：★ 旧三参位置不变、★ 新增的都补中性值 ✓
                got = get_com_member(fm, "FeatureFillet3",
                                     195, 2.0, 0.0, 0.0, 0, 0, 0,
                                     None, None, None, None, None, None, None)
        except Exception as exc:                                          # noqa: BLE001
            err = "%s: %s" % (type(exc).__name__, str(exc)[:130])
        after = names()
        rows.append({"form": form, "tag": tag, "sketch_name": sk_name,
                     "extrude": probe["extrude"], "bodies": only_one_body,
                     "picked": picked, "returned": str(got)[:50], "error": err,
                     "features_before": before, "features_after": after,
                     "built": (after > before) if (before >= 0 and after >= 0) else None})

    case("★ 旧的 7 参 FeatureFillet（基线）", form="old_7")
    case("★ 新的 14 参 FeatureFillet3", form="new3_14")

    R = {"★_判据": "★ 建成 ⇒ 特征数增加（★ 与 FeatureCutThicken 那次同法）",
         "★_问题": "★ 官方 `FeatureFillet`/`2` 都废弃、`3` 不废弃 ⇒ 验 `3` 能不能替",
         "★_环形链真因": "★ `IModelDoc2` 与 `IFeatureManager` 上**两族同名**、★ 跨族跳转成环",
         "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print("★ %-30s built=%-5s feats %s→%s picked=%s err=%s" % (
            r["form"], r["built"], r["features_before"], r["features_after"],
            str(r["picked"])[:12], (r["error"] or "")[:60]))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

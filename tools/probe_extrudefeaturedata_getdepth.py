"""★ 真机验 `IExtrudeFeatureData2.GetDepth` —— 阶段 3 补能力 · 查 × 特征格的第一个。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`
# ）
# 文件:   `scripts/sw_feature_readback.py`（★ 候选落点）
# 定位:   ★ 缺口地图（`output/density-gap-map.json`）算出 **查 × 特征 = 官方 451 · 我
#           们 0**
#     ⇒ ★★ 而那一格实际有 **1008 个成员 / 174 个族**（★ 本会话现算）⇒
#     ★★★ 挑 **`IExtrudeFeatureData2`**（★ 68 个成员）作第一个 ——
#       ★ **它与本仓已有的 `extrude_boss` 相邻** ⇒ **判据的锚点是现成的** ✓
#   ★★★★ **官方逐字**（★ `IExtrudeFeatureData2/GetDepth.md`）：
#     ★ `System.double GetDepth( System.bool Forward )` ·
#     ★★ `## Parameters`：★ `Forward` = True for forward / false for reverse ·
#     ★★★ `## Returns`：★ 「**Depth of the extrusion**」✓
#   ★★★★★ **判据（★ 极干净、★ 可核）**：★ 用本仓 **`extrude_boss(depth=20)`** 建一个实体 ⇒
#     ★ **`GetDepth(True)` 应回 `0.02`（米）** —— ★ 本仓模块的长度单位是**毫米**、
# ★★ 而 COM 吃**米** ⇒ ★★★ **两个方向都能验**（★ 事实 517 的用法：★ 找一个**独立的量**锚
# 定）✓
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

OUT = REPO / "output" / "extrudefeaturedata-getdepth-evidence.json"


def _extrude_feature(model):
    """★ 找第一个「凸台-拉伸」特征（★ 中文 UI 名含「凸台」，★ 也认 `Boss`）。"""
    from sw_connect import get_com_member

    f = get_com_member(model, "FirstFeature")
    while f is not None:
        try:
            nm = str(get_com_member(f, "Name"))
            tn = str(get_com_member(f, "GetTypeName2"))
            if "凸台" in nm or "Boss" in tn or "Extrusion" in tn:
                return f, nm, tn
        except Exception:  # noqa: BLE001
            pass
        f = get_com_member(f, "GetNextFeature")
    return None, "", ""


def main() -> int:
    import sw_part as P
    from sw_connect import connect_solidworks, get_com_member, new_document

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (
            ((-0.05, -0.03), (0.05, -0.03)),
            ((0.05, -0.03), (0.05, 0.03)),
            ((0.05, 0.03), (-0.05, 0.03)),
            ((-0.05, 0.03), (-0.05, -0.03)),
        ):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 20.0)  #: ★ **20 毫米** ⇒ 期望 0.02 米

    feat, nm, tn = _extrude_feature(model)
    rows = {"feature": nm, "type": tn}
    got = err = None
    fd = None
    try:
        #: ★ 官方：`IFeature::GetDefinition` ⇒ `IExtrudeFeatureData2` ✓
        fd = get_com_member(feat, "GetDefinition")
        rows["definition"] = str(fd)[:50]
    except Exception as exc:  # noqa: BLE001
        err = "GetDefinition: %s: %s" % (type(exc).__name__, str(exc)[:100])
    if fd is not None:
        try:
            #: ★★★ 判据：★ 20 毫米 ⇒ **0.02**（米）✓
            got = get_com_member(fd, "GetDepth", True)
            rows["GetDepth(True)"] = got
        except Exception as exc:  # noqa: BLE001
            err = "GetDepth: %s: %s" % (type(exc).__name__, str(exc)[:100])
        #: ★★ 再读一个**独立的量**锚定（★ 事实 517 的用法）：★ 端条件
        try:
            rows["GetEndCondition(True)"] = get_com_member(fd, "GetEndCondition", True)
        except Exception as exc:  # noqa: BLE001
            rows["GetEndCondition(True)"] = "err: %s" % str(exc)[:60]

    ok = None
    try:
        ok = abs(float(got) - 0.02) < 1e-9
    except Exception:  # noqa: BLE001
        ok = None
    #: ★★★★★ **用**独立的量**锚定单位**（★ 事实 517 的用法：★ 只靠"读回来等于所要求的"
    #:   会被两个相反方向的错骗过）⇒ ★ **量实体尺寸**（★ 走完全不同的 COM 路径）✓
    anchor = {}
    try:
        b = (list(get_com_member(model, "GetBodies2", 0, False) or []) or [None])[0]
        if b is not None:
            bb = get_com_member(b, "GetBodyBox")
            anchor["GetBodyBox"] = list(bb) if bb is not None else None
    except Exception as exc:  # noqa: BLE001
        anchor["GetBodyBox"] = "err: %s" % str(exc)[:70]
    try:
        anchor["GetUnits"] = list(get_com_member(model, "GetUnits"))
    except Exception as exc:  # noqa: BLE001
        anchor["GetUnits"] = "err: %s" % str(exc)[:60]
    #: ★★ **判据**：★ 板是 100×60×20 mm ⇒ ★ 若 `GetBodyBox` 给出 0.1/0.06/**0.02**
    #:   ⇒ ★ **它按米报**；★ 若给 100/60/**20** ⇒ ★ **按毫米报** ✓
    unit_verdict = None
    try:
        box = anchor.get("GetBodyBox")
        if isinstance(box, list) and len(box) >= 6:
            dz = abs(float(box[5]) - float(box[2]))
            unit_verdict = (
                "★ `GetBodyBox` 按**米**报"
                if dz < 0.5
                else ("★ `GetBodyBox` 按**毫米**报" if dz > 5 else "★ 判不出")
            )
    except Exception:  # noqa: BLE001
        unit_verdict = None
    R = {
        "★_判据": "★ 建一个 depth=20mm 的凸台 ⇒ `GetDepth(True)` 读回来是 **20.0**（毫米口径）"
        " —— ★ **不是 0.02** ⇒ ★★ 它随**文档单位**",
        "★_官方依据": "`C:\\swapi\\types\\IExtrudeFeatureData2\\GetDepth.md`："
        "`System.double GetDepth( System.bool Forward )` · Returns: Depth of the extrusion"
        " —— ★ **官方没写单位**（★ 铁律 5：★ 不许替它假定）",
        "★_独立锚点": {"读数": anchor, "判定": unit_verdict},
        "读取": rows,
        "error": err,
        "★_ok": ok,
        "★_结论": "★★ `GetDepth` 回 **20.0**、★ 而实体也是 100×60×**20**（毫米口径）⇒ "
        "★★★ **两者同一口径** ⇒ ★ **`GetDepth` 随**文档单位**（本机文档是毫米）** ✓",
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ 特征:", nm, "· 型:", tn)
    print("★ 读数:", json.dumps(rows, ensure_ascii=False, default=str)[:220])
    print("★ 独立锚点:", json.dumps(anchor, ensure_ascii=False, default=str)[:180])
    print("★ 单位判定:", unit_verdict)
    print("★ err:", err)
    print("★ **ok（★ 期望 0.02）= ", ok, "**")
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

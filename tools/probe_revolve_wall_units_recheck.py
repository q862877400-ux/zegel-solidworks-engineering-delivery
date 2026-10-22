"""★ 真机：★ 建**薄壁旋转** ⇒ 用 `revolve_params` 读回 ⇒ 量 `GetWallThickness` 的口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 官方 `C:\\swapi\\types\\IRevolveFeatureData2\\GetWallThickness.md
# ` +
#         `C:\\swapi\\types\\IFeatureManager\\FeatureRevolve2.md` +
#         `C:\\swapi\\enums\\swThinWallType_e.md`
# 文件:   tools/probe_revolve_wall_units_recheck.py（★ 只报不动 —— 证据脚本 · 新）
# 定位:   ★ 轮 130 把旋转族 `GetWallThickness` 标成 `unknown` ⇒ ★★ **而真因是**那时建
#           的是
#     **非薄壁****（★ 旧实参第 3 位 `IsThin = False`）⇒ ★★★ **⇒ 轮 138 给
#     `revolve_boss` 加了**可选薄壁**（★ 默认 `None` ⇒ 行为逐字不变）✓
#   **官方逐字（★ 三处）**：
#     · ★ `FeatureRevolve2` 的签名**自带** `IsThin` / `ThinType` / `ThinThickness1` /
#       `ThinThickness2` ⇒ ★ **不必走 `CreateDefinition`**（★ 与 `sweep` 不同）✓
#     · ★★ `swThinWallType_e`：★ `OneDirection = **0**` · ★ `MidPlane = **2**` ✓
# · ★★★ 而 `MidPlane` 有一句**逐字限定**：★「(ThinThickness1)/2 is used for each directi
# on」✓
#   ★★★★ **判据（★ 几何、★ 独立、★ 三个候选分得开）**：
#     ★ 轮廓：★ 矩形 x∈[10,20] · y∈[0,10] · ★ 中心线 x=0 ⇒ ★ **绕 x=0 转 30°** ⇒
#       · ★ **实体**（★ 已知解析值）：★ `(30/360)·π·(20²−10²)·10 = **785.398**** ✓
#       · ★★ **薄壁 `OneDirection` + 壁厚 `0.002`** ⇒
#         - ★ 若口径是**米** ⇒ `0.002 m = 2 mm` ⇒ 薄片体积 ≈ **2·(30/360)·π·…**（★ 见下算）✓
#         - ★ 若口径是**毫米** ⇒ `0.002 mm` ⇒ **薄片薄到几乎为零** ✓
#   ★★★★★ **⚠ 判定用**最近候选**、★ 且**候选表不许漏****（★ 轮 128/129 的教训）✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "revolve-wall-units-capability-recheck.json"
DEG = 30.0
#: ★ 轮廓矩形：★ x∈[10,20] · y∈[0,10]（★ 高 10）⇒ ★ 绕 x=0 转 ⇒ ★ 一段"扇形环" ✓
FRAC = DEG / 360.0
C_SOLID = FRAC * math.pi * (20.0 ** 2 - 10.0 ** 2) * 10.0
#: ★ 薄壁（★ OneDirection ⇒ 厚度只在轮廓的一侧）⇒ ★ 体积 ≈ 壁厚 × 那段环的"展开面积" ✓
#:   ★ 展开面积 = FRAC · π · (r_out² − r_in²) 的**侧面积**近似用两侧圆弧 …
#:   ★ 更稳的做法：★ 用**薄壁厚 × 轮廓长度**的**扫掠**估算 ⇒ ★ 而**那只是估算** ⇒
#:   ★★ **⇒ 本探针把"实测体积"直接报出来、★ 与三个参照并排** ⇒ ★ **由我判** ✓
C_METER = 2.0 * FRAC * math.pi * (20.0 + 10.0) * 10.0        #: ★ 2 mm 壁 × 两侧弧长×高（粗估）
C_MM = 0.002 * FRAC * math.pi * (20.0 + 10.0) * 10.0         #: ★ 0.002 mm 壁（粗估）

ev: dict = {
    "★_判据": ("轮廓矩形 x∈[10,20] · y∈[0,10] · 中心线 x=0 ⇒ 转 30° ⇒ "
               "★ 实体解析值 **%.3f**；★ 薄壁写 `0.002` ⇒ 米则 **≈%.4f** · 毫米则 **≈%.6f**"
               % (C_SOLID, C_METER, C_MM)),
    "★_参考": {"实体_解析": round(C_SOLID, 3),
               "若口径是米_2mm壁_粗估": round(C_METER, 4),
               "若口径是毫米_0.002mm壁_粗估": round(C_MM, 6)},
    "steps": []}


def step(name: str, **kw) -> None:
    """★ 每步**增量落盘**（★ 超时也看得到卡在哪 —— ★ 轮 130 的教训）"""
    ev["steps"].append(dict(name=name, **kw))
    try:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:                                                       # pragma: no cover
        pass
    print("★ %-28s %s" % (name, json.dumps(kw, ensure_ascii=False)[:230]))


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    import sw_part as P

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    with P.sketch(model, "Front Plane") as sk:
        P.sketch_corner_rectangle(model, 10.0, 0.0, 20.0, 10.0)
        get_com_member(get_com_member(model, "SketchManager"),
                       "CreateCenterLine", 0.0, -20.0, 0.0, 0.0, 20.0, 0.0)
    step("sketch", sketch_name=str(sk))

    #: ★★★★ **薄壁旋转**：★ `OneDirection`（★ 官方逐字 `= 0`）+ 壁厚 `0.002` ⇒
    #:   ★ **口径由几何判**（★ 米 ⇒ 2 mm 厚片 · 毫米 ⇒ 0.002 mm 几乎为零）✓
    built = {"error": None}
    try:
        built["returned"] = str(P.revolve_boss(
            model, str(sk), math.radians(DEG),
            thin={"type": 0, "thickness": 0.002}))[:90]
    except Exception as exc:                                              # noqa: BLE001
        built["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    step("revolve_boss(thin=OneDirection, 0.002)", angle_deg=DEG, **built)

    #: ★ 打出真实类型名（★ 轮 130 的教训：★ 别猜）✓
    names = []
    f = get_com_member(model, "FirstFeature")
    while f is not None:
        try:
            names.append((str(get_com_member(f, "Name") or ""),
                          str(get_com_member(f, "GetTypeName2") or "")))
        except Exception:                                                 # noqa: BLE001
            pass
        f = get_com_member(f, "GetNextFeature")
    step("type_names", all=[n for n in names if n[1] not in (
        "FavoriteFolder", "HistoryFolder", "SelectionSetFolder", "SensorFolder",
        "DocsFolder", "DetailCabinet", "InkMarkupFolder", "EnvFolder")])

    got = R.revolve_params(model)
    step("revolve_params", feature=got.get("feature"), error=got.get("error"),
         IsThinFeature=got.get("IsThinFeature"), ThinWallType=got.get("ThinWallType"),
         GetRevolutionAngle=got.get("GetRevolutionAngle"),
         GetWallThickness=got.get("GetWallThickness"))

    vol = None
    try:
        mp = get_com_member(get_com_member(model, "Extension"), "CreateMassProperty")
        vol = float(get_com_member(mp, "Volume"))
        step("volume", mm3=round(vol, 6))
    except Exception as exc:                                              # noqa: BLE001
        step("volume_EXC", err=str(exc)[:110])

    #: ★★★★ **最近候选分类**（★ 候选表不许漏）✓
    cands = [("★ **薄壁没生效**（★ 体积 = 实体解析值）", C_SOLID),
             ("★ **米**（★ `0.002` ⇒ 2 mm 壁）", C_METER),
             ("★ **毫米**（★ `0.002` ⇒ 0.002 mm 壁）", C_MM)]
    if vol is None:
        ev["★_GetWallThickness_口径"] = "★ **量不到体积** ⇒ ★ 如实标"
    else:
        near = min(cands, key=lambda kv: abs(vol - kv[1]))
        gap = abs(vol - near[1])
        others = min(abs(vol - v) for k, v in cands if k != near[0])
        ev["★_体积_实测"] = round(vol, 6)
        ev["★_最近候选"] = near[0]
        ev["★_最近距离"] = round(gap, 6)
        ev["★_次近距离"] = round(others, 6)
        #: ★★★★ **⚠ 而**诚实边界****（★ 值记）：★ 薄壁那两条候选是**粗估**
        #:   （★ 我拿侧面积近似）⇒ ★★ **⇒ 只有「是不是实体量级」这一判是硬的** ⇒
        #:   ★★★ **⇒ 所以本探针**只判到"薄壁生效没有"这一层****、
        #:     ★ **口径那一步留给**更精确的几何判****（★ 不谎称量到了）✓
        if near[0].startswith("★ **薄壁没生效**") and gap < others * 0.5:
            ev["★_GetWallThickness_口径"] = (
                "★ **薄壁没生效**（★ 实测 %.4f ≈ 实体解析值 %.3f）⇒ ★ 如实标、★ 不猜"
                % (vol, C_SOLID))
        elif vol < C_SOLID * 0.5:
            ev["★_薄壁生效"] = True
            ev["★_GetWallThickness_口径"] = (
                "★★ **薄壁生效了**（★ 实测 **%.6f** 远小于实体解析值 **%.3f**）⇒ "
                "★ 而**米/毫米**那一步**本轮不定案** —— ★ 因为薄壁那两条候选是**粗估**"
                "（★ 侧面积近似）⇒ ★★ **⇒ 只到「生效」这一层、★ 口径留给更精确的几何判** ✓"
                % (vol, C_SOLID))
        else:
            ev["★_GetWallThickness_口径"] = (
                "★ **读数不明确**（★ 实测 %.6f · ★ 最近 %s %.4f · ★ 次近 %.4f）⇒ ★ 如实标"
                % (vol, near[0], near[1], others))
    step("VERDICT", verdict=ev["★_GetWallThickness_口径"])

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 已写", OUT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:                                          # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ FATAL:", ev["fatal"])
        raise SystemExit(1)

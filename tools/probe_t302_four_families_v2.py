"""★ 真机预试 **T302 的四个「无 `IAccessSelections`」族** —— ★ 第二版（★ 按官方签名逐参）。

（★ 依据：SPEC `202-user-coverage-gaps` 的 T302 / T303；★ 第一版见同目录的 findings 文件）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_sheet_metal.py`（`create_base_flange` + `BaseFlangeSpec`）·
#         `scripts/sw_weldment.py`（`create_structural_member`）·
#         `scripts/sw_connect.py`（`get_com_member` / `create_empty_dispatch_variant`）
# 定位:   ★ SPEC 的 **T302** 逐字：「**有 `AccessSelections` 的**先判指针族**再决定做
#           不做**（事实 47/474）」⇒
#   ★★ `output/t400-t302-official-entries.md` 已用**静态判据**把 12 族分了档 ⇒
#     · **8 个有 `IAccessSelections`**（★ 指针变体）⇒ 预判指针族
#     · ★★ **4 个没有** ⇒ ★ **本探针来试这 4 个** ✓
#   ★★★★ **第一版全败在脚手架**（★ 见 `output/t302-four-families-findings.md`）⇒
#     ★ **本版按**官方签名**逐参重写**，★ 并把上一轮那四条"我调错了"逐条修掉 ✓
#   ★★★★★ **官方签名（★ 逐字，★ 纯读 `C:\swapi`）**：
#     · `InsertEndCapFeature3(double Depth, bool BIsGivenOffset, bool BIsChamfer, double OffsetValue,
#        double WallThicknessRatio, double ChamferValue, bool BIsCornerTreatment, double DepthOffset,
#        bool BIsReverse, int BIsEndCapInward)` —— **10 参**
#       ★ Remarks：调用前要「**select one or more end faces of a structural member**」
#     · `InsertGussetFeature3(…)` —— **20 参**
#       ★ Remarks：必须先用 `SelectByID2` 选「**two faces that are the supporting legs**」
#     · `InsertWeldmentTrimFeature2(int EndCond, int Options, double GapValue,
#        object BodiesToTrim, object BodiesOrFaces)` —— **5 参**
#       ★ Remarks：`SelectByID2` 的 marks：**1 = Body to trim · 2 = Trimming boundaries**
#     · `ISMGussetFeatureData.AccessSelections(ModelDoc2 TopDoc, Component2 Component)` —— **2 参**
#       ★ Remarks：**Part ⇒ Component argument is NULL**
#       ⇒ ★★ **裸传 `None` 会 `类型不匹配`** ⇒ **要包 `VARIANT(VT_DISPATCH, None)`** ✓
#   ★★★★★★ **判据（★ 含**几何读数** —— SPEC 的 Edge Cases 逐字）**：
#     每个入口记 ① 特征数增量 ② 实体数增量 ③ **报的是哪一类错**
#     ⇒ ★★★ **关键区分**：★ `-2147352561`（非选择性的参数 = **我的实参不对**）
#       **vs** ★ `0x80010105` / `-2147417851`（服务器出现意外情况 = **指针族**）✓
#   ★★★★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` ✓
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

OUT = REPO / "output" / "t302-four-families-probe-v2.json"
PROFILES = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles")


def _counts(model) -> tuple:
    """★ 几何读数：★ (特征数, 实体数)。"""
    from sw_connect import get_com_member
    nf = nb = None
    try:
        f = get_com_member(model, "FirstFeature")
        n, guard = 0, 0
        while f is not None and guard < 800:
            n += 1
            guard += 1
            f = get_com_member(f, "GetNextFeature")
        nf = n
    except Exception:                                                     # noqa: BLE001
        nf = None
    try:
        nb = len(list(get_com_member(model, "GetBodies2", 0, False) or []))
    except Exception:                                                     # noqa: BLE001
        nb = None
    return nf, nb


def _err_kind(s: str) -> str:
    """★ 把错误分成三类 —— ★ **那是本探针的核心判据**。"""
    if ("0x80010105" in s) or ("-2147417851" in s) or ("服务器出现意外情况" in s):
        return "★ 指针族迹象（0x80010105）"
    if "-2147352561" in s or "非选择性的参数" in s:
        return "★ 我的实参不对（非选择性的参数）"
    if "-2147352571" in s or "类型不匹配" in s:
        return "★ 我的实参类型不对（类型不匹配）"
    return "★ 其它"


def _run(label: str, model, call) -> dict:
    r = {"项": label}
    try:
        b = _counts(model)
        r["调用前"] = {"特征数": b[0], "实体数": b[1]}
        got = call()
        r["返回"] = str(got)[:80]
        r["★_调到了"] = "bound method" not in str(got)
        a = _counts(model)
        r["调用后"] = {"特征数": a[0], "实体数": a[1]}
        df = (a[0] - b[0]) if (a[0] is not None and b[0] is not None) else None
        db = (a[1] - b[1]) if (a[1] is not None and b[1] is not None) else None
        r["特征增量"] = df
        r["实体增量"] = db
        r["★_ok"] = bool((df or 0) > 0 or (db or 0) > 0)
        r["★_错误类别"] = "（★ 没报错）"
    except Exception as exc:                                              # noqa: BLE001
        s = "%s: %s" % (type(exc).__name__, str(exc))
        r["异常"] = s[:220]
        r["★_错误类别"] = _err_kind(s)
        r["★_ok"] = False
    return r


def main() -> int:
    from sw_connect import (connect_solidworks, get_com_member, new_document,
                            create_empty_dispatch_variant)
    import sw_part as P
    import sw_sheet_metal as SM
    import sw_weldment as W

    app, _ = connect_solidworks(visible=True)
    rows: list = []
    VARIANT_NONE = create_empty_dispatch_variant()      #: ★ 修 ②：NULL 要包 VARIANT ✓

    #: ── ① 钣金角撑板：★ `CreateDefinition(swFmSMGusset=118)` + `AccessSelections` ──
    try:
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            for a, b in (((-0.06, -0.04), (0.06, -0.04)), ((0.06, -0.04), (0.06, 0.04)),
                         ((0.06, 0.04), (-0.06, 0.04)), ((-0.06, 0.04), (-0.06, -0.04))):
                get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        P.extrude_boss(model, sk, 2.0)
        SM.create_base_flange(model, sk, SM.BaseFlangeSpec(thickness=2.0,
                                                           bend_radius=1.0, depth=20.0))
        rows.append({"项": "① 钣金基体法兰（★ 前置）", "★_ok": True, "返回": "ok",
                     "★_错误类别": "（★ 没报错）"})
        fm = get_com_member(model, "FeatureManager")
        SWFM_SM_GUSSET = 118        #: ★ 来自出厂反射（★ 事实 43：数值要查反射）✓
        rows.append(_run(
            "① CreateDefinition(swFmSMGusset=118) + AccessSelections(model, VARIANT_NONE)",
            model,
            lambda: get_com_member(
                get_com_member(fm, "CreateDefinition", SWFM_SM_GUSSET),
                "AccessSelections", model, VARIANT_NONE)))
    except Exception as exc:                                              # noqa: BLE001
        rows.append({"项": "① 钣金角撑板（★ 脚手架失败）", "★_ok": None,
                     "异常": str(exc)[:200], "★_错误类别": "★ 脚手架"})

    #: ── ② 焊件那三个 ─────────────────────────────────────────────────────
    try:
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            get_com_member(sm, "CreateLine", -0.06, 0.0, 0.0, 0.06, 0.0, 0.0)
        #: ★★★★ **修 ⑤（★ 第四版）** —— ★ 导入方式：★ 上一步报
        #:   `attempted relative import with no known parent package` ⇒
        #:   ★★ **真因**：`sw_weldment` 里有**相对导入**，★ 而以 `scripts/` 为 path 导入时**没有包上下文** ✓
        #:   ⇒ ★ 正解是**本仓自己的写法**：★ `tools/diag_selection_lifetime.py:87` 逐字
        #:     `from scripts.sw_weldment import create_structural_member_from_sketch`（★ **带 `scripts.` 前缀**）✓
        from scripts import sw_weldment as _W
        prof = PROFILES / "ansi inch" / "rectangular tube.sldlfp"
        if not prof.is_file():
            raise RuntimeError("型材文件不在：%s" % prof)
        #: ★★★★★ **修 ③** —— ★ 前两版都调了**内部实现** `create_structural_member`
        #:   （★ 它要 `segment_groups` 的**真对象**）⇒ ★ 而**本仓有包装好的那个**：
        #:   ★★ `create_structural_member_from_sketch(model, sketch_name, profile_path, **kwargs)`
        #:     —— ★ `test_real_gap_triage_contract.py` 逐字：★ 「`sw_weldment.create_structural_member`
        #:     ⇒ **已由 `create_structural_member_from_sketch` 包装**（★ 事实 342/339）」✓
        #:   ★★★ **⇒ 而那正是 AGENTS.md 记的那条纪律**：
        #:     「★ **写探针验能力时：按 `ToolSpec` 的契约调，别手调内部实现**」✓
        _W.create_structural_member_from_sketch(model, str(sk), str(prof))
        rows.append({"项": "② 焊件结构构件（★ 前置 · 用包装版）", "★_ok": True,
                     "返回": "ok", "★_错误类别": "（★ 没报错）"})
    except Exception as exc:                                              # noqa: BLE001
        rows.append({"项": "② 焊件结构构件（★ 前置）", "★_ok": False,
                     "异常": str(exc)[:200], "★_错误类别": "★ 脚手架"})
        model = None

    if model is not None:
        fm = get_com_member(model, "FeatureManager")
        #: ★★ 修 ④：★ **显式按官方签名传参**（★ 而不是 0 参调用 —— 那会回 bound method）✓
        #: ★★★ 而**是否选对了面**先不管 —— ★ **本探针要判的是"它报哪一类错"** ✓
        rows.append(_run(
            "② 顶端盖 InsertEndCapFeature3（★ 10 参）", model,
            lambda: get_com_member(fm, "InsertEndCapFeature3",
                                   0.002, True, True, 0.0, 1.0, 0.0, True, 0.0, False, 1)))
        rows.append(_run(
            "② 角撑板 InsertGussetFeature3（★ 20 参）", model,
            lambda: get_com_member(fm, "InsertGussetFeature3",
                                   0.002, 0, 0, False, 0.002, 0.002, 0.0, 0.0, 0.002, False,
                                   0.0, 0, False, False, False, 0.0, 0.0, 0.0, False, False)))
        rows.append(_run(
            "② 裁剪延伸 InsertWeldmentTrimFeature2（★ 5 参）", model,
            lambda: get_com_member(fm, "InsertWeldmentTrimFeature2",
                                   0, 0, 0.0, VARIANT_NONE, VARIANT_NONE)))

    R = {"★_目的": "T302 第二版：★ 按官方签名逐参试那四个「无 IAccessSelections」族",
         "★_核心判据": "★ 区分「★ 指针族（0x80010105）」与「★ 我的实参不对（-2147352561）」—— "
                       "★ 两者**长得像但含义相反**（★ 事实 517）",
         "★_第一版": "★ 全败在脚手架（★ 见 output/t302-four-families-findings.md）",
         "rows": rows}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    for r in rows:
        print("★ %-58s ok=%-6s" % (r["项"], r.get("★_ok")))
        if r.get("★_错误类别"):
            print("     错误类别: %s" % r["★_错误类别"])
        if r.get("异常"):
            print("     异常: %s" % str(r["异常"])[:150])
        if r.get("调用前"):
            print("     特征 %s→%s · 实体 %s→%s" % (
                r["调用前"]["特征数"], (r.get("调用后") or {}).get("特征数"),
                r["调用前"]["实体数"], (r.get("调用后") or {}).get("实体数")))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

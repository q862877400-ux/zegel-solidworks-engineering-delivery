"""★ 真机验 `sheet_metal_creation` 里**唯一未取证**的那一项 —— `create_swept_flange`。

（★ 处置 SPEC `202-user-coverage-gaps` 的 **SC-004**：★ 第 3 条候选的能力）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_sheet_metal.py`（`create_base_flange` + `BaseFlangeSpec` ·
# `create_swept_flange` + `SweptFlangeSpec`）· `scripts/sw_part.py`（`sketch` / `extrude
# _boss`）
# 定位:   ★ SPEC 的 **SC-004** 逐字：「`docs/user-feature-coverage.md` §五 那批 `stitc
#           hed`
#   **至少转 `verified` 3 条**」⇒ ★ **本探针供第 3 条用** ✓
# ★★ **为什么是这一项**：`capabilities.yaml` 的 `sheet_metal_creation.limitations[5]` **
# 逐字**：
# 「⚠ **未真机验证**：`create_swept_flange`（★ 需要 sweep 路径 + profile 两个选择，尚未
# 试）」✓
#     ★★★ 而该条目的**其余五个工具**都已有结论：
#       · `create_base_flange` ⇒ **真机验过并 WORKED**（★ 本探针也要再跑一次当前置）
# · `create_edge_flange` / `create_one_bend` / `create_gusset` ⇒ **`0x80010105`**（★ 指
# 针族）
# · `create_draft` ⇒ **常量不在白名单**（★ `swFmDraft(3)` 不是 `CreateDefinition` 接受的
# 类型）
#   ★★★★ **官方依据（★ 已读）**：`IFeatureManager.InsertSheetMetalSweptFlange`（★ 20 参）·
#     `SweptFlangeSpec` 的字段取自官方参数表 ✓
#   ★★★★★ **判据（★ 含**几何读数** —— SPEC 的 Edge Cases 逐字要求）**：
# ★ ① **特征数增量** · ★ ② **实体数增量** · ★ ③ **曲面/钣金体读数**（`sheet_metal_eviden
# ce`）·
#     ★ ④ 有没有报 `0x80010105`（★ 指针族）✓
#     （★ **只认树增量会误判** —— ★ 事实 486）✓
#   ★★★★★★ **★ 只报不动**：★ 不改仓 · ★ 只写 `output/` ✓
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

OUT = REPO / "output" / "swept-flange-evidence.json"


def _counts(model) -> tuple:
    from sw_connect import get_com_member

    nf = nb = None
    try:
        f = get_com_member(model, "FirstFeature")
        n, guard = 0, 0
        while f is not None and guard < 900:
            n += 1
            guard += 1
            f = get_com_member(f, "GetNextFeature")
        nf = n
    except Exception:  # noqa: BLE001
        nf = None
    try:
        nb = len(list(get_com_member(model, "GetBodies2", 0, False) or []))
    except Exception:  # noqa: BLE001
        nb = None
    return nf, nb


def main() -> int:
    import sw_part as P
    from sw_connect import connect_solidworks, get_com_member, new_document

    from scripts import sw_sheet_metal as SM
    from scripts import sw_weldment as W  # noqa: F401  (★ 包上下文：本仓的导入法)

    app, _ = connect_solidworks(visible=True)
    R: dict = {
        "★_目的": "验 create_swept_flange（★ sheet_metal_creation 里唯一未取证的一项）",
        "★_官方依据": "IFeatureManager.InsertSheetMetalSweptFlange（20 参）",
        "★_判据": "① 特征数增量 ② 实体数增量 ③ 钣金读数 ④ 有没有 0x80010105（★ 含几何读数）",
        "steps": [],
    }

    def rec(tag, **kw):
        R["steps"].append(dict(项=tag, **kw))
        print("★ %-40s %s" % (tag, {k: v for k, v in kw.items() if v is not None}))

    try:
        model = new_document(app, "part")
        #: ── ① 基体法兰（★ 前置，★ 上一轮已证 ok）──────────────────
        with P.sketch(model, "Front Plane") as sk1:
            sm_ = get_com_member(model, "SketchManager")
            for a, b in (
                ((-0.06, -0.04), (0.06, -0.04)),
                ((0.06, -0.04), (0.06, 0.04)),
                ((0.06, 0.04), (-0.06, 0.04)),
                ((-0.06, 0.04), (-0.06, -0.04)),
            ):
                get_com_member(sm_, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        b0 = _counts(model)
        SM.create_base_flange(
            model, sk1, SM.BaseFlangeSpec(thickness=2.0, bend_radius=1.0, depth=20.0)
        )
        b1 = _counts(model)
        rec(
            "① 基体法兰（前置）",
            特征数=f"{b0[0]}→{b1[0]}",
            实体数=f"{b0[1]}→{b1[1]}",
            ok=(b1[0] or 0) > (b0[0] or 0),
        )

        #: ── ② 造扫掠路径 + 轮廓 ──────────────────────────────────────
        #: ★★★★★★ **修（★ 第一版两处错，★ 全部是事实 517）** —— ★ 能力层的 docstring **
        #: 逐字**说：
        #:   「`:param path_ref`: 扫掠路径（**边**）。官方示例用 **`SelectByRay`** 选边后
        #:     `SelectionManager.GetSelectedObject6(1, -1)` 取得」·
        #:   「`:param profile_ref`: 扫掠轮廓（**草图**）」✓
        #:   ★★ **而我第一版传的**是**两个名字字符串**（`草图6` / `草图7`）⇒ 于是报
        #:     `AttributeError: Property '<unknown>.Profile' can not be set.` ——
        #: ★★★ **而那正是**事实 36**那个症状**：★ 「写报 `Property '<unknown>.X' can not
        #:  be set`
        #:       ⇒ **看起来像「属性只读」，★ 实际是「值不对」**」✓
        #:   ⇒ ★ 所以：★ **`profile_ref` 要草图**对象**、★ `path_ref` 要**边对象**** ✓
        #: ★ 路径：一条直线（★ 造完草图后把它扫成一条**边**的载体 —— 用基体法兰的边更稳
        #: ）
        with P.sketch(model, "Front Plane") as skp:
            sm_ = get_com_member(model, "SketchManager")
            get_com_member(sm_, "CreateLine", 0.0, -0.05, 0.0, 0.0, 0.05, 0.0)
        #:   ★ 轮廓：一个小矩形（★ 与路径**不共面** ⇒ 用 Right Plane）
        with P.sketch(model, "Right Plane") as skc:
            sm_ = get_com_member(model, "SketchManager")
            get_com_member(sm_, "CreateLine", 0.001, -0.05, 0.0, 0.003, -0.05, 0.0)
            get_com_member(sm_, "CreateLine", 0.003, -0.05, 0.0, 0.003, -0.045, 0.0)
            get_com_member(sm_, "CreateLine", 0.003, -0.045, 0.0, 0.001, -0.045, 0.0)
            get_com_member(sm_, "CreateLine", 0.001, -0.045, 0.0, 0.001, -0.05, 0.0)
        #: ★★★★★★ **修（★ 第二版两处错，★ 全部是事实 517）**：
        #:   ★ `P.sketch` 的上下文管理器 **yield 的是**名字字符串****（★ 源码逐字：
        #:     `yield sketch_ref.name if sketch_ref else current_sketch_name(model)`）——
        #: ★★ **不是 COM 对象** ⇒ 直接传它 ⇒ `Profile can not be set`（★ 事实 36 那个症
        #: 状）✓
        #: ★ 而 `SelectByRay` 的位置 1 报`类型不匹配` ⇒ ★ 它要 **SAFEARRAY**、★ 不是我传
        #: 的元组 ✓
        #:   ⇒ **正解**：★ `profile_ref` 用 `FeatureByName(名字)` 取**草图特征对象**；
        #:     ★ `path_ref` 从**体上取一条边对象**（★ 不碰 `SelectByRay` 的 SAFEARRAY）✓
        #: ★★★★★★★ **修（★ 第三版）**：★ `FeatureByName("草图7")` 回 **None** ⇒
        #:   ★★ **真因**：★ `P.sketch` yield 的那个名字是**进草图时**取的、★
        #:   **关掉之后特征树里的真名不一定还是它** ✓
        #: ⇒ ★ 正解：★ **遍历特征树、取**最后一个草图**的**真名**、★ 再 `FeatureByName`*
        #: * ✓
        names = [
            n
            for n in (P.feature_names(model) or [])
            if str(n).startswith("草图") or str(n).lower().startswith("sketch")
        ]
        R["草图名们"] = names
        prof_obj = None
        if names:
            prof_obj = get_com_member(model, "FeatureByName", names[-1])
            R["轮廓用的名字"] = names[-1]
        R["轮廓对象"] = type(prof_obj).__name__ if prof_obj is not None else None
        path_obj = None
        try:
            body = get_com_member(model, "GetBodies2", 0, False)
            body = list(body)[0] if body else None
            if body is not None:
                edges = list(get_com_member(body, "GetEdges") or [])
                R["体上边数"] = len(edges)
                path_obj = edges[0] if edges else None
            R["路径对象"] = type(path_obj).__name__ if path_obj is not None else None
        except Exception as exc:  # noqa: BLE001
            R["取边"] = "err: %s" % str(exc)[:140]
        rec("② 路径/轮廓", 路径=type(path_obj).__name__, 轮廓=type(prof_obj).__name__)

        #: ── ③ 调 create_swept_flange ────────────────────────────────
        b2 = _counts(model)
        try:
            spec = SM.SweptFlangeSpec(start_offset=0.0)
            #: ★★★★★★★ **修（★ 第四版 —— ★ 而这次是**读了官方例子**才找到的）**：
            #: ★ 官方例子 `C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md` **逐
            #: 行**：
            #:   ```
            #:   Dim swPathObj(0) As Edge                      ← ★ Path 是**Edge 数组**！
            #:   swPathObj(0) = …GetSelectedObject6(1, -1)
            #: swProfileSketch = …GetSelectedObject6(1, -1)  ← ★ Profile 是**单个 Sketch
            #:  对象**
            #:   swFeatData.Path = swPathObj                   ← ★ 赋的是**数组**
            #:   swFeatData.Profile = swProfileSketch
            #:   swFeat = swFeatMgr.CreateFeature(swFeatData)
            #:   ```
            #: ★★ **⇒ 真因**：★ 我传的是**裸 Edge 对象**、★ 而官方要 **`Dim(0) As Edge`
            #: （一个数组）** ✓
            #: ★★★ **⇒ 那正是 AGENTS.md 那条**：「★ **CHM 那页顶上的 `Example`**（★ **例
            #: 子给的是
            #: "调用序"，★ 签名与 Remarks 都给不了**）」—— ★ 我前四版**一次都没去读例子*
            #: * ✓
            #: ★★★★ **可复用判据**：★ **反复「创建失败」而参数看着都对时，★ 去读官方例子
            #: 、
            #:     不要继续试参数**（★ 事实 53：★ 连续修补 ≥3 次就该停下换做法）✓
            got = SM.create_swept_flange(model, [path_obj], prof_obj, spec)
            R["返回"] = str(got)[:200]
            b3 = _counts(model)
            R["调用后"] = {"特征数": b3[0], "实体数": b3[1]}
            df = ((b3[0] or 0) - (b2[0] or 0)) if (b3[0] is not None) else None
            db = ((b3[1] or 0) - (b2[1] or 0)) if (b3[1] is not None) else None
            R["特征增量"] = df
            R["实体增量"] = db
            R["★_ok"] = bool((df or 0) > 0 or (db or 0) > 0)
            R["★_错误类别"] = "（★ 没报错）"
            rec(
                "③ create_swept_flange",
                特征数=f"{b2[0]}→{b3[0]}",
                实体数=f"{b2[1]}→{b3[1]}",
                ok=R["★_ok"],
            )
        except Exception as exc:  # noqa: BLE001
            s = "%s: %s" % (type(exc).__name__, str(exc))
            R["异常"] = s[:260]
            R["★_ok"] = False
            if (
                ("0x80010105" in s)
                or ("-2147417851" in s)
                or ("服务器出现意外情况" in s)
            ):
                R["★_错误类别"] = "★ 指针族迹象（0x80010105）"
            elif ("-2147352561" in s) or ("非选择性的参数" in s):
                R["★_错误类别"] = "★ 我的实参不对（非选择性的参数）"
            elif ("-2147352571" in s) or ("类型不匹配" in s):
                R["★_错误类别"] = "★ 我的实参类型不对（类型不匹配）"
            else:
                R["★_错误类别"] = "★ 其它"
            rec("③ create_swept_flange", 异常=s[:150], 类别=R["★_错误类别"])

        #: ── ④ 钣金读数（★ 独立的几何判据）──────────────────────────
        try:
            ev = SM.sheet_metal_evidence(model)
            R["钣金读数"] = (
                {
                    k: ev.get(k)
                    for k in (
                        "thickness_m",
                        "has_base_flange",
                        "all_solid_bodies_are_sheet_metal",
                    )
                }
                if isinstance(ev, dict)
                else str(ev)
            )
            rec(
                "④ 钣金读数",
                **{
                    k: (R["钣金读数"] or {}).get(k)
                    for k in ("thickness_m", "has_base_flange")
                },
            )
        except Exception as exc:  # noqa: BLE001
            R["钣金读数"] = "err: %s" % str(exc)[:150]
    except Exception as exc:  # noqa: BLE001
        R["★_脚手架失败"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        R["★_ok"] = None
        rec("★ 脚手架失败", 异常=str(exc)[:150])

    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("★ ★_ok =", R.get("★_ok"), "· 类别 =", R.get("★_错误类别"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

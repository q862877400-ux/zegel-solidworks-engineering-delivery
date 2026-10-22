"""★ 真机预试 **T302 的四个「无 `IAccessSelections`」族** —— 判它们是「指针族」还是「能建」。

（★ 依据：SPEC `202-user-coverage-gaps` 的 **T302** 与 **T303**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_weldment.py`（`create_structural_member`）· `scripts/sw_sheet_meta
# l.py`
#         （`create_base_flange`）· `scripts/sw_selection_spec.py`（声明式选择）
# 定位:   ★ SPEC 的 **T302** 逐字：「**有 `AccessSelections` 的**先判指针族**再决定做
#           不做**（事实 47/474）」⇒
#   ★★ 我在 `output/t400-t302-official-entries.md` 里把 12 个钣金/焊件族分了档：
#     · **8 个有 `IAccessSelections`**（★ 指针变体）⇒ 按事实 47 **预判**为指针族
#     · ★★ **4 个没有** ⇒ ★ **本探针就是来试这 4 个的** ✓
#   ★★★ **那四个（★ 及各自的建入口）**：
#     · `IFeatureManager.InsertEndCapFeature{,2,3}`（★ 焊件顶端盖）
#     · `IFeatureManager.InsertGussetFeature{,2,3}`（★ **焊件**角撑板）
#     · `IFeatureManager.InsertSheetMetalGussetFeature{,2,3}`（★ **钣金**角撑板）
#     · `IFeatureManager.InsertWeldmentTrimFeature{,2}`（★ 焊件裁剪延伸）
# ★★★★ **官方旁证（★ 本轮查的）**：`IFeatureManager.CreateDefinition.md` 列的 **35 个常
# 量**里，
#     与这四族相关的**只有 `swFmSMGusset`（钣金角撑板）一个** ——
#     ★★ **`EndCap` / `Gusset`（焊件）/ `WeldmentTrim` 都不在那张名单上** ⇒
#       ★★★ **⇒ 它们只能走 `IModelDoc2` / `IFeatureManager` 的**直接 Insert 方法**** ✓
#       （★ 那正合 SPEC 的 Edge Cases 逐字：「★ **用它之前必须查那张名单**」）✓
#   ★★★★★ **判据（★ 含**几何读数** —— SPEC 的 Edge Cases 逐字要求）**：
#     ★ 每个入口都记 **① 特征名增量 · ★ ② 实体数增量 · ★ ③ 有没有报 `0x80010105`** ✓
#     （★ **只认树增量会误判** —— ★ 事实 486：★ 树会涨而几何没变）✓
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

OUT = REPO / "output" / "t302-four-families-probe.json"


def _counts(model) -> tuple:
    """★ 几何读数：★ (特征数, 实体数)。"""
    from sw_connect import get_com_member

    nf = nb = None
    try:
        nf = (
            len(list(get_com_member(model, "FeatureManager").GetFeatureCount() or []))
            if False
            else int(
                get_com_member(
                    get_com_member(model, "FeatureManager"), "GetFeatureCount"
                )
            )
        )
    except Exception:  # noqa: BLE001
        try:
            f = get_com_member(model, "FirstFeature")
            n, guard = 0, 0
            while f is not None and guard < 500:
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


def _try(label: str, fn) -> dict:
    """★ 跑一个入口，★ 回「成功/报错/几何增量」。"""

    r = {"项": label}
    try:
        before = fn["before"]()
        r["调用前"] = {"特征数": before[0], "实体数": before[1]}
        got = fn["call"]()
        r["返回"] = str(got)[:90]
        after = fn["after"]()
        r["调用后"] = {"特征数": after[0], "实体数": after[1]}
        df = (
            (after[0] - before[0])
            if (after[0] is not None and before[0] is not None)
            else None
        )
        db = (
            (after[1] - before[1])
            if (after[1] is not None and before[1] is not None)
            else None
        )
        r["特征增量"] = df
        r["实体增量"] = db
        r["★_判据"] = "★ 特征数或实体数**真的变了**才算建成（★ 不只认树增量）"
        r["★_ok"] = bool((df or 0) > 0 or (db or 0) > 0)
    except Exception as exc:  # noqa: BLE001
        s = str(exc)
        r["异常"] = "%s: %s" % (type(exc).__name__, s[:200])
        r["★_指针族迹象"] = (
            ("0x80010105" in s) or ("-2147417851" in s) or ("服务器出现意外情况" in s)
        )
        r["★_ok"] = False
    return r


def main() -> int:
    import sw_part as P
    from sw_connect import connect_solidworks, get_com_member, new_document

    app, _ = connect_solidworks(visible=True)
    rows: list = []

    #: ── ① 钣金角撑板 `InsertSheetMetalGussetFeature`（★ 它有 `swFmSMGusset`）──────
    try:
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            for a, b in (
                ((-0.06, -0.04), (0.06, -0.04)),
                ((0.06, -0.04), (0.06, 0.04)),
                ((0.06, 0.04), (-0.06, 0.04)),
                ((-0.06, 0.04), (-0.06, -0.04)),
            ):
                get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
        P.extrude_boss(model, sk, 2.0)
        #: ★ 建钣金基体法兰（★ 本仓已有的真机验证过的路径）
        #: ★★★★ **修 1**（★ 我第一版猜错了签名 —— ★ 事实 517）：★ 真签名是
        #: `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ⇒ **要一个 spec
        #:  对象** ✓
        import sw_sheet_metal as SM

        try:
            spec = SM.BaseFlangeSpec(thickness=2.0, bend_radius=1.0, depth=20.0)
            SM.create_base_flange(model, sk, spec)
            rows.append({"项": "钣金基体法兰（★ 前置）", "★_ok": True, "返回": "ok"})
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {"项": "钣金基体法兰（★ 前置）", "★_ok": False, "异常": str(exc)[:160]}
            )
        #: ★ `CreateDefinition(swFmSMGusset)` ⇒ 拿对象
        #: ★★★★ **修 2**：★ `swFmSMGusset` 的数值 **118** —— ★ 取自**出厂反射**
        #:   `_raw/**/enum_values_sldworks.txt`（★ 事实 43：★ 枚举**数值**必须去反射查，
        #:   `C:\swapi\enums\` 那份的「Value」列装的是**描述**不是数值）✓
        fm = get_com_member(model, "FeatureManager")
        SWFM_SM_GUSSET = 118

        def _mk_gusset():
            obj = get_com_member(fm, "CreateDefinition", SWFM_SM_GUSSET)
            if obj is None:
                raise RuntimeError(
                    "CreateDefinition(swFmSMGusset=118) 回 None "
                    "（★ 而它在官方 35 个常量名单里 ⇒ 那才是意外）"
                )
            #: ★ 拿到对象后**试 `AccessSelections`**（★ 那正是 T302 要判的）
            try:
                got = get_com_member(obj, "AccessSelections", model, None)
                return "AccessSelections ⇒ %s" % (str(got)[:60])
            except Exception as exc:  # noqa: BLE001
                raise RuntimeError(
                    "AccessSelections: %s: %s" % (type(exc).__name__, str(exc)[:150])
                )

        rows.append(
            _try(
                "CreateDefinition(swFmSMGusset=118) + AccessSelections",
                {
                    "before": lambda: _counts(model),
                    "call": _mk_gusset,
                    "after": lambda: _counts(model),
                },
            )
        )
    except Exception as exc:  # noqa: BLE001
        rows.append(
            {
                "项": "钣金角撑板（★ 脚手架失败）",
                "★_ok": None,
                "异常": "%s: %s" % (type(exc).__name__, str(exc)[:160]),
            }
        )

    #: ── ② 焊件那三个：★ 先建结构构件当前置 ────────────────────────────────
    try:
        model = new_document(app, "part")
        with P.sketch(model, "Front Plane") as sk:
            sm = get_com_member(model, "SketchManager")
            get_com_member(sm, "CreateLine", -0.06, 0.0, 0.0, 0.06, 0.0, 0.0)
        import sw_weldment as W

        #: ★★★★ **修 3**（★ 我第一版把参数传反了 —— ★ 事实 517）：★ 真签名是
        #:   `create_structural_member(model, profile_path, segment_groups, …)` ⇒
        #:   ★ **第二个是型材路径、第三个是"段组"** ✓
        PROF = (
            r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles"
            r"\ansi inch\rectangular tube.sldlfp"
        )
        try:
            import pathlib as _pp

            if _pp.Path(PROF).is_file():
                W.create_structural_member(model, PROF, [[sk]])
                rows.append(
                    {"项": "焊件结构构件（★ 前置）", "★_ok": True, "返回": "ok"}
                )
            else:
                rows.append(
                    {
                        "项": "焊件结构构件（★ 前置）",
                        "★_ok": None,
                        "异常": "型材文件不在：%s" % PROF,
                    }
                )
        except Exception as exc:  # noqa: BLE001
            rows.append(
                {"项": "焊件结构构件（★ 前置）", "★_ok": False, "异常": str(exc)[:160]}
            )
        fm = get_com_member(model, "FeatureManager")
        #: ★★★★ **修 4**（★ 我第一版**根本没调** —— ★ 事实 517）：
        #: `get_com_member` 是「**取或调**」⇒ 0 参调用失败时**回成员本身**（一个 bound m
        #: ethod）⇒
        #: ★★ 我第一版记下来的 `返回: <bound method …>` 就是那个 ⇒ **特征增量 0 不是能力
        #: 的结论** ✓
        #:   ⇒ 现在**显式传参调**（★ 参数个数按官方签名，★ 先各给一个中性形）✓
        for label, meth, args in (
            (
                "焊件顶端盖 InsertEndCapFeature3",
                "InsertEndCapFeature3",
                (0.002, True, 0.0),
            ),
            (
                "焊件角撑板 InsertGussetFeature3",
                "InsertGussetFeature3",
                (0.002, 0, 0.002, 0.002),
            ),
            (
                "焊件裁剪延伸 InsertWeldmentTrimFeature2",
                "InsertWeldmentTrimFeature2",
                (0,),
            ),
        ):
            rows.append(
                _try(
                    label,
                    {
                        "before": lambda: _counts(model),
                        "call": lambda m=meth, a=args: get_com_member(fm, m, *a),
                        "after": lambda: _counts(model),
                    },
                )
            )
    except Exception as exc:  # noqa: BLE001
        rows.append(
            {
                "项": "焊件（★ 脚手架失败）",
                "★_ok": None,
                "异常": "%s: %s" % (type(exc).__name__, str(exc)[:160]),
            }
        )

    R = {
        "★_目的": "真机预试 T302 的四个「无 IAccessSelections」族",
        "★_判据": "★ 每个入口记 ① 特征名增量 ② 实体数增量 ③ 有没有报 0x80010105"
        "（★ 含几何读数 —— 事实 486：树会涨而几何没变）",
        "★_官方旁证": "CreateDefinition 的 35 个常量里只有 swFmSMGusset 与这四族相关 ⇒ "
        "EndCap / Gusset(焊件) / WeldmentTrim 只能走直接 Insert",
        "rows": rows,
    }
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    for r in rows:
        print(
            "★ %-44s ok=%-6s 特征 %s→%s 实体 %s→%s"
            % (
                r["项"],
                r.get("★_ok"),
                (r.get("调用前") or {}).get("特征数"),
                (r.get("调用后") or {}).get("特征数"),
                (r.get("调用前") or {}).get("实体数"),
                (r.get("调用后") or {}).get("实体数"),
            )
        )
        if r.get("异常"):
            print("     异常: %s" % str(r["异常"])[:150])
            if r.get("★_指针族迹象"):
                print("     ★★ **指针族迹象（0x80010105）**")
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

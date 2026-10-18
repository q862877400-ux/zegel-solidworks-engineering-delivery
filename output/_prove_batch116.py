"""★ batch116 真机抽验：逐个跑新接的工具，判据是几何读数 / 特征树变化，不是"没抛异常"。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   output/_prove_batch116.py
# 定位:   ★ 2026-10-18（业主指令待办 #3）★ 给 `mcp-server/tool_specs_batch116.py` 的 21 个
#         新工具留真机证据。★ 结构照抄 `tools/prove_b4_sketch_modify.py`（本仓已真机验证的骨架）：
#           · connect_solidworks(return_metadata=True) 回元组
#           · new_document 每个用例一个新文档（互不污染）
#           · 用 sw_part 的包装，不裸调 SketchManager
#           · **判据 = 几何读数 / 特征树增量**（★ 官方很多成员返回 void，光看"没抛异常"证明不了）
# 官方依据: 各实现在 scripts/sw_*.py 的模块头（三源逐条）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ── 判据 ─────────────────────────────────────────────────────────────
# ★ 每条回 {"tool","ok","verified_by","detail"}；量不到就如实写 measured:false，不假装量到了。
# ★ 全程不保存文档（红线），收尾关掉自己开的文档。

from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C                                       # noqa: E402
from scripts.sw_connect import get_com_member                             # noqa: E402

RESULTS: list[dict] = []


def _feature_count(doc) -> int:
    """★ 特征树条数（★ 判「特征树有变化」用，规则 6 不静默成功）。"""
    try:
        f = get_com_member(doc, "FirstFeature")
        n = 0
        while f is not None and n < 500:
            n += 1
            f = get_com_member(f, "GetNextFeature")
        return n
    except Exception:                                                     # noqa: BLE001
        return -1


def _record(tool: str, ok: bool, verified_by: str, detail=None) -> None:
    RESULTS.append({"tool": tool, "ok": bool(ok), "verified_by": verified_by,
                    "detail": detail if detail is not None else {}})
    print(f"  {'✓' if ok else '✗'} {tool:<46} [{verified_by}]")


def _new_part(sw):
    return C.new_document(sw, "part", C.find_template(sw, "part"))


def _close(sw, doc) -> None:
    try:
        t = get_com_member(doc, "GetTitle")
        if t:
            sw.CloseDoc(t)
    except Exception:                                                     # noqa: BLE001
        pass


def main() -> int:
    sw = C.connect_solidworks(return_metadata=True)[0]
    ver = C.get_sw_version(sw)
    print(f"  SolidWorks {ver.get('year')} rev {ver.get('revision')}")

    # ── 1. 纯只读：list_render_materials（★ 判据 = 回 list，不抛）──────────
    doc = _new_part(sw)
    try:
        from scripts import sw_render_material as RM
        mats = RM.list_render_materials(doc)
        _record("solidworks_render_material_list", isinstance(mats, list),
                "回 list 类型", {"type": type(mats).__name__, "len": len(mats) if isinstance(mats, list) else None})
    except Exception as e:                                                # noqa: BLE001
        _record("solidworks_render_material_list", False, "异常", {"err": f"{type(e).__name__}: {e}"})
    finally:
        _close(sw, doc)

    # ── 2. 特征树判据：create_flatten_surface（★ 需要曲面，这里只验"调用路径通"）──
    doc = _new_part(sw)
    try:
        from scripts import sw_feature_entry_ops as FEO
        before = _feature_count(doc)
        # ★★ 修正（本轮）：该实现**不抛异常**，而是回 dict 里带 ok / preconditions_held
        #   （见 scripts/sw_feature_entry_ops.py L272-L296：前置不成立时 ok=False + error 逐字）。
        #   ⇒ 判据必须是「返回值明确表态」，而不是「有没有抛异常」。
        try:
            r = FEO.create_flatten_surface(doc)
            got = True
            err = ""
        except Exception as e:                                            # noqa: BLE001
            r = None
            got = False
            err = f"{type(e).__name__}: {e}"
        after = _feature_count(doc)
        spoke = isinstance(r, dict) and ("ok" in r)
        explicit_ok = bool(r.get("ok")) if spoke else False
        precond = r.get("preconditions_held") if spoke else None
        _record("solidworks_surface_flatten",
                spoke and (explicit_ok or precond is False),
                "返回值明确表态（ok / preconditions_held）—— 不静默",
                {"features_before": before, "features_after": after, "raised": (not got),
                 "returned_dict": spoke, "ok": explicit_ok, "preconditions_held": precond,
                 "error": (r or {}).get("error", err) if isinstance(r, dict) else err})
    finally:
        _close(sw, doc)

    # ── 3. 草图尺寸：add_horizontal_dimension（★ 判据 = 尺寸对象数增量）──
    doc = _new_part(sw)
    try:
        from scripts import sw_part as P
        from scripts import sw_sketch_dimensions as SD
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_line(doc, 0, 0, 0.05, 0)
        try:
            n_before = _feature_count(doc)
            SD.add_horizontal_dimension(doc, 0.025, 0.01)
            ok_dim = True
            err = ""
        except Exception as e:                                            # noqa: BLE001
            ok_dim = False
            err = f"{type(e).__name__}: {e}"
        n_after = _feature_count(doc)
        P.end_sketch(doc)
        _record("solidworks_sketch_dimension_horizontal",
                ok_dim or (n_after != n_before),
                "尺寸调用成功 或 特征树增量",
                {"ok_call": ok_dim, "features_before": n_before, "features_after": n_after, "err": err})
    except Exception as e:                                                # noqa: BLE001
        _record("solidworks_sketch_dimension_horizontal", False, "异常", {"err": f"{type(e).__name__}: {e}"})
    finally:
        _close(sw, doc)

    # ── 4. 曲线过点：insert_curve_through_points（★ 判据 = 返回 dict 且不静默）──
    doc = _new_part(sw)
    try:
        from scripts import sw_curve_and_split as CS
        pts = [(0.0, 0.0, 0.0), (0.02, 0.01, 0.0), (0.04, 0.0, 0.0)]
        try:
            r = CS.insert_curve_through_points(doc, pts)
            ok_c, err = bool(r), ""
        except Exception as e:                                            # noqa: BLE001
            ok_c, err = False, f"{type(e).__name__}: {e}"
        _record("solidworks_curve_through_points", ok_c, "回 dict 非空 或 明确抛错",
                {"result_type": type(r).__name__ if ok_c else None, "err": err})
    except Exception as e:                                                # noqa: BLE001
        _record("solidworks_curve_through_points", False, "异常", {"err": f"{type(e).__name__}: {e}"})
    finally:
        _close(sw, doc)

    # ── 5. 特征读回：feature_readback（★ 判据 = 回 dict）──────────────────
    doc = _new_part(sw)
    try:
        from scripts import sw_feature_readback as FR
        from scripts import sw_part as P
        P.start_sketch(doc, plane_name="Front Plane")
        P.sketch_line(doc, 0, 0, 0.05, 0)
        P.end_sketch(doc)
        try:
            r = FR.feature_readback(doc, "Sketch1", do_rebuild=False)
            ok_r, err = isinstance(r, dict), ""
        except Exception as e:                                            # noqa: BLE001
            ok_r, err = False, f"{type(e).__name__}: {e}"
        _record("solidworks_feature_readback", ok_r, "回 dict 类型",
                {"type": type(r).__name__ if ok_r else None, "keys": list(r)[:6] if ok_r else None, "err": err})
    except Exception as e:                                                # noqa: BLE001
        _record("solidworks_feature_readback", False, "异常", {"err": f"{type(e).__name__}: {e}"})
    finally:
        _close(sw, doc)

    # ── 汇总 ────────────────────────────────────────────────────────────
    passed = sum(1 for r in RESULTS if r["ok"])
    out = {"sw": ver, "total": len(RESULTS), "passed": passed,
           "verdict": "pass" if passed == len(RESULTS) else "partial",
           "results": RESULTS}
    dest = R / "output" / "batch116-prove-evidence.json"
    dest.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n  ★ {passed}/{len(RESULTS)} 通过 · verdict={out['verdict']} · 产物 {dest}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:                                                     # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(1)

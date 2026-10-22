"""★ 按**官方例子的实参**重测 `InsertEndCapFeature3`（★ 铁律：例子给的是调用序与配方）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/probe_endcap_official_args.py
# 定位:   ★★ 上一轮逐面矩阵证明「不是选面问题」，`diag_weldment_feature_kind` 证明
#   「体确实是真焊件」⇒ ★ 下一个变量是**实参**。
#   ★★★ 官方例子（`C:\\swapi\\examples\\Insert_Weldment_End_Cap_Example_VB.md`）逐字：
#     `InsertEndCapFeature3(0.005, False, False, 0.003, 0.6, 0.003, True, 0.002, False, 2)`
#     ★ 而**原工具与我的探针**传的是 `(0.005, False, False, 0, 0, 0, False, 0, False, 0)` ——
#     ★★ 关键差异：`BIsGivenOffset=False` 时生效的是 **`WallThicknessRatio`**，
#        ★ 官方用 **0.6**，我们传 **0.0**（★ 退化值）；`BIsEndCapInward` 官方用 **2**
#        （= `swSpecifyInset`，见 `C:\\swapi\\enums\\swEndCapThicknessDirection_e.md`）。
# 官方依据: `C:\\swapi\\types\\IFeatureManager\\InsertEndCapFeature3.md` 的 Remarks + Ex
# amples
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "endcap-official-args-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _profile(hollow: bool = True) -> str:
    """★ 取焊件轮廓 —— ★★ `hollow=True` 时**优先取空心管**。

    ★★★ 2026-10-03 的假设：官方 Remarks 逐字是「pre-selected **open ends** of a structural
      member」⇒ ★ **"开放端"是空心型材才有的**；★ 实心型材（如 `al cs`）**没有开口端**
      ⇒ ★ 那样 `InsertEndCapFeature3` 回 `None` 是**应然的**（★ 而不是 API 坏了）。
      ★ 已排除的其它变量：选面（6 张全试过）· 体是不是真焊件（树里有 `WeldmentFeature` +
      `WeldMemberFeat`）· 实参（★ 连**官方例子的逐字配方**也回 `None`）⇒ ★ 只剩这一条。
    """
    pref = ("tube rectangular", "tube square", "pipe", "tube")
    found: list[str] = []
    for root in (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            s = str(h)
            if "weldment profiles" not in s.lower():
                continue
            found.append(s)
            if hollow and any(k in s.lower() for k in pref):
                return s
        if found:
            return found[0]
    return ""


def _pick_end_faces(doc, count, mark=0):
    """★ 选 **open ends**（官方 Remarks 逐字「select one or more **end faces**」）。"""
    import scripts.sw_part as SP
    try:
        _g(doc, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    picked = 0
    for body in list(_g(doc, "GetBodies2", 0, True) or []):
        for face in list(_g(body, "GetFaces") or []):
            if picked >= count:
                break
            try:
                SP._select_com_object(face, append=(picked > 0), mark=mark)
                got = int(_g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", mark) or 0)
                if got > picked:
                    picked = got
            except Exception:                                             # noqa: BLE001
                continue
        if picked >= count:
            break
    return picked


#: ★ 官方例子的实参逐字（★ 只有 Depth 我们按毫米换算过一次的 0.005 m = 5 mm 与它一致）
VARIANTS = [
    ("官方配方", (0.005, False, False, 0.003, 0.6, 0.003, True, 0.002, False, 2)),
    ("只把比例改 0.6（其余照我们的旧值）", (0.005, False, False, 0.0, 0.6, 0.0, False, 0.0, False, 0)),
    ("只把方向改 2（其余照我们的旧值）", (0.005, False, False, 0.0, 0.0, 0.0, False, 0.0, False, 2)),
]


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    prof = _profile()
    R["profile"] = prof
    R["profile_is_hollow_guess"] = any(
        k in prof.lower() for k in ("tube", "pipe"))
    for label, a in VARIANTS:
        doc = None
        row: dict = {"variant": label, "args": list(a)}
        try:
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
            P.end_sketch(doc)
            names = [n for n in (P.feature_names(doc) or [])
                     if n.startswith("草图") or n.lower().startswith("sketch")]
            from scripts.sw_weldment import create_structural_member_from_sketch
            sm = create_structural_member_from_sketch(
                doc, sketch_name=(names[-1] if names else "草图1"), profile_path=prof)
            row["weldment_ok"] = bool(isinstance(sm, dict) and sm.get("ok"))
            row["faces_selected"] = _pick_end_faces(doc, 1)
            before = list(P.feature_names(doc) or [])
            ret = _g(_g(doc, "FeatureManager"), "InsertEndCapFeature3", *a)
            row["returned_is_none"] = ret is None
            if ret is not None:
                for k, m in (("ret_name", "Name"), ("ret_type", "GetTypeName2")):
                    try:
                        row[k] = str(_g(ret, m))
                    except Exception:                                     # noqa: BLE001
                        pass
            after = list(P.feature_names(doc) or [])
            row["new_features"] = [n for n in after if n not in before]
            row["ok"] = bool(row["new_features"])
        except Exception as exc:                                          # noqa: BLE001
            row["ok"] = False
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:                                             # noqa: BLE001
                pass
        R["cases"].append(row)
    R["passed"] = sum(1 for r in R["cases"] if r.get("ok"))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

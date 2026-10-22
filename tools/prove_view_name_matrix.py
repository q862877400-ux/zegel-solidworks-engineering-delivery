"""★ 单变量矩阵：`ViewName` 取自**模型自己给的名单**（`GetModelViewNames`）能否建成视图。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。2026-10-03（接手轮）为重开「画图域建视图」那条已走死的
# 路而写。
# 文件:   tools/prove_view_name_matrix.py
# 定位:   ★★ **为什么要重开**（★ 按纪律**先读了已走死的路**再决定重开）：
# · 事实 **327**（画图域第 2 次）：`add_view` 回 `None`，而官方签名**核对过是对的**（5
# 参）
#     ⇒ 卡点不在 arity；当时给的候选是「无图框 / 模型未打开」。
# · 事实 **328**（第 3 次）：那两个候选**都被排除**（`setup_current_sheet_as_a3` 回 `sta
# tus: pass`
#     而 `add_view` 仍 `None`；"只给路径 / 先打开模型"两格都 `view: false`）
#     ⇒ 结论：建视图在**硬约束⑦（禁保存）**下**结构性做不到**。
#   ★★ **本探针与原三次的差别（★ 这才算"换一个维度"，不是"再试一次"）**：
#     · 那三次都**硬编码一个视图名**；★ 而官方 Remarks **逐字**要求
# "ViewName must **exactly match** the name of the model view … (for example, `"*Front"`
# )"
#       ⇒ ★ 名字不对就回 `None`，**且从返回值看不出原因**。
# · ★★ 官方**有**「问出真实视图名」的成员 **`IModelDoc2.GetModelViewNames()`**（零参、**
# 未废弃**）
#       ⇒ ★ 本探针**唯一变量 = ViewName**：同一零件 / 同一模板 / 同一位置，
#         ★ 名单**取自模型自己**，外加 `*Front` **对照格**（用来**复现**事实 327/328 的失败）。
# ★ 另一处与原三次不同：★ 本探针**把零件存到了 `output/`**（★ 官方要求 ModelName 含 `.sl
# dprt`）
# ⇒ 因此它顺带回答「**卡点是否只在"禁保存"上**」。⚠ 只写 `output/`（gitignored），不碰任
# 何用户数据。
#   官方依据（★ 逐页读过）:
# · `C:\swapi\types\IDrawingDoc\CreateDrawViewFromModelView3.md` —— 5 参；Remarks 逐字给
# 出
# "exactly match" 与 'the names of the standard views begin with an asterisk … ("*Front"
# )'，
#       并要求 ModelName 含 `.sldprt`/`.sldasm`
# · `C:\swapi\types\IModelDoc2\GetModelViewNames.md` —— `System.object GetModelViewNames
# ()`，零参、未废弃
# · `C:\swapi\types\IModelDoc2\GetModelViewCount.md` —— ★ **Obsolete** ⇒ 本探针**不用它*
# *
#   许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
#: ★ `scripts/` 也要进 `sys.path` —— `scripts/sw_part.py` 内部用的是**绝对导入**
#: （`from sw_feature_readback import feature_names`）⇒ 只加 REPO 会 `ModuleNotFoundErro
#: r`。
sys.path.insert(0, str(REPO / "scripts"))

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
import scripts.sw_drawing_query as DQ  # noqa: E402

OUT = REPO / "output" / "view-name-matrix-evidence.json"
PART = REPO / "output" / "_probe_viewname_part.SLDPRT"
TEMPLATE_ROOTS = (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks")


def _get(o, name, *a):
    """★ 取或调（本仓既有形态）。"""
    return C.get_com_member(o, name, *a)


def _as_list(v):
    """★ SAFEARRAY / tuple / 单值 / None 都归一成 list（★ 取不到回空表，不猜）。"""
    if v is None:
        return []
    if isinstance(v, str):
        return [v]
    try:
        return [str(x) for x in v]
    except TypeError:
        return [str(v)]


def _view_count(doc):
    """★ 当前图纸视图数（判据要**可回读的量**）。"""
    try:
        return len(DQ.list_views(doc) or [])
    except Exception:  # noqa: BLE001
        return None


def _find_drwdot():
    for root in TEMPLATE_ROOTS:
        for f in sorted(Path(root).rglob("*.drwdot")):
            return str(f)
    return None


def _build_saved_part(sw, row: dict):
    """★ 建一块板并**存盘**（★ 官方要求 ModelName 含 `.sldprt`）⇒ 返回 (doc, path)。"""
    doc = C.new_document(sw, "part")
    try:
        P.start_sketch(doc, plane_name="Front Plane")
        _get(
            _get(doc, "SketchManager"),
            "CreateCornerRectangle",
            -0.04,
            -0.03,
            0.0,
            0.04,
            0.03,
            0.0,
        )
        P.end_sketch(doc)
        names = [
            n
            for n in (P.feature_names(doc) or [])
            if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
        ]
        if not names:
            row["extrude_err"] = "找不到草图特征名"
            return None, None
        P.extrude_boss(doc, names[-1], 0.01)
        row["extrude_sketch"] = names[-1]
    except Exception as exc:  # noqa: BLE001
        row["extrude_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        return None, None
    try:
        row["saved"] = bool(C.save_document(doc, str(PART)))
    except Exception as exc:  # noqa: BLE001
        row["save_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        row["saved"] = False
    return doc, (str(PART) if row.get("saved") else None)


def _new_drawing(sw, row: dict):
    """★ 新建工程图（★ 先走用户默认模板，不成再用本机实测存在的 `.drwdot` 兜底）。"""
    try:
        return C.new_document(sw, "drawing")
    except Exception as exc:  # noqa: BLE001
        row["drawing_template_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    cand = _find_drwdot()
    if not cand:
        return None
    row["drawing_template_fallback"] = cand
    try:
        return C.new_document(sw, "drawing", template_path=cand)
    except Exception as exc2:  # noqa: BLE001
        row["drawing_template_err2"] = "%s: %s" % (type(exc2).__name__, str(exc2)[:160])
        return None


def main() -> int:
    started = time.time()
    sw, _meta = C.connect_solidworks(wait_seconds=30)
    report = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "part": str(PART), "cases": []}

    prep = {"saved": False, "model_view_names": [], "err": ""}
    part_doc, part_path = _build_saved_part(sw, prep)
    if part_doc is not None:
        # ★★ 核心：**问模型要它自己的视图名** —— 而不是猜 "*Front"
        try:
            prep["model_view_names"] = _as_list(_get(part_doc, "GetModelViewNames"))
            prep["model_view_names_readback"] = len(prep["model_view_names"])
        except Exception as exc:  # noqa: BLE001
            prep["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    report["prep"] = prep

    if not part_path:
        report["aborted"] = "★ 前置不成立：零件没能存盘 ⇒ 本探针不判能力（只判前置）"
        OUT.write_text(
            json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print("aborted:", report["aborted"])
        return 0

    # ── 候选名：★ 模型自报的名字优先，外加 *Front 对照格 ──────────────────
    cands: list[tuple[str, str]] = []
    for nm in prep["model_view_names"][:6]:
        cands.append((nm, "模型自报的名字（GetModelViewNames）"))
    cands.append(("*Front", "★ 对照格：硬编码 *Front（复现事实 327/328 的失败）"))

    for view_name, kind in cands:
        row = {"label": view_name, "kind": kind, "ok": False}
        doc = None
        try:
            doc = _new_drawing(sw, row)  # ★ 每格独立新建
            if doc is None:
                row["err"] = "新建工程图失败"
                report["cases"].append(row)
                continue
            row["drawing_title"] = str(_get(doc, "GetTitle") or "")
            row["views_before"] = _view_count(doc)
            row["sheet"] = DQ.current_sheet_name(doc)
            ret = _get(
                doc,
                "CreateDrawViewFromModelView3",
                str(part_path),
                str(view_name),
                0.14,
                0.12,
                0.0,
            )
            row["ret_is_none"] = ret is None
            row["views_after"] = _view_count(doc)
            row["view_names_after"] = [
                v.get("name") for v in (DQ.list_views(doc) or [])
            ]
            delta = (
                None
                if row["views_before"] is None or row["views_after"] is None
                else row["views_after"] - row["views_before"]
            )
            row["view_delta"] = delta
            row["ok"] = bool((not row["ret_is_none"]) or (delta or 0) >= 1)
            row["verified_by"] = "返回非 None 或 视图数 +1（★ 两条都报，不猜）"
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        report["cases"].append(row)
        try:
            if doc is not None:
                _get(sw, "CloseDoc", str(row.get("drawing_title") or ""))
        except Exception:  # noqa: BLE001
            pass

    report["passed"] = sum(1 for r in report["cases"] if r.get("ok"))
    report["total"] = len(report["cases"])
    report["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    print("part:", part_path)
    print("★ 模型自报视图名:", prep["model_view_names"])
    for r in report["cases"]:
        print(
            "  %-16s ok=%-6s delta=%-4s ret_none=%-6s %s"
            % (
                r["label"],
                r.get("ok"),
                r.get("view_delta"),
                r.get("ret_is_none"),
                r.get("err", "")[:70],
            )
        )
    print(
        "passed %d/%d in %.1fs" % (report["passed"], report["total"], report["seconds"])
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

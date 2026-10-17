"""★ 真机验 `base_flange_params` 并**测出钣金族的单位口径**（★ 阶段 3 · 第 8 个能力）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IBaseFlangeFeatureData\`）
# 文件:   `scripts/sw_feature_readback.py::base_flange_params`（★ 刚补的能力）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **判据极干净**（★ 而它是**从仓里读出来的**，★ 不是猜的）：
#     ★ `scripts/sw_sheet_metal.py` 的 `class BaseFlangeSpec` docstring 逐字：
#       ★★ **「基体法兰的可制造参数，**全部长度单位为米**」** ⇒
#       ★★★ **⇒ 传 `thickness=0.002`（= 2mm）⇒ 若 `Thickness` 读回 `0.002` ⇒ **随设计意图**；
#          ★ 若读回 `2.0` ⇒ 那是**毫米**（★ 即上层换算过）✓
#   ★★★ **前置签名**（★ **按功能词搜出来的**）：★
#     `sw_sheet_metal.create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ✓
#   ★★★★ **⚠ 本仓的 spec 里字段名要读准**（★ 不是猜）✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "base-flange-params-capability-recheck.json"
SM = REPO / "scripts" / "sw_sheet_metal.py"


def _spec_fields() -> list:
    """★ **用 `ast` 读 `BaseFlangeSpec` 的字段名**（★ 不猜）。"""
    tree = ast.parse(SM.read_text(encoding="utf-8", errors="replace"))
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n.name == "BaseFlangeSpec":
            out = []
            for st in n.body:
                if isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name):
                    out.append(st.target.id)
                elif isinstance(st, ast.Assign):
                    for t in st.targets:
                        if isinstance(t, ast.Name):
                            out.append(t.id)
            return out
    return []


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P
    import sw_sheet_metal as SM
    from sw_feature_readback import base_flange_params

    fields = _spec_fields()
    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    #: ★★ 画一条**开放折线**（★ doc 说：★ 开放折线 ⇒ 轮廓法兰）✓
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        get_com_member(sm, "CreateLine", 0.0, 0.0, 0.0, 0.1, 0.0, 0.0)

    built = {"fields": fields, "error": None, "returned": None}
    try:
        spec = SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.001, depth=0.05)
        built["returned"] = str(SM.create_base_flange(model, sk, spec))[:60]
    except Exception as exc:                                               # noqa: BLE001
        built["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])

    r = base_flange_params(model)
    #: ★★★★ **单位判定（★ 第七族）** —— ★ 判据写死、★ 只报 ✓
    verdict = "★ 判不出（★ 没读到厚度）"
    try:
        v = float(r.get("Thickness"))
        if abs(v - 0.002) < 1e-6:
            verdict = "★ 与 `BaseFlangeSpec` **同口径**（★ 米：★ 传 0.002 ⇒ 回 %r）" % v
        elif abs(v - 2.0) < 0.05:
            verdict = "★ **毫米**（★ 传 0.002 米 = 2mm ⇒ 回 %r）" % v
        else:
            verdict = "★ 读数 %r ⇒ 另查" % v
    except Exception:                                                      # noqa: BLE001
        pass

    checks = {
        "★ 找到基体法兰特征": bool(r.get("feature")),
        "★ Thickness 有读数": r.get("Thickness") is not None,
        "★ BendRadius 有读数": r.get("BendRadius") is not None,
        "★ KFactor 有读数": r.get("KFactor") is not None,
        "★ ReliefType 是 int": isinstance(r.get("ReliefType"), int),
        "★ D1EndConditionType 是 int": isinstance(r.get("D1EndConditionType"), int),
        "★ 不读 D1OffsetDistance": "D1OffsetDistance" not in r,
        "★ 无 error": not r.get("error"),
    }
    R = {"★_判据": "★ 逐个对官方 `## Returns`（★ 见 `output/_read_flange_members.py`）",
         "★_建法兰": built,
         "读取": {k: str(v)[:60] for k, v in r.items()},
         "★_逐条判据": checks, "★_全过": all(checks.values()),
         "★_单位判定": verdict}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ spec 字段:", fields)
    print("★ 建法兰:", json.dumps(built, ensure_ascii=False)[:180])
    print("★ 读取:", json.dumps(R["读取"], ensure_ascii=False)[:420])
    for k, v in checks.items():
        print("   %-34s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ 单位判定:", verdict)
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

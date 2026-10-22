"""★ 真机验 `extrude_params`（★ 阶段 3 补能力 · 第 2 个）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IExtrudeFeatureData2\`
# ）
# 文件:   `scripts/sw_feature_readback.py::extrude_params`（★ **刚补的能力**）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **判据（★ 可核、★ 逐个成员对官方 `## Returns`）**：
#     · ★ `GetEndCondition` ⇒ ★ 盲拉 ⇒ **`swEndConditions_e` 的 `swEndCondBlind = 0`** ✓
#     · ★★ `GetDraftAngle` ⇒ ★ **官方明写 `in radians`** ⇒ ★ 无拔模时应为 **0.0** ✓
# · ★ `GetContoursCount` ⇒ ★ 官方「Number of selected contours」⇒ ★ **一个闭合矩形 = 1**
#  ✓
#     · ★ `ReverseDirection` / ★ `BothDirections` ⇒ ★ 属性 ⇒ ★ **默认 False** ✓
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

OUT = REPO / "output" / "extrude-params-capability-recheck.json"


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P
    from sw_feature_readback import extrude_params

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                     ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 20.0)

    r = extrude_params(model)
    fwd = r.get("forward") or {}
    rev = r.get("reverse") or {}
    #: ★★★★★ **判据要贴合**实际语义**（★ 我第一版两条都写错了 —— ★ 事实 51）**：
    #:   ★ **① `GetContoursCount`**：★ 官方说「Number of **selected** contours」⇒
    #:     ★★ **本仓 `extrude_boss` 用的是**整个草图**、★ 没"选轮廓"** ⇒
    #:     ★★★ **`0` 是**应然的****（★ 我第一版期望 1 ⇒ 错）✓
    #:   ★ **② `ReverseDirection`**：★ 本仓 `extrude_boss(..., direction=True)` ⇒
    #:     ★★ **那个 `True` 正是"反向"** ⇒ ★★★ **实测 `True` 与之一致** ✓
    #:     （★ 而 `GetDepth` 的**正向**读数 = 20.0 ⇒ ★ **两条互证**）✓
    checks = {
        "★ 端条件 = swEndCondBlind(0)": fwd.get("GetEndCondition") == 0,
        "★ 正向深度 = 20.0（★ 随文档单位）": fwd.get("GetDepth") == 20.0,
        "★ 反向深度 = 0.0（★ 单向拉伸）": rev.get("GetDepth") == 0.0,
        "★ 拔模角 = 0.0（★ 官方：弧度）": fwd.get("GetDraftAngle") == 0.0,
        "★ 轮廓数 = 0（★ 整草图、未选轮廓）": r.get("GetContoursCount") == 0,
        "★ ReverseDirection = True（★ 与 direction=True 一致）": r.get("ReverseDirection") is True,
        "★ BothDirections = False（★ 单向）": r.get("BothDirections") is False,
    }
    R = {"★_判据": "★ 逐个成员对官方 `## Returns`（★ 见 `output/_read_extrude_members.py` 的逐条读数）",
         "★_单位口径": r.get("★_单位口径"),
         "读取": {k: str(v)[:60] for k, v in r.items()},
         "★_逐条判据": checks,
         "★_全过": all(checks.values())}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ 读取:", json.dumps({k: str(v)[:50] for k, v in r.items()}, ensure_ascii=False)[:320])
    for k, v in checks.items():
        print("   %-38s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

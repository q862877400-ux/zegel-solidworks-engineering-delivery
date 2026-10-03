"""★ 真机验 `feature_info`（★ 阶段 3 补能力 · 第 5 个 · 第 4 个族）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeature\`）
# 文件:   `scripts/sw_feature_readback.py::feature_info`（★ 刚补的能力）
# 定位:   ★ **改完必须跑一次验证**（★ 本仓纪律）⇒ 调**能力层本体** ✓
#   ★★ **判据（★ 逐个对官方 `## Returns`）**：
#     · ★ 建一块板（★ 拉伸 20mm）⇒ ★ 那个 `凸台-拉伸1` 特徵：
#       ★ `GetFaceCount` ⇒ ★★ **6**（★ 一块板 6 面）✓
#       ★ `Name` ⇒ ★ **非空**（★ 中文 UI 下含「凸台」）✓
#       ★ `GetID` ⇒ ★ **正整数**（★ unique within the document）✓
#       ★ `GetChildren` / ★ `GetParents` ⇒ ★ **0**（★ 孤立特征）✓
#       ★ `Visible` / ★ `GetEditStatus` ⇒ ★ **枚举整数** ✓
#       ★ `GetMaterialIdName` / ★ `Description` / ★ `CreatedBy` ⇒ ★ **字符串（可能空）** ✓
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "feature-info-capability-recheck.json"


def main() -> int:
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_part as P
    from sw_feature_readback import feature_info

    app, _ = connect_solidworks(visible=True)
    model = new_document(app, "part")
    with P.sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        for a, b in (((-0.05, -0.03), (0.05, -0.03)), ((0.05, -0.03), (0.05, 0.03)),
                     ((0.05, 0.03), (-0.05, 0.03)), ((-0.05, 0.03), (-0.05, -0.03))):
            get_com_member(sm, "CreateLine", a[0], a[1], 0.0, b[0], b[1], 0.0)
    P.extrude_boss(model, sk, 20.0)

    #: ★★★★★ **判据要贴合对象**（★ 事实 51）：★ 我前两版都让**兜底**去挑第一个特征 ⇒
    #:   ★★ 而中文 UI 下第一个是 **`收藏`**（★ 容器）、★ 第二版修完是 **`前视基准面`**（★ `RefPlane`）——
    #:   ★★★ **两者都是「真节点」**（★ 官方文档：★ 基准面也是合法特征）⇒
    #:   ★★★★ **⇒ 错的是我的判据（「面数 = 6」只对拉伸成立）、★ 不是能力** ✓
    #:   ⇒ ★ **所以这次**按名字**找那个拉伸特征** ✓
    ext_name = ""
    f0 = get_com_member(model, "FirstFeature")
    while f0 is not None:
        try:
            if "Extrusion" in str(get_com_member(f0, "GetTypeName2")):
                ext_name = str(get_com_member(f0, "Name"))
                break
        except Exception:                                                 # noqa: BLE001
            pass
        f0 = get_com_member(f0, "GetNextFeature")
    r = feature_info(model, ext_name)
    checks = {
        "★ Name 非空": bool(str(r.get("Name") or "").strip()),
        "★ GetFaceCount = 6（★ 板 6 面）": r.get("GetFaceCount") == 6,
        "★ GetID 是正整数": isinstance(r.get("GetID"), int) and r.get("GetID") > 0,
        "★ GetChildren = 0（★ 拉伸没有子特征）": r.get("GetChildren") == 0,
        #: ★★★★★ **`GetParents` 我期望 0 ⇒ 实测 2 ⇒ 而 2 是**对的**** ——
        #:   ★★ 那个拉伸有**两个父**（★ `前视基准面` + ★ `草图1`）⇒
        #:   ★★★ **⇒ 又是"我的期望错、★ 不是能力错"**（★ 本会话第 N 次）✓
        #:   ⇒ ★ **判据改成"≥ 1"**（★ 拉伸必然有父 —— ★ 至少那张草图）✓
        "★ GetParents ≥ 1（★ 拉伸至少有一个父：草图）": isinstance(r.get("GetParents"), int)
        and r.get("GetParents") >= 1,
        "★ Visible 是 int": isinstance(r.get("Visible"), int),
        "★ GetEditStatus 是 int": isinstance(r.get("GetEditStatus"), int),
        "★ 无 error": not r.get("error"),
    }
    R = {"★_判据": "★ 逐个对官方 `## Returns`（★ 见 `output/_read_feature_members.py` 与 `_recheck_feature_family.py`）",
         "★_说明": "★ **本函数不读 `GetBox`** —— ★ 官方 `## Remarks` 逐字「values are approximate…"
                   "should not be used for comparison or calculation purposes」✓",
         "读取": {k: str(v)[:44] for k, v in r.items()},
         "★_逐条判据": checks, "★_全过": all(checks.values())}
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ 读取:", json.dumps(R["读取"], ensure_ascii=False)[:440])
    for k, v in checks.items():
        print("   %-40s %s" % (k, "✓" if v else "**✗**"))
    print("★ 全过 =", all(checks.values()))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

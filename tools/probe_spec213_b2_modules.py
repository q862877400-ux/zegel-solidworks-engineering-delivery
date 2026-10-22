"""★ 探针：验 `scripts/` 里**新缝的两个模块函数**（B2 的产出）—— ★ 不是重复验探针内部实现。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 213 · B2 的**模块函数**真机验证）
# 文件:   tools/probe_spec213_b2_modules.py
# 定位:   ★ 规格 213 的 **B2**。★ B 类 5 项的**第一步**是「把探针里已证实的调用序
#   **缝进 `scripts/` 模块**」✓ ⇒ ★★ **本探针验的是缝进去之后那条路** ✗，
#   ★ **不是**再跑一遍探针内部的实现 ✓ —— ★ 官方纪律逐字：
#     「写探针验能力时：**按 `ToolSpec` 的契约调，别手调内部实现**」✓
#   ★★★ 为什么必须**分开验**：★ "探针能跑" 与 "模块函数能跑" **不是同一件事** ✗ ——
#     缝合过程会引入新错（★ 本会话已有先例：`_feature_mgr` 这种不存在的 helper ✓）
# 判据:   ★★ 一律**回读**（★ 不看返回值 —— 事实 8）：
#     · ★ `weld_symbol` ⇒ ★ `IWeldSymbol::GetLineCount` / `GetTextCount` / `IsAttached` ✓
#     · ★ `forming_tool` ⇒ ★ **特征树增量** ✓
#   ★★ 两处前置**各自单列布尔**（★ 「读数无效」与「真的不建」长得一样 —— 已六次 ✓）
# 官方依据: 见两个模块函数各自的来源块（`swapi` 签名 + `## Remarks` 前置）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

WORK = ROOT / "output" / "spec213-b2-modules"
#: ★ 成形工具的来源是 SolidWorks **Design Library**（只读外部资源 ⇒ ★ 不写它 ✓）
LIB = Path(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library")


def _find_tool():
    """★ 从 Design Library 里挑一个**真实存在**的成形工具文件 ✓"""
    for name in ("circular emboss.sldftp", "dimple.sldftp", "counter sink emboss.sldftp"):
        for sub in ("forming tools\\embosses", "forming tools", ""):
            p = LIB / sub / name if sub else LIB / name
            if p.is_file():
                return p
    hits = sorted(LIB.rglob("*.sldftp")) if LIB.is_dir() else []
    return hits[0] if hits else None


def _feature_names(model):
    """★ 取特征树里的名字 —— ★ 直接走模块自己的 `iter_features_recursive`（★ 不绕弯 ✓）。"""
    import sw_connect
    import sw_weldment as W
    return [str(sw_connect.get_com_member(f, "Name") or "") for f in W.iter_features_recursive(model)]


def main() -> int:
    import sw_connect
    import sw_part
    import sw_selection_spec as SS
    import sw_sheet_metal as SM
    import sw_weldment as W

    out: dict = {"purpose": "★ 验 B2 缝进 scripts/ 的两个模块函数（★ 走模块、不走探针实现）",
                 "cases": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    WORK.mkdir(parents=True, exist_ok=True)

    #: ══════════ ① 焊接符号：★ 走 `sw_weldment.insert_weld_symbol_report` ══════════
    row1: dict = {"case": "weld_symbol（走模块函数）"}
    try:
        model = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 60.0, 40.0)
        sk = sw_part.current_sketch_name(model)
        sw_part.end_sketch(model)
        sw_part.extrude_boss(model, sk, 20.0)                     #: ★ 有实体才有面可选 ✓
        row1["features_before"] = _feature_names(model)

        #: ★★ **只调模块函数**（★ 按它自己的契约：`(model, *, face_index=…)` ✓）
        res = W.insert_weld_symbol_report(model, face_index=0, symbol="BUTT")
        row1["result"] = {k: (v if isinstance(v, (int, bool, str, list, dict)) else str(v)[:60])
                          for k, v in res.items()}
        #: ★ 判据：★ **回读**（★ `GetLineCount > 0` ✓）
        rb = res.get("readback") or {}
        row1["ok"] = bool(isinstance(rb.get("GetLineCount"), int) and rb["GetLineCount"] > 0)
        row1["readback"] = rb
        print("★ ① 焊接符号 ⇒ ok=%r · 回读 %r" % (row1["ok"], rb))
    except Exception as e:                                          # noqa: BLE001
        row1["ok"] = False
        row1["exception"] = "%s: %s" % (type(e).__name__, str(e)[:180])
        print("★ ① 焊接符号 ⇒ 抛 %s" % row1["exception"])
    out["cases"].append(row1)

    #: ══════════ ② 成形工具：★ 走 `sw_sheet_metal.insert_form_tool_report` ══════════
    row2: dict = {"case": "forming_tool（走模块函数）"}
    tool = _find_tool()
    row2["tool_path"] = str(tool) if tool else None
    try:
        if tool is None:
            row2["ok"] = False
            row2["error"] = "★ 前置：Design Library 里没有 *.sldftp ⇒ ★ 本项**判不了**（不是建不出来）"
        else:
            model2 = sw_connect.new_document(sw, "part")
            sw_part.start_sketch(model2, "Front Plane")
            sw_part.sketch_corner_rectangle(model2, 0.0, 0.0, 80.0, 60.0)
            sk2 = sw_part.current_sketch_name(model2)
            sw_part.end_sketch(model2)
            #: ★★ 契约逐字：`create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)
            #: ` ✗ ——
            #:   ★ 不是 `(model, sketch, thickness, …)`（★ 且它**不抛、只回 `None`** ✓）
            spec = SM.BaseFlangeSpec(thickness=float(sw_connect.mm(2.0)),
                                     bend_radius=float(sw_connect.mm(1.0)),
                                     depth=float(sw_connect.mm(40.0)))
            SM.create_base_flange(model2, sk2, spec)
            row2["features_after_flange"] = _feature_names(model2)

            res2 = SM.insert_form_tool_report(model2, str(tool), face_index=0)
            row2["result"] = {k: (v if isinstance(v, (int, bool, str, list, dict)) else str(v)[:60])
                              for k, v in res2.items()}
            #: ★ 判据：★ **特征树增量**（★ 回读 ✓）
            row2["ok"] = bool(res2.get("added"))
            row2["added"] = res2.get("added")
            print("★ ② 成形工具 ⇒ ok=%r · 新增 %r" % (row2["ok"], res2.get("added")))
    except Exception as e:                                          # noqa: BLE001
        row2["ok"] = False
        row2["exception"] = "%s: %s" % (type(e).__name__, str(e)[:180])
        print("★ ② 成形工具 ⇒ 抛 %s" % row2["exception"])
    out["cases"].append(row2)

    ok1, ok2 = bool(row1.get("ok")), bool(row2.get("ok"))
    out["module_functions_verified"] = {"weld_symbol": ok1, "forming_tool": ok2}
    out["verdict"] = (
        "★★★★★ **两个模块函数都在真机上成立** ✓ ⇒ ★★ 声明的 `verified` **在**模块这条路**上复现了** ✓"
        if (ok1 and ok2) else
        "★★ **未全过**（weld_symbol=%r · forming_tool=%r）⇒ ★ **如实记、★ 不许把 `stitched` 写成 `verified`** ✓"
        % (ok1, ok2))
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec213-b2-modules.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec213-b2-modules-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)

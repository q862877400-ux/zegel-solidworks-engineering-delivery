"""★ 探针：`InsertFormToolFeature` —— ★ 成形工具（★ 前置链**全在本机**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B7 成形工具的真机探针）
# 文件:   tools/probe_spec211_formtool.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「钣金 / 成形工具」。
# 官方依据（★ 三样逐字读过）：
#   · ★★ `C:\swapi\types\IFeatureManager\InsertFormToolFeature.md`
#     `Feature InsertFormToolFeature( System.string Path, System.bool Flip, System.double RotAngle,
#      System.string Config, System.bool OverrideDoc, System.bool ShowPunch, System.bool ShowProfile,
#      System.bool ShowCenter, System.bool LinkToPart )` ⇒ ★ **参数式 9 参** ✓
#     ★ `## Parameters` 逐字：★ `Path` = **Pathname of the forming tool part file in the Design Library**；
#       ★ `RotAngle` = Angle of the forming tool；★ `OverrideDoc` = True to override the document
#       settings in Tools > Options > Document Properties > **Sheet Metal**；
#       ★ `ShowPunch` / `ShowProfile` / `ShowCenter` **valid only if `OverrideDoc` = true** ✓
#   · ★ 另有属性式一代 `ILibraryFormToolFeatureData` —— ★★ **它带 `AccessSelections`** ✗
#     ⇒ ★ **那条路到不了建成**（**事实 47**）⇒ ★ 本探针**只走参数式** ✓
# 前置核实（★ 本批现场查的，★ 不是假设）：
#   ★★ 本机**有** Design Library 的成形工具文件 ✓：
#     `C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library\` 下的
#     `.sldftp`：`circular emboss` · `counter sink emboss` · `counter sink emboss2` · `dimple` ✓
#   ★ 另一个前置是**钣金件** ✓ —— ★ 本仓 `sw_sheet_metal.create_base_flange` **真机已验能建成** ✓
#     （★ 已知事实 34：★ 真建出「钣金6 / 基体-法兰1 / 平展型式6」✓）
# 判据:   ★★ 第一步只"查行为"（★ 与"扫描曲面"/"裁剪焊件"/"曲线驱动阵列"**同型** ✓）：
#     · ★ **建成**（★ 特征树 +1）⇒ ★ 大发现 ✓
#     · ★ **抛** ⇒ 记下（★ 形态被拒 ✓）
#     · ★ **静默回 `None` / 回对象而无特征** ⇒ ★★ **还不算试死**（★ 定则：「读到静默」≠「判定试死」✓）
#   ★★ 且按**新立的第 ④ 样**：★ 先把上面那些**枚举/路径**读完再动手 ✓
#   ★★ 前置逐条落布尔字段（★ 「读数无效」与「真的不建」长得一模一样 —— 已四次 ✓）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 本机实测存在的成形工具文件（★ 本批现场列过目录 ✓ —— ★ 挑最短名那个 ✓）
LIB = Path(r"C:\ProgramData\SolidWorks\SOLIDWORKS 2026\design library")


def _find_tool() -> tuple:
    """★ 从 Design Library 里挑一个**真实存在**的成形工具文件 ✓"""
    for name in ("circular emboss.sldftp", "dimple.sldftp",
                 "counter sink emboss.sldftp", "counter sink emboss2.sldftp"):
        for sub in ("forming tools", "forming tools\\embosses", ""):
            p = LIB / sub / name if sub else LIB / name
            if p.is_file():
                return p, "★ 直命中"
    hits = sorted(LIB.rglob("*.sldftp"))
    return (hits[0], "★ rglob 兜底") if hits else (None, "★ 一个都没有 ✗")


def _fnames(model):
    import sw_surface_features as SF
    return SF.feature_names(model)


def main() -> int:
    import sw_connect
    import sw_part

    out: dict = {"official": "IFeatureManager.InsertFormToolFeature",
                 "step": "第一步：查行为（★ 前置链全在本机 ✓）"}

    tool, how = _find_tool()
    out["tool_path"] = str(tool) if tool else None
    out["tool_found_how"] = how
    print("★ 成形工具文件 ⇒ %r（%s）" % (out["tool_path"], how))
    if tool is None:
        out["verdict"] = "★★ 前置缺：★ 本机 Design Library 里没有 `.sldftp` ✗"
        print(out["verdict"])
    else:
        sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
        if sw is None:
            print("★ 连不上")
            return 2
        model = sw_connect.new_document(sw, "part")
        if model is None:
            print("★ 建不了零件")
            return 2

        #: ★ 前置：★ **钣金件**（★ 仓里 `create_base_flange` 真机已验 ✓）
        import sw_sheet_metal as SM
        #: ★★★ 按**契约**调（★ AGENTS.md：「按 `ToolSpec` 的契约调，别手调内部实现」✓）——
        #:   ★ 签名是 `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ✗
        #:   ★★ 我第一版传 `(model, 80.0, 60.0, 2.0)` ⇒ **参数错** ⇒ 它**不抛**、回 `None` ✗
        #:     ⇒ ★ 前置没上、**读数无效** ✓（★ 而 `flange_created=False` 一眼看出来 —— 第四次救命 ✓）
        #:   ★ 契约逐字：`BaseFlangeSpec(thickness, bend_radius, depth, k_factor=0.42, …)` ✓
        before = _fnames(model)
        #: ★ 先画**基体法兰的轮廓草图**（★ 契约要 `sketch_ref` ✓）
        sw_part.start_sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, 0.0, 0.0, 80.0, 60.0)
        sk = sw_part.current_sketch_name(model)
        sw_part.end_sketch(model)
        flange = None
        try:
            spec = SM.BaseFlangeSpec(thickness=float(sw_connect.mm(2.0)),
                                     bend_radius=float(sw_connect.mm(1.0)),
                                     depth=float(sw_connect.mm(40.0)))
            flange = SM.create_base_flange(model, sk, spec)
        except Exception as e:                                          # noqa: BLE001
            out["flange_error"] = "%s: %s" % (type(e).__name__, str(e)[:130])
        after_flange = _fnames(model)
        out["flange_created"] = bool([n for n in after_flange if n not in before]) or bool(flange)
        out["features_after_flange"] = after_flange
        print("★ 钣金前置 ⇒ %r · 特征 %r → %r"
              % (out["flange_created"], len(before), len(after_flange)))

        #: ★ 调（★ 9 参逐位：★ Path · Flip · RotAngle · Config · OverrideDoc ·
        #:    ShowPunch · ShowProfile · ShowCenter · LinkToPart ✓）
        #: ★★★ 官方 `## Remarks` 逐字：「**Before calling this method, select either a face or a
        #:   2D sketch containing points**」✗ ⇒ ★ **前置 = 先选一个面** ✓
        #:   （★ 我第一版没选 ⇒ 回 None ⇒ ★ 那正是「前置没上」✓ —— ★ 判定文字也这么写的 ✓）
        import sw_selection_spec as SS
        face_ok = False
        face_err = None
        try:
            #: ★ 选索引 0 的面（★ `append` 默认 `False` ⇒ 正好清空后单选一面 ✓）
            SS.select_entity_by_index(model, "FACE", 0)
            face_ok = SS.get_selection_count(model) > 0
        except Exception as e:                                          # noqa: BLE001
            face_err = "%s: %s" % (type(e).__name__, str(e)[:120])
        out["face_selected"] = face_ok
        out["face_error"] = face_err
        out["selection_count"] = SS.get_selection_count(model)
        print("★ 前置：选面 ⇒ %r · 选区计数=%r" % (face_ok, out["selection_count"]))
        b2 = _fnames(model)
        exc = None
        feat = None
        try:
            feat = sw_connect.get_com_member(
                sw_connect.get_com_member(model, "FeatureManager"),
                "InsertFormToolFeature",
                str(tool), False, 0.0, "", False, False, False, False, False)
        except Exception as e:                                          # noqa: BLE001
            exc = e
        added = [n for n in _fnames(model) if n not in b2]
        out.update({"new_features": added, "returned_is_none": feat is None,
                    "returned_name": getattr(feat, "Name", None) if feat is not None else None,
                    "exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:150])})
        if added:
            out["verdict"] = "★★★★★ **建成**（★ 新增 %r）⇒ ★ 成形工具**走得通** ✓" % added
        elif exc is not None:
            out["verdict"] = "★★ **抛**：%s" % out["exception"]
        else:
            out["verdict"] = ("★★ **不建**（★ 回 %r）⇒ ★ **还不算试死** —— "
                              "★ 前置复核：★ 钣金件=%r · 工具文件=%r"
                              "（★ 定则：「读到静默」≠「判定试死」✓）"
                              % (out["returned_name"], out["flange_created"], bool(tool)))
        print("★★ 调用后 ⇒ 新增 %r · 回 %r" % (added, out["returned_name"]))
        print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b7-formtool.json"
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
        (ROOT / "output" / "spec211-b7-formtool-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)

"""★ 真机：建**结构系统**（Structure System）—— ★ 走事实 358 那条官方序列。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_structure_system.py
# 定位:   ★ 2026-10-03（轮 445）承**事实 358**（那条链的官方序列）与**事实 359**（判据的最后一块拼图）。
#   ★★★ **它要证明的**：★ 结构系统那条链**能不能建成** —— ★ 而它是
#     `configure_member_profile` / `configure_split_member` 那两条**从"不做"回到"该挂"**的依赖。
#   ★★ 官方序列（★ 逐句，★ 出自 `Access_Structure_System_Corner_Treatments_Example_VB.htm`）：
#     ```
#     ① modDocExt.SelectByID2("Line4@3DSketch1", "EXTSKETCHSEGMENT", 0,0,0, True, 0, Nothing, 0)
#        ★ 逐条 **Append = True**（★ 选区先行）
#     ② Set structMemDef = modDocExt.CreateStructureSystemMemberData(0)
#     ③ Set profDef = structMemDef.MemberProfile
#        profDef.ProfileStandard = "GB" · ProfileType = "round-rods" · ProfileSize = "ROUND BAR 23"
#     ④ Set PrimDef = structMemDef ; Set memPathSegDef = PrimDef
#        Set segments(0) = swSelMgr.GetSelectedObject6(1, 0) … ⇒ stat = memPathSegDef.SetPathSegments(segments)
#     ⑤ Set memData(0) = structMemDef ; memDataArray = memData
#     ⑥ modDocExt.CreateStructureSystem memDataArray, Nothing ⇒ **IStructureSystemFolder**
#     ```
# ★ 判据（★ 规则 6：★ 建/改特征后**回读**）：★ 特征树**有增量** · 且报出**新特征的类型名**。
#   ★★ 而**不拿 COM 返回值当判据**（★ 本仓一贯；★ 事实 8）。
# 官方依据: `IModelDocExtension.CreateStructureSystemMemberData`（1 参 ⇒ `IStructureSystemMemberFeatureData`）·
#   `IModelDocExtension.CreateStructureSystem`（2 参 ⇒ `IFeature`，实为 `IStructureSystemFolder`）·
#   `swStructureSystemMemberCreationType_Primary_PathSegment = 0` · 本机轮廓库 `GB\round-rods.sldlfp`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（★ 特征树增量 + 类型名）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "structure-system-evidence.json")

#: ★ 候选尺寸名（★ `sldlfp` 里的**配置名** —— ★ 试几个，★ 而把错误带回来）
SIZES = ["ROUND BAR 23", "Round Bar 23", "ROUND BAR 20", "23"]


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member, set_com_member

    ev: dict = {"trials": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        from scripts.sw_part import (_empty_callout, current_sketch_name, end_sketch,
                                     sketch_line, start_sketch)
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, -40.0, -20.0, 40.0, -20.0)
        sketch_line(doc, 40.0, -20.0, 40.0, 20.0)
        sk = current_sketch_name(doc, "Sketch1")
        end_sketch(doc)
        ev["sketch"] = sk

        #: ★ 特征树（★ 判据用）
        def tree() -> list:
            #: ★ ★★ `GetFeatureCount` 是**方法**（不是属性）——
            #:   ★ 真机第一版报 `TypeError: int() argument ... not 'method'`（★ 而那个报错**直接指出了真因**）。
            fm = get_com_member(doc, "FeatureManager")
            #: ★ 它要**一个参数**（`TopLevelOnly`）—— ★ 真机第二版报
            #:   `com_error(非选择性的参数)`（★ 而那正是**事实 33 同族**：参数不对时报的是这个）。
            n = int(get_com_member(fm, "GetFeatureCount", True) or 0)
            out = []
            for i in range(n):
                try:
                    f = get_com_member(fm, "GetFeatureByPosition", i)
                    out.append(str(get_com_member(f, "Name") or ""))
                except Exception:                              # noqa: BLE001
                    out.append("?")
            return out

        ext = get_com_member(doc, "Extension")
        sm = get_com_member(doc, "SelectionManager")
        before = tree()
        ev["tree_before"] = len(before)

        #: ① 按名字选两条线段（★ 事实 359 证实这条路读得到多实体）
        #: ★★ 先**清选区** —— 真机第一版 `selected_count` 是 **3**（★ 2 线段 + **基准面**）。
        try:
            doc.ClearSelection2(True)
        except Exception:                                  # noqa: BLE001
            pass
        stats = []
        for i in (1, 2):
            st = ext.SelectByID2("Line%d@%s" % (i, sk), "EXTSKETCHSEGMENT",
                                 0.0, 0.0, 0.0, True, 0, _empty_callout(), 0)
            stats.append(bool(st))
        ev["select_stats"] = stats
        ev["selected_count"] = int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)

        #: ② MemberData（★ 0 = Primary_PathSegment）
        mem = ext.CreateStructureSystemMemberData(0)
        ev["member_data_none"] = mem is None
        if mem is None:
            ev["verdict"] = "fail"
            ev["stage"] = "CreateStructureSystemMemberData"
        else:
            #: ③ 型材
            prof = get_com_member(mem, "MemberProfile")
            ev["profile_none"] = prof is None
            size_used = None
            if prof is not None:
                prof_names = []
                for cand in SIZES:
                    try:
                        set_com_member(prof, "ProfileStandard", "GB")
                        set_com_member(prof, "ProfileType", "round-rods")
                        set_com_member(prof, "ProfileSize", cand)
                        size_used = cand
                        break
                    except Exception as exc:                   # noqa: BLE001
                        prof_names.append("%s: %s" % (cand, str(exc)[:60]))
                ev["size_used"] = size_used
                ev["size_errors"] = prof_names
            #: ④ 线段组 ⇒ SetPathSegments
            segs = []
            for i in range(1, ev["selected_count"] + 1):
                o = get_com_member(sm, "GetSelectedObject6", i, 0)
                if o is not None:
                    segs.append(o)
            ev["segments_got"] = len(segs)
            set_ok = None
            if segs:
                try:
                    #: ★★★ 2026-10-03（轮 446）**换接口** ——
                    #:   ★ `SetPathSegments` **只在 `IPrimaryMemberPathSegmentFeatureData` 上**（★ 事实 360），
                    #:   ★★ 而我们手里只有 `IStructureSystemMemberFeatureData` ⇒ **必须 QueryInterface**
                    #:   ★ 而 IID 从**出厂程序集的 `[Guid]`** 取（★ `tools/typelib_iids.py`）。
                    try:
                        import sys as _s
                        _s.path.insert(0, str(REPO_ROOT / "tools"))
                        from typelib_iids import qi as _qi
                        prim = _qi(mem, "IPrimaryMemberPathSegmentFeatureData")
                        ev["qi_ok"] = prim is not None
                        set_ok = bool(get_com_member(prim, "SetPathSegments", segs))
                    except Exception as exc1:                  # noqa: BLE001
                        ev["qi_err"] = "%s: %s" % (type(exc1).__name__, str(exc1)[:120])
                        set_ok = "no-qi: %s" % str(exc1)[:80]
                except Exception as exc:                       # noqa: BLE001
                    set_ok = "%s: %s" % (type(exc).__name__, str(exc)[:120])
            ev["set_path_segments"] = set_ok
            #: ⑤⑥ 建
            try:
                arr = sw_connect.create_empty_dispatch_variant()   # ⚠ 先占位，下面替换
            except Exception:                                  # noqa: BLE001
                arr = None
            try:
                #: ★ 诊断：它到底在不在（★ `'NoneType' object is not callable` 指向"getattr 回了 None"）
                try:
                    _raw = getattr(ext, "CreateStructureSystem", "<没这个属性>")
                    ev["css_attr"] = type(_raw).__name__
                except Exception as _e:                    # noqa: BLE001
                    ev["css_attr"] = "err: %s" % str(_e)[:70]
                feat = get_com_member(ext, "CreateStructureSystem", [mem],
                                     sw_connect.create_empty_dispatch_variant())
                ev["feature_none"] = feat is None
                if feat is not None:
                    try:
                        ev["feature_type"] = str(get_com_member(feat, "GetTypeName2") or "")
                    except Exception:                          # noqa: BLE001
                        ev["feature_type"] = "?"
            except Exception as exc:                           # noqa: BLE001
                ev["create_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
            after = tree()
            new = [n for n in after if n not in before]
            ev["tree_after"] = len(after)
            ev["new_features"] = new
            ev["verdict"] = "pass" if new else "partial"
        ev["note"] = ("★ 走事实 358 的官方序列：选线段（EXTSKETCHSEGMENT）⇒ "
                      "CreateStructureSystemMemberData(0) ⇒ MemberProfile(GB/round-rods/…）⇒ "
                      "GetSelectedObject6 装 segments ⇒ SetPathSegments ⇒ CreateStructureSystem。"
                      "★ 判据：★ 特征树**有增量**（★ 不拿 COM 返回值当判据）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1600])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

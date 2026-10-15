"""★ 诊断探针：定位「SketchUseEdge3 返回 ok 但投影出 0 个实体」的真因。

★★ 本轮假设（按官方示例逐字比对得出，★ 不是猜）：
   官方示例（`Convert_Edges_and_Inner_Loops_..._Example_CSharp.md`）选的是 **FACE**：
       SelectByID2("", "FACE", x, y, z, false, 0, null, 0)
       swSketchManager.SketchUseEdge3(false, true)
   ★★ 而我们的探针选的是 **EDGE**（`IComponent2.GetBody().GetEdges()[0]`）——
   取的是**任意第一条边**，没有验证它是否**可投影**（例如它可能是装配体里不可见/
   被遮挡的边，或属于另一个方向）。

★★ 而且旧探针有一个**判据缺陷**：它的检查名写「选中一条外部边」，而判据是
   `Select4` 的**返回值** —— 本仓事实 8 明写「`Select4`/`SelectByID2` 的 bool
   不可信，必须回读 `GetSelectedObjectCount2(-1)`」⇒ **旧探针从来没回读过选区计数**。

★ 本探针把每一步都回读，并把「选区计数」「活动文档」「草图实体数」全部落盘。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/diag_in_context_projection.py
# 定位:   规格 315 的 ① 在位设计攻关 —— 诊断探针（只读+建临时件，不碰业主文件）
# 官方依据: ① C:\swapi\examples\Convert_Edges_and_Inner_Loops_of_Face_to_Sketch_Entities_Example_CSharp.md
#              （★ 官方示例给的是「调用序」：先开草图 → 再选面 → 再 SketchUseEdge3）
#           ② C:\swapi\types\ISketchManager\SketchUseEdge3.md（签名 2 参 + Remarks）
#           ③ 本仓事实 8（选择返回值不可信，回读计数）
#           ④ 本仓事实 32（边/面没有名字，按对象选或按点选）
#           ⑤ 本仓事实 102（旧诊断：四个可能已排除，真因未查明）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")]

DIR = ROOT / "output" / "diag-in-context-projection"
EV: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": []}


def step(name: str, **kw) -> None:
    EV["steps"].append({"step": name, **kw})
    print("   %-52s %s" % (name, json.dumps(kw, ensure_ascii=False)[:120]))


def main() -> int:
    import sw_connect
    from scripts import sw_part, sw_assembly, sw_assembly_doc, sw_sketch_edit

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    DIR.mkdir(parents=True, exist_ok=True)
    docs: list = []

    def sel_count(doc=None) -> int:
        """★ 事实 8：回读选区计数，不信返回值。

        ⚠ `SelectionManager` 在**文档**上（`IModelDoc2.SelectionManager`），
        ★ 不在 `ISldWorks` 上（本仓 `sw_assembly_doc.py` 就是这么取的）。
        """
        d = doc or sw_connect.safe_get_com_member(sw, "ActiveDoc")
        if d is None:
            return 0
        mgr = sw_connect.safe_get_com_member(d, "SelectionManager")
        return int(sw_connect.safe_get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)

    def seg_count(doc) -> object:
        """★ 活动草图的线段数（三态：取不到回 None）。"""
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        if sk is None:
            return None
        try:
            from scripts import sw_sketch
            return len(sw_sketch.get_sketch_segments(sk) or [])
        except Exception:      # noqa: BLE001
            return None

    try:
        #: ══ ① 两个零件（★ 复刻业主场景：板 + 导轨）══════════════
        paths = []
        for name, (w, h, d) in (("plate", (200.0, 150.0, 10.0)),
                                ("rail", (30.0, 30.0, 120.0))):
            doc = sw_connect.new_document(sw, "part")
            docs.append(doc)
            sw_part.start_sketch(doc)
            sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, w, h)
            sw_part.end_sketch(doc)
            sw_part.extrude_boss(doc, "草图1", d)
            p = DIR / ("%s.sldprt" % name)
            sw_connect.save_document(doc, str(p))
            paths.append(str(p))
        step("① 造 2 个零件（板 200×150×10 / 导轨 30×30×120）", n=len(paths))

        #: ══ ② 装配 ═══════════════════════════════════════════
        asm = sw_connect.new_document(sw, "assembly")
        docs.append(asm)
        c0 = sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        c1 = sw_assembly.add_component(asm, paths[1], x=60, y=40, z=10)
        comps = [c for c in (c0, c1) if c is not None]
        step("② 装配 2 个组件", comps=len(comps))
        if len(comps) < 2:
            raise RuntimeError("组件不够")

        #: ══ ③ 进入在位编辑 ═══════════════════════════════════
        code = sw_assembly_doc.edit_part_in_context(asm, comps[0])
        tgt = sw_connect.safe_get_com_member(asm, "GetEditTarget")
        active = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        step("③ 进入在位编辑", EditPart2=code, edit_target="非空" if tgt else "空",
             active_is_asm=(active is asm))
        tgt_doc = active or asm

        #: ══ ④ 开草图（★ 官方序第 2 步）═══════════════════════
        sw_part.start_sketch(tgt_doc)
        step("④ 开草图", segments=seg_count(tgt_doc), selection=sel_count())

        #: ══ ⑤ 取「导轨」那条边（★ 外部边）═══════════════════
        b2 = sw_connect.safe_get_com_member(comps[1], "GetBody")
        eds = list(sw_connect.safe_get_com_member(b2, "GetEdges") or [])
        step("⑤ 导轨的边", edge_count=len(eds))

        #: ══ ⑥ 变体 A：按对象选边 + 回读计数 ═══════════════════
        cand = eds[0] if eds else None
        ret_a = bool(cand.Select4(False, sw_part._empty_callout())) if cand is not None else None
        step("⑥A 按对象选边（Select4）", returned=ret_a, selection=sel_count())

        #: ══ ⑦ 变体 A：投影 ═══════════════════════════════════
        before = seg_count(tgt_doc)
        try:
            r = sw_sketch_edit.convert_entities(tgt_doc)
            step("⑦A convert_entities", ok=r.get("ok"), before=r.get("segments_before"),
                 after=r.get("segments_after"), delta=r.get("new_segments"))
        except Exception as exc:      # noqa: BLE001
            step("⑦A convert_entities 抛", err="%s: %s" % (type(exc).__name__, str(exc)[:110]))
        step("⑦A 投影后", segments=seg_count(tgt_doc))

        #: ══ ⑧ 变体 B：按「面上的点」选面（★ 官方示例的做法）═══
        sw_part.end_sketch(tgt_doc)
        sw_part.start_sketch(tgt_doc)
        step("⑧ 重开草图（清选择）", segments=seg_count(tgt_doc), selection=sel_count())
        #: ★ 官方示例：SelectByID2("", "FACE", x, y, z, false, 0, null, 0)
        #:   取导轨**顶面**上一点（导轨在 x=60,y=40,z=10，截面 30×30 ⇒ 中心 75,55）
        ext = sw_connect.safe_get_com_member(tgt_doc, "Extension")
        ret_b = None
        for (px, py, pz) in ((0.075, 0.055, 0.13), (0.075, 0.055, 0.01),
                             (0.06, 0.04, 0.13), (0.09, 0.07, 0.13)):
            try:
                ret_b = bool(ext.SelectByID2("", "FACE", px, py, pz, False, 0,
                                             sw_part._empty_callout(), 0))
            except Exception:      # noqa: BLE001
                ret_b = None
            if sel_count() > 0:
                step("⑧B 按点选面（命中）", xyz=(px, py, pz), returned=ret_b,
                     selection=sel_count())
                break
            step("⑧B 按点选面（未命中）", xyz=(px, py, pz), returned=ret_b,
                 selection=sel_count())

        if sel_count() > 0:
            before = seg_count(tgt_doc)
            try:
                r = sw_sketch_edit.convert_entities(tgt_doc)
                step("⑨B convert_entities（选面）", ok=r.get("ok"),
                     before=r.get("segments_before"), after=r.get("segments_after"),
                     delta=r.get("new_segments"))
            except Exception as exc:      # noqa: BLE001
                step("⑨B convert_entities 抛",
                     err="%s: %s" % (type(exc).__name__, str(exc)[:110]))
            step("⑨B 投影后", segments=seg_count(tgt_doc))

        sw_part.end_sketch(tgt_doc)
        sw_assembly_doc.exit_edit_part_in_context(asm)
        step("⑩ 退出在位编辑", ok=True)

        EV["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out = DIR / "diag.json"
        out.write_text(json.dumps(EV, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\n★ 证据 → %s" % out)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in reversed(docs):
            try:
                sw_connect.close_document(sw, d, save=False)
            except Exception:      # noqa: BLE001
                pass


if __name__ == "__main__":
    raise SystemExit(main())

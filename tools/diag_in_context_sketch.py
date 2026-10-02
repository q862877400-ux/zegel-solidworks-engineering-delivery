r"""@brief 诊断：`convert_entities` 之后**到底哪个草图里有几个实体** —— 换读数法，不再改写法。

## 背景（轮 162）
`verify_in_context_reference_smoke.py` 一直报「投影后草图实体数 = 0」，
而 `convert_entities` **不抛异常**。⚠ 已在这一行上换了 5 次写法 ⇒ **按事实 53 停手**，
先做**读数诊断**：是**投影真的没成**，还是**我读错了对象**。

## 本诊断要分别回答
```
① 进入在上下文编辑**前后**，`sw.ActiveDoc` 分别是谁
② `SketchManager.ActiveSketch` 的名字（进入草图后）
③ 用**三种**读数法数那个草图里的实体：仓库助手 / 直接 COM / `GetSketchSegments2`
④ `convert_entities` 前后各数一次
```

## ⚠ 安全
scratch 存到 `output/` 的每轮子目录；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机诊断）
# 文件:   tools/diag_in_context_sketch.py
# 定位:   给 Spec Kit `082` 定位「投影后实体数为 0」是**投影没成**还是**读数对象错**。
# 官方依据: `ISketchManager.SketchUseEdge3` · `ISketch.GetSketchSegments` · `IModelDoc2.GetActiveSketch2`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\diag-in-context-sketch.json")
DIR = Path(r"D:\AI\SW\output\diag-in-context") / time.strftime("%H%M%S")
def segs_of(sketch, sw_connect, sw_sketch) -> dict:
    out = {}
    try:
        s = sw_sketch.get_sketch_segments(sketch)
        out["repo_helper"] = len(s) if isinstance(s, list) else -1
    except Exception as exc:      # noqa: BLE001
        out["repo_helper"] = "EXC:%s" % str(exc)[:40]
    try:
        s = sw_connect.safe_get_com_member(sketch, "GetSketchSegments")
        out["direct"] = len(list(s)) if s else 0
    except Exception as exc:      # noqa: BLE001
        out["direct"] = "EXC:%s" % str(exc)[:40]
    try:
        s = sw_connect.safe_get_com_member(sketch, "GetSketchSegments2")
        out["direct2"] = len(list(s)) if s else 0
    except Exception as exc:      # noqa: BLE001
        out["direct2"] = "EXC:%s" % str(exc)[:40]
    return out


def main() -> int:
    ev: dict = {"steps": []}
    sw = None
    docs: list = []
    try:
        import sw_connect
        from scripts import sw_part, sw_assembly, sw_assembly_doc, sw_sketch, sw_sketch_edit
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        DIR.mkdir(parents=True, exist_ok=True)
        paths = []
        for name, (w, h, d) in (("plate", (100.0, 60.0, 10.0)), ("rail", (40.0, 40.0, 200.0))):
            doc = sw_connect.new_document(sw, "part")
            docs.append(doc)
            sw_part.start_sketch(doc)
            sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, w, h)
            sw_part.end_sketch(doc)
            sw_part.extrude_boss(doc, "草图1", d)
            p = DIR / ("%s.sldprt" % name)
            sw_connect.save_document(doc, str(p))
            paths.append(str(p))
        asm = sw_connect.new_document(sw, "assembly")
        docs.append(asm)
        c0 = sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        c1 = sw_assembly.add_component(asm, paths[1], x=140, y=0, z=0)

        #: ① 进入前后分别看活动文档
        before = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        code = sw_assembly_doc.edit_part_in_context(asm, c0)
        after = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        ev["edit_code"] = code
        ev["active_before_is_asm"] = (before is asm)
        ev["active_after_is_asm"] = (after is asm)
        print("  ① `EditPart2` 码=%r · 活动文档 前=asm?%s 后=asm?%s"
              % (code, ev["active_before_is_asm"], ev["active_after_is_asm"]))
        tgt = after or asm

        #: ② 开草图 + 读名字
        sw_part.start_sketch(tgt)
        skm = sw_connect.safe_get_com_member(tgt, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        try:
            nm = str(sw_connect.safe_get_com_member(sk, "Name") or "?")
        except Exception:      # noqa: BLE001
            nm = "EXC"
        print("  ② ActiveSketch = %s" % ("有" if sk is not None else "**没有**"))
        ev["active_sketch"] = sk is not None
        ev["sketch_name"] = nm

        #: ③ 先数一次（应当 0）
        ev["before_convert"] = segs_of(sk, sw_connect, sw_sketch) if sk is not None else {}
        print("  ③ 投影**前**读数: %s" % ev["before_convert"])

        #: 选边（此刻选才作数）
        sel_ok = False
        try:
            b = sw_connect.safe_get_com_member(c1, "GetBody")
            eds = sw_connect.safe_get_com_member(b, "GetEdges")
            eds = list(eds) if eds else []
            ev["edge_count"] = len(eds)
            if eds:
                sel_ok = bool(eds[0].Select4(False, sw_part._empty_callout()))
        except Exception as exc:      # noqa: BLE001
            print("     ⚠ 选边异常: %s" % str(exc)[:80])
        try:
            cnt = int(sw_connect.safe_get_com_member(
                sw_connect.safe_get_com_member(tgt, "SelectionManager"),
                "GetSelectedObjectCount2", -1) or 0)
        except Exception:      # noqa: BLE001
            cnt = -1
        ev["selected_count"] = cnt
        print("  ④ 选边返回=%s · **回读选择集计数=%d**（事实 94：不许只信返回值）" % (sel_ok, cnt))

        #: ⑤ 投影 + 再数
        try:
            sw_sketch_edit.convert_entities(tgt)
            print("  ⑤ `convert_entities` 未抛异常")
        except Exception as exc:      # noqa: BLE001
            print("  ⑤ `convert_entities` 抛错: %s" % str(exc)[:100])
        ev["after_convert"] = segs_of(sk, sw_connect, sw_sketch) if sk is not None else {}
        print("  ⑥ 投影**后**读数（三种读法对照）: %s" % ev["after_convert"])
        #: 也看看**重取**的活动草图
        sk2 = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        ev["same_sketch"] = (sk2 is sk)
        if sk2 is not None and sk2 is not sk:
            ev["after_convert_resketch"] = segs_of(sk2, sw_connect, sw_sketch)
            print("      （重取的活动草图读数: %s）" % ev["after_convert_resketch"])
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 诊断出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        for d in docs:
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:      # noqa: BLE001
                pass

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print("  收尾：扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

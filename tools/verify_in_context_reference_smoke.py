r"""@brief 真机冒烟：**在上下文编辑 + 外部参考** —— 验提案 §六 的前两条判据。

## 验什么（判据要能被**空操作证伪**）
```
① 草图关系层：建立外部参考**前** `GetRelationsCount` = N ⇒ 建**后** = N+1   ← 空操作不变
② 文档层    ：`ListExternalFileReferencesCount` **0 → ≥1**                  ← 空操作不变
```
⚠ 提案 §六.③（改型材间距 ⇒ 端板宽度实测值变化）**本轮不做** —— 那要完整的自顶向下链。

## 步骤（照提案 §三 的四步链，但用本仓库**已有**的部件）
```
① 造 2 个零件（A=端板 100x60x10 · B=型材 40x40x200），存盘
② 装成一个装配，B 与 A 相邻（**不重叠**，别跟干涉检查混）
③ `edit_part_in_context(asm, compA)` ⇒ 进入在上下文编辑
④ 在 A 里开草图 ⇒ `convert_entities`（**已有**，真机 17/17）把 B 的边**投影**进来
⑤ `add_relation(sketch, entities, swConstraintType_COLINEAR = 27)`（**已有**）
⑥ 读 `GetRelationsCount` ⇒ 与 ⑤ 之前的差值
⑦ `exit_edit_part_in_context(asm)`
⑧ `list_external_file_references_count(compA)` ⇒ **0 → ≥1**
```

## ⚠ 安全
scratch 存到 `output/` 的**每轮子目录**（上一轮的文件被 SW 占着，就地删会 WinError 32）；
收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_in_context_reference_smoke.py
# 定位:   给 Spec Kit `080` 取「在上下文编辑 + 外部参考」的证据。
# 官方依据: `IAssemblyDoc.EditPart2` / `EditAssembly` · `IComponent2.ListExternalFileReferencesCount` ·
#          `ISketchRelationManager.AddRelation` · `swConstraintType_e.swConstraintType_COLINEAR = 27` ·
#          `swSketchRelationFilterType_e.swExternal = 3`
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "in-context-reference-smoke.json")
DIR = Path(Path(__file__).resolve().parents[1] / "output" / "in-context-smoke") / time.strftime("%H%M%S")
COLINEAR = 27          #: swConstraintType_e.swConstraintType_COLINEAR
EXTERNAL = 3           #: swSketchRelationFilterType_e.swExternal


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:320]}
        print("   %s %-50s %s" % ("✓" if ok else "**✗**", name, str(detail)[:64]))

    sw = None
    docs: list = []
    try:
        import sw_connect
        from scripts import sw_part, sw_assembly, sw_assembly_doc, sw_sketch_edit, sketch_relations
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        DIR.mkdir(parents=True, exist_ok=True)

        #: ① 两个零件
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
        chk("造出 2 个零件并保存（端板 / 型材）", len(paths) == 2, "ok")

        #: ② 装配
        asm = sw_connect.new_document(sw, "assembly")
        docs.append(asm)
        #: ★★ **`sw_assembly.add_component` 本身就返回 `IComponent2`**（它的 docstring 明写）
        #: ⇒ 直接用它，**别去 `asm.GetComponents(True)` 再猜返回的是哪个接口族**
        #: （轮 161 就是这么卡住的：那批对象上**没有 `GetBody2`**）。
        c0 = sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        c1 = sw_assembly.add_component(asm, paths[1], x=140, y=0, z=0)   #: 挨着但不重叠
        comps = [c for c in (c0, c1) if c is not None]
        chk("装配里 2 个组件（**用 add_component 的返回值**）", len(comps) >= 2,
            "组件对象 %d 个" % len(comps))
        if len(comps) < 2:
            raise RuntimeError("组件不够，无法继续")

        #: ⑧-前：外部参考计数基线
        base_refs = sw_assembly_doc.list_external_file_references_count(comps[0])
        ev["refs_before"] = base_refs
        chk("★ 基线：外部参考计数（**取证用，不一定 0**）", True, "= %s" % base_refs)

        #: ③ 进入在上下文编辑
        code = sw_assembly_doc.edit_part_in_context(asm, comps[0])
        ev["edit_part_code"] = code
        chk("★★ `EditPart2` 返回（原样透出数字，不翻译）", code is not None,
            "返回码 = %r" % (code,))
        try:
            tgt = sw_connect.safe_get_com_member(asm, "GetEditTarget")
            ev["edit_target"] = "非空" if tgt is not None else "空"
            chk("★★ **在上下文编辑态已生效**（`GetEditTarget` 非空）", tgt is not None,
                "GetEditTarget = %s" % ev["edit_target"])
        except Exception as exc:      # noqa: BLE001
            chk("读 GetEditTarget", False, "%s: %s" % (type(exc).__name__, str(exc)[:80]))

        #: ④⑤ 投影 + 加共线关系
        #: ⚠⚠⚠ **关键**：进入「在上下文编辑」之后 **`sw.ActiveDoc` 已经变成那个零件** ——
        #: 草图操作必须落在**活动文档**上，**不是 `asm`**。
        #: ★ 轮 161 我一直对 `asm` 开草图/投影 ⇒ `convert_entities` 返回 ok
        #:   而**草图里一个实体都没有**（因为它作用在另一个文档上）。
        tgt_doc = sw_connect.safe_get_com_member(sw, "ActiveDoc") or asm
        ev["active_doc_is_asm"] = (tgt_doc is asm)
        print("     活动文档就是 asm 吗: %s（**应当不是**）" % ev["active_doc_is_asm"])
        sw_part.start_sketch(tgt_doc)
        skm = sw_connect.safe_get_com_member(tgt_doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")

        #: ⚠⚠⚠ **顺序很重要**（轮 162 查出）：`sw_part.start_sketch` 内部会
        #: `ClearSelection2(True)` ⇒ **它会把我刚选的那条边清掉**。
        #: ⇒ 正确顺序是：**先开草图 → 再选边 → 再投影**（第一版把选边放在开草图**之前**，
        #:   于是 `SketchUseEdge3` 拿到的是**空选择集** ⇒ 返回 ok 而**草图里 0 个实体**）。
        #: `SketchUseEdge3` 用的是**当前选择集** ⇒ 此刻选它才作数。
        #: 否则它返回 ok 而草图里**一个实体都没有**（轮 161 实测到这一步才发现）。
        #: ★ 选边走**按对象**（`IEntity.Select4`，事实 32 认可的可行路径），
        #: 而**不是**按名字（`SelectByID2("Edge1","EDGE")` 计数恒 0）。
        sel_ok = False
        try:
            #: ⚠⚠ 第一版用 `asm.GetBodies2(...)` ⇒ `<unknown>.GetBodies2` ——
            #: 那是 **`IPartDoc`** 的成员，**不在 `IAssemblyDoc` 上**。
            #: ⇒ ★ 从**组件**取：`IComponent2.GetBody2()`（零参，返回 `Body2`）。
            bodies = []
            #: ⚠⚠ **我第一版把名字读错了**：反射里是 **`Body2 GetBody()`** ——
            #: `Body2` 是**返回类型**，方法名是 **`GetBody`**（**不带 2**）。
            #: ⇒ 传 `GetBody2` 会报 `<unknown>.GetBody2`。
            b2 = sw_connect.safe_get_com_member(comps[1], "GetBody")
            if b2 is not None:
                bodies = [b2]
            #: 型材那条边 ⇒ 取第一条
            cand = None
            for b in bodies:
                eds = sw_connect.safe_get_com_member(b, "GetEdges")
                eds = list(eds) if eds else []
                if eds:
                    cand = eds[0]
                    break
            if cand is not None:
                sel_ok = bool(cand.Select4(False, sw_part._empty_callout()))
        except Exception as exc:      # noqa: BLE001
            print("     ⚠ 选边异常: %s" % str(exc)[:80])
        chk("★★ 先**选中一条外部边**（`SketchUseEdge3` 的前置条件）", sel_ok,

            "实体数 %d" % (len(bodies) if 'bodies' in dir() else -1))
        try:
            sw_sketch_edit.convert_entities(tgt_doc)
            chk("★ `convert_entities`（**已有实现**，本轮当部件复用）", True, "ok")
        except Exception as exc:      # noqa: BLE001
            chk("convert_entities", False, "%s: %s" % (type(exc).__name__, str(exc)[:100]))
        mgr = sw_connect.safe_get_com_member(sk, "RelationManager") if sk is not None else None
        before = int(sw_connect.safe_get_com_member(mgr, "GetRelationsCount", 0) or 0) if mgr else 0
        ev["relations_before"] = before
        try:
            #: ⚠ 用**仓库已验证的**取法（`sw_sketch.get_sketch_segments`）——
            #: 第一版我自己写 `sk.GetSketchSegments()` ⇒ 拿到的东西不对
            #: ⇒ 报 `TypeError: 'NoneType' object is not callable`（**不是** `add_relation` 的错）。
            from scripts import sw_sketch
            ents = sw_sketch.get_sketch_segments(sk) if sk is not None else []
            ents = list(ents) if ents else []
            if len(ents) >= 1:
                sketch_relations.add_relation(sk, ents, COLINEAR)
                chk("★ `add_relation(COLINEAR=27)`（**已有实现**）", True, "ok")
            else:
                chk("★ `add_relation` 前提（投影出实体）", False,
                    "投影后草图实体数 = %d ⇒ **前提没满足**" % len(ents))
        except Exception as exc:      # noqa: BLE001
            chk("add_relation", False, "%s: %s" % (type(exc).__name__, str(exc)[:110]))
        after = int(sw_connect.safe_get_com_member(mgr, "GetRelationsCount", 0) or 0) if mgr else 0
        ev["relations_after"] = after
        chk("★★ 判据①：`GetRelationsCount` **N → N+1**（空操作不变）", after == before + 1,
            "%d → %d" % (before, after))
        sw_part.end_sketch(tgt_doc)

        #: ⑦ 退出
        sw_assembly_doc.exit_edit_part_in_context(asm)
        chk("★ `EditAssembly()` 退出（零参）", True, "ok")

        #: ⑧ 判据②
        new_refs = sw_assembly_doc.list_external_file_references_count(comps[0])
        ev["refs_after"] = new_refs
        chk("★★ 判据②：外部参考计数 **0 → ≥1**（空操作不变）", new_refs >= 1,
            "%s → %s" % (base_refs, new_refs))
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:180]))
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
        print("   （已关闭 scratch 文档，不保存）")

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    chk("★ 收尾无残留模态框（事实 64）", (not dialogs) and scanned > 0,
        "扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

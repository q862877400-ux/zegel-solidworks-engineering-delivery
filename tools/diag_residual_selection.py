"""★ 诊断探针 2：查「开草图后 selection=1」那个残留选择是什么。

★★ 上一轮发现（`output/diag-in-context-projection/diag.json`）：
   ④ 开草图 ⇒ selection = **1**（★ 而我还没选任何东西）
   ⑧ 重开草图（我以为清掉了）⇒ selection 仍 = **1**
   ⇒ ★★ **`sw_part.start_sketch` 内部清选择之后，仍有 1 个残留** ⇒
       `SketchUseEdge3` 拿到的是**这个残留**，不是我要投影的边。

★ 本探针把「那 1 个残留到底是什么」读出来（类型 + 名字 + 所属文档）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/diag_residual_selection.py
# 定位:   规格 315 的 ① 在位设计攻关 —— 查残留选择
# 官方依据: ① 本仓事实 8（选择返回值不可信，回读计数）
#           ② ISelectionMgr.GetSelectedObject6(Index, Mark) / GetSelectedObjectType3
#           ③ C:\swapi\types\ISelectionMgr\GetSelectedObjectCount2.md（Mark 语义）
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

DIR = ROOT / "output" / "diag-residual-selection"
EV: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "steps": []}


def step(name: str, **kw) -> None:
    EV["steps"].append({"step": name, **kw})
    print("   %-46s %s" % (name, json.dumps(kw, ensure_ascii=False)[:130]))


def main() -> int:
    import sw_connect
    from scripts import sw_part, sw_assembly, sw_assembly_doc

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:      # noqa: BLE001
        pass
    DIR.mkdir(parents=True, exist_ok=True)
    docs: list = []

    def dump_sel(tag: str) -> list:
        """★ 把当前选区逐项读出来（类型 + 名字 + 文档）。"""
        d = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        mgr = sw_connect.safe_get_com_member(d, "SelectionManager")
        n = int(sw_connect.safe_get_com_member(mgr, "GetSelectedObjectCount2", -1) or 0)
        out = []
        for i in range(1, n + 1):
            item = {"index": i}
            for k in (-1, 0):
                c = sw_connect.safe_get_com_member(mgr, "GetSelectedObjectCount2", k)
                item["mark%d" % k] = c
            t = sw_connect.safe_get_com_member(mgr, "GetSelectedObjectType3", i, -1)
            item["type"] = t
            o = sw_connect.safe_get_com_member(mgr, "GetSelectedObject6", i, -1)
            item["obj"] = type(o).__name__ if o is not None else None
            for meth in ("GetTypeName2", "Name", "GetPathName"):
                try:
                    v = getattr(o, meth)
                    v = v() if callable(v) else v
                    item[meth] = str(v)[:70]
                except Exception:      # noqa: BLE001
                    pass
            out.append(item)
        step("选区 @%s" % tag, count=n, items=out)
        return out

    try:
        #: 两件
        paths = []
        for name, (w, h, dd) in (("plate", (200.0, 150.0, 10.0)),
                                 ("rail", (30.0, 30.0, 120.0))):
            doc = sw_connect.new_document(sw, "part")
            docs.append(doc)
            sw_part.start_sketch(doc)
            sw_part.sketch_corner_rectangle(doc, 0.0, 0.0, w, h)
            sw_part.end_sketch(doc)
            sw_part.extrude_boss(doc, "草图1", dd)
            p = DIR / ("%s.sldprt" % name)
            sw_connect.save_document(doc, str(p))
            paths.append(str(p))
        step("① 造 2 件", n=len(paths))

        asm = sw_connect.new_document(sw, "assembly")
        docs.append(asm)
        c0 = sw_assembly.add_component(asm, paths[0], x=0, y=0, z=0)
        c1 = sw_assembly.add_component(asm, paths[1], x=60, y=40, z=10)
        step("② 装配", comps=len([c for c in (c0, c1) if c]))

        dump_sel("装配态·未做任何事")

        code = sw_assembly_doc.edit_part_in_context(asm, c0)
        step("③ 进入在位编辑", EditPart2=code)
        dump_sel("进入在位编辑后")

        tgt = sw_connect.safe_get_com_member(sw, "ActiveDoc")
        sw_part.start_sketch(tgt)
        dump_sel("★ 开草图后（★ 关键：这 1 个是什么）")

        #: ★ 手动清一次，再看
        try:
            tgt.ClearSelection2(True)
        except Exception as e:      # noqa: BLE001
            step("ClearSelection2 异常", err=str(e)[:80])
        dump_sel("★ 手动 ClearSelection2 之后")

        #: ★ 现在选边
        b2 = sw_connect.safe_get_com_member(c1, "GetBody")
        eds = list(sw_connect.safe_get_com_member(b2, "GetEdges") or [])
        cand = eds[0] if eds else None
        ret = bool(cand.Select4(False, sw_part._empty_callout())) if cand is not None else None
        step("④ 选导轨第一条边", returned=ret)
        dump_sel("★ 选边之后")

        EV["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
        out = DIR / "residual.json"
        out.write_text(json.dumps(EV, ensure_ascii=False, indent=1), encoding="utf-8")
        print("\n★ 证据 → %s" % out)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        #: ★★ 收尾必须**真的关掉自己建的文档** ——
        #: ⚠ `GetTitle` / `GetPathName` 是**方法**（不是属性）⇒
        #:   `safe_get_com_member` 拿到的是 **bound method**，
        #:   直接喂给 `CloseDoc` 会**静默失败**（被 except 吞掉）⇒ 文档留在会话里
        #:   ⇒ 下一轮护栏预检会拒绝开始（★ 实测踩过：护栏报「3 个不是我们打开的文档」）。
        #:   ⇒ ★ 取名字必须**调用**那个方法。
        for d in reversed(docs):
            try:
                t = sw_connect.safe_get_com_member(d, "GetTitle")
                if callable(t):
                    t = t()
                if t:
                    sw.CloseDoc(str(t))
            except Exception:      # noqa: BLE001
                pass


if __name__ == "__main__":
    raise SystemExit(main())

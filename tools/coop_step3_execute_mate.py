"""人工验收 · 第 3 步「执行」：在两块板之间建**重合配合**。

## 前置

必须先跑 `tools/coop_step2_prepare_mate.py` 并由业主**确认初始状态**。
本脚本假定 SolidWorks 里打开的正是那个场景（两块板，X 差 30mm、Z 差 50mm）。

## 做什么

① 射线选面（各取一块**独占**的 x，事实 571）：
   - 组件1 顶面：x=−40mm，从 z=70mm 自上而下
   - 组件2 底面：x=+70mm，从 z=40mm 自下而上
② 核**两个面确实分属不同组件**（`GetSelectedObjectsComponent4`）—— 不核就是假前提
③ `CreateMateData(swMateCOINCIDENT=0)` → `EntitiesToMate`（VARIANT 对象数组，事实 566）
   → `MateAlignment=2` → `CreateMate`
④ 数**真实配合特征**（类型以 Mate 开头且不是 MateGroup）
⑤ 存盘 → 截图 → 把文档**保持打开**给业主看结果

## 输出（给业主对照）

执行前后的**平移读数**（配合应当把组件2 拉下来：z 从 60 → 30 附近）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（人工验收 · 第 3 步「执行」）
# 文件:   tools/coop_step3_execute_mate.py
# 定位:   在第 2 步摆好的场景上建重合配合，并把执行前后的平移读数打出来给业主对照。
#          起因：业主 2026-10-26 要求「机器判据 + 人工确认」两关都过，见
#          docs/human-acceptance-protocol.md 阶段 3/4。
# 官方依据: IModelDocExtension::SelectByRay ·
#          ISelectionMgr::GetSelectedObjectsComponent4 ·
#          IAssemblyDoc::CreateMateData / CreateMate · IMate2 ·
#          IModelDoc2::EditRebuild3 ·
#          IModelDocExtension::SaveAs（6 参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "coop" / "配合演示_结果.SLDASM"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def _translations(doc) -> list:
    out = []
    for cp in list(get_com_member(doc, "GetComponents", False) or ()):
        tr = get_com_member(cp, "Transform2")
        d = list(get_com_member(tr, "ArrayData") or ())
        if len(d) >= 12:
            out.append(
                (
                    str(get_com_member(cp, "Name2") or ""),
                    round(d[9] * 1000, 1),
                    round(d[10] * 1000, 1),
                    round(d[11] * 1000, 1),
                )
            )
    return out


def main() -> int:
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    try:
        doc = c_.try_call(get_com_member, sw, "ActiveDoc")
        doc = doc[1] if isinstance(doc, tuple) else doc
        if doc is None or int(get_com_member(doc, "GetType") or 0) != 2:
            print("★ 当前活动文档不是装配体 —— 先跑第 2 步准备场景")
            return 1
        title = str(get_com_member(doc, "GetTitle") or "")
        print("当前装配体：%s" % title)

        before = _translations(doc)
        print("① 执行前平移(mm)：")
        for name, x, y, z in before:
            print("     %-18s (%.1f, %.1f, %.1f)" % (name, x, y, z))
        print(
            "   配合数：%d"
            % len(
                [
                    r
                    for r in (asm_.collect_mate_feature_summary(doc) or ())
                    if str(r.get("type") or "") != "MateGroup"
                    and str(r.get("type") or "").startswith("Mate")
                ]
            )
        )

        #: ① 选面
        sel = asm_probe_select(doc)
        print("② 选面：%s" % sel)

        #: ② 核归属
        sm = get_com_member(doc, "SelectionManager")
        owners = []
        for k in (1, 2):
            ok_o, comp = c_.try_call(
                c_.get_com_member, sm, "GetSelectedObjectsComponent4", k, 1
            )
            name = str(get_com_member(comp, "Name2") or "") if ok_o else None
            owners.append(name if comp is not None else None)
        print("③ 面归属：%s · distinct=%d" % (owners, len({o for o in owners if o})))
        if len({o for o in owners if o}) != 2:
            print("★ 两个面不属于不同组件 ⇒ 配合会变成「面和它自己」，中止")
            return 1

        #: ③ 建配合
        ok_d, data = c_.try_call(lambda: get_com_member(doc, "CreateMateData", 0))
        if ok_d and data is not None:
            import pythoncom
            from win32com.client import VARIANT

            faces = []
            for k in (1, 2):
                ok_f, f = c_.try_call(
                    c_.get_com_member, sm, "GetSelectedObject6", k, -1
                )
                faces.append(f if ok_f else None)
            c_.try_call(
                lambda: setattr(
                    data,
                    "EntitiesToMate",
                    VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, faces),
                )
            )
            c_.try_call(lambda: setattr(data, "MateAlignment", 2))
            c_.try_call(lambda: get_com_member(doc, "CreateMate", data))
            print("④ 已调用 CreateMate")

        mates = [
            r
            for r in (asm_.collect_mate_feature_summary(doc) or ())
            if str(r.get("type") or "") != "MateGroup"
            and str(r.get("type") or "").startswith("Mate")
        ]
        print("⑤ 真实配合：%s" % [(r.get("name"), r.get("type")) for r in mates])

        doc.EditRebuild3()
        after = _translations(doc)
        print("⑥ 执行后平移(mm)：")
        for name, x, y, z in after:
            print("     %-18s (%.1f, %.1f, %.1f)" % (name, x, y, z))

        #: 存盘 + 视图
        c_.try_call(
            c_.get_com_member,
            c_.get_com_member(doc, "Extension"),
            "SaveAs",
            str(DEST),
            0,
            5,
            c_.create_empty_dispatch_variant(),
            c_.out_i4(),
            c_.out_i4(),
        )
        try:
            doc.ShowNamedView2("*等轴测", 7)
            doc.ViewZoomtofit2()
        except Exception:  # noqa: BLE001
            pass
        print("★ 已存 %s（文档保持打开）" % DEST.name)
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def asm_probe_select(doc) -> dict:
    """复用探针里**已跑通**的选面实现（第 61 轮验过能选到两个不同组件）。"""
    from probe_e4_assembly import _select_two_faces

    return _select_two_faces(doc, nonplanar=True)


if __name__ == "__main__":
    raise SystemExit(main())

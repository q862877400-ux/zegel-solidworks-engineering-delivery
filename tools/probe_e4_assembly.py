"""E4 真机装配探针（**唯一一份**）：搭两组件 → 试配合 → 读干涉。

## 合并说明

第 44 / 45 轮各写了一个探针，重复了「边跑边写证据」的辅助函数，还因为打补丁弄乱了。
本轮**合成一份**：既复现「组件 0 → 2」，也复现「配合三条路都建不成」，还读干涉。

## 已确认的事实（不在此重验）

| 事实 | 内容 |
|---|---|
| 564 | 加组件通了：官方 Remarks 要求「文件必须已在内存」+ 兜底要用 `GetPathName()` |
| 565 | 配合三条路都建不成（`AddMate5` 选错 / `CreateMate` 回 None ×2）；装配本体已通 |

★ `IComponent2.GetBody()` / `IGetBody()` 在本机晚绑定下都不可用
  （`0x80020003` 成员未找到 / 「无法读只写属性」）⇒ 面改用 `SelectByRay` 取。

## 判据（全部独立读数，不看返回值）

| 读数 | 手段 |
|---|---|
| 组件数 | `IAssemblyDoc.GetComponents(False)` 条数 |
| **真实**配合数 | 特征树里类型以 `Mate` 开头且**不是** `MateGroup` 的条数（事实/第 44 轮教训） |
| 干涉 | `sw_assembly.get_interference_detection` |

## 证据边跑边写

`Evidence` 每 `mark()` 一次就落盘 —— 第 43 轮实测：进程被杀时 `finally` 不执行，
一份证据都没留下。
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))

import pythoncom  # noqa: E402
from e4_probe_common import Evidence  # noqa: E402

from scripts import sw_assembly as asm_  # noqa: E402
from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import get_com_member, open_doc_count  # noqa: E402
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · E4 真机装配，唯一一份）
# 文件:   tools/probe_e4_assembly.py
# 定位:   合并第 44/45 轮两个探针：搭两组件 → 试配合（三条已排除的路径只复现第一条）
#          → 读干涉。判据全用独立读数（组件数 / 真实配合特征数），不看返回值。
# 官方依据: IAssemblyDoc\AddComponent5.md（文件必须已在内存）· IAssemblyDoc\GetComponents ·
#          IAssemblyDoc\CreateMate.md / CreateMateData.md（继任者，`*` 表示支持预选）·
#          ICoincidentMateFeatureData\EntitiesToMate.md · enums\swMateType_e.md（COINCIDENT=0）·
#          IModelDocExtension\SelectByRay（12 参）· enums\swAddMateError_e.md
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "e4-assembly.json"
EV = Evidence(DEST, {"probe": "e4-assembly", "part": str(PART)})
SW_MATE_COINCIDENT = 0
#: ★ `--nonplanar` ⇒ 组件 2 抬到 z=50mm（验「共面冗余」假设用；第 46 轮该变体射线打空）
NONPLANAR = "--nonplanar" in sys.argv


def _count(asm_doc) -> int:
    try:
        return len(list(get_com_member(asm_doc, "GetComponents", False) or []))
    except Exception:  # noqa: BLE001
        return -1


def _real_mates(model) -> list:
    """★ 真实配合特征：类型以 `Mate` 开头且**不是** `MateGroup`（第 44 轮的教训）。"""
    out = []
    for rec in asm_.collect_mate_feature_summary(model) or []:
        t = str(rec.get("type") or "")
        if t != "MateGroup" and t.startswith("Mate"):
            out.append(rec)
    return out


def _select_two_faces(doc, *, nonplanar: bool = False) -> dict:
    """★ 用 `SelectByRay` 选两块板的顶面（`IComponent2` 取实体的两条路都不可用）。"""
    ext = get_com_member(doc, "Extension")
    doc.ClearSelection2(True)
    rows = []
    #: ★ 第 46 轮：两条射线方向不同 —— 一条自上而下打组件 1 的顶面（z=20mm），
    #:   一条自下而上打组件 2 的底面（z=50mm）⇒ 两面不共面、法向相反。
    #: ★ 两种几何都留着：
    #:   · 默认（共面）：两块都在 z 0..20 ⇒ 顶面都在 z=20mm（第 45 轮用过）
    #:   · `nonplanar`：组件 2 抬到 z=50mm ⇒ 打它的底面（z=50mm）
    #:     ⚠ 第 46 轮实测：这条射线**打空**（选中数没从 1 变 2）⇒ 该变体尚未成功设置
    #: ★ 第 48 轮修：两条**都从上方**打（`-z` 方向已验证可用），只改起射高度。
    #:   组件 2 抬到 z=50mm 后其顶面在 z=70mm ⇒ 射线起点要高于 70mm。
    #:   ⇒ 两面平行但不共面（z=20 与 z=70）⇒ 重合配合若成立会把组件 2 拉下来。
    rays = (
        (5.0, 5.0, 0.070, -1.0),
        (35.0, 5.0, 0.090, -1.0) if nonplanar else (35.0, 5.0, 0.070, -1.0),
    )
    for idx, (x_mm, y_mm, z_m, dz) in enumerate(rays):
        get_com_member(
            ext, "SelectByRay",
            x_mm / 1000.0, y_mm / 1000.0, z_m,
            0.0, 0.0, dz, 1e-4,
            2,                                      #: swSelFACES
            bool(idx), 0, 0,
        )
        try:
            n = int(
                get_com_member(
                    get_com_member(doc, "SelectionManager"),
                    "GetSelectedObjectCount2", -1,
                ) or 0
            )
        except Exception:  # noqa: BLE001
            n = -1
        rows.append({"i": idx, "selected": n})
    return {"rays": rows, "max_selected": max((r["selected"] for r in rows), default=0)}


def main() -> int:
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        if not PART.is_file():
            EV.mark("abort", err="零件不存在")
            return 1

        ok_p, part_doc = _try(c_.open_document, sw, str(PART))
        EV.mark(
            "open_part",
            ok=ok_p,
            loaded=Path(str(_member(part_doc, "GetPathName") or "")).name,
        )

        ok_n, asm_doc = _try(c_.new_document, sw, "assembly")
        _try(sw.ActivateDoc3, str(_member(asm_doc, "GetTitle") or ""), 0, False)
        EV.mark("new_assembly", ok=ok_n)

        before = _count(asm_doc)
        #: ★ 第 46 轮：把第二个组件**抬到 z=50mm**，让两块的接触面不共面、法向相反
        #:   —— 用来验第 45 轮那个「共面导致冗余、所以 CreateMate 回 None」的假设。
        _try(asm_.add_component, asm_doc, str(PART), 0.0, 0.0, 0.0, "", sw)
        _try(
            asm_.add_component, asm_doc, str(PART), 30.0, 0.0,
            (50.0 if NONPLANAR else 0.0), "", sw,
        )
        after = _count(asm_doc)
        EV.mark("components", before=before, after=after, added=after - before)

        sel = _select_two_faces(asm_doc, nonplanar=NONPLANAR)
        EV.mark("select_faces", **sel)

        m_before = len(_real_mates(asm_doc))
        ok_d, data = _try(
            lambda: get_com_member(asm_doc, "CreateMateData", SW_MATE_COINCIDENT)
        )
        ok_m, feat = False, None
        if ok_d and data is not None:
            #: ★★ 第 49 轮：**只加一个变量** —— `MateAlignment`（官方成员，之前没设过）。
            #:   `swMateAlign_e` 逐字：ALIGNED=0 / ANTI_ALIGNED=1 / **CLOSEST=2**。
            #:   用 CLOSEST 让 SolidWorks 自己定朝向，避免因「朝向反了」被拒。
            ok_sel, sel_mgr = _try(lambda: get_com_member(asm_doc, "SelectionManager"))
            faces_back = []
            if ok_sel and sel_mgr is not None:
                for k in (1, 2):
                    ok_f, fobj = _try(
                        get_com_member, sel_mgr, "GetSelectedObject6", k, -1
                    )
                    faces_back.append(fobj if ok_f else None)
            ok_set = False
            if all(f is not None for f in faces_back):
                #: ★★ 第 49 轮：`EntitiesToMate` 是 `System.object`（VARIANT 里的对象数组）。
                #:   直接 `setattr(data, "EntitiesToMate", (f1, f2))` 在真机上
                #:   **回 True 但读回 0** ⇒ 值没进去。改用显式 VARIANT 对象数组。
                from win32com.client import VARIANT

                ok_set, _ = _try(
                    lambda: setattr(
                        data,
                        "EntitiesToMate",
                        VARIANT(
                            pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                            [faces_back[0], faces_back[1]],
                        ),
                    )
                )
            ok_align, _ = _try(lambda: setattr(data, "MateAlignment", 2))

            #: ★★★ 读回 —— `setattr` 回 True **不等于**值进去了（返回值 ≠ 实际结果）。
            #:   ★ 第 46 轮的教训：测试设置无效时得出的「排除」不算数。
            back = {}
            ok_rb1, rb_ent = _try(lambda: data.EntitiesToMate)
            try:
                back["entities"] = len(list(rb_ent or ())) if ok_rb1 else -1
            except TypeError:
                back["entities"] = -1
            ok_rb2, rb_align = _try(lambda: data.MateAlignment)
            back["alignment"] = int(rb_align) if (ok_rb2 and rb_align is not None) else -1

            EV.mark(
                "mate_data",
                faces=len([f for f in faces_back if f is not None]),
                set_entities=ok_set,
                set_alignment=ok_align,
                #: ★ 读回为证：`entities==2 and alignment==2` 才能说「设置生效」
                readback=back,
                setup_effective=bool(
                    back["entities"] == 2 and back["alignment"] == 2
                ),
            )
            ok_m, feat = _try(lambda: get_com_member(asm_doc, "CreateMate", data))
        m_after = len(_real_mates(asm_doc))
        EV.mark(
            "try_mate",
            data_ok=ok_d,
            create_ok=ok_m,
            feat_none=(feat is None) if ok_m else None,
            mates_before=m_before,
            mates_after=m_after,
        )

        ok_i, interf = _try(asm_.get_interference_detection, asm_doc)
        EV.mark("interference", ok=ok_i, detail=str(interf)[:220])

        EV.data["components"] = after
        EV.data["real_mates"] = m_after
        EV.data["interference"] = str(interf)[:400] if ok_i else "err"
        EV.data["ok"] = bool(after >= 2)
        EV.data["conclusion"] = (
            "★ 两组件装配搭起来了（%s → %s）；真实配合特征 %s → %s；干涉%s"
            % (
                before,
                after,
                m_before,
                m_after,
                "已读" if ok_i else "读失败",
            )
        )
        EV.mark("conclusion", text=EV.data["conclusion"])
        return 0 if EV.data["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        EV.data["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        EV.data["traceback"] = traceback.format_exc()[-1000:]
        EV.mark("exception", err=EV.data["err"])
        return 1
    finally:
        if sw is not None:
            for d in list(sw.GetDocuments() or []):
                _try(sw.CloseDoc, str(_member(d, "GetTitle") or ""))
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            EV.data["docs_left"] = open_doc_count(sw)
        EV.flush()
        print("   证据已写：output/e4-assembly.json")


if __name__ == "__main__":
    raise SystemExit(main())

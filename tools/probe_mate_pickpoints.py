"""候选 13（最后一个）：`ICoincidentMateFeatureData.PickPoints` 显式给坐标。

## 官方依据（逐字）

`C:\\swapi\\types\\ICoincidentMateFeatureData\\PickPoints.md`
- 签名 `System.object PickPoints {get; set;}`
- Returns：「Array of x, y, z-coordinates, **one set for each mate entity**」
  ⇒ 两个实体 = **6 个 double**（依次 x1,y1,z1,x2,y2,z2）
- Remarks：「Pick points define **the position of the entities to mate**. If no pick points are
  specified, then entities are mated using **default pick points**.」
  ⇒ 不指定时用默认拾取点 —— 所以我一直没设它，而默认拾取点可能落在无效位置。

## 本变体只改一处

给 `PickPoints` 送 6 个 double（两块板接触面中心），其余与已排除的候选完全相同。

★ 用 `VARIANT(VT_ARRAY|VT_R8, [...])` —— 与事实 566 同一条教训：
  `System.object` 参数直接送 Python 列表会被静默丢掉。

## 判据

真实配合特征 **0 → 1** ⇒ 成；仍 0 → 0 ⇒ 13 个候选全排除，配合这条路**整体挂起**。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 配合候选 13）
# 文件:   tools/probe_mate_pickpoints.py
# 定位:   最后一个未试的配合候选：给 `PickPoints` 显式送 6 个 double。
#          已排除 12 个（事实 565/566；存盘那条见 `probe_mate_after_save.py`）。
# 官方依据: C:\swapi\types\ICoincidentMateFeatureData\PickPoints.md（签名 + Returns + Remarks）·
#          IAssemblyDoc::CreateMate / CreateMateData · IModelDocExtension::SelectByRay（Mark=1）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "mate-pickpoints.json"

#: 两块板接触面中心（米）：组件1 顶面 z=20mm、组件2 底面 z=50mm（后者抬 50mm 放置）
PICK_POINTS = (
    0.050, 0.030, 0.020,   # 组件 1 顶面中心
    0.080, 0.030, 0.050,   # 组件 2 底面中心（x 30..130 → 中心 80）
)

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from probe_e4_assembly import (  # noqa: E402
    SW_MATE_COINCIDENT,
    _real_mates,
    _select_two_faces,
)
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "mate-pickpoints", "pick_points": list(PICK_POINTS)}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ok_p, _part = c_.try_call(c_.open_document, sw, str(PART))
        ev["open_part"] = bool(ok_p)
        ok_n, asm_doc = c_.try_call(c_.new_document, sw, "assembly")
        ev["new_assembly"] = bool(ok_n)
        if asm_doc is not None:
            try:
                sw.ActivateDoc3(str(get_com_member(asm_doc, "GetTitle") or ""), 0, False)
            except Exception:  # noqa: BLE001
                pass

        #: 与真相位（非共面）以配合有意义
        c_.try_call(asm_.add_component, asm_doc, str(PART), 0.0, 0.0, 0.0, "", sw)
        c_.try_call(asm_.add_component, asm_doc, str(PART), 30.0, 0.0, 50.0, "", sw)
        sel = _select_two_faces(asm_doc, nonplanar=True)
        ev["select"] = sel
        print("① 选面：max_selected=%s" % sel.get("max_selected"))

        m_before = len(_real_mates(asm_doc))
        ok_d, data = c_.try_call(
            lambda: get_com_member(asm_doc, "CreateMateData", SW_MATE_COINCIDENT)
        )
        rec: dict = {"data_ok": bool(ok_d)}
        if ok_d and data is not None:
            import pythoncom
            from win32com.client import VARIANT

            sm = get_com_member(asm_doc, "SelectionManager")
            faces = []
            for k in (1, 2):
                ok_f, f = c_.try_call(get_com_member, sm, "GetSelectedObject6", k, -1)
                faces.append(f if ok_f else None)
            if all(f is not None for f in faces):
                ok_e, _ = c_.try_call(
                    lambda: setattr(
                        data,
                        "EntitiesToMate",
                        VARIANT(
                            pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                            [faces[0], faces[1]],
                        ),
                    )
                )
                rec["set_entities"] = bool(ok_e)

            #: ★★★ 本轮唯一的差别：显式 PickPoints（6 个 double）。
            #:   ★ 第 59 轮实测：`VARIANT(VT_ARRAY|VT_R8, [...])` **setattr 回 False、读回 0**
            #:     ⇒ 设置没生效 ⇒ 那句结论不算数（事实 566 的纪律）。
            #:   ⇒ 三种 marshaling 依次试，**每一种都读回验证**，只记真正进去的那一种。
            import array as _array

            attempts = [
                (
                    "VARIANT(VT_ARRAY|VT_R8)",
                    lambda: VARIANT(
                        pythoncom.VT_ARRAY | pythoncom.VT_R8, list(PICK_POINTS)
                    ),
                ),
                ("tuple", lambda: tuple(PICK_POINTS)),
                ("array.array(d)", lambda: _array.array("d", PICK_POINTS)),
            ]
            pp_tried = []
            for name, maker in attempts:
                ok_t, ret_t = c_.try_call(lambda mk=maker: setattr(
                    data, "PickPoints", mk()
                ))
                ok_rb, rb_val = c_.try_call(lambda: data.PickPoints)
                try:
                    n_rb = len(list(rb_val or ())) if ok_rb else -1
                except TypeError:
                    n_rb = -1
                pp_tried.append(
                    {"form": name, "set_ok": bool(ok_t), "readback": n_rb}
                )
                print("   PickPoints[%s] set=%s · 读回 %s" % (name, ok_t, n_rb))
                if n_rb == 6:
                    break
            rec["pickpoints_attempts"] = pp_tried
            rec["set_pickpoints"] = any(a["readback"] == 6 for a in pp_tried)
            ok_al, _ = c_.try_call(lambda: setattr(data, "MateAlignment", 2))
            rec["set_alignment"] = bool(ok_al)

            #: 读回（事实 566：`System.object` 参数要证明真的进去了）
            back: dict = {}
            ok_rb, rb = c_.try_call(lambda: data.PickPoints)
            try:
                back["pickpoints"] = len(list(rb or ())) if ok_rb else -1
            except TypeError:
                back["pickpoints"] = -1
            ok_rb2, rb2 = c_.try_call(lambda: data.EntitiesToMate)
            try:
                back["entities"] = len(list(rb2 or ())) if ok_rb2 else -1
            except TypeError:
                back["entities"] = -1
            rec["readback"] = back
            rec["setup_effective"] = bool(
                back.get("entities") == 2 and rec["set_pickpoints"]
            )
        print("② 数据：%s" % json.dumps({k: rec.get(k) for k in
                                          ("data_ok", "set_entities", "set_pickpoints",
                                           "set_alignment", "readback",
                                           "setup_effective")}, ensure_ascii=False))

        ok_m, feat = (
            c_.try_call(lambda: get_com_member(asm_doc, "CreateMate", data))
            if (ok_d and data is not None)
            else (False, None)
        )
        m_after = len(_real_mates(asm_doc))
        rec.update(
            {
                "create_ok": bool(ok_m),
                "feat_none": (feat is None) if ok_m else None,
                "mates_before": m_before,
                "mates_after": m_after,
            }
        )
        ev["mate"] = rec
        print("③ CreateMate：ok=%s · 真实配合特征 %s → %s"
              % (ok_m, m_before, m_after))

        ev["ok"] = bool(m_after > m_before)
        #: ★★ 结论措辞要分三种，别混：
        #:   ① 成 → 配合建成
        #:   ② 设置生效但建不出 → **排除**这个候选
        #:   ③ 设置**根本没生效** → **验不了**这个候选（不能说它无效）
        _attempts = ev.get("mate", {}).get("pickpoints_attempts") or []
        _set_ok = any(a.get("readback") == 6 for a in _attempts)
        if ev["ok"]:
            ev["conclusion"] = "★ PickPoints 生效：配合 %s → %s" % (m_before, m_after)
        elif not _set_ok:
            ev["conclusion"] = (
                "★★ `PickPoints` **写不进去**（%d 种 marshaling 全 set=False、读回 0）"
                "⇒ 这个候选**验不了**（不是无效）⇒ 配合这条路整体挂起"
                % len(_attempts)
            )
        else:
            ev["conclusion"] = (
                "★ PickPoints 设置已生效但配合仍 %s → %s ⇒ 第 13 个候选**排除**"
                % (m_before, m_after)
            )
        print(ev["conclusion"])
        return 0 if ev["ok"] else 1
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ev["traceback"] = traceback.format_exc()[-800:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            try:
                for d in list(get_com_member(sw, "GetDocuments") or ()):
                    sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
            except Exception:  # noqa: BLE001
                pass
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = len(list(get_com_member(sw, "GetDocuments") or ()))
            except Exception:  # noqa: BLE001
                pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())

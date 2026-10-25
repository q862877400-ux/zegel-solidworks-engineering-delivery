"""候选 12：**先把装配存盘**再 `CreateMate`。

## 为什么试它

配合仍建不出来，已排除 11 个候选（事实 565/566）。
剩下的两条里，「先把装配存盘再建配合」是**最省的一个**：不引入新 API，只多加一步存盘。

**假设**：`CreateMate` 可能需要文档已经落盘（有路径）才能把配合特征写进去；
未保存的装配里它可能直接返回 `None`。

## 复用而不重写

`_real_mates` / `_select_two_faces` 直接**导入** `probe_e4_assembly` 里的实现 ——
再写一份会触发统一化门禁的「跨文件同函数体」判据（第 58 轮踩过）。

## 判据

| 读数 | 结论 |
|---|---|
| 真实配合特征 **0 → 1** | 成 ⇒ 存盘就是缺的前提 |
| 仍 0 → 0 | 不成 ⇒ 第 12 个候选排除，只剩 `PickPoints` |

★ 「真实配合特征」= 类型以 `Mate` 开头且**不是** `MateGroup`（第 44 轮教训）。
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
# 仓库:   本项目自身（工具 · 配合候选 12）
# 文件:   tools/probe_mate_after_save.py
# 定位:   验「`CreateMate` 是否需要装配已落盘」。已排除 11 个候选（事实 565/566）；
#          本条只加「存盘」一步，不引入新 API。复用 `probe_e4_assembly` 的取面与配合计数。
# 官方依据: IAssemblyDoc::CreateMate / CreateMateData · ICoincidentMateFeatureData::EntitiesToMate ·
#          IModelDocExtension::SelectByRay（Mark=1）· IModelDoc2::Save3（经 `save_document`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "mate-after-save.json"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from probe_e4_assembly import (  # noqa: E402
    SW_MATE_COINCIDENT,
    _real_mates,
    _select_two_faces,
)
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "mate-after-save"}
    sw = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ok_p, part_doc = c_.try_call(c_.open_document, sw, str(PART))
        ev["open_part"] = bool(ok_p)
        ok_n, asm_doc = c_.try_call(c_.new_document, sw, "assembly")
        ev["new_assembly"] = bool(ok_n)
        if asm_doc is not None:
            try:
                sw.ActivateDoc3(str(get_com_member(asm_doc, "GetTitle") or ""), 0, False)
            except Exception:  # noqa: BLE001
                pass

        #: ★★ 与已排除的候选**唯一的差别**：加两个组件后先存盘
        for dx in (0.0, 30.0):
            c_.try_call(asm_.add_component, asm_doc, str(PART), dx, 0.0, 0.0, "", sw)
        out = R / "output" / "mate_save" 
        out.mkdir(parents=True, exist_ok=True)
        ok_s, s_ret = c_.try_call(
            c_.save_document, asm_doc, str(out / "with_mate.SLDASM")
        )
        ev["saved"] = bool(ok_s)
        ev["saved_path"] = str(get_com_member(asm_doc, "GetPathName") or "")
        print("① 装配已存盘：%s → %s" % (ev["saved"], ev["saved_path"]))

        sel = _select_two_faces(asm_doc, nonplanar=True)
        ev["select"] = sel
        print("② 选面：max_selected=%s" % sel.get("max_selected"))

        m_before = len(_real_mates(asm_doc))
        ok_d, data = c_.try_call(
            lambda: get_com_member(asm_doc, "CreateMateData", SW_MATE_COINCIDENT)
        )
        ok_set = ok_align = False
        if ok_d and data is not None:
            import pythoncom
            from win32com.client import VARIANT

            sm = get_com_member(asm_doc, "SelectionManager")
            faces = []
            for k in (1, 2):
                ok_f, f = c_.try_call(get_com_member, sm, "GetSelectedObject6", k, -1)
                faces.append(f if ok_f else None)
            if all(f is not None for f in faces):
                ok_set, _ = c_.try_call(
                    lambda: setattr(
                        data,
                        "EntitiesToMate",
                        VARIANT(
                            pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                            [faces[0], faces[1]],
                        ),
                    )
                )
            ok_align, _ = c_.try_call(lambda: setattr(data, "MateAlignment", 2))
        ev["data"] = {"ok": bool(ok_d), "set_entities": bool(ok_set),
                      "set_alignment": bool(ok_align)}

        ok_m, feat = c_.try_call(
            lambda: get_com_member(asm_doc, "CreateMate", data)
        ) if (ok_d and data is not None) else (False, None)
        m_after = len(_real_mates(asm_doc))
        ev["mate"] = {
            "create_ok": bool(ok_m),
            "feat_none": (feat is None) if ok_m else None,
            "mates_before": m_before,
            "mates_after": m_after,
        }
        print("③ CreateMate：ok=%s · 真实配合特征 %s → %s"
              % (ok_m, m_before, m_after))

        ev["ok"] = bool(m_after > m_before)
        ev["conclusion"] = (
            "★ 存盘后再建配合**成功**（配合 %s → %s）⇒ 存盘就是缺的前提"
            % (m_before, m_after)
            if ev["ok"]
            else "★ 存盘后仍建不出来（%s → %s）⇒ 第 12 个候选排除，只剩 PickPoints"
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
                ev["docs_left"] = len(
                    list(get_com_member(sw, "GetDocuments") or ())
                )
            except Exception:  # noqa: BLE001
                pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())

"""把交付件的板宽改回设计值（100mm）并保存 —— 探针验证时把它改成 120 了。

## 为什么要这一步

第 55 轮把四个孔位尺寸落到交付件时，探针**为了验证联动**把 `D1@草图1` 从 100 改成 120，
然后**连着保存**了 ⇒ 交付件落地成了 120mm 宽的板。

★ 交付件必须是**设计尺寸**（100mm），联动是"改宽时孔跟着动"的**能力**，
  不是"把板做成 120"。
  ⇒ 本脚本把宽度改回 100、重建、保存，并**回读**确认。

## 判据

`solid_body_extent_mm(doc).x_mm == 100.0`（±0.01）
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
# 仓库:   本项目自身（工具 · 交付件尺寸复位）
# 文件:   tools/restore_deliverable_width.py
# 定位:   第 55 轮把孔位尺寸落到交付件时，探针为验证联动把板宽改成 120 并保存；
#          交付件必须是设计尺寸 100mm ⇒ 本脚本改回并回读确认。
# 官方依据: IDimension::SetSystemValue3（经 `update_dimension_mm`，单位米）·
#          IModelDoc2::EditRebuild3 · IModelDoc2::Save3（经 `save_document`）·
#          `solid_body_extent_mm` 回读
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

TARGET = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "restore-width.json"
WANT_MM = 100.0
TOL_MM = 0.01

import sw_connect as c_  # noqa: E402

from scripts.sw_document_data import update_dimension_mm  # noqa: E402
from scripts.sw_feature_readback import solid_body_extent_mm  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "restore-width", "target": str(TARGET)}
    sw = doc = None
    try:
        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        ok_o, doc = c_.try_call(c_.open_document, sw, str(TARGET))
        ev["open"] = bool(ok_o)
        ev["extent_in"] = solid_body_extent_mm(doc).get("x_mm")
        print("① 打开：%s · 当前板宽 %s mm" % (ok_o, ev["extent_in"]))

        if abs(float(ev["extent_in"]) - WANT_MM) > TOL_MM:
            ok_w, w_ret = c_.try_call(update_dimension_mm, doc, "D1@草图1", WANT_MM)
            ev["width_change"] = {
                "ok": bool(ok_w),
                "err": "" if ok_w else str(w_ret)[:100],
            }
            print("② 改回 %s mm：%s" % (WANT_MM, ev["width_change"]))
            try:
                c_.get_com_member(doc, "EditRebuild3")
            except Exception:  # noqa: BLE001
                pass
        else:
            print("② 已是 %s mm，不需要改" % WANT_MM)

        ev["extent_out"] = solid_body_extent_mm(doc).get("x_mm")
        ok_sv, sv_ret = c_.try_call(c_.save_document, doc)
        ev["saved"] = bool(ok_sv)
        if not ok_sv:
            ev["save_err"] = str(sv_ret)[:120]
        print("③ 回读板宽 %s mm · 保存 %s" % (ev["extent_out"], ev["saved"]))

        ev["ok"] = bool(
            ev["saved"] and abs(float(ev["extent_out"]) - WANT_MM) <= TOL_MM
        )
        ev["conclusion"] = (
            "★ 交付件板宽已复位到 %s mm" % ev["extent_out"]
            if ev["ok"]
            else "★ 未达：回读 %s mm · 保存 %s" % (ev["extent_out"], ev["saved"])
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
        if doc is not None:
            try:
                ttl = str(c_.get_com_member(doc, "GetTitle") or "")
                if ttl:
                    sw.CloseDoc(ttl)
            except Exception:  # noqa: BLE001
                pass
        if sw is not None:
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
            try:
                ev["docs_left"] = c_.open_doc_count(sw)
            except Exception:  # noqa: BLE001
                pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())

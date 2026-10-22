"""★ 真机：**焊件切割清单那条链** —— ★ 在一个「**真有结构构件**」的文档上验。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_cut_list_chain.py
# 定位:   ★ 2026-10-03（轮 429）`plan-200r-v3` **段 2（焊件族）**的第二步。
# ★★ **为什么现在值得重试**：★ `capabilities.yaml` 的 `weldment_cut_list`（`level: stitc
# hed`）
#     记着两条卡点，★ 而它们的**前提在轮 428 已经不成立了**：
#     ```
#     · `set_cut_list_properties` 报「**没有可写入切割清单的结构构件实体**」
#       → ★ 而那条的**真因**（轮 364 记的）是「本机没装焊件轮廓库 ⇒ **建不出结构构件**」
#       → ★★ 而**轮 428 建成了结构构件**（PASS）⇒ ★ **这个前提没了** ✓
#     · ⚠ 「**只在新建零件上验过**（★ 未建结构构件）」 —— ★ 而本探针正是补这一条 ✓
#     ```
#   ★★ **本探针把那条链一次走完**：
#     ```
#     建构件 → weldment_evidence（看切割清单文件夹）→ ensure_cut_list
#       → set_cut_list_properties → update_cut_list → export_cut_list_csv（看文件）
#     ```
#   ★★ **判据**：★ ① `evidence` 里**真有**切割清单文件夹 ★ ② CSV **文件存在且非空**
#     （★ 后者是硬约束③的原话：★ "判据是 FILE"）。
# ⚠ 只新建、**不保存** SW 文档（★ 硬约束⑦）；★ CSV 写到 `output/`（★ 那是产物目录，★ 不
# 算保存文档）。
# 官方依据: `IFeatureManager.InsertStructuralWeldment5` · `IWeldmentCutListFeature` 那族
#           （★ 仓内已有）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 切割清单文件夹**非空** ★ 且 导出 CSV **文件存在且非空**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "cut-list-chain-evidence.json"
)
CSV = Path(Path(__file__).resolve().parents[1] / "output" / "cut-list-chain.csv")
PROFILE = Path(
    r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles\GB\square-rods.sldlfp"
)


def main() -> int:
    import sw_connect

    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        sketch_line,
        start_sketch,
    )
    from scripts.sw_weldment import (
        create_structural_member_from_sketch,
        ensure_cut_list,
        export_cut_list_csv,
        set_cut_list_properties,
        update_cut_list,
        weldment_evidence,
    )

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_line(doc, 0.0, 0.0, 100.0, 0.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        #: ★ ① 先建构件（★ 轮 428 已验的链）
        rep = create_structural_member_from_sketch(doc, sk, str(PROFILE))
        ev["steps"]["structural_member"] = {
            "ok": bool(rep.get("ok")),
            "feature": rep.get("feature"),
            "new_type_names": rep.get("new_type_names"),
        }
        #: ★ ② 看切割清单文件夹（★ 不建）
        ev1 = weldment_evidence(doc)
        ev["steps"]["evidence_before"] = {
            "ok": True,
            "cut_list_folders": str(ev1.get("cut_list_folders"))[:200],
            "keys": sorted(ev1.keys())[:12],
        }
        #: ★ ③ 建切割清单（若没有）
        try:
            cl = ensure_cut_list(doc)
            ev["steps"]["ensure_cut_list"] = {
                "ok": cl is not None,
                "returned": json.dumps(cl, ensure_ascii=False, default=str)[:200],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["ensure_cut_list"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        #: ★ ④ 写属性
        try:
            props = set_cut_list_properties(
                doc, {"Description": "DSH \u65b9\u7ba1", "Material": "Q235"}
            )
            ev["steps"]["set_cut_list_properties"] = {
                "ok": bool(props),
                "returned": json.dumps(props, ensure_ascii=False, default=str)[:200],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["set_cut_list_properties"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:150]),
            }
        #: ★ ⑤ 刷新
        try:
            up = update_cut_list(doc)
            ev["steps"]["update_cut_list"] = {
                "ok": up is not None,
                "returned": json.dumps(up, ensure_ascii=False, default=str)[:200],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["update_cut_list"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        #: ★ ⑥ 证据 + 导出 CSV（★ 判据是**文件**）
        ev2 = weldment_evidence(doc)
        ev["steps"]["evidence_after"] = {
            "ok": True,
            "cut_list_folders": str(ev2.get("cut_list_folders"))[:300],
        }
        try:
            if CSV.exists():
                CSV.unlink()
            p = export_cut_list_csv(ev2, str(CSV))
            ev["steps"]["export_csv"] = {
                "ok": CSV.is_file() and CSV.stat().st_size > 0,
                "path": str(p) if p else None,
                "bytes": CSV.stat().st_size if CSV.is_file() else 0,
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["export_csv"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        ok_cl = bool(
            (ev["steps"].get("evidence_after") or {}).get("cut_list_folders")
            and "[]"
            not in str(
                (ev["steps"].get("evidence_after") or {}).get("cut_list_folders")
            )
        )
        ok_csv = bool((ev["steps"].get("export_csv") or {}).get("ok"))
        ev["verdict"] = "pass" if (ok_cl and ok_csv) else "partial"
        ev["note"] = (
            "★ 在**真有结构构件**的文档上走完切割清单那条链 —— "
            "★ 而它的**旧卡点前提**（「**建不出结构构件**」）**已在轮 428 失效**。"
            "★ 判据：① 切割清单文件夹非空 ② 导出 CSV 文件存在且非空。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1800])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""★ 真机：hem 为什么回 None —— **假设驱动的诊断**（一次跑完，不是换着参数瞎试）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_spec209_hem_diag.py
# 定位:   ★ 承 `tools/probe_spec209_b2.py`：那一轮 **T2 hem 回 `None`**（★ T1 前置建成
#           、T4 负例正常）。
#   ★★ 本探针**同时判三个假设**（★ 每个假设都有一条可回读的判据，不是"再试一次"）：
#     ```
#     H1 选错了边   —— 60×40×2 的板有 12 条边：4 长(60) + 4 宽(40) + 4 **短(2，厚度棱)**
#                      ★ `index:0` 很可能挑中的是**厚度棱**，而 hem 要的是**板面外缘**
#                      ⇒ 判据：**枚举每条边的长度**，再挑**最长**的那条重试
#     H2 单位不是米 —— ★ 本仓刚在 `InsertMoveCopyBody2` 上实测过「长度是文档单位、不是米」
#                      ⇒ 判据：把 4 个长度参数**整体 ×1000**（毫米口径）重试
#     H3 卸料槽挡路 —— 用默认卸料槽（`UseDefaultRelief=True`）重试
#     ```
#   ★ 每个变体**各开一张新零件**（★ 免副作用污染 —— 本仓栽过这个跟头）✓
# 官方依据: `C:\swapi\types\IFeatureManager\InsertSheetMetalHem2.md`（16 参 + 四步前置）
#           ·
#   `C:\swapi\examples\Insert_Sheet_Metal_Hem_Example_VB.md`（调用序）·
#   `C:\swapi\enums\swHemTypes_e.md`（Open=0 · Closed=1 · Double=4）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R / "scripts"))
OUT = R / "output" / "spec209-hem-diag.json"


def main() -> int:
    import sw_connect
    import sw_part as p_
    import sw_selection_spec as ss
    import sw_sheet_metal as sm
    from sw_connect import get_com_member, safe_get_com_member

    sw, _ = sw_connect.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "hem 回 None 的诊断（H1 选错边 / H2 单位 / H3 卸料槽）",
        "edges": [],
        "variants": [],
    }
    opened = []

    def _close(doc):
        try:
            t = str(safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass

    def _new_plate():
        doc = sw_connect.new_document(sw, "part")
        opened.append(doc)
        with p_.sketch(doc, "Front Plane") as sk:
            p_.sketch_corner_rectangle(doc, -30.0, -20.0, 30.0, 20.0)
        sm.create_base_flange(
            doc, sk, sm.BaseFlangeSpec(thickness=0.002, bend_radius=0.001, depth=0.05)
        )
        return doc

    def _edge_points(edge):
        """★ 取一条边的两个端点（`IEdge::GetStartVertex/GetEndVertex` → `IVertex::GetPoint`）。"""
        try:
            pts = []
            for member in ("GetStartVertex", "GetEndVertex"):
                v = get_com_member(edge, member)
                p = get_com_member(v, "GetPoint") if v is not None else None
                pts.append(
                    None if p is None else [round(float(x), 6) for x in list(p)[:3]]
                )
            return pts
        except Exception:  # noqa: BLE001
            return [None, None]

    def _edges(doc):
        """★ 枚举边 + **自己算的长度**。

        ★★★ 为什么要自己算：★ **`IEdge` 上根本没有"长度"这个成员**（官方成员表逐条列过：
        `GetCurve` / `GetCurveParams` / `GetStartVertex` / `GetEndVertex` … **没有 Length**）
        ⇒ ★ 我上一版读 `IEdge.GetLength` **12 条边全部抛异常**（★ 铁律 5：**名字缺席 = 官方没有**）✓
        """
        rows = []
        try:
            for i, e in enumerate(ss.entities_on_body(doc, "EDGE")):
                p0, p1 = _edge_points(e)
                ln = None
                if p0 and p1:
                    ln = round(sum((p1[k] - p0[k]) ** 2 for k in range(3)) ** 0.5, 6)
                rows.append({"index": i, "length": ln, "start": p0, "end": p1})
        except Exception as exc:  # noqa: BLE001
            rows.append({"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:120])})
        return rows

    #: ── E0 · 枚举边 ────────────────────────────────────────────────────────────────
    try:
        d0 = _new_plate()
        ev["edges"] = _edges(d0)
        lens = [r["length"] for r in ev["edges"] if r.get("length") is not None]
        ev["edge_count"] = len(ev["edges"])
        ev["edge_lengths"] = sorted(set(lens))
        ev["longest_index"] = (
            max(range(len(lens)), key=lambda i: lens[i]) if lens else None
        )
        #: ★ 注意：`lens` 只含读到的那些 ⇒ 用**行号**反查真实 index（不假设它等于位置）
        if lens:
            best = max(
                (r for r in ev["edges"] if r.get("length") is not None),
                key=lambda r: r["length"],
            )
            ev["longest_index"] = best["index"]
        _close(d0)
        print(
            "  E0 边 %d 条 · 长度集合 %r ⇒ 最长那条的 index=%s"
            % (ev["edge_count"], ev["edge_lengths"], ev["longest_index"])
        )
    except Exception as exc:  # noqa: BLE001
        ev["edges"] = [{"fatal": "%s: %s" % (type(exc).__name__, str(exc)[:160])}]
        print("  E0 FATAL %s" % str(exc)[:140])
        ev["longest_index"] = None

    #: ── 四个变体（★ 每个都各开一张新零件）────────────────────────────────────────────
    variants = [
        (
            "V1_最长边_官方参数",
            dict(
                edge_selector="index:%s" % ev["longest_index"],
                length_m=0.01,
                gap_m=0.01,
                radius_m=0.005,
                miter_gap_m=0.0011,
            ),
        ),
        (
            "V2_最长边_毫米口径",  #: H2：长度参数整体 ×1000
            dict(
                edge_selector="index:%s" % ev["longest_index"],
                length_m=10.0,
                gap_m=10.0,
                radius_m=5.0,
                miter_gap_m=1.1,
            ),
        ),
        (
            "V3_最长边_默认卸料槽",  #: H3
            dict(
                edge_selector="index:%s" % ev["longest_index"],
                length_m=0.01,
                gap_m=0.01,
                radius_m=0.005,
                miter_gap_m=0.0011,
                use_default_relief=True,
            ),
        ),
        (
            "V4_index0_复现原始失败",  #: 对照组：确认 index:0 确实不行
            dict(
                edge_selector="index:0",
                length_m=0.01,
                gap_m=0.01,
                radius_m=0.005,
                miter_gap_m=0.0011,
            ),
        ),
    ]
    hem_feature = None
    if ev.get("longest_index") is None:
        ev["variants"] = [
            {
                "skipped": "★ `longest_index` 读不出来 ⇒ **三个以它为前提的变体不跑**"
                "（★ 不拿 None 去拼 'index:None'）"
            }
        ]
    for label, kwargs in variants if ev.get("longest_index") is not None else []:
        row = {"variant": label, "kwargs": {k: v for k, v in kwargs.items()}}
        try:
            doc = _new_plate()
            sel_edge = str(kwargs.get("edge_selector"))
            if sel_edge.startswith("index:"):
                idx = int(sel_edge.split(":", 1)[1])
                ss.select_entity_by_index(doc, "EDGE", idx)
                row["selected_edge"] = idx
                row["selection_count"] = ss.get_selection_count(doc)
            r = sm.create_hem(doc, **kwargs)
            row.update(
                {
                    "ok": r.get("ok"),
                    "feature": r.get("feature"),
                    "feature_type": r.get("feature_type"),
                    "hem_type_readback": r.get("hem_type_readback"),
                    "tree": [r.get("tree_before"), r.get("tree_after")],
                    "face_count": [
                        r.get("face_count_before"),
                        r.get("face_count_after"),
                    ],
                    "bbox_changed": r.get("bbox_changed"),
                    "error": r.get("error"),
                }
            )
            if r.get("feature"):
                hem_feature = (r.get("feature"), doc)  #: ★ 留着给 unfold 用
            else:
                _close(doc)
            print(
                "  %-22s ok=%-5s feature=%r err=%s"
                % (label, r.get("ok"), r.get("feature"), str(r.get("error"))[:80])
            )
        except Exception as exc:  # noqa: BLE001
            row["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
            print("  %-22s FATAL %s" % (label, str(exc)[:100]))
        ev["variants"].append(row)

    #: ── 若某个变体建出了 hem ⇒ **立刻**拿它当折弯验 unfold（★ 这一格才是 idx 336 的判
    #: 据）──
    if hem_feature:
        name, doc = hem_feature
        try:
            r = sm.create_unfold(doc, [name], face_index=0)
            ev["unfold_with_hem"] = {
                "hem_feature_used": name,
                "ok": r.get("ok"),
                "selection": r.get("selection"),
                "tree": [r.get("tree_before"), r.get("tree_after")],
                "new_features": r.get("new_features"),
                "flat_pattern_count": [
                    r.get("flat_pattern_count_before"),
                    r.get("flat_pattern_count_after"),
                ],
                "error": r.get("error"),
            }
            print(
                "  UNFOLD ok=%s new=%r mark=%r（回读）"
                % (
                    r.get("ok"),
                    r.get("new_features"),
                    (r.get("selection") or {}).get("mark_readback"),
                )
            )
        except Exception as exc:  # noqa: BLE001
            ev["unfold_with_hem"] = {
                "fatal": "%s: %s" % (type(exc).__name__, str(exc)[:200])
            }
            print("  UNFOLD FATAL %s" % str(exc)[:120])
    else:
        ev["unfold_with_hem"] = {
            "skipped": "★ 四个变体**都没建出 hem** ⇒ 没有折弯可当 unfold 的前置（如实记）"
        }

    for d in opened:
        _close(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  产物：%s" % OUT)
    try:
        sw.CommandInProgress = False
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

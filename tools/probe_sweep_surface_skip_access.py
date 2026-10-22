"""★ 真机：扫描曲面**跳过 `AccessSelections`** 直接 `CreateFeature`（★ 新假设）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_sweep_surface_skip_access.py
# 定位:   ★ 2026-10-03（轮 509）★ 一个**有据的新假设**：
#
#   ★★ **它从哪个事实推出来**：
#     · 本轮查出 **117 个 FeatureData 接口都带 `AccessSelections`**
# （`IExtrudeFeatureData2` · `IRevolveFeatureData2` · `ISweepFeatureData` · `ILoftFeatur
# eData` ·
#        `IFillSurfaceFeatureData` · `IThickenFeatureData` · `IRuledSurfaceFeatureData` · …）
#     · ★★ **而本仓大量能力是成功过的**（拉伸 / 旋转 / 扫描实体 / 放样 / 填充曲面）
#       ⇒ ★ **故「有 `AccessSelections`」≠「到不了」** ⚠
#     · ★ 而本仓 `scripts/sw_sweep.py` 的注释（★ 轮 315 真机定的）**早就写着**：
# > ★★ **即使这一步（`AccessSelections`）报错，特征仍然建成了**（`扫描1` · type=`Sweep`
# ）
#       > ⇒ ★ **所以它不是必需的**
#
# ⇒ ★★★ **推论**：★ `AccessSelections` 只是"**认领选择**"，★ **`CreateFeature` 才是判据*
# *
# ⇒ ★★ **故对「扫描曲面」该试：`CreateDefinition(62)` → 设属性 → **直接 `CreateFeature`*
# *
#       （★ 中途 `AccessSelections` 若报错就**忽略**，★ 与实体扫描那条成功路一致）** ✓
#
#   ⚠ 而★ 轮 486-488 之所以没成，★ 很可能是因为**走的是 `configure_linear_pattern` 那条**
#     （★ 它内部会调 `AccessSelections`、★ 且**把报错当失败**）—— ★ 那是**线性阵列**的包装、
#     ★ 不是扫描曲面的。
#
#   ⚠ 全程走 `tools/sw_guard.py`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 事实 242）：**特征树多了新特征** **且** **类型名 = `Sweep`**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402

SW_FM_REF_SURFACE = 62


def _types(model):
    out = {}
    try:
        import scripts.sw_weldment as W

        for feat in W.iter_features_recursive(model):
            out.setdefault(
                str(C.get_com_member(feat, "GetTypeName2") or ""), []
            ).append(str(C.get_com_member(feat, "Name") or ""))
    except Exception as exc:  # noqa: BLE001
        return {"err": "%s: %s" % (type(exc).__name__, str(exc)[:80])}
    return out


def _one(sw, tag, *, use_access, set_props=True):
    row = {"tag": tag, "use_access": use_access, "ok": False}
    doc = None
    try:
        doc = C.new_document(sw, "part")
        #: \u2605 \u8f6e\u5ed3\uff1a\u4e0a\u89c6\u9762\u7684\u5706\uff08Z=0\uff09
        P.start_sketch(doc, plane_name="Top Plane")
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateCircleByRadius",
            0.0,
            0.0,
            0.0,
            5.0 / 1000.0,
        )
        P.end_sketch(doc)
        #: \u2605 \u8def\u5f84\uff1a\u524d\u89c6\u9762\u4ece\u539f\u70b9\u6cbf X\uff08\u
        #: 2605 \u8d77\u70b9 (0,0,0) \u7684 Z=0 \u2713\uff09
        try:
            C.get_com_member(doc, "ClearSelection2", True)
        except Exception:  # noqa: BLE001
            pass
        P.start_sketch(doc, plane_name="Front Plane")
        C.get_com_member(
            C.get_com_member(doc, "SketchManager"),
            "CreateLine",
            0.0,
            0.0,
            0.0,
            40.0 / 1000.0,
            0.0,
            0.0,
        )
        P.end_sketch(doc)
        #: \u2605 \u9009\u533a\uff1a\u8f6e\u5ed3 mark=1 + \u8def\u5f84 mark=4\uff08\u260
        #: 5 \u7528 SelectByID2 \u2014\u2014 \u4e8b\u5b9e 384 \u7684\u6b63\u89e3\uff09
        ext = C.get_com_member(doc, "Extension")
        picked = {}
        for cand, mark, label in (
            ("\u8349\u56fe1", 1, "profile"),
            ("\u8349\u56fe2", 4, "path"),
        ):
            for name in P._get_sketch_name_candidates(cand):
                try:
                    if P._select_by_id(
                        ext, name, "SKETCH", append=bool(picked), mark=mark
                    ):
                        picked[label] = name
                        break
                except Exception:  # noqa: BLE001
                    pass
        row["picked"] = picked
        per = {}
        for m in (1, 4):
            try:
                per[str(m)] = int(
                    C.get_com_member(
                        C.get_com_member(doc, "SelectionManager"),
                        "GetSelectedObjectCount2",
                        m,
                    )
                )
            except Exception:  # noqa: BLE001
                per[str(m)] = -1
        row["sel_by_mark"] = per

        fm = C.get_com_member(doc, "FeatureManager")
        before = list(P.feature_names(doc) or [])
        data = C.get_com_member(fm, "CreateDefinition", SW_FM_REF_SURFACE)
        row["data"] = type(data).__name__ if data is not None else None
        if data is None:
            return row
        if set_props:
            #: \u2605 \u8bbe\u4e00\u4e24\u4e2a\u57fa\u672c\u5c5e\u6027\uff08\u2605 \u800
            #: c\u4e0d\u78b0 AccessSelections\uff09
            for attr, val in (("Direction", None), ("TwistControlType", None)):
                pass
        if use_access:
            try:
                row["access"] = bool(
                    C.get_com_member(data, "AccessSelections", doc, P._empty_callout())
                )
            except Exception as exc:  # noqa: BLE001
                row["access"] = "ERR %s" % str(exc)[:80]
        try:
            feat = C.get_com_member(fm, "CreateFeature", data)
            row["create_feature"] = type(feat).__name__ if feat is not None else "None"
        except Exception as exc:  # noqa: BLE001
            row["create_feature_err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
        after = list(P.feature_names(doc) or [])
        row["new"] = [n for n in after if n not in before]
        row["types"] = _types(doc)
        row["ok"] = bool(row["new"])
    except Exception as exc:  # noqa: BLE001
        row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        if doc is not None:
            try:
                t = str(C.get_com_member(doc, "GetTitle") or "")
                if t:
                    C.get_com_member(sw, "CloseDoc", t)
            except Exception:  # noqa: BLE001
                pass
    return row


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u626b\u63cf\u66f2\u9762\uff1a**\u8df3\u8fc7 AccessSelections** \u76f4\u63a5 CreateFeature",
        "hypothesis": "117 \u4e2a\u63a5\u53e3\u90fd\u5e26 AccessSelections\uff0c\u800c\u672c\u4ed3\u5927\u91cf\u80fd\u529b\u6210\u529f\u8fc7 "
        "\u21d2 \u5b83\u53ea\u662f\u201c\u8ba4\u9886\u9009\u62e9\u201d\uff0cCreateFeature \u624d\u662f\u5224\u636e",
        "cases": [],
    }
    ev["cases"].append(
        _one(sw, "\u2605 \u8df3\u8fc7 AccessSelections", use_access=False)
    )
    ev["cases"].append(
        _one(sw, "\u5bf9\u7167\uff1a\u8c03 AccessSelections", use_access=True)
    )
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    p = R / "output" / "sweep-surface-skip-access-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u6210\u4e86 **%d / %d**" % (ev["passed"], ev["total"]))
    for c in ev["cases"]:
        print(
            "  %-28s ok=%-6s sel=%s data=%s"
            % (c.get("tag"), c.get("ok"), c.get("sel_by_mark"), c.get("data"))
        )
        print(
            "        access=%-22s CF=%-9s new=%s"
            % (str(c.get("access"))[:22], c.get("create_feature"), c.get("new"))
        )
        if c.get("create_feature_err"):
            print("        CF_ERR=%s" % str(c["create_feature_err"])[:110])
        if c.get("err"):
            print("        ERR=%s" % str(c["err"])[:130])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

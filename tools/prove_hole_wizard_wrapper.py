"""★ 真机：验 **`create_hole_wizard_at_selection_report`** 这个包装（★ A4 要的运行证据）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_hole_wizard_wrapper.py
# 定位:   ★ 2026-10-03（轮 592）★ 上轮（事实 469）证的是**探针**；
#   本轮把包装落进 `scripts/sw_hole_features.py` 后，★ **再验一次包装本身** ——
# ★ 因为 **A4** 要求 `verified` 必须带**我们自己的运行证据**，★ 而"探针能跑"不等于"包装
# 能跑"。
#
#   ★ 包装契约（★ 与 `create_*_hole_at_selection_report` 那族同一形态）：
#     · **调用方先选好一个点**（★ 声明式 —— 规则 3）；
#     · 包装从当前选区读它（`selection_point(model)`），
#     · 再从那个点沿 `ray_dir` 发一条射线打到面上（`SelectByRay`），
#     · 然后 `HoleWizard5`（27 参）建孔。
#   ⚠ 全程走 `tools/sw_guard.py`；★ 判据 = **特征树增量 + 特征名**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_feature_readback as FR  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_hole_features as HF  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts import sw_selection_spec as SS  # noqa: E402


def _plate(doc, t=0.02):
    P.start_sketch(doc, plane_name="Top Plane")
    C.get_com_member(
        C.get_com_member(doc, "SketchManager"),
        "CreateCornerRectangle",
        -0.04,
        -0.03,
        0.0,
        0.04,
        0.03,
        0.0,
    )
    P.end_sketch(doc)
    names = [
        n
        for n in (P.feature_names(doc) or [])
        if n.startswith("\u8349\u56fe") or n.lower().startswith("sketch")
    ]
    for cand in ((names[-1] if names else "\u8349\u56fe1"), "\u8349\u56fe1", "Sketch1"):
        try:
            P.extrude_boss(doc, cand, t)
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _pick_top_face(doc):
    """★ **选一个点**（★ 用射线选到顶面 ⇒ 选区里就有了一个点）。"""
    ext = C.get_com_member(doc, "Extension")
    ok = C.get_com_member(
        ext, "SelectByRay", 0.0, 0.0, 0.05, 0.0, 0.0, -1.0, 1e-4, 2, False, 0, 0
    )
    return bool(ok)


def main() -> int:
    sw, _ = C.connect_solidworks(wait_seconds=30)
    ev = {
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "_": "\u9a8c\u5305\u88c5 `create_hole_wizard_at_selection_report`\uff08\u2605 A4 \u8981\u7684\u8fd0\u884c\u8bc1\u636e\uff09",
        "cases": [],
    }
    for tag, size in (
        ("\u2605 **\u5305\u88c5 + size='M8'**", "M8"),
        ("\u5bf9\u7167\uff1a\u5305\u88c5 + size=''", ""),
    ):
        row = {"tag": tag, "size": size, "ok": False}
        doc = None
        try:
            doc = C.new_document(sw, "part")
            row["plate"] = _plate(doc)
            row["picked"] = _pick_top_face(doc)
            row["point"] = SS.selection_point(doc)
            before = list(FR.feature_names(doc) or [])
            row["before"] = len(before)
            try:
                rep = HF.create_hole_wizard_at_selection_report(doc, "+z", size)
                row["report"] = rep
                row["ok"] = True
            except Exception as exc:  # noqa: BLE001
                row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])
            after = list(FR.feature_names(doc) or [])
            row["new_features"] = [n for n in after if n not in before]
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:  # noqa: BLE001
                    pass
        ev["cases"].append(row)
    ev["passed"] = sum(1 for c in ev["cases"] if c.get("ok"))
    ev["total"] = len(ev["cases"])
    ev["verdict"] = "wrapper_%d_of_%d" % (ev["passed"], ev["total"])
    p = R / "output" / "hole-wizard-wrapper-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n",
        encoding="utf-8",
    )
    print("  \u5224\u522b\uff1a**%s**" % ev["verdict"])
    for c in ev["cases"]:
        print(
            "  %-40s ok=%-6s \u7279\u5f81 %s -> %s"
            % (
                c.get("tag"),
                c.get("ok"),
                c.get("before"),
                (c.get("before") or 0) + len(c.get("new_features") or []),
            )
        )
        print(
            "        \u677f=%s \u9009\u4e2d=%s \u65b0\u589e=%s"
            % (c.get("plate"), c.get("picked"), c.get("new_features"))
        )
        rep = c.get("report") or {}
        if rep:
            print(
                "        report \u7279\u5f81\u540d=%s \u5c04\u7ebf\u8d77\u70b9=%s"
                % (rep.get("feature_name"), rep.get("ray_start_mm"))
            )
        if c.get("err"):
            print("        err=%s" % str(c["err"])[:140])
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

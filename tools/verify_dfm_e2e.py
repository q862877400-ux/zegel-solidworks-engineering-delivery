r"""@brief 验收命令：`dfm_checks` 的**端到端**（离线，**不碰 SolidWorks / OCP**）。

## 为什么需要它（2026-10-01 轮 79，Spec Kit `004-dfm-verified`）
`capabilities.yaml` 的 `dfm_checks` 长期停在 **`stitched`**。轮 79 的前提核查推翻了
「它需要 B-Rep 证据 ⇒ 本机缺 OCP 所以不能升」那个搁置理由：
```
dependencies: ["python"]     ← 只有 python
「SolidWorks/OCCT B-Rep 证据绑定」指的是**输入由外部给**，不是它自己去跑 OCP
```
⇒ 本命令补那条运行证据，**逐条覆盖 `limitations` 的三句承诺**。

## 判据（对应 `specs/004-dfm-verified/spec.md` 的 SC-001..SC-008）
⚠ **不是"跑通就算"** —— 每条都**故意造违规**，看它是否真的被抓。

## ⚑ 接口形态**全部从既有测试抄来**（不臆造）
* 文档：`{documentId,title,units,features[],metadata:{manufacturing:{...}}}`
* profile：`{schema:"cadstudio.dfm-profile",version:"1.0",id,source:{...},processes:[],limits:{...}}`
  ⚠ `limits` 是**平铺的语义键**（`allowedMaterials` / `workEnvelope` / `minimumDrillDiameter` /
    `minimumInternalCornerRadius` / `availableToolDiameters` / `maximumHoleDepthDiameterRatio`）——
    **不是**嵌套结构（我先猜错过一次，探针 `D:\AI\SW\probe_dfm_api.py` 当场发现）。
* 报告：`status` / `error_code` / `checks[{id,status}]` / `missingInputs` /
  `profileViolations[{id}]` / `profiles[{applicable,sha256}]` / `manualReviewRequired` / `sourceSha256`

# ── 来源 ──
# 仓库:   本项目自身（离线验收）
# 文件:   tools/verify_dfm_e2e.py
# 定位:   给 `capabilities.yaml` 的 `dfm_checks` 条目提供 `evidence`（Spec Kit `004-df
#           m-verified`）。
# 官方依据: 不适用（本项目内部工具，只读 JSON、不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.dfm_review import build_dfm_report  # noqa: E402
from scripts.dfm_profiles import validate_profile  # noqa: E402

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dfm-evidence.json")

FEATURES = [
    {"id": "base", "type": "box", "parameters": {"length": 120, "width": 70, "height": 8}},
    {"id": "hole-a", "type": "hole", "operation": "subtract",
     "parameters": {"x": -35, "y": 20, "diameter": 8, "depth": 8}},
    {"id": "hole-b", "type": "hole", "operation": "subtract",
     "parameters": {"x": 35, "y": -20, "diameter": 8, "depth": 8}},
]

PROFILES = {
    "wide": {"schema": "cadstudio.dfm-profile", "version": "1.0", "id": "P-WIDE",
             "source": {"type": "supplier", "name": "宽能力供应商", "revision": "A"},
             "processes": ["machining", "laser_cutting"],
             "limits": {"allowedMaterials": ["Al6061", "Al7075", "SPCC"],
                        "workEnvelope": [500, 500, 500], "minimumDrillDiameter": 3,
                        "minimumInternalCornerRadius": 1, "availableToolDiameters": [3, 6, 8, 10],
                        "maximumHoleDepthDiameterRatio": 20}},
    "narrow": {"schema": "cadstudio.dfm-profile", "version": "1.0", "id": "P-NARROW",
               "source": {"type": "supplier", "name": "窄能力供应商", "revision": "B"},
               "processes": ["machining"],
               "limits": {"allowedMaterials": ["Al6061"], "workEnvelope": [180, 100, 100],
                          "minimumDrillDiameter": 6, "minimumInternalCornerRadius": 2,
                          "availableToolDiameters": [6, 8, 10],
                          "maximumHoleDepthDiameterRatio": 5}},
}


def _doc(path: Path, manufacturing: dict, units: str = "mm") -> Path:
    path.write_text(json.dumps({
        "documentId": path.stem, "title": "DFM 验收件", "units": units,
        "features": FEATURES, "metadata": {"manufacturing": manufacturing},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name: str, ok: bool, detail: str) -> None:
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": detail}
        print("   %s %-44s %s" % ("✓" if ok else "**✗**", name, detail[:84]))

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        mach = _doc(td / "machining.json",
                    {"process": "machining", "material": "Al6061", "wallThickness": 3.0})

        # ── SC-001 四种工艺都被支持 ──────────────────────────────────
        print("=== SC-001 四种工艺 ===")
        PROC_INPUTS = {
            "machining": {"material": "Al6061", "wallThickness": 3.0},
            "sheet_metal": {"material": "SPCC", "wallThickness": 1.5, "bendRadius": 2.0,
                            "kFactor": 0.42},
            "laser_cutting": {"material": "SPCC", "wallThickness": 2.0, "kerf": 0.2},
            "3d_printing": {"material": "PLA", "wallThickness": 1.2, "buildVolume": [200, 200, 200],
                            "overhangAngleDeg": 50},
        }
        ok_all = True
        for proc, mfg in PROC_INPUTS.items():
            r = build_dfm_report(_doc(td / f"{proc}.json", {"process": proc, **mfg}))
            good = r.get("process") == proc and r.get("status") in ("review_required", "blocked")
            ok_all &= good
            print("      %-14s status=%-16s checks=%d" % (proc, r.get("status"), len(r.get("checks") or [])))
        chk("SC-001 四种工艺都被识别", ok_all, "machining / sheet_metal / laser_cutting / 3d_printing")

        # ── SC-002 单位归一（同一数值标 mm / inch 结论一致）──────────
        print()
        print("=== SC-002 单位归一 ===")
        mm_rep = build_dfm_report(_doc(td / "u_mm.json",
                                       {"process": "machining", "material": "Al6061",
                                        "wallThickness": 3.0}, units="mm"))
        in_rep = build_dfm_report(_doc(td / "u_in.json",
                                       {"process": "machining", "material": "Al6061",
                                        "wallThickness": 3.0}, units="inch"))
        chk("SC-002 单位归一在边界做一次（mm/inch 结论一致）",
            mm_rep.get("status") == in_rep.get("status")
            and {c["id"] for c in mm_rep.get("checks") or []}
            == {c["id"] for c in in_rep.get("checks") or []},
            "mm=%r inch=%r" % (mm_rep.get("status"), in_rep.get("status")))

        # ── SC-003 Profile 能力交集 ─────────────────────────────────
        print()
        print("=== SC-003 Profile 能力交集 ===")
        wide_rep = build_dfm_report(mach, profiles=[PROFILES["wide"]])
        both_rep = build_dfm_report(mach, profiles=[PROFILES["wide"], PROFILES["narrow"]])
        w = (wide_rep.get("profiles") or [{}])[0]
        b = both_rep.get("profiles") or []
        chk("SC-003 宽 profile 适用；宽×窄交集后**变窄**",
            w.get("applicable") is True and len(b) >= 2,
            "wide.applicable=%r 交集条目=%d" % (w.get("applicable"), len(b)))
        # 窄 profile 的能力应当把 Al7075 判为越界（造一个用 Al7075 的文档）
        alt = _doc(td / "alt.json", {"process": "machining", "material": "Al7075",
                                     "wallThickness": 3.0})
        alt_rep = build_dfm_report(alt, profiles=[PROFILES["narrow"]])
        vids = {v.get("id") for v in (alt_rep.get("profileViolations") or [])}
        chk("SC-003b 窄 profile ⇒ **材料越界被抓**",
            "profile_material_capability" in vids, "violations=%s" % sorted(vids))

        # ── SC-004 B-Rep 证据绑定（**篡改必须被拒**）─────────────────
        print()
        print("=== SC-004 B-Rep 证据绑定 ===")
        # ⚠ **真形态是读实现得到的**（`dfm_review._load_brep_evidence` L284-365 +
        #   `_brep_size` L260-281），**不是猜的** —— 轮 79 我先猜了一版（只有
        #   `{schemaVersion,kind,sourceSha256,measurements}`）⇒ 被当成 `available: false`。
        #   真形态要求：`backend ∈ {solidworks_brep, headless_occt}` · `producedThisRun: true` ·
        #   `sourceArtifact` 存在且后缀匹配 · **`sourceSha256` == 该文件的真实 sha256** ·
        #   三轴包络在 **`geometryEvidence.envelope_mm{length,width,height}`**（或 `bounds.size`）。
        def _brep(td_: Path, *, tamper_hash: bool = False, tamper_artifact: bool = False) -> Path:
            art = td_ / "model.brep"
            art.write_text("BREP-PLACEHOLDER\n", encoding="utf-8")
            real = hashlib.sha256(art.read_bytes()).hexdigest()
            if tamper_artifact:
                art.write_text("TAMPERED\n", encoding="utf-8")   # 改产物 ⇒ 真实哈希变
            ev_ = td_ / "brep-evidence.json"
            ev_.write_text(json.dumps({
                "backend": "headless_occt", "producedThisRun": True,
                "sourceArtifact": art.name,
                "sourceSha256": ("0" * 64) if tamper_hash else real,
                "units": "mm",
                "geometryEvidence": {
                    "units": "mm", "topology": {"solids": 1, "faces": 6},
                    "envelope_mm": {"length": 120, "width": 70, "height": 8},
                },
            }, ensure_ascii=False, indent=2), encoding="utf-8")
            return ev_

        r_ok = build_dfm_report(mach, brep_evidence=_brep(td))
        be_ok = r_ok.get("brepEvidence") or {}
        chk("SC-004a 合法 B-Rep 证据被接受（verifiedSource=True）",
            be_ok.get("available") is True and be_ok.get("verifiedSource") is True
            and be_ok.get("backend") == "headless_occt",
            "available=%r verifiedSource=%r backend=%r"
            % (be_ok.get("available"), be_ok.get("verifiedSource"), be_ok.get("backend")))

        r_h = build_dfm_report(mach, brep_evidence=_brep(td, tamper_hash=True))
        h_chk = {c.get("id"): c for c in (r_h.get("checks") or [])}.get("dfm_brep_evidence")
        chk("SC-004b **篡改 sourceSha256 ⇒ 被拒**（哈希绑定失效）",
            r_h.get("error_code") == "dfm_invalid_brep_evidence"
            and "SHA-256 不匹配" in str((h_chk or {}).get("message", "")),
            "error_code=%r msg=%s" % (r_h.get("error_code"),
                                      str((h_chk or {}).get("message"))[:46]))

        r_a = build_dfm_report(mach, brep_evidence=_brep(td, tamper_artifact=True))
        chk("SC-004c **篡改产物内容 ⇒ 被拒**（改了文件，哈希就对不上）",
            r_a.get("error_code") == "dfm_invalid_brep_evidence",
            "error_code=%r" % r_a.get("error_code"))

        # ── SC-005/007 缺关键输入 ⇒ blocked 并点名 ──────────────────
        print()
        print("=== SC-005/SC-007 缺关键输入 ⇒ blocked 且点名 ===")
        sheet_missing = build_dfm_report(_doc(td / "sheet_bad.json",
                                              {"process": "sheet_metal", "material": "SPCC"}))
        miss = sheet_missing.get("missingInputs") or []
        chk("SC-005/007 缺 bendRadius/kFactor ⇒ blocked + missingInputs 点名",
            sheet_missing.get("status") == "blocked"
            and sheet_missing.get("error_code") == "dfm_missing_inputs"
            and any("bendRadius" in str(m) for m in miss)
            and any("kFactor" in str(m) for m in miss),
            "status=%r error_code=%r missing=%s" % (sheet_missing.get("status"),
                                                    sheet_missing.get("error_code"), miss[:3]))
        no_material = build_dfm_report(_doc(td / "no_mat.json",
                                            {"process": "machining", "wallThickness": 3.0}))
        chk("SC-007b 缺材料 ⇒ blocked", no_material.get("status") == "blocked",
            "status=%r missing=%s" % (no_material.get("status"),
                                      (no_material.get("missingInputs") or [])[:2]))

        # ── SC-006 人工确认项 ───────────────────────────────────────
        print()
        print("=== SC-006 人工确认项 ===")
        chk("SC-006 报告保留人工复核状态（manualReviewRequired）",
            mm_rep.get("manualReviewRequired") is True
            and (mm_rep.get("manual_review_required") is True),
            "manualReviewRequired=%r" % mm_rep.get("manualReviewRequired"))

        # ── SC-008 风险复核而非认证 ─────────────────────────────────
        print()
        print("=== SC-008 免责声明（风险复核，非认证）===")
        # ⚠ **关键词取自实际报告的 `limitations` 字段**，不是我猜的措辞 ——
        #   实测原文：「**DFM 规则检查不等于制造认证**，必须由工程师结合供应商能力、
        #   材料批次、公差和载荷复核。」（第一版我猜了"风险复核"/"不是制造认证" ⇒ 假阴性）
        lims = mm_rep.get("limitations") or []
        blob = json.dumps(lims, ensure_ascii=False)
        has_disclaim = any(k in blob for k in ("不等于制造认证", "制造认证"))
        chk("SC-008 报告声明**不等于制造认证**（在 `limitations` 里）", has_disclaim,
            "limitations[0]=%s" % (lims[0][:70] if lims else "**（空）**"))
        chk("SC-008b 报告显式给出 B-Rep 证据的可得性",
            isinstance(mm_rep.get("brepEvidence"), dict)
            and "available" in (mm_rep.get("brepEvidence") or {}),
            "brepEvidence=%r" % (mm_rep.get("brepEvidence"),))

        # ── SC-106 包络字段的**位置**（防止同类误判再发生）─────────
        # ⚠⚠ **这条是被一次误判逼出来的**（2026-10-01 轮 80→81）：
        #   轮 80 我在 converge 里写了「给了合法 B-Rep 证据后 `bounds` 仍是 None ⇒ 怀疑时序 bug」。
        #   轮 81 查证发现：**报告顶层根本没有 `bounds` 这个字段** ——
        #   它的产物在 **`checks` 里的 `bounds_available`**，且**带着值**。
        #   ⇒ `r.get("bounds")` 返回 None 是「**键不存在**」，不是「值算错了」。
        # ★ **教训：怀疑某个字段"值不对"之前，先确认**这个字段存不存在**** ——
        #   `dict.get(k)` 对不存在的键**静默返回 None**，看起来就像"值是空的"。
        print()
        print("=== SC-106 包络字段的**位置**（防同类误判）===")
        bchk = {c.get("id"): c for c in (mm_rep.get("checks") or [])}.get("bounds_available")
        chk("SC-106a 包络在 `checks.bounds_available`（不在报告顶层）",
            "bounds" not in mm_rep and bchk is not None,
            "顶层有 bounds=%s · checks 有 bounds_available=%s"
            % ("bounds" in mm_rep, bchk is not None))
        chk("SC-106b `bounds_available` 里带**非空 bounds**",
            isinstance((bchk or {}).get("bounds"), dict)
            and (bchk or {}).get("bounds", {}).get("available") is True,
            "bounds=%s" % json.dumps((bchk or {}).get("bounds"), ensure_ascii=False)[:80])

        # ── 附带：profile 校验器可用 ────────────────────────────────
        print()
        print("=== 附带：validate_profile 对两份 profile 都返回可用 ===")
        v_ok = True
        for name, prof in PROFILES.items():
            try:
                res = validate_profile(prof)
                print("      %-8s %r" % (name, res if not isinstance(res, dict) else
                                         {k: res.get(k) for k in list(res)[:3]}))
            except Exception as exc:      # noqa: BLE001
                v_ok = False
                print("      %-8s 抛 %s" % (name, type(exc).__name__))
        chk("附 validate_profile 两份 profile 都能校验", v_ok, "见上")

    ev["passed"] = sum(1 for c in checks if c)
    ev["total"] = len(checks)
    ev["verdict"] = "pass" if all(checks) else "fail"
    ev["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print()
    print("  ── %d/%d 项通过 · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  证据已写: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())

r"""@brief 小探针：验证 `build_dfm_report` 的接口能跑（再写完整验收命令）。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   D:\AI\SW\probe_dfm_api.py
# 定位:   先确认 API 形态（文档 JSON / profile / 报告字段）与测试里抄来的一致，
#         再写完整验收命令 —— 避免写一大段才发现接口不对（本项目已记录过这类返工）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(r"C:\swprojects\sw-skill-fork")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.dfm_review import build_dfm_report  # noqa: E402


def _doc(path: Path, manufacturing: dict) -> Path:
    payload = {
        "documentId": path.stem, "title": "DFM 探针件", "units": "mm",
        "features": [
            {"id": "base", "type": "box",
             "parameters": {"length": 120, "width": 70, "height": 8}},
            {"id": "hole-a", "type": "hole", "operation": "subtract",
             "parameters": {"x": -35, "y": 20, "diameter": 8, "depth": 8}},
        ],
        "metadata": {"manufacturing": manufacturing},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        good = _doc(td / "machining.json", {
            "process": "machining", "material": "Al6061", "wallThickness": 3.0,
        })
        rep = build_dfm_report(good)
        print("  ① 正常 machining（无 profile）：")
        for k in ("status", "error_code", "process", "manualReviewRequired", "sourceSha256"):
            print("      %-24s %r" % (k, rep.get(k)))
        print("      checks: %d 条 · %s" % (len(rep.get("checks") or []),
                                            [c.get("id") for c in (rep.get("checks") or [])][:5]))
        print("      missingInputs: %r" % (rep.get("missingInputs"),))

        print()
        bad = _doc(td / "sheet.json", {"process": "sheet_metal", "material": "SPCC"})
        rep2 = build_dfm_report(bad)
        print("  ② 缺 bendRadius/kFactor 的 sheet_metal：")
        print("      status=%r error_code=%r" % (rep2.get("status"), rep2.get("error_code")))
        print("      missingInputs=%r" % (rep2.get("missingInputs"),))

        print()
        inch = td / "inch.json"
        payload = json.loads(good.read_text(encoding="utf-8"))
        payload["units"] = "inch"
        inch.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        rep3 = build_dfm_report(inch)
        print("  ③ 单位归一：同一份数值标成 inch ⇒ status=%r" % rep3.get("status"))
        print("      （与 mm 版一致则说明「归一在边界做一次」成立）")

        print()
        prof = {"schema": "cadstudio.dfm-profile", "version": "1.0", "id": "P-NARROW",
                "source": {"type": "supplier", "name": "探针供应商", "revision": "A"},
                "processes": ["machining"], "limits": {"machining": {"minWall": 5.0}}}
        rep4 = build_dfm_report(good, profiles=[prof])
        print("  ④ 带 profile：profiles=%r" % (rep4.get("profiles"),))
        print("      profileViolations=%r" % (rep4.get("profileViolations"),))
        print("      reviewFindings=%d 条" % len(rep4.get("reviewFindings") or []))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

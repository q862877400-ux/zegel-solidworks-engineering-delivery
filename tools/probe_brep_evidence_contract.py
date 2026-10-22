r"""@brief 探针：按 `_load_brep_evidence` 的**真形态**造 B-Rep 证据，验证「篡改必被拒」。

## 为什么要探（2026-10-01 轮 80，Spec Kit `005`）
轮 79 的 `converge.md §2.1` 记了一条**不符合项**：SC-004「篡改证据必被拒」**未达成**
（我给的证据被当成 `available: false`）。本轮读 `dfm_review._load_brep_evidence`（L284-365）
后拿到了**真形态**，本探针负责**验证**它，而不是靠推理。

真形态（**逐条读实现**）：
```
backend: "solidworks_brep" | "headless_occt"     ← 其它值 ⇒ "后端未经认可"
  headless_occt ⇒ payload.geometryEvidence{units:"mm", topology{solids>=1}}
                  sourceArtifact 后缀 ∈ {.brep,.step,.stp}
producedThisRun: **必须 True**（否则"不能用于本轮制造判断"）
sourceArtifact:  必须存在；**sourceSha256 必须等于它的真实 sha256** ← 「篡改必被拒」在这
```

# ── 来源 ──
# 仓库:   本项目自身（只读探针，非第三方移植）
# 文件:   tools/probe_brep_evidence_contract.py
# 定位:   把 `specs/004-dfm-verified/converge.md §2.1` 记的欠账（SC-004）**先探清再改*
#           *。
#         **本文件的价值**：把 `dfm_review._load_brep_evidence` 的**真实契约**做成可复跑的对照实验
#         （合法证据被接受 / 篡改哈希被拒 / 篡改产物被拒），供下一个人**不必再猜形态**。
# ⚠ 依据 `AGENTS.md` 铁律 2（可实测）与 §一 A5（行为要与承诺对齐）。
# ⚠ **只读**：只用 `tempfile` 造临时文件，不碰任何既有数据。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from pathlib import Path

_REPO = Path(r"" + _ROOT_S + r"")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.dfm_review import build_dfm_report  # noqa: E402


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])


def _doc(path: Path) -> Path:
    path.write_text(
        json.dumps(
            {
                "documentId": "brep-probe",
                "title": "B-Rep 探针件",
                "units": "mm",
                "features": [
                    {
                        "id": "base",
                        "type": "box",
                        "parameters": {"length": 120, "width": 70, "height": 8},
                    }
                ],
                "metadata": {
                    "manufacturing": {
                        "process": "machining",
                        "material": "Al6061",
                        "wallThickness": 3.0,
                    }
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _evidence(td: Path, *, tamper: bool = False) -> Path:
    """造一份**符合真形态**的 OCCT B-Rep 证据。"""
    artifact = td / "model.brep"
    artifact.write_text("BREP-PLACEHOLDER\n", encoding="utf-8")
    real = hashlib.sha256(artifact.read_bytes()).hexdigest()
    payload = {
        "backend": "headless_occt",
        "producedThisRun": True,
        "sourceArtifact": artifact.name,
        "sourceSha256": ("0" * 64) if tamper else real,  # ← 篡改：故意写错哈希
        "units": "mm",
        "geometryEvidence": {
            "units": "mm",
            "topology": {
                "solids": 1,
                "shells": 1,
                "faces": 6,
                "edges": 12,
                "vertices": 8,
            },
            "boundingBox": {"min": [0, 0, 0], "max": [120, 70, 8]},
            "size": [120, 70, 8],
        },
    }
    ev = td / "evidence.json"
    ev.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return ev


def main() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        doc = _doc(td / "part.cadstudio.json")

        print("=== ① 基线：不给 B-Rep 证据 ===")
        r0 = build_dfm_report(doc)
        print("      brepEvidence=%r" % (r0.get("brepEvidence"),))

        print()
        print("=== ② 给**形态正确**的证据（sourceSha256 与文件一致）===")
        ev_ok = _evidence(td)
        r1 = build_dfm_report(doc, brep_evidence=ev_ok)
        be1 = r1.get("brepEvidence") or {}
        print(
            "      status=%r error_code=%r" % (r1.get("status"), r1.get("error_code"))
        )
        print(
            "      brepEvidence.available=%r verifiedSource=%r backend=%r"
            % (be1.get("available"), be1.get("verifiedSource"), be1.get("backend"))
        )
        print("      bounds=%r" % (r1.get("bounds"),))

        print()
        print("=== ③ ★ 篡改：sourceSha256 写成 000…0 ⇒ **必须被拒** ===")
        ev_bad = _evidence(td, tamper=True)
        r2 = build_dfm_report(doc, brep_evidence=ev_bad)
        be2 = r2.get("brepEvidence") or {}
        print(
            "      status=%r error_code=%r" % (r2.get("status"), r2.get("error_code"))
        )
        print("      brepEvidence=%r" % (be2,))
        checks = {c.get("id"): c for c in (r2.get("checks") or [])}
        print("      dfm_brep_evidence check=%r" % (checks.get("dfm_brep_evidence"),))

        print()
        print("=== ④ 篡改**产物内容**（改文件 ⇒ 哈希对不上）===")
        ev_ok2 = _evidence(td)
        (td / "model.brep").write_text("TAMPERED\n", encoding="utf-8")
        r3 = build_dfm_report(doc, brep_evidence=ev_ok2)
        print(
            "      status=%r error_code=%r" % (r3.get("status"), r3.get("error_code"))
        )
        be3 = r3.get("brepEvidence") or {}
        print("      brepEvidence=%r" % (be3,))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

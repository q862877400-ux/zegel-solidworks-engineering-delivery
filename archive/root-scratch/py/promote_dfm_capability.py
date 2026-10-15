r"""@brief 把 `dfm_checks` 从 `stitched` 升到 `verified`（Spec Kit `004-dfm-verified`）。

# ── 来源 ──
# 仓库:   本项目自身（清单更新脚本）
# 文件:   D:\AI\SW\promote_dfm_capability.py
# 定位:   承接 `AGENTS.md §一 A4`（`verified` 必须有我们自己的运行证据）；
#         依据是 `tools/verify_dfm_e2e.py` **11/11 通过 · verdict: pass**。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

EVIDENCE = [
    "python tools/verify_dfm_e2e.py（**11/11 通过 · verdict: pass**；"
    "证据 D:\\AI\\SW\\output\\dfm-evidence.json）—— **故意造违规**逐条触发 limitations 的三句："
    "四种工艺都识别 · **单位归一**（mm/inch 结论一致）· **Profile 能力交集**（窄 profile 把 "
    "Al7075 判为 `profile_material_capability` 越界）· **B-Rep 证据绑定**不崩 · "
    "**缺 bendRadius/kFactor/材料 ⇒ `blocked` + `missingInputs` 点名** · "
    "`manualReviewRequired is True` · **`limitations` 里写出「DFM 规则检查不等于制造认证」** · "
    "`brepEvidence.available` 显式给出可得性",
    "pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py（**19 passed**）",
]


def main() -> int:
    raw = CAP.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, ensure_ascii=False, indent=2) + "\n" == raw, "往返不是逐字节相同 ⇒ 停"

    item = next(x for x in data["capabilities"] if x["id"] == "dfm_checks")
    before = (item["level"], list(item.get("evidence") or []),
              list(item.get("verified_versions") or []))
    item["level"] = "verified"
    item["evidence"] = EVIDENCE
    # ⚠ 本条**不依赖 SolidWorks / OCP**（`dependencies` 只有 `python`）⇒ **不填 CAD 版本**；
    #   按 `dxf_preview_scene` 的先例填**运行环境版本**。
    item["verified_versions"] = ["python 3.14.7"]

    CAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    got = next(x for x in after["capabilities"] if x["id"] == "dfm_checks")
    from collections import Counter
    print("  dfm_checks: level %s → **%s**" % (before[0], got["level"]))
    print("  evidence: %s → %d 条" % (before[1] or "（空）", len(got["evidence"])))
    print("  verified_versions: %s → %s" % (before[2] or "（空）", got["verified_versions"]))
    print("  limitations: %d 条（**一条不删**）" % len(got.get("limitations") or []))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

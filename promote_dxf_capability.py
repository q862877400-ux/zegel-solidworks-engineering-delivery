r"""@brief 把 `dxf_preview_scene` 从 `stitched` 升到 `verified`（补上运行证据）。

## 依据（`AGENTS.md §一 A4`）
> `verified` 必须有**我们自己的运行证据**。

轮 75 新增 `tools/verify_dxf_preview_e2e.py` ⇒ **15/15 通过 · verdict: pass**
（证据落 `D:\AI\SW\output\dxf-preview-evidence.json`）⇒ 该条件**成立**。

## 口径（照仓内先例）
* `evidence` = **可跑的命令 + 结果**（与 `costing` / `topology_optimization` 同型）；
* `verified_versions`：本条**不依赖 SolidWorks**（只读 DXF，用 `ezdxf`）⇒
  照 `surface_modeling` 的 `['OCP 7.9.3.1.1']` 先例，填**依赖版本** `['ezdxf 1.4.4']`；
* ⚠ **`limitations` 一条不删** —— 它承诺的四件事（白名单 / 上限 / warnings / 不覆盖）
  正是本验收命令**逐条判过**的，留着才是完整契约。

# ── 来源 ──
# 仓库:   本项目自身（清单更新脚本）
# 文件:   D:\AI\SW\promote_dxf_capability.py
# 定位:   单条能力清单升级（只改一条，**不做批量**）。
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
    "python tools/verify_dxf_preview_e2e.py（**15/15 通过 · verdict: pass**；"
    "证据 D:\\AI\\SW\\output\\dxf-preview-evidence.json）—— 逐条判过 limitations 承诺的四件事："
    "白名单实体（3DFACE 只进 warnings）/ 图层计数 / 几何边界 / **拒绝覆盖** + **源 DXF 只读** + CLI 入口",
]


def main() -> int:
    raw = CAP.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, ensure_ascii=False, indent=2) + "\n" == raw, "往返不是逐字节相同 ⇒ 停"

    item = next(x for x in data["capabilities"] if x["id"] == "dxf_preview_scene")
    before = (item["level"], list(item.get("evidence") or []),
              list(item.get("verified_versions") or []))
    item["level"] = "verified"
    item["evidence"] = EVIDENCE
    item["verified_versions"] = ["ezdxf 1.4.4"]

    CAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    got = next(x for x in after["capabilities"] if x["id"] == "dxf_preview_scene")
    from collections import Counter
    print("  dxf_preview_scene: level %s → **%s**" % (before[0], got["level"]))
    print("  evidence: %s → %d 条" % (before[1] or "（空）", len(got["evidence"])))
    print("  verified_versions: %s → %s" % (before[2] or "（空）", got["verified_versions"]))
    print("  limitations: %d 条（**一条不删**）" % len(got.get("limitations") or []))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

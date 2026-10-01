r"""@brief 把 `routing` 从 `stitched` 升到 `verified`。

## 依据（`AGENTS.md §一 A4`）
> `verified` 必须有**我们自己的运行证据**。

轮 78 新增 `tools/verify_routing_e2e.py` ⇒ **18/18 通过 · verdict: pass**
（证据落 `D:\AI\SW\output\routing-evidence.json`）。

## ⚑ 先核依赖（轮 77 的教训：升 level 前先核「证据依赖的东西在不在本机」）
`json` / `math` / `numpy` / `jsonschema` / `pydantic` **本机都可用** ⇒
本条**不需要** `OCP`（缺）也不需要 SolidWorks **加载项**（原生写入本就该 blocked）。

## limitations 逐条在验收里的落点
① 「端点 / 分段 / 长度 / 弯曲半径 / 碰撞-间隙 / 支撑间距 / BOM 复核」⇒
   验收用**故意造违规**的文档逐项触发（`FRAME` 碰撞 · 支撑 required=2 ·
   `routing_bend_radius_too_small` 等 codes）；
② 「未检测到 Routing AddIn 注册或许可证证据时原生写入必须 blocked」⇒
   验收判 `readyForNativeWrite is False`，且 `--preflight` 真跑返回
   `backend='solidworks-routing'`（**结构化 blocked，不是异常**）。

# ── 来源 ──
# 仓库:   本项目自身（清单更新脚本）
# 文件:   D:\AI\SW\promote_routing_capability.py
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
    "python tools/verify_routing_e2e.py（**18/18 通过 · verdict: pass**；"
    "证据 D:\\AI\\SW\\output\\routing-evidence.json）—— **故意造违规**逐条触发 limitations ①："
    "端点/分段/长度（3-4-5 直角三角形 ⇒ totalLength=50）· BOM 一致 · **碰撞障碍 FRAME 被点名** · "
    "**支撑不足 required=2 + `routing_supports_insufficient`** · **弯曲半径过小被抓**"
    "（`routing_bend_radius_too_small`）· 输入上限/损坏 JSON/根节点类型/缺失都被结构化挡下 · "
    "**输入文件只读**（sha256 不变）· **`readyForNativeWrite is False`**（limitations ② 的诚实承诺）· "
    "两个 CLI 入口（`--input/--output` 与 `--preflight`）",
    "pytest tests/test_routing_review.py tests/test_sw_routing_contract.py（**23 passed**）",
]


def main() -> int:
    raw = CAP.read_text(encoding="utf-8")
    data = json.loads(raw)
    assert json.dumps(data, ensure_ascii=False, indent=2) + "\n" == raw, "往返不是逐字节相同 ⇒ 停"

    item = next(x for x in data["capabilities"] if x["id"] == "routing")
    before = (item["level"], list(item.get("evidence") or []),
              list(item.get("verified_versions") or []))
    item["level"] = "verified"
    item["evidence"] = EVIDENCE
    # ⚠ 它的 limitations ② 讲的正是「**本机 SW2026** 可发现 SWRoutingLib.tlb 和核心接口」
    #   ⇒ 那部分**真的在本机跑过**（`--preflight` 返回 `backend='solidworks-routing'`）⇒ 记 SW 版本。
    item["verified_versions"] = ["2026"]

    CAP.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    after = json.loads(CAP.read_text(encoding="utf-8"))
    got = next(x for x in after["capabilities"] if x["id"] == "routing")
    from collections import Counter
    print("  routing: level %s → **%s**" % (before[0], got["level"]))
    print("  evidence: %s → %d 条" % (before[1] or "（空）", len(got["evidence"])))
    print("  verified_versions: %s → %s" % (before[2] or "（空）", got["verified_versions"]))
    print("  limitations: %d 条（**一条不删**）" % len(got.get("limitations") or []))
    print("  level 分布: %s" % dict(Counter(x["level"] for x in after["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

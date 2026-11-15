"""工程判断层：拿到一个零件需求，先决定「买 / 造 / 放一放」，再谈怎么画。

这是 MCP 工具层（会操作 SolidWorks）之上缺的那一层：**外行与工程师的差别不在手上，在决定里。**

判据来自 triage.jsonl（53 项分流表），不是硬编码的 if-else：
    买        → 标准件，尺寸由厂商目录定义，自己算几何是浪费
    造        → 几何由参数+公式唯一决定，且有现成实现
    造-无代码 → 非标/多解/无成熟实现 → 放一放，不许硬画
    非零件    → 判据/工艺/数据，不是几何
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

TRIAGE = Path(__file__).resolve().parent.parent / "triage.jsonl"

# 造 → 已实现的生成器；未实现的族不在此登记。
# ★★ 2026-11-07 业主令：齿轮族原有 `plan_spur_gear` 是折线模拟曲线，已删除。
#    真曲线齿轮实现（scripts/gear_geometry.py）尚未通过真机验证 ⇒ 当前**无**可用生成器。
GENERATORS: dict[str, str] = {}

ROUTES = {
    "买": "选型 → 取模型（STEP/原生件）→ 插入；不重建特征树",
    "造": "需求 → 参数 → FeaturePlan → execute → L3/L4 校验",
    "造-无代码": "登记为已知缺口；不进入建模流程",
    "非零件": "作为判据层数据源，不产生几何",
}


@dataclass(frozen=True)
class Decision:
    part: str
    verdict: str
    route: str
    source: str | None      # 买：去哪拿；造：哪个生成器
    action: str
    reason: str
    known_gap: bool


def _load() -> dict[str, dict]:
    rows = [json.loads(l) for l in TRIAGE.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {r["id"]: r for r in rows}


def decide(part_id: str) -> Decision:
    """先判买/造，再谈几何。判不出来就报错，不猜。"""
    t = _load()
    if part_id not in t:
        raise KeyError(f"分流表里没有 {part_id}；新增族必须先登记，不许直接画")
    r = t[part_id]
    v = r["verdict"]
    src = r.get("where") if v == "买" else r.get("code")
    return Decision(
        part=r["name"],
        verdict=v,
        route=ROUTES[v],
        source=src,
        action=r["action"],
        reason=r["why"],
        known_gap=(v == "造-无代码"),
    )


def can_build_now(part_id: str) -> bool:
    """只有「造」且生成器已实现，才谈得上现在就能产出几何。"""
    d = decide(part_id)
    return d.verdict == "造" and part_id in GENERATORS


def render(d: Decision) -> str:
    lines = [
        f"【{d.part}】判定：{d.verdict}",
        f"  为什么：{d.reason}",
        f"  怎么做：{d.route}",
        f"  来源  ：{d.source or '无'}",
        f"  下一步：{d.action}",
    ]
    if d.known_gap:
        lines.append("  ⚠ 这是已知缺口，不是本次要做的事——登记而不硬画。")
    return "\n".join(lines)


if __name__ == "__main__":
    for pid in ("bearing-deep-groove", "gear-cylindrical", "cam", "tolerance"):
        print(render(decide(pid)))
        print(f"  → 现在就能出几何？{'能' if can_build_now(pid) else '不能'}")
        print()

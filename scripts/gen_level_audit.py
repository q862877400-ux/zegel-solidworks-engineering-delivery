r"""@brief 生成 `docs/union-level-audit.md`（R8 承诺的那份**等级审计**生成物）。

## 为什么有它（**R8 曾是幽灵规则**）
`scripts/check_union_conventions.py` 的 `check_capabilities_schema()` docstring 从很早就写着：

> R8 读生成物 `docs/union-level-audit.md`。

**而这个文件**从来没有生成器、也没有读者**** —— 2026-10-01（轮 60）实测：
* 全仓 grep `union-level-audit` ⇒ **只命中那句 docstring**；
* `docs/union-level-audit.md` **不存在**。

⇒ **「文档串与代码不符，比没有文档更糟」**（本项目方法学教训）：读文档的人会以为
「等级已经审计过了」，而**审计根本没发生**。本脚本把 R8 从承诺变成**事实**。

## 它做什么
读 `capabilities.yaml`，出一份**人可读**的等级审计：
1. **总表** —— 每条能力的 `id / level / source / 有无 evidence`（**逐条可核**）
2. **交叉表** —— `level × source`（**这两条线独立**，见 A2）
3. **不一致自检** —— 调 `check_union_conventions` 的 `check_capabilities_levels()`
   + `check_capabilities_schema()`，把**问题数**写进报告
   ⇒ **审计报告自己带「门禁怎么看」** —— 两者不一致就说明有一方错了

## 不做什么
* **不修改** `capabilities.yaml`（只读）。
* **不重复定义**枚举 —— `LEVELS` / `SOURCES` **从既有门禁 import**（**不重造**；
  两处各写一份枚举正是「两个家」的经典错误）。

# ── 来源 ──
# 仓库:   本项目自身（R8 那半边的实现）
# 文件:   scripts/gen_level_audit.py —— 本文件自身
#         scripts/check_union_conventions.py（枚举真源 + 一致性自检）
#         docs/capabilities-schema-proposal.md §五（R8 的定义）
# 定位:   把 R8 从 docstring 承诺变成可跑的生成物；依据是 2026-10-01（轮 60）实测到的
#         「docstring 提了、文件不存在、也没有生成器」。
# 官方签名依据: 不适用（纯静态：读 JSON + 写 markdown，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "docs" / "union-level-audit.md"


def _load_gate():
    """从既有门禁取 `LEVELS` / `SOURCES` 与两个检查函数（**不重造枚举**）。"""
    spec = importlib.util.spec_from_file_location(
        "check_union_conventions", REPO / "scripts" / "check_union_conventions.py"
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_union_conventions"] = mod
    spec.loader.exec_module(mod)
    return mod


def build(manifest: dict, gate) -> str:
    caps = manifest["capabilities"]
    lv = Counter(c["level"] for c in caps)
    sc = Counter(c["source"] for c in caps)
    cross = {(s, item): 0 for s in sorted(gate.SOURCES) for item in sorted(gate.LEVELS)}
    for c in caps:
        cross[(c["source"], c["level"])] = cross.get((c["source"], c["level"]), 0) + 1

    bad_schema = gate.check_capabilities_schema()
    bad_levels = gate.check_capabilities_levels()

    idx: list[str] = []
    idx.append("# 等级审计（union-level-audit）")
    idx.append("")
    idx.append(
        "> ⚠ **本文件是生成物** —— 由 `python scripts/gen_level_audit.py` 产出；"
        "**不要手改**（改了会被下次生成覆盖）。"
    )
    idx.append(
        "> 生成日期：%s ｜ 数据源：`capabilities.yaml`（`schema_version` = `%s`）"
        % (date.today().isoformat(), manifest.get("schema_version"))
    )
    idx.append(
        "> ⚑ 本文件是 `scripts/check_union_conventions.py` docstring 里 **R8** 承诺的那一份 —— "
        "在 2026-10-01（轮 60）之前，**它只有承诺、没有生成器**（详见本脚本 docstring）。"
    )
    idx.append("")
    idx.append("## 一、总表（逐条可核）")
    idx.append("")
    idx.append("| # | 能力 id | level | source | 有 evidence | 有 provenance |")
    idx.append("|---|---|---|---|---|---|")
    for i, c in enumerate(sorted(caps, key=lambda x: x["id"]), 1):
        idx.append(
            "| %d | `%s` | `%s` | `%s` | %s | %s |"
            % (
                i,
                c["id"],
                c["level"],
                c["source"],
                "✓" if c.get("evidence") else "—",
                "✓" if c.get("provenance") else "—",
            )
        )
    idx.append("")
    idx.append("**合计 %d 条**。" % len(caps))
    idx.append("")
    idx.append("## 二、`level` 分布")
    idx.append("")
    idx.append("| level | 条数 |")
    idx.append("|---|---|")
    for k in sorted(gate.LEVELS):
        idx.append("| `%s` | %d |" % (k, lv.get(k, 0)))
    idx.append("")
    idx.append("## 三、`source` 分布")
    idx.append("")
    idx.append("| source | 条数 |")
    idx.append("|---|---|")
    for k in sorted(gate.SOURCES):
        idx.append("| `%s` | %d |" % (k, sc.get(k, 0)))
    idx.append("")
    idx.append("## 四、交叉表 `level × source`（**两条线独立**，见 `AGENTS.md §一 A2`）")
    idx.append("")
    idx.append("| level \\ source | " + " | ".join(sorted(gate.SOURCES)) + " |")
    idx.append("|---|" + "---|" * len(gate.SOURCES))
    for item in sorted(gate.LEVELS):
        row = [str(cross.get((s, item), 0)) for s in sorted(gate.SOURCES)]
        idx.append("| `%s` | " % item + " | ".join(row) + " |")
    idx.append("")
    idx.append("> ⚠ 读法：`level: verified` 说的是「**有我们自己的运行证据**」，")
    idx.append("> `source: upstream` 说的是「**代码/广度来自上游**」—— **不是一回事**。")
    idx.append("")
    idx.append("## 五、护城河三域（`AGENTS.md §〇`）")
    idx.append("")
    idx.append("| 域 | level | source |")
    idx.append("|---|---|---|")
    for mid in ("topology_optimization", "costing", "animation_export"):
        c = next((x for x in caps if x["id"] == mid), None)
        idx.append(
            "| `%s` | `%s` | `%s` |" % (mid, c["level"], c["source"])
            if c
            else "| `%s` | **缺** | — |" % mid
        )
    idx.append("")
    idx.append("## 六、不一致自检（**报告自己带「门禁怎么看」**）")
    idx.append("")
    idx.append("| 检查 | 问题数 |")
    idx.append("|---|---|")
    idx.append(
        "| `check_capabilities_schema()`（R1-R3/R6/R9/R10/**R12**/**R13**） | **%d** |"
        % len(bad_schema)
    )
    idx.append(
        "| `check_capabilities_levels()`（规则 4 + R5/R7/R11） | **%d** |"
        % len(bad_levels)
    )
    idx.append("")
    if bad_schema or bad_levels:
        idx.append("⚠ **有问题**（逐条）：")
        idx.append("")
        for b in bad_schema + bad_levels:
            idx.append("* %s" % b)
    else:
        idx.append("✅ **两项检查都为 0 问题** —— 本报告与门禁的判读一致。")
    idx.append("")
    return "\n".join(idx)


def main() -> int:
    manifest = json.loads((REPO / "capabilities.yaml").read_text(encoding="utf-8"))
    gate = _load_gate()
    text = build(manifest, gate)
    OUT.write_text(text, encoding="utf-8")
    caps = manifest["capabilities"]
    print(
        "  已写 %s（%d 字节 / %d 条能力）"
        % (OUT.relative_to(REPO), len(text.encode("utf-8")), len(caps))
    )
    print("  level 分布: %s" % dict(Counter(c["level"] for c in caps)))
    print("  source 分布: %s" % dict(Counter(c["source"] for c in caps)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

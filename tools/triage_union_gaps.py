r"""@brief 分诊：`union-coverage-matrix` 的「缺口操作」里，多少是**别名**（我们其实有），多少是**真缺**。

## 为什么（2026-10-01 轮 86，Spec Kit `010`）
`tools/build_union_map.py` 打印「并集 404 操作 / **本仓库缺 339**」。
轮 86 从模具域撞见：那 3 个「缺口」里 **2 个我们明明有**
（`solidworks_mold_parting_line` / `solidworks_mold_shut_off_surface`）。

**根因（已查证）**：`build_union_sources._normalize` 去掉的是
**厂商前缀**（`solidworks_`/`sw_`/`cadscope_`…）与**动词前缀**（`create_`/`insert_`…），
**但不剥域词** ⇒
```
solidworks_mold_parting_line → mold_parting_line     ≠  parting_line（外部）
```
⇒ 同一条操作在两边**归一成不同的键** ⇒ 被记成缺口。

## ⚠ 为什么不给主匹配器加模糊启发式（**纪律**）
已知事实 53：**「调到看起来对」的识别信号是同一个启发式连续修补 ≥3 次还没稳定，就该停下回退**。
⇒ 本工具**不碰主匹配器**（那 339 仍是**严格名口径**的诚实数字），
只**另出一张分诊表**，用**有原则的规则**把缺口分成：

| 类 | 规则 | 含义 |
|---|---|---|
| **别名（强）** | 我们的归一操作名**以缺口名结尾**，且**多出来的词全是「域词」** | 极可能同一操作（如 `mold_` + `parting_line`）|
| **别名（弱）** | 以缺口名结尾，但多出来的词里**含动词** | 疑似但**语义可能不同**（如 `validate_` + `motion_study`）|
| **真缺** | 无任何我们的操作名以它结尾 | 确实没有 |

⚠ **域词表**取自 `build_union_map._CAP_KEYWORDS` 的键与 `DOMAIN_LABELS`（**不另造一套**）。

# ── 来源 ──
# 仓库:   本项目自身（分诊工具，只读）
# 文件:   tools/triage_union_gaps.py
# 定位:   把「缺 N」拆成「别名候选 / 真缺」，为 B 级并入**定范围**。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.stdout.reconfigure(encoding="utf-8")

SOURCES = ROOT / "tools" / "union-sources.json"      # ⚠ 在 `tools/` 下，不是 `docs/`（读 `build_union_map.py` 得到）
OUT = ROOT / "docs" / "union-gap-triage.md"

#: **域词**（取自各域的关键词表 —— 不另造一套）。出现在缺口名**之前**的这类词，视为「域
#: 限定」而非「不同操作」。
DOMAIN_WORDS = {
    "mold", "sketch", "part", "assembly", "asm", "drawing", "view", "sheet", "metal",
    "sheetmetal", "weldment", "weld", "surface", "simulation", "motion", "study",
    "appearance", "material", "color", "config", "configuration", "ref", "reference",
    "refgeom", "param", "dimension", "feature", "inspect", "measure", "macro", "session",
    "document", "doc", "file", "hole", "fillet", "chamfer", "pattern", "boss", "cut",
    "extrude", "revolve", "loft", "sweep", "draft", "shell", "rib", "bend", "flange",
    "gusset", "endcap", "core", "cavity", "parting", "shut", "off", "balloon", "bom",
    "section", "detail", "annotat", "topology", "fea", "mesh", "load", "restraint",
    "result", "costing", "routing", "dfm", "pdm", "dimxpert", "ocp", "smooth",
}
#: **动词**（`_normalize` 已剥的那批 + 常见同类）。多出来的词里含这些 ⇒ 语义可能不同。
VERBS = {
    "create", "add", "insert", "set", "get", "list", "draw", "start", "make", "build",
    "validate", "run", "apply", "delete", "remove", "update", "edit", "check", "export",
    "import", "open", "close", "save", "load", "generate", "compute", "collect", "probe",
    "enable", "disable", "toggle", "select", "clear", "reset", "copy", "move", "rotate",
}


def _our_ops() -> set:
    """我们的归一操作名（复用采集器的归一逻辑，**不另造**）。"""
    from build_union_map import _our_tools
    from build_union_sources import _normalize
    return {_normalize(t) for t in _our_tools()}


def _script_ops() -> set:
    """**第三个口径**：`scripts/sw_*.py` 的公开函数名（**能力面**）。

    ⚠ 为什么必须分开量：`_our_ops()` 是**MCP 暴露面**。
    一个缺口可能「**能力早就写了、只是没暴露成 MCP 工具**」——
    那与「真的没实现」是**两件事**，待办也不同（前者只要接出去，后者要写）。
    ⚠ 已知事实 25 记着这件事：`server.py` 只引用 25 个模块，后补的 58+ 个没进。
    """
    import re
    pat = re.compile(r"^def ([a-z_]\w*)\(", re.MULTILINE)
    out: set = set()
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        out |= set(pat.findall(p.read_text(encoding="utf-8", errors="ignore")))
    return out


def _classify(gap: str, ours: set) -> tuple:
    """⇒ `(类, 证据)`。"""
    suffix = gap.split("_")[-1]
    cands = sorted(o for o in ours if o.endswith("_" + suffix) or o == gap)
    if not cands:
        return "真缺", ""
    strong, weak = [], []
    for c in cands:
        extra = c[: -len(suffix) - 1] if c.endswith("_" + suffix) else ""
        toks = [t for t in extra.split("_") if t]
        if not toks:
            strong.append(c)                       # 完全相同
        elif all(t in DOMAIN_WORDS for t in toks):
            strong.append(c)                       # 多出来的全是域词
        else:
            weak.append(c)                         # 含动词 ⇒ 语义可能不同
    if strong:
        return "别名（强）", ", ".join(strong[:2])
    return "别名（弱）", ", ".join(weak[:2])


def main() -> int:
    if not SOURCES.is_file():
        print("  先跑 tools/build_union_sources.py")
        return 1
    data = json.loads(SOURCES.read_text(encoding="utf-8"))
    ours = _our_ops()
    scripts = _script_ops()

    # 并集里的全部操作（来自四家来源文件）
    union: set = set()
    for src in data["sources"]:
        for op in src.get("operations") or []:
            union.add(op)
    gaps = sorted(union - ours)

    buckets: dict[str, list] = {"别名（强）": [], "别名（弱）": [], "后缀候选（需人工核）": [], "真缺": []}
    for g in gaps:
        kind, ev = _classify(g, ours)
        if kind == "真缺":
            # ⚑ **第三口径**：能力在 `scripts/` 里、只是没暴露成 MCP 工具 ⇒ **不是"没实
            # 现"**
            suffix = g.split("_")[-1]
            near = sorted(f for f in scripts if f.endswith("_" + suffix) or f == g)
            if near:
                buckets["后缀候选（需人工核）"].append((g, ", ".join(near[:2])))
                continue
        buckets[kind].append((g, ev))

    total = len(gaps)
    print("并集 %d 操作 · 我们（MCP 暴露面）%d · `scripts/` 公开函数 %d · **缺口 %d**"
          % (len(union), len(ours), len(scripts), total))
    print()
    for k in ("别名（强）", "别名（弱）", "后缀候选（需人工核）", "真缺"):
        n = len(buckets[k])
        print("  %-16s **%3d** 个%s" % (k, n, "" if not n else "  （%.0f%%）" % (100.0 * n / total)))
    print()
    print("  ⇒ **真的要从零实现的** = 「真缺 %d」；"
          "其余 %d 个是「命名/暴露」问题" % (len(buckets["真缺"]), total - len(buckets["真缺"])))
    print()
    print("  ⚠⚠ **抽验警告（2026-10-01 轮 86 实测 10 条）**：")
    print("     「后缀候选」这一类的**假阳性率约一半** —— 它只比**最后一个词**：")
    print("       ✅ parting_line → insert_parting_line · add_dimension → add_dimension · create_mate → add_mate")
    print("       ❌ shut_off_surface → create_bspline_surface（都是 surface，但不是 shut-off）")
    print("       ❌ set_material → add_render_material · create_section_view → activate_view")
    print("     ⇒ 本表**只用于定范围**，**每个候选都要人工核**（★ 已知事实 53：不为它继续调启发式）。")

    lines = [
        "# B 级并入缺口分诊（`010`）",
        "",
        "> **本表干什么**：把 `union-coverage-matrix.md` 的「缺 N」拆成"
        "「**别名候选**（我们其实有，只是名字不同）」与「**真缺**」，为并入**定范围**。",
        "> ⚠ **主匹配器没动**（纪律：已知事实 53 —— 不靠模糊启发式硬凑）。",
        "> 这张表是**另一口径**，用**有原则的规则**算出来，供人核。",
        "",
        "**算于**：2026-10-01（轮 86）· 并集 **%d** · 我们 **%d** · 缺口 **%d**" % (len(union), len(ours), total),
        "",
        "| 类 | 个数 | 占比 | 含义 |",
        "|---|---|---|---|",
        "| **别名（强）** | %d | %.0f%% | 我们的操作名**以缺口名结尾**，且多出来的词**全是域词** ⇒ 极可能同一操作 |"
        % (len(buckets["别名（强）"]), 100.0 * len(buckets["别名（强）"]) / max(total, 1)),
        "| **别名（弱）** | %d | %.0f%% | 以缺口名结尾，但多出来的词里**含动词** ⇒ 疑似，语义可能不同 |"
        % (len(buckets["别名（弱）"]), 100.0 * len(buckets["别名（弱）"]) / max(total, 1)),
        "| **能力在、未暴露** | %d | %.0f%% | `scripts/sw_*.py` 里有同名函数，**只是没暴露成 MCP 工具** |"
        % (len(buckets["后缀候选（需人工核）"]), 100.0 * len(buckets["后缀候选（需人工核）"]) / max(total, 1)),
        "| **真缺** | %d | %.0f%% | 连 `scripts/` 里也没有同名函数 ⇒ **要从零实现** |"
        % (len(buckets["真缺"]), 100.0 * len(buckets["真缺"]) / max(total, 1)),
        "",
        "---",
        "",
    ]
    for k in ("别名（强）", "别名（弱）", "后缀候选（需人工核）", "真缺"):
        lines.append("## %s（%d）" % (k, len(buckets[k])))
        lines.append("")
        if not buckets[k]:
            lines.append("（空）")
        else:
            lines.append("| 缺口操作 | 我们的候选 |")
            lines.append("|---|---|")
            for g, ev in buckets[k][:200]:
                lines.append("| `%s` | %s |" % (g, ("`%s`" % ev) if ev else "—"))
            if len(buckets[k]) > 200:
                lines.append("")
                lines.append("（还有 %d 个，见 `tools/triage_union_gaps.py` 的输出）"
                             % (len(buckets[k]) - 200))
        lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  ⇒ 已写 %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

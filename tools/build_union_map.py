r"""生成「并集广度地图」—— 域 × 来源 矩阵 + 缺口清单。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本工具为原创
# 文件:   tools/build_union_map.py —— 本文件自身
# 定位:   docs/union-conventions.md §二「地图的形态」的实现；
#         读 tools/union-sources.json（外部来源）+ capabilities.yaml（本仓库能力），
#         产出 docs/union-coverage-matrix.md。
# 官方依据: 无（本工具不涉及 SolidWorks API）
# 许可:   本仓库 MIT
# ⚠ 本工具只做**静态汇总**，不运行任何被扫描项目、不连 SolidWorks，
#   未在本机实测（见 AGENTS.md 铁律 2）。
# 覆盖:   后续同级定义
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "tools" / "union-sources.json"
OUT = ROOT / "docs" / "union-coverage-matrix.md"
#: ⚑ 「不做 + 原因」的显式清单（`AGENTS.md §一 A1` 的另一半，2026-10-01 轮 67 加）。
#: 形状由 `check_union_conventions` 的 **R14** 守（`subject`/`reason`/`evidence` 三者非
#: 空）。
NOT_DOING = ROOT / "docs" / "union-not-doing.json"

#: 域的展示名与顺序（与 docs/union-conventions.md 的域枚举一致）
DOMAIN_LABELS = {
    "session": "① 会话 / 文档 / 文件",
    "refgeom": "② 参考几何",
    "sketch": "③ 草图",
    "param": "④ 尺寸 / 约束 / 参数",
    "feature": "⑤ 零件特征",
    "surface": "⑥ 曲面",
    "sheetmetal": "⑦ 钣金",
    "weldment": "⑧ 焊件",
    "mold": "⑨ 模具",
    "assembly": "⑩ 装配",
    "drawing": "⑪ 工程图",
    "inspect": "⑫ 检查 / 测量 / 反馈",
    "simulation": "⑬ 仿真 / Motion",
    "appearance": "⑭ 外观 / 材质 / 配置",
    "macro": "⑮ 宏 / 自动化",
    "advanced": "⑯ 高级 / 专项（含护城河候选）",
    "other": "⑰ 未归类",
}

#: 许可 -> 能不能抄
COPYABLE = {"MIT", "Apache-2.0"}


def _our_tools() -> list[str]:
    """本仓库 MCP 暴露的工具名（**两个来源都读**）。

    ⚠⚠ **2026-10-01 轮 86 修**：本函数原先**只读 `server.py` 的 `@mcp.tool(name=...)` 装饰器形式**
    ⇒ 而本仓库后补的工具注册在 **`mcp-server/tool_specs_batch*.py`** 里（`name="solidworks_*"`），
    **与装饰器形式零交集**。实测：
    ```
    server.py 装饰器        : 45 个
    tool_specs_batch*.py    : 20 个（**与装饰器交集 = 0**）
    合并                    : **65** 个
    ```
    ★ **后果**：暴露面被低估 20 个 ⇒ 「缺口」数被灌水。
    实测印证：模具域的 3 个「缺口」里 **2 个我们明明有**
    （`solidworks_mold_parting_line` / `solidworks_mold_shut_off_surface`，在 `tool_specs_batch1.py` 里）。

    ⚠ **仍须分清两个口径**（本函数只量「MCP 暴露面」，不是「能力面」）：
    能力实现在 `scripts/` 里，其中一部分没被暴露成 MCP 工具。
    另一列 `_our_capabilities()` 量能力面，**两列并存、互不替代**。
    """
    import re

    out: set[str] = set()
    server = ROOT / "mcp-server" / "server.py"
    if server.is_file():
        text = server.read_text(encoding="utf-8", errors="ignore")
        out |= set(re.findall(r'@mcp\.tool\(\s*\n?\s*name\s*=\s*"([^"]+)"', text))
    # ⚑ 第二个来源：`tool_specs_batch*.py` 的注册表（轮 86 补上 —— 此前**完全没读**）
    for spec in sorted((ROOT / "mcp-server").glob("tool_specs_*.py")):
        stext = spec.read_text(encoding="utf-8", errors="ignore")
        out |= set(re.findall(r'name="((?:solidworks|cadstudio)_[\w]+)"', stext))
    return sorted(out)


#: 域 → 函数名关键词（用于把 `scripts/sw_*.py` 的公开函数粗略归类）
_CAP_KEYWORDS: dict[str, tuple[str, ...]] = {
    "session": (
        "session",
        "document",
        "doc",
        "file",
        "open",
        "save",
        "export",
        "import",
    ),
    "refgeom": ("plane", "axis", "point", "csys", "coordinate", "reference"),
    "sketch": ("sketch", "spline", "line", "circle", "arc", "constraint", "relation"),
    "param": ("dimension", "param", "equation", "tolerance"),
    "feature": (
        "feature",
        "extrude",
        "cut",
        "fillet",
        "chamfer",
        "hole",
        "pattern",
        "draft",
        "shell",
        "rib",
    ),
    "surface": ("surface", "loft", "sweep", "knit", "trim_surf", "patch"),
    "sheetmetal": ("sheet", "bend", "flange", "hem", "jog", "unfold"),
    "weldment": (
        "weld",
        "gusset",
        "endcap",
        "end_cap",
        "cutlist",
        "cut_list",
        "structural_member",
    ),
    "mold": ("mold", "core", "cavity", "parting", "shut_off", "ripple"),
    "assembly": ("assembl", "mate", "component", "explode", "interference"),
    "drawing": ("drawing", "view", "balloon", "bom", "section", "detail", "annotat"),
    "inspect": (
        "measure",
        "mass_prop",
        "check",
        "review",
        "validate",
        "inspect",
        "diff",
        "provenance",
    ),
    "simulation": (
        "simulation",
        "study",
        "motion",
        "fea",
        "mesh",
        "load",
        "restraint",
        "topology",
        "result",
    ),
    "appearance": ("appearance", "material", "color", "render", "config", "texture"),
    "macro": ("macro", "vba", "script", "batch", "auto", "queue", "worker", "cli"),
    "advanced": ("dfm", "costing", "routing", "pdm", "dimxpert", "ocp", "smooth"),
}


def _our_capabilities() -> dict[str, set[str]]:
    """**能力面**：`scripts/sw_*.py` 的公开函数按域粗略归类。

    与 `_our_tools()`（MCP 暴露面）**是两个口径，不可合并**：

    | 口径 | 含义 | 用途 |
    |---|---|---|
    | MCP 暴露面 | 四家有、我们没以 MCP 工具暴露的操作数 | 决定「要不要做 MCP 注册」 |
    | **能力面**（本函数） | 该域我们有多少 `scripts/` 公开函数 | 决定「要不要实现该域」 |

    ⚠ **已知噪声**：按函数名关键词匹配，同名函数会分到多个域，且**有意**宁可重复不漏
    ⇒ 本列用于**排序与发现矛盾**，不是精确计数。
    """
    import re

    out: dict[str, set[str]] = {k: set() for k in DOMAIN_LABELS}
    func_re = re.compile(r"^def ([a-z_]\w*)\(", re.MULTILINE)
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in func_re.finditer(text):
            fn = m.group(1)
            low = fn.lower()
            hit = False
            for dom, kws in _CAP_KEYWORDS.items():
                if any(k in low for k in kws):
                    out[dom].add(fn)
                    hit = True
            if not hit:
                out["other"].add(fn)
    return out


def _our_operations() -> dict[str, str]:
    """本仓库工具 -> 操作名（复用采集器的归一逻辑）。"""
    sys.path.insert(0, str(ROOT / "tools"))
    from build_union_sources import _domain, _normalize  # noqa: E402

    out = {}
    for t in _our_tools():
        op = _normalize(t)
        out[op] = _domain(op)
    return out


def main() -> int:
    if not SOURCES.is_file():
        print("  先跑 tools/build_union_sources.py 生成 %s" % SOURCES.name)
        return 1
    data = json.loads(SOURCES.read_text(encoding="utf-8"))
    sources = data["sources"]
    ours = _our_operations()

    # ⚑ 「不做 + 原因」（A1 的另一半）—— 文件不存在时**不是错误**：
    #   它表示「一个都没登记」⇒ 生成一段**空清单警告**（见 §二 之后的那个小节）。
    not_doing: list = []
    if NOT_DOING.is_file():
        try:
            not_doing = (
                json.loads(NOT_DOING.read_text(encoding="utf-8")).get("not_doing") or []
            )
        except json.JSONDecodeError as exc:
            print("  ⚠ %s 不是合法 JSON（%s）⇒ 按空清单处理" % (NOT_DOING.name, exc))

    # 域 -> {来源名: 操作集合}
    grid: dict[str, dict[str, set]] = {}
    for dom in DOMAIN_LABELS:
        grid[dom] = {s["repo"]: set(s["domains"].get(dom, [])) for s in sources}
        grid[dom]["本仓库"] = {op for op, d in ours.items() if d == dom}

    lines: list[str] = []
    A = lines.append
    A("# 并集广度地图")
    A("")
    A("> **本文件是生成物** —— 由 `tools/build_union_map.py` 从")
    A("> `tools/union-sources.json` + `capabilities.yaml` 生成，不要手改。")
    A(">")
    A(
        "> 配套规范：`docs/union-conventions.md`（命名 / 单位 / 选择 / 验证等级 / 出处 / 失败要响）"
    )
    A("")
    A("## 一 来源与许可（读**真实 LICENSE 文件**判定，不采信 README 徽章）")
    A("")
    A("| 来源 | 许可 | 工具数 | 操作数 | 它自己声明跑过的环境 | 能抄吗 |")
    A("|---|---|---|---|---|---|")
    for s in sources:
        lic = s["license"]
        can = "✅ 可抄改商用" if lic in COPYABLE else "👁 只读思想"
        if lic == "Apache-2.0":
            can = "✅ 可抄（**须带 NOTICE + 声明改动文件**）"
        A(
            "| `%s` | %s | %d | %d | %s | %s |"
            % (
                s["repo"],
                lic,
                s["tool_count"],
                s["operation_count"],
                s["declared_verified"] or "**未声明**",
                can,
            )
        )
    A(
        "| **本仓库（上游 + 本次）** | MIT | %d | %d | 见 capabilities.yaml | — |"
        % (len(_our_tools()), len(ours))
    )
    A("")
    A("> ⚠ **验证口径的真相**：四家里只有 `Slacker-LLC` 声明全工具真机跑过。")
    A("> `Eduardof0nt` 工具最多（187），但**仓库内测试文件数为 0**。")
    A("> 详见每家的 `note` 字段（`tools/union-sources.json`）。")
    A("")
    A("## 二 域 × 来源 矩阵")
    A("")
    A("> ⚠ **两列口径不同，不可互相替代**（2026-10-01 加）：")
    A("> - **本仓库（MCP）** = `mcp-server/server.py` 里静态抽出的**工具名**。")
    A(">   「缺口」列是它相对四家并集算出来的 —— 量的是**MCP 暴露面**之差。")
    A("> - **本仓库能力面** = `scripts/sw_*.py` 的**公开函数数**。")
    A(">   本仓库的能力多数**没被暴露成 MCP 工具**（`AGENTS.md` 已知事实 25：")
    A(">   `server.py` 只引用 25 个模块，我们后补的 58+ 个一个都没进）。")
    A(">")
    A("> **⇒ 只看「缺口」列会把已有的域记成「零」**（例：焊件列显示 `·`，")
    A(
        "> 而 `scripts/sw_weldment.py` 有 666 行 / 20 个函数且 `capabilities.yaml` 里是 `verified`）。"
    )
    A("> **判断「该实现哪个域」请看能力面列；判断「该暴露哪个工具」才看 MCP 列。**")
    A(">")
    # ⚠ 这个标记的**含义原先只写在下面 `cell_cap += "⚠"` 的代码注释里** ⇒
    #   读者拿到的矩阵里查不到它是什么意思。**⇒ 图例里必须自解释**（一个事实一个家）。
    #   （2026-10-01 轮 49 跑 `specs/002-merge-template` 的 converge 步时发现。）
    A(
        "> - 能力面列里的 **`⚠`** = 该域**缺口(MCP) > 0 而我们已有 ≥5 个函数** ⇒ "
        "**它多半不是能力缺口，只是没暴露成 MCP 工具**。"
    )
    A(">   ⚠ 这是**启发式标记**（阈值 5），不是判定；**要下结论仍须逐域人工核**。")
    A("")
    caps = _our_capabilities()
    header = (
        ["域"]
        + [s["repo"].split("/")[0][:14] for s in sources]
        + ["本仓库(MCP)", "本仓库能力面", "并集", "缺口(MCP)"]
    )
    A("| " + " | ".join(header) + " |")
    A("|" + "---|" * len(header))
    total_union = 0
    total_gap = 0
    gap_rows: list[tuple[str, int]] = []
    for dom, label in DOMAIN_LABELS.items():
        cells = grid[dom]
        u: set = set()
        for v in cells.values():
            u |= v
        ours_set = cells["本仓库"]
        gap = u - ours_set
        total_union += len(u)
        total_gap += len(gap)
        if gap:
            gap_rows.append((label, len(gap)))
        row = [label]
        for s in sources:
            n = len(cells[s["repo"]])
            row.append("%d" % n if n else "·")
        row.append("%d" % len(ours_set) if ours_set else "·")
        n_cap = len(caps.get(dom, ()))
        # 能力面列：缺口>0 而我们有 >=5 个函数时标 ⚠（提醒「这不是能力缺口」）
        cell_cap = "%d" % n_cap if n_cap else "·"
        if gap and n_cap >= 5:
            cell_cap += "⚠"
        row.append(cell_cap)
        row.append("%d" % len(u))
        row.append("**%d**" % len(gap) if gap else "✓")
        A("| " + " | ".join(row) + " |")
    A("")
    A(
        "**合计**：并集 %d 个操作；**MCP 暴露面**缺 **%d** 个（**不是**能力缺口 —— 见上）。"
        % (total_union, total_gap)
    )
    A("")
    if gap_rows:
        A("### 缺口按域排序（大 → 小）")
        A("")
        A("| 域 | 缺 |")
        A("|---|---|")
        for label, n in sorted(gap_rows, key=lambda x: -x[1]):
            A("| %s | %d |" % (label, n))
        A("")

    # ⚑ **§二之后：「不做 + 原因」**（2026-10-01 轮 67 加）——
    # `AGENTS.md §一 A1` 的原文是「域覆盖矩阵里本仓库每一格**都有来源，或写明「不做 + 原
    # 因」**」。
    # ⚠ 此前**只有「有来源」那一半有机制**（`capabilities.yaml` 的 `source`/`source_evid
    # ence`，
    #     由 R12/R13 门禁守着），而「不做 + 原因」**一格机制都没有** ——
    #     矩阵里只有「缺 N」，读者**无从知道哪些是「我们不做」、哪些是「还没做」**。
    # ⇒ 数据源 `docs/union-not-doing.json`；形状由 `check_union_conventions` 的 **R14**
    # 守
    #     （`subject` / `reason` / `evidence` 三者非空）。
    A("### 不做 + 原因（A1 的另一半）")
    A("")
    A("> `AGENTS.md §一 A1`：「…每一格**都有来源，或写明「不做 + 原因」**」。")
    A(
        "> **有来源**那一半由 `capabilities.yaml` 的 `source`/`source_evidence` 承担（R12/R13 守着）；"
    )
    A(
        "> **本表**承担「不做 + 原因」那一半。数据源 `docs/union-not-doing.json`，形状由 R14 守。"
    )
    A(">")
    A(
        "> ⚠ **本表是显式清单，不是默认放行** —— 没登记在这里、又没在 `capabilities.yaml` 里的，"
    )
    A("> 就仍是**缺口**（见上表的「缺 N」），不是「不做」。")
    A("")
    if not_doing:
        A("| 不做 | 原因 | 依据（可核） |")
        A("|---|---|---|")
        for item in not_doing:
            ev = "<br>".join("· %s" % e for e in item.get("evidence") or [])
            A(
                "| %s | %s | %s |"
                % (item.get("subject", ""), item.get("reason", ""), ev)
            )
        A("")
    else:
        A(
            "> ⚠ **本清单为空** —— 一个「不做」都没登记（那通常意味着**还没逐域确证**，而不是「全都做」）。"
        )
        A("")

    A("## 三 每个域的**独家来源**（只有一家有 ⇒ 只能抄它，且必须自己测）")
    A("")
    A("| 域 | 独家操作 | 唯一来源 |")
    A("|---|---|---|")
    for dom, label in DOMAIN_LABELS.items():
        cells = grid[dom]
        u: set = set()
        for v in cells.values():
            u |= v
        exclusive = []
        for op in sorted(u):
            owners = [k for k, v in cells.items() if op in v]
            if len(owners) == 1 and owners[0] != "本仓库":
                exclusive.append((op, owners[0]))
        if exclusive:
            A(
                "| %s | %d 个：%s | %s |"
                % (
                    label,
                    len(exclusive),
                    ", ".join("`%s`" % o for o, _ in exclusive[:6])
                    + ("…" if len(exclusive) > 6 else ""),
                    exclusive[0][1],
                )
            )
    A("")
    A("## 四 本仓库独家（别人都没有）")
    A("")
    ext_union: set = set()
    for s in sources:
        ext_union |= set(s["operations"])
    our_only = sorted(set(ours) - ext_union)
    A("共 %d 个操作只有本仓库有：" % len(our_only))
    A("")
    for op in our_only:
        A("- `%s`（%s）" % (op, DOMAIN_LABELS.get(ours[op], ours[op])))
    A("")

    # ── 五 可执行的并入清单 ───────────────────────────────────────
    # 地图只说「缺什么」；本节说「从哪抄、抄之前先知道什么」。
    # ⚠ 关键一列是「来源验证过吗」：Eduardof0nt 工具最多但测试文件为 0，
    #   抄它的东西**必须自己实测**，不能因为来源大就默认可信。
    A("## 五 可执行的并入清单（按域）")
    A("")
    A(
        "> **怎么读**：`来源` 列给出该域最有货的家；`来源验证` 列是**该来源自己声明的"
        "跑过的环境** —— 空 = **它没声明跑过**，抄进来只能先标 `stitched`，"
        "必须我们实测过才能升 `verified`（规则 4）。"
    )
    A("")
    for dom, label in DOMAIN_LABELS.items():
        cells = grid[dom]
        u: set = set()
        for v in cells.values():
            u |= v
        gap = sorted(u - cells["本仓库"])
        if not gap:
            continue
        # 该域各来源的覆盖数 + 验证口径
        ranked = sorted(
            (
                (s["repo"], len(cells[s["repo"]]), s["declared_verified"], s["license"])
                for s in sources
                if cells[s["repo"]]
            ),
            key=lambda x: -x[1],
        )
        if not ranked:
            continue
        A("### %s（缺 %d）" % (label, len(gap)))
        A("")
        A("| 来源 | 该域有 | 许可 | 来源验证 |")
        A("|---|---|---|---|")
        for repo, n, ver, lic in ranked:
            A("| `%s` | %d | %s | %s |" % (repo, n, lic, ver or "**未声明**"))
        A("")
        A("缺口操作：%s" % "、".join("`%s`" % g for g in gap[:24]))
        if len(gap) > 24:
            A("（还有 %d 个，见 `tools/union-sources.json`）" % (len(gap) - 24))
        A("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("  并集 %d 操作 / 本仓库缺 %d" % (total_union, total_gap))
    print("  本仓库独家 %d 个" % len(our_only))
    print("  已写入 %s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

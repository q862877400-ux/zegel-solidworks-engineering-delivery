r"""@brief 按**能力**对照各域缺口（补上广度地图只数 MCP 工具名的口径缺陷）。

## 为什么需要它
`tools/build_union_map.py` 的「本仓库」列只数 `mcp-server/server.py` 里的**工具名**：

    def _our_tools() -> list[str]:
        '''本仓库 MCP 暴露的工具名（从 server.py 静态抽取）。'''

⇒ 而本仓库的能力实现在 `scripts/sw_*.py` 里，**它们没被暴露成 MCP 工具**
（AGENTS.md 已知事实 25：上游 MCP 只引用 25 个模块，我们后补的 58 个一个都没进）。

**实证矛盾**：地图说「⑧ 焊件 | 本仓库 ·（零）| 缺 5」，而 `scripts/sw_weldment.py`
有 666 行 / 20 个函数。同类还有钣金 / 草图 / 仿真 / 工程图 / 曲面。

## 本工具做什么
**两个口径并存、各自标注**（不互相替代 —— 上一次误读正是因为只有一个数）：

| 口径 | 含义 | 用途 |
|---|---|---|
| **MCP 暴露面**（地图原有） | 四家有、我们没以 MCP 工具暴露的操作数 | 决定「要不要做 MCP 注册」 |
| **能力面**（本工具新增） | 该域我们有多少 `scripts/` 模块与公开函数 | 决定「要不要实现该域」 |

**⇒ 绝不把两个数合并成一个**。合并会重演「把四家域操作总数当成我们的缺口」那类错。

# ── 来源 ──
# 仓库:   本项目自身（口径校正工具）
# 文件:   tools/capability_gap.py
# 定位:   AGENTS.md「报告计数要附枚举命令」；`specs/002-merge-template` 的 US1 交付物
#         （该 spec 的 T-005 与本工具互为验收）。
#         纠正对象是 `tools/build_union_map.py` 的 `_our_tools()` 口径 —— 该文件本身不改
#         （它是地图的一部分，动它会影响生成物），本工具只做**并存的第二口径**。
# 官方签名依据: 不适用（纯静态统计，不碰 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态统计，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
#    ⚠ 已知噪声：按函数名匹配关键词归类，同名函数会分到多个域；
#      这是**有意的**（宁可重复也不漏），故本表用于**排序**而非精确计数。
# ⚠ **2026-10-01（轮 53）从工作区根搬进 `tools/`**，理由：`specs/002-merge-template/tasks.md`
#   的 T-005 把它当**验收命令**，而它原先只在 `D:\AI\SW\`（**换机器/CI 跑不了**）。
#   搬移时把 `REPO = Path(r"")` 改成 `parents[1]`
#   （**可移植**）—— 这是本轮新加的**可跑性门禁** `scripts/check_spec_acceptance_paths.py`
#   查出来的第 1 例。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# ⚠ **可移植**：不要硬编码机器路径（原先写死 ``）。
REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "union-coverage-matrix.md"
SCRIPTS = REPO / "scripts"

#: 域关键词 —— 与 build_union_map 的 16 个域对应（顺序一致，便于并排看）
DOMAIN_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    (
        "① 会话/文档/文件",
        ("session", "document", "doc", "file", "open", "save", "export", "import"),
    ),
    ("② 参考几何", ("plane", "axis", "point", "csys", "coordinate", "reference")),
    ("③ 草图", ("sketch", "spline", "line", "circle", "arc", "constraint", "relation")),
    (
        "④ 尺寸/约束/参数",
        ("dimension", "param", "equation", "tolerance", "gd", "mate_"),
    ),
    (
        "⑤ 零件特征",
        (
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
    ),
    ("⑥ 曲面", ("surface", "loft", "sweep", "knit", "trim_surf", "patch")),
    ("⑦ 钣金", ("sheet", "bend", "flange", "hem", "jog", "unfold")),
    (
        "⑧ 焊件",
        (
            "weld",
            "gusset",
            "endcap",
            "end_cap",
            "cutlist",
            "cut_list",
            "structural_member",
        ),
    ),
    ("⑨ 模具", ("mold", "core", "cavity", "parting", "shut_off", "ripple")),
    ("⑩ 装配", ("assembl", "mate", "component", "explode", "interference")),
    ("⑪ 工程图", ("drawing", "view", "balloon", "bom", "section", "detail", "annotat")),
    (
        "⑫ 检查/测量/反馈",
        (
            "measure",
            "mass_prop",
            "check",
            "review",
            "validate",
            "inspect",
            "diff",
            "provenance",
        ),
    ),
    (
        "⑬ 仿真/Motion",
        (
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
    ),
    (
        "⑭ 外观/材质/配置",
        ("appearance", "material", "color", "render", "config", "texture"),
    ),
    (
        "⑮ 宏/自动化",
        ("macro", "vba", "script", "batch", "auto", "queue", "worker", "cli"),
    ),
    (
        "⑯ 高级/专项",
        ("dfm", "costing", "routing", "pdm", "dimxpert", "topology", "ocp", "smooth"),
    ),
    ("⑰ 未归类", ()),  # 占位：不参与关键词匹配
]

FUNC_RE = re.compile(r"^def ([a-z_]\w*)\(", re.MULTILINE)


def our_functions() -> list[tuple[str, str]]:
    """返回 [(模块名, 函数名)] —— 本仓库 `scripts/sw_*.py` 的公开函数。"""
    out: list[tuple[str, str]] = []
    for p in sorted(SCRIPTS.glob("sw_*.py")):
        for m in FUNC_RE.finditer(p.read_text(encoding="utf-8", errors="replace")):
            out.append((p.name, m.group(1)))
    return out


def ours_by_domain(funcs: list[tuple[str, str]]) -> dict[str, set[str]]:
    grid: dict[str, set[str]] = {label: set() for label, _ in DOMAIN_KEYWORDS}
    unclassified: set[str] = set()
    for _mod, fn in funcs:
        low = fn.lower()
        hit = False
        for label, kws in DOMAIN_KEYWORDS:
            if not kws:
                continue
            if any(k in low for k in kws):
                grid[label].add(fn)
                hit = True
        if not hit:
            unclassified.add(fn)
    grid["⑰ 未归类"] = unclassified
    return grid


def _norm_domain(s: str) -> str:
    """域名的**规范化键**：**去掉所有空白**。

    ⚠⚠ 这是必需的（2026-10-01 轮 53 查出）：矩阵里**同一个域在不同节写法不同** ——
    §二 写 `| ① 会话 / 文档 / 文件 |`（带空格），§五 写 `| ① 会话/文档/文件 |`（不带）。
    本模块的 `DOMAIN_KEYWORDS` 用的是**不带空格**那套 ⇒ 若不规范化，
    `gaps.get(label)` 对这些域**全部扑空**（与下面那个正则 bug 叠加，一起把列变成 `?`）。
    """
    return re.sub(r"\s+", "", s)


#: §五「缺口按域排序」是**两列**表：`| ⑪ 工程图 | 49 |`。
#: ⚠⚠ **本正则原来写的是八列**（`|域|a|b|c|d|e|f|**N**|`），**两张表都不匹配**
#:   —— §二 是**九列**（且能力面那格含 `⚠` 后缀），§五 是**两列**。
#:   ⇒ 结果：`map_gap_counts()` 恒返回空 ⇒ 输出里「地图缺口」列**全是 `?`**。
#:   **2026-10-01 轮 53 修正为两列**（§五 是工具 docstring 自己声明的来源）。
GAP_ROW = re.compile(r"\|\s*([①-⑰][^|]*?)\s*\|\s*(\d+)\s*\|")


def map_gap_counts() -> dict[str, int]:
    """从地图 §五 抽每域的「缺口」数（地图口径 = MCP 暴露面）。

    ⚠ 键经过 `_norm_domain` 规范化（去空白），调用方查询时**也必须规范化**。
    """
    out: dict[str, int] = {}
    if not MAP.is_file():
        return out
    for line in MAP.read_text(encoding="utf-8").splitlines():
        m = GAP_ROW.match(line)
        if m:
            out[_norm_domain(m.group(1))] = int(m.group(2))
    return out


def main() -> int:
    funcs = our_functions()
    ours = ours_by_domain(funcs)
    gaps = map_gap_counts()
    mods = len({m for m, _ in funcs})
    print(
        "本仓库能力面：%d 个 scripts/sw_*.py 模块 / %d 个公开函数" % (mods, len(funcs))
    )
    print()
    print("%-22s %8s %10s %10s" % ("域", "地图缺口", "我们函数", "我们模块"))
    print("-" * 54)
    for label, _ in DOMAIN_KEYWORDS:
        n_fn = len(ours.get(label, ()))
        n_md = len({m for m, f in funcs if f in ours.get(label, ())})
        # ⚠ 查询也要规范化（地图 §五 的域名带空格，本模块的常量不带）—— 见 `_norm_domain
        # `
        gap = gaps.get(_norm_domain(label))
        flag = ""
        if gap and gap > 0 and n_fn >= 5:
            flag = "  ← ⚠ 地图说有缺口但我们有 %d 个函数" % n_fn
        print(
            "%-22s %8s %10d %10d%s"
            % (label, gap if gap is not None else "?", n_fn, n_md, flag)
        )
    total_gap = sum(gaps.values()) if gaps else 0
    print()
    print("地图缺口合计（**MCP 暴露面口径，非能力口径**）: %d" % total_gap)
    print(
        "已分类函数: %d / 未归类: %d"
        % (len(funcs) - len(ours["⑰ 未归类"]), len(ours["⑰ 未归类"]))
    )
    print()
    print("⚠ 两个数字**不可合并**：")
    print("   「地图缺口」= 四家以 MCP 工具暴露、而本仓库没有以 MCP 工具暴露的操作数")
    print("   「我们函数」= 本仓库 scripts/ 里的实现（未暴露成 MCP 工具）")
    print(
        "   ⇒ 焊件行最能说明问题：地图说缺 5，而 scripts/sw_weldment.py 有 20 个函数。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

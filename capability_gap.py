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
# 文件:   D:\AI\SW\capability_gap.py
# 定位:   AGENTS.md「报告计数要附枚举命令」；specs/002-merge-template 的 US1 交付物。
#         纠正对象是 tools/build_union_map.py 的 _our_tools() 口径 —— 该文件本身不改
#         （它是地图的一部分，动它会影响生成物），本工具只做**并存的第二口径**。
# 官方签名依据: 不适用（纯静态统计，不碰 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态统计，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
#    ⚠ 已知噪声：按函数名匹配关键词归类，同名函数会分到多个域；
#      这是**有意的**（宁可重复也不漏），故本表用于**排序**而非精确计数。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(r"C:\swprojects\sw-skill-fork")
MAP = REPO / "docs" / "union-coverage-matrix.md"
SCRIPTS = REPO / "scripts"

#: 域关键词 —— 与 build_union_map 的 16 个域对应（顺序一致，便于并排看）
DOMAIN_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("① 会话/文档/文件", ("session", "document", "doc", "file", "open", "save", "export", "import")),
    ("② 参考几何", ("plane", "axis", "point", "csys", "coordinate", "reference")),
    ("③ 草图", ("sketch", "spline", "line", "circle", "arc", "constraint", "relation")),
    ("④ 尺寸/约束/参数", ("dimension", "param", "equation", "tolerance", "gd", "mate_")),
    ("⑤ 零件特征", ("feature", "extrude", "cut", "fillet", "chamfer", "hole", "pattern", "draft", "shell", "rib")),
    ("⑥ 曲面", ("surface", "loft", "sweep", "knit", "trim_surf", "patch")),
    ("⑦ 钣金", ("sheet", "bend", "flange", "hem", "jog", "unfold")),
    ("⑧ 焊件", ("weld", "gusset", "endcap", "end_cap", "cutlist", "cut_list", "structural_member")),
    ("⑨ 模具", ("mold", "core", "cavity", "parting", "shut_off", "ripple")),
    ("⑩ 装配", ("assembl", "mate", "component", "explode", "interference")),
    ("⑪ 工程图", ("drawing", "view", "balloon", "bom", "section", "detail", "annotat")),
    ("⑫ 检查/测量/反馈", ("measure", "mass_prop", "check", "review", "validate", "inspect", "diff", "provenance")),
    ("⑬ 仿真/Motion", ("simulation", "study", "motion", "fea", "mesh", "load", "restraint", "topology", "result")),
    ("⑭ 外观/材质/配置", ("appearance", "material", "color", "render", "config", "texture")),
    ("⑮ 宏/自动化", ("macro", "vba", "script", "batch", "auto", "queue", "worker", "cli")),
    ("⑯ 高级/专项", ("dfm", "costing", "routing", "pdm", "dimxpert", "topology", "ocp", "smooth")),
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


def map_gap_counts() -> dict[str, int]:
    """从地图 §五 抽每域的「缺口」数（地图口径 = MCP 暴露面）。"""
    out: dict[str, int] = {}
    if not MAP.is_file():
        return out
    for line in MAP.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*([①-⑰][^|]*?)\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*\*\*(\d+)\*\*\s*\|", line)
        if m:
            out[m.group(1).strip()] = int(m.group(8))
    return out


def main() -> int:
    funcs = our_functions()
    ours = ours_by_domain(funcs)
    gaps = map_gap_counts()
    mods = len({m for m, _ in funcs})
    print("本仓库能力面：%d 个 scripts/sw_*.py 模块 / %d 个公开函数" % (mods, len(funcs)))
    print()
    print("%-22s %8s %10s %10s" % ("域", "地图缺口", "我们函数", "我们模块"))
    print("-" * 54)
    for label, _ in DOMAIN_KEYWORDS:
        n_fn = len(ours.get(label, ()))
        n_md = len({m for m, f in funcs if f in ours.get(label, ())})
        gap = gaps.get(label)
        flag = ""
        if gap and gap > 0 and n_fn >= 5:
            flag = "  ← ⚠ 地图说有缺口但我们有 %d 个函数" % n_fn
        print("%-22s %8s %10d %10d%s" % (label, gap if gap is not None else "?", n_fn, n_md, flag))
    total_gap = sum(gaps.values()) if gaps else 0
    print()
    print("地图缺口合计（**MCP 暴露面口径，非能力口径**）: %d" % total_gap)
    print("已分类函数: %d / 未归类: %d"
          % (len(funcs) - len(ours["⑰ 未归类"]), len(ours["⑰ 未归类"])))
    print()
    print("⚠ 两个数字**不可合并**：")
    print("   「地图缺口」= 四家以 MCP 工具暴露、而本仓库没有以 MCP 工具暴露的操作数")
    print("   「我们函数」= 本仓库 scripts/ 里的实现（未暴露成 MCP 工具）")
    print("   ⇒ 焊件行最能说明问题：地图说缺 5，而 scripts/sw_weldment.py 有 20 个函数。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

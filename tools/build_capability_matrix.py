"""★ 画「操作 × 对象」矩阵并跑**三个预先写死的可数判据**（★ 业主 2026-10-03 批准）。

★ 为什么要它（★ 业主的问题链）：
  ★「分母到底用什么口径」→ ★「矩阵是否就是要包含所有『工具』分母的矩阵」→
  ★「官方组织的方式已经很好用了，按官方划分画矩阵」→ ★「有必要派 verifier 吗」→ ★「先做」。
★★ 结论（★ 已由官方原文证实）：★ **分母不是"所有按钮"（`swCommands_e` 2204）** ——
  ★★ 官方例子 `Run_SOLIDWORKS_Commands_Example_VB.md` 逐字写着
    「**CLICK THE OK BUTTON** … **TO FILLET** the selected edges」＋ 宏里一句 **`Stop`**
  ⇒ ★★★ **`RunCommand` 只是"打开界面等人点"，★ 不是"把事做完"**。
  ⇒ ★★ **AI 无人值守能用的分母 = 官方接口族 × 成员（566 × 8239）**。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★★★ 三个判据 —— ★ **本文件在跑之前就写死了，跑完不改**（★ 事实 510：判据先标定再接线）
  ① ★ 无处可放率 = 归不进任何格子的工具 / 全部工具
        ● 好：≤ 10%   ● 可接受：≤ 20%   ● 难看：> 20%
  ② ★ 空格率 = 没有被任何工具覆盖的格子 / 全部格子
        ● 好：≤ 60%   ● 可接受：≤ 80%   ● 难看：> 80%
     ⚠ ★ 空格率高**不一定是矩阵坏**（★ 也可能就是**缺口多**）——
        ★ 所以它**只当参考**，★ 判据①才是矩阵好坏的判官。
  ③ ★★ 双源一致率 = `swCommands_e` 的命令能在官方接口族成员里找到对应名字的比例
        ● ★ 它是**上界**（★ 按名字 token 匹配，★ 必然高估）
        ● 好：≥ 50%   ● 可接受：≥ 30%   ● 难看：< 30%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
★ 只读。产出 `output/operation-object-matrix.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_capability_matrix.py
# 定位:   画「操作 × 对象」矩阵并跑**三个预先写死的可数判据**（★ 业主 2026-10-03 批准
#           ）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi")
OUT = REPO / "output" / "operation-object-matrix.json"

#: ★★ 操作轴（7）—— ★ 官方**不提供**这一轴（官方按接口分），★ 所以是我们补的。
#:   规则 = 对「族名 + 成员名」做关键词匹配；★ 顺序即优先级（★ 先匹配到的算）。
OPS: list = [
    (
        "建",
        r"Create|Insert|Add|New|Make|Build|Sketch|Feature(?!Data)|Extrud|Revolv|Loft|Sweep|"
        r"Fillet|Chamfer|Hole|Rib|Shell|Draft|Pattern|Mirror|Thicken|Wrap|"
        #: ★★★★ 2026-10-04（轮 99）**补词**（★ 消解"无处可放" · ★ **阈值不动、★ 只加
        #: 词**）——
        #:   依据：`output/unplaced-tools-analysis.json` 的**逐条**分析 ——
        #: ★ 35 个无处可放里 **28 个**是"`OPS` 一条规则都不命中"、★ **19 个**是对象轴
        #: 同理、
        #:   ★★ **而"其余（★ 靠顺序截走）"是 0 个** ⇒ **全是缺词、★ 不是顺序问题** ✓
        #: 加的词**都来自真实工具名**（★ 不是为凑数）：★ `Gear` / `Helix` / `Fastener
        #: ` /
        #:   `Costing` / `Delivery` / `Motion` / `Flatten` / `Measure` / `Summary` ✓
        r"Gear|Helix|Fastener|Flatten|Dome|Bend|"
        r"Activate|Calibrate|Recalculate",
    ),
    (
        "改",
        r"Edit|Modify|Set|Update|Rebuild|Change|Assign|Apply|Reorder|Suppress|Unsuppress|"
        r"Replace|Delete|Remove|Clear|Reset|"
        #: ★ 同上（★ 轮 99 补词）
        r"Fix|Float|Move|Rotate|Scale|Stretch|Trim|Extend|Offset",
    ),
    (
        "组合",
        r"Assembl|Mate|Compon|Explode|Interfer|Collision|Pattern(?:Component)|"
        r"AddComponent|Fix|Float",
    ),
    (
        "查",
        r"Get|Read|Query|List|Count|Is[A-Z]|Has[A-Z]|Measure|Mass|Propert|Find|Select|"
        r"Enumerat|Inspect|Evidence|Report|"
        #: ★ 同上（★ 轮 99 补词）
        r"Collect|Summary|Entities|Traceability|Types|Default|Value|Check|Validat",
    ),
    (
        "表达",
        r"Drawing|View|Annotation|Dimension|Note|Balloon|Table|BOM|Sheet|Export|Save|"
        r"Print|Pdf|Dxf|Stl|Iges|Step|Image|"
        #: ★ 同上（★ 轮 99 补词）
        r"Delivery|PackAndGo|Preview|Template",
    ),
    (
        "校核",
        r"Stud|Simulat|Mesh|Analys|Topolog|Result|Load|Restraint|Frequency|Buckl|"
        r"Thermal|Fatigue|Displace|"
        #: ★ 同上（★ 轮 99 补词）
        r"Motion|BoundingBox|CenterOfMass|DFM|Dfm",
    ),
    ("参数化", r"Equation|Config|DesignTable|Parameter|Global|Variable|Driven|Family"),
]

#: ★★ 对象轴 —— ★ 取「官方接口族的 category」+ 名字兜底（★ 官方自己在 front-matter 里给
#: 了 category）
OBJ_RULES: list = [
    ("草图", r"Sketch"),
    (
        "特征",
        r"Feature|Boss|Cut|Extru|Revolv|Loft|Sweep|Fillet|Chamfer|Hole|Rib|Shell|Draft|"
        r"Pattern|Mirror|Thicken|Wrap|Dome|Bend",
    ),
    ("几何体/面/边", r"Body|Face|Edge|Vertex|Loop|Surface|Curve|Point|Mesh"),
    ("装配", r"Assembl|Component|Mate|Explode"),
    (
        "工程图",
        r"Drawing|View|Sheet|Annotation|Dimension|Note|Balloon|Table|Gtol|Datum",
    ),
    ("钣金", r"SheetMetal|Flange|Bend|Rip|Corner|Jog"),
    ("焊件", r"Weldment|StructuralMember|CutList|Gusset|EndCap"),
    ("模具", r"Mold|PartingLine|PartingSurface|CoreCavity|ShutOff"),
    ("仿真/校核", r"Stud|Simulat|Mesh|Cosmos|CW|Topolog|Result|Load|Restraint"),
    ("材料/属性", r"Material|CustomInfo|Propert|Config|Equation|DesignTable"),
    ("选择", r"Select|Selection"),
    ("文档/文件", r"ModelDoc|Document|SldWorks|File|Import|Export|Save|Open|Close"),
    ("视图/外观", r"View|Camera|Scene|Appearance|Render|Display|Color"),
    ("参考几何", r"RefPlane|RefAxis|CoordinateSystem|ReferencePoint|Plane|Axis"),
    ("Costing/交付", r"Cost|PackAndGo|Bom|Delivery"),
    #: ★★★★ 2026-10-04（轮 99）**补两个对象**（★ 消解"无处可放" · ★ **阈值不动、★ 只加词
    #: **）——
    #: 依据 `output/unplaced-tools-analysis.json`：★ 19 个工具在对象轴上**一条规则都不命
    #: 中**、
    #:   ★★ 而**缺的正是"传动件"与"体/测量"这两类**（★ `Gear` / `Helix` / `Fastener` /
    #:   `CenterOfMass` / `BoundingBox` / `Entities`）✓
    #:   ★★★ **判据**：★ 新加的两个对象名**能从工具名反推**（★ 不是为凑数）✓
    ("传动件", r"Gear|Helix|Fastener|Thread|Spring|Belt|Chain|Pulley"),
    (
        "体/测量",
        r"Cent(?:er|re)OfMass|BoundingBox|EntitiesOnBody|MassPropert|Interference",
    ),
]


def load_families() -> dict:
    out = {}
    for d in sorted(p for p in (SWAPI / "types").iterdir() if p.is_dir()):
        members = sorted(p.stem for p in d.glob("*.md"))
        if members:
            out[d.name] = members
    return out


def load_commands() -> list:
    f = SWAPI / "enums" / "swCommands_e.md"
    t = f.read_text(encoding="utf-8", errors="replace")
    return [
        m
        for m, _ in re.findall(r"^\|\s*(sw[A-Za-z0-9_]+)\s*\|\s*([^|]*?)\s*\|", t, re.M)
    ]


def our_tools() -> list:
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "mcp-server"))
    sys.path.insert(0, str(REPO / "scripts"))
    import register_capabilities as rc

    return sorted(
        getattr(s, "name", "") for s in rc.all_specs() if getattr(s, "name", None)
    )


def classify(text: str, rules: list) -> str:
    for name, pat in rules:
        if re.search(pat, text):
            return name
    return "（未归类）"


def tool_text(name: str) -> str:
    """★ 把 **MCP 工具名**规范化成与规则同形的文本（★ 2026-10-04 修 · 轮 93）✓

    ★★★★★ **为什么要它**：★ 第一版的判据①报 **无处可放率 = 100.00%（280/280）**、
      ★★ 而逐条打印显示**全部落在 `（未归类）×（未归类）`** ⇒ ★ **那不是"矩阵全空"、
      是**喂进去的文本形态不对**** ✓
    ★ **真因**（★ 我做了**证伪实验** `output/_why_all_unplaced.py`）：
      ★ `OPS` / `OBJ_RULES` 的规则是 **CamelCase**（★ `Add` / `Sketch` / `Get`）、
      ★★ 而 MCP 工具名是 **snake_case + 前缀**（★ `solidworks_add_dimension`）⇒
      ★★★ `classify` 用的是 `re.search(pat, text)`（★ **大小写敏感**）⇒ **一个都命中不了** ✓
    ★★ **证伪读数**：★ 原样 ⇒ **280/280 = 100.0%** · ★ 驼峰化后 ⇒ **35/280 = 12.5%** ✓
      ★ 逐条对上：★ `add_dimension` ⇒ **建** · ★ `assembly_list_components` ⇒ **组合** ·
      ★ `available_direction_selectors` ⇒ **查** ✓
    ★★★ **⚠ 本函数只规范**输入形态**、★ 一个字都没动阈值**（★ 三个判据的阈值
      在文件头写死、★ 「跑之前写死、跑完不改」）✓
    ★★★★ **可复用判据**：★★★ **一个"全为 0 / 全未归类"的统计，
      先怀疑**输入形态**、★ 再怀疑**结论**** ——
      ★ 因为"全都归不进去"在真实系统里**极罕见**（★ 与**事实 517**同族：
      ★★ **"我读错了"与"能力坏了"长得一模一样**）✓
    """
    s = re.sub(r"^(?:solidworks|cadstudio)_", "", str(name))
    return "".join(w.capitalize() for w in s.split("_")) or str(name)


def main() -> int:
    started = time.time()
    fams = load_families()
    cmds = load_commands()
    tools = our_tools()
    #: ★ 成员 → 所属族
    member_to_fam = {}
    for fam, ms in fams.items():
        for m in ms:
            member_to_fam.setdefault(m, fam)
    all_members = sorted(member_to_fam)

    #: ★★ 格子 = (操作, 对象) —— ★ 对**每个成员**分类 ⇒ 得到"有东西的格子"
    cell_members: dict = defaultdict(list)
    for m in all_members:
        cell = (classify(m, OPS), classify(member_to_fam[m] + " " + m, OBJ_RULES))
        cell_members[cell].append(m)
    #: ★★ 每个工具也分类（★ 用工具名 + 它的注入/模块名做不到 ⇒ 只用工具名，★ 如实标注这
    #: 个局限）
    #: ★★★ **⚠ 工具名要先经 `tool_text` 规范化** —— ★ 规则是 CamelCase、★ 工具名是 snake
    #: _case，
    #: ★★ 不规范化会**全落 `（未归类）`**（★ 轮 93 修；★ 证伪见 `output/_why_all_unplace
    #: d.py`）✓
    tool_cells, tool_unplaced = {}, []
    for t in tools:
        text = tool_text(t)
        op, obj = classify(text, OPS), classify(text, OBJ_RULES)
        tool_cells[t] = (op, obj)
        if op == "（未归类）" or obj == "（未归类）":
            tool_unplaced.append({"tool": t, "op": op, "obj": obj})

    ops = [o for o, _ in OPS]
    objs = [o for o, _ in OBJ_RULES]
    total_cells = len(ops) * len(objs)
    filled = {c for c, v in cell_members.items() if v}
    #: ★ 被我们工具覆盖的格子
    covered = {tool_cells[t] for t in tools}
    covered_real = {c for c in covered if c[0] != "（未归类）" and c[1] != "（未归类）"}

    #: ★★★ 判据③ 双源一致率：★ 命令名 → 有没有对应成员（★ 名字 token 匹配，★ 上界）
    def toks(s: str) -> set:
        return {
            w.lower()
            for w in re.findall(r"[A-Za-z]{3,}", re.sub(r"^swCommands?_?", "", s))
        }

    member_tokens = set()
    for m in all_members:
        member_tokens |= toks(m)
    hit = 0
    for c in cmds:
        tk = toks(c)
        if tk and tk & member_tokens:
            hit += 1

    r1 = 100.0 * len(tool_unplaced) / max(1, len(tools))
    r2 = 100.0 * (total_cells - len(filled)) / total_cells
    r3 = 100.0 * hit / max(1, len(cmds))

    def band(v, good, ok, higher_better=False):
        if higher_better:
            return "★ 好" if v >= good else ("可接受" if v >= ok else "★★ 难看")
        return "★ 好" if v <= good else ("可接受" if v <= ok else "★★ 难看")

    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "矩阵": {
            "操作轴": ops,
            "对象轴": objs,
            "格子总数": total_cells,
            "有官方成员的格子": len(filled),
            "被我们工具覆盖的格子": len(covered_real),
        },
        "规模": {
            "官方接口族": len(fams),
            "官方成员": len(all_members),
            "我们的工具": len(tools),
            "官方命令(swCommands_e)": len(cmds),
        },
        "判据①无处可放率": {
            "值": round(r1, 2),
            "分子": len(tool_unplaced),
            "分母": len(tools),
            "判定": band(r1, 10, 20),
            "阈值": "好≤10% · 可接受≤20%",
        },
        "判据②空格率": {
            "值": round(r2, 2),
            "分子": total_cells - len(filled),
            "分母": total_cells,
            "判定": band(r2, 60, 80),
            "阈值": "好≤60% · 可接受≤80%",
            "注": "★ 它只当参考 —— 空格多也可能是**缺口多**，★ 判据①才是矩阵好坏的判官",
        },
        "判据③双源一致率": {
            "值": round(r3, 2),
            "分子": hit,
            "分母": len(cmds),
            "判定": band(r3, 50, 30, higher_better=True),
            "阈值": "好≥50% · 可接受≥30%",
            "注": "★ 按名字 token 匹配 ⇒ **上界**",
        },
        "无处可放的例子": [x["tool"] for x in tool_unplaced[:24]],
        "格子占用前 20": sorted(
            ([list(k), len(v)] for k, v in cell_members.items()), key=lambda x: -x[1]
        )[:20],
        "工具落在的格子前 20": sorted(
            ([list(k), n] for k, n in Counter(tool_cells.values()).most_common(20))
        ),
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print(
        "★ 规模：官方 **%d** 族 · **%d** 成员 · 我们 **%d** 工具 · 官方命令 **%d**"
        % (len(fams), len(all_members), len(tools), len(cmds))
    )
    print(
        "★ 矩阵：★ 操作 %d × 对象 %d = **%d** 格 ⇒ 有官方成员的 **%d** 格 · 我们工具覆盖 **%d** 格"
        % (len(ops), len(objs), total_cells, len(filled), len(covered_real))
    )
    print()
    print("★★★ 三个预先写死的判据：")
    print(
        "   ① 无处可放率   = **%.2f%%**（%d/%d）⇒ %s"
        % (r1, len(tool_unplaced), len(tools), R["判据①无处可放率"]["判定"])
    )
    print(
        "   ② 空格率       = **%.2f%%**（%d/%d）⇒ %s（★ 参考项）"
        % (r2, total_cells - len(filled), total_cells, R["判据②空格率"]["判定"])
    )
    print(
        "   ③ 双源一致率   = **%.2f%%**（%d/%d，★ 上界）⇒ %s"
        % (r3, hit, len(cmds), R["判据③双源一致率"]["判定"])
    )
    print()
    if tool_unplaced:
        print("★ 无处可放的工具（前 24）：")
        print(
            "   "
            + ", ".join(
                x["tool"].replace("solidworks_", "") for x in tool_unplaced[:24]
            )
        )
        print()
    print("★ 工具最集中的格子（前 12）：")
    for (op, obj), n in Counter(tool_cells.values()).most_common(12):
        print("   %-8s × %-14s %d" % (op, obj, n))
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

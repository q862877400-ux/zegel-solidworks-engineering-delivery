"""生成 `docs/metrics.md` —— 项目里**所有对外引用的数字**，逐条给「定义 / 口径 / 当前值 / 重算命令」。

## 为什么要它（2026-10-01 轮 217，地基①）
一次会话里我撞到**同一个词两个意思**至少五处（并集 439 vs 349 · 成员 15,466 vs 8,238 ·
函数 692/657/1,390 · 工具 99/58/103 · 缺口 336 是逐域相加）。
⇒ ★ **数字只要有两个来源，迟早会打架。** 本文件是**唯一来源**：
  散文里引用数字必须指向本文件；本文件里的每个数**都由这里的代码现算**（不抄别处）。

## 同时落「验证分级」（地基②）
`hit`（名字在代码里出现过）实测是 **100.0%** —— ★ 因为我们的全量索引把 774 族的名字都抄了
⇒ 那个数**没有判别力**，却被当成"覆盖广"。
⇒ ★ 所以本文件把两个数**永远并列**：
    · **静态缝合覆盖** —— 名字层面被包进函数的成员比例（宽口径，说明"抄准了签名"）
    · **真机验证覆盖** —— 真有运行证据的成员比例（窄口径，说明"真能用"）
  ★ 任何"覆盖广"的说法**必须同时带这两个数**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本工具为原创；生成器与产物**同仓**，见 docs/plan-foundation.md 地基④）
# 文件:   tools/gen_metrics.py —— 本文件自身
# 定位:   docs/metrics.md 的生成器。地基①+②的落地。
# 官方依据: 不适用（本项目内部统计）
# 许可:   本仓库 MIT
# ⚠ 本工具只做**静态统计**，不连 SolidWorks；凡"真机"相关的数都只数**证据文件**，不重新跑。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
WS = Path(r"D:\AI\SW")
SWAPI = Path(r"C:\swapi")
OUT = ROOT / "docs" / "metrics.md"

DEF_RE = re.compile(r"(?m)^\s*(?:async\s+)?def\s+([a-z_]\w*)\s*\(")
TOP_DEF = re.compile(r"(?m)^def ([A-Za-z_]\w*)\s*\(")          #: 只抓**顶格**的 def（含 _ 开头）
ANY_DEF = re.compile(r"(?m)^\s*(?:async\s+)?def\s+([a-z_]\w*)\s*\(")  #: 含缩进（类方法与嵌套函数）
CAT_RE = re.compile(r"(?im)^\s*\*{0,2}category\*{0,2}\s*[:：]\s*(.+)$")

rows: list[tuple[str, str, str, str]] = []   #: (指标, 定义/口径, 值, 重算命令)


def add(metric: str, definition: str, value, cmd: str) -> None:
    rows.append((metric, definition, str(value), cmd))


def pys(*subs: str, pattern: str = "*.py"):
    out = []
    for s in subs:
        out += [p for p in (ROOT / s).rglob(pattern) if "__pycache__" not in str(p)]
    return out


def defs(files) -> tuple[int, set]:
    n, names = 0, set()
    for p in files:
        found = DEF_RE.findall(p.read_text(encoding="utf-8", errors="replace"))
        n += len(found)
        names |= set(found)
    return n, names


def main() -> int:
    fc = json.loads((ROOT / "docs" / "family-coverage.json").read_text(encoding="utf-8"))

    # ── A. 官方给的 ──────────────────────────────────────────────
    mem_files = [p for p in SWAPI.glob("types/**/*.md") if p.name != "_overview.md"]
    mem_names = {p.stem for p in mem_files}
    add("接口族（Interface）", "官方按功能分的「组」，例如 IFeatureManager", len(fc),
        "读 docs/family-coverage.json 的行数")
    add("成员位次（接口×成员）", "同一个成员名出现在 N 个接口里就算 N 次", sum(r["members"] for r in fc),
        "family-coverage.json 各行 members 相加")
    add("★ 不重复成员名", "同名只算一次（★ 与上一行**不是**同一个东西）", len(mem_names),
        "C:\\swapi\\types\\*\\*.md 的**文件名**去重（一个成员一个文件）")
    cats = set()
    for p in mem_files:
        m = CAT_RE.search(p.read_text(encoding="utf-8", errors="replace"))
        if m:
            cats.add(m.group(1).strip())
    add("官方分类种数", "官方 category 字段的不同取值个数", len(cats), "扫 C:\\swapi\\types 的 category 字段去重")
    add("枚举", "官方的固定取值清单", len(list((SWAPI / "enums").glob("*.md"))), "C:\\swapi\\enums\\*.md")
    add("官方示例文件", "官方给的用法示例页", len(list((SWAPI / "examples").glob("*.md"))), "C:\\swapi\\examples\\*.md")
    add("CHM 解包文件", "安装自带说明书解出来的文件", len([p for p in (WS / "AI Solidworks" / "官方文档").rglob("*") if p.is_file()]),
        "D:\\AI\\SW\\AI Solidworks\\官方文档 下的文件数")

    # ── B. 接口族的四种状态 ──────────────────────────────────────
    unc = [r for r in fc if str(r.get("domain", "")).startswith("全量索引/")]
    add("归到业务分类的族", "domain 是 14 个业务域之一", len(fc) - len(unc), "family-coverage.json 里 domain 不以「全量索引/」开头的行数")
    add("未认领的族", "domain 是「全量索引/<程序集>」（未归业务域）", len(unc), "同上，取其补集")
    add("我们调用过的族", "该族有成员被使用过（used > 0）", sum(1 for r in fc if (r.get("used") or 0) > 0), "family-coverage.json 里 used > 0 的行数")
    add("零调用族", "该族一个成员都没被调用过", sum(1 for r in fc if (r.get("used") or 0) == 0), "同上，used == 0")

    # ── C. 我们自己写的 ─────────────────────────────────────────
    sw_files = sorted((ROOT / "scripts").glob("sw_*.py"))
    sw_raw, sw_uniq = defs(sw_files)
    #: ★ 两个口径必须分开（2026-10-01 轮 217 撞出来的）：
    #:   `TOP_DEF` 只抓**顶格**的 def ⇒ 那是"能挂成工具的候选"（657）
    #:   允许缩进会连**类方法与嵌套函数**一起抓（859）⇒ 那个数**不可与「工具」相比**
    top = set()
    anydef = 0
    for p in sw_files:
        t = p.read_text(encoding="utf-8", errors="replace")
        top |= set(TOP_DEF.findall(t))
        anydef += len(ANY_DEF.findall(t))
    top_public = {n for n in top if not n.startswith("_")}
    sw_any = anydef
    prod_raw, prod_uniq = defs(pys("scripts", "mcp-server"))
    add("函数（顶格，含 _ 开头）", "scripts/sw_*.py 里**顶格**的 def（含 _ 开头的内部函数）", len(top),
        "python tools/gen_metrics.py（本行由 tools/ 现算）")
    add("★ 公开函数（可挂工具的候选）", "顶格**且不以 _ 开头**的 def。"
        "⚠ 不含类方法与嵌套函数 —— 那些不是候选", len(top_public),
        "同上前提下，名字不以 _ 开头")
    add("函数（含类方法与嵌套）", "scripts/sw_*.py 里所有 def（含缩进的）—— ★ 与上一行**不是同一个东西**，不可与「工具」相比",
        sw_any, "正则允许前导空白，抓缩进的 def")
    add("函数（含工具层与声明层）", "scripts/ + mcp-server/ 里的 def", prod_raw, "同上，扫两个目录")
    add("测试文件", "tests/ 下的 test_*.py", len(list((ROOT / "tests").glob("test_*.py"))), "C:\\swprojects\\sw-skill-fork\\tests\\test_*.py")

    # ── D. MCP 工具 ─────────────────────────────────────────────
    sys.path.insert(0, str(ROOT / "mcp-server"))
    import register_capabilities as rc                                    # noqa: E402
    ours_decl = rc.all_specs()
    srv = (ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="replace")
    upstream = len(re.findall(r"@mcp\.tool", srv))
    add("MCP 工具（我们新登记）", "tool_specs_batch*.py 的声明条目", len(ours_decl), "register_capabilities.all_specs()")
    add("MCP 工具（上游原有）", "server.py 里的 @mcp.tool 装饰器", upstream, "server.py 里 @mcp.tool 出现次数")
    add("★ MCP 工具合计", "上面两行相加（AI 能调的按钮总数）", len(ours_decl) + upstream, "两行相加")

    # ── E. 与四家比 ─────────────────────────────────────────────
    u = json.loads((ROOT / "tools" / "union-sources.json").read_text(encoding="utf-8"))
    tu = len(u.get("union_operations") or [])
    tsum = sum(len(s.get("tools") or []) for s in u["sources"])
    add("四家工具数（原始相加）", "四家各自工具数直接相加（有重名，会虚高）", tsum, "union-sources.json 的 sources[].tools 长度相加")
    add("★ 四家工具数（去重＝并集）", "去掉重名后的总数（★ 与上一行不是同一个东西）", tu, "union-sources.json 的 union_operations 长度")

    # ── F. 能力清单与记录 ───────────────────────────────────────
    cap = (ROOT / "capabilities.yaml").read_text(encoding="utf-8")
    lv = re.findall(r'"level":\s*"(\w+)"', cap)
    add("能力清单条目", "capabilities.yaml 的条目数", len(lv), "capabilities.yaml 里 level 字段出现次数")
    add("  其中 verified", "有我们自己的运行证据", lv.count("verified"), "同上，按取值分组")
    add("  其中 stitched", "代码写好但没真机跑过", lv.count("stitched"), "同上")
    add("  其中 not_implemented", "没做", lv.count("not_implemented"), "同上")
    add("门禁", "scripts/check_*.py 的自动检查程序", len(list((ROOT / "scripts").glob("check_*.py"))), "scripts/check_*.py")
    kf = (WS / "docs" / "known-facts.md").read_text(encoding="utf-8")
    add("已知事实条数", "docs/known-facts.md 里编号的条目", len(re.findall(r"(?m)^\| \d+ \|", kf)), "known-facts.md 里 ^| N | 的行数")
    add("Spec Kit 特性", "specs/<NNN>-* 目录数", len([d for d in (WS / "specs").iterdir() if d.is_dir() and re.match(r"^\d{3}-", d.name)]),
        "D:\\AI\\SW\\specs 下形如 NNN- 的目录数")

    # ── G. ★★ 验证分级（地基②）────────────────────────────────
    #: ⚠⚠ 2026-10-01 轮 217：**本段第一版有 bug** —— 我写了
    #:     `len({p.stem for p in pys(...)} and mem_names)`，那是**真值判断**（非空集合为真）
    #:     ⇒ 恒等于分母 ⇒ 印出"100.0%"。★ 而 100.0% 正是本轮要拆穿的那个**无判别力**的数。
    #:   ⇒ 修法：**三个口径分开报，且把无判别力的那个明确标注出来**。
    hit = sum(r.get("hit") or 0 for r in fc)
    used = sum(r.get("used") or 0 for r in fc)
    total_slots = sum(r["members"] for r in fc)
    ev_files = sorted((ROOT / "tools").glob("capture_*.py"))
    probes = sorted(WS.glob("probe*.py"))
    lo: set = set()
    for p in ev_files + probes:
        t = p.read_text(encoding="utf-8", errors="replace")
        for line in t.splitlines():
            for name in re.findall(r"[\"']([A-Za-z_]\w*)[\"']|\b([A-Z]\w+)\s*\(", line):
                nm = name[0] or name[1]
                if nm in mem_names:
                    lo.add(nm)
    add("覆盖口径 ①「名字出现过」（宽）",
        "台账 hit / 成员位次。★★ **无判别力** —— 我们的全量索引把 774 族的名字都抄了，"
        "所以它必然接近 100%，**不能用来说「覆盖广」**",
        "%.1f%%（%d / %d）" % (100.0 * hit / max(total_slots, 1), hit, total_slots),
        "family-coverage.json 各行 hit 相加 ÷ members 相加")
    add("覆盖口径 ②「真的被调用」（中）",
        "台账 used / 成员位次 —— 代码里真的有调用，不只是抄了名字",
        "%.1f%%（%d / %d）" % (100.0 * used / max(total_slots, 1), used, total_slots),
        "family-coverage.json 各行 used 相加 ÷ members 相加")
    add("★ 覆盖口径 ③「真机碰过」（窄）",
        "证据/探针脚本里出现过的**官方成员名**（下界；★ 这个才是「真能用」的证据）",
        "%.2f%%（%d / %d 个不重复成员名）" % (100.0 * len(lo) / max(len(mem_names), 1), len(lo), len(mem_names)),
        "python tools/gen_metrics.py（扫 capture_*.py + 工作区 probe*.py）")
    add("真机证据脚本", "产出证据文件的脚本（仿真 / 拓扑两条链）", len(ev_files), "tools/capture_*.py")
    add("真机探针脚本", "为查清行为而真机跑过的探针", len(probes), "D:\\AI\\SW\\probe*.py")

    # ── 输出 ────────────────────────────────────────────────────
    L = ["# 项目数字（唯一来源）", "",
         "> **本文件是生成物** —— 由 `tools/gen_metrics.py` 现算，**不要手改**。",
         "> ★ 散文里引用数字**必须指向本文件**；同一个词**只允许一个定义**。",
         "> 重算：`python tools/gen_metrics.py`", "",
         "| # | 指标 | 定义 / 口径 | 当前值 | 重算命令 |", "|---|---|---|---|---|"]
    for i, (m, d, v, c) in enumerate(rows, 1):
        L.append("| %d | %s | %s | **%s** | `%s` |" % (i, m, d, v, c))
    L += ["",
          "## ★ 两条纪律（地基②）",
          "```",
          "1. 「静态缝合覆盖」与「真机验证覆盖」**必须永远并列出现** ——",
          "   只说前者会让人以为「都能用」，只说后者会让人以为「什么都没做」。",
          "2. 任何「覆盖广 / 全覆盖」的说法，**必须带那个真机数**。",
          "```", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    for m, _d, v, _c in rows:
        print("  %-34s %s" % (m, v))
    print("")
    print("  产物:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

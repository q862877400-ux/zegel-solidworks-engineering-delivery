"""★ 生成 `docs/tools-index.md`：709 个开发工具的**可检索索引**（按 lean 口径）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/gen_tools_index.py
# 定位:   业主 2026-10-19 的原话：「tools/ 是这个项目的开发工具吗，那么多工具怎么用是
#           有文档还是怎么说，不然这些什么探针什么工具，越积累越多，最后可能遇到问题每次
#           都重写，而不是从多如牛毛的历史工具里找了」
#         ★ 现状实测：`tools/*.py` **709 个 / 5.6 MB**，`tools/README.md` **不存在**，
#           `docs/tools-index.md` **不存在** ⇒ ★ 没有任何索引。
#         ★★ 已有门禁 `scripts/check_probe_reuse.py` 只拦「明明有工具你还重写」，
#            ★ **拦不住「你不知道有，所以你没找」** —— 那是**可发现性**问题。
# 官方依据: 不适用（本仓内部工具面）。★ 设计约束来自本仓自己的 lean 实测：`docs/recon/le
#           an-tool-surface.md`  与 `specs/215-tool-surface-decisions/spec.md` ——  ★★ 「
#           lean 投影只保留**第一句**、且截断到 **120 字**」⇒  ★ 索引的每一行**必须把结
#           论放在第一句 120 字内**，否则模型看不到。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `tools/*.py`（全量）→ `docs/tools-index.md`
# ⚠ 本脚本**不连 SolidWorks**，纯静态读文件头。
# -----------------------------------------------------------------------------
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 事实 58

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
OUT = ROOT / "docs" / "tools-index.md"

#: ★ lean 口径：第一句 + 120 字（与 `@local/dsh-lean-mode` 的 `firstLine()` 同源）。
LEAN_CHARS = 120

#: ★ 无文件头说明时的占位文案（★ 与 `scripts/check_tools_index_fresh.py` 的 NODESC 必须
#: 同一句）
NODESC = "★ **无文件头说明**（该脚本没写 docstring / 首行注释）"

#: ★ 分类：按**文件名前缀**分（机械、零歧义），每类给一句「什么时候该用它」。
#: ⚠ 前缀之外的落 `其他` —— ★ 不硬猜语义（事实 53：启发式硬凑会错）。
CATEGORIES = [
    ("probe", "探针", "真机验证某个 API 到底能不能用 / 怎么调"),
    ("prove", "取证", "把探针结论落成可复现的证据"),
    ("verify", "冒烟/回归", "验证某能力端到端仍然可用"),
    ("check", "门禁", "静态检查，违反即红（部分在 scripts/ 下）"),
    ("gen", "生成器", "从真源生成文档/索引（跑完要提交生成物）"),
    ("audit", "审计", "对账/查缺口，只读不改"),
    ("capture", "证据采集", "真机跑一遍并把结果落盘成证据"),
    ("measure", "度量", "量一个数（覆盖率/误报率/成本）"),
    ("build", "构建索引", "从官方源建结构化索引"),
    ("scan", "扫描", "全仓扫描找某种形态"),
    ("triage", "分诊", "给条目分类/定处置"),
    ("report", "报告", "生成给人看的报告"),
    ("run", "编排运行", "按规格串多个阶段跑"),
    ("list", "清单", "列出某类条目"),
    ("analyze", "分析", "对某类数据做分析"),
    ("judge", "裁判", "对候选做判定"),
    #: ★ 2026-10-19 补：把「其他」从 150 个压下来（实测前缀分布后加的，不是猜的）。
    ("diag", "诊断", "查某现象为什么发生（不改任何东西）"),
    ("add", "批量追加", "往台账/清单里批量加条目（★ 一次性居多）"),
    ("fix", "修复", "按已知根因批量改文件"),
    ("extract", "提取", "从官方源或日志里抽出结构"),
    ("spotcheck", "抽检", "抽几条核对"),
    ("recheck", "复核", "对别人的结论再核一遍"),
    ("tally", "计票", "统计判定结果"),
    ("modal", "弹窗", "弹窗处置相关（配 sw_guard 用）"),
    ("sw", "真机运行器", "直接连 SolidWorks 的执行器/护栏"),
]


def first_line_of(path: Path) -> str:
    """★ 取文件头的第一句实质内容（docstring 优先，其次首行注释）。"""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    #: ① 优先 AST 取模块 docstring（最准，且能剥掉 ★/引号）
    try:
        doc = ast.get_docstring(ast.parse(text))
        if doc:
            return _first_sentence(doc)
    except (SyntaxError, ValueError):
        pass
    #: ② 退回首行注释（本仓大量文件用 `# ── 来源 ──` 风格，首行就是一句话）
    for line in text.splitlines()[:12]:
        s = line.strip()
        if not s:
            continue
        if s.startswith("#"):
            body = s.lstrip("#").strip()
            if body and not body.startswith("──") and len(body) > 4:
                return _first_sentence(body)
        elif s.startswith(('"""', "'''")):
            body = s.strip("\"'").strip()
            if len(body) > 4:
                return _first_sentence(body)
    return ""


def _first_sentence(text: str) -> str:
    """★ lean 口径：取第一句，截到 120 字。"""
    text = " ".join(text.split())
    #: 中文句号/换行/分号都算句界（与 lean 的 split(/[。\\n]/) 同精神，多认「；」）
    for sep in ("。", "；", "\n"):
        if sep in text:
            text = text.split(sep)[0]
    return text.strip()[:LEAN_CHARS]


def classify(name: str) -> tuple[str, str]:
    """★ 返回 (分类键, 中文名)。★ 前缀匹配，不猜语义。"""
    for key, label, _desc in CATEGORIES:
        if name.startswith(key + "_"):
            return key, label
    #: ★ 按**轮次/批次**命名的（`t1_*` / `t4_*` / `w6_*` / `s206_*`）——
    #:   它们不是「一种用途」，是「某一轮的临时活」⇒ 单列一类，别混进「其他」。
    #: ⚠ 判据是**命名形态**（单字母/字母数字 + 数字 + 下划线），不是语义猜测。
    if re.match(r"^(?:t\d+|w\d+|s\d+)_", name):
        return "byround", "按轮次临时"
    return "other", "其他"


def collect() -> list[dict]:
    rows = []
    for p in sorted(TOOLS.glob("*.py")):
        if p.name.startswith("_"):
            continue          #: ★ `_` 开头是内部件，不进检索面（同 lean 的「管线内部件」口径）
        key, label = classify(p.name)
        rows.append({
            "name": p.name,
            "stem": p.stem,
            "cat": key,
            "cat_label": label,
            "desc": first_line_of(p),
            "size": p.stat().st_size,
        })
    return rows


def render(rows: list[dict]) -> str:
    by_cat: dict[str, list[dict]] = {}
    for r in rows:
        by_cat.setdefault(r["cat"], []).append(r)

    out: list[str] = []
    out.append("# 开发工具索引（`tools/`）")
    out.append("")
    out.append("> ★ **本文件由 `tools/gen_tools_index.py` 生成，不要手改。**")
    out.append("> 重生成：`python tools/gen_tools_index.py`")
    out.append("")
    out.append("**为什么有这份索引**：`tools/` 有 %d 个脚本，此前没有任何索引 —— "
               "「你不知道有，所以你没找」是可发现性问题，"
               "已有门禁 `check_probe_reuse.py` 只拦「明明有你还重写」，拦不住这个。"
               % len(rows))
    out.append("")
    out.append("**怎么用**：先按「我想干什么」找到分类，再在分类里按文件名扫一眼。"
               "★ 每条的第一句就是它的用途（**lean 口径：结论在 120 字内，模型才看得见**）。")
    out.append("")
    out.append("---")
    out.append("")

    #: ★★ 先给「我想…→ 去哪个分类」的入口表（这是检索的第一跳）
    out.append("## 我想… → 去哪一类")
    out.append("")
    out.append("| 我想… | 分类 | 条数 | 目录内文件前缀 |")
    out.append("|---|---|---|---|")
    for key, label, desc in CATEGORIES:
        items = by_cat.get(key) or []
        if not items:
            continue
        out.append("| %s | **%s** | %d | `%s_*` |" % (desc, label, len(items), key))
    if by_cat.get("other"):
        out.append("| （未归入上面任何一类） | 其他 | %d | — |" % len(by_cat["other"]))
    out.append("")

    #: ★ 分类明细
    for key, label, desc in CATEGORIES + [("byround", "按轮次临时", "按轮次/批次命名的临时活（t1_/t4_/w6_/s206_ 等），不是一种长期用途"), ("other", "其他", "未按前缀归类的脚本")]:
        items = by_cat.get(key)
        if not items:
            continue
        out.append("## %s（%d 个）" % (label, len(items)))
        out.append("")
        out.append("> 用途：%s" % desc)
        out.append("")
        out.append("| 脚本 | 用途（第一句，≤%d 字） |" % LEAN_CHARS)
        out.append("|---|---|")
        for r in items:
            desc_txt = r["desc"] or NODESC
            out.append("| `%s` | %s |" % (r["name"], desc_txt.replace("|", "\\|")))
        out.append("")

    #: ★ 无说明的清单（★ 这是索引自身的债，要能一眼看见）
    nodesc = [r for r in rows if not r["desc"]]
    out.append("---")
    out.append("")
    out.append("## 索引自身的债：无文件头说明的脚本（%d 个）" % len(nodesc))
    out.append("")
    if nodesc:
        out.append("这些脚本没有 docstring 也没有首行注释 ⇒ **索引只能列出名字，说不出用途**。")
        out.append("补一行注释就能让它们可检索：")
        out.append("")
        for r in nodesc:
            out.append("- `%s`" % r["name"])
    else:
        out.append("★ 无 —— 每个脚本都有说明。")
    out.append("")
    out.append("---")
    out.append("")
    out.append("## 相关机制（别重复造）")
    out.append("")
    out.append("| 机制 | 位置 | 作用 |")
    out.append("|---|---|---|")
    out.append("| 探针复用门禁 | `scripts/check_probe_reuse.py` | 拦住「为已有工具写了替代品」 |")
    out.append("| 死路台账 | `docs/dead-ends.md` | 已走死的路，动手前先扫 |")
    out.append("| 已知事实 | `docs/known-facts.md` | 已验证的技术事实 |")
    out.append("| 假设台账 | `docs/assumption-ledger.md` | 未验证的假设（不得当证据） |")
    out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    if not TOOLS.is_dir():
        print("★ 没有 tools/ 目录")
        return 1
    rows = collect()
    text = render(rows)
    OUT.write_text(text, encoding="utf-8")
    #: ★ 落盘后回读校验（事实 48 定则②）
    again = OUT.read_text(encoding="utf-8")
    n_lines = len(again.splitlines())
    print("★ 已写 %s（%d 字节 / %d 行）" % (OUT.relative_to(ROOT), len(again.encode('utf-8')), n_lines))
    print("★ 收录 %d 个工具 · 无说明 %d 个"
          % (len(rows), len([r for r in rows if not r["desc"]])))
    for key, label, _d in CATEGORIES + [("byround", "按轮次临时", ""), ("other", "其他", "")]:
        n = len([r for r in rows if r["cat"] == key])
        if n:
            print("   %-10s %3d" % (label, n))
    n_other = len([r for r in rows if r["cat"] == "other"])
    if n_other:
        print("   %-10s %3d" % ("其他", n_other))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

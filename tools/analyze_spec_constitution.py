"""★ 跨制品一致性检查：把 `.specify` 宪法的 §I–§V 判据**跑出来**（`speckit.analyze` 的可执行版）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（SDD 制品检查器）· 依据 `.specify/memory/constitution.md` §I–§V
# 文件:   tools/analyze_spec_constitution.py
# 定位:   ★ 2026-10-03（接手轮）★ 补 **Spec Kit 全路径里我跳过的那一步**：
#   宪法 §"命令的顺序" 逐字：「本项目默认走**全路径** ——
# `constitution → specify → clarify → plan → checklist → tasks → analyze → implement → c
# onverge`」，
#   ★ 而**我只走了 specify → plan → tasks → implement** ⚠
#   ★ 且宪法自己点明：**「analyze（跨制品一致性）恰好是挡住『凭印象写 API』的那道」**。
#
#   ★★ **为什么不手写一份 analyze 报告**：★ 本仓的纪律是「**把验证责任转移到静态比对**」——
#     ★ 宪法的 §I–§V **本来就写成了可 grep 的判据**（见其每节的「判据」行）⇒
#       ★ **把它跑出来**既是 analyze 的产物，也是一道**可复用的门禁**。
#
#   ★ 用法：`python tools/analyze_spec_constitution.py specs/202-user-coverage-gaps`
#     ★ 退出码：有 `FAIL` 即 1；只有 `WARN` 即 0。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def check(spec_dir: Path):
    """★ 逐条跑宪法判据。回 `(findings, fails)`；findings 每项 `(级别, 条款, 说明)`。"""
    f, spec = [], _read(spec_dir / "spec.md")
    plan, tasks = _read(spec_dir / "plan.md"), _read(spec_dir / "tasks.md")
    recon = spec_dir / "recon"
    recon_txt = (
        "".join(_read(p) for p in sorted(recon.glob("*.md"))) if recon.is_dir() else ""
    )

    #: §I 缝合优先 —— 每条 FR 都要写「来源=」
    frs = re.findall(r"^- \*\*FR-\d+\*\*", spec, re.M)
    with_src = re.findall(r"^- \*\*FR-\d+\*\*.*?来源=", spec, re.M)
    if not frs:
        f.append(("FAIL", "§I", "spec.md 里**一条 `**FR-xxx**` 都没有**"))
    elif len(with_src) < len(frs):
        f.append(
            (
                "FAIL",
                "§I",
                "FR %d 条里只有 %d 条带「来源=」" % (len(frs), len(with_src)),
            )
        )
    else:
        f.append(("PASS", "§I", "FR %d 条**全部**带「来源=」" % len(frs)))

    #: §II 签名三源互证 —— plan 要列出三源 + 裁决顺序
    src_hits = [k for k in ("C:\\swapi", "官方文档", "_raw") if k in plan]
    has_order = ("裁决" in plan) or (">" in plan and "冲突" in plan)
    if len(src_hits) >= 3 and has_order:
        f.append(("PASS", "§II", "三源齐（%s）+ 有裁决顺序" % "/".join(src_hits)))
    else:
        f.append(
            ("FAIL", "§II", "plan.md 三源缺项或没写裁决顺序（命中 %s）" % src_hits)
        )

    #: §III 查不到就写查不到 —— 侦察产物要真的出现该字样（★ 0 处 = 可能整份在凑）
    n_missing = recon_txt.count("官方没写")
    if n_missing > 0:
        f.append(
            (
                "PASS",
                "§III",
                "侦察产物里「官方没写」出现 **%d** 处（★ 说明它敢报查不到）"
                % n_missing,
            )
        )
    else:
        f.append(
            (
                "WARN",
                "§III",
                "侦察产物里**没有**「官方没写」—— ★ 要么真的全命中，要么在凑（需人工抽查）",
            )
        )

    #: §IV 许可红线 —— plan 每行来源都要带 license
    lic = sum(1 for l in plan.splitlines() if "license" in l.lower())
    if lic >= 5:
        f.append(("PASS", "§IV", "plan.md 里带 `license` 的行 **%d** 条（≥5）" % lic))
    else:
        f.append(("FAIL", "§IV", "plan.md 带 `license` 的行只有 %d 条（<5）" % lic))

    #: §V 验收判据必须能跑 —— 任务数 == `→ 验收:` 数
    n_task = len(re.findall(r"^- \[[ x~-]\] \*\*T\d+\*\*", tasks, re.M))
    n_acc = tasks.count("→ 验收:")
    if n_task and n_task == n_acc:
        f.append(
            (
                "PASS",
                "§V",
                "任务 **%d** 条 · `→ 验收:` **%d** 条（一一对应）" % (n_task, n_acc),
            )
        )
    else:
        f.append(
            (
                "FAIL",
                "§V",
                "任务 %d 条而 `→ 验收:` %d 条 ⇒ **没有一一对应**" % (n_task, n_acc),
            )
        )

    #: 宪法 §"三处不许写" 第 1 条 —— spec 不许写「当前进度」
    #: ★ 判据**只认真正的进度形态**（`x/145` 覆盖率 · `x%` 百分数 · `x → y` 变化），
    #:   ★ **不认事实编号（`事实 47`）/ 条款编号（`第 1 条`）/ 小节号（`§五`）** ——
    #:   ★ 第一版用 `\d+\s*条` 这种粗判据，把「宪法第 1 条」「事实 47/474」也报了 11 处
    #:     ⇒ ★ **狼来了的检查会被忽略**（本仓教训：门禁的假阳性比漏报更耗人）。
    #: ★ **先剥掉"引用"再判**：`事实 47/474`、`第 1 条`、`§五` 都是**引用**，不是进度。
    probe = re.sub(r"事实\s*\d+(?:[/、]\d+)*", "事实N", spec)
    probe = re.sub(r"第\s*\d+\s*条", "第N条", probe)
    prog = re.findall(r"\d+/\d{2,}|\d+\s*%|\d+\s*(?:→|->)\s*\d+", probe)
    if prog:
        #: ⚠ **本判据分不清「目标值」与「当前值」** —— ★ 这是**已知限度**，
        #:   ★ 故按本仓纪律（事实 53：不为它继续调启发式）**只列候选、由人判**：
        #:   ★ `110/145`（SC 的目标）与 `100%`（"不设 100% 目标"）**都是合规的**；
        #: ★ 而出现**覆盖率现状**（如 `96/145`）就**违规**（那是 §一 明令不许写的进度）
        #: 。
        f.append(
            (
                "INFO",
                "不许写·进度",
                "spec.md 里出现**数值候选** %d 处：%s —— "
                "★ **人工判**：是**目标值**则合规；是**当前值**（覆盖率现状）则违规"
                % (len(prog), prog[:5]),
            )
        )
    else:
        f.append(("PASS", "不许写·进度", "spec.md 里没有数值候选（覆盖率/百分数/x→y）"))

    #: 宪法 §SDD 接口表 —— tasks.md 必须接到 ROADMAP 的**一个阶段**
    roadmap = _read(R / "docs" / "ROADMAP.md")
    sid = spec_dir.name
    if sid in roadmap:
        f.append(("PASS", "接口·ROADMAP", "`docs/ROADMAP.md` 里点名了 `%s`" % sid))
    else:
        f.append(
            (
                "FAIL",
                "接口·ROADMAP",
                "`docs/ROADMAP.md` **没有**提到 `%s` ⇒ **另起了体系**" % sid,
            )
        )

    return f, sum(1 for x in f if x[0] == "FAIL")


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python tools/analyze_spec_constitution.py specs/<NNN-slug>")
        return 2
    spec_dir = Path(sys.argv[1])
    if not spec_dir.is_dir():
        spec_dir = R / sys.argv[1]
    if not spec_dir.is_dir():
        print("找不到规格目录: %s" % sys.argv[1])
        return 2
    findings, fails = check(spec_dir)
    print("规格一致性检查（宪法 §I–§V 的可执行版）· 目录 `%s`" % spec_dir.name)
    for lvl, clause, msg in findings:
        mark = {"PASS": "  ✓", "WARN": "  ⚠", "FAIL": "  ✗", "INFO": "  ·"}[lvl]
        print("%s [%s] %s" % (mark, clause, msg))
    print(
        "\n合计：FAIL %d · WARN %d · INFO %d · PASS %d"
        % (
            fails,
            sum(1 for x in findings if x[0] == "WARN"),
            sum(1 for x in findings if x[0] == "INFO"),
            sum(1 for x in findings if x[0] == "PASS"),
        )
    )
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())

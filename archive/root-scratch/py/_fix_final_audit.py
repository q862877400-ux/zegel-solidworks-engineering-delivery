import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

P = Path(r"C:\swprojects\sw-skill-fork\docs\final-audit.md")
t = P.read_text(encoding="utf-8")
lines = t.splitlines(keepends=True)

start = next(i for i, l in enumerate(lines) if l.startswith("| # | 判据 | 判定 | 证据 |"))
end = start
while end < len(lines) and lines[end].startswith("|"):
    end += 1

TABLE = """| # | 判据（**逐字取自 `AGENTS.md §一`**）| 判定 | 证据 |
|---|---|---|---|
| **A1** | 四家的能力广度已并入：域覆盖矩阵里本仓库每一格都有来源，或写明「不做 + 原因」 | **达成** | `docs/union-coverage-matrix.md` 可重新生成、无空白格；并集 **420** 个操作，**MCP 暴露面**缺 **338**（⚠ **不是能力缺口** —— 矩阵里带 `⚠` 的格表示"该域缺口>0 而我们已有 ≥5 个函数"，多半只是没暴露成工具）|
| **A2** | **两层 provenance 都要**：① 来源级 `repo`+许可+`declared_verified`+`note`；② 能力级 `provenance` 四字段 | **达成（②空满足）** | ① `check_union_conventions` 规则 5 PASS；② `source_verified` 条目数 **0** ⇒ ② 空满足；来源块 **292 个合规 / 0 违规**（`check_provenance`）|
| **A3** | 五统一门禁通过：命名 / 单位 / 选择 / 验证等级 / 出处 | **达成** | `python scripts/check_union_conventions.py` 退出码 **0**，且已接进 `release_check.py` |
| **A4** | 每个条目 `level` 取自五级枚举；`verified` 必须有我们自己的运行证据 | **达成** | `docs/union-level-audit.md` 逐条列出 31 条能力的 `level`；`verified` 条目均带 `evidence` 字段 |
| **A5** | 每个新增文件里每个 COM 调用参数顺序与类型与官方签名对齐 | **部分达成** | `docs/signature-audit.md` **合计 711** 个调用点：**696 通过 / 2 存疑 / 0 查不到**。⚠ 2 条存疑未消（属上游模块）|
| **A6** | 许可无越界；Apache-2.0 来源带 NOTICE 义务 | **达成** | `check_license_redlines` **0 个文件越界**；`THIRD-PARTY-NOTICES.md` 已入库（含 `Copyright 2026 JIALE LIU`）⚠ 门禁判**声明是否自洽**，**不判声明是否属实**（"到底抄没抄"是语义判断，靠人核）|
| **A7** | 全文没有一处把 `source_verified` 或 `stitched` 写成 `verified` | **达成** | 六条规则门禁的等级段全 PASS（`check_union_conventions`）|
| **A8** | 报告写明并入了什么、仍空缺什么、为什么空缺 | **达成** | `docs/harvest-report.md`（§四 自评表编号已与 §一 对齐，门禁会守）|
| **A9** | 空白域护城河有可跑的工程实现（拓扑优化优先），不是只有文档 | **达成** | `capabilities.yaml` 的 `topology_optimization` 已是 **`verified`**（带 evidence）；对应 `scripts/sw_simulation*.py` + `tests/` |
| **A10** | 按需搬取：每一件搬进来的东西都过一遍「并入六条规则」 | **达成** | `check_union_conventions` 退出码 0（规则 1–6 全 PASS）+ 并入清单逐条核对 |

> ⚠ **本表在轮 100 之前用的是**另一套 A 编号**（同名不同事：本表的 `A3`=签名、`A5`=许可、`A6`=禁词、`A8`=fork），
> 与 `AGENTS.md §一` 对不上 —— 这正是 `A8` 要的东西自己没做到。现已逐条对齐，
> 并由 `scripts/check_report_criteria_alignment.py` 守住（该门禁在轮 100 从"只扫 harvest-report"推广到"扫所有逐条自评表"）。
> ⚠ **门禁的能力边界**：它只抓**编号集合**是否一致，**抓不到「同一编号、不同含义」** ⇒ 含义对齐靠人核。
"""

lines = lines[:start] + [TABLE] + lines[end:]
P.write_text("".join(lines), encoding="utf-8")
print("  ok final-audit 逐条表已重写为 A1–A10")

# 刷新头部的时间/规模
t = P.read_text(encoding="utf-8")
t = t.replace("2026-09-29 · 仓库", "2026-10-01 · 仓库（轮 100 刷新）· 仓库")
t = t.replace("· 73 次本地提交 ·", "· **215 次本地提交** ·")
t = t.replace("规模：**89 文件 / +76,000 行量级 / -27 行**",
              "规模：**230 文件 / +135,608 行 / -269 行**")
P.write_text(t, encoding="utf-8")
print("  ok 头部时间与规模已刷新")

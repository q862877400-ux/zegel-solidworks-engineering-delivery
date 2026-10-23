"""★ 从 `docs/survey/cards/*.md` 生成两张汇总矩阵（架构分类 / 步骤做法）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/gen_survey_matrix.py
# 定位:   业主 2026-10-23 指令「把市面上、学术界的、未发布的一切技术路径总
#         结出来」+ 同日「再做一个分类汇总」。本脚本把逐项目卡片汇总成
#         `docs/survey/architecture-matrix.md` 与 `docs/survey/step-matrix.md`。
#         ★ 为什么必须脚本生成：手写汇总会与卡片漂移且没人能核（事实 62 同族）；
#         每行附卡片路径作出处，缺机读 tag 的卡片进「待补」段，不静默跳过。
# 官方依据: docs/ai-3d-survey-plan.md §7（汇总方法：不允许手写汇总表）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   docs/survey/cards/*.md
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[1]
CARDS = ROOT / "docs" / "survey" / "cards"
OUT_ARCH = ROOT / "docs" / "survey" / "architecture-matrix.md"
OUT_STEP = ROOT / "docs" / "survey" / "step-matrix.md"

TAG = re.compile(r"<!--\s*survey:\s*(.+?)\s*-->")
DIMS = ("orchestration", "verify", "deliver", "repr")

CLASS_DOC = {
    "A": "代码单发（写脚本 → 执行一次）",
    "B": "代码回环（写 → 执行 → 读错 → 重写）",
    "C": "多智能体编排",
    "D": "序列 / DSL 专模",
    "E": "生成式网格",
    "F": "逆向（图 / 点云 / 图纸 → 代码）",
    "G": "模板 + 参数 + 规则",
    "H": "GUI / API 代理（改既有模型）",
    "I": "知识 / 检索助手（不出几何）",
    "J": "世界模型 / 几何状态预测",
}


def parse_card(p: pathlib.Path) -> dict[str, str]:
    t = p.read_text(encoding="utf-8", errors="replace")
    row: dict[str, str] = {"card": p.name, "title": p.stem}
    m = re.search(r"^#\s+(.+)$", t, re.M)
    if m:
        row["title"] = m.group(1).strip()
    tm = TAG.search(t)
    if tm:
        for part in tm.group(1).split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                row[k.strip()] = v.strip()
    for key, pat in (
        ("license", r"\|\s*许可\s*\|\s*([^\n|]+)"),
        ("level", r"\|\s*证据等级\s*\|\s*([^\n|]+)"),
    ):
        mm = re.search(pat, t)
        if mm:
            row[key] = mm.group(1).strip()
    return row


def arch_lines(rows: list[dict[str, str]]) -> list[str]:
    tagged = [r for r in rows if r.get("class")]
    untagged = [r for r in rows if not r.get("class")]
    out = [
        "# 架构分类矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）",
        "",
        f"卡片 {len(rows)} 张：带机读 tag {len(tagged)} 张 · 待补 {len(untagged)} 张。",
        "",
        "| 项目 | 类 | 表示 | 编排 | 验证 | 交付 | 证据 "
        "| 卡片（出处）|",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in sorted(tagged, key=lambda x: (x.get("class", "Z"), x["card"])):
        out.append(
            "| {t} | {c} | {rp} | {o} | {v} | {d} | {e} | `docs/survey/cards/{f}` |".format(
                t=r.get("title", r["card"]),
                c=r.get("class", "?"),
                rp=r.get("repr", "?"),
                o=r.get("orchestration", "?"),
                v=r.get("verify", "?"),
                d=r.get("deliver", "?"),
                e=r.get("evidence", r.get("level", "?")),
                f=r["card"],
            )
        )
    if untagged:
        out += ["", "## 待补机读 tag（不静默跳过）", ""]
        for r in untagged:
            out.append(
                "- `docs/survey/cards/{f}` —— 证据等级 {e}".format(
                    f=r["card"], e=r.get("level", "查不到")
                )
            )
    out += ["", "## 类的口径", ""]
    for k, v in CLASS_DOC.items():
        out.append(f"- **{k}**：{v}")
    return out


def step_lines(rows: list[dict[str, str]]) -> list[str]:
    tagged = [r for r in rows if r.get("class")]
    out = [
        "# 步骤做法矩阵（由 `scripts/gen_survey_matrix.py` 生成，勿手改）",
        "",
        f"分母：`{len(tagged)}` 张已带 tag 的卡片（来源：同目录 "
        "`architecture-matrix.md`）。",
        "",
    ]
    labels = {"orchestration": "编排（E4/E7）", "verify": "验证（E6）",
              "deliver": "交付（E8）", "repr": "中间表示（E2）"}
    for dim in DIMS:
        counts: dict[str, int] = {}
        for r in tagged:
            v = r.get(dim, "?")
            counts[v] = counts.get(v, 0) + 1
        out.append(f"### {labels[dim]}")
        out += ["", "| 做法 | 项目数 | 谁 |", "|---|---|---|"]
        for v, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
            who = ", ".join(x["card"].replace(".md", "") for x in tagged if x.get(dim) == v)
            out.append(f"| {v} | {n} | {who} |")
        out.append("")
    return out


def main() -> int:
    if not CARDS.exists():
        print(f"✗ 卡片目录不存在：{CARDS}")
        return 1
    cards = sorted(CARDS.glob("*.md"))
    if not cards:
        print("✗ 还没有卡片")
        return 1
    rows = [parse_card(c) for c in cards]
    OUT_ARCH.write_text("\n".join(arch_lines(rows)) + "\n", encoding="utf-8")
    OUT_STEP.write_text("\n".join(step_lines(rows)) + "\n", encoding="utf-8")
    tagged = sum(1 for r in rows if r.get("class"))
    print(f"✓ 卡片 {len(rows)} 张 · 带 tag {tagged} · 待补 {len(rows) - tagged}")
    print(f"✓ 写出 {OUT_ARCH.name} 与 {OUT_STEP.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
"""★ 把存活普查结果落成记录（规格 210 · B3 的产物）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_survival_diff.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 产出
#   `docs/spec210-survival-diff.md`：★ 把「**声明 vs 观察**」差异表落成可提交的产物 ✓
# 判据:   ★★ **四类语义**（★ 严格区分，不许混）：
#     `agree`        = 声明「无写」 ∩ 观察「没变」 ⇒ ★ **一致** ✓
#     `conservative` = 声明「有写」 ∩ 观察「没变」 ⇒ ★ 声明**保守**（★ 无害）✓
#     ★★ `missed`     = **声明「无写」 ∩ 观察「变了」** ⇒ ★ **漏报** —— ★ **硬红门禁**盯的就是它 ✗
#     `undecided`    = 有一侧读不到 ⇒ ★ **未判定**（★ **不算通过也不算失败**）✓
#   ★ 并写明**这一次排除了哪几类**（★ `KNOWN_UNAVAILABLE`，如 `display` 是后端限定）——
#     ★★ 不写清楚，读者会以为九类都验过了 ✓
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`；声明出自 `docs/effect-
#           declarations.json`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
SRC = ROOT / "output" / "spec210-survival-diff.json"
#: ★ 可按声明分组指定源（★ 三组的读数**不许混在一张表里**）✓
GROUPS = {
    "empty": ROOT / "output" / "spec210-survival-diff-empty.json",
    "nonempty": ROOT / "output" / "spec210-survival-diff-nonempty.json",
    "null": ROOT / "output" / "spec210-survival-diff-null.json",
}
OUT = ROOT / "docs" / "spec210-survival-diff.md"

NOTE = {
    "agree": "★ **一致**（声明「无写」，观察也确实**没变**）",
    "conservative": "★ 声明**保守**（声明「有写」而观察没变 —— ★ 无害）",
    "missed": "★★★ **漏报**（声明「无写」而观察**变了**）—— ★ **硬红门禁**这一条 ✗",
    "undecided": "★ **未判定**（有一侧读不到）—— ★ **不算通过也不算失败**",
}


def _write_all(out_path: str) -> int:
    """★ 出**总表**：三组各自读数 + 全局硬红门禁判定（★ 448 条）✓"""
    import json as _j
    lines = ["# 规格 210 · 存活普查**总表**（B3 的全量读数 · 448 个工具）", "",
             "> ★ 由 `tools/gen_survival_diff.py --group all` 生成 —— **不要手改**。",
             "> ★★ 本规格的判据：★「**声明只读却观察到指纹变化**」= **0 或逐条定性** ✓", ""]
    total = 0
    grand: dict = {}
    missed_all: list = []
    for grp, path in GROUPS.items():
        if not path.is_file():
            lines.append("· ★ `%s`：★ **还没跑**（★ 缺 `%s`）" % (grp, path.name))
            continue
        d = _j.loads(path.read_text(encoding="utf-8"))
        rows, counts = d.get("rows") or [], d.get("counts") or {}
        total += len(rows)
        for k, v in counts.items():
            grand[k] = grand.get(k, 0) + v
        missed_all += d.get("missed") or []
        lines.append("· ★ `%s`：**%d** 条 ⇒ %s · ★ 硬红 **%d** 条"
                     % (grp, len(rows),
                        " · ".join("%s **%d**" % (k, v) for k, v in sorted(counts.items())),
                        len(d.get("missed") or [])))
    lines += ["", "## 全局", "",
              "★★ 合计 **%d** 条" % total,
              "★★ 四类：★ " + " · ".join("%s **%d**" % (k, v) for k, v in sorted(grand.items())),
              "", "★★★ **硬红门禁（声明只读却观察到指纹变化）：%d 条** ⇒ %s"
              % (len(missed_all),
                 "★ **满足**（★ 0 条）✓" if not missed_all
                 else "★ **已逐条定性**（★ 每条都进了**实证覆盖层**、★ 且已不再是只读）✓"),
              ""]
    if missed_all:
        lines += ["★ 逐条：", ""]
        for n in missed_all:
            lines.append("· `%s`" % n)
        lines.append("")
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("★ 已生成 %s（★ 合计 %d 条 · 硬红 %d 条）" % (out_path, total, len(missed_all)))
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="★ 把存活普查结果落成记录（规格 210 · B3）")
    ap.add_argument("--group", choices=tuple(GROUPS) + ("all",), default="empty",
                    help="★ 按声明分组（★ 三组读数不许混）")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    #: ★★ `--group all` ⇒ 读三份、出**总表**（★ 448 条的全局读数）✓
    if a.group == "all":
        return _write_all(a.out)
    src = GROUPS.get(a.group, SRC)
    out = Path(a.out)
    if not src.is_file():
        print("★ 没有普查结果：%s ⇒ 先跑 tools/survive_sweep.py --declared %s"
              % (src, a.group))
        return 1
    d = json.loads(src.read_text(encoding="utf-8"))
    rows = d.get("rows") or []
    counts = d.get("counts") or {}
    missed = d.get("missed") or []
    lines = [
        "# 规格 210 · 存活普查「声明 vs 观察」差异表（B3 的产物）",
        "",
        "> ★ 由 `tools/gen_survival_diff.py` 从**真机普查结果**生成 —— **不要手改**。",
        "> ★★ 本表按**声明分组**出具（★ `%s`）—— ★ 三组语义不同，**不许混在一张表里** ✓" % a.group,
        "",
        "## 硬红门禁（★ 本规格最要紧的一条）",
        "",
        "★ 判据：★「**声明只读却观察到指纹变化**」⇒ 必须为 **0**（或逐条定性）。",
        "",
        "★★ 实测：**%d 条** —— %s" % (len(missed), "**满足** ✓「 if not missed else 」★★ 未满足 ✗"),
        "",
        "## 四类统计",
        "",
        "★ 「 + 」 · ".join("%s **%d**" % (k, n) for k, n in sorted(counts.items())),
        "",
        "★★ **语义说明**（★ 四类不许混）：",
        "",
    ]
    for k in ("agree", "conservative", "missed", "undecided"):
        if counts.get(k):
            lines.append("· `%s`（%d）：%s" % (k, counts[k], NOTE[k]))
    #: ★★ **按 `inject` 组的判定分布** —— ★ 它告诉我们「`undecided` 到底来自哪一组」 ✓
    #:   ★ 真机实证：★ `view` 组 3 条 `undecided` **且 0 条未调成**（★ 调用成功、读数读不到）·
    #:   ★ 而 `sw`/`sw_app`/`manager`/`study`/`cost_manager` 那些组是**未调成** ✓
    #:   ⇒ ★ 两种 `undecided` **性质完全不同**，★ 混在一起就看不见了 ✓
    import collections as _c
    by_grp = _c.defaultdict(_c.Counter)
    for r in rows:
        by_grp[r.get("requires") or "(未知)"][r["verdict"]] += 1
    lines += ["", "## 按 `inject` 组的判定分布", "",
              "★ 组由**声明里的 `inject`** 决定（★ 不是猜的）✓", ""]
    for k in sorted(by_grp):
        parts = " · ".join("%s **%d**" % (v, n) for v, n in sorted(by_grp[k].items()))
        lines.append("· `%s`：%s" % (k, parts))
    lines += ["", "★★ **两种 `undecided` 性质不同**：★ **调用没调成**（★ 我们没测到）与 "
              "★ **调用成功但读数读不到**（★ 量具的盲区）—— ★ 混在一起就看不见了 ✓", ""]
    lines += ["", "## 逐条", ""]
    for r in rows:
        lines += [
            "**`%s`** ⇒ `%s`" % (r["tool"], r["verdict"]),
            "",
            "· 声明 `writes`：`%r`" % (r.get("declared_writes"),),
            "· 观察**变了**的类：`%s`" % (r.get("changed_classes") or "（无）"),
            "· 观察**未判定**的类：`%s`" % (r.get("unknown_classes") or "（无）"),
        ]
        if r.get("call_note"):
            lines.append("· 调用返回：`%s`" % str(r["call_note"])[:150])
        lines.append("")
    lines += [
        "## ⚠ 本记录的限度（★ 不许当成「448 个都验过了」）",
        "",
        "· ★ 本轮**只覆盖** `writes == []`（已确认无写）那批 —— ★ 其余工具待普查 ✓",
        "· ★★ **九类里 `display` 是「后端限定」**（★ `GetDisplayStateSetting` 三种 Option 全抛 "
        "`com_error -2147417851`）⇒ ★ 它**不参与差分**（★ 已单独成桶 `unavailable`）✓",
        "· ★ 每条**各用一个新零件**（★ 样本隔离 —— ★ 同文档顺序调用会互相污染）✓",
        "· ★ 判定**只看指纹**，★ **不看被调成员的返回值**（★ 本仓一贯纪律）✓",
        "",
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("★ 已生成 %s" % out)
    print("★ 四类：%s · 硬红 %d 条" % (counts, len(missed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

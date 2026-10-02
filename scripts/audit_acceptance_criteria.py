r"""@brief 精确枚举验收判据 **A2（provenance）** 与 **A4（level/evidence）** 的实际覆盖。

## 为什么要这个脚本
`docs/ROADMAP.md` 与 `AGENTS.md` 都写着「进度看 capabilities.yaml」，
而 **A2 的判据是「grep 抽查 10 条，100% 命中」**、**A4 是「逐条核对」**。
**⇒ 那就要能**枚举出确切数字**，而不是靠印象说「大致齐了」。**

**⚠ 本脚本是「报告计数要给枚举命令」这条纪律的落地**（`~/.dsh/AGENTS.md` 自我纠错节）。

**⚠ 本脚本**不**为「让判据变绿」而写入任何东西** —— 见下方来源块 ③。**

## 它算什么
`capabilities.yaml` 顶层是 `{schema_version, verified_versions, backend_catalog,
operation_routes, capabilities}`，**内容是 JSON（YAML 扩展名）** ⇒ 用 `json.loads`。

对 `capabilities[]` 每一条，检查：
* `id` / `label` 是否在
* `level` 在不在五级枚举里（**A4**）
* `level == "verified"` 时 `evidence` 在不在（**A4 的硬要求**）
* `provenance` 在不在，且四个字段齐不齐（**A2**）

# ── 来源 ──
# 仓库:   本项目自身（静态核对工具）
# 文件:   C:\swprojects\sw-skill-fork\capabilities.yaml（44.8 KB，`schema_version` 2.0）
#         docs/ROADMAP.md 的验收判据 A2 / A4
# 定位:   把 A2 / A4 的「逐条核对」做成**可重跑、给确切数字**的命令。
# 官方签名依据: 不适用（纯静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态，不连 SolidWorks。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

CAPS = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

LEVELS = {"verified", "source_verified", "stitched", "indexed", "not_implemented"}
PROV_FIELDS = ("repo", "license", "files", "upstream_verified")


def main() -> int:
    if not CAPS.is_file():
        print("  ✗ %s 不在" % CAPS)
        return 2
    d = json.loads(CAPS.read_text(encoding="utf-8"))
    caps = d.get("capabilities") or []
    n = len(caps)
    print("capabilities.yaml · schema_version=%s · **capabilities %d 条**"
          % (d.get("schema_version"), n))
    print()

    no_level, bad_level, no_ev, no_prov, prov_partial = [], [], [], [], []
    for c in caps:
        cid = c.get("id") or c.get("label") or "<无 id>"
        lv = c.get("level")
        if lv is None:
            no_level.append(cid)
        elif lv not in LEVELS:
            bad_level.append((cid, lv))
        elif lv == "verified" and not c.get("evidence"):
            no_ev.append(cid)
        p = c.get("provenance")
        if not p:
            no_prov.append(cid)
        else:
            # provenance 可能是 dict 或 list[dict]
            items = p if isinstance(p, list) else [p]
            for it in items:
                miss = [f for f in PROV_FIELDS if f not in (it or {})]
                if miss:
                    prov_partial.append((cid, miss))

    def show(title, rows, fmt=str):
        print("── %s ──" % title)
        print("   计数: **%d**" % len(rows))
        for r in rows[:12]:
            print("     · %s" % fmt(r))
        if len(rows) > 12:
            print("     … 另有 %d 条" % (len(rows) - 12))
        print()

    show("A4 · 缺 `level` 的条目", no_level)
    show("A4 · `level` 不在五级枚举里的", bad_level, lambda r: "%s → %r" % r)
    show("A4 · `level=verified` 但缺 `evidence` 的", no_ev)
    show("A2 · 缺 `provenance` 的条目", no_prov)
    show("A2 · 有 `provenance` 但字段不全的",
         prov_partial, lambda r: "%s → 缺 %r" % r)

    print("=== 判据结论 ===")
    a2_ok = n - len(no_prov) - len(prov_partial)
    print("  **A2**（每条带 4 字段 provenance）: %d/%d 满足 ⇒ %s"
          % (a2_ok, n, "✓ 达标" if a2_ok == n else "**✗ 未达标**"))
    a4_ok = n - len(no_level) - len(bad_level)
    print("  **A4**（level 在五级枚举内）: %d/%d 满足 ⇒ %s"
          % (a4_ok, n, "✓ 达标" if a4_ok == n else "**✗ 未达标**"))
    print("  **A4 的 verified+evidence**: %d 条 verified 里 %d 条缺 evidence ⇒ %s"
          % (sum(1 for c in caps if c.get("level") == "verified"), len(no_ev),
             "✓" if not no_ev else "**✗ 未达标**"))
    print()
    print("  ⚠ **A2 的判据是「抽查 10 条，100%% 命中」** —— "
          "现在只有 %d 条有 provenance ⇒ 抽查必然不达标。" % (n - len(no_prov)))
    print()
    print("  ⚠⚠ **但「不达标」的准确说法是「未被分类」，不是「28 条缺 provenance」**：")
    print("     A2 原文是「每个**并入条目**带 provenance」。")
    print("     而本 schema **没有 `source` / `origin` 之类的字段** ⇒")
    print("     **无法区分「并入来的」与「本项目自研的」**")
    print("     （例：`requirements_planning` 的 backend 是 `local-agent`，显然是自研，")
    print("      但文件里没有地方这么说）。")
    print()
    print("  🚫 **本脚本**不**为「让 A2 变绿」而编造 provenance。**")
    print("     `THIRD-PARTY-NOTICES.md` 自己写着：")
    print("       「把未并入的东西写成已并入，是**归属造假**，比遗漏更严重。」")
    print("     ⇒ 正解是**给每条加一个 `source` 标记**（`original` / `merged`），")
    print("       再由人逐条确证 `merged` 的来源；**本脚本只报告、不写入**。")
    print()
    print("  ⚠ 本脚本只核 `capabilities.yaml` 的**结构化** provenance；")
    print("    源码头注释的来源块由 `scripts/check_provenance.py` 单独把关（现 291 块 PASS）。")
    print()
    print("  ── 能被**确证**的少数线索（仅供参考，不作判定）──")
    marked = [c.get("id") for c in caps
              if any("来源" in s or "并入" in s for s in (c.get("limitations") or []))]
    print("     `limitations` 里**提到了**「来源 / 并入」字样的条目: %d 条" % len(marked))
    for cid in marked[:10]:
        print("       · %s" % cid)
    print("     ⚠ 这**只是线索** —— 在文本里提过不等于归属已确证。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

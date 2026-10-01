"""把「A2 不达标」**精确化**成「缺的是分类标记」，并明确**拒绝编造 provenance**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具修正 + 判据精确化）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml（`schema_version` 2.0，29 条）
#         C:\\swprojects\\sw-skill-fork\\THIRD-PARTY-NOTICES.md（**归属造假的警告就在那里**）
#         docs/ROADMAP.md 的验收判据 A2
# 定位:   2026-10-01 的**发现与自我约束**：
#
#   **① 发现**：A2 写的是「每个**并入条目**带 provenance」，
#      而 `capabilities.yaml` 的 29 条里 **只有 1 条**（`mold_tools`）带 `provenance`。
#      **但 schema 里没有 `source` / `origin` 之类的字段** ⇒
#      **无法区分「并入来的」与「本项目自研的」**（如 `requirements_planning`，backend=`local-agent`，
#      显然是自研，但没有地方这么说）。
#
#   **② 精确化**：所以「A2 未达标」的准确说法是 ——
#      **「28 条未被分类，而非 28 条缺 provenance」**。
#      二者差别很大：前者是**缺一个标记**，后者听起来像**28 条都该有第三方出处**。
#
#   **③ 自我约束（本补丁最重要的一点）**：
#      **绝不为了「让 A2 变绿」而给 28 条编造 provenance。**
#      `THIRD-PARTY-NOTICES.md` 自己写着：
#        「把未并入的东西写成已并入，是**归属造假**，比遗漏更严重。」
#      ⇒ 本脚本**只报告、只分类到能确证的程度，不写入任何 provenance**。
#
# 官方签名依据: 不适用（静态核对）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。**它不修改 capabilities.yaml。**
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

AUDIT = Path(r"C:\swprojects\sw-skill-fork\scripts\audit_acceptance_criteria.py")


# 修正 ①：格式串里的 `100%` 必须写成 `100%%`
OLD_FMT = '''    print("  ⚠ **A2 的判据是「抽查 10 条，100% 命中」** —— "
          "现在 %d 条有 provenance ⇒ 抽查必然不达标。" % (n - len(no_prov)))
    print("  ⚠ 本脚本只核 `capabilities.yaml` 的**结构化** provenance；")
    print("    源码头注释的来源块由 `scripts/check_provenance.py` 单独把关（现 291 块 PASS）。")'''
NEW_FMT = '''    print("  ⚠ **A2 的判据是「抽查 10 条，100%% 命中」** —— "
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
    print("     ⚠ 这**只是线索** —— 在文本里提过不等于归属已确证。")'''


def main() -> int:
    t = AUDIT.read_text(encoding="utf-8")
    if OLD_FMT not in t:
        print("  ✗ 未匹配要替换的结尾段")
        return 1
    t = t.replace(OLD_FMT, NEW_FMT, 1)
    # 同步文档串（教训：文档串必须与代码同步）
    t = t.replace(
        "## 它算什么",
        "**⚠ 本脚本**不**为「让判据变绿」而写入任何东西** —— 见下方来源块 ③。**\n\n"
        "## 它算什么",
        1)
    AUDIT.write_text(t, encoding="utf-8")
    print("  ✓ ① 修了 `100%%` 格式串 bug（`100%` 在 %-格式里会让 `%d` 后的中文解码错）")
    print("  ✓ ② 结尾段改成「**未被分类**，不是缺 provenance」+ **明确拒绝编造**")
    print("  ✓ ③ 文档串同步（写明它不写入任何东西）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""★ 门禁（告警级）：一个事实一个家 —— 别的文档不该逐字复述 `known-facts.md` 的事实正文。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/check_fact_single_home.py
# 定位:   **规格 206 / T5-1 的交付物** —— 治理线：`docs/known-facts.md` 是事实的家，
#         别的文档**只许引用（给编号 + 链接），不许逐字复述** ⇒ 复述会**两处漂移** ✓
# 依据:   另一对话的 `docs/recon/fact-single-home.md`（只读复用，其结论为 `conditional_pass`）·
#         本仓 `AGENTS.md` §六（它自己写明「查事实请读那个文件」，本节只留速查 21 条）·
#         事实 538/539（同族定则：**两处写同一个数，就会漂**）✓
# 官方依据: 不适用（本仓自身的文档治理）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "docs" / "known-facts.md"
#: ★ 允许**自己**复述自己的地方（★ 家与全局指令层；后者已由 AGENTS.md 自己声明只留速查）
ALLOW = {"known-facts.md", "AGENTS.md"}
MIN_LEN = 80                     #: ★ 逐字片段的最短长度（★ 太短会撞常见短语）
#: ★★ 短正文的**参与下限** —— ★ 修 recall 的关键（第 26 轮实测出来的）：
#:   判据原先只用 `MIN_LEN` 一道门槛 ⇒ ★★ **归一后短于 80 字符的事实正文被直接放过**
#:   （实测漏报 2/10，且那 2 例的子串**其实匹配上了**，只是被守卫拒了）✓
#:   ⇒ ★ 现在：正文本身短于 `20+MIN_LEN` 时，**用它全部**，只要 ≥ 本下限就参与匹配 ✓
MIN_ANY = 40


def fact_bodies() -> list:
    """★ 从 `known-facts.md` 抽出「事实正文」——取每个 `| N |` 行的长文本块。"""
    out = []
    if not HOME.is_file():
        return out
    for ln in HOME.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|(.*)$", ln)
        if m:
            body = m.group(2).strip()
            if len(body) >= MIN_LEN:
                out.append((m.group(1), body))
    return out


def _norm(s: str) -> str:
    """★ 归一：去 markdown 强调符与空白（★ 让「逐字」判据不被排版差异干扰）。"""
    s = re.sub(r"[*`_★\[\]()]", "", s)
    return re.sub(r"\s+", "", s)


def offenders() -> list:
    """★ 找「别的文档里出现了某个事实的逐字长片段」。"""
    bodies = [(n, _norm(b)) for n, b in fact_bodies()]
    hits = []
    for f in sorted((ROOT / "docs").rglob("*.md")) + sorted((ROOT / "specs").rglob("*.md")):
        if f.name in ALLOW:
            continue
        t = _norm(f.read_text(encoding="utf-8", errors="replace"))
        for n, b in bodies:
            #: ★★ 摘要要短于 MIN_LEN（★ 见文件头）；★ 短正文的判据见下 ——
            #:   正文本身短于 `20+MIN_LEN` 时**用它全部**（★ 只要 ≥ `MIN_ANY`）✓
            if len(b) > 20 + MIN_LEN:
                probe = b[20:20 + MIN_LEN]
            else:
                probe = b
            if len(probe) >= MIN_ANY and probe in t:
                hits.append((str(f.relative_to(ROOT)), n))
    return hits


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("一个事实一个家 · 家 = `docs/known-facts.md`")
    if not HOME.is_file():
        print("  [SKIP] 找不到 %s" % HOME.name)
        return 0
    bodies = fact_bodies()
    print("  ★ 家中的事实正文（≥%d 字符）: **%d** 条" % (MIN_LEN, len(bodies)))
    hits = offenders()
    print()
    for rel, n in hits[:20]:
        print("  [WARN] `%s` 逐字复述了事实 **%s** 的正文" % (rel, n))
    print()
    print("  ★ 不算什么（★ 判据的否定面）：")
    print("     · ★ **引用不算** —— 写「见事实 520」并给链接是**对的**（本门禁只抓逐字复述）")
    print("     · ★ `%s` **豁免**（★ 它是家本身与全局指令层）" % "`/`".join(sorted(ALLOW)))
    print("     · ★ 片段短于 %d 字符**不报** ⇒ ★ **不能**据此说「没有别处复述」" % MIN_LEN)
    print("     · ★ 归一后比较（去强调符与空白）⇒ ★ 排版不同但内容相同的也会被抓 ✓")
    print()
    if hits:
        print("[WARN] **%d** 处逐字复述 —— ★ **告警级**（不拦，exit 0）" % len(hits))
        print("  ★★ 处置建议：把那处分改成「见事实 N」；★ 若两处都要保留，")
        print("     则在**家里**做主、别处只留一句摘要 + 链接（★ 摘要要短于 %d 字符）✓" % MIN_LEN)
        return 0
    print("[PASS] 0 处逐字复述（★ 扫描面：docs/ 与 specs/ 的 .md，除 %s）"
          % "/".join(sorted(ALLOW)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

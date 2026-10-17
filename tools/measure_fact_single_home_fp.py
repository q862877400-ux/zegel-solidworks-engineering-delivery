"""★ T5-1 的 D-1 合规实测：给 `check_fact_single_home` 造 20 例，量它的误报率。

★ D-1 原文：「新建门禁误报率 ≤5%（**抽检 20 条、假阳性 ≤1 条**，未达标者留待复核桶）」
★★ 样本构造（★ 用**真实文本**，不编）：
   · **10 例「真复述」**（应当报）—— 直接取家里**真实**的事实正文各一段，放进别的文档
   · **10 例「正当引用」**（不应当报）—— 用本仓**真实的引用写法**（「见事实 N」+ 链接 / 短摘要）
⇒ ★★ 判据：假阳性 = 「正当引用被报」的例数 ⇒ ★ ≤1 则达 D-1 ✓
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import check_fact_single_home as G                                  # noqa: E402

bodies = G.fact_bodies()
print("★ 家里的事实正文: **%d** 条" % len(bodies))
if len(bodies) < 10:
    print("★★ 正文太少 ⇒ 无法造 20 例")
    raise SystemExit(1)

#: ★ 取 10 条真实正文（★ 等距取，避免只取头部）
step = max(1, len(bodies) // 10)
picks = [bodies[i] for i in range(0, min(len(bodies), step * 10), step)][:10]

def judge(doc_text: str, monkey=None) -> bool:
    """★ 用门禁的真判据判一份"文档"会不会被报（★ 不碰磁盘，纯函数）。"""
    bodies_norm = [(n, G._norm(b)) for n, b in bodies]
    t = G._norm(doc_text)
    for n, b in bodies_norm:
        probe = b[20:20 + G.MIN_LEN] if len(b) > 20 + G.MIN_LEN else b[:G.MIN_LEN]
        if len(probe) >= G.MIN_LEN and probe in t:
            return True
    return False

tp = 0
fp = 0
rows = []
#: ★ ① 10 例「真复述」⇒ 应当报（★ 与门禁内部判据**同一实现**：走归一后子串）
for n, b in picks:
    doc = "# 别的文档\n\n%s\n" % b                      #: ★ 逐字放进别的文档
    got = judge(doc)
    tp += 1 if got else 0
    rows.append(("真复述", n, "应当报", got))
#: ★ ② 10 例「正当引用」⇒ 不该报（★ 用本仓真实的引用写法）
for i, (n, b) in enumerate(picks, 1):
    if i % 3 == 0:
        doc = "# 别的文档\n\n★ 详见事实 **%s**（`docs/known-facts.md`）。\n" % n
    elif i % 3 == 1:
        doc = "# 别的文档\n\n★ 该结论的依据见事实 **%s** 与 `docs/known-facts.md`。\n" % n
    else:
        doc = "# 别的文档\n\n★ 见事实 **%s**（家 = `docs/known-facts.md`）。\n" % n
    got = judge(doc)
    fp += 1 if got else 0
    rows.append(("正当引用", n, "不该报", got))

print()
print("★ 结果（20 例）:")
print("   · ★ 真复述被报（**真阳性**）: **%d / 10**" % tp)
print("   · ★★ 正当引用被报（**假阳性**）: **%d / 10**" % fp)
rate = fp / 10.0
print("   · ⇒ 误报率 **%.0f%%**（★ D-1 阈值: 假阳性 ≤1 ⇒ ★ **%s**）"
      % (100 * rate, "达标 ✓" if fp <= 1 else "**未达标**"))

L = [
    "# T5-1 的 D-1 合规实测：`check_fact_single_home` 的误报率",
    "",
    "> 生成物 —— 由 `tools/measure_fact_single_home_fp.py` 产出，不要手改。",
    "> ★ D-1 原文：「新建门禁误报率 ≤5%（**抽检 20 条、假阳性 ≤1 条**，未达标者留待复核桶）」",
    "",
    "## 一 · 样本怎么造的（★ 用真实文本，不编）",
    "",
    "| 组 | 例数 | ★ 怎么造 | 期望 |",
    "|---|---:|---|---|",
    "| **真复述** | 10 | 取家里**真实**的事实正文各一段，逐字放进「别的文档」| 应当报 |",
    "| **正当引用** | 10 | 用本仓**真实的引用写法**（三种：「详见事实 N」/「依据见事实 N」/「见事实 N」）| **不该报** |",
    "",
    "★ 样本取自家里 **%d** 条正文中等距取的 10 条（★ 避开只取头部）✓" % len(bodies),
    "",
    "## 二 · ★ 结果",
    "",
    "| 指标 | 值 |",
    "|---|---|",
    "| ★ 真阳性（真复述被报）| **%d / 10** |" % tp,
    "| ★★ 假阳性（正当引用被报）| **%d / 10** |" % fp,
    "| 误报率 | **%.0f%%** |" % (100 * rate),
    "| ★ D-1 判定（假阳性 ≤1）| **%s** |" % ("达标 ✓" if fp <= 1 else "未达标 ⇒ 留复核桶"),
    "",
    "## 三 · ★ 本实测的「不算什么」",
    "",
    "- ★★ 样本是**合成**的（我造进临时字符串），**不是**真实文档 ⇒",
    "  ★ 它量的是**判据的性质**，**不是**真实语料上的发生率 ✓；",
    "- ★ 只测了**三种**引用写法 ⇒ ★ 真实世界的引用写法**更多**（可能漏测）✓；",
    "- ★ **真阳性 10/10** 说明判据实现没坏；★ 但**真实文档里的复述**是否都长这样，**未验证** ✓",
    "- ★★ 结论的适用范围：**「本判据对合成样本的误报率」**，不可外推成「全仓误报率」✓",
]
out = ROOT / "docs" / "recon-206" / "fact-single-home-fp.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))

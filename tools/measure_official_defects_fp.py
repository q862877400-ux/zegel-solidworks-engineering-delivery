"""★ D-1 合规实测（第 2 道门禁）：`check_official_source_defects` 的误报率与漏报率。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/measure_official_defects_fp.py
# 定位:   D-1 合规实测（第 2 道门禁）：`check_official_source_defects` 的误报率与漏报
#           率。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import check_official_source_defects as G                            # noqa: E402

ifaces, members, enums = G._real()
print("★ 本机真名: 接口 %d · 枚举 %d" % (len(ifaces), len(enums)))
real_ifaces = sorted(ifaces)[:10]
fake_ifaces = ["ZZZFakeOne", "ZZZFakeTwo", "ZZZFakeThree", "ZZZFakeFour", "ZZZFakeFive",
               "ZZZFakeSix", "ZZZFakeSeven", "ZZZFakeEight", "ZZZFakeNine", "ZZZFakeTen"]


def judge(files: dict) -> int:
    """★ 用门禁的**真判据**在临时目录上判（★ 不碰真仓库）⇒ 返回报出的处数。"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "scripts"
        d.mkdir()
        for name, text in files.items():
            (d / name).write_text(text, encoding="utf-8")
        old_root, old_dirs = G.ROOT, G.SCAN_DIRS
        try:
            G.ROOT, G.SCAN_DIRS = Path(td), ("scripts",)
            return len(G.scan())
        finally:
            G.ROOT, G.SCAN_DIRS = old_root, old_dirs


tp = fp = tn = fn = 0
rows = []
#: ★ ① 10 例「真断链」⇒ 期望报（★ 引用一个**确实不存在**的接口）
for i, fk in enumerate(fake_ifaces):
    got = judge({"a%d.py" % i: '# 来源: [[%s::SomeMember]]\n' % fk}) > 0
    tp += 1 if got else 0
    fn += 0 if got else 1
    rows.append(("真断链", fk, "应当报", got))
#: ★ ② 10 例「正当引用」⇒ 期望不报（★ 引用**确实存在**的接口）
for i, ok in enumerate(real_ifaces):
    got = judge({"b%d.py" % i: '# 来源: C:\\swapi\\types\\%s\\x.md\n' % ok}) > 0
    fp += 1 if got else 0
    tn += 0 if got else 1
    rows.append(("正当引用", ok, "不该报", got))

#: ★★★ ③ 10 例「**只带 `#:` 注释、不带文字标记**的真断链」⇒ ★★ 盲区测量（第 30 轮）：
#:   ★ 第 29 轮的 `CITATION` 里含泛化的 `^\s*#:` ⇒ ★★ 实测盲区 **10/10**（全放过）✓✗
#:   ⇒ ★ 本组样本**只带 `#:`**（★ 不带 `逐字`/`Superseded by`）⇒
#:     ★★ 收窄 `CITATION` 之后本组**应当被报** ⇒ ★ 这就是"收窄有没有效"的判据 ✓
blind = 0
for i, fk in enumerate(fake_ifaces):
    got = judge({"c%d.py" % i: '#: ★ 见 [[%s::SomeMember]]\n' % fk}) > 0
    blind += 0 if got else 1                    #: ★ 没报 ⇒ 落在盲区里
    rows.append(("只带 #: 的真断链", fk, "应当报（收窄后）", got))

print()
print("★ 结果（20 例）:")
print("   · ★ 真阳性（真断链被报）: **%d / 10**" % tp)
print("   · ★★ 假阳性（正当引用被报）: **%d / 10**" % fp)
print("   · ★ 漏报: **%d / 10**" % fn)
print("   · ⇒ D-1（假阳性 ≤1）: **%s**" % ("达标 ✓" if fp <= 1 else "**未达标**"))
print("   · ★★★ 盲区（带引文标记的真断链被放过）: **%d / 10**"
      " ← ★ 这就是引文判据（第 29 轮加的）的代价" % blind)

L = [
    "# D-1 合规实测（第 2 道门禁）：`check_official_source_defects`",
    "",
    "> 生成物 —— 由 `tools/measure_official_defects_fp.py` 产出，不要手改。",
    "> ★ D-1 原文：「新建门禁误报率 ≤5%（**抽检 20 条、假阳性 ≤1 条**，未达标者留待复核桶）」",
    "",
    "## 一 · 样本（20 例，★ 在临时目录上判，不碰真仓库）",
    "",
    "| 组 | 例数 | ★ 怎么造 | 期望 |",
    "|---|---:|---|---|",
    "| **真断链** | 10 | 引用**确实不存在**的接口（`[[ZZZFakeN::SomeMember]]`）| 应当报 |",
    "| **正当引用** | 10 | 引用**确实存在**的接口（★ 取自本机真名集合的前 10 个）| **不该报** |",
    "",
    "## 二 · ★ 结果",
    "",
    "| 指标 | 值 |",
    "|---|---|",
    "| ★ 真阳性（真断链被报）| **%d / 10** |" % tp,
    "| ★★ 假阳性（正当引用被报）| **%d / 10** |" % fp,
    "| ★ 漏报 | **%d / 10** |" % fn,
    "| ★ D-1 判定（假阳性 ≤1）| **%s** |" % ("达标 ✓" if fp <= 1 else "未达标 ⇒ 留复核桶"),
    "",
    "## 三 · ★ 本实测的「不算什么」",
    "",
    "- ★★ 样本是**合成**的（临时目录里的假文件）⇒ ★ 量的是**判据的性质**，**不是**真仓库上的命中率 ✓；",
    "- ★ 「真断链」用的是**我造的名字**（`ZZZFakeN`）⇒ ★ 它与「真断链」同形（都是查不到），",
    "  ★★ 但**不代表**真仓库里那些命中也是对的（★ 那要靠逐条判）✓；",
    "- ★ 「正当引用」只取**真名集合的前 10 个** ⇒ ★ 未覆盖全量真名 ✓；",
    "- ★★ 适用范围：**「本判据对合成样本的表现」**，**不可**外推 ✓",
    "",
    "## 四 · ★ 与首轮真实命中的关系",
    "",
    "★ 该门禁首次真跑时报 6 处，其中：★ **4 处真断链**（`[[SketchManager::…]]`，已修）、",
    "★★ **2 处边界**（`[[IFeatureManager::IInsertMidSurface]]` 的 `I` 前缀 · `[[Iface::Member]]` 模板占位）",
    "⇒ ★ 那 2 处**不在本 20 例的范围内**（★ 它们是**半真半假**的引用，本实测的样本是纯真/纯假）",
    "⇒ ★★ **它们仍需人判** ✓",
]
out = ROOT / "docs" / "recon-206" / "official-defects-fp.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print()
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
for kind, nm, exp, got in rows[:4]:
    print("   %-10s %-24s %s ⇒ %s" % (kind, nm, exp, "报了" if got else "没报"))

"""★ T3-2：把已核验的错拼名逐个配对到本机真名（编辑距离），出「错拼 → 正确名」表。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def lev(a: str, b: str) -> int:
    """★ 编辑距离（★ 只用于"错拼"这一类：官方源里同一接口的两种拼法差 1–2 个字符）。"""
    if abs(len(a) - len(b)) > 3:
        return 99
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


#: ★ 本机真名集合（接口目录 + 枚举页）
TD, ED = Path(r"C:\swapi\types"), Path(r"C:\swapi\enums")
real = set()
if TD.is_dir():
    real |= {p.name for p in TD.iterdir() if p.is_dir()}
if ED.is_dir():
    real |= {p.stem for p in ED.glob("*.md")}
print("★ 本机真名: **%d**" % len(real))

rows = json.loads((ROOT / "specs" / "203-bunny-sideline-batches" / "recon"
                   / "b2-defects.json").read_text(encoding="utf-8"))
verified = [r for r in rows if r.get("verified") is True or str(r.get("verified")).lower() == "true"]
spelling = [r for r in verified if r.get("type") == "spelling"]
print("★ 已核验 spelling: **%d** 条" % len(spelling))

#: ★ 错拼候选名 = 不是本机真名、且形状像 COM 标识符的名字（★ 从 why/quote 里抽）
import re
CAND = re.compile(r"\b([A-Z][A-Za-z0-9]{3,})\b")
pairs: dict = {}
for r in spelling:
    blob = "%s\n%s\n%s" % (r.get("quote_a") or "", r.get("quote_b") or "", r.get("why") or "")
    for m in CAND.finditer(blob):
        nm = m.group(1)
        if nm in real or nm in pairs:
            continue
        #: ★ 与某个真名的编辑距离 ≤2 ⇒ 判为「该真名的错拼」
        best = None
        for cand in real:
            if abs(len(cand) - len(nm)) > 2:
                continue
            d = lev(nm, cand)
            if d <= 2 and (best is None or d < best[1]):
                best = (cand, d)
        if best:
            nm_is, cor = nm, best[0]
            #: ★★★ 拆两类（★ 编辑距离**分不开**它们 —— 这是我这次判据宽了的根因）：
            #:   ① `少 I 前缀`：正确名恰是错名前面加个 `I`（如 `Attribute` → `IAttribute`）
            #:      ⇒ ★ 这不是"拼错"，是**官方链接写法不完整**（真名带 I 前缀）✓
            #:   ② `真错拼`：其余（字母换位 / 漏字母，如 `IConfiguraiton` → `IConfiguration`）
            #:      ⇒ ★ 这才是"照它写就一定失败"的那种 ✓
            cls = "少I前缀" if cor == "I" + nm_is else "真错拼"
            pairs[nm_is] = {"correct": cor, "dist": best[1], "cls": cls,
                          "why": (r.get("why") or "")[:110]}

print("★★ 抽到「错拼 → 正确名」配对: **%d** 对" % len(pairs))
print()
L = [
    "# 官方源里的**错拼名 → 正确名**表（★ T3-2：554 条 `spelling` 的机械复核）",
    "",
    "> 生成物 —— 由 `tools/t3_2_spelling_pairs.py` 产出，不要手改。",
    "> 输入：`specs/203-bunny-sideline-batches/recon/b2-defects.json`（另一个对话的 B2 扫描，只读复用）",
    "> + 本机 `C:\\swapi\\types`（566 接口目录）与 `C:\\swapi\\enums`（枚举页）。",
    "",
    "## 一 · 口径",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 本机真名集合 | **%d**（接口目录 + 枚举页）|" % len(real),
    "| 已核验 `spelling` | **%d** 条（★ 其总数 554）|" % len(spelling),
    "| ★ 本表配对出 | **%d** 对「错拼 → 正确名」|" % len(pairs),
    "",
    "★★ 本表「不算什么」：",
    "",
    "- ★ 判据是**编辑距离 ≤2 且长度差 ≤2** —— ★ 这是**启发式**，不是官方裁定；",
    "  ★ 若两个真名都很近，本表只取**最近的**一个 ⇒ ★ **可能有歧义未标**（需人核）；",
    "- ★ 配不上对的名字**不在本表里**（★ 它们可能是：名字根本没拼错、或错得太多没法猜）"
    "⇒ ★ **不要**读成「本表就是全部错拼」✓；",
    "- ★ 来源是另一个对话的 `conditional_pass` 产出 ✓",
    "",
    "## 二 · ★ 真错拼（★ 照它写就一定失败的那种）",
    "",
    "| 错拼 | ★ 正确名 | 编辑距离 | 官方源的解释 |",
    "|---|---|---:|---|",
]
for nm, info in sorted(pairs.items(),
                       key=lambda kv: (kv[1]["cls"] != "真错拼", kv[1]["dist"], kv[0])):
    if info["cls"] == "真错拼":
        L.append("| `%s` | `%s` | %d | %s |"
                 % (nm, info["correct"], info["dist"], info["why"].replace("|", "/")[:100]))
n_true = sum(1 for v in pairs.values() if v["cls"] == "真错拼")
n_pref = len(pairs) - n_true
L += [
    "",
    "## 三 · ★ 少 `I` 前缀（**不是拼错** —— 是官方**链接写法不完整**）",
    "",
    "★ 官方页里写 `[[Attribute::X]]`，而真名是 `IAttribute` ⇒ ★ 这**不影响我们写码**",
    "（我们写的是真名），★ 但**影响我们读官方链接** ⇒ 查的时候要自己补 `I` ✓",
    "★★ 它与上一节是**两个不同的缺陷类** —— ★ 而**编辑距离分不开它们**",
    "（这正是本次判据又宽了一次的根因，★ 已记进事实）✓",
    "",
    "| 官方链接里写 | ★ 真名 |",
    "|---|---|",
]
for nm, info in sorted(pairs.items(),
                       key=lambda kv: (kv[1]["cls"] != "少I前缀", kv[0])):
    if info["cls"] == "少I前缀":
        L.append("| `%s` | `%s` |" % (nm, info["correct"]))
L += [
    "",
    "★ **两类计数**：真错拼 **%d** · 少 `I` 前缀 **%d** ✓" % (n_true, n_pref),
]
L += [
    "",
    "## 三 · ★ 怎么用",
    "",
    "★ 与 `scripts/check_official_source_defects.py` 配合：那个门禁管**我们引用的官方页是否存在**；",
    "★ 本表管**名字本身该拼成什么** ⇒ ★ 写码时若不确定某个接口名，先查本表 ✓",
    "",
    "★ **两份合起来的覆盖**：本表（名字拼法）· 门禁（引用是否存在）· `docs/official-source-errors.md`（抄录指引）·",
    "`docs/recon/official-source-defects-2.md`（964 条穷举）✓",
]
out = ROOT / "docs" / "recon-206" / "spelling-pairs.md"
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out.name, len(L)))
print()
for nm, info in sorted(pairs.items(), key=lambda kv: (kv[1]["dist"], kv[0]))[:10]:
    print("   %-22s → %-22s (d=%d)" % (nm, info["correct"], info["dist"]))

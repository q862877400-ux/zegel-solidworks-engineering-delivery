"""★ T4-1 修正：用 `ast` 精确区分「真调用」与「注释/文档里的提及」—— 修正上一轮的高估。"""
from __future__ import annotations

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 上一轮说有冲突的成员（★ 从 c4 里重取，不硬编码）
rows = json.loads((ROOT / "specs" / "204-bunny-moat-batches" / "recon"
                   / "c4-merged.json").read_text(encoding="utf-8"))["results"]
WANT = ("unit_diff", "mark_diff")
conf: dict = defaultdict(list)
for cap in rows:
    for c in (cap.get("conflicts") or []):
        if str(c.get("kind")) in WANT:
            conf[cap.get("member")].append(c.get("kind"))
members = sorted(conf)
print("★ 25 条冲突涉及 %d 个成员" % len(members))

SRC = []
for d in ("scripts", "mcp-server", "tools"):
    SRC += sorted((ROOT / d).rglob("*.py"))


def real_uses(path: Path, member: str) -> list:
    """★ **真调用**的两种形态（★ 用 `ast`，不是文本匹配）：

    ① `get_com_member(<任意>, "member")` —— ★ 第二实参是字符串常量
    ② `<任意>.member` —— ★ 属性访问
    ⇒ ★ 其余（docstring / 注释 / 散文里的 `"member"`）**一律算提及** ✓
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            if name == "get_com_member" and len(n.args) >= 2:
                a = n.args[1]
                if isinstance(a, ast.Constant) and a.value == member:
                    out.append((n.lineno, "get_com_member"))
        elif isinstance(n, ast.Attribute) and n.attr == member:
            out.append((n.lineno, "attr_access"))
    return out


#: ★★ 判据的**否定面自证**（★ 事实 517 定则二）：同时数一遍"文本命中数"，
#:    用来展示**高估了多少**（★ 上一轮的口径）
import re
real: dict = {}
text_hits: dict = {}
for m in members:
    hits = []
    for f in SRC:
        for ln, how in real_uses(f, m):
            hits.append((str(f.relative_to(ROOT)), ln, how))
    real[m] = hits
    n = 0
    for f in SRC:
        try:
            n += len(re.findall(r'"%s"' % re.escape(m), f.read_text(encoding="utf-8", errors="replace")))
        except Exception:                                          # noqa: BLE001
            pass
    text_hits[m] = n

used_real = [m for m in members if real[m]]
only_text = [m for m in members if not real[m] and text_hits[m]]
none = [m for m in members if not real[m] and not text_hits[m]]
print()
print("★★ 真调用（ast 判）: **%d** 个 %s" % (len(used_real), ", ".join(used_real)))
print("★★ 只出现在文本里（★ 提及，非调用）: **%d** 个 %s" % (len(only_text), ", ".join(only_text)))
print("★★ 完全没出现: **%d** 个 %s" % (len(none), ", ".join(none)))
print()
print("★ 真调用的逐条（★ 这才是要人核的）:")
for m in used_real:
    kinds = ", ".join(sorted({k for _f, _l, k in real[m]}))
    f0, l0, _k0 = real[m][0]
    print("   %-30s %s:%d (%s) 共 %d 处" % (m, f0, l0, kinds, len(real[m])))
print()
print("★★ 与上一轮对比（★ 高估了多少）:")
print("   上一轮（文本匹配口径）: 用了 8 个")
print("   本轮（ast 精确口径）  : 真调用 %d 个 ⇒ ★ 高估 %d 个" % (len(used_real), 8 - len(used_real)))

#: ★ 把修正追加进上一轮那张表（★ 不覆盖原文 —— 保留"我改了什么"的痕迹）
out = ROOT / "docs" / "recon-206" / "conflicts-25-crosscheck.md"
L = [
    "",
    "---",
    "",
    "## 五 · ★★ 修正（★ 2026-10-04 第 12 轮）：上一轮的「用了」口径**高估了**",
    "",
    "★ 触发：判读第一条（`AutoDimension2`）时发现 7 处命中里 **6 处是注释/docstring 里的提及** ⇒",
    "★ 即上一轮判据的第三种写法（字符串字面量）**把提及也算成了使用** —— ★ 那正是上一轮",
    "「本表不算什么」第 ③ 条**预告过的风险**，现在**实测确认它发生了** ✓",
    "",
    "★★ 本轮改用 `ast` 精确判：**真调用**只有两种形态 ——",
    "`get_com_member(<任意>, \"member\")` 的**第二实参**、或 `<任意>.member` 的**属性访问**；",
    "★ 其余（docstring / 注释 / 散文里的字符串）**一律算提及** ✓",
    "",
    "| 口径 | 「用了」的成员数 |",
    "|---|---|",
    "| 上一轮（文本匹配）| **8** |",
    "| ★★ 本轮（`ast` 精确）| **%d** |" % len(used_real),
    "| ⇒ 高估 | **%d** 个 |" % (8 - len(used_real)),
    "",
    "### 5.1 ★ 真调用（`ast` 判 · 需要人核的那批）",
    "",
    "| 成员 | 引用处 | 方式 |",
    "|---|---|---|",
]
for m in used_real:
    for f, l, k in real[m][:8]:
        L.append("| `%s` | `%s:%d` | %s |" % (m, f, l, k))
L += ["", "### 5.2 ★ 只出现在文本里（提及，非调用）—— 上一轮被误算成「用了」的", ""]
for m in only_text:
    L.append("- `%s`（文本命中 %d 处，真调用 0 处）" % (m, text_hits[m]))
L += ["", "### 5.3 完全没出现", ""]
for m in none:
    L.append("- `%s`" % m)
L += ["", "★ **口径**：本轮判据的否定面已写明（提及不算）；",
      "★ 但它仍有边界：`getattr(obj, \"member\")` 这类**动态取用**不在两种形态里 ⇒ 会漏 ✓",
      "★ 另有冲突类 %s 的成员分布见 `conflicts-25.md` ✓" % "/".join(sorted({k for v in conf.values() for k in v}))]
out.write_text(out.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(L) + "\n",
               encoding="utf-8")
print()
print("★ 已把修正追加进 %s" % out.name)

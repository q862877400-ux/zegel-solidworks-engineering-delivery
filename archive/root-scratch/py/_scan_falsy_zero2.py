"""按**正确判据**重数 `or <默认>` 的零值吞噬 bug。

## 正确判据（**我第一版数错了，这里记下为什么**）
```python
int(x or 0)      # x == 0 ⇒ 0 or 0 = 0      ⇒ 幂等 ⇒ **无害**
float(x or 0.0)  # x == 0.0 ⇒ 0.0 or 0.0 = 0.0 ⇒ 幂等 ⇒ **无害**
int(x or -1)     # x == 0 ⇒ 0 or -1 = **-1**  ⇒ **吞掉合法的 0** ⇒ 真 bug
```
⇒ **只有「默认值 ≠ 该类型的 falsy 值」才有害。** 我第一版把 `or 0.0` 也标成有害 ⇒ **假阳性**。
（本项目纪律：「门禁首跑必然有假阳性 ⇒ 必须用真实数据核对」，这次是**我自己**撞上的。）
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")

#: `get_com_member(x, "Y") or <字面量>`
PAT = re.compile(r'"(\w+)"\s*\)\s*or\s+(-?\d+(?:\.\d+)?|""|\'\')')

#: 该类型的**幂等默认值**（or 之后结果不变）⇒ 无害
IDEMPOTENT = {"0", "0.0", '""', "''"}

hits = []
for f in sorted((REPO / "scripts").glob("sw_*.py")):
    txt = f.read_text(encoding="utf-8", errors="replace")
    for m in PAT.finditer(txt):
        ln = txt[: m.start()].count("\n") + 1
        default = m.group(2)
        if default in IDEMPOTENT:
            continue                      # 无害
        hits.append((f.name, ln, m.group(1), default))

by_mod: dict[str, int] = {}
for name, _, _, _ in hits:
    by_mod[name] = by_mod.get(name, 0) + 1

print("  ⚠ **真 bug**（默认值 ≠ falsy 值 ⇒ 会吞掉合法的 0）：共 **%d** 处 / %d 个模块"
      % (len(hits), len(by_mod)))
print()
for name in sorted(by_mod, key=lambda k: -by_mod[k]):
    print("   %-30s %d 处" % (name, by_mod[name]))
print()
print("  ⚠ 它们**不一定**都是真故障 —— 只有当那个成员的 **0 是有意义的值**时才是。")
print("     例：`AnalysisType or -1` ⇒ AnalysisType==0 是合法的「静力学」⇒ 会被误报成 -1 ⇒ **是 bug**。")
print("     反例：某个「错误码」成员，0 == 成功 而默认 -1 == 未知 ⇒ 也是 bug（把成功报成未知）。")
print("  ⇒ 结论：**这一族全是「哨兵值与合法值撞车」**，都该修，但要不要一次全改由人定（事实 61）。")

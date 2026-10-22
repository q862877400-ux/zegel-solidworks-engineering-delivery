"""★ 把 bunny 对比稿里的**分歧点**抽出来分类 —— 找"批量推进"的规律（★ 业主指令）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/classify_audit_divergences.py
# 定位:   把 bunny 对比稿里的**分歧点**抽出来分类 —— 找"批量推进"的规律（★ 业主指令）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = (
    Path(Path(__file__).resolve().parents[1])
    / "specs"
    / "202-user-coverage-gaps"
    / "recon"
    / "audit-vs-official"
)

#: ★ 分歧的**根因类**（★ 关键词按本仓既有事实命名，便于对上 known-facts）
PATTERNS = [
    ("★ mark 值不对/没给", ("mark", "Mark", "标记")),
    (
        "★ 参数个数不符",
        ("参数个数", "少一个", "多一个", "个数", "共 \\d+ 个参", "参不对"),
    ),
    ("★ 参数顺序不符", ("顺序", "次序")),
    ("★ 标量 vs 数组", ("数组", "标量", "SafeArray", "VARIANT", "array")),
    (
        "★ 类型不符（short/int/bool/double）",
        ("类型", "short", "int 型", "bool", "double", "long"),
    ),
    ("★ 用了废弃成员", ("Obsolete", "废弃", "已废弃", "Superseded")),
    ("★ 枚举取值不是合法成员", ("枚举", "enum", "不是合法", "非法值")),
    (
        "★ 少调了官方要求的步骤",
        ("没有调", "未调用", "缺少调用", "少了叫", "少一步", "未先"),
    ),
    ("★ 前置没做（先选/先建）", ("先选", "前置", "未选", "调用前", "必须先")),
    ("★ 返回值/出参形状不符", ("出参", "返回值", "out ", "byref", "指针")),
]

rows = []
for f in sorted(D.glob("audit-*.md")):
    t = f.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"audit-(\d+)-([a-z0-9\-]+)-([ABC])\.md", f.name)
    chk = m.group(3) if m else "?"
    for line in t.splitlines():
        if not re.match(r"\|\s*\d+\s*\|", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            continue
        rows.append(
            {
                "file": f.name,
                "check": chk,
                "ours": cells[1],
                "theirs": cells[2],
                "what": cells[3],
            }
        )

print("★ 抽出分歧行：**%d** 条" % len(rows))
cnt = Counter()
for r in rows:
    blob = r["what"] + " " + r["theirs"]
    hit = None
    for name, keys in PATTERNS:
        if any(re.search(k, blob) for k in keys):
            hit = name
            break
    r["pattern"] = hit or "（未能归类）"
    cnt[r["pattern"]] += 1

print()
print("%-34s %s" % ("根因类", "条数"))
print("-" * 52)
for name, n in cnt.most_common():
    print("%-34s %d" % (name, n))
print()
print("★ 按**核对面 × 根因类**：")
comb: Counter = Counter()
for r in rows:
    comb[(r["check"], r["pattern"])] += 1
for (chk, pat), n in sorted(comb.items()):
    print("   %s × %-32s %d" % (chk, pat, n))
print()
print("★ 逐条（前 24 条，★ 用来看「规律」是不是真的）：")
for r in rows[:24]:
    print("   [%s] %-30s %s" % (r["check"], r["pattern"][:28], r["what"][:96]))

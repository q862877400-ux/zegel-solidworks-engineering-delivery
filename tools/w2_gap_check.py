"""W2：把 ⑪工程图 的 49 个缺口名逐个核「我们是否已有实现」。

★ 判据（避免"名字不同就当成没做"这个错）：
  对每个缺口名，取其**动作词 + 对象词**，去 `scripts/` 里找：
    ① 同名的函数 / 模块（可能只是没挂）
    ② 名字里含同一对词的函数
  命中 ⇒ 标「可能已有」（**仍需人工确认**，不当结论）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\w2_gap_check.py
# 定位:   回答「⑪工程图 的 49 个缺口里，多少是我们已有实现却没挂的」。
# 官方依据: `tools/union-sources.json`（缺口名的权威来源）
# 许可:   本仓库 MIT。
# ⚠ 启发式，输出只作线索，不作结论（事实 51：先问"分析范围对不对"）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"" + _ROOT_S + r"")
u = json.loads((REPO / "tools" / "union-sources.json").read_text(encoding="utf-8"))

#: 取 ⑪ 的缺口名（矩阵里那个数来自同一份数据）
ops = u.get("union_operations") or []
drawing = []
for o in ops:
    if isinstance(o, dict):
        dom = str(o.get("domain") or o.get("domain_cn") or "")
        nm = str(o.get("name") or o.get("op") or "")
        if "工程图" in dom or "drawing" in dom.lower():
            drawing.append(nm)
    elif isinstance(o, str):
        pass
print("  ⑪ 缺口名（从 union_operations 取）: **%d** 个" % len(drawing))
if not drawing:
    print("  ⚠ 取不到 —— 先看 union_operations 的字段形状")
    k = ops[0] if ops else {}
    print("     样例:", json.dumps(k, ensure_ascii=False)[:300] if isinstance(k, dict) else str(k)[:200])
    sys.exit(0)

#: 我们的函数名全集
ours: dict[str, str] = {}
for p in (REPO / "scripts").glob("sw_*.py"):
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"(?m)^def ([a-z_]\w*)\s*\(", t):
        ours.setdefault(m.group(1), p.name)

STOP = {"a", "the", "of", "and", "to", "in", "with", "for", "by"}
hit_same, hit_words, miss = [], [], []
for nm in drawing:
    if nm in ours:
        hit_same.append((nm, ours[nm]))
        continue
    words = [w for w in re.split(r"[_\W]+", nm.lower()) if w and w not in STOP]
    found = []
    for on, mod in ours.items():
        ol = on.lower()
        if ol == nm.lower() or all(w in ol for w in words if len(w) > 2):
            found.append("%s(%s)" % (on, mod))
    (hit_words if found else miss).append((nm, found[:3]))

print("  ① **同名函数已在** : %d" % len(hit_same))
for nm, mod in hit_same[:8]:
    print("       %-34s → %s" % (nm, mod))
print("  ② **名字含同一批词** : %d" % len(hit_words))
for nm, f in hit_words[:14]:
    print("       %-34s → %s" % (nm, ", ".join(f)))
print("  ③ 没找到对应 : %d" % len(miss))
for nm, _ in miss[:10]:
    print("       %s" % nm)

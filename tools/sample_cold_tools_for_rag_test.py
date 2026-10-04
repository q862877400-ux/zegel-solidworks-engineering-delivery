"""★ 机械抽样：从全部工具清单里挑一批**冷门**的（★ 不靠我的口味）。

★ 为什么要有它（业主 2026-10-04 批评）：
  我上一轮的 24 个任务**全是常见功能**（圆角/拉伸/导出/质量属性/压力载荷…）
  ⇒ ★★ **选择偏倚** ⇒ 那个 88–92% 是**乐观值** ✓
  ⇒ 本脚本按**机械判据**分层抽样，把"冷门"变成可复核的事 ✓

★ 「冷门」的机械定义（三档，从强到弱）：
  C1 ★★ **任何中文清单里都查不到**：`docs/usage-guide.md`（域→模块）、
     `docs/user-feature-coverage.md`（145 项）、`capabilities.yaml`（112 条能力的 mcp_tools）
     —— 都不提它 ⇒ **没有人为它写过面向用户的话** ✓
  C2 ★ **所在域是长尾**：该 module 的工具有限（< 8 个）
  C3 ★ **它的 doc 很短**（< 120 字符）⇒ 少被人打磨过 ✓
  ★ 另单列一档 **NON-API**：取不到官方 COM 成员名的（本仓自研 GUI/报表层）✓

★ 输出：`output/rag-sample.json` —— 给扇出的 Bunny 用（★ 它们照这些记录产中/英查询）。
"""
from __future__ import annotations

import ast
import io
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                    # noqa: E402

SEED = 20261004
TARGET_PER_STRATUM = 40          #: ★ 每档 40 ⇒ 总 ~120–160（比上一轮 24 大 5–6 倍）


def read_docs() -> str:
    """★ 把三份中文清单拼起来（用于判"有没有人给它写过面向用户的话"）。"""
    parts = []
    for rel in ("docs/usage-guide.md", "docs/user-feature-coverage.md", "capabilities.yaml"):
        p = ROOT / rel
        if p.is_file():
            parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def has_official_member(module: str, function: str) -> bool:
    """★ 能否在该函数体里取到逐字的 COM 成员名（取不到 ⇒ 本仓自研层）。"""
    p = ROOT / "scripts" / (module + ".py")
    if not p.is_file():
        return False
    try:
        tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    except Exception:                                                  # noqa: BLE001
        return False
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == function), None)
    if fn is None:
        return False
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and len(n.args) >= 2:
            a = n.args[1]
            if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                    and re.match(r"^[A-Z][A-Za-z0-9_]{2,}$", a.value):
                return True
    return False


def main() -> int:
    docs = read_docs()
    specs = rc.all_specs()
    per_mod = Counter(getattr(s, "module", "") for s in specs)
    rng = random.Random(SEED)
    recs = []
    for s in specs:
        doc = getattr(s, "doc", "") or ""
        #: ★ 机械判据 ① 该工具名在中文清单里出现过吗
        #: ★★ 2026-10-04 修：原先写 `core in docs`（**子串**匹配）⇒ `part` 会命中
        #:   任何含 "part" 的词 ⇒ 把大量**真冷门**误判成"有文档" ⇒ 冷门池被压到只剩 44 ✓
        #:   ⇒ 改成**词边界**匹配（名字两侧必须是非字母数字）✓
        core = s.name.removeprefix("solidworks_")
        pat = r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(s.name)
        pat2 = r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(core)
        mentioned = bool(re.search(pat, docs)) or bool(re.search(pat2, docs))
        mod = getattr(s, "module", "")
        recs.append({
            "tool": s.name, "module": mod, "function": getattr(s, "function", ""),
            "title": getattr(s, "title", "") or "",
            "doc": doc, "doc_len": len(doc),
            "params": [p.name for p in (getattr(s, "params", None) or [])],
            "domain_size": per_mod[mod],
            "mentioned_in_cn_docs": mentioned,
            "has_official_member": has_official_member(mod, getattr(s, "function", "")),
        })

    cold_strong = [r for r in recs if not r["mentioned_in_cn_docs"]
                   and r["domain_size"] < 8 and r["has_official_member"]]
    cold_soft = [r for r in recs if not r["mentioned_in_cn_docs"]
                 and r["doc_len"] < 120 and r["has_official_member"]]
    non_api = [r for r in recs if not r["has_official_member"]]
    hot = [r for r in recs if r["mentioned_in_cn_docs"] and r["domain_size"] >= 8]

    def pick(pool, n):
        pool = sorted(pool, key=lambda x: x["tool"])       #: ★ 先定序，保证可复现
        rng.shuffle(pool)
        return pool[:n]

    sample = {
        "C1_cold_no_cn_doc_small_domain": pick(cold_strong, TARGET_PER_STRATUM),
        "C2_cold_thin_doc": pick(cold_soft, TARGET_PER_STRATUM),
        "C3_non_api_selfmade": pick(non_api, TARGET_PER_STRATUM),
        "H_hot_baseline": pick(hot, 20),
    }
    print("★ 框架：433 个工具 · 域 %d 个" % len(per_mod))
    print("★ 三档候选池大小：C1(无中文文档 ∧ 长尾域) **%d** · C2(无中文文档 ∧ doc<120) **%d** · "
          "NON-API **%d** · HOT(基线) **%d**" % (len(cold_strong), len(cold_soft), len(non_api), len(hot)))
    print("★ 抽样（seed=%d）：%s" % (SEED, {k: len(v) for k, v in sample.items()}))
    print()
    for k, v in sample.items():
        print("  【%s】%d 个 ⇒ 例：%s" % (k, len(v),
              ", ".join(x["tool"].removeprefix("solidworks_") for x in v[:5])))
    out = ROOT / "output" / "rag-sample.json"
    out.write_text(json.dumps({"seed": SEED, "target_per_stratum": TARGET_PER_STRATUM,
                               "strata": {k: [x["tool"] for x in v] for k, v in sample.items()},
                               "records": {x["tool"]: x for v in sample.values() for x in v}},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ 写出：%s（★ 共 %d 条记录）" % (out, sum(len(v) for v in sample.values())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

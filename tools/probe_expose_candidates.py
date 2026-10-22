r"""@brief 换口径找暴露候选：**「未暴露 + 被生产代码调用」** 比「孤立」更靠得住。

## 为什么要换（2026-10-01 轮 97，Spec Kit `017`）
`012`/`013`/`016` 三轮的候选都来自「**孤立能力**」（既没暴露、也没人调用）。
轮 97 撞见一个反例：`sw_review.collect_model_summary` **已经遍历特征树并返回 JSON-ready 数据**
（正是我想暴露的"特征树遍历"能力），**却没暴露** —— 只因为它**被生产代码调用**，所以不算"孤立"。

★ **孤立 ≠ 该暴露；未暴露 ≠ 孤立。** 两个口径的交集才是"便宜且可能有用"，
但**「未暴露 + 被调用」的池子更可能是好的**（有调用者 ⇒ 跑过的概率更高）。

## 判据
* **未暴露**：不在 `server.py` 分发表、也不在 `tool_specs_batch*.py` 的 `function=` 里；
* **被生产代码调用**：在 `scripts/` / `subskills/` / `examples/` / `mcp-server/` 里被调过
  （⇒ **有人用过 ⇒ 比孤立函数更可能真的能跑**）；
* **签名兼容**：首参 `model` 或完全无参（不需要新解析器）。

⚠ 本工具**只出候选清单**，不下"该暴露"结论。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_expose_candidates.py
# 定位:   给 Spec Kit `017` 取证：换口径重找暴露候选。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib
import inspect
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

DEF = re.compile(r"^def ([a-z_]\w*)\(", re.M)
INTERNAL = re.compile(
    r"(_to_|_from_|^parse|^normalize|^empty|^variant|^callout|^pump|^_|^get_com|^coerce|^make_empty|^try_|^is_|^has_)"
)


def main() -> int:
    funcs: dict = {}
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        for fn in DEF.findall(p.read_text(encoding="utf-8", errors="ignore")):
            funcs.setdefault(fn, p.name)

    srv = (ROOT / "mcp-server" / "server.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    exposed = {f for _, f in re.findall(r'"(\w+)":\s*[A-Za-z_]\w*\.(\w+)\s*,', srv)}
    for p in (ROOT / "mcp-server").glob("tool_specs_*.py"):
        exposed |= set(
            re.findall(
                r'function="([\w]+)"', p.read_text(encoding="utf-8", errors="ignore")
            )
        )

    called: set = set()
    for d in ("scripts", "subskills", "examples", "mcp-server"):
        base = ROOT / d
        if not base.is_dir():
            continue
        for p in base.rglob("*.py"):
            src = p.read_text(encoding="utf-8", errors="ignore")
            others = {f for f, o in funcs.items() if o != p.name}
            for m in re.finditer(r"\b(\w+)\s*\(", src):
                if m.group(1) in others:
                    called.add(m.group(1))

    rows = []
    for f, mod in sorted(funcs.items()):
        if f in exposed or INTERNAL.search(f) or f not in called:
            continue
        try:
            fn = getattr(importlib.import_module("scripts.%s" % mod[:-3]), f)
            sig = inspect.signature(fn)
        except Exception:  # noqa: BLE001
            continue
        ps = list(sig.parameters.values())
        if ps and ps[0].name != "model":
            continue
        if len(ps) > 3:
            continue
        rows.append((mod, f, str(sig)))

    by_mod = defaultdict(list)
    for mod, f, s in rows:
        by_mod[mod].append((f, s))

    print(
        "=== 「未暴露 + 被生产代码调用 + 签名兼容」的候选：**%d** 个，跨 %d 个模块 ==="
        % (len(rows), len(by_mod))
    )
    print("（⚠ 这个池子比「孤立」更可能真的能跑 —— 有调用者 = 有人用过）")
    print()
    for mod in sorted(by_mod, key=lambda m: -len(by_mod[m]))[:10]:
        print("── %s（%d）" % (mod, len(by_mod[mod])))
        for f, s in by_mod[mod][:6]:
            print("     %-42s %s" % (f, s[:56]))
        if len(by_mod[mod]) > 6:
            print("     …（还有 %d 个）" % (len(by_mod[mod]) - 6))
    print()
    print("★ 对照：`012`/`013`/`016` 用的口径是「**孤立**」（既没暴露、也没人调用）——")
    print("  本次证明那个口径**会漏掉更好的**（`collect_model_summary` 就是一例）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

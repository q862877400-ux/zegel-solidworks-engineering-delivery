r"""@brief 量第三个池子：**「未暴露 + 只被测试调用」** —— 前两个口径都漏了它。

## 为什么（2026-10-01 轮 97，Spec Kit `017`）
三轮（`012`/`013`/`016`）用「**孤立**」（既没暴露、也没人调用）选候选；
轮 97 想暴露"特征树遍历"时撞见 `sw_review.collect_model_summary` ——
**它已经遍历特征树并返回 JSON-ready 数据**，正是要的能力，**却没暴露**。

查它为什么没被发现：
```
出现位置：scripts/sw_review.py（定义）· tests/solidworks_spur_gear_regression.py（调用）
⇒ **只被测试调用** ⇒ 两个口径都把它排除了：
   · 孤儿口径排掉"有调用者"的；
   · "被生产代码调用"口径排掉"只被测试调用"的。
```

★ **而这一池特性最好**：**有测试 ⇒ 跑过的概率高**；**未暴露 ⇒ 用户够不到**。

⚠ 本工具**只出候选清单**，不下"该暴露"结论。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_testonly_candidates.py
# 定位:   给 Spec Kit `017` 取证：第三个候选池（未暴露 + 只被测试调用）。
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
    r"(_to_|_from_|^parse|^normalize|^empty|^variant|^callout|^pump|^_|^get_com|"
    r"^coerce|^make_empty|^try_|^is_|^has_|^main$|^session$|^connect$|^cache_drop$)"
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

    def _callers(dirs):
        got: set = set()
        for d in dirs:
            base = ROOT / d
            if not base.is_dir():
                continue
            for p in base.rglob("*.py"):
                src = p.read_text(encoding="utf-8", errors="ignore")
                others = {f for f, o in funcs.items() if o != p.name}
                for m in re.finditer(r"\b(\w+)\s*\(", src):
                    if m.group(1) in others:
                        got.add(m.group(1))
        return got

    prod = _callers(("scripts", "subskills", "examples", "mcp-server"))
    tests = _callers(("tests",))

    rows = []
    for f, mod in sorted(funcs.items()):
        if f in exposed or INTERNAL.search(f):
            continue
        if f in prod or f not in tests:  # ★ **只要"只被测试调用"**
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

    by = defaultdict(list)
    for mod, f, s in rows:
        by[mod].append((f, s))

    print(
        "=== 「未暴露 + **只被测试调用** + 签名兼容」：**%d** 个，跨 %d 个模块 ==="
        % (len(rows), len(by))
    )
    print("★ 这一池特性最好：**有测试 ⇒ 跑过的概率高** · **未暴露 ⇒ 用户够不到**")
    print()
    for mod in sorted(by, key=lambda m: -len(by[m])):
        print("── %s（%d）" % (mod, len(by[mod])))
        for f, s in by[mod][:7]:
            print("     %-42s %s" % (f, s[:54]))
        if len(by[mod]) > 7:
            print("     …（还有 %d 个）" % (len(by[mod]) - 7))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

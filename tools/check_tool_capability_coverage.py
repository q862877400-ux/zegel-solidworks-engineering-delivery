r"""@brief **门禁：每个工具都要有归属** —— ★ 一个 `solidworks_*` 工具必须至少被**一条能力条目**认领。

## ★★★ 为什么需要它（2026-10-01 轮 265 量出来的）
```
★ 清点：`all_specs()` = **117** 个工具；★ 而 `capabilities.yaml` 的 **58 条**能力条目里
  被引用的工具 = ★ **0** ⇒ ★★ **`mcp_tools` 字段根本没人填**。**
⇒ ★★★ **所以"能力清单"现在只说清"有哪些能力"，没说清"这个能力由**哪些工具**实现"** ——
   ★ 而那正是 A1/A4 想要的**映射**（★ 域级条目 ↔ 具体工具）。
⇒ ★★★★ **本条把它做成可跑的判据**，于是它以后**每次都给出一份"待办清单"**，
   ★ 而不是靠人记着（★ 事实 16：反复犯的错要机器化）。
```

## 判据（★ 刻意宽松，只抓"完全没归属"）
```
★ 对 `all_specs()` 的每个工具名：★ **它必须出现在某条能力条目的 `mcp_tools` 里**。
★★ **只报"一个都没被认领"的工具** —— ★ **不判"归属对不对"**（★ 那要人工判断，见 fact 191）。
⇒ ★★ 所以本门禁**假阳性为零**（★ 它只问「有没有人认领」这个事实问题）。
⚠ 与 `check_interface_member_ownership.py` 的 `MANUAL_MAP` 同一哲学：
   ★ **没有依据的不许进来** · ★ **输出分开报**。
```

## 输出
```
★ 逐模块列出**没有归属**的工具（★ 那就是「该补 `mcp_tools` 或补能力条目」的清单）
★★ 退出码：★ **恒为 0**（★ 它**现在是报告器，不是硬门禁** —— 因为映射还在补齐中）。
   ⚠ **为什么不硬失败**：★ 117 个工具一次补齐不现实；★ 而**硬失败会挡住所有别的提交**
     （★ 本项目有过这个教训 —— 门禁的价值在于**能跑**，不在于**能拦**）。
   ⇒ ★★ **等 `mcp_tools` 补齐到 100% 再转硬门禁**（★ 而那时把退出码改掉即可）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁/报告器）
# 文件:   tools/check_tool_capability_coverage.py
# 定位:   量"能力 ↔ 工具"的映射缺口（★ 事实 191 的正路：缺口要在**条目/域**这一级找）。
# 官方依据: 不适用（本项目内部口径）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")


def _cited_tools(cap_path: Path) -> set:
    """★ 能力条目里 `mcp_tools` 引用的工具名（★ 容错：字符串或列表都能读）。"""
    cited: set = set()
    if not cap_path.is_file():
        return cited
    data = json.loads(cap_path.read_text(encoding="utf-8"))
    for c in data.get("capabilities", []):
        raw = c.get("mcp_tools") or []
        if isinstance(raw, str):
            raw = [raw]
        for t in raw:
            if isinstance(t, str):
                cited.add(t)
            elif isinstance(t, (list, tuple)):
                cited.update(x for x in t if isinstance(x, str))
    return cited


def main() -> int:
    import register_capabilities as rc

    specs = rc.all_specs()
    cited = _cited_tools(ROOT / "capabilities.yaml")
    by_name = {s.name: s for s in specs}
    uncited = sorted(set(by_name) - cited)

    print("工具↔能力 归属检查 · `all_specs()` = %d 个工具 · 被能力条目认领的 = %d"
          % (len(by_name), len(set(by_name) & cited)))
    print()
    if not uncited:
        print("  ✓ 每个工具都有归属（★ `mcp_tools` 已补齐）")
        return 0

    by_mod: dict = defaultdict(list)
    for n in uncited:
        by_mod[by_name[n].module].append(n)
    print("  ★ **没有归属的工具 %d 个** ⇒ ★ 这就是「该补 `mcp_tools` 或补能力条目」的清单："
          % len(uncited))
    for m in sorted(by_mod, key=lambda x: (-len(by_mod[x]), x)):
        print("    %-24s %2d 个" % (m, len(by_mod[m])))
        for n in by_mod[m]:
            print("        %s" % n)
    print()
    print("  ⚠ 本报告**不判归属对不对**（★ 那要人工判断，见 known-facts 191）；")
    print("    ★ 它只回答「有没有人认领」这个事实问题 ⇒ ★ 假阳性为零。")
    print("  ⚠ 退出码恒为 0（★ 映射补齐前它是**报告器**，不是硬门禁）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

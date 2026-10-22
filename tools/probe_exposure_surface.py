r"""@brief 探针：量清「本仓库 MCP 暴露面」的**两个来源**，判断「缺 339」是否被低估。

## 为什么探（2026-10-01 轮 86，Spec Kit `010`）
`tools/build_union_map.py` 打印「并集 384 操作 / **本仓库缺 339**」。
但它的 `_our_tools()` **只读 `mcp-server/server.py` 的 `@mcp.tool(name=...)` 装饰器形式**，
而 `server.py` 自己的 docstring 就承认：
> `server.py` 只引用 25 个模块，我们后补的 58+ 个一个都没进

⇒ **怀疑**：我们后补的工具注册在 `mcp-server/tool_specs_batch*.py` 里（`name="solidworks_*"`），
**而 `_our_tools()` 完全没读它们** ⇒ **暴露面被低估 ⇒ 缺口被灌水**。
⚠ 实测印证：模具域那 3 个「缺口」里有 2 个**我们明明有**
（`solidworks_mold_parting_line` / `solidworks_mold_shut_off_surface`），
它们就在 `tool_specs_batch1.py` 里。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_exposure_surface.py
# 定位:   为 Spec Kit `010`（缺口数复算）取证。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
ROOT = Path(r"" + _ROOT_S + r"")
sys.stdout.reconfigure(encoding="utf-8")

DECO = re.compile(r"@mcp\.tool\(\s*\n?\s*name\s*=\s*\"([^\"]+)\"")
SPEC_NAME = re.compile(r"name=\"((?:solidworks|cadstudio)_[\w]+)\"")


def main() -> int:
    srv = (ROOT / "mcp-server" / "server.py").read_text(
        encoding="utf-8", errors="ignore"
    )
    deco = sorted(set(DECO.findall(srv)))
    print("① `server.py` 的 `@mcp.tool(name=...)` 装饰器：**%d** 个" % len(deco))

    print()
    batch: dict[str, list] = {}
    for p in sorted((ROOT / "mcp-server").glob("tool_specs_*.py")):
        names = sorted(
            set(SPEC_NAME.findall(p.read_text(encoding="utf-8", errors="ignore")))
        )
        batch[p.name] = names
        print("② %-30s **%3d** 个工具名" % (p.name, len(names)))

    allb = sorted({n for ns in batch.values() for n in ns})
    union = sorted(set(allb) | set(deco))
    print()
    print("③ 注册表合计（去重）：**%d**" % len(allb))
    print("④ 注册表 ∪ 装饰器：**%d**" % len(union))
    print(
        "   ⇒ 交集 %d · **只在注册表里（装饰器没有）的 %d**"
        % (len(set(allb) & set(deco)), len(set(allb) - set(deco)))
    )

    print()
    print("⑤ 复算：模具域那 3 个「缺口」在**合并后的暴露面**里吗？")
    for k in ("parting_line", "shut_off_surface", "tooling_split"):
        hit = [n for n in union if k in n]
        print(
            "   %-18s %s" % (k, ("✅ **有**：%s" % hit[:2]) if hit else "❌ 真的没有")
        )

    print()
    print("⑥ 仿真/Motion 域的 4 个「缺口」呢？")
    for k in ("motion_study", "run_simulation", "simulation_setup", "simulation_study"):
        hit = [n for n in union if k in n]
        print(
            "   %-18s %s" % (k, ("✅ **有**：%s" % hit[:2]) if hit else "❌ 真的没有")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

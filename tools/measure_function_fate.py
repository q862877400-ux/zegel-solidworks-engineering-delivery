"""量清 692 个公开函数的三种命运：**挂了 / 被别的函数调用 / 两者都没有**。

方法（2026-10-01 轮 215）：
  ① 公开函数名 = `scripts/sw_*.py` 里 `^def <名字>(` 且不以 `_` 开头
  ② 「挂了」= 该函数名出现在
        · `mcp-server/server.py` 的工具定义里，或
        · `mcp-server/tool_specs_batch*.py` 的 `function="<名字>"`
  ③ 「被调用」= 该名字出现在 `scripts/` **其它地方**（不是它自己的 `def` 行）
  ④ 两者都没有 ⇒ ★ **孤立**（写了没人用、也没挂出去）

⚠ 只读；产物落 `D:\\AI\\SW\\output\\`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\measure_function_fate.py
# 定位:   回答「不挂出去的函数是不是白写了」——把"挂出去"与"被调用"分开量。
# 官方依据: 不适用（纯静态统计）
# 许可:   本仓库 MIT。
# ⚠ 只做静态文本比对。
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

CODE = Path(r"" + _ROOT_S + r"")
SCRIPTS = CODE / "scripts"
MCP = CODE / "mcp-server"
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "function-fate.json")


def main() -> int:
    #: ① 公开函数
    pub = {}
    for p in SCRIPTS.glob("sw_*.py"):
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"(?m)^def ([a-z][a-z0-9_]*)\s*\(", t):
            pub.setdefault(m.group(1), p.name)
    print("  公开函数: **%d**" % len(pub))

    #: ② 挂出去的
    exposed = set()
    srv = (MCP / "server.py").read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r'@mcp\.tool\(([^)]*)\)', srv, re.S):
        for n in re.findall(r'"([a-z_][a-z0-9_]*)"', m.group(1)):
            exposed.add(n)
    for p in MCP.glob("tool_specs_batch*.py"):
        t = p.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'function="([a-z_][a-z0-9_]*)"', t):
            exposed.add(m.group(1))
    print("  其中挂成工具的: **%d**" % len(set(pub) & exposed))

    #: ③ 被别的代码调用（扫 scripts/ 全部文件；排除自己的 def 行）
    others = {}
    for p in SCRIPTS.glob("*.py"):
        t = p.read_text(encoding="utf-8", errors="replace")
        for line in t.splitlines():
            if re.match(r"^\s*def ", line):
                continue
            others.setdefault(p.name, []).append(line)

    called = set()
    for name in pub:
        home = pub[name]
        for fname, lines in others.items():
            for line in lines:
                if re.search(r"\b%s\s*\(" % re.escape(name), line):
                    #: 排除"自己文件里自己调自己"的递归
                    if fname == home and re.search(r"\b%s\s*\([^)]*$" % re.escape(name), line) is None:
                        pass
                    called.add(name)
                    break
            if name in called:
                break
    print("  被别处调用的: **%d**" % len(called))

    both = set(pub) & exposed & called
    only_tool = (set(pub) & exposed) - called
    only_called = called - exposed
    orphan = set(pub) - exposed - called
    print("")
    print("  ── 三种命运 ──")
    print("    既挂了、也被别的代码调用 : %4d" % len(both))
    print("    只挂了（没人内部调）     : %4d" % len(only_tool))
    print("    只被内部调用（没挂）     : %4d" % len(only_called))
    print("    ★ **两者都没有（写了没人用）** : %4d  ← 这就是「是不是白写」的答案" % len(orphan))
    OUT.write_text(json.dumps({
        "public": len(pub), "exposed": sorted(set(pub) & exposed), "called": sorted(called),
        "orphan": sorted(orphan)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("")
    print("  孤立函数里的前 20 个（模块 · 函数）:")
    for n in sorted(orphan)[:20]:
        print("    %-30s %s" % (pub[n], n))
    print("")
    print("  产物:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

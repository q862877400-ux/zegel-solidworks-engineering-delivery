# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/measure_four_merged.py
# 定位:   （本文件无模块 docstring）
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

import json
import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
PY = re.compile(r"(?m)^\s*(?:async\s+)?def\s+([a-z_]\w*)\s*\(")
TSF = re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_]\w*)\s*\(")
TSA = re.compile(r"(?m)^\s*(?:export\s+)?(?:const|let)\s+([A-Za-z_]\w*)\s*=\s*(?:async\s*)?\(")

SCAN = {
    "Eduardof0nt": (r"C:\swprojects\Eduardof0nt", ["server.py", "sw_client.py"]),
    "andrewbartels1": (r"C:\swprojects\andrewbartels1", ["src"]),
    "vespo92": (r"C:\swprojects\SolidworksMCP-TS", ["src"]),
    "Slacker-LLC": (r"C:\swprojects\Slacker-LLC", ["solidworks_mcp"]),
}
OURS = Path(r"" + _ROOT_S + r"")

raw_all, uniq_all = 0, set()
print("  各家产品代码的函数（Python 的 def + TypeScript 的 function/箭头函数）:")
for name, (root, subs) in SCAN.items():
    r = Path(root)
    files = []
    for s in subs:
        p = r / s
        files += [p] if p.is_file() else [q for q in p.rglob("*")
                                          if q.suffix in (".py", ".ts") and "node_modules" not in str(q)
                                          and ".git" not in str(q) and not q.name.endswith(".d.ts")]
    names = set()
    n = 0
    for f in files:
        t = f.read_text(encoding="utf-8", errors="replace")
        found = PY.findall(t) + TSF.findall(t) + (TSA.findall(t) if f.suffix == ".ts" else [])
        n += len(found)
        names |= set(found)
    raw_all += n
    uniq_all |= names
    print("    %-16s 原始 %5d · 去重 %5d" % (name, n, len(names)))


def funcs_of(subdirs):
    names = set()
    n = 0
    for sub in subdirs:
        for p in (OURS / sub).rglob("*.py"):
            if "__pycache__" in str(p):
                continue
            found = PY.findall(p.read_text(encoding="utf-8", errors="replace"))
            n += len(found)
            names |= set(found)
    return n, names


our_raw, our_uniq = funcs_of(["scripts", "mcp-server"])
sw_raw, sw_uniq = funcs_of(["scripts"])

u = json.loads((OURS / "tools" / "union-sources.json").read_text(encoding="utf-8"))
tools_uniq = len(u.get("union_operations") or [])
tools_raw = sum(len(s.get("tools") or []) for s in u["sources"])

print("")
print("  ══════════ 最终：四家合并 vs 我们 ══════════")
print("  %-34s %12s %12s" % ("指标", "四家合并", "★ 我们"))
for k, a, b in (
    ("函数（原始相加）", raw_all, our_raw),
    ("函数（去重后）", len(uniq_all), len(our_uniq)),
    ("MCP 工具（去重=并集）", tools_uniq, 103),
    ("MCP 工具（原始相加）", tools_raw, 103),
    ("真机跑过的工具", 92, 103),          #: 只有 Slacker-LLC 声明全工具跑过（92 个）
):
    print("  %-34s %12d %12d" % (k, a, b))
print("")
print("  ★ 我们的纯函数层（scripts/sw_*.py）: 原始 %d / 去重 %d" % (sw_raw, len(sw_uniq)))

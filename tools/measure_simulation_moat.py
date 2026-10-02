"""量护城河：① 先查四家有没有**仿真载荷**的判据（用户纪律 §5.0）；② 核能力层现状。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\w7_sim.py
# 定位:   给砌墙 W7（仿真载荷包装层）定范围；★ 也是**护城河说法**的可复跑依据
#          （`capabilities.yaml` 的 `simulation_loads_wiring` 引用了它）。
# ⚠ 只读；★ 四家的克隆在 `C:/swprojects/<owner>/`（只读对照，见 AGENTS.md §4.2）。
# 官方依据: `C:\\swapi\\types\\ICWLoadsAndRestraintsManager` 等（本脚本只列现状）
# 许可:   本仓库 MIT。
# ⚠ 只读。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
import inspect
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(__file__).resolve().parents[1]          #: ★ 仓库根（不写死绝对路径）
sys.path[:0] = [str(REPO / "scripts"), str(REPO / "mcp-server"), str(REPO)]

print("  ══ ① 四家的 live/general 测试里有没有**仿真载荷**的判据（用户纪律：先找）══")
pats = re.compile(r"simulation|study|restraint|fixture|force|pressure|load|mesh|stress|displacement",
                  re.I)
FOUR = Path("C:/swprojects")                        #: ★ 四家的克隆盘（只读对照）
for owner in ("andrewbartels1", "Eduardof0nt", "Slacker-LLC", "SolidworksMCP-TS"):
    d = FOUR / owner
    if not d.is_dir():
        continue
    hits = []
    for f in d.rglob("*"):
        if f.suffix not in (".py", ".ts", ".js") or ".git" in f.parts or "node_modules" in f.parts:
            continue
        if not re.search(r"test", f.name, re.I):
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        if re.search(r"restraint|fixture|apply_force|apply_pressure|create_study|mesh", t, re.I):
            hits.append(f.name)
    print("    %-16s 测试里含仿真关键词的文件: %s" % (owner, hits[:4] if hits else "**（无）**"))

print()
print("  ══ ② 四家的工具名里有没有仿真（名字级）══")
import json
u = json.loads((REPO / "tools" / "union-sources.json").read_text(encoding="utf-8"))
for s in u["sources"]:
    owner = s.get("repo") or s.get("owner") or "?"
    sim = [t for t in (s.get("tools") or []) if pats.search(str(t))]
    print("    %-46s 仿真相关工具: **%d** %s" % (owner, len(sim), sim[:5]))

print()
print("  ══ ③ 能力层现状：`sw_simulation` / `sw_simulation_loads` 里有什么 ══")
for mod_name in ("sw_simulation", "sw_simulation_loads"):
    try:
        m = __import__(mod_name)
    except Exception as exc:                                   # noqa: BLE001
        print("    %s: 导入失败 %s" % (mod_name, str(exc)[:60]))
        continue
    fns = []
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if callable(o) and getattr(o, "__module__", "").endswith(mod_name):
            try:
                sig = inspect.signature(o)
            except Exception:                                  # noqa: BLE001
                continue
            ps = list(sig.parameters)
            fns.append((n, ps[0] if ps else "", str(sig)[:52]))
    print("    ── %s（%d 个函数）──" % (mod_name, len(fns)))
    for n, first, sig in fns:
        mark = "★" if re.search(r"restraint|force|pressure|fixture|load|mesh|study", n, re.I) else " "
        print("      %s %-34s 首参=%-10s %s" % (mark, n, first, sig))

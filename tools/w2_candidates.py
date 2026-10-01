"""W2 候选筛选：工程图族里**已实现、首参可注入、且没挂**的函数。

判据（照 W1 的教训，先问"能不能直接挂"）：
  · 公开（不以 _ 开头）
  · 首参 ∈ {model, sw_app, study} ⇒ 可注入
  · 不在 all_specs() 里
  · ★ 返回值**能过 JSON**（不是 COM 对象列表）—— 逐个看签名与 docstring

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\w2_candidates.py
# 定位:   给砌墙 W2（Spec Kit `132`）筛候选。
# 官方依据: 不适用（纯静态统计）
# 许可:   本仓库 MIT。
# ⚠ 只读。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")
for p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
import register_capabilities as rc

exposed = {x.function for x in rc.all_specs()}
INJECTABLE = ("model", "sw_app", "study")

mods = sorted(p.stem for p in (REPO / "scripts").glob("sw_drawing*.py"))
print("  工程图相关模块: %s" % mods)
print()
have, need = [], []
for mod in mods:
    try:
        m = __import__(mod)
    except Exception as exc:                                   # noqa: BLE001
        print("  （%s 导入失败: %s）" % (mod, str(exc)[:50]))
        continue
    for n in sorted(dir(m)):
        if n.startswith("_"):
            continue
        o = getattr(m, n)
        if not callable(o) or not getattr(o, "__module__", "").endswith(mod):
            continue
        if n in exposed:
            continue
        try:
            sig = inspect.signature(o)
        except Exception:                                      # noqa: BLE001
            continue
        first = list(sig.parameters)[0] if sig.parameters else ""
        (have if first in INJECTABLE else need).append((mod, n, str(sig)))

print("  ══ ★ 首参是注入点（可**直接挂**）的未挂函数：%d 个 ══" % len(have))
for mod, n, s in have:
    print("    %-22s %-34s %s" % (mod, n, s[:66]))
print()
print("  ══ 首参不是注入点的：%d 个（需包装层）══" % len(need))
seen_first = {}
for mod, n, s in need:
    f = s[1:].split(",")[0].split(":")[0].strip("' ")
    seen_first.setdefault(f, []).append("%s.%s" % (mod, n))
for f, lst in sorted(seen_first.items(), key=lambda kv: -len(kv[1])):
    print("    首参=%-14s %2d 个  %s" % (f, len(lst), ", ".join(lst[:4])))

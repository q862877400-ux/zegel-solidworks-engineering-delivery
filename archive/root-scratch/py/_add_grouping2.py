"""★ 一次性（第 2 步）：跑循环改成"每组一次状态 + 写工具后重建"。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

OLD = """    rows = []
    for name in targets:
        model = _fresh_part(sw)
        if model is None:
            rows.append({"tool": name, "verdict": "undecided", "why": "★ 建不了新零件"})
            continue"""

NEW = """    rows = []
    for req in sorted(by_requires):
        group = by_requires[req]
        print("\\n★ ── `requires=%s` 组：%d 个（★ **只建一次状态**，★ 写工具后重建）──" % (req, len(group)))
        model, why_state = build_state(sw, req)
        if model is None and req != "app":
            #: ★ 建不出宿主 ⇒ 整组**如实记未判定**（★ 不许当成通过）✓
            for name in group:
                rows.append({"tool": name, "verdict": "undecided", "requires": req,
                             "why": why_state})
            print("   ★ 整组跳过：%s" % why_state)
            continue
        for name in group:
            #: ★★ **写工具之后要"副本重载"** —— 本仓的做法是**重建宿主状态** ✓
            #:   ★（★ 读工具可以连着调 —— ★ 那正是分组省时间的地方）✓
            decl = table.get(name) or {}
            if decl.get("writes"):
                model, why_state = build_state(sw, req)
                if model is None and req != "app":
                    rows.append({"tool": name, "verdict": "undecided", "requires": req,
                                 "why": "★ 重建状态失败：%s" % why_state})
                    continue"""

assert OLD in s, "跑循环没匹配上"
s = s.replace(OLD, NEW)

#: ★ `before/after` 之后的收尾：把 requires 记进行
s = s.replace('''            "tool": name, "verdict": verdict, "writer_ok": ok,''',
              '''            "tool": name, "verdict": verdict, "writer_ok": ok, "requires": req,''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("跑循环已改成按组 + 写后重建")

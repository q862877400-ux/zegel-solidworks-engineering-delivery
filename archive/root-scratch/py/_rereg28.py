import re, sys
sys.stdout.reconfigure(encoding="utf-8")
from pathlib import Path
P = Path(r"C:\\swprojects\\sw-skill-fork\\mcp-server\\register_capabilities.py")
t = P.read_text(encoding="utf-8")
m = re.search(r"\n    #: ⚠⚠ \*\*轮 240 回退\*\*.*?（见 known-facts 174）。\n", t, re.S)
if m:
    t = t[:m.start()] + "\n" + t[m.end():]
    print("  ✓ 撕掉旧的「撒下」注记")
NOTE = (
    "    #: ⚠⚠⚠ **轮 240：`tool_specs_batch28.py`（网格/求解/读数 4 个）**已注册但**未真机验证**** ——\n"
    "    #:   ★ 真机验证**三次都触发 Simulation 的模态框**「未定义载荷或规定的位移」\n"
    "    #:   （框内原文：「**固定-刚性零件上的载荷将不处于活动状态**」）⇒ **COM 挂起、救不回来**；\n"
    "    #:   加了两道前置门（材料回读非空 + `LoadsAndRestraintsManager.Count >= 2`）**仍然弹**。\n"
    "    #:   ⇒ ★ 按 `AGENTS.md` 硬约束③：**明确标注「未真机验证」**（★ 不谎称验证过），\n"
    "    #:     能力条目等级 = **`stitched`**（不是 `verified`）。\n"
    "    #:   ★ 查清的正路 = **对照实验逐个分离变量**（事实 165 第 12 条）—— 见 known-facts 174。\n"
)
i = t.find("    \"tool_specs_batch27\",\n")
assert i > 0, "锚点不符"
j = i + len("    \"tool_specs_batch27\",\n")
t = t[:j] + NOTE + "    \"tool_specs_batch28\",\n" + t[j:]
P.write_text(t, encoding="utf-8")
import ast; ast.parse(t)
print("  ✓ 已按正解注册 batch28（带未验证标注）")

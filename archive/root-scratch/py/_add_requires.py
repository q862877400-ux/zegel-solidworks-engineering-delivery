"""★ 一次性：机械初推 requires（★ 从 inject 的种类推"这条工具需要什么宿主"）。"""
from pathlib import Path

# ── ① effect_rules：加 requires 的推导规则 ───────────────────────────────
p = Path(r"D:\AI\SW\mcp-server\effect_rules.py")
s = p.read_text(encoding="utf-8")
ADD = '''

#: ★★★ **`requires` 的机械初推规则**（★ 规格 210 · B3 的"分组基数"）。
#:   ★★ 起因（真机读数）：★ `nonempty` 组抽样 20 里，★ 剩余的失败**全部**是
#:     「**声明注入 X 但没给对应对象**」（`asm_model` · `view` · `sldworks`）或环境/取值类 ⇒
#:     ★★ **分组要按"需要什么宿主对象"来分**，★ 而那个信息**声明里已经有了**（`inject`）✓
#:   ★ 判据：★ 直接**从 `inject` 的种类**推 —— ★ 这是**声明里的事实**，★ 不是我猜的 ✓
#:   ★★ 为什么值得机械推：★ 评审说「耗时随**不同前置的数量**增长，不随工具数增长」——
#:     ★ 而 `requires` 的种类数就是那个"不同前置的数量" ✓
INJECT_REQUIRES = {
    "": "none",                       # ★ 不需要宿主对象（★ 如纯静态查询）✓
    "model": "part",
    "doc": "part",
    "asm_model": "assembly",
    "component": "assembly",
    "drawing_model": "drawing",
    "view": "view",
    "sldworks": "app",
    "sw_app": "app",
    "sw": "app",
    "manager": "app",
    "defaults": "app",
    "options": "app",
    "selection": "selection",
    "study": "study",
    "mesh": "study",
    "results": "study",
    "motion_study": "study",
    "cost_manager": "costing",
    "cost_part": "costing",
    "cost_body": "costing",
    "cost_analysis": "costing",
}


def derive_requires(inject: str) -> str:
    """★ 从 `inject` 推**这一条需要什么宿主**（★ 未知的注入名 ⇒ 原样带回并加前缀，★ 不吞）✓"""
    key = str(inject or "").strip()
    if key in INJECT_REQUIRES:
        return INJECT_REQUIRES[key]
    return "host:" + (key or "unknown")
'''
s = s.rstrip() + ADD
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① effect_rules 已加 INJECT_REQUIRES 与 derive_requires")

# ── ② 生成器：把 requires 写进表 ─────────────────────────────────────────
g = Path(r"D:\AI\SW\tools\gen_effect_declarations.py")
gs = g.read_text(encoding="utf-8")
gs = gs.replace("from effect_rules import STATE_CLASSES, classify_members, load_kind_index",
                "from effect_rules import (STATE_CLASSES, classify_members, derive_requires,\n"
                "                          load_kind_index)")
gs = gs.replace("from effect_rules import STATE_CLASSES, classify_members, load_kind_index",
                "from effect_rules import (STATE_CLASSES, classify_members, derive_requires,\n"
                "                          load_kind_index)")
gs = gs.replace("""        tools[s.name] = {
            "writes": verdict["writes"],            # ★ None = 未知（★ 不是"无写"）""",
"""        #: ★★ `requires` —— ★ **机械初推**（★ 从 `inject` 的种类推，★ 见 `effect_rules`）✓
        try:
            import tool_registry as _tr
            _inj = _tr.effective_inject(s)
        except Exception:                                               # noqa: BLE001
            _inj = getattr(s, "inject", "") or ""
        tools[s.name] = {
            "requires": derive_requires(_inj),      # ★ 需要什么宿主（★ 分组就按它）✓
            "inject": _inj,
            "writes": verdict["writes"],            # ★ None = 未知（★ 不是"无写"）""")
g.write_text(gs, encoding="utf-8")
ast.parse(gs)
print("② 生成器已写 requires")

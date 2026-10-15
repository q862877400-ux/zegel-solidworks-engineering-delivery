"""★ 一次性：按 inject 建"对的宿主对象"并**按那个名字传进去**。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

HELPER = '''def build_host(sw, inject_name: str):
    """★★ 按**注入名**建**对的宿主对象** —— ★ 这是分组省时间之后**必须补的那一半** ✓

    ★★★ 2026-10-06 **分组暴露的真问题**：★ 每组需要的**不只是"一个文档"**，★ 而是**那个特定的对象** ——
      ★ `asm_model` 要装配体 · `view` 要视图 · `study` 要研究 · `cost_manager` 要成本管理器 ⇒
      ★★ 而我第一版 `build_state` **只会建文档、且一律当 `model` 传** ⇒
      ★ 于是除 `part`/`none` 外的组**根本没跑到**（★ 真机：`empty` 47 条里 33 条"调用没调成"）✗
    ★★ 另外一处更细的认识：★ 分组的键应当是 **`inject`（精确的注入名）**，
      ★ 不是 `requires`（**种类**）—— ★ `requires` 只用来做**基数统计**（9 种）✓

    :returns: `(inject_objects, why)` —— ★ `why` 非空表示**这一组还没法建**（★ 如实记，不假装）✓
    ★⚠ 限度：★ `view` / `study` / `cost_manager` / `selection` **这四类还没建**
      （★ 要构造视图/研究/成本管理器/选中对象）⇒ ★ 那些组会**如实记 `undecided`** ✓
    """
    import sw_connect
    name = str(inject_name or "")
    if name in ("", "none"):
        return {"sw": sw}, ""
    #: ★ 应用对象类（`sldworks` / `sw_app` / `sw` / `manager` / `defaults` / `options`）⇒ 给 `sw` ✓
    if name in ("sldworks", "sw_app", "sw", "manager", "defaults", "options", "sw_app"):
        return {name: sw, "sw": sw}, ""
    kind = {"model": "part", "doc": "part", "asm_model": "assembly",
            "component": "assembly", "drawing_model": "drawing"}.get(name)
    if kind:
        try:
            return {name: sw_connect.new_document(sw, kind), "sw": sw}, ""
        except Exception as exc:                                        # noqa: BLE001
            return {}, "★ 建 %s 失败：%s" % (kind, type(exc).__name__)
    #: ★ 其余四类（view / study / cost_manager / selection）**还没建** ⇒ ★ 如实报出 ✓
    return {}, "★ 这一类宿主**还没建**（`%s`）—— ★ 需要构造视图/研究/成本管理器/选中对象" % name


'''
anchor = "def build_state(sw, requires: str):"
assert anchor in s, "build_state 锚点没找到"
s = s.replace(anchor, HELPER + anchor, 1)

# ── 跑循环：按 inject 分组并传对的宿主 ───────────────────────────────────
s = s.replace('''    def _requires_of(tool_name: str) -> str:
        return str((table.get(tool_name) or {}).get("requires") or "unknown")''',
'''    def _requires_of(tool_name: str) -> str:
        #: ★★ 分组用 **`inject`（精确注入名）**；★ `requires`（种类）只用于统计基数 ✓
        return str((table.get(tool_name) or {}).get("inject") or "none")''')

s = s.replace('''        model, why_state = build_state(sw, req)
        if model is None and req != "app":
            #: ★ 建不出宿主 ⇒ 整组**如实记未判定**（★ 不许当成通过）✓
            for _n in group:
                rows.append({"tool": _n, "verdict": "undecided", "requires": req,
                             "writer_ok": True, "why": why_state})
            print("   ★ 整组跳过：%s" % why_state)
            continue''',
'''        injects, why_state = build_host(sw, req)
        if why_state:
            #: ★ 建不出宿主 ⇒ 整组**如实记未判定**（★ 不许当成通过）✓
            for _n in group:
                rows.append({"tool": _n, "verdict": "undecided", "requires": req,
                             "writer_ok": True, "why": why_state})
            print("   ★ 整组跳过：%s" % why_state)
            continue''')

s = s.replace('''            if decl.get("writes"):
                model, why_state = build_state(sw, req)
                if model is None and req != "app":
                    rows.append({"tool": name, "verdict": "undecided", "requires": req,
                                 "writer_ok": True, "why": "★ 重建状态失败：%s" % why_state})
                    continue''',
'''            if decl.get("writes"):
                injects, why_state = build_host(sw, req)
                if why_state:
                    rows.append({"tool": name, "verdict": "undecided", "requires": req,
                                 "writer_ok": True, "why": "★ 重建状态失败：%s" % why_state})
                    continue''')

s = s.replace('''            before = FP.read(model, sw)''',
              '''            before = FP.read(injects.get(req) or injects.get("sw"), sw)''')
s = s.replace('''            ok, note = tool_caller.call(
                name, inject_objects={"model": model, "sw": sw},''',
              '''            ok, note = tool_caller.call(
                name, inject_objects=dict(injects),''')
s = s.replace('''            after = FP.read(model, sw)''',
              '''            after = FP.read(injects.get(req) or injects.get("sw"), sw)''')

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("已按 inject 建宿主并按那个名字传")

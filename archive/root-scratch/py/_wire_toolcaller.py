"""★ 一次性：探针的写操作改成**按 ToolSpec 契约**调（替掉手调能力层函数）。"""
from pathlib import Path

pr = Path(r"D:\AI\SW\tools\probe_fingerprint_sensitivity.py")
s = pr.read_text(encoding="utf-8")

# ── ① 写操作表：改成**工具名** ────────────────────────────────────────────
OLD_MAP = s[s.index("KNOWN_WRITERS = {"):s.index("def _connect():")]
NEW_MAP = '''#: ★★ 每一类配一个**已知会改它**的写操作 —— ★ 值是 **MCP 工具名**（★ 按 `ToolSpec` 契约调）✓
#:   ★ 我第一版是**手调能力层函数**（`sw_part.xxx`）⇒ ★ 形状不对、抛 `TypeError` ✗
#:   ★★ 本仓纪律原话：「写探针验能力时：**按 `ToolSpec` 的契约调**，别手调内部实现」✓
#:   ★ 空串 = 本轮**没给这一类配写操作** ⇒ ★ 记 `untested`（★ **不许**说成「看不见」）✓
KNOWN_WRITERS = {
    "selection": "solidworks_clear_selection",
    "edit_mode": "solidworks_sketch_start",
    "dirty": "solidworks_sketch_start",
    "features": "solidworks_extrude_boss",
    "bodies": "solidworks_extrude_boss",
    "faces": "solidworks_extrude_boss",
    "display": "",              # ★ 没有"改显示状态"的现成工具 ⇒ 记 untested
    "config": "solidworks_config_create",
    "rebuild": "solidworks_session_rebuild",
}

#: ★ 每个写操作要传的形参（★ 名字与声明一致；★ 没给的用声明里的默认值）✓
WRITER_PARAMS = {
    "solidworks_clear_selection": {},
    "solidworks_sketch_start": {},
    "solidworks_extrude_boss": {},
    "solidworks_config_create": {"name": "标定用配置"},
    "solidworks_session_rebuild": {},
}


'''
s = s.replace(OLD_MAP, NEW_MAP)

# ── ② act()：改成走 tool_caller ──────────────────────────────────────────
start = s.index("def act(sw, model, name):")
end = s.index("def main() -> int:")
new_act = '''def act(sw, model, name):
    """★ 执行一个「已知会改状态」的写操作 —— ★ **按 `ToolSpec` 契约调工具** ✓

    ★ 契约（读 `tool_registry.make_tool_function` 得知）：★ 底层函数按 **kwargs** 调，
      形参名与声明一致，★ 注入对象用 **`inject` 声明的那个名字**传进去 ✓
    ★★ **拿不到 / 缺参数 / 抛异常 ⇒ 回 `(False, 原因)`** —— ★ 调用方据此记 `untested`，
      ★ **绝不许**把"没调成"说成"这一类不可见" ✗
    """
    import tool_caller
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects={"model": model, "sw": sw}, **params)


'''
s = s[:start] + new_act + s[end:]

# ── ③ 调用点：act 现在回 (ok, msg) ───────────────────────────────────────
OLD_CALL = """        before = FP.read(model, sw)
        try:
            ok = act(sw, model, writer)
        except Exception as exc:                                        # noqa: BLE001
            report["classes"][cls] = {"verdict": "untested",
                                      "why": "★ 写操作抛异常：%s" % type(exc).__name__}
            print("   %-10s ⇒ ★ untested（写操作抛 %s）" % (cls, type(exc).__name__))
            continue"""
NEW_CALL = """        before = FP.read(model, sw)
        ok, note = act(sw, model, writer)
        if not ok:
            #: ★★ **没调成 ⇒ 记 `untested`**（★ 不许说成"不可见"）✓
            report["classes"][cls] = {"verdict": "untested", "writer": writer, "why": note}
            print("   %-10s ⇒ ★ untested（写操作没调成：%s）" % (cls, note[:70]))
            continue"""
assert OLD_CALL in s
s = s.replace(OLD_CALL, NEW_CALL)
s = s.replace('''        report["classes"][cls] = {"verdict": verdict, "writer": writer, "writer_ok": ok,''',
              '''        report["classes"][cls] = {"verdict": verdict, "writer": writer, "writer_ok": ok,
                                  "writer_note": note[:120],''')

pr.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("探针已改成按契约调工具")

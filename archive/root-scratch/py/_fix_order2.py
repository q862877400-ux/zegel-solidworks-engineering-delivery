"""★ 一次性：把前置挪到 before 读数**之前**；并把 display 记成**明确限定**。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\probe_fingerprint_sensitivity.py")
s = p.read_text(encoding="utf-8")

OLD_ACT = '''    import tool_caller
    inj = {"model": model, "sw": sw}
    #: ★★ 先跑**前置链**（★ 让写操作"从一个变得了的状态出发"）✓
    for step_name, step_params in (WRITER_PRECONDITION.get(cls) or []):
        ok_step, note_step = tool_caller.call(step_name, inject_objects=inj, **step_params)
        if not ok_step:
            return False, "★ 前置 %s 没成：%s" % (step_name, note_step[:90])
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects=inj, **params)'''

NEW_ACT = '''    import tool_caller
    inj = {"model": model, "sw": sw}
    params = dict(WRITER_PARAMS.get(name) or {})
    return tool_caller.call(name, inject_objects=inj, **params)


def run_precondition(sw, model, cls):
    """★★ 跑**前置链** —— ★★ 必须在 **`before` 读数之前**跑（★ 真机踩过）✓

    ★★★ 2026-10-06 **真机查明的顺序错**：★ 前置原来写在 `act()` 里 ⇒
      ★ 而 `before = FP.read(...)` 在 `act()` **之前** ⇒ ★★ 于是 before 是在
      **还没建前置状态**的新零件上取的 ✗
      ★ 现场：`selection` 的前置会**选中一个实体**（工具回 `count: 1`、直接回读也是 `1` ✓）⇒
      ★ 可 before 取在选中**之前** ⇒ ★★ 读出 `0 ⇒ 0` ⇒ **被误判成「这一类不可见」** ✗✗
      ⇒ ★ 正解：★ **先跑前置 → 再取 before → 再跑写操作 → 再取 after** ✓
    """
    import tool_caller
    inj = {"model": model, "sw": sw}
    for step_name, step_params in (WRITER_PRECONDITION.get(cls) or []):
        ok_step, note_step = tool_caller.call(step_name, inject_objects=inj, **step_params)
        if not ok_step:
            return False, "★ 前置 %s 没成：%s" % (step_name, note_step[:90])
    return True, ""'''
assert OLD_ACT in s, "act() 没匹配上"
s = s.replace(OLD_ACT, NEW_ACT)

OLD_LOOP = """        model = fresh
        before = FP.read(model, sw)
        ok, note = act(sw, model, writer, cls)"""
NEW_LOOP = """        model = fresh
        #: ★★ **顺序**（★ 真机踩过）：★ 前置 ⇒ before ⇒ 写操作 ⇒ after ✓
        pre_ok, pre_note = run_precondition(sw, model, cls)
        if not pre_ok:
            report["classes"][cls] = {"verdict": "untested", "writer": writer, "why": pre_note}
            print("   %-10s ⇒ ★ untested（前置没成：%s）" % (cls, pre_note[:60]))
            continue
        before = FP.read(model, sw)
        ok, note = act(sw, model, writer, cls)"""
assert OLD_LOOP in s, "标定循环没匹配上"
s = s.replace(OLD_LOOP, NEW_LOOP)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① act 拆成 前置/写操作 ② 前置搬到 before 之前")

fp = Path(r"D:\AI\SW\scripts\sw_fingerprint.py")
fs = fp.read_text(encoding="utf-8")
OLD_D = """        setting, why2 = _read("GetDisplayStateSetting", ext, SW_ALL_DISPLAY_STATE)
        if setting is None:
            put("display", None, why2 or "★ GetDisplayStateSetting(2) 返回 None")"""
NEW_D = """        setting, why2 = _read("GetDisplayStateSetting", ext, SW_ALL_DISPLAY_STATE)
        if setting is None:
            #: ★★★ 真机查明（★ 这**不是**"读不到"，是一条**可记录的限定**）：
            #:   ★ `GetDisplayStateSetting(1|2|3)` **三种 Option 全部**抛
            #:     `com_error (-2147417851, '服务器出现意外情况')` ⇒
            #:   ★★ 与**事实 47**（`AccessSelections`）**同一个错误族**（服务端故障 / RPC）
            #:     ⇒ ★ 该成员在**本后端**上**不可用** ✓
            #:   ⇒ ★ 于是 `display` 这一类**当前无法作为差分依据** ⇒
            #:     ★★ 按验收判据的第二种出口**明写出来**（★ 不是"没试"，也不是"看不见"）✓
            put("display", None, "★★ 读数不可用（★ 本后端限定）：`GetDisplayStateSetting` 三种 Option "
                                 "全部抛 `com_error -2147417851`（服务端故障，★ 与事实 47 同族）")"""
assert OLD_D in fs, "display 块没匹配上"
fs = fs.replace(OLD_D, NEW_D)
fp.write_text(fs, encoding="utf-8")
ast.parse(fs)
print("③ display 记成明确限定")

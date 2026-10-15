"""★ 一次性：把 B4 的预检接进注册层的调用路径（★ 带开关，可回退）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\mcp-server\tool_registry.py")
s = p.read_text(encoding="utf-8")

HOOK = '''#: ★★ B4 的预检开关（★ 规格 210）—— ★ **默认开**；★ `SW_PRECHECK=off` 可关（★ 于是**可回退**）✓
PRECHECK_ENABLED = str(os.environ.get("SW_PRECHECK", "on")).strip().lower() not in ("off", "0", "false")


def precheck_payload(spec: "ToolSpec", inject_name: str, host) -> Optional[str]:
    """★★ **按声明自动生成的预检** —— ★ 返回 `None` 表示**放行**；★ 否则返回**要直接回的 JSON 串** ✓

    ★★ 这是 B4 的落点（★ 评审的四条之一）：★「工具层返回**结构化**的『不适用』，
      ★ **不要抛字符串异常**」⇒ ★★ 于是**不适用时工具回的是 JSON 载荷**，★ 不是异常 ✓
    ★★ 三条保守判据：
      ① ★ **预检自己出错 ⇒ 放行** —— ★ 预检是**保护**，★ 不该变成新的**路障** ✓
         （★ 这条与本会话两次"过度纠正"的教训**同族**：★ 保守 ≠ 一律拒绝）✓
      ② ★ **没建的检查（`unchecked`）⇒ 放行**（★ 它如实说"没查"，★ 不许因此挡住工具）✓
      ③ ★ 开关关掉 ⇒ 一律放行 ✓
    """
    if not PRECHECK_ENABLED or not inject_name:
        return None
    try:
        try:
            import scripts.sw_applicability as ap
        except ImportError:
            import sw_applicability as ap                                  # noqa: PLC0415
        ap.precheck(inject_name, host, tool_name=spec.name)
        return None
    except Exception as exc:                                            # noqa: BLE001
        #: ★ 认得出是"不适用" ⇒ 回**结构化载荷**（★ 这是唯一的"拒绝"路径）✓
        name = type(exc).__name__
        if name == "NotApplicable" and hasattr(exc, "to_dict"):
            import json as _json
            return _json.dumps(exc.to_dict(), ensure_ascii=False)
        #: ★ 其余异常（含"没建的检查"）⇒ **放行** —— ★ 保护不许变成路障 ✓
        return None


'''
anchor = "def make_tool_function("
assert anchor in s, "make_tool_function 锚点没找到"
s = s.replace(anchor, HOOK + anchor, 1)

OLD = """                kwargs[inject_as or inj] = resolver(params)"""
NEW = """                kwargs[inject_as or inj] = resolver(params)
                #: ★★ **B4：按声明自动生成的预检** ⇒ ★ 不适用就回**结构化载荷**，★ 不调目标函数 ✓
                #:   ★（★ 只在 `inject` 非空时做 —— ★ 没有宿主对象就没有"不适用"可言）✓
                _blocked = precheck_payload(spec, inj, kwargs.get(inject_as or inj))
                if _blocked is not None:
                    return _blocked"""
assert OLD in s, "注入点没匹配上"
s = s.replace(OLD, NEW, 1)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("预检已接进注册层（★ 带 SW_PRECHECK 开关）")

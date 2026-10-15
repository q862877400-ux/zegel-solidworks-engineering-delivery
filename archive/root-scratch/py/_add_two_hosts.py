"""★ 一次性：build_host 补 selection 与 view 两类（★ 官方属性，易取）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

OLD = """    #: ★ 其余四类（view / study / cost_manager / selection）**还没建** ⇒ ★ 如实报出 ✓
    return {}, "★ 这一类宿主**还没建**（`%s`）—— ★ 需要构造视图/研究/成本管理器/选中对象" % name"""
NEW = """    #: ★★ 补两类**易取**的（★ 官方属性，★ 已读页面）✓
    #:   · `selection` ⇒ `IModelDoc2.SelectionManager`（★ 官方："makes the currently selected
    #:     object available"）✓
    #:   · `view` ⇒ `IModelDoc2.ActiveView`（★ 官方："Gets the current active model view
    #:     in read-only mode"）✓
    #:   ★ 这两类合起来覆盖 **32 个工具**（`selection` 9 + `view` 23）✓
    if name in ("selection", "view"):
        try:
            import sw_connect as _sc
            doc = _sc.new_document(sw, "part")
            attr = {"selection": "SelectionManager", "view": "ActiveView"}[name]
            host = _sc.get_com_member(doc, attr)
            if host is None:
                return {}, "★ 零件建好了，但 `%s` 取不到（★ 返回 None）" % attr
            return {name: host, "sw": sw}, ""
        except Exception as exc:                                        # noqa: BLE001
            return {}, "★ 建 `%s` 宿主失败：%s" % (name, type(exc).__name__)
    #: ★ 剩下两类（study / cost_manager）**还没建** ⇒ ★ 如实报出 ✓
    return {}, ("★ 这一类宿主**还没建**（`%s`）—— ★ 需要构造仿真研究 / 成本管理器"
                "（★ 要加载对应插件）" % name)"""
assert OLD in s, "build_host 的尾块没匹配上"
s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("build_host 已补 selection 与 view")

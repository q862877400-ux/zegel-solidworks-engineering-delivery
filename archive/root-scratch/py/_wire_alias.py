"""★ 一次性：让 tool_caller 按契约应用 param_alias 与 derived_args。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\tool_caller.py")
s = p.read_text(encoding="utf-8")

OLD = """        kwargs = {}
        for p in (spec.params or []):
            if p.name in params:
                kwargs[p.name] = params[p.name]
            #: ★★ 声明的 `default` 可能是 **`Ellipsis`**（★ 那在本仓约定里表示**必填**，
            #:   ★ 真机实测：`extrude_boss` 的 `sketch_name`/`depth_mm` 就是 `Ellipsis`）⇒
            #:   ★ 把它当**值**传下去是错的 ⇒ ★ **视为未给**，★ 让底层自己的默认值生效，
            #:     ★ 或由底层报"缺参数"（★ 那也算一次**没调成**，记 `untested`）✓
            elif getattr(p, "default", None) is not None and getattr(p, "default", None) is not Ellipsis:
                kwargs[p.name] = p.default
            elif getattr(p, "required", False):
                return False, "★ 缺必需形参：%s" % p.name"""

NEW = """        #: ★★★ 契约里有**两层映射**，`make_tool_function` 的注释写得很清楚
        #:   （★ 我第一版**没实现这两层**，所以调用形状不对 —— ★ 那是我的缺陷，不是声明的）✓
        #:   ① `param_alias`：**对外参数名 → 目标函数形参名**；★ 值为 `None` ⇒
        #:      **该参数由解析器消费、不传给目标函数** ✓
        #:   ② `derived_args`：`lambda params: {...}` —— ★ **从已声明的标量入参派生额外实参**，
        #:      返回的字典**并进**调用关键字实参里 ✓（★ 单位换算也在这里做）
        vals = {}
        for pp in (spec.params or ()):
            if pp.name in params:
                vals[pp.name] = params[pp.name]
            elif getattr(pp, "default", None) is not None and getattr(pp, "default", None) is not Ellipsis:
                vals[pp.name] = pp.default
        #: ★ 先按声明检查"必填且没给"（★ `Ellipsis` 是本仓约定的"必填"）✓
        for pp in (spec.params or ()):
            if getattr(pp, "default", None) is Ellipsis and pp.name not in vals:
                return False, "★ 缺必填形参：%s" % pp.name
        alias = getattr(spec, "param_alias", None) or {}
        kwargs = {}
        for name, value in vals.items():
            target = alias.get(name, name)
            if target is None:
                continue                       # ★ 解析器消费掉，不传给目标函数 ✓
            kwargs[target] = value
        derived = getattr(spec, "derived_args", None)
        if callable(derived):
            import types as _types
            try:
                extra = derived(_types.SimpleNamespace(**vals)) or {}
                kwargs.update(extra)
            except Exception as exc:                                    # noqa: BLE001
                return False, "★ derived_args 抛 %s: %s" % (type(exc).__name__, str(exc)[:80])"""
assert OLD in s, "参数构造块没匹配上"
s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("tool_caller 已实现 param_alias 与 derived_args")

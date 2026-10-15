"""★ 一次性：合成器改成按**真函数签名**的类型提示（★ 声明里没有 annotation）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

OLD = s[s.index("def synth_args(spec) -> dict:"):s.index("\n\ndef classify(declared_writes")]
NEW = '''def synth_args(spec) -> dict:
    """★ 按**真函数签名**给每条必填形参**合成一个值**（★ 形状对即可）✓

    ★★★ 2026-10-06 **真机拆解逼出来的两处修正**（★ 见 `docs/spec210-b3-undecided-breakdown.md`）：
      ① ★★ **声明里没有类型信息**：★ `ToolSpec.params` 的 `annotation` 全是 `None` ✗
         ⇒ ★ 类型只能从**底层真函数的签名**取（★ 用 `inspect.signature`）✓
      ② ★★ **只按名字后缀猜类型会猜错**：★ 真机实录 ——
         · `automation_get_flag(pref)` ⇒ ★ 我给了 `'MCP_CALIB'`（字符串）⇒
           ★★ 真函数要 **`int`** ⇒ 报 `invalid literal for int(): 'MCP_CALIB'` ✗
         · `config_set_custom_properties(properties)` ⇒ ★ 我给了字符串 ⇒
           ★★ 真函数要 **`dict`** ⇒ 报 `'str' object has no attribute 'items'` ✗
    ⇒ ★ 判序：★ **① 真函数签名的类型注解 → ② 名字后缀启发式 → ③ 兜底字符串** ✓
      ★（★ 把类型放**第一位**，★ 因为它是**真的**；★ 名字后缀是**猜的**）✓
    """
    import inspect
    import importlib
    ann: dict = {}
    try:
        mod = importlib.import_module("scripts." + str(getattr(spec, "module", "")))
        fn = getattr(mod, str(getattr(spec, "function", "")), None)
        if fn is not None:
            for pname, pp in inspect.signature(fn).parameters.items():
                ann[pname] = pp.annotation
    except Exception:                                                   # noqa: BLE001
        ann = {}

    out = {}
    for pp in (getattr(spec, "params", None) or ()):
        if getattr(pp, "default", None) is not Ellipsis:
            continue                        # ★ 有默认值的不必合成 ✓
        #: ★ ① 先按**真签名里的类型注解**（★ 最硬）✓
        a = ann.get(pp.name)
        if a is not None:
            t = str(a).lower()
            base = t.replace("typing.", "").split("[")[0]
            if base in ("int",):
                out[pp.name] = 1
                continue
            if base in ("float",):
                out[pp.name] = 1.0
                continue
            if base in ("bool",):
                out[pp.name] = True
                continue
            if base in ("dict", "mapping", "mutabledmapping"):
                #: ★ dict 给**非空**的（★ 真空 dict 多半没用）✓
                out[pp.name] = {"MCP_CALIB": "1"}
                continue
            if base in ("list", "sequence", "tuple", "iterable"):
                out[pp.name] = ["MCP_CALIB"]
                continue
            if base in ("str",):
                pass                        # ★ 落到 ② 让名字后缀再细化（如 path）✓
        #: ★ ② 再按名字后缀（★ 猜的，★ 所以排在类型后面）✓
        low = pp.name.lower()
        value = None
        for hint, v in _SYNTH_BY_HINT:
            if hint in low:
                value = v
                break
        if value is None:
            value = "MCP_CALIB"
        out[pp.name] = value
    return out'''

s = s.replace(OLD, NEW)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("合成器已改成按真函数签名的类型注解")

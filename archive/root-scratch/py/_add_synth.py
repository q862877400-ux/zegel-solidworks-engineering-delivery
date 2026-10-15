"""★ 一次性：给驱动器加"按声明合成实参"（★ 评审说的「参数由声明合成」）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

SYNTH = '''#: ★★★ 2026-10-06 **真机读数纠正了我自己的结论**：★ 我上一轮说"写工具缺前置" ✗ ——
#:   ★★ 17 条失败里 **12 条**其实是「**缺必填形参**」（`x_mm`/`configuration_name`/`view_name`/…），
#:   ★ 另有 **4 条**是「声明注入 `asm_model`/`sldworks`/`view` 但没给对象」· **2 条**是环境/取值错 ✓
#:   ⇒ ★ 正解是评审早说过的「**参数由声明合成**」—— ★ 不是每样都要"建前置" ✓
#:   ★★ 合成规则**按形参名与单位后缀**来（★ 只求"形状对"，★ 不求语义对 —— 语义由差分去判）✓
_SYNTH_BY_HINT = (
    ("_mm", 20.0), ("_deg", 90.0), ("_count", 1), ("_index", 0),
    ("_name", "MCP_CALIB"), ("path", "MCP_CALIB_out.step"),
    ("_type", 0), ("_flag", True), ("_id", 0), ("_size", 1.0),
)


def synth_args(spec) -> dict:
    """★ 按**声明**给每条必填形参**合成一个值**（★ 形状对即可）✓

    ★★ 为什么值得做：★ 真机读数证明，**12/17** 的失败只是"没给参数" ⇒
      ★ 不合成的话，我们**永远测不到**这些工具（★ 而它们会被记成 `undecided`）✓
    ★ 优先级：★ 先看名字后缀（`_mm` / `_deg` / `_name` / `path` …），
      ★ 都命不中就看类型提示，★ 再命不中给一个**保守的字符串** ✓
    ★⚠ 限度：★ 合成的值**只保证类型/形状对** —— ★ **不保证语义对**；
      ★ 所以调用**仍可能失败**，★ 那会如实记 `undecided`（★ 不许当成"通过"）✓
    """
    out = {}
    for pp in (getattr(spec, "params", None) or ()):
        if getattr(pp, "default", None) is not Ellipsis:
            continue                        # ★ 有默认值的不必合成 ✓
        low = pp.name.lower()
        value = None
        for hint, v in _SYNTH_BY_HINT:
            if hint in low:
                value = v
                break
        if value is None:
            kind = str(getattr(pp, "kind", "") or "").lower()
            if "int" in kind:
                value = 0
            elif "float" in kind or "double" in kind:
                value = 1.0
            elif "bool" in kind:
                value = True
            else:
                value = "MCP_CALIB"
        out[pp.name] = value
    return out


'''
anchor = "def classify(declared_writes"
assert anchor in s, "classify 锚点没找到"
s = s.replace(anchor, SYNTH + anchor, 1)

#: ★ 调用点：合成实参 + 只给**本工具声明**的那些（★ 别把别的工具的参数塞进去）
OLD_CALL = """        before = FP.read(model, sw)
        ok, note = tool_caller.call(name, inject_objects={"model": model, "sw": sw})"""
NEW_CALL = """        before = FP.read(model, sw)
        #: ★★ 按声明**合成实参**（★ 真机证明 12/17 的失败只是"没给参数"）✓
        spec_entry = tool_caller._specs().get(name)
        extra = synth_args(spec_entry[0]) if spec_entry else {}
        ok, note = tool_caller.call(name, inject_objects={"model": model, "sw": sw},
                                    **{k: v for k, v in extra.items()
                                       if k not in ("model", "sw", "asm_model", "view",
                                                    "sldworks", "doc", "study")})"""
assert OLD_CALL in s, "调用点没匹配上"
s = s.replace(OLD_CALL, NEW_CALL)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("驱动器已能按声明合成实参")

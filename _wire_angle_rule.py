import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")
t = P.read_text(encoding="utf-8")

# ① 角度词表 + 豁免（接在长度表之后）
OLD = '''_LEN_SUFFIX_EXEMPT: dict = {'''
NEW = '''#: 规则 2 的**角度词汇**。⚠ 刻意**不含** `rad` —— 它会**子串命中 `radius`**
#: （本轮实测：`bend_radius_mm` / `use_default_radius` 一共 **7 处**假阳性就是这么来的）。
_ANGLE_WORDS = ("angle", "degrees", "draft")

#: ⚑⚑ **规则 2 的角度那一半的显式豁免**（判据同长度表：值是**交给 SolidWorks 的
#: 文档默认量**，不是我们换算出的度）。
_ANGLE_SUFFIX_EXEMPT: dict = {
    ("solidworks_mold_parting_surface", "angle"):
        "官方参数 `Angle`；本工具的文档写明「**0.0 = 用文档默认**」⇒ "
        "是**交给 SolidWorks 的文档默认量** ⇒ 加 `_deg` 反而**说错话**。",
}

_LEN_SUFFIX_EXEMPT: dict = {'''
if "_ANGLE_WORDS" not in t:
    assert OLD in t, "锚点不符"
    t = t.replace(OLD, NEW, 1)
    print("  ok 已加角度词表与豁免")
else:
    print("  角度表已有")

# ② 判据本体：接在长度那条之后
OLD_CHECK = '''                    "要么改名（`%s%s`），要么在 `_LEN_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是毫米**"
                    % (spec.name, p.name, _LEN_SUFFIX, p.name, _LEN_SUFFIX)
                )'''
NEW_CHECK = OLD_CHECK + '''
        # ⚑⚑ 规则 2 的**角度那一半**（2026-10-01 轮 135 接上；同 `_LEN_SUFFIX` 一样，
        #    它此前也是**死常量** —— `probe_dead_guards.py` 扫出来的）。
        if p.kind is not bool and any(w in low for w in _ANGLE_WORDS) \\
                and not low.endswith(_ANGLE_SUFFIX):
            if (spec.name, p.name) not in _ANGLE_SUFFIX_EXEMPT:
                raise GateError(
                    "规则 2 违反：工具 %r 的入参 %r 像是**角度**，却不以 %r 结尾 —— "
                    "要么改名（`%s%s`），要么在 `_ANGLE_SUFFIX_EXEMPT` 里"
                    "**写明为什么它不是度**"
                    % (spec.name, p.name, _ANGLE_SUFFIX, p.name, _ANGLE_SUFFIX)
                )'''
if "角度那一半**（2026-10-01 轮 135" not in t:
    assert OLD_CHECK in t, "判据锚点不符"
    t = t.replace(OLD_CHECK, NEW_CHECK, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已接上规则 2 的角度那一半")
else:
    print("  判据已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

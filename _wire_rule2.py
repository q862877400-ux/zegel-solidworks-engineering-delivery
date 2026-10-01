import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")
t = P.read_text(encoding="utf-8")

# ① 常量与豁免表（放在 _BARE_COORD_NAMES 之后）
OLD_CONST = '_BARE_COORD_NAMES = {"x", "y", "z", "x_mm", "y_mm", "z_mm", "point", "coordinate"}'
NEW_CONST = OLD_CONST + '''

#: 规则 2 的**长度词汇**：参数名里出现这些词 ⇒ 认为是长度参数，必须以 `_mm` 结尾。
#: ⚠ 这是**有界词表**，刻意保守（只收"几乎必然是长度"的词）。
#: ⚠⚠ **不包含** `size` / `w` / `h` —— 它们在非几何语境里同样常用
#: （`lot_size` 是批量、`h` 可能是句柄）⇒ 收进来只会制造假阳性
#: （见已知事实 74：按名字判语义的检查在本项目的失败记录）。
_LEN_WORDS = (
    "radius", "diameter", "depth", "thickness", "distance",
    "width", "height", "length", "offset", "spacing", "pitch",
)

#: ⚑⚑ **规则 2 的显式豁免**：这些参数的**单位不是毫米**，`_mm` 后缀会**说错话**。
#: 判据：该参数的值是**直接交给 SolidWorks 的"文档默认单位"**，而不是我们换算过的毫米。
#: ⚠ 照 `check_interface_member_ownership.MANUAL_MAP` 的先例：
#: **每条都要写清"为什么它不属于这一条"**，没依据的不许进来。
_LEN_SUFFIX_EXEMPT: dict[tuple[str, str], str] = {
    ("solidworks_mold_core_cavity_split", "thickness"):
        "官方参数 `Thickness`；本工具的文档写明「**0.0 = 用文档默认**」⇒ "
        "它是**交给 SolidWorks 的文档默认量**，不是我们换算出的毫米 ⇒ 加 `_mm` 反而**说错话**。",
    ("solidworks_mold_core_cavity_split", "offset"):
        "同 `thickness`：官方 `Offset`，文档写明「**0.0 = 用文档默认**」。",
    ("solidworks_mold_parting_surface", "distance"):
        "同 `thickness`：官方 `Distance`，文档写明「**0.0 = 用文档默认**」。",
}'''

if "_LEN_SUFFIX_EXEMPT" not in t:
    assert OLD_CONST in t, "常量锚点不符"
    t = t.replace(OLD_CONST, NEW_CONST, 1)
    print("  ok 已加 _LEN_WORDS / _LEN_SUFFIX_EXEMPT")
else:
    print("  常量已有")

# ② 判据本体：接在裸坐标那条之后
OLD_CHECK = '''            if p.name in ("response_format",):
                raise GateError(
                    "工具 %r 不要自己声明 response_format —— 注册器会自动加" % spec.name
                )'''
NEW_CHECK = OLD_CHECK + '''
            # ⚑⚑ 规则 2 的**长度那一半**（2026-10-01 轮 134 接上）。
            #    ⚠⚠ **接上之前，这一半从未生效** —— `_LEN_SUFFIX` 是个**死常量**
            #    （只在定义处出现一次）。⇒ 规则 2 一直被算进「五统一门禁通过」，
            #    但它的长度那一半**从来没拦过任何东西**（已知事实 40：存在但没人用的守卫）。
            #    证据：`tests/test_rule2_length_suffix_is_enforced.py` 的负例。
            low = p.name.lower()
            #: ⚠ `bool` **不是长度**（`use_default_radius` / `reverse_thickness` 是**标志**）
            if p.kind is not bool and any(w in low for w in _LEN_WORDS) \\
                    and not low.endswith(_LEN_SUFFIX):
                if (spec.name, p.name) not in _LEN_SUFFIX_EXEMPT:
                    raise GateError(
                        "规则 2 违反：工具 %r 的入参 %r 像是**长度**，却不以 %r 结尾 —— "
                        "要么改名（`%s%s`），要么在 `_LEN_SUFFIX_EXEMPT` 里**写明为什么它不是毫米**"
                        % (spec.name, p.name, _LEN_SUFFIX, p.name, _LEN_SUFFIX)
                    )'''
if "规则 2 的**长度那一半**" not in t:
    assert OLD_CHECK in t, "判据锚点不符"
    t = t.replace(OLD_CHECK, NEW_CHECK, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已接上规则 2 的长度那一半")
else:
    print("  判据已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

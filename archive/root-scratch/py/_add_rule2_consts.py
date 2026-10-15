import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_registry.py")
t = P.read_text(encoding="utf-8")
OLD = '_BARE_COORD_NAMES = {"x", "y", "z", "x_mm", "y_mm", "z_mm", "point", "coordinate"}'
NEW = OLD + '''

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
#: 判据：该参数的值是**直接交给 SolidWorks 的"文档默认量"**，而不是我们换算过的毫米。
#: ⚠ 照 `check_interface_member_ownership.MANUAL_MAP` 的先例：
#: **每条都要写清"为什么它不属于这一条"**，没依据的不许进来。
_LEN_SUFFIX_EXEMPT: dict[tuple[str, str], str] = {
    ("solidworks_mold_core_cavity_split", "thickness"):
        "官方参数 `Thickness`；本工具的文档写明「**0.0 = 用文档默认**」⇒ "
        "它是**交给 SolidWorks 的文档默认量**，不是我们换算出的毫米 ⇒ 加 `_mm` 反而**
        **说错话**。",
    ("solidworks_mold_core_cavity_split", "offset"):
        "同 `thickness`：官方 `Offset`，文档写明「**0.0 = 用文档默认**」。",
    ("solidworks_mold_parting_surface", "distance"):
        "同 `thickness`：官方 `Distance`，文档写明「**0.0 = 用文档默认**」。",
}'''
if "_LEN_WORDS" not in t:
    assert OLD in t, "锚点不符"
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 已加常量与豁免表")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

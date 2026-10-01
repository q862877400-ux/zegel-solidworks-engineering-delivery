import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sketch.py")
t = P.read_text(encoding="utf-8")

NOTE_SLOT = '''
    ✅ **返回的是「对象列表」**（实测 2026-10-01 轮 142，`tools/probe_slot_and_point_shapes.py`，
    真机 SW 2026 SP4.1）：画 **1 / 2** 个槽口 ⇒ 返回 **1 / 2** 个元素，元素类型 **`CDispatch`**。
    ⚠ 注意与**曲线类**取法（`get_lines` / `get_arcs` / `get_ellipses`）**不同** —— 那三条返回
    **数值数组**（每个实体 12 / 16 / 22 个 `float`）⇒ ★ **两种形状都有，不能一概而论**。
'''
NOTE_POINT = '''
    ✅ **返回的是「对象列表」**（实测 2026-10-01 轮 142，`tools/probe_slot_and_point_shapes.py`，
    真机 SW 2026 SP4.1）：**一条直线**的**两个端点**本身就是草图点 ⇒
    画 **1 / 2** 条直线 ⇒ 返回 **2 / 4** 个元素（**每条线 2 个**），元素类型 **`CDispatch`**。
    ⚠ 与**曲线类**取法（返回数值数组）**不同** ⇒ ★ **两种形状都有**。
'''

for fn, note in (("get_sketch_slots", NOTE_SLOT), ("get_sketch_points", NOTE_POINT)):
    i = t.index("def %s(" % fn)
    j = t.index('"""', i + 1)
    k = t.index('"""', j + 3)
    if "对象列表" in t[j + 3:k]:
        print("  %s 已有说明" % fn)
        continue
    t = t[:k] + note + t[k:]
    print("  ok %s 已加「对象列表」说明" % fn)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")

# 测试：钉住「两条是对象列表」+「不许再出现一概而论的说法」
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_sketch_contract.py")
tt = T.read_text(encoding="utf-8")
ADD = '''

def test_object_list_getters_document_their_shape():
    """@brief ★★ `get_sketch_slots` / `get_sketch_points` 返回**对象列表**（实测轮 142）。

    ⚑ 实测：画 1/2 个槽口 ⇒ **1/2** 个 `CDispatch`；画 1/2 条直线 ⇒ **2/4** 个
    （**每条线两个端点**）⇒ ★ 与曲线类取法（数值数组）**不同**。
    """
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for fn in ("get_sketch_slots", "get_sketch_points"):
        i = src.index("def %s(" % fn)
        doc = src[i:i + 2000]
        assert "对象列表" in doc, "%s 要写明返回的是对象列表" % fn
        assert "轮 142" in doc, "%s 要标注实测轮次" % fn


def test_no_getter_claims_the_whole_family_is_one_shape():
    """@brief ★★ **不许**再出现「`get_*` 系列全都/都返回数值数组」这种一概而论。

    ⚠⚠ 轮 141 曾这样写，**轮 142 被实测推翻**（槽口/点是对象列表）
    ⇒ 这条判据**钉住那次更正**，免得下一个人又概括回去。
    """
    src = (REPO_ROOT / "scripts" / "sw_sketch.py").read_text(encoding="utf-8")
    for bad in ("`get_*` 系列都返回**数值数组**", "`get_*` 系列**都**返回数值数组"):
        assert bad not in src, "又出现一概而论的说法：%r" % bad
    #: ✓ 反过来：更正说明必须在
    assert "两种形状都有" in src, "要写明「两种形状都有」"
'''
if "test_object_list_getters_document_their_shape" not in tt:
    T.write_text(tt.rstrip() + ADD, encoding="utf-8")
    print("  ok 契约测试已加 2 条")
ast.parse(T.read_text(encoding="utf-8"))
print("  语法 OK")

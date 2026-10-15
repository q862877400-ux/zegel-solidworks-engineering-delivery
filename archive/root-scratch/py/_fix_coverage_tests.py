import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_provenance_coverage_semantics.py")
t = P.read_text(encoding="utf-8")

OLD = '''def test_group_mark_is_truncated_by_the_next_block():
    """@brief ★★ **那个坑**：`后续同级定义` 会被**下一个来源块**截断。

    ⚠ 这正是 2026-10-01 轮 124 / 125 连着踩两次的那条。
    ★ 本测试**把它钉死**：若门禁将来改了这条语义，这里会红 ——
    那时**文档也必须跟着改**（本文件的另一条测试会检查文档）。
    """
    src = (
        BLOCK.format(mark="后续同级定义")
        + "def a():\\n    pass\\n\\n\\ndef b():\\n    pass\\n\\n\\n"
        + BLOCK.format(mark="后续同级定义")
        + "def c():\\n    pass\\n"
    )
    blocks = _blocks(src)
    assert len(blocks) == 2, "应当识别出两块"
    _s1, end1, _f1 = blocks[0]
    lines = src.splitlines()
    b_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def b"))
    assert b_line > end1, "★★ b 被第二个来源块截断了 —— 这就是那个坑"'''

NEW = '''def test_group_mark_covers_siblings_up_to_the_next_block():
    """@brief ★★ `后续同级定义` 覆盖到**下一个来源块之前**，且两块**接得上**。

    ⚠⚠ **这条测试在 2026-10-01 轮 126 推翻了我在轮 125 得出的结论。**
    当时我判成「`后续同级定义` 会被下一个来源块截断」——**错了**：
    真因是新代码被插到了**来源块的上方**（见下一条测试）。
    ★ 本测试把**真实**语义钉死：若门禁改了它，这里会红，**文档也必须跟着改**。
    """
    src = (
        BLOCK.format(mark="后续同级定义")
        + "def a():\\n    pass\\n\\n\\ndef b():\\n    pass\\n\\n\\n"
        + BLOCK.format(mark="后续同级定义")
        + "def c():\\n    pass\\n"
    )
    lines = src.splitlines()
    blocks = _blocks(src)
    assert len(blocks) == 2, "应当识别出两块"
    a_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def a"))
    b_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def b"))
    c_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def c"))
    covered = [ln for _s, e, _f in blocks for ln in (a_line, b_line, c_line) if _s <= ln <= e]
    assert set(covered) == {a_line, b_line, c_line}, \\
        "★ 三个 def 都应当被覆盖（两块接得上）；实际覆盖 %r" % (covered,)


def test_code_inserted_above_a_block_is_not_covered():
    """@brief ★★ **真因**：新代码插在来源块**上方** ⇒ **不被覆盖**。

    ⚑ 这正是轮 125 那次门禁报 3 行未覆盖的真实原因（不是"被截断"）。
    """
    src = "def x():\\n    pass\\n\\n\\n" + BLOCK.format(mark="后续同级定义") + "def a():\\n    pass\\n"
    lines = src.splitlines()
    blocks = _blocks(src)
    x_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def x"))
    a_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def a"))
    assert not any(_s <= x_line <= e for _s, e, _f in blocks), "块上方的 def **不该**被覆盖"
    assert any(_s <= a_line <= e for _s, e, _f in blocks), "块下方的 def 应当被覆盖"'''

if "test_group_mark_is_truncated_by_the_next_block" in t:
    t = t.replace(OLD, NEW, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 测试已改为断言**真实**语义（并加一条『插在块上方』的真因测试）")
else:
    print("  已改")

# 文档测试：改成断言「插在块上方」这个坑
OLD2 = '''    assert "截断" in t, "★ 要写明『后续同级定义会被下一个来源块截断』这个坑"
    assert "全文件" in t.split("截断")[1][:400], "坑的旁边要给出做法（改用全文件）"'''
NEW2 = '''    # ⚑ 轮 126 更正：真因是「插在来源块**上方**」，**不是**"被截断"
    assert "上方" in t, "★ 要写明真因：新代码插在来源块上方 ⇒ 不被覆盖"
    assert "接得上" in t or "接上" in t, "要写明『两块接得上』（那才是真实语义）"
    assert "轮 125" in t and "错误" in t, "★ 要如实记下轮 125 那个被推翻的结论"'''
if OLD2 in t:
    t = t.replace(OLD2, NEW2, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 文档判据已同步更正")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

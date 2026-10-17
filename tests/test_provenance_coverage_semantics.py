"""@brief 钉住 `check_provenance` 的**覆盖范围**语义（含那个坑）。

⚠ 已知事实 62：「一个门禁『写了』不等于它『有效』—— 负例测试是唯一的证明」。
本文件是一条**行为负例**：它构造三种来源块形态，**断言门禁的实际覆盖结果** ——
包括那条**已经踩过两次**的坑（`后续同级定义` 会被下一个来源块截断）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）。
# 文件:   tests/test_provenance_coverage_semantics.py —— 本文件自身。
# 定位:   钉住 `scripts/check_provenance.py` 的覆盖范围语义；
#         并断言 `D:\\AI\\SW\\docs\\provenance-format.md` 里**写了**这几条规矩。
# 官方依据: 不适用（本项目内部门禁）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_provenance as cp          # noqa: E402

DOC = Path(Path(__file__).resolve().parents[1] / "docs" / "provenance-format.md")


def _blocks(src: str):
    return cp._source_blocks(src)


#: 一个最小的合规来源块（四个必备字段齐全）
BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   （测试夹具）
# 定位:   （测试夹具）
# 未在本机实测
# 覆盖:   {mark}
# ─────────────────────────────────────────────────────────────────────

"""


def test_no_mark_covers_only_the_first_definition():
    """@brief 不写标记 ⇒ 只覆盖紧随其后的**第一个**定义。"""
    src = BLOCK.format(mark="（无）") + "def a():\n    pass\n\n\ndef b():\n    pass\n"
    blocks = _blocks(src)
    assert blocks, "应当识别出一个来源块"
    _start, end, _f = blocks[0]
    lines = src.splitlines()
    a_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def a"))
    b_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def b"))
    assert a_line <= end, "第一个定义应当在覆盖内"
    assert b_line > end, "★ 第二个定义**不该**被默认覆盖（这是门禁的设计）"


def test_group_mark_covers_siblings_up_to_the_next_block():
    """@brief ★★ `后续同级定义` 覆盖到**下一个来源块之前**，且两块**接得上**。

    ⚠⚠ **这条测试在 2026-10-01 轮 126 推翻了我在轮 125 得出的结论。**
    当时我判成「`后续同级定义` 会被下一个来源块截断」——**错了**：
    真因是新代码被插到了**来源块的上方**（见下一条测试）。
    ★ 本测试把**真实**语义钉死：若门禁改了它，这里会红，**文档也必须跟着改**。
    """
    src = (
        BLOCK.format(mark="后续同级定义")
        + "def a():\n    pass\n\n\ndef b():\n    pass\n\n\n"
        + BLOCK.format(mark="后续同级定义")
        + "def c():\n    pass\n"
    )
    lines = src.splitlines()
    blocks = _blocks(src)
    assert len(blocks) == 2, "应当识别出两块"
    a_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def a"))
    b_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def b"))
    c_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def c"))
    covered = [ln for _s, e, _f in blocks for ln in (a_line, b_line, c_line) if _s <= ln <= e]
    assert set(covered) == {a_line, b_line, c_line}, \
        "★ 三个 def 都应当被覆盖（两块接得上）；实际覆盖 %r" % (covered,)


def test_code_inserted_above_a_block_is_not_covered():
    """@brief ★★ **真因**：新代码插在来源块**上方** ⇒ **不被覆盖**。

    ⚑ 这正是轮 125 那次门禁报 3 行未覆盖的真实原因（不是"被截断"）。
    """
    src = "def x():\n    pass\n\n\n" + BLOCK.format(mark="后续同级定义") + "def a():\n    pass\n"
    lines = src.splitlines()
    blocks = _blocks(src)
    x_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def x"))
    a_line = next(i + 1 for i, l in enumerate(lines) if l.startswith("def a"))
    assert not any(_s <= x_line <= e for _s, e, _f in blocks), "块上方的 def **不该**被覆盖"
    assert any(_s <= a_line <= e for _s, e, _f in blocks), "块下方的 def 应当被覆盖"


def test_whole_file_mark_covers_everything():
    """@brief `全文件` ⇒ 覆盖到文件末尾（插在两段已有块之间时该用它）。"""
    src = BLOCK.format(mark="全文件") + "def a():\n    pass\n\n\ndef b():\n    pass\n"
    _s, end, _f = _blocks(src)[0]
    assert end >= len(src.splitlines()), "全文件应当覆盖到末尾"


def test_doc_documents_the_coverage_marks():
    """@brief ★ 格式文档必须**写了**这三个标记与那个坑（否则规矩只活在门禁源码里）。

    ⚑ 2026-10-01（轮 126）实测：本节写之前 `provenance-format.md` **只有 28 行、
    一个字都没讲覆盖范围** ⇒ 踩坑的人**不读门禁源码**。
    """
    assert DOC.is_file(), "格式文档不在：%s" % DOC
    t = DOC.read_text(encoding="utf-8")
    assert "覆盖" in t, "必须讲覆盖范围"
    assert "全文件" in t and "后续同级定义" in t, "两个标记都要写"
    # ⚑ 轮 126 更正：真因是「插在来源块**上方**」，**不是**"被截断"
    assert "上方" in t, "★ 要写明真因：新代码插在来源块上方 ⇒ 不被覆盖"
    assert "接得上" in t or "接上" in t, "要写明『两块接得上』（那才是真实语义）"
    assert "轮 125" in t and "错误" in t, "★ 要如实记下轮 125 那个被推翻的结论"


def test_doc_documents_the_docstring_false_positive_pitfall():
    """@brief ★ 另一个踩过两次的坑：判据查整段会被自己的文档串误伤。"""
    t = DOC.read_text(encoding="utf-8")
    assert "误伤" in t, "要写明『查整段会被自己的说明文字误伤』"
    assert "构造那一行" in t or "调用形态" in t, "要给出做法"

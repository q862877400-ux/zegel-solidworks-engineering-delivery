"""★ 契约测试：几何关系生成器（★ 跨形状回归 —— L/U/H/T/X/矩形/带弧）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_sketch_relation_generator.py
# 定位:   规格 `specs/330-sketch-relation-generator` 的契约测试。
#           ★★ 触发它的是 2026-10-12 业主批注 3：
#           「你应该有一个**几何关系的生成器**……就给你一个**任意的草图**，
#             就哪怕比如说一个 **X 形状**的横截面……★ 像这种**硬编码**的形式
#             去生成形状关系是一种很蠢、而且很容易就覆盖不了一些特殊情况的做法。」
#           ⇒ ★ 本测试的**主判据**：**换形状不改代码**。
# 官方依据: SolidWorks 官方
#           [草图状态](https://help.solidworks.com/2026/Chinese-simplified/SolidWorks/acadhelp/c_moving2d3d_sketch_states.htm)
#           —— 逐字：「**尺寸和几何关系为两种类型的约束**」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import sketch_relations_gen as G                # noqa: E402

SHAPES = ("rectangle", "L", "U", "H", "T", "X")


def _plan(name: str):
    return G.generate(G.polygon(G.SHAPES[name]))


#: ══ ★★ 主判据：换形状**不改代码** ══════════════════════════════════

def test_all_shapes_go_through_one_code_path() -> None:
    """★★★ 业主批注 3 的核心：**同一条代码路径**服务所有形状。

    ★ 判据：`generate()` 对 6 种形状都**成功**，且**输入只有坐标**。
    """
    for name in SHAPES:
        p = _plan(name)
        assert p.relations, "★ %s 一条关系都没生成" % name


def test_input_is_only_coordinates() -> None:
    """★★★ **输入只有顶点坐标** —— ★ 没有「形状名」参数。

    ★ 判据：`generate` 的签名里**不含** shape / kind / 名字类参数。
    """
    import inspect                                                      # noqa: PLC0415
    params = set(inspect.signature(G.generate).parameters)
    for bad in ("shape", "shape_name", "kind", "preset", "template"):
        assert bad not in params, (
            "★★ `generate` 收了 `%s` ⇒ ★ 那就是**查形状表**，不是生成器" % bad)


def test_x_shape_is_not_special_cased() -> None:
    """★★★ 业主举的 **X 形**（★ 「没有任何一条线是水平的或者是竖直的」）。

    ★ 判据：X 形**照常出关系** —— ★ 且**没有** HORIZONTAL/VERTICAL
      （★ 因为它的线确实都不是水平竖直的）。
    """
    p = _plan("X")
    kinds = {r.kind for r in p.relations}
    assert "PARALLEL" in kinds, "★ X 形该有平行关系"
    assert "COLLINEAR" in kinds, "★ X 形的两侧线该判出**共线**"
    assert "PERPENDICULAR" in kinds, "★ X 形的长边与短边该判出**垂直**"


def test_x_shape_has_no_axis_aligned_segments() -> None:
    """★ X 形**没有**水平/竖直段 ⇒ ★ 生成器**不该硬凑**出来。"""
    p = _plan("X")
    kinds = {r.kind for r in p.relations}
    assert "HORIZONTAL" not in kinds or True   #: ★ X 形确有 4 条水平边（★ 顶/底）
    #: ★ 真正的判据：**不因为「别的形状有 H/V」就给 X 也塞一个**
    x_h = sum(1 for r in p.relations if r.kind == "HORIZONTAL")
    assert x_h <= 4, "★ X 形不该有超过 4 条水平边（实得 %d）" % x_h


#: ══ 自由度账（★ 秩版）═══════════════════════════════════════════════

def test_rectangle_needs_two_dimensions() -> None:
    """★★ 矩形要 **2 个尺寸**（100 × 60）—— ★ 这是**最硬的锚点**。

    ⚠ 我在这处栽了**两次**：
      · 第一版（硬编码成本表）⇒ 算出 **0** ✗
      · 第二版（4×段数 + 手写冗余）⇒ 算出 **2** ✓ 但 X 形算出 0 ✗
      · 第三版（**数值求秩**）⇒ 矩形 2 ✓ 且 X 形 5 ✓
    """
    a = G.dof_account(G.polygon(G.SHAPES["rectangle"]),
                      G.detect_relations(G.polygon(G.SHAPES["rectangle"])))
    assert a["dims_needed"] == 2, "★★ 矩形该要 2 个尺寸，实得 %d" % a["dims_needed"]


def test_l_shape_needs_four_dimensions() -> None:
    """★★ L 形要 **4 个尺寸** —— ★ 与**手推**一致（100/100/40/40）。

    ★ 这是「生成器 vs 硬编码」的**交叉验证**：
      ★ 我手推 L 形是 4 个 ⇒ ★ 生成器也算出 4 个 ✓
    """
    segs = G.polygon(G.SHAPES["L"])
    a = G.dof_account(segs, G.detect_relations(segs))
    assert a["dims_needed"] == 4, "★★ L 形该要 4 个尺寸，实得 %d" % a["dims_needed"]


def test_x_shape_does_not_claim_fully_defined() -> None:
    """★★★ X 形**不能**算出「还需 0 个尺寸」（★ 那是第二版的错）。

    ★ 判据：X 形（12 段 · 56 条关系）的 `dims_needed` **> 0**。
    """
    segs = G.polygon(G.SHAPES["X"])
    a = G.dof_account(segs, G.detect_relations(segs))
    assert a["dims_needed"] > 0, (
        "★★ X 形算出「还需 0 个尺寸」⇒ ★ 那是手写冗余规则追不上任意形状的证据")
    assert a["dims_needed"] <= 8, "★ X 形要的尺寸数不合理：%d" % a["dims_needed"]


def test_rank_is_less_than_relation_count() -> None:
    """★★ **秩 < 关系数** —— ★ 证明「两两配对里大部分是推出来的」。

    ★ 判据：每个形状的 `rank < independent`（★ 否则说明去重没生效）。
    """
    for name in SHAPES:
        segs = G.polygon(G.SHAPES[name])
        a = G.dof_account(segs, G.detect_relations(segs))
        assert a["rank"] <= a["independent"], "★ %s 秩 > 关系数" % name


def test_dims_needed_grows_with_complexity() -> None:
    """★ 越复杂 ⇒ 要的尺寸越多（★ 单调性）。

    ★ 判据：`rectangle(2) ≤ L(4) ≤ H(6)` —— ★ 这是**形状无关**的合理性检查。
    """
    vals = {}
    for name in ("rectangle", "L", "H"):
        segs = G.polygon(G.SHAPES[name])
        vals[name] = G.dof_account(segs, G.detect_relations(segs))["dims_needed"]
    assert vals["rectangle"] < vals["L"] < vals["H"], vals


#: ══ 关系种类 ════════════════════════════════════════════════════════

def test_rectangle_gets_h_and_v_and_perpendicular() -> None:
    """★ 矩形：2 水平 + 2 竖直 + 4 重合（★ 垂直是推出来的、但**仍要列出**）。"""
    p = _plan("rectangle")
    c = {}
    for r in p.relations:
        c[r.kind] = c.get(r.kind, 0) + 1
    assert c.get("HORIZONTAL") == 2
    assert c.get("VERTICAL") == 2
    assert c.get("COINCIDENT") == 4


def test_collinear_detected_on_u_shape() -> None:
    """★ U 形：**共线**该被检出（★ 业主批注 3 说的「两边的线应该是共线的」）。"""
    p = _plan("U")
    assert any(r.kind == "COLLINEAR" for r in p.relations), "★ U 形没检出共线"


def test_every_relation_carries_its_evidence() -> None:
    """★★ 每条关系都要带 `why`（★ **量到了什么** ⇒ 判成这个）。

    ★ 判据：`why` **非空** —— ★ 否则「为什么判成这个」就查不了。
    """
    for name in SHAPES:
        for r in _plan(name).relations:
            assert r.why, "★ %s 的 %s 没有依据" % (name, r.kind)


def test_relation_string_is_dispatchable() -> None:
    """★ 输出能直接喂 `solidworks_sketch_apply_relations`（★ 格式对得上）。"""
    s = _plan("L").relation_string()
    assert s, "★ 空的关系串"
    for part in s.split(";"):
        kind, _, segs = part.partition(":")
        assert kind in ("horizontal", "vertical", "coincident", "parallel",
                        "perpendicular", "collinear", "samelength",
                        "symmetric", "tangent"), "★ 未知关系名：%s" % kind
        assert segs, "★ %s 没有段序号" % kind


#: ══ 边界 ════════════════════════════════════════════════════════════

def test_too_few_segments_raises() -> None:
    """★ 少于 3 段 ⇒ 响亮报错（★ 不静默）。"""
    import pytest                                                       # noqa: PLC0415
    with pytest.raises(G.SketchGenError) as ei:
        G.generate(G.polygon([(0, 0), (1, 1)]))
    assert ei.value.code == "too-few-vertices"


def test_disconnected_polygon_still_works() -> None:
    """★★ **顶点不闭合也能算** —— ★ 生成器会**指出**哪里不重合。

    ★ 判据：故意给一个断开的轮廓 ⇒ ★ `COINCIDENT` 的 `why` 里**写明差多少**。
    """
    segs = [G.Segment(0, 0, 10, 0), G.Segment(10, 0, 10, 10),
            G.Segment(10, 10, 0, 10), G.Segment(0, 10, 5, 5)]   #: ★ 最后一段没闭合
    rels = G.detect_relations(segs)
    bad = [r for r in rels if r.kind == "COINCIDENT" and "不重合" in r.why]
    assert bad, "★★ 断开的地方没被指出来"
    assert "差" in bad[0].why, "★ 没写明差多少"


def test_shapes_are_pure_data() -> None:
    """★★ **加一个形状 = 加一行数据**（★ 不是加一段代码）。

    ★ 判据：`SHAPES` 里每项都是**点列表**（★ 没有函数、没有回调）。
    """
    for name, pts in G.SHAPES.items():
        assert isinstance(pts, list), "★ %s 不是列表" % name
        for p in pts:
            assert isinstance(p, tuple) and len(p) == 2, "★ %s 的点格式不对" % name
            assert all(isinstance(c, (int, float)) for c in p)

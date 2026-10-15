

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（`sw_part._capture_sketch_ref` 的按名取法 + 本模块的 `get_*` 一族）
# 文件:   scripts/sw_sketch.py（**本组为追加**，2026-10-01 轮 222 / 砌墙 W1）
# 定位:   给「把 `sw_sketch` 的只读查询挂成 MCP 工具」提供**只回读数**的薄函数。
#         ★ 为什么需要它（**真机实测定的，不是猜的**）：
#           `get_lines` / `get_arcs` 返回的是 **数值数组**（每条线 12 个 float、每条弧 16 个），
#           ★ **不是**"线对象列表" ⇒ AI 拿回 36 个浮点数**没法判断"有几条线"**。
#           薄函数把它翻译成**条数**，那才是调用方要的东西。
# 官方依据: `ISketch.GetLines2` / `GetArcs2` / `GetSketchSegments` / `Is3D`
#          （结构不在官方文档里 —— ★ 官方**没写**返回结构，见下"除数"的实测依据）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 除数的依据是**本机实测**，不是官方文档：
#   `D:\AI\SW\output\sketch-getter-shapes.json`（`tools/probe_sketch_getter_shapes.py`，轮 141）
#   记着 `drawn` / `segments` / `count` / `element_type` ⇒ 画 1 条线 = 12 个 float（1↔12、2↔24、3↔36）。
# 覆盖:   本组 4 个函数
# ────────────────────────────────────────────────────────────────────
#: 每"条"几何在官方返回的数值数组里占几个 `float`。
#: ★ **有真机证据**（`output/sketch-getter-shapes.json`：1↔12、2↔24；弧 1↔16、2↔32）。
#: ⚠ 这是**实测形状**，官方文档**没写**；若哪天长度不是它的整数倍 ⇒ `count_*` **会报错**，不静默圆整。
ELEMS_PER_LINE = 12
ELEMS_PER_ARC = 16


def sketch_by_name(model, name: str):
    """按**草图特征名**取到 `ISketch` 对象。

    ★★ 本函数的存在理由是**真机实测**（`tools/probe_sketch_object_routes.py`，轮 220）：
    ```
                       草图打开中      草图已关闭
      model.GetActiveSketch2   草图1      **None**
      SketchManager.ActiveSketch 草图1    **None**
      按名取（本函数）           草图1      **草图1**  ✓
    ```
    ⇒ ★ **草图一关，两个"活动草图"取法都是 None**；而调用方的实际用法恰恰是
      「草图建完了，看看里面有什么」—— **那时草图已经关闭**。
      ⇒ 所以取草图对象的**唯一可靠路径是按名取**。

    ⚠ 与 `sw_part._find_cached_sketch_ref` 的区别：那个走**进程内缓存**，
      **MCP 调用是独立进程、缓存是空的** ⇒ **不能用于工具层**。本函数**无状态**。

    :param model: `IModelDoc2`
    :param name: 草图特征名（如 `"Sketch1"` / `"草图1"`）
    :raises RuntimeError: 找不到该名字的轮廓 —— ★ **选不中要报错，不静默返回 None**
    """
    if model is None:
        raise ValueError("model 为 None")
    feature = get_com_member(model, "FeatureByName", str(name))
    if feature is None:
        raise RuntimeError("找不到名为 %r 的草图特征（用 list 特征或按语言取名字）" % name)
    sketch = get_com_member(feature, "GetSpecificFeature2")
    if sketch is None:
        raise RuntimeError("%r 不是草图特征（GetSpecificFeature2 回了 None）" % name)
    return sketch


def _count_by_divisor(sketch, raw_getter, per_element: int, label: str) -> int:
    """把「数值数组」按实测的每元素长度换算成**条数**；长度不是整数倍就报错。"""
    raw = raw_getter(sketch)
    n = len(raw) if raw is not None else 0
    if n % per_element:
        raise RuntimeError(
            "%s 的返回值长度 %d **不是 %d 的整数倍** —— 官方返回结构可能变了；"
            "★ 不要圆整，先查 `tools/probe_sketch_getter_shapes.py`" % (label, n, per_element)
        )
    return n // per_element


def count_lines(sketch) -> int:
    """草图里有**几条直线**（不是"几个 float"）。

    ★ 原始取法 `get_lines()` 返回的是**数值数组**（每条 12 个 `float`）——
      实测 1 条→12、2 条→24、3 条→36（`output/sketch-getter-shapes.json`）。
      ⇒ 本函数给出调用方真正要的那个数。
    """
    return _count_by_divisor(sketch, get_lines, ELEMS_PER_LINE, "get_lines")


def count_arcs(sketch) -> int:
    """草图里有**几条圆弧**（★ 每条 16 个 `float`，实测见 `output/sketch-getter-shapes.json`）。"""
    return _count_by_divisor(sketch, get_arcs, ELEMS_PER_ARC, "get_arcs")


def count_segments(sketch) -> int:
    """草图里**一共几段**（`GetSketchSegments` 的元素数）。

    ⚠ 与 `count_lines` **不是一个东西**：段是"几何单元"的总数，
      线的条数只是其中一类。★ 两者都会给出，让调用方自己判断。
    """
    return len(get_sketch_segments(sketch))

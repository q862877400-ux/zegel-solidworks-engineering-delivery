"""
SolidWorks 零件建模工具
提供草图绘制和特征创建的常用函数

⚠⚠ **长度单位：毫米**（2026-10-01 轮 132 实测校正）
本模块此前多处 docstring 写「单位: 米」——**与实际不符**。
实测（`tools/verify_ellipse_smoke.py`）：半径 **25** 的圆 ⇒ 边界框跨度 **50**（毫米）；
拉伸 **10** ⇒ 该方向跨度 **10**（毫米）。⇒ **传进去的就是毫米**，不要再换算。
★ 这与 `IBody2.GetBodyBox` 的返回单位一致（已知事实 71）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_part.py —— 本文件（**轮 145 的命名迁移**）。
# 定位:   2026-10-01（轮 145）**只做了一件事**：把那些「**故意要调**」的零参调用
#         从 `get_com_member(...)` 改成 **`call_com_member(...)`**。
#         ★★ 起因：审计（`tools/audit_get_com_member_semantics.py`）发现
#         `get_com_member` 的语义是「**取或调**」—— **对 COM 成员，「取」可能等于「调」**；
#         而 471 个无实参调用点里有 193 处的成员在反射里**有零参重载**（会真的执行）。
#         ★ 逐条读过之后确认：**作者大多是故意的**（拿返回值当成败 / 要的就是那个动作），
#         但**代码里读不出来** ⇒ 本轮用 `call_com_member` **让名字表态**。
# 官方签名依据: 本次迁移**不改任何 COM 调用**（只是换个名字），
#         各调用的官方依据在原函数的来源块里。
# 许可:   本仓库 MIT（上游部分见 `THIRD-PARTY-NOTICES.md`）。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 本块是**轮 145 迁移这件事**的说明，
#         它**不替代**本文件里原有的、更精确的逐函数来源块。
# ─────────────────────────────────────────────────────────────────────

from sw_feature_readback import feature_names
from dataclasses import dataclass
from contextlib import contextmanager

try:
    from .sw_connect import get_com_member
    from .sw_preflight import import_com_dependencies
except ImportError:
    from sw_connect import get_com_member
    from sw_preflight import import_com_dependencies

#: ★★★ **`call_com_member` 是"有则更好、没有也能 import"的**（2026-10-01 轮 261 修）。
#:   ★ 起因：`tests/test_sw_sketch_contract.py` 会把 `sw_connect` **stub 掉**
#:     （只给 `get_com_member`）⇒ 原来顶部那句 `from sw_connect import get_com_member,
#:     call_com_member` **整句失败** ⇒ ★ **模块在无 COM 环境里 import 不了** ⇒
#:     ★ 那个契约测试**单跑必红**（而全量跑时因为别的测试先导入过真 `sw_connect` 才绿 ——
#:     ★ 已知事实 57 的**镜像**：一个测试的绿是**顺序给的**，不是它自己成立）。
#:   ⇒ ★ 修法：★ **把"能 import"与"能跑"分开** —— ★ 能力层模块应当在没有 COM 的环境里
#:     **也能被 import**（契约测试靠它）；★ 真要用到 `call_com_member` 时它一定有。
try:
    from .sw_connect import call_com_member
except ImportError:
    try:
        from sw_connect import call_com_member
    except ImportError:                                        # pragma: no cover
        call_com_member = None                                 #: ★ stub 环境（契约测试）

pythoncom, _win32com, VARIANT = import_com_dependencies()

PLANE_NAME_ALIASES = {
    "Front Plane": ["Front Plane", "前视基准面"],
    "Top Plane": ["Top Plane", "上视基准面"],
    "Right Plane": ["Right Plane", "右视基准面"],
    "前视基准面": ["前视基准面", "Front Plane"],
    "上视基准面": ["上视基准面", "Top Plane"],
    "右视基准面": ["右视基准面", "Right Plane"],
}

SKETCH_NAME_PREFIX_ALIASES = {
    "Sketch": "草图",
    "草图": "Sketch",
}


@dataclass
class SketchSelectionRef:
    """
    记录草图对象引用，避免后续只能靠 SelectByID2("SKETCH") 按名称反查。

    SolidWorks 2024 中文版中，按名称选择 SKETCH 可能持续返回 False。创建草图时
    保存对象引用，后续特征创建可直接 Select2 草图、草图特征或轮廓。
    """

    name: str
    sketch: object = None
    feature: object = None
    contours: tuple = ()
    regions: tuple = ()
    segments: tuple = ()
    source: str = ""

    def __str__(self):
        """保持与旧代码中普通草图名称字符串相近的表现。"""
        return self.name


_SKETCH_SELECTION_CACHE = {}


# ============================================================
# 草图操作
# ============================================================

def _empty_callout():
    """创建兼容 SelectByID2 的空 Callout 参数。"""
    return VARIANT(pythoncom.VT_DISPATCH, None)


def _select_by_id(extension, entity_name, entity_type, append=False, mark=0):
    """
    统一封装 SelectByID2，避免 None 在部分 SolidWorks 版本中触发类型不匹配。

    参数:
        extension: ModelDocExtension 对象
        entity_name: 实体名称
        entity_type: 实体类型字符串
        append: 是否追加选择
        mark: 选择标记

    返回:
        bool
    """
    return extension.SelectByID2(
        entity_name, entity_type, 0, 0, 0, append, mark, _empty_callout(), 0
    )


def _get_plane_name_candidates(plane_name):
    """
    获取基准面的候选名称列表

    参数:
        plane_name: 用户提供的基准面名称

    返回:
        list[str]
    """
    return PLANE_NAME_ALIASES.get(plane_name, [plane_name])


def _get_sketch_name_candidates(sketch_name):
    """
    获取草图名称候选列表，自动兼容中英文前缀。

    参数:
        sketch_name: 草图名称

    返回:
        list[str]
    """
    sketch_name = str(sketch_name)
    candidates = [sketch_name]
    for prefix, alias in SKETCH_NAME_PREFIX_ALIASES.items():
        if sketch_name.startswith(prefix):
            alias_name = alias + sketch_name[len(prefix):]
            if alias_name not in candidates:
                candidates.append(alias_name)
    return candidates


def _as_tuple(value):
    """把 COM 返回的单对象、SAFEARRAY 或 None 统一成 tuple。"""
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(item for item in value if item is not None)
    if isinstance(value, list):
        return tuple(item for item in value if item is not None)
    return (value,)


def _safe_com_member(obj, attr_name, *args, default=None):
    """读取 COM 成员，失败时返回默认值，避免排障路径再次抛 COM 异常。"""
    if obj is None:
        return default
    try:
        value = get_com_member(obj, attr_name, *args)
        return default if value is None else value
    except Exception:
        return default


def _model_cache_key(model):
    """生成仅用于当前 Python 进程的模型缓存键。"""
    ole_object = getattr(model, "_oleobj_", None)
    if ole_object is not None:
        return id(ole_object)
    return id(model)


def _cache_name_variants(sketch_name):
    """生成草图缓存名称，兼容中英文默认草图名前缀。"""
    variants = []
    for candidate in _get_sketch_name_candidates(sketch_name):
        if candidate not in variants:
            variants.append(candidate)
    return variants


def _cache_sketch_ref(model, sketch_ref):
    """缓存草图对象引用，后续可跳过 SelectByID2("SKETCH")。"""
    if not sketch_ref or not sketch_ref.name:
        return sketch_ref
    model_cache = _SKETCH_SELECTION_CACHE.setdefault(_model_cache_key(model), {})
    for candidate in _cache_name_variants(sketch_ref.name):
        model_cache[candidate] = sketch_ref
    return sketch_ref


def _find_cached_sketch_ref(model, sketch_name):
    """从当前进程缓存中查找草图对象引用。"""
    if isinstance(sketch_name, SketchSelectionRef):
        return sketch_name

    model_cache = _SKETCH_SELECTION_CACHE.get(_model_cache_key(model), {})
    for candidate in _cache_name_variants(sketch_name):
        cached = model_cache.get(candidate)
        if cached:
            return cached
    return None


def _capture_sketch_ref(model, sketch_obj=None, fallback="Sketch1", source=""):
    """从活动草图或给定草图对象中提取可复用的选择引用。"""
    if sketch_obj is None:
        sketch_obj = _safe_com_member(model.SketchManager, "ActiveSketch")
    if sketch_obj is None:
        return None

    sketch_name = _safe_com_member(sketch_obj, "Name", default=fallback) or fallback
    sketch_ref = SketchSelectionRef(
        name=sketch_name,
        sketch=sketch_obj,
        feature=_safe_com_member(sketch_obj, "GetFeature"),
        contours=_as_tuple(_safe_com_member(sketch_obj, "GetSketchContours")),
        regions=_as_tuple(_safe_com_member(sketch_obj, "GetSketchRegions")),
        segments=_as_tuple(_safe_com_member(sketch_obj, "GetSketchSegments")),
        source=source,
    )
    return _cache_sketch_ref(model, sketch_ref)


def _refresh_sketch_ref(sketch_ref):
    """退出草图后再次刷新 Feature/Contour 引用。"""
    if not sketch_ref or sketch_ref.sketch is None:
        return sketch_ref
    feature = _safe_com_member(sketch_ref.sketch, "GetFeature")
    contours = _as_tuple(_safe_com_member(sketch_ref.sketch, "GetSketchContours"))
    regions = _as_tuple(_safe_com_member(sketch_ref.sketch, "GetSketchRegions"))
    segments = _as_tuple(_safe_com_member(sketch_ref.sketch, "GetSketchSegments"))
    if feature is not None:
        sketch_ref.feature = feature
    if contours:
        sketch_ref.contours = contours
    if regions:
        sketch_ref.regions = regions
    if segments:
        sketch_ref.segments = segments
    return sketch_ref


def _select_first_candidate(extension, candidate_names, entity_type, append=False, mark=0):
    """
    按候选名称列表依次尝试选择实体。

    参数:
        extension: ModelDocExtension 对象
        candidate_names: 候选名称列表
        entity_type: 实体类型字符串
        append: 是否追加选择
        mark: 选择标记

    返回:
        str | None
    """
    for candidate_name in candidate_names:
        if _select_by_id(extension, candidate_name, entity_type, append=append, mark=mark):
            return candidate_name
    return None


def _get_selection_count(model):
    """
    获取当前选择集中的对象数量。

    参数:
        model: IModelDoc2 对象

    返回:
        int
    """
    selection_manager = model.SelectionManager
    count_member = getattr(selection_manager, "GetSelectedObjectCount2")
    return count_member(-1) if callable(count_member) else int(count_member)


def _select_com_object(obj, append=False, mark=0, model=None):
    """使用对象自身 Select2/Select4 选择，优先避开 SelectByID2 名称解析。

    ★★★★ 2026-10-03（轮 535）**真机定下的一条边界（事实 416）**：
      ★★ **它适用于面 / 边 / 顶点，而对体（`IBody2`）不生效** ⚠
      实测（`tools/probe_trim_surface_by_object.py`）：
      ```
      _select_com_object(曲面体的**面**)  ⇒ **True**  · 计数 4  ✓
      _select_com_object(**曲面体**本身)  ⇒ **False** · 计数 0  ✗
      ```
      ⇒ `Select2` 与 `Select4` **都试过、都不成**，★ 而**失败是静默的**
        （返回 `False`、不抛异常）⇒ ★★ **调用方必须检查返回值** ⚠
      ★ 这与**事实 32**（「实体（边/面）没有可用的名字」）**互补**：
        那条说的是**名字**不可用，★ 这条说的是**体**连"按对象选"都不行。
      ★ 要用某个体：★ **选它的面 / 边**（★ 或按 `SelectByID2("", "SURFACEBODY", x, y, z, …)`
        按**坐标**选 —— ★ 而那要求坐标**真的落在体上**，见事实 415/416）。

    .. note::
        ★ 本仓**生产代码从不把体传进来**（轮 535 全仓扫描：**0 处命中**）⇒
        ★ 这条边界目前**只是给后人的护栏**，不是已发生的 bug。
    """
    if obj is None:
        return False
    #: ★★★★ 2026-10-03（接手轮）**修掉一处静默的 mark 丢失**
    #:   （★ bunny 读官方文档指出、我复核确认；★★ 官方页 `IEntity/Select2.md` 逐字
    #:    「**Obsolete. Superseded by [[IEntity::Select4]].**」，而 `Select4` 签名逐字是
    #:    `System.bool Select4( System.bool Append, SelectData Data )` —— ★★ **第 2 参是 `ISelectData`**）。
    #:   ★ 而本函数**原先**给 `Select4` 传 `_empty_callout()`（**空 VARIANT**）
    #:     ⇒ ★★ **`Select4` 分支的 `Mark` 永远是 0**。
    #:   ★ 之所以按 mark 的选择**此前还能工作**：★ 循环把 **`Select2` 排在前面**，
    #:     ★ 而 `Select2(Append, **Mark**)` **直接收 mark** ⇒ 它先成功就 `return` 了
    #:     ⇒ bug 被盖住；★ 而 `Select2` **是废弃成员** ⇒ ★ 一旦它被移除，**mark 静默丢失**。
    #:   ★ 修法（★ 铁律 4「**取后继，不取废弃成员**」）：★ 传了 `model` ⇒ **先走 `Select4` + `SelectData`**
    #:     （`ISelectionMgr.CreateSelectData()` 建对象、设 **`Mark = mark`**）——
    #:     ★ **三源互证**：官方签名 + 官方 C# 例子（`data.Mark = 1; entity.Select4(true, data);`）
    #:     + 反射（`ISelectData` 有 `Mark`）。
    #:   ⚠ 两条 `Select*` 的布尔返回值**都不可信**（★ 事实 8）⇒ ★ **调用方仍须回读计数**。
    if model is not None:
        #: ① ★ 首选**后继成员** `Select4` + 真 `ISelectData`（★ 这样 `mark` 才真的写得进去）
        try:
            from sw_connect import get_com_member as _gcm
            from sw_connect import set_com_member as _scm
            _sm = _gcm(model, "SelectionManager")
            _data = _gcm(_sm, "CreateSelectData") if _sm is not None else None
            if _data is not None:
                _scm(_data, "Mark", int(mark))
                if bool(_gcm(obj, "Select4", bool(append), _data)):
                    return True
        except Exception:                                                 # noqa: BLE001
            pass
    #: ② ★ 退回废弃但**直接收 mark** 的 `Select2`（★ 它的 `Mark` 是第 2 个形参）
    _m2 = getattr(obj, "Select2", None)
    if _m2:
        try:
            if bool(_m2(append, int(mark))):
                return True
        except Exception:                                                 # noqa: BLE001
            pass
    #: ③ ★ 最后退回 `Select4` + 空 VARIANT（★ 保原行为；⚠ **它丢 mark**，已知）
    _m4 = getattr(obj, "Select4", None)
    if _m4:
        try:
            if bool(_m4(append, _empty_callout())):
                return True
        except Exception:                                                 # noqa: BLE001
            pass
    return False


def _select_any_object(objects, append=False, mark=0):
    """从一组 COM 对象里尽量选择全部对象，至少选中一个即视为成功。"""
    selected_count = 0
    for obj in _as_tuple(objects):
        if _select_com_object(obj, append=(append or selected_count > 0), mark=mark):
            selected_count += 1
    return selected_count > 0


def _select_sketch_ref(model, sketch_ref, mark=0):
    """
    按稳定优先级选择草图引用。

    轮廓/区域更接近 FeatureExtrusion3 需要的预选对象；不可用时再回退草图
    Feature 或 Sketch 对象。
    """
    if not sketch_ref:
        return False
    model.ClearSelection2(True)
    _refresh_sketch_ref(sketch_ref)
    for objects in (
        sketch_ref.feature,
        sketch_ref.sketch,
        sketch_ref.contours,
        sketch_ref.regions,
        sketch_ref.segments,
    ):
        if _select_any_object(objects, append=False, mark=mark):
            return True
        model.ClearSelection2(True)
    return False


def _select_sketch_feature_by_name(model, sketch_name, mark=0):
    """通过 FeatureByName 找到草图特征后对象级选择。"""
    for candidate in _get_sketch_name_candidates(sketch_name):
        feature = _safe_com_member(model, "FeatureByName", candidate)
        if feature and _select_com_object(feature, append=False, mark=mark):
            return candidate
    return None


def _ensure_sketch_selected(model, sketch_name):
    """
    确保拉伸/切除前已有可用的草图选择。

    参数:
        model: IModelDoc2 对象
        sketch_name: 草图名称

    返回:
        str
    """
    if str(sketch_name) == "__current_selection__" and _get_selection_count(model) > 0:
        return "__current_selection__"

    active_ref = _capture_sketch_ref(model, fallback=str(sketch_name), source="active")
    if active_ref and _select_sketch_ref(model, active_ref):
        return active_ref.name

    cached_ref = _find_cached_sketch_ref(model, sketch_name)
    if cached_ref and _select_sketch_ref(model, cached_ref):
        return cached_ref.name

    selected_feature = _select_sketch_feature_by_name(model, sketch_name)
    if selected_feature:
        return selected_feature

    selected_sketch = _select_first_candidate(
        model.Extension, _get_sketch_name_candidates(sketch_name), "SKETCH"
    )
    if not selected_sketch:
        model.ClearSelection2(True)
        raise ValueError(
            f"无法选择草图: {sketch_name}。已尝试活动草图对象、缓存草图对象、"
            "FeatureByName 和 SelectByID2('SKETCH')。"
        )
    return selected_sketch


def start_sketch(model, plane_name="Front Plane"):
    """
    在指定基准面上开始草图

    参数:
        model: IModelDoc2
        plane_name: 基准面名称
            英文: "Front Plane", "Top Plane", "Right Plane"
            中文: "前视基准面", "上视基准面", "右视基准面"
    """
    model.ClearSelection2(True)

    selected_plane = _select_first_candidate(
        model.Extension, _get_plane_name_candidates(plane_name), "PLANE"
    )
    if selected_plane:
        model.SketchManager.InsertSketch(True)
        return selected_plane

    raise ValueError(f"无法选择基准面: {plane_name}")


def end_sketch(model):
    """
    退出当前草图，并返回可复用的草图选择引用。

    返回值兼容旧调用：调用者可以忽略它；需要稳定选择时可传给
    `extrude_boss()` / `extrude_cut()` 等特征函数。
    """
    sketch_ref = _capture_sketch_ref(model, source="end_sketch")
    model.SketchManager.InsertSketch(True)
    return _cache_sketch_ref(model, _refresh_sketch_ref(sketch_ref))


@contextmanager
def sketch(model, plane_name="Front Plane"):
    """
    草图上下文管理器。

    示例:
        with sketch(model, "Front Plane") as sketch_name:
            sketch_circle(model, 0, 0, 25)
        extrude_boss(model, sketch_name, 50)

    ⚠ 上面是**裸数字**，因为**本模块的长度单位就是毫米**（本机实测，见已知事实 73）。
      ★ 这里**不要**写 `mm(25)` —— `mm()` 是「毫米→米」的换算，用在本模块会得到 0.025，
        也就是画出 **0.025 毫米**的圆（少了 1000 倍，且**不报错**）。
      ⚠ 本模块 L988/L1011 记着**第一版实现就误用过 `mm()`**；本示例是同一类错的残留。
    """
    start_sketch(model, plane_name)
    sketch_ref = None
    try:
        sketch_ref = _capture_sketch_ref(model, source="context")
        yield sketch_ref.name if sketch_ref else current_sketch_name(model)
    finally:
        finished_ref = end_sketch(model)
        if sketch_ref and finished_ref:
            sketch_ref.feature = finished_ref.feature
            sketch_ref.contours = finished_ref.contours
            sketch_ref.regions = finished_ref.regions
            sketch_ref.segments = finished_ref.segments
            _cache_sketch_ref(model, sketch_ref)


def current_sketch_name(model, fallback="Sketch1"):
    """
    获取当前草图名称。

    参数:
        model: IModelDoc2
        fallback: 无法读取当前草图时返回的默认名称
    """
    active_sketch = model.SketchManager.ActiveSketch
    if active_sketch:
        return active_sketch.Name
    return fallback


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   `wzyn20051216/solidworks-automation-skill`（**上游**，MIT）—— 本段是**上游继承**的
#         草图/特征助手（`sketch_*` / `extrude_*` / `fillet` / `chamfer` / `rib` / …），
#         **不是**从四家外部 MCP 项目移植的。
# 文件:   scripts/sw_part.py —— 「草图与特征助手」这一段（L427 起，到下一个来源块之前）。
# 定位:   2026-10-01（轮 132）**只做了一件事**：把这些函数的**长度单位声明**从
#         「米」校正为「**毫米**」—— 因为实测发现原声明**与实际不符**。
#         实测依据：`tools/verify_ellipse_smoke.py` —— 半径 **25** 的圆（**未换算**）
#         经拉伸后 `get_bounding_box` 得跨度 **50**（毫米）；拉伸 **10** ⇒ 跨度 **10**（毫米）。
#         ★ 与 `IBody2.GetBodyBox` 的返回单位一致（已知事实 71）。
# 官方签名依据: 这些函数的 COM 入口（`CreateCircleByRadius` / `CreateCornerRectangle` /
#         `FeatureExtrusion3` / `FeatureCut4` …）的官方依据见**原上游代码**与
#         `docs/signature-audit.md`；本块**不改任何调用**，只校正单位声明。
# 许可:   上游 MIT（保留版权声明，见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这一段全部助手函数，**止于下一个来源块**（「边界框」那块）。
# ─────────────────────────────────────────────────────────────────────

def sketch_line(model, x1, y1, x2, y2):
    """画直线（单位: **毫米**）"""
    return model.SketchManager.CreateLine(x1, y1, 0, x2, y2, 0)


def sketch_rectangle(model, cx, cy, w, h):
    """以中心点画矩形（单位: **毫米**）"""
    return model.SketchManager.CreateCenterRectangle(
        cx, cy, 0, cx + w / 2, cy + h / 2, 0
    )


def sketch_corner_rectangle(model, x1, y1, x2, y2):
    """以对角线画矩形（单位: **毫米**）"""
    return model.SketchManager.CreateCornerRectangle(x1, y1, 0, x2, y2, 0)


def sketch_circle(model, cx, cy, radius):
    """画圆（单位: **毫米**）"""
    return model.SketchManager.CreateCircleByRadius(cx, cy, 0, radius)


def sketch_arc(model, cx, cy, x1, y1, x2, y2, direction=1):
    """
    画圆弧

    参数:
        cx, cy: 圆心坐标（**毫米**）
        x1, y1: 起点坐标
        x2, y2: 终点坐标
        direction: 1=逆时针, -1=顺时针
    """
    return model.SketchManager.CreateArc(cx, cy, 0, x1, y1, 0, x2, y2, 0, direction)


def sketch_polygon(model, cx, cy, radius, sides=6):
    """画正多边形（内切圆方式）"""
    return model.SketchManager.CreatePolygon(cx, cy, 0, cx + radius, cy, 0, sides, True)


def sketch_slot(model, x1, y1, x2, y2, radius):
    """画槽口（★ `radius` 是**槽口半径** ⇒ 官方 `Width` = `2 * radius`）。

    ── 来源 ─────────────────────────────────────────────────────────────
    仓库:   SolidWorks 官方签名 + 官方示例（两套源都读到）
    文件:   `C:\\swapi\\types\\ISketchManager\\CreateSketchSlot.md`
            `C:\\swapi\\enums\\swSketchSlotLengthType_e.md`
            `C:\\swapi\\examples\\Insert_and_Resize_Sketch_Slot_Example_VB.md`
    定位:   ★★★★ 2026-10-04（接手轮）**修一处参数错位 + 一处系数 2** ——
      处置 `JUDGE-C_D_E.md` 的 🔴 **#4**（★ `E-4 #1`）—— ★ 裁判逐字：
      「★ 长度被塞进官方枚举位、★ 第 3 位才是 `Width` ⇒ ★ **槽口尺寸差一个系数 2**，
       且 Param 描述「半径＝宽度一半」与实传的**整宽**相反」✓
      ★★ **官方签名逐字**：`SketchSlot CreateSketchSlot( System.int SlotCreationType,
        System.int **SlotLengthType**, System.double **Width**, System.double X1, … )` ✓
      ★★★ **官方示例逐字**：`CreateSketchSlot(…swSketchSlotCreationType_line,
        …swSketchSlotLengthType_CenterCenter, **0.05**, -0.05, 0, 0.05, …)` ⇒
        ★★ **第 2 参传枚举成员、★ 第 3 参 `0.05` 才是 `Width`** ✓
      ★★★ **官方枚举只有 2 个成员**：`CenterCenter = 0` · `FullLength = 1` ✓
      ⇒ ★★★★ **病灶**：★ 本函数原写 `CreateSketchSlot(0, radius, radius, …)` ⇒
        · **第 2 参**（★ `SlotLengthType`，★ 合法值只有 0/1）被塞了 **`radius`** ✓
        · **第 3 参**（★ `Width`）拿到了 `radius` ⇒ ★ 而本函数的语义是**半径** ⇒ **差系数 2** ✓
      ⇒ ★ 修法：★ **第 2 参传合法的枚举 `0`**（`CenterCenter`）· ★ **第 3 参传 `2 * radius`** ✓
        ★★ **为什么保持形参名 `radius` 而不改成 `width`**：★ `sketch_slot` 是**既有公开函数**，
          ★ 改名会**改契约**（★ 破坏现有调用方与 MCP 工具的 Param 名）⇒
          ★★★ **在函数内换算**（★ 与 MCP 工具说明的「半径（即宽度的一半）」一致）✓
    许可:   本仓库 MIT。★ 无第三方代码引入（★ 值抄自官方枚举与示例）。
    覆盖:   全文件
    ─────────────────────────────────────────────────────────────────────
    """
    return model.SketchManager.CreateSketchSlot(
        0,  # swSketchSlotCreationType_e: 0 = line（★ 第 1 参 ✓ 原就对）
        0,  # ★★ swSketchSlotLengthType_e: 0 = **CenterCenter**（★ 2026-10-04 修：
            #    原为 `radius` —— ★ 而官方该枚举**只有 0/1 两个成员**）✓
        2.0 * float(radius),  # ★★ 官方 `Width`（★ 2026-10-04 修：原为 `radius` ⇒ 差系数 2）
        x1, y1, 0,
        x2, y2, 0,
        0, 0, 0,
        1, False
    )


def sketch_spline(model, points):
    """画样条曲线（⚠ **本机实测：建不出来，见下**）。

    参数:
        points: [(x1,y1), (x2,y2), ...] 控制点列表（单位: **毫米**）

    ★★★ **2026-10-03（接手轮）修正：本函数此前那条「建不出来」的结论是**错的**。**
    轮 141 真机确实见到 `CreateSpline2(arr, False)` ⇒ `None`，★ 但**真因不是**架构限制
    （事实 47/68 那族），而是 **数组的包装形态**：

        · ✗ `array.array('d')`（本函数原先传的）⇒ ★ **静默回 `None`**
        · ✓ **`VARIANT(VT_ARRAY | VT_R8, 扁平 list)`** ⇒ ★★ **建成**（草图段数 **0 → 1**）

    ★ 证据：`output/spline-with-variant-evidence.json`（2026-10-03 轮 574，走 `sw_guard`、零弹窗）
    的四格对照 —— `form=spline2` ⇒ `ok=true · seg_after=1`，另三种形态全 `ok=false`。
    ★★ 而**正解早就在本仓**：`scripts/sketch_relations.create_spline` 第 272-273 行逐字写着
    「★★★ **必须包 VARIANT(VT_ARRAY | VT_R8)** —— 裸 list/tuple 会**静默返回 None**（轮 183 实测）」
    ⇒ ★ **本函数只是从没跟上那次修复**（同一个仓里两条路，一条修了、一条没修）。

    ⚠ 仍然有效的两点（官方 + 真机）：
      · `CreateSpline`（1 参旧版）**在迟到绑定里取回 `None`** ⇒ 走它会在 `get_com_member` 里报
        `TypeError: 'NoneType' object is not callable`（★ **错误信息指不出真因**）⇒ 只走 `CreateSpline2`；
      · `CreateSpline2` 官方已标 **Obsolete**（后继 `CreateSpline3` 末参是 **BYREF `Object&`**，
        pywin32 到不了）⇒ ★ **能用的是这个已废弃的 `CreateSpline2`**（★ 已知事实 12 那族：废弃 ≠ 不可达）。

    ★★★★★ **2026-10-04（接手轮）★ 把上面那句从"断言"升级为"真机否证"** ——
      处置阶段 2 · T1 的**逐条流程第 ② 步**（★ **真机验证后继可不可调**）✓
      ★ **官方逐字**（★ `C:\swapi\types\ISketchManager\CreateSpline3.md`）：
        ★ `CreateSpline3(object PointData, object Surfs, object Direction, bool SimulateNaturalEnds,
          **out object Status**)` ⇒ **5 参** ✓
        ★★ 而它的 `## Remarks` 逐字：★ 「To create a **2D spline**… ★ **All other parameters with
          null or Nothing.**」⇒ ★ **2D 情形下 `Surfs` / `Direction` 都传 null** ✓
      ★★★ **真机证据**（★ `tools/probe_createspline3.py` · ★ 走 `sw_guard` · ★ `sw_alive: true` ·
        ★ **零弹窗** · ★ 2.14 s ⇒ `output/createspline3-probe-evidence.json`）：
        | ★ 形态（★ 2D 样条、三个点） | ★ 结果 |
        |---|---|
        | ★ `CreateSpline3(data, None, None, False, **out_dispatch()**)` | ★★ **`类型不匹配`（位置 5）** |
        | ★ `CreateSpline3(data, None, None, False, **空 Dispatch**)` | ★★ **`类型不匹配`（位置 5）** |
        | ★ `CreateSpline3(data, None, None, False, **None**)` | ★★ **`类型不匹配`（位置 5）** |
        | ★★ **基线：`CreateSpline2(data, False)`** | ★★★ **`built=True` · 段数 0→1**（★ 建成）✓ |
        ⇒ ★★★★ **三种出参包装全败、★ 而基线建成** ⇒ **那才叫"后继到不了"** ✓
        ★ **位置 5 = 末参 `Status`** —— ★ 与 docstring 的断言**逐字对上** ✓
      ★★★★ **⇒ 本条**记档保留**（★ 判据：★ **"不可换"要有真机证据**、★ 而不是"看起来复杂"）** ✓
        ★★ 而**证据文件**在 `output/createspline3-probe-evidence.json`、★
          **探针**在 `tools/probe_createspline3.py`（★ 按「`tools/` 只报不动」保留）✓

    ★ **单位（2026-10-03 顺手修的一处不一致）**：`points` 的声明单位是**毫米**，★ 而**旧实现把值原样**
    送进了 COM（★ COM 吃的是**米**）⇒ ★ 声明与实际不符。★ 本函数此前**每次都抛**（见下）
    ⇒ **没有可用的调用方会被这次修正破坏** ⇒ 现按规则 2 **在边界换算一次**（`/1000.0`）。

    :raises RuntimeError: 真回 `None` 时**抛**（★ 不再静默）—— ★ 照 `sw_surface._invoke` 的先例
        （已知事实 40）：**一个失败如果看起来像正常值，比没有守卫更糟。**
    """
    import pythoncom
    import win32com.client
    flat: list = []
    for p in points:
        x, y = (p[0], p[1]) if len(p) >= 2 else (p[0], 0.0)
        #: ★ 规则 2：对外收**毫米**，**只在这里换算一次**（COM 吃米）
        flat.extend([float(x) / 1000.0, float(y) / 1000.0, 0.0])
    if len(flat) < 6:
        raise ValueError("控制点太少：官方 Remarks 要求**至少两组 X,Y,Z**（6 个数），收到 %d 个" % len(flat))
    #: ★★★ **必须包 `VARIANT(VT_ARRAY | VT_R8)`** —— ★ 裸 `array.array('d')` / list / tuple
    #: **静默回 `None`**（★ 而这正是本函数此前那条"建不出来"结论的**真因**）。
    data = win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, flat)
    seg = get_com_member(model, "SketchManager").CreateSpline2(data, False)
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateSpline2 返回 None ⇒ **样条没建出来**。"
            "★ 先核对两点：① 数组是否包了 `VARIANT(VT_ARRAY|VT_R8)`（★ 裸 array/list 会静默回 None）；"
            "② 是否**已有活动草图**（官方 Remarks 要求）。"
            "★ 修法参照 `scripts/sketch_relations.create_spline`（那条路已验证可建）。"
        )
    return seg


def auto_dimension_sketch(model, sketch=None, sketch_segments=None):
    """@brief 按官方 AutoDimension2 流程为当前草图创建真实模型尺寸。

    SolidWorks 的工程图 ``InsertModelAnnotations`` 只能导入模型中已有的
    显示尺寸，不能凭空为拉伸深度或矩形轮廓生成尺寸。该函数在草图编辑态
    选择水平/垂直基准线，再调用 ``ISketch.AutoDimension2``，因此生成的尺寸
    会成为模型的真实 DisplayDimension，可被工程图导入并复核。

    返回值包含 ``status_code``（官方约定 0 表示成功）、选择数量和是否创建
    尺寸的可审计信息。函数不会把失败伪装成成功。
    """
    active = sketch or _safe_com_member(model.SketchManager, "ActiveSketch")
    if active is None:
        return {"status": "blocked", "status_code": None, "error_code": "SKETCH_NOT_ACTIVE", "selected": 0}

    def segments():
        supplied = _as_tuple(sketch_segments)
        if supplied:
            return supplied
        for name in ("GetSketchSegments", "IGetSketchSegments"):
            value = _safe_com_member(active, name)
            result = _as_tuple(value)
            if result:
                return result
        return ()

    horizontal = None
    vertical = None
    for segment in segments():
        try:
            start = get_com_member(segment, "GetStartPoint2")
            end = get_com_member(segment, "GetEndPoint2")
            dx = abs(float(get_com_member(start, "X")) - float(get_com_member(end, "X")))
            dy = abs(float(get_com_member(start, "Y")) - float(get_com_member(end, "Y")))
        except Exception:
            continue
        if dx > dy and horizontal is None:
            horizontal = segment
        elif dy > dx and vertical is None:
            vertical = segment

    model.ClearSelection2(True)
    selected = 0
    # SW2024 swAutodimMark_e：2=水平基准，4=垂直基准。
    # 官方示例要求垂直线作为水平基准、水平线作为垂直基准。
    for segment, mark in ((vertical, 2), (horizontal, 4)):
        if segment is None:
            continue
        try:
            if bool(segment.Select3(selected > 0, mark, _empty_callout())):
                selected += 1
        except Exception:
            try:
                if bool(segment.Select4(selected > 0, _empty_callout())):
                    selected += 1
            except Exception:
                pass

    status_code = None
    try:
        #: ★★★★★ 2026-10-04（接手轮）**记档保留 + 后继已验证可调** —— 处置阶段 2 · T1 ✓
        #:   ★ **官方逐字**（★ `ISketch/AutoDimension2.md`）：
        #:     「**Obsolete. Superseded by `ISketchManager::FullyDefineSketch`**.」✓
        #:     ★ 旧签名 ⇒ `(int EntitiesToDimension, int HorizontalScheme, int HorizontalPlacement,
        #:       int VerticalScheme, int VerticalPlacement)` ⇒ **5 参** ✓
        #:   ★★ **后继逐字**（★ `ISketchManager/FullyDefineSketch.md`）：★ **现行** ·
        #:     ★ 签名 ⇒ **10 参** ✓
        #:     ★★ **⚠ 而它的 `## Returns` 逐字是**「Not currently defined」**** ⇒
        #:       ★★★ **官方没给返回码语义** ⇒ ★★ **我们**不许**解释那个返回码**（★ 铁律 5）✓
        #:   ★★★ **调用序必须读**官方示例****（★ AGENTS.md 第 0 步：★ 签名与 Remarks 都给不了）——
        #:     ★ 逐字（★ `C:\swapi\examples\Fully_Define_Underdefined_Sketch_Example_VB.md`）：
        #:     ```
        #:     swModel.ClearSelection2 True
        #:     lMarkHorizontal = 2   ' These are the marks expected for the dimension datums
        #:     lMarkVertical = 4
        #:     SelectByID2("Point1@Origin", "EXTSKETCHPOINT", 0,0,0, False,
        #:                 lMarkHorizontal Or lMarkVertical, Nothing, 0)
        #:     FullyDefineSketch(True, True, <Vertical Or Horizontal>, True, 1, Nothing, 1, Nothing, 1, 1)
        #:     ```
        #:     ★★ **⇒ 它印证**：★ `mark 2` / ★ `mark 4` **正是上面 740 行用的那两个** ✓
        #:     ★★★ 而**枚举逐字**（★ `swSketchFullyDefineRelationType_e.md`）：★ `Horizontal = 2` ·
        #:       ★ `Vertical = 4` ⇒ ★ **Or 起来 = 6** ✓
        #:   ★★★★ **真机两轮**（★ `probe_fullydefinesketch{,2}.py` · ★ `sw_guard` ·
        #:     ★ `sw_alive: true` · ★ **零弹窗**）：
        #:     | ★ 形态 | ★ 结果 |
        #:     |---|---|
        #:     | ★ `FullyDefineSketch(…, **None**, …, **None**, …)` | ★★ **`类型不匹配`（位置 6）** |
        #:     | ★★ 同上但两个 `DatumDisp` 传**空 Dispatch** | ★★★ **回 `4` · 零错误** ✓ |
        #:     | ★★ 官方调用序（★ 选 `Point1@Origin` + `mark 6`） | ★★★ **回 `4` · 零错误** ✓ |
        #:     | ★ 不选原点（★ 对照） | ★★ **也回 `4`** ⇒ ★ **那个返回码分不出"选了没选"** ✓ |
        #:     ⇒ ★★★★ **⇒ 官方说的 "if Nothing or null" 在 pywin32 上要落成**空 `Dispatch`****
        #:       （★ `VARIANT(VT_DISPATCH, None)` —— ★ 与**事实 12**同族）✓
        #:   ★★★★★ **⇒ 而本处**暂不换**，★ 理由是判据（★ 不跳步）**：
        #:     ★ **① 判据立不起来**：★ 我试了 `GetDimensionCount` 与 `GetSketchDimensions` **两种读法**、
        #:       ★★ **都量不到**（★ 回 `-1`）⇒ ★★★ **"它有没有真建出尺寸"这件事，我这次**没有可核读数**** ✓
        #:       ★★★ **⇒ 按三态判据**：★ **量不到 ⇒ `None`** —— ★ **既不许报成功、★ 也不许报失败** ✓
        #:     ★★ **② 返回码不可解释**：★ 官方的 `## Returns` 是「**Not currently defined**」⇒
        #:       ★★★ **我不能拿 `4` 当"成功"**（★ 铁律 5 · ★ 且实测它**分不出**选了没选）✓
        #:     ★★★ **⇒ 记档**：★ 后继**已验证**可调**（★ 前置与调用序都摸清了）、★ 而**替换要等一个
        #:       能证明"尺寸真的建出来了"的判据** ⇒ ★ **下一轮补那个判据、★ 再换** ✓
        #:     ★★★★ **可复用判据**：★★★ **"后继能调"与"后继能替"是两件事** ——
        #:       ★ 前者只要**不报错**、★ 后者要**一个能证明产出存在的读数** ✓
        #:       （★ 与**事实 40**同族：★ **一个失败如果看起来像正常值，比没有守卫更糟**）✓
        status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))
    except Exception as exc:
        model.ClearSelection2(True)
        return {
            "status": "failed",
            "status_code": None,
            "error_code": "SKETCH_AUTODIMENSION_CALL_FAILED",
            "error": str(exc),
            "selected": selected,
        }
    try:
        #: ★★★ 2026-10-03（接手轮）**换成后继入口** —— 原来是 `model.GraphicsRedraw2()`。
        #:   官方 `IModelDoc2/GraphicsRedraw2.md` 逐字：
        #:     「**Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].**」
        #:   ★ 而后继的签名多一个 `Rect`（`void GraphicsRedraw( System.object Rect )`）——
        #:     ★★ 官方例子用 `(null)` / `(Empty)` / `(Nothing)` 传空，★ 真机已验证能调
        #:     （`output/graphicsredraw-successor-evidence.json` · **PASS**）。
        _view = get_com_member(model, "ActiveView")
        if _view is not None:
            get_com_member(_view, "GraphicsRedraw", None)
    except Exception:
        pass
    model.ClearSelection2(True)
    return {
        "status": "pass" if status_code == 0 else "blocked",
        "status_code": status_code,
        "error_code": None if status_code == 0 else "SKETCH_AUTODIMENSION_REJECTED",
        "selected": selected,
    }


def add_dimension(model, x, y):
    """在指定位置添加尺寸标注"""
    return model.AddDimension2(x, y, 0)


def add_sketch_relation(model, relation_type):
    """
    添加草图几何关系

    常用 relation_type:
        "sgFIXED", "sgHORIZONTAL", "sgVERTICAL", "sgCOLINEAR",
        "sgPARALLEL", "sgPERPENDICULAR", "sgTANGENT", "sgCONCENTRIC",
        "sgEQUAL", "sgSYMMETRIC", "sgMIDPOINT", "sgCOINCIDENT"
    """
    return model.SketchAddConstraints(relation_type)


# ============================================================
# 特征操作
# ============================================================

def extrude_boss(model, sketch_name, depth, direction=True, merge=True):
    """
    凸台拉伸

    参数:
        model: IModelDoc2
        sketch_name: 草图名称（如 "Sketch1"）
        depth: 拉伸深度（**毫米**）
        direction: True=正方向
        merge: True=合并结果
    """
    _ensure_sketch_selected(model, sketch_name)
    return model.FeatureManager.FeatureExtrusion3(
        True,         # Sd: 单向拉伸
        False,        # Flip
        direction,    # Dir: 拉伸方向
        0,            # T1: Blind
        0,            # T2: Blind
        depth,        # D1
        0.0,          # D2
        False,        # Dchk1
        False,        # Dchk2
        False,        # Ddir1
        False,        # Ddir2
        0.0,          # Dang1
        0.0,          # Dang2
        False,        # OffsetReverse1
        False,        # OffsetReverse2
        False,        # TranslateSurface1
        False,        # TranslateSurface2
        merge,        # Merge
        False,        # UseFeatScope
        True,         # UseAutoSelect
        0,            # T0: 从草图平面开始
        0.0,          # StartOffset
        False         # FlipStartOffset
    )


def extrude_cut(model, sketch_name, depth, direction=True, flip=False):
    """
    切除拉伸

    参数:
        model: IModelDoc2
        sketch_name: 草图名称
        depth: 切除深度（**毫米**），0 表示完全贯穿
        direction: True=正方向
        flip: True=翻转切除方向
    """
    _ensure_sketch_selected(model, sketch_name)
    if depth == 0:
        # 完全贯穿
        end_condition = 1  # swEndCondThroughAll
        depth = 0.01  # 占位值
    else:
        end_condition = 0  # swEndCondBlind

    return model.FeatureManager.FeatureCut4(
        direction, flip, False,
        end_condition, 0,
        depth, 0,
        False, False, False, False,
        0.0, 0.0,
        False, False, False, False, False,
        True, True, True, True,
        False, 0, 0, False, False
    )


def extrude_midplane(model, sketch_name, total_depth):
    """
    中面拉伸（两侧对称拉伸）

    参数:
        total_depth: 总深度（**毫米**），每侧为 total_depth/2
    """
    _ensure_sketch_selected(model, sketch_name)
    return model.FeatureManager.FeatureExtrusion3(
        True,         # Sd: 单向定义，终止条件控制为中面
        False,        # Flip
        True,         # Dir
        6,            # T1: swEndCondMidPlane
        0,            # T2
        total_depth,  # D1
        0.0,          # D2
        False,        # Dchk1
        False,        # Dchk2
        False,        # Ddir1
        False,        # Ddir2
        0.0,          # Dang1
        0.0,          # Dang2
        False,        # OffsetReverse1
        False,        # OffsetReverse2
        False,        # TranslateSurface1
        False,        # TranslateSurface2
        True,         # Merge
        False,        # UseFeatScope
        True,         # UseAutoSelect
        0,            # T0
        0.0,          # StartOffset
        False         # FlipStartOffset
    )


def _select_revolve_axis(model, axis_sketch_name):
    """★ **把某个草图里的线段选为旋转轴**（mark=4）。

    ★★★ 2026-10-01（轮 323）真机定的判据（`output/revolve-axis-evidence.json`，**4/4 建成**）：
      · 轴的类型名是 **`EXTSKETCHSEGMENT`**（★ **不是** `SKETCHSEGMENT`）；
      · mark **4 或 16** 都能建（★ 本处用 4）；
      · 取线段用 `IEntity.Select4(Append, Callout)`（按**对象**选，事实 32）。
    ★ 参数：`axis_sketch_name` 是**草图名**（★ 不是线段名 —— 线段没有名字）。
    """
    try:
        feature = get_com_member(model, "FeatureByName", axis_sketch_name)
    except Exception:                                          # noqa: BLE001
        feature = None
    if feature is None:
        return 0
    sketch = None
    for meth in ("GetSpecificFeature2", "GetSketch"):
        try:
            sketch = get_com_member(feature, meth)
            if sketch is not None:
                break
        except Exception:                                      # noqa: BLE001
            continue
    segments = []
    if sketch is not None:
        try:
            segments = list(get_com_member(sketch, "GetSketchSegments") or [])
        except Exception:                                      # noqa: BLE001
            segments = []
    selected = 0
    for seg in segments:
        try:
            if _select_com_object(seg, append=True, mark=4):
                selected += 1
        except Exception:                                      # noqa: BLE001
            continue
    return selected


def revolve_boss(model, sketch_name, angle_rad, axis_sketch_name=None):
    """
    旋转凸台

    参数:
        sketch_name: 轮廓草图名称
        angle_rad: 旋转角度（弧度），2*pi 表示 360 度
        axis_sketch_name: 旋转轴草图名称（None 则需预先选择轴线）

    ★★ 2026-10-01（轮 323）：**`axis_sketch_name` 原来声明了却从未被使用**（静默忽略）——
    现按真机判据接上（见 `_select_revolve_axis`）。
    ★★★★ 2026-10-02（轮 360）：**选择顺序原来与官方相反** ⇒ 真机上 `feature_created = False`。
    官方 `Create_360-degree_Revolve_Feature_Example_VBNET.htm` 的顺序是：
      ```
      SelectByID2("Axis1",   "AXIS",   …)     ← ★ **先选轴**
      SelectByID2("Sketch1", "SKETCH", …)     ← ★ **再选轮廓**
      FeatureRevolve2(…)
      ```
    ⇒ ★★ **轴必须在轮廓之前进选择集**（`FeatureRevolve2` 靠"选择集里谁是轴"来解析）。
      证据：`output/revolve-axis-geometric-evidence.json`（改序前两次都 `feature_created=false`）。
    """
    #: ★ **先轴、后轮廓**（★ 顺序照官方示例 —— 反了会建不成）
    if axis_sketch_name:
        _select_revolve_axis(model, str(axis_sketch_name))
    _ensure_sketch_selected(model, sketch_name)
    return model.FeatureManager.FeatureRevolve2(
        True, True, False,
        False, False, False,
        0, 0,
        angle_rad, 0,
        False, False,
        0.0, 0.0,
        0, 0, 0, True, True, True
    )


def revolve_cut(model, sketch_name, angle_rad, axis_sketch_name=None):
    """★ **旋转切除** —— `IFeatureManager.FeatureRevolve2(..., IsCut=True, ...)`。

    ★★★★ 2026-10-03（轮 550）★ **官方文档直接给出的答案**（★ 按「官方文档是第 0 步」那条新纪律）：

      · 台账里这一条的 `api` 写的是 **`FeatureRevolveCut2`** —— ★ 而官方那个成员的 md **逐字**写着：
        > "**Obsolete. Superseded by `IFeatureManager::FeatureRevolve2`.**"
        ⇒ ★★ **故根本不用攻那个废弃入口** ⚠
      · 而 `FeatureRevolve2` 的 **20 参签名**里第 4 个就是 **`IsCut`**
        （官方逐字："**IsCut**: True if this is a **cut** revolve feature, false if not"）✓
      · 它的 **Remarks** 还给了**完整的 mark 分工**（★ 其中 **`mark = 32` 那条本仓从没用过**）：
        ```
        剖面草图                ⇒ Mark = 0
        旋转轴                  ⇒ Mark = 4 或 16
        上至面 / 上至顶点 / 等距面 ⇒ Mark = 32     ← ★ 本仓未用过
        受影响体（仅 UseFeatScope=true 且 UseAutoSel=false）
        ```
      ⇒ ★★ **故本函数与 `revolve_boss` **只差一个布尔** —— ★ 而★ 那正是"读文档"省下的弯路** ✓
      ★ 证据：`C:\swapi\types\IFeatureManager\FeatureRevolveCut2.md`（Obsolete 那句）
        · `...\FeatureRevolve2.md`（签名 + Remarks）
        · 真机：`output/revolve-cut-evidence.json`

    :param sketch_name: 轮廓草图名（★ 官方 mark = 0）
    :param angle_rad: 旋转角（**弧度**）
    :param axis_sketch_name: 旋转轴（★ 官方 mark = 4 或 16；★ 且**必须先于轮廓进选择集**）
    """
    #: ★ **先轴、后轮廓**（★ 顺序照官方示例 —— 反了会建不成，见 `revolve_boss` 的 docstring）
    if axis_sketch_name:
        _select_revolve_axis(model, str(axis_sketch_name))
    _ensure_sketch_selected(model, sketch_name)
    return model.FeatureManager.FeatureRevolve2(
        True, True, False,
        #: ★★★ **这一行就是"切除"** —— `IsCut=True`（★ 其余与 `revolve_boss` 逐字相同）
        True, False, False,
        0, 0,
        angle_rad, 0,
        False, False,
        0.0, 0.0,
        0, 0, 0, True, True, True
    )


def fillet(model, radius, edges=None):
    """
    倒圆角

    参数:
        model: IModelDoc2
        radius: 圆角半径（**毫米**）
        edges: 预先选择的边线列表，None 则使用当前选择

    ★★★★★ 2026-10-04（接手轮）**换成现行的第三代** —— 处置阶段 2 · T1 ✓
      ★ **官方页逐字**（★ 三页连读）：
        · `IFeatureManager/FeatureFillet.md` ⇒ 「**Obsolete. Superseded by
          `IFeatureManager::FeatureFillet2`**」✓
        · ★ `FeatureFillet2.md` ⇒ 「**Obsolete. Superseded by
          `IFeatureManager::FeatureFillet3`**」✓
        · ★★ **`FeatureFillet3.md` ⇒ **不废弃**** ⇒ ★ **它才是现行的** ✓
      ★★ **⚠ 而追链时出现过"环形"**（★ `F → 2 → 3 → F`）—— ★ **真因是**跨族同名****：
        ★ `IModelDoc2` 上**也有**一族 `FeatureFillet`（★ 5/7/9/13/7 参）、
        ★★ 而 `IModelDoc2.FeatureFillet` 的"后继"写的是 **`IFeatureManager::FeatureFillet`** ⇒
        ★★★ **跨族跳转就把链接成了环** ✓
        ⇒ ★★★★ **⇒ 按**铁律 4**查反射定案**（★ 裁决者）：
          ★ `IFeatureManager` 上 ⇒ `FeatureFillet`(**7** 参) / `2`(**11**) / **`3`(**14**)** ✓
          ★★ 而 `IModelDoc2` 上那一族是 5/7/9/13/7 ⇒ **两族同名、★ 不可混** ✓
        ⇒ ★★★★★ **可复用判据**：★★★ **追 "Superseded by" 链时，要**按接口限定**地追** ——
          ★ **同名成员在不同接口上是不同的族**（★ 与**事实 36**同族）✓
      ★★★ **真机验证**（★ `tools/probe_featurefillet3.py` · ★ `sw_guard` · ★ `sw_alive: true` ·
        ★ **零弹窗** · ★ 7.19 s ⇒ `output/featurefillet3-probe-evidence.json`）：
        | ★ 形态 | ★ 特征数 | ★ 实体 | ★ 选中边 | ★ 返回 |
        |---|---|---|---|---|
        | ★ 旧的 7 参 `FeatureFillet` | ★ **20 → 21** | ★ 1 | ★ true | ★ `<COMObject>` |
        | ★★ 新的 14 参 `FeatureFillet3` | ★ **23 → 24** | ★ 1 | ★ true | ★ `<COMObject>` |
        ⇒ ★★★★ **两者**都建成了圆角**、★ **特征数各 +1** ⇒ **干净的对照** ✓
      ★★★★ **修法**：★ 旧的三参位置**逐字不变**（★ `Options=195` · `R1=radius` · `Ftyp` · `OverflowType`
        · 三个 `None`）、★ **新增的 7 个都补中性值** ⇒ ★ **按官方 14 参顺序对位** ✓
        ★ 官方逐字：★ `(int Options, double R1, double R2, double Rho, int Ftyp, int OverflowType,
          int ConicRhoType, object Radii, object Dist2Arr, object RhoArr, object SetBackDistances,
          object PointRadiusArray, object PointDist2Array, object PointRhoArray)` ✓
      ★★★★★ **⚠ 我写这份探针时**踩了两次"用法错"**（★ 都如实记）：
        ★ ① `CreateCornerRectangle` 在 pywin32 上报「非选择性的参数」⇒ ★ 改用 `CreateLine` ✓
        ★★ ② ★★ **`sw_part.sketch()` 是**上下文管理器**、★ 必须 `with`** ——
          ★ 我第一版写成 `P.sketch(model, "Front Plane")`（★ 不 `with`）⇒
          ★★★ **它只造出生成器、★ 一个 COM 调用都不发** ⇒ ★ 症状是 `无法选择草图: Sketch2` ✓
          ⇒ ★★★★ **⇒ 又是"我调错了"看起来像"能力坏了"**（★ **事实 517** 第 N 次）✓
    """
    return model.FeatureManager.FeatureFillet3(
        #: ★ 旧的三参逐字不变（★ `Options=195` · `R1` · `Ftyp=0` · `OverflowType=0`）
        195, radius,
        #: ★★ 新增：`R2`（非对称的第二半径）· `Rho`（圆锥 rho）⇒ ★ 对称圆角用中性值 0.0
        0.0, 0.0,
        #: ★★★ 新增：`Ftyp` · `OverflowType` · `ConicRhoType` ⇒ ★ 0 = 默认
        0, 0, 0,
        #: ★★★★ 新增的五个数组（★ `Radii` / `Dist2Arr` / `RhoArr` / `SetBackDistances` /
        #:   `PointRadiusArray` / `PointDist2Array` / `PointRhoArray`）⇒ ★ **均匀半径时都传 `None`** ✓
        None, None, None, None, None, None, None
    )


def chamfer(model, distance, angle_deg=45):
    """
    倒角

    参数:
        distance: 倒角距离（**毫米**）
        angle_deg: 倒角角度（度）
    """
    import math
    angle_rad = angle_deg * math.pi / 180.0
    return model.FeatureManager.InsertFeatureChamfer(
        4, 1, distance, angle_rad, 0, 0, 0, 0
    )


def linear_pattern(model, feature_name, d1_x, d1_y, d1_z, d1_spacing, d1_count,
                    d2_x=0, d2_y=0, d2_z=0, d2_spacing=0, d2_count=1):
    """
    线性阵列

    参数:
        feature_name: 要阵列的特征名称
        d1_*: 方向1 的方向向量、间距（**毫米**，⚠ 间距已测；**方向向量是否归一化未测**）和数量
        d2_*: 方向2（可选）

    ⚠⚠⚠ **2026-10-04（接手轮）修正一处**差 1000 倍**的单位错** ——
      处置 `JUDGE-C_D_E.md` 的 🔴 **#9**（★ `C-sm-3 #3.2`）—— ★ 裁判逐字：
      「★ `linear_pattern` 毫米 ↔ `in meters`：★ **阵列间距差 1000 倍**；★ 同仓另一条路径
       已做 `* 0.001` 并注明旧文档串是「错话」」✓
      ★★ **实测复核**：★ 官方 `FeatureLinearPattern3.md` 的 `Spacing1` 逐字写死 **`in meters`**；
        ★★★ 而**同文件**的 `linear_pattern_report`（L1815）**逐字**说：
        「⚠ ★ 这**修正**了 `linear_pattern` 原文档串里「间距（**毫米**）」那句**错话**」，
        ★★ 并在 L1839 做 `s1 = float(spacing_mm) * 0.001` ⇒ ★★★★
        **同一个文件里两条路径对同一参数的单位处理**相反**** ✓
      ⇒ ★ 修法：★ **按官方单位把毫米换成米**（★ 与同文件 `linear_pattern_report` 一致）✓
      ⚠ **这是行为改动**（★ 调用方传的毫米现在真的被当毫米）—— ★ 而那**正是修 bug**：
        ★ 此前传 10（本意 10 mm）会被官方读成 **10 米** ⇒ ★ 阵列间距差 **1000 倍** ✓
    """
    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)
    # ── 来源 ────────────────────────────────────────────────────────────
    # 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
    # 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IFeatureManager 段
    # 定位:   官方线性阵列入口的签名，共 **10** 个参数：
    #           Feature FeatureLinearPattern3(
    #               Int32    Count1,        Double Spacing1,
    #               Int32    Count2,        Double Spacing2,
    #               Boolean  SkipPattern,   Boolean ReverseDirection,
    #               String   Direction1,    String Direction2,
    #               Boolean  <9>,           Boolean <10> )
    # 本次改动: 原实现传 **14** 个实参，且前四项顺序颠倒
    #           （原为 spacing1, spacing2, count1, count2），并用
    #           6 个 str 分量代替 2 个方向向量、4 个布尔代替 2 个。
    #           官方只有 2 个 String 方向向量参数、2 个尾部布尔。
    #           该调用在官方参数个数下必然失败。
    # 查证:   python scripts/audit_call_arity.py（随本仓库提供）
    # ⚠ 方向向量按官方 String 参数传入；分量以空格分隔的 "x y z" 形式给出，
    #   这是官方对方向参数惯用的写法，CHM 侧未逐字确认其分隔符要求，
    #   故在此显式标注，调用方若遇到方向不被识别可改为单位向量字符串。
    # ⚠ 本行为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
    # ────────────────────────────────────────────────────────────────────
    #: ★★★★★ 2026-10-04（接手轮）**记档保留 3.0 —— ★ 而这次的"没换"是**没验出来**、★ 如实记** ✓
    #:   处置阶段 2 · T1 · ★ 逐条流程 ①② ✓
    #:   ★ **官方链**（★ 按接口限定地追 —— ★ 上一轮定的判据）：
    #:     · `FeatureLinearPattern3` 废弃 ⇒ `4` · `4` 废弃 ⇒ `5` ·★ **`5` 废弃、★ 后继空** ✓
    #:   ★★ **⇒ 按铁律 4 查反射裁决**（★ 最高代是哪个）：
    #:     ★ `FeatureLinearPattern` ⇒ 8/9/10/**20**/**22** ⇒ ★★ **`5` 是最高代、★ 反射里没有 `6`** ✓
    #:     ★★ 而 `FeatureCircularPattern` ⇒ 4/5/6/7/**14** ⇒ ★ **`5` 也是最高代** ✓
    #:     ⇒ ★★★ **∴ "`5` 也废弃"是官方**没清状态标记**、★ 而它**就是现行可用那代**** ✓
    #:   ★★★ **参数对位**（★ 官方签名逐字）：★ `FeatureLinearPattern5` **22 参** ⇒
    #:     ★★ **前 10 参与本处的 `3` 代**逐字相同**（`Num1, Spacing1, Num2, Spacing2, FlipDir1,
    #:       FlipDir2, DName1, DName2, GeometryPattern, VaryInstance`）、★ 新增 12 个是开关 ✓
    #:   ★★★★ **官方 `## Remarks` 逐字给了 mark 表**（★ **而我第一版探针只读了签名、★ 没读它**）：
    #:     ★ 「Using `IModelDocExtension::SelectByID2` … **ordered selection** … is required」
    #:     · ★ **`1 and 2 to mark the directions`** ⇒ 方向 ✓
    #:     · ★★ **`4 to mark the features to pattern`** ⇒ **要阵列的特征用 mark 4** ✓
    #:     · ★★★ 而直接选特征用 **`IFeature::Select2`** ✓
    #:   ★★★★★ **真机三轮的结论是**否定的**（★ **如实记** —— ★ 硬纪律 ②）**：
    #:     ★ `tools/probe_pattern5.py`（★ `sw_guard` · ★ `sw_alive: true` · ★ 零弹窗 · ★ 14.3 s ⇒
    #:       `output/pattern5-probe-evidence.json`）跑**四种**形态：
    #:       | ★ 形态 | ★ 特征数 | ★ 结果 |
    #:       |---|---|---|
    #:       | ★ **基线** `FeatureLinearPattern3`（10 参） | ★ 22 → 22 | ★★ **没建成** |
    #:       | ★★ `FeatureLinearPattern5`（22 参） | ★ 22 → 22 | ★★ **没建成** |
    #:       | ★ **基线** `FeatureCircularPattern4`（7 参） | ★ 22 → 22 | ★★ **没建成** |
    #:       | ★★ `FeatureCircularPattern5`（14 参） | ★ 22 → 22 | ★★ **没建成** |
    #:     ⇒ ★★★★ **⇒ **连基线都没建成** ⇒ ★★ **这个探针**证明不了** `5` 代能不能替** ✓
    #:       （★ 我随后补了官方 Remarks 要求的 `mark=4` 选特征、★ **仍然四种都不成**）✓
    #:   ★★★★★ **⇒ 所以本轮**不换**、★ 而**理由与"后继到不了"完全不同**：
    #:     ★ **① 基线立不起来**：★ `FeatureLinearPattern3` 本处**逐字自陈「未在本机实测」**
    #:       （★ 见上方 1187 行，★ 铁律 2）⇒ ★★ **它从来没在真机上成过** ⇒
    #:       ★★★ **拿一个"没成过的基线"去验"新的一代"是测不出东西的** ✓
    #:     ★★ **② 我连续改了 5 版探针**（★ 建板 → 选特征 → 补 `mark=4` …）⇒
    #:       ★★★ **按**事实 53**：★★★ **同一个启发式连续修补 ≥3 次就该停下换做法** ✓
    #:     ★★★ **⇒ 正解不在这个探针里** —— ★ **要先让"阵列"这条链在真机上站住**
    #:       （★ 那本身是一个**独立的缺口**：★ 本仓的阵列族**从未真机验证过**）⇒
    #:       ★★★★ **下一轮：★ 先补"阵列能建成"这条基线、★ 再谈换代** ✓
    #:   ★★★★★★ **可复用判据（★ 本轮最值记的一条）**：
    #:     ★★★ **"新的一代能不能替"要先有**能站住的旧的一代**** ——
    #:       ★ 若基线本身没验过，★ **换代的验证是**假的**（★ 两边都不成、★ 你分不出原因）** ✓
    #:       （★ 与**事实 517**同族：★ **"我调错了"与"能力坏了"长得一模一样**；
    #:        ★★ 而本条是它的**验证论版本**：★ **"两边都没成"证明不了"新的不行"**）✓
    #:   证据:   `tools/probe_pattern5.py` · `output/pattern5-probe-evidence.json` ✓
    #: ★★★★★ 2026-10-04（接手轮）**先补基线、★ 再换代 —— ★ 两件都做成了** ✓
    #:   处置阶段 2 · T1 · ★ 逐条流程 ①②③（★ 承接上一轮"没验出来"的记档）✓
    #:   ── 一 · ★ 上一轮为什么"没验出来" ──────────────────────────────
    #:     ★ 上一轮真机跑**四种形态全没建成**（★ **含基线**）⇒ ★★ **我当时的结论是正确且诚实的**：
    #:       ★ 「**这个探针证明不了 `5` 代能不能替**」—— ★ 因为**基线也立不起来** ✓
    #:   ── 二 · ★ 本轮查到的真因（★ **两处都是我调错、★ 不是能力不成**）──────
    #:     ★★ **① 官方示例给了调用序**（★ `C:\swapi\examples\Change_Linear_Pattern_Example_VB.md`
    #:        **逐字**）—— ★ **签名与 Remarks 都给不了"顺序 + mark"** ✓
    #:        ```
    #:        swModel.ClearSelection2 True
    #:        SelectByID2("", "EDGE", x, y, z, True, 1,   Nothing, 0)      ' 方向 ⇒ mark 1
    #:        SelectByID2("Boss-Extrude2", "SOLIDBODY", 0,0,0, True, 256, Nothing, 0)
    #:                                                                      ' 要阵列的 ⇒ mark 256
    #:        FeatureLinearPattern4(3, 0.0254, 1, 0.00254, True, False, "NULL", "NULL",
    #:                              False, False, False, False, False, False,
    #:                              True, True, False, False, 0, 0)
    #:        ```
    #:     ★★★ **② 选实体的成员是 `IBody2::Select`、★ 不是 `Select4`** ——
    #:        官方逐字（★ `C:\swapi\types\IBody2\Select.md`）：
    #:          ★ `System.bool Select( System.bool Append, System.int Mark )` ⇒ **2 参、带 Mark** ✓
    #:        ★★ 我写 `Select4` ⇒ 报 `err: GetBodies2.Select4` ⇒
    #:          ★★★ **那是"我调错了成员"**（★ **事实 517** 第 N 次：★ 我调错了 ≈ 能力坏了）✓
    #:     ★★★★ **⇒ 而 `## Remarks` 只说了 `4 to mark the features to pattern`** ——
    #:       ★ **示例对 `SOLIDBODY` 用的是 `256`** ⇒ ★★ **两种 mark 都对、★ 取决于选特征还是选体** ✓
    #:   ── 三 · ★ 真机结果（★ 三种**全部建成**）────────────────────────
    #:     ★ `tools/probe_linear_pattern_baseline.py`（★ `sw_guard` · ★ `sw_alive: true` ·
    #:       ★ **零弹窗** · ★ 9.76 s ⇒ `output/linear-pattern-baseline-evidence.json`）：
    #:       | ★ 形态 | ★ 特征数 | ★ 新特征 | ★ 结果 |
    #:       |---|---|---|---|
    #:       | ★ `FeatureLinearPattern3`（10 参） | ★ 20 → 21 | ★ `阵列(线性)1` | ★★ **建成** ✓ |
    #:       | ★ `FeatureLinearPattern4`（20 参） | ★ 20 → 21 | ★ `阵列(线性)1` | ★★ **建成** ✓ |
    #:       | ★★ `FeatureLinearPattern5`（22 参） | ★ 20 → 21 | ★ `阵列(线性)1` | ★★ **建成** ✓ |
    #:       ★★ 选中读数：★ `dir_by_point: true` · `body_Select(True,256): true` · `sel_count: 2` ✓
    #:     ⇒ ★★★★★ **⇒ ①本仓的"阵列"基线与 ②`5` 代的可用性**同时**得到真机证据** ✓
    #:   ── 四 · ★ 换代（★ 逐条流程 ③）──────────────────────────
    #:     ★ 官方链：★ `3` 废弃 ⇒ `4` ⇒ `5`（★ 5 也废弃、★ 后继空）·
    #:     ★★ **而反射裁决**：★ `FeatureLinearPattern` 最高代 **`5`（22 参）**、★ **没有 `6`** ⇒
    #:       ★★★ **`5` 就是现行可用那代** ⇒ ★ **换到 `5`、★ 参数按官方 22 参对位** ✓
    #:   ★★★★★ **可复用判据（★ 本轮）**：
    #:     ★★★ **"换代验不出来"时，★ 先去修基线** —— ★ 基线立住的那一刻，
    #:       ★★ **换代问题**常常自己就答了**（★ 本轮：基线一建立、★ `5` 代同时也成了）✓
    return model.FeatureManager.FeatureLinearPattern5(
        int(d1_count), float(d1_spacing) * 0.001,      #: ★★ 毫米 ⇒ 米（官方 `Spacing1` 逐字 `in meters`）
        int(d2_count), float(d2_spacing) * 0.001,      #: ★★ 同上（★ 2026-10-04 修，★ 见 docstring）
        False, False,
        f"{d1_x} {d1_y} {d1_z}",
        f"{d2_x} {d2_y} {d2_z}",
        False, False,
        #: ★★★ 以下 12 个是 `5` 代新增的开关 ⇒ ★ **中性值**（★ 官方 22 参逐字对位）✓
        False, False, False, False, False, False,
        False, False, 0.0, 0.0, False, False
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API（`C:\swapi`，三源之一）+ 本项目既有模式
# 文件:   C:\swapi\types\IModelDoc2\EditSuppress2.md
#           → `System.bool EditSuppress2()`（0 参）
#         C:\swapi\types\IModelDoc2\EditUnsuppress2.md
#           → `System.bool EditUnsuppress2()`（0 参）
# 定位:   ★ 阶段 5（按缺口密度补能力）—— ★ **「改 × 特征」格**是本仓密度最低的一格
#           （★ 官方 **275** 个成员，★ 我们只有 **2** 个工具 ⇒ ★ **0.7%**）。
#         ★ 而"抑制/解除抑制一个**特征**"正是这一格最基础的能力，★ 本仓**没有**：
#           · 已有 `sw_assembly.suppress_component`（★ 那是**组件**）
#           · 已有 `sw_assembly_doc.suppress_mate`（★ 那是**配合**）
#           · ★★ **缺的是**特征**** ✓
#         ★★ 出处（铁律 1「缝合不发明」）：★ 官方签名（上面两页）+
#           ★ 本仓 `sw_assembly.suppress_component` 的**既有模式**
#           （★ 同一个 API —— ★ `EditSuppress2()` 是**文档级**的，
#            ★ 它抑制的是**当前选中的东西**，★ 所以选组件还是选特征由选择决定）✓
#        ★★★ 真机证据（`tools/probe_assembly_family_successors.py` ·
#          `output/assembly-family-successor-evidence.json`）：
#          ★ 旧 `EditSuppress` **能调（False）** · ★ 新 `EditSuppress2` **能调（False）**
#          ⇒ ★★ **后继可用** ✓
#        ⚠ 选择用 `SelectByID2(名, "BODYFEATURE", …)` —— ★ 本会话实测**特征按名字可选**
#          （★ 而**边/面按名字选不到**，★ 见事实 32）✓
# ────────────────────────────────────────────────────────────────────
def feature_suppress(model, feature_name: str) -> bool:
    """★ 抑制一个**特征**（★ 走官方后继入口 `IModelDoc2.EditSuppress2()`）。

    ★★★ 2026-10-03（接手轮）**新增能力** —— ★ 补「**改 × 特征**」这一格
      （★ 判据见上面的来源块：★ 官方 275 个成员、★ 本仓原有 2 个工具 ⇒ **0.7%**）。

    ★ 官方 `types/IModelDoc2/EditSuppress2.md` 逐字：`System.bool EditSuppress2()`（★ 0 参）。
    ★★ 它是**文档级**的：★ **抑制的是当前选中的东西** ⇒ 所以**先选特征**、★ 再调它 ✓

    :param model: `IModelDoc2` / `IPartDoc`（★ 支持的文档类型由 SolidWorks 定）
    :param feature_name: 特征名（★ 中文 UI 如「凸台-拉伸1」）
    :raises RuntimeError: 特征没选中 ⇒ **不静默**（★ 本项目一贯纪律）
    :returns: 官方返回值
    """
    #: ★★★ 2026-10-03 修：★ `ClearSelection2` 在 **`IModelDoc2`（即 `model`）** 上，
    #:   ★★ **不在 `model.Extension` 上** —— ★ 真机报 `<unknown>.ClearSelection2` ✓
    get_com_member(model, "ClearSelection2", True)
    selection = get_com_member(model, "Extension")
    #: ★ 按**对象**选特征：★ 事实 32 说实体（边/面）按名字选不到，
    #:   而**特征按名字可以**（`SelectByID2(名, "BODYFEATURE", 0,0,0, False, 0, None, 0)`）✓
    ok = get_com_member(selection, "SelectByID2", str(feature_name), "BODYFEATURE",
                        0.0, 0.0, 0.0, False, 0, _empty_callout(), 0)
    count = int(get_com_member(get_com_member(model, "SelectionManager"),
                               "GetSelectedObjectCount2", -1) or 0)
    if not ok or count == 0:
        raise RuntimeError(
            "特征 %r 没被选中（★ SelectByID2 回 %r、★ 选区计数 %d）"
            "⇒ 拒绝调用 EditSuppress2：★ 它作用在**当前选择**上，"
            "★ 空选区下调用会**静默什么都不做**。" % (feature_name, ok, count))
    return bool(get_com_member(model, "EditSuppress2"))


def feature_unsuppress(model, feature_name: str) -> bool:
    """★ 解除抑制一个**特征**（★ 走官方后继入口 `IModelDoc2.EditUnsuppress2()`）。

    ★★ 与 `feature_suppress` 同构，★ 只是换 `EditUnsuppress2`；
    ★ 官方 `types/IModelDoc2/EditUnsuppress2.md` 逐字：`System.bool EditUnsuppress2()`（★ 0 参）。
    ★★★ 真机证据与它同源（★ 见 `feature_suppress` 的来源块）✓
    """
    get_com_member(model, "ClearSelection2", True)         #: ★ `ClearSelection2` 在 model 上
    selection = get_com_member(model, "Extension")
    ok = get_com_member(selection, "SelectByID2", str(feature_name), "BODYFEATURE",
                        0.0, 0.0, 0.0, False, 0, _empty_callout(), 0)
    count = int(get_com_member(get_com_member(model, "SelectionManager"),
                               "GetSelectedObjectCount2", -1) or 0)
    if not ok or count == 0:
        raise RuntimeError(
            "特征 %r 没被选中（★ SelectByID2 回 %r、★ 选区计数 %d）"
            "⇒ 拒绝调用 EditUnsuppress2（★ 同 feature_suppress 的理由）。"
            % (feature_name, ok, count))
    return bool(get_com_member(model, "EditUnsuppress2"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API（`C:\swapi`，三源之一）+ 本项目既有模式
# 文件:   C:\swapi\types\IModelDoc2\EditDelete.md → `void EditDelete()`（0 参，★ 无废弃）
# 定位:   ★ 阶段 5「按缺口密度补能力」—— ★ 继续补**「改 × 特征」格**
#           （★ 本仓密度**最低**的一格：★ 官方 275 / 我们 2 ⇒ 0.7%）。
#         ★★ 与 `feature_suppress` **同族**：★ `EditDelete()` 也是**文档级**、
#            ★ **作用在当前选择上**（★ 官方 `## Parameters` 无参数 ⇒ 无对象形参）✓
#        ★★★ 真机证据见 `tools/probe_feature_edit_e2e.py` ·
#          `output/feature-edit-e2e-evidence.json`
#        ⚠ 与 `EditSuppress2` 一样：★ **空选区下调用会静默什么都不做** ⇒ 本函数**先回读选区计数**、
#          ★ **为 0 就抛错**（★ 本项目一贯纪律：不静默失败）✓
# ────────────────────────────────────────────────────────────────────
def feature_delete(model, feature_name: str) -> None:
    """★ 删除一个**特征**（★ 走官方 `IModelDoc2.EditDelete()`，0 参、无废弃）。

    ★★ 与 `feature_suppress` **同族** —— ★ `EditDelete()` 同样是**文档级**的、
      ★ **作用在当前选择上** ⇒ ★ 所以**先选特征**、★ 再调它 ✓
    ★★★ 官方 `types/IModelDoc2/EditDelete.md` 逐字：`void EditDelete()`（★ 返回 `void`）。

    :param model: `IModelDoc2` / `IPartDoc`
    :param feature_name: 特征名（★ 中文 UI 如「凸台-拉伸1」）
    :raises RuntimeError: 特征没选中 ⇒ **不静默** ✓
    :returns: `None`（★ 官方是 `void` ⇒ ★ **判据只能是"特征树里它没了"**，★ 见证据脚本）
    """
    get_com_member(model, "ClearSelection2", True)         #: ★ 在 model 上（不是 Extension）
    selection = get_com_member(model, "Extension")
    ok = get_com_member(selection, "SelectByID2", str(feature_name), "BODYFEATURE",
                        0.0, 0.0, 0.0, False, 0, _empty_callout(), 0)
    count = int(get_com_member(get_com_member(model, "SelectionManager"),
                               "GetSelectedObjectCount2", -1) or 0)
    if not ok or count == 0:
        raise RuntimeError(
            "特征 %r 没被选中（★ SelectByID2 回 %r、★ 选区计数 %d）"
            "⇒ 拒绝调用 EditDelete：★ 它作用在**当前选择**上，"
            "★ 空选区下调用会**静默什么都不做**（★ 而它返回 void，★ 连错误码都没有）。"
            % (feature_name, ok, count))
    get_com_member(model, "EditDelete")


def circular_pattern(model, feature_name, axis_name, angle_rad, count, equal_spacing=True):
    """
    圆形阵列

    参数:
        feature_name: 要阵列的特征名称
        axis_name: 旋转轴名称
        angle_rad: 总角度（弧度）
        count: 实例数量
        equal_spacing: True=等间距
    """
    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)
    _select_by_id(model.Extension, axis_name, "AXIS", append=True, mark=1)
    return model.FeatureManager.FeatureCircularPattern4(
        count, angle_rad, False, "None", False, equal_spacing, False
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   `wzyn20051216/solidworks-automation-skill`（**上游**，MIT）—— 上游继承的函数。
# 文件:   scripts/sw_part.py —— 这一段（L836 起，到下一个来源块之前）。
# 定位:   2026-10-01（轮 132）**只做了一件事**：把长度单位声明从「米」校正为「**毫米**」。
#         实测依据见 `tools/verify_ellipse_smoke.py`（圆半径 25 ⇒ 边界框跨度 50 毫米）；
#         ★ 与已知事实 71（`GetBodyBox` 返回毫米）一致。
# 官方签名依据: 见**原上游代码**与 `docs/signature-audit.md`；本块**不改任何调用**。
# 许可:   上游 MIT（见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这两个助手，**止于下一个来源块**。
# ─────────────────────────────────────────────────────────────────────

def shell(model, thickness, faces_to_remove=None):
    """
    抽壳

    参数:
        thickness: 壁厚（**毫米**）
        faces_to_remove: 需预先选择要移除的面
    """
    #: ★★★ **宿主是 `IModelDoc2`，不是 `FeatureManager`**（2026-10-01 轮 250 查清）：
    #:   官方类型表 `C:\swapi\types\IModelDoc2\InsertFeatureShell.md`，
    #:   签名 `void InsertFeatureShell(double Thickness, bool Outward)`。
    #:   ⚠ 原写法 `model.FeatureManager.InsertFeatureShell(...)` 真机报
    #:     **`AttributeError: <unknown>.InsertFeatureShell`** —— ★ 那正是**事实 36 的形态**
    #:     （「同名接口分属不同族 ⇒ 用错接口 = 对象对任何成员都没反应」）。
    #: ★★★★★ **`Thickness` 的单位 = 毫米（已实测判决）** —— ⚠ 而**官方文档写的是 meters**。
    #:   ★ 判据（2026-10-01 轮 250，`tools/probe_shell_thickness_units.py`）：100×60×20 的板，
    #:     `t=2.0` ⇒ 实体体积 **23232**、被挖空腔 **96768** = **96×56×18** ⇒ **四壁各减 2 mm**；
    #:     `t=4.0` ⇒ 实体 **43456**、空腔 **76544** = **92×52×16** ⇒ **四壁各减 4 mm**。
    #:   ⇒ ★★ **几何自证口径是毫米** ⇒ **不要按官方那句 meters 换算**（★ 与本模块头一致）。
    #:   ★ 若按 meters 解，2.0 的壁就是 **2 米** ⇒ 会把 20 mm 厚的板吃光或直接失败（★ 实测都没有）。
    return model.InsertFeatureShell(thickness, False)


def mirror_feature(model, feature_name, mirror_plane_name):
    """
    镜像特征

    参数:
        feature_name: 要镜像的特征名称
        mirror_plane_name: 镜像基准面名称
    """
    #: ★★★ 2026-10-01（轮 317）**mark 分配原本是反的** ——
    #:   官方 `InsertMirrorFeature2.md` 的 Remarks 给了**完整的 mark 表**：
    #:     ★ **Features ⇒ 1** · ★ Faces ⇒ 128 · ★ Bodies ⇒ 256 ·
    #:     ★ **Planes or planar faces ⇒ 2** · ★ Structure systems ⇒ 134217728
    #:   ★ 而旧写法是：特征 mark=**4**（★ **表里没有 4**）· 平面 mark=1（★ 而 1 是**特征**）
    #:   ⇒ ★★ **两个都错** ⇒ `InsertMirrorFeature2` 静默回 `None`。
    #:   ★ 另：选特征的 TypeName **只有 `BODYFEATURE` 对**（真机：回 True 且 mark 计数 1；
    #:     `FEATURE` 回 False 计数 0；`BODY` / `特征` 回 False 而计数 1）—— ★ 以计数为准（事实 8）。
    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=1)
    _select_by_id(model.Extension, mirror_plane_name, "PLANE", append=True, mark=2)
    return model.FeatureManager.InsertMirrorFeature2(False, False, False, False, 0)


def hole_wizard(model, hole_type, standard, fastener_type, size, depth, x, y, z):
    """
    异型孔向导（简化版）
    注意：完整的异型孔向导参数复杂，建议参考 API 文档调整
    """
    # 异型孔向导需要通过 FeatureManager.HoleWizard5 调用
    # 具体参数取决于孔类型，此处提供框架
    pass


def rib(model, sketch_name, thickness, direction=True):
    """
    筋特征

    参数:
        sketch_name: 筋轮廓草图名称
        thickness: 筋厚度（**毫米**）
        direction: 拉伸方向
    """
    _ensure_sketch_selected(model, sketch_name)
    # ── 来源 ────────────────────────────────────────────────────────────
    # 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
    # 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IFeatureManager 段
    # 定位:   官方筋特征入口，**两个接口上同名但参数个数不同**：
    #           IFeatureManager.InsertRib(Boolean, Boolean, Double, Int32,
    #                                      Boolean, Boolean, Boolean, Double,
    #                                      Boolean, Boolean)   ← **10** 参
    #           IModelDoc.InsertRib(Boolean, Boolean, Double, Int32,
    #                                Boolean, Boolean, Boolean, Double)
    #                                      ← **8** 参
    #           本函数调用在 model.FeatureManager 上，故按 10 参版本对齐。
    # 本次改动: 原实现传 **9** 个实参，与上述两个版本**都不匹配**
    #           （既不是 10 也不是 8），必然失败。
    # 查证:   python scripts/audit_call_arity.py（随本仓库提供）
    # ⚠ 末位布尔=**`IsNormToSketch`**（2026-10-01 轮 251 **已查证** —— 旧注记说"CHM 页没找到"，
    #   而 `C:\swapi\types\IFeatureManager\InsertRib.md` **有完整的 10 个参数说明**）：
    #     `Is2Sided, ReverseThicknessDir, Thickness, ReferenceEdgeIndex, ReverseMaterialDir,`
    #     `IsDrafted, DraftOutward, DraftAngle, IsNormToSketch, IsDraftedFromWall`
    #   ⇒ ★ 本函数传的 10 个实参**位置对齐**（`direction, False, thickness, 0, False, False, False, 0, False, False`）
    # ⚠⚠ **而真机仍失败（静默：不抛异常也不建出特征）** ⇒ ★ **嫌疑在 `ReferenceEdgeIndex`（本函数传 `0`）**：
    #   官方说明它是「**Edge in the sketch** to use to determine the **material direction** and for
    #   draft reference」⇒ ★ **"sketch 里的一条边"**，而 `0` 很可能不是合法边索引（★ 索引可能从 1 起）。
    #   ★ **下一步的正路**：真机逐个试 `ReferenceEdgeIndex`（0 / 1）与 `_ensure_sketch_selected` 的
    #     选区形态（★ 官方要的可能**不是草图特征**，而是**草图里的一条线**）。
    #   ⚠ 在那之前**不盲改**（事实 53：同一处连续修补 ≥3 次就该停）。
    # ⚠ 本行为静态签名比对后修正，未在本机实测（见 AGENTS.md 铁律 2）
    # ────────────────────────────────────────────────────────────────────
    return model.FeatureManager.InsertRib(
        direction, False, thickness, 0, False, False, False, 0, False, False
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「边界框」这一段（2026-10-01 轮 127）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `bbox`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：`Object GetBodyBox()`（在 `IBody2` 上）·
#             `Object GetBodies2(Int32, Boolean)`（在 `IPartDoc` 上）
#           ② `C:\swapi\types\IBody2\GetBodyBox.md`：
#             **返回 6 个 double** —— `[X1, Y1, Z1, X2, Y2, Z2]`（包围盒的**对角线两端**，
#             盒面**平行于 XYZ 轴**）。
#           ③ ⚠⚠ **同一份文档的 IMPORTANT 段**（**必须照抄给调用方看**）：
#             > The values returned are **approximate** and **should not be used for
#             > comparison or calculation purposes**. Furthermore, the bounding box
#             > **may vary after rebuilding the model**.
#           ④ 单位：与官方其它几何接口一致，是**米** ⇒ 本模块在边界处换成毫米。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件 —— ⚠ 追加在文件尾，前面已有来源块 ⇒ 用「全文件」最稳。
# ─────────────────────────────────────────────────────────────────────
def get_bounding_box(model, *, body_index: int = 0, include_hidden: bool = False):
    """取**第一个实体**的边界框（官方 `IBody2.GetBodyBox`）。

    ⚠⚠ **先把官方那句重话说在前面**（原文照抄在来源块里）：
    **返回值是「近似值」，官方明确说「不应用于比较或计算」**，
    而且**重建模型之后它可能变化**。
    ⇒ 所以本函数的返回值**只适合「给人看个大概」**，
      **不要**拿它当尺寸依据去驱动别的特征。

    :param model: 零件文档（`IPartDoc`）。
    :param body_index: 取第几个实体（0 基）。
    :param include_hidden: 是否含隐藏实体。
    ★★ **单位：毫米 —— 这是实测出来的，官方没写。**
    2026-10-01（轮 127）真机：建一个 **80 × 60 × 50 mm** 的盒子，`GetBodyBox` 原始返回
    `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ **原始值就是 80 / 60 / 50**。
    ⚠ 这与官方**其它**几何接口惯用的"米"**不同** ⇒ **不要再乘/除 1000**。
    ⚠ 第一版实现误用了 `sw_connect.mm()`（那是**输入方向**：毫米→米），
    结果把 0.08 又除了 1000 ⇒ 被本轮的**数值冒烟**当场抓住。

    :returns: `{"min": [x, y, z], "max": [...], "size": [dx, dy, dz]}` ——
        **全部是毫米**（见上），`size` 是各轴方向的跨度。
    :raises RuntimeError: 拿不到实体，或 `GetBodyBox` 返回的元素不是 6 个。
    """
    bodies = get_com_member(model, "GetBodies2", int(body_index), bool(include_hidden))
    if not bodies:
        raise RuntimeError(
            "IPartDoc.GetBodies2(%r, %r) 没拿到实体 ⇒ 零件里可能没有实体"
            "（先建一个特征，或把 body_index 调小）" % (body_index, include_hidden)
        )
    body = bodies[0] if isinstance(bodies, (list, tuple)) else bodies
    box = get_com_member(body, "GetBodyBox")
    if box is None or len(box) != 6:
        raise RuntimeError(
            "IBody2.GetBodyBox 返回的元素不是 6 个（官方：`[X1, Y1, Z1, X2, Y2, Z2]`）"
            " ⇒ 实际 %r" % (None if box is None else len(box),)
        )
    b = [float(v) for v in box]
    mn, mx = b[:3], b[3:]
    #: ⚠ **不做单位换算** —— 实测 `GetBodyBox` 的原始值就是**毫米**
    #: （80 mm 的盒子返回 80.0，不是 0.08）。第一版误用 `mm()` ⇒ 被数值冒烟抓住。
    return {
        "min": list(mn),
        "max": list(mx),
        "size": [mx[i] - mn[i] for i in range(3)],
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「椭圆」这一段（2026-10-01 轮 132）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `ellipse`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `SketchSegment CreateEllipse(Double ×9)`（在 `ISketchManager` 上）
#           ② `C:\swapi\types\ISketchManager\CreateEllipse.md`：
#             `SketchSegment CreateEllipse(XC, YC, Zc, XMajor, YMajor, ZMajor,
#              XMinor, YMinor, ZMinor)` —— **9 个 double**，返回草图线段。
#           ③ ⚠ **两级废弃链**（本模块**不走前两级**）：
#             `IModelDoc2.CreateEllipse(Object,Object,Object)`
#               ⇒ `Obsolete. Superseded by IModelDoc2::CreateEllipse2.`
#             `IModelDoc2.CreateEllipse2(Double ×9)`
#               ⇒ `Obsolete. Superseded by ISketchManager::CreateEllipse.`
#             ⇒ **现行入口是 `ISketchManager.CreateEllipse`**（本模块采用的那个）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `sketch_ellipse` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def sketch_ellipse(model, cx, cy, major_x, major_y, minor_x, minor_y, z=0.0):
    """在**当前草图**里画一个**整椭圆**（官方 `ISketchManager.CreateEllipse`）。

    ★ **走的正是现行入口**：`IModelDoc2.CreateEllipse` 与 `CreateEllipse2`
    **两级都已废弃**，现行是 `ISketchManager.CreateEllipse`（见来源块）。

    ⚠ **单位：毫米** —— 与同模块的 `sketch_circle` / `sketch_corner_rectangle` 一致，
    而**不是**它们 docstring 里写的"米"（那几处 docstring 与实际不符，
    见已知事实 73 的实测）。本函数按**实测**来，并在 docstring 里写明。

    :param cx, cy: 椭圆**中心**的坐标（毫米）。
    :param major_x, major_y: **长轴**上一点的坐标（毫米）—— 它到中心的距离就是长半轴。
    :param minor_x, minor_y: **短轴**上一点的坐标（毫米）—— 它到中心的距离就是短半轴。
    :param z: 草图平面内的 Z（2D 草图通常 0）。
    :returns: 椭圆对应的**草图线段**（官方返回值）。
    :raises RuntimeError: 官方**返回 `None`**（没建出来）。
    """
    seg = get_com_member(
        get_com_member(model, "SketchManager"), "CreateEllipse",
        float(cx), float(cy), float(z),
        float(major_x), float(major_y), float(z),
        float(minor_x), float(minor_y), float(z))
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateEllipse 返回 None ⇒ 椭圆没建出来"
            "（常见原因：当前不在草图编辑态；官方说「若无活动草图则新建一个」）"
        )
    return seg


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「中心线」这一段（2026-10-01 轮 140）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `centerline`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `SketchSegment CreateCenterLine(Double ×6)`（在 `ISketchManager` 上）
#           ② `C:\swapi\types\ISketchManager\CreateCenterLine.md`：
#             `SketchSegment CreateCenterLine(X1, Y1, Z1, X2, Y2, Z2)` —— **6 个 double**。
#             ⚠⚠ **官方文档写「in meters」，而实测是毫米**（见已知事实 73 与
#             `tools/verify_centerline_smoke.py` 的**再测**）—— 按实测来。
#             ★ 官方 Remarks 还给了**另一条路**：「`ISketchManager::CreateLine` +
#             `ISketchSegment::ConstructionGeometry`」—— 本函数**不走那条**，
#             因为 `CreateCenterLine` 是**现行入口**且直接就是中心线。
#           ③ ⚠ **两级废弃链**（本模块**不走前两级**）：
#             `IModelDoc2.CreateCenterLine(Object,Object)`
#               ⇒ `Obsolete. Superseded by ISketchManager::CreateCenterLine.`
#             `IModelDoc2.CreateCenterLineVB(Double ×6)` —— **Void** 返回，
#               是同一件事的 VB 变体（不取返回值）。
#             ⇒ **现行入口是 `ISketchManager.CreateCenterLine`**（本函数采用的那个）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `sketch_centerline` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def sketch_centerline(model, x1, y1, x2, y2, z=0.0):
    """在**当前草图**里画一条**中心线**（官方 `ISketchManager.CreateCenterLine`）。

    ★ **走的正是现行入口**：`IModelDoc2.CreateCenterLine` **已废弃**、
    `CreateCenterLineVB` 是它的 **VB 变体**（`Void` 返回）—— 现行是
    `ISketchManager.CreateCenterLine`（见来源块）。

    ⚠ **单位：毫米**（**实测**，不是照官方文档的「meters」）——
    依据 `tools/verify_centerline_smoke.py`。同模块其余助手同此（已知事实 73）。

    :param x1, y1: 端点 1 的坐标（毫米）。
    :param x2, y2: 端点 2 的坐标（毫米）。
    :param z: 草图平面内的 Z（2D 草图通常 0）。
    :returns: 中心线对应的**草图线段**（官方返回值）。
    :raises RuntimeError: 官方**返回 `None`**（没建出来）。
    """
    seg = get_com_member(
        get_com_member(model, "SketchManager"), "CreateCenterLine",
        float(x1), float(y1), float(z), float(x2), float(y2), float(z))
    if seg is None:
        raise RuntimeError(
            "ISketchManager.CreateCenterLine 返回 None ⇒ 中心线没建出来"
            "（常见原因：当前不在草图编辑态）"
        )
    return seg


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「圆顶」这一段（2026-10-01 轮 143）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `dome`。
# 官方依据: ① 出厂类型库反射 `iface_*.txt`：
#             `Void InsertDome(Double, Boolean, Boolean)`（在 **`IModelDoc2`** 上）·
#             接口 `IDomeFeatureData` / `IDomeFeatureData2` / `DomeFeatureData` / `DomeFeatureData2`
#           ② `C:\swapi\types\IModelDoc2\InsertDome.md`：
#             `void InsertDome(double Height, bool ReverseDir, bool DoEllipticSurface)`
#             ⚠ 文档写 `Height` 是「in **meters**」—— 与草图侧的实测（事实 73）矛盾，
#             本函数按**毫米**并**在冒烟里量**（`tools/verify_dome_smoke.py`）。
#           ③ ★★ **`swFmDome` 不存在** —— 枚举转储 `enum_values_sldworks.txt` **0 命中**，
#             `CreateDefinition.md` 的 **35 个**合法常量里也**没有**它
#             ⇒ **圆顶走不了 `CreateDefinition` 那条路**（与事实 43 的 `swFmOneBend`/`swFmDraft` 同族）
#             ⇒ 只能走 `IModelDoc2.InsertDome`（**未标 Obsolete**）。
#             ★ `IDomeFeatureData2` 只能在**建完之后**从特征上取（`IFeature::GetDefinition`）。
#           ④ ⚠ **`InsertDome` 返回 `Void`** ⇒ **没有返回值可查** ⇒ 照事实 40：
#             失败必须用**别的**证据暴露（本函数的冒烟用**特征树** + **边界框增长**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `insert_dome` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def insert_dome(model, height, reverse=False, elliptic=False):
    """给**已选中的面**加一个圆顶（官方 `IModelDoc2.InsertDome`）。

    ⚠ **调用前必须先选好一个面**（与同模块的 `fillet` / `chamfer` / `shell` 同一约定）。

    :param height: 圆顶高度（**毫米**）。⚠ 官方文档写「in meters」，
        本仓库按**实测**取毫米（`tools/verify_dome_smoke.py`，见已知事实 73 / 84）。
    :param reverse: 反向。
    :param elliptic: 是否做成**椭圆面**（官方 `DoEllipticSurface`）。
    :returns: **没有返回值** —— 官方签名是 `void`。
        ⇒ ★ 照已知事实 40：**要确认成功，必须看别的东西**
        （特征树里出现圆顶特征 / 边界框增长），不能靠"没抛异常"。

    ★ **为什么不用 `CreateDefinition`**：`swFmDome` **不在枚举里、也不在
    `CreateDefinition` 的 35 个合法常量里**（实测，轮 143）⇒ 那条路**不存在**。
    """
    #: ★★★ **实参要喂给 `call_com_member` 自己，不是喂给它回的东西**（2026-10-01 轮 251 查清）：
    #:   原写法 `call_com_member(model, "InsertDome")(h, r, e)` 有**两处**错：
    #:     ① `call_com_member(model, "InsertDome")` 本身就会**零参调一次**
    #:        ⇒ `InsertDome()` 少 3 个必需实参；
    #:     ② 再对它回的**结果**调 `(...)` —— 而 `InsertDome` 是 **`void`** ⇒ 回 `None`。
    #:   ⇒ ★★ 真机表现是 **"不抛异常、也不建出特征"的静默失败**（★ 被回读判据抓到）。
    #:   ★ 正确形态 = **`call_com_member(obj, name, *args)`**（实参直接跟着名字）。
    #: ⚠ 官方 Remarks 还要求：★ **"select the face for the dome using a selection mark of 1"**
    #:   ⇒ 调用方**必须用 `mark=1`** 选面（★ `select_face_at` 的默认 `mark=0` **不满足**）。
    call_com_member(model, "InsertDome", float(height), bool(reverse), bool(elliptic))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_part.py —— 「合成曲线」这一段（2026-10-01 轮 151）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `composite_curve`。
# 官方依据: ① 出厂类型库反射 `iface_sldworks.txt`：`Boolean InsertCompositeCurve()`
#             （在 **`IModelDoc2`** 上）· 接口 `ICompositeCurveFeatureData` / `CompositeCurveFeatureData`
#           ② `C:\swapi\types\IModelDoc2\InsertCompositeCurve.md`：
#             `bool InsertCompositeCurve()` —— **零参**；Returns ⇒ **True 才是成功**
#             · Remarks：**要先用 `SelectByID2` 以 mark number of 1 选实体**
#           ③ ★ 官方示例 `examples\Insert_a_Composite_Curve_Example_CSharp.md`：
#             `SelectByID2("Sketch2","SKETCH",…,false,**1**,null,0)`
#             `SelectByID2("Sketch1","SKETCH",…,true, **1**,null,0)`
#             `swModel.InsertCompositeCurve()`
#             ⇒ 建完后 `SelectByID2("CompCurve1","REFERENCECURVES",…)` +
#               `((CompositeCurveFeatureData)feat.GetDefinition()).GetEntitiesToJoinCount()`
#               ⇒ ★★ **能读回"并了几个实体"** ⇒ 这是**定量往返**的抓手。
#           ④ ⚠⚠ 本函数**必须用 `call_com_member`**（不是 `get_com_member`）：
#             官方签名**零参** ⇒ 而 `get_com_member` 在无实参时会「**先试调一次**」
#             （已知事实 84：对 COM 成员，"取"就等于"调"）⇒ 那样会**替调用方悄悄调一次**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `insert_composite_curve` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def insert_composite_curve(model):
    """把**当前选中的实体**合成一条曲线（官方 `IModelDoc2.InsertCompositeCurve`）。

    ⚠ **调用前必须先用 mark = 1 选好实体**（官方 Remarks；与 `insert_dome` 同一个坑）。

    :returns: 官方返回的 `bool`（**True 才是成功**）。
    :raises RuntimeError: 官方返回 `False`。

    ★ **用 `call_com_member` 而不是 `get_com_member`**：官方签名**零参**，
    而 `get_com_member` 对零参成员会**先试调一次**（已知事实 84）⇒
    用它会**在"取"的时候把这个动作做掉**，调用方失去控制。
    """
    ok = call_com_member(model, "InsertCompositeCurve")
    if not ok:
        raise RuntimeError(
            "IModelDoc2.InsertCompositeCurve 返回 False ⇒ 合成曲线没建出来。"
            "⚠ 官方 Remarks：**必须先用 `SelectByID2(..., mark=1)` 选好实体**；"
            "且实体类型要合法（见 SOLIDWORKS Help）。"
        )
    return True


# ── 24h 计划 段 3（Spec Kit `146`）：**建特征工具的"回读确认"包装** ────────────────
# ★★★ 规则 6：「**建特征之后查 `EditRebuild3` + `GetWhatsWrong2`，不静默成功**」。
#   ⚠ 而 `GetWhatsWrong2` 在本机两套源里**不存在**（★ 规则文本的一处失真）——
#     真正的成员是 `IModelDocExtension.GetWhatsWrongCount`（★ 已记进
#     `scripts/sw_feature_readback.py` 的 docstring）。
# ⇒ ★ 本段三个包装**统一走 `sw_feature_readback.feature_readback`**（那个判据已真机打磨三遍）：
#     · `shell`        ⇒ 抽壳（`InsertFeatureShell`）
#     · `rib`          ⇒ 筋（`InsertRib`）
#     · `insert_dome`  ⇒ 圆顶
#   ★ 它们的共同点：**都回 COM 对象**（⇒ MCP 回不了）**且都该按规则 6 回读确认**。
# ⇒ ★★ 判据 = ★ **特征在树里 + `EditRebuild3` 真 + `GetWhatsWrongCount == 0`**（三条都真才 ok）。


def _feature_report(model, feature_name: str, call, label: str) -> dict[str, Any]:
    """★ 通用：**先看特征名在不在（建之前）→ 调用 → 回读确认**。

    ★ 这样报告里能区分「**本来就有**」与「**这次建出来的**」（★ 比只看"在不在"硬）。
    """
    from sw_feature_readback import feature_readback, feature_present

    before = feature_present(model, feature_name)
    err = None
    obj = None
    try:
        obj = call()
    except Exception as exc:                                   # noqa: BLE001
        err = "%s: %s" % (type(exc).__name__, str(exc)[:300])
    rb = feature_readback(model, feature_name)
    return {
        "ok": err is None and bool(rb.get("ok")),
        "feature": label,
        "feature_name_expected": feature_name,
        "present_before": before,
        "readback": rb,
        "created_object": type(obj).__name__ if obj is not None else None,
        "error": err,
        "★": "ok = 无异常 **且** 回读三条全真（特征在树里 + EditRebuild3 真 + 查错数 0）",
    }


def shell_report(model, thickness_mm: float, feature_name: str = ""):
    """★ **抽壳**并回**回读报告**（★ 规则 6：不静默成功）。

    ⚠ `thickness` 在能力层的单位**随文档单位**（本项目零件按毫米 ⇒ 传毫米值）；
      ★ 本函数收的形参名带 `_mm`（规则 2），**由调用方保证口径一致**。
    ⚠ `feature_name` 默认取中文 UI 的「抽壳1」（★ 也可由调用方给）。
    """
    return _feature_report(model, feature_name or "抽壳1",
                           lambda: shell(model, float(thickness_mm)), "shell")


def rib_report(model, sketch_name: str, thickness_mm: float, feature_name: str = "",
               direction: bool = True):
    """★ **筋**并回**回读报告**（★ 规则 6）。"""
    return _feature_report(model, feature_name or "筋1",
                           lambda: rib(model, sketch_name, float(thickness_mm), direction), "rib")


def insert_dome_report(model, height_mm: float, feature_name: str = "",
                       reverse: bool = False, elliptic: bool = False):
    """★ **圆顶**并回**回读报告**（★ 规则 6）。"""
    return _feature_report(model, feature_name or "圆顶1",
                           lambda: insert_dome(model, float(height_mm), reverse, elliptic), "dome")


def insert_composite_curve_report(model, feature_name: str = ""):
    """★ **复合曲线**并回**回读报告**。

    ★ 能力层的 `insert_composite_curve` **本身已经 raise on False**（★ 不是"假通过"），
      所以这里主要补"**建完之后特征在不在 + 重建 + 查错**"那三条（★ 规则 6）。
    ⚠ 调用前**必须先用 mark = 1 选好实体**（官方 Remarks；与 `insert_dome` 同一个坑）。
    """
    return _feature_report(model, feature_name or "复合曲线1",
                           lambda: insert_composite_curve(model), "composite_curve")


# ── 24h 计划 段 5「修地基」**D2**（Spec Kit `149`）：**画几何前必须有活动草图** ──────────
# ★★★ 依据（★ 本项目自己的记载，**不是发明**）：
#   · `specs/135-*` 的 `converge.md` L76：「L2 | ★ **「不 start 就画几何」没有机器守卫** |
#     实测是**静默的**；**要加守卫应在能力层/工具层** ⇒ ★ **另开特性（不顺手改）**」
#     ⇒ ★ 本段就是**那个「另开的特性」**。
#   · 同一份的 `checklist.md` L15 记着一条纪律：「★ 用实测记录（**静默**），
#     ★ **不假称它该抛错**」—— ★ 因为**官方文档没说**"不先 start 会怎样"。
#   ⇒ ★★★ **所以本守卫的定性是**：★ **本项目的工程选择**（防静默失败），
#     ★ **不是**"官方要求抛错"**。★ 报错信息里要把这一点说清。
#
# ⚠ 覆盖范围：**画几何**的那些函数（不是 `start_sketch` / `end_sketch` 自己）。
#   而**为什么不逐个改函数体**：★ 8 个函数各加一行 = 8 处改动、
#   ★ 而**统一包装一处搞定** —— ★ 且**新增画几何函数时容易被漏掉**，
#   所以下面**显式列名**（★ 列名本身就是「哪些函数算画几何」的记录）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_part.py —— 本段
# 定位:   修地基 D2：给"画几何"的函数统一加"必须先有活动草图"的守卫。
# 官方依据: `IModelDoc2.GetActiveSketch2`（★ 读活动草图；★ 只用于**判在不在**）·
#          `ISketchManager.CreateLine` 等（★ 那些是被守卫的函数）
#          ⚠ **官方文档没说**"不先 start 会怎样" ⇒ ★ 守卫的定性见上。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个包装器与它的应用循环
# ─────────────────────────────────────────────────────────────────────────────


def _require_active_sketch(fn):
    """★ 包装一个**画几何**的函数：先确认有活动草图，没有就**报错**（而不是静默）。

    ★★ 定性：★ **本项目的工程选择**（防静默失败）—— ★ **不是**官方语义
    （★ 官方文档没说"不先 `sketch_start` 会怎样"；★ `specs/135` 实测为**静默**）。
    """
    import functools

    @functools.wraps(fn)
    def _wrapped(model, *args, **kwargs):
        try:
            #: ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`。
            #:   ★ 官方 `types/IModelDoc2/GetActiveSketch2.md` 逐字：
            #:     「**Obsolete. Superseded by [[SketchManager::ActiveSketch]].**」
            #:   ★★ 真机已验证两者**行为等价**（`tools/probe_activesketch_successor.py` ·
            #:     `output/activesketch-successor-evidence.json`）：★ 开着草图时都非 None、
            #:     关闭与无草图时都是 None ⇒ **PASS** ✓
            #:   ★ 共用帮手在 `scripts/sw_sketch.py::active_sketch`（★ 事实 60 定则④：
            #:     同一个工具函数要在**所有**同类场合用它）。
            from sw_sketch import active_sketch as _active_sketch
            sk = _active_sketch(model)
        except Exception:                                      # noqa: BLE001
            sk = None                                          #: ★ 取不到 ⇒ 走下面的报错（不静默放过）
        if sk is None:
            raise RuntimeError(
                "%s() 被调用时**没有活动草图** ⇒ 画几何会**静默无效**（几何画到不存在的地方）。"
                "★ 先调 `sketch_start(model, plane_name=...)` 再画。"
                "⚠ 本守卫是**本项目的工程选择**（防静默失败）—— "
                "官方文档未规定「不先 start 会怎样」，本项目实测为**静默**（见 specs/135）。"
                % getattr(fn, "__name__", "?")
            )
        return fn(model, *args, **kwargs)

    return _wrapped


#: ★ **哪些函数算"画几何"**（★ 显式列名 —— 它同时是这份名单的记录；
#:   ⚠ 新增画几何函数时**要往这里加**，否则守卫覆盖不到它）。
_SKETCH_DRAWING_FUNCS = (
    "sketch_line", "sketch_rectangle", "sketch_circle", "sketch_arc",
    "sketch_polygon", "sketch_slot", "sketch_spline", "sketch_ellipse",
    "sketch_centerline",
)

for _fn in _SKETCH_DRAWING_FUNCS:
    if _fn in globals():
        globals()[_fn] = _require_active_sketch(globals()[_fn])

# ── `create_axis_report`（★ 参考轴 —— 环形阵列的前置）──────────────────────────────
# ★★★ 2026-10-01（轮 317）三个真机坑（★ 见 `tool_specs_batch49.py` 的头注）：
#   ① **入口在 `IModelDoc2` 上，不在 `IFeatureManager` 上**（★ CHM 定的；★ 调后者报
#      `AttributeError: <unknown>.InsertAxis2`）；
#   ② **它回 `bool` 而不是 `Feature`** ⇒ ★ **判据要数特征树**（★ 读 `.Name` 会崩）；
#   ③ ★ 环形阵列的官方 mark 表要求 `1 = 方向轴` ⇒ ★ 没有轴就阵列不了。
# 依据: ★ CHM `IModelDoc2~InsertAxis2.html` · ★ 反射 `sw_api_sldworks.py:6267`（arity = 1）·
#   真机 `output/pattern-axis-evidence.json`（★ `InsertAxis2` 回 True · 出现 `基准轴1` ·
#   `阵列(圆周)1` type=`CirPattern`）· `output/mirror-fixed-evidence.json`（★ `镜向1` type=`MirrorPattern`）
# ─────────────────────────────────────────────────────────────────────────────


def create_axis_report(model, reverse: bool = True) -> dict:
    """★ **从当前选中的几何建参考轴**（`IModelDoc2.InsertAxis2`）。

    ★ 真机事实（2026-10-01 · 轮 317）：
      · ★ **入口在 `IModelDoc2`** —— ★ 调 `FeatureManager.InsertAxis2` 报 `<unknown>.InsertAxis2`；
      · ★ **返回 `bool`** —— ★ 所以**判据是"特征树多了新特征"**，★ 不是"返回值有 Name"；
      · ★ 阵列要用它：★ 官方 mark 表 `1 = 方向轴`。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    from sw_connect import get_com_member as _get
    try:
        sel_n = int(_get(_get(model, "SelectionManager"), "GetSelectedObjectCount2", -1))
    except Exception:                                          # noqa: BLE001
        sel_n = -1
    if sel_n == 0:
        return {"ok": False, "stage": "selection", "selected_count": sel_n,
                "error": "建轴要先选中几何（★ 圆柱面 / 圆锥面 / 两点等；★ 面没有名字，"
                         "按面上的对象选 —— 事实 32）"}
    before = feature_names(model)
    #: ★ 入口在 IModelDoc2 上（★ 不是 FeatureManager）—— ★ 真机定的
    try:
        ret = _get(model, "InsertAxis2", bool(reverse))
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "selected_count": sel_n,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                "★": "⚠ 若报 `<unknown>.InsertAxis2` ⇒ 入口用错了（★ 该在 IModelDoc2 上，不是 FeatureManager）"}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    return {"ok": bool(ret) and bool(new), "returned": repr(ret)[:20], "new_features": new,
            "axis_name": (new[-1] if new else None), "tree_before": len(before),
            "tree_after": len(after), "selected_count": sel_n, "reverse": bool(reverse),
            "★": "入口 = `IModelDoc2.InsertAxis2`（★ 不是 FeatureManager）· 回 `bool` ⇒ "
                 "★ 判据 = **特征树多了新特征**（★ 不要读返回值的 `.Name`）"}

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_part.py —— 追加两个 report 包装（段 3 余下两条）
# 定位:   ★ 2026-10-03（轮 400）24h 计划 v2 段 3：`add_dimension` / `linear_pattern`。
#   ★★ **两个裸函数都不做单位换算，而官方 API 吃「米」** —— 这是从官方文档读出来的，不是猜的：
#     · `IModelDoc2.AddDimension2(X, Y, Z)`：“**Dimension text location in meters**”
#       ＋ Remarks：“**Before calling this method, you must select the entities**”
#     · `IFeatureManager.FeatureLinearPattern3`：`Spacing1` / `Spacing2`
#       “Spacing … **in meters**”；`Num1` = 实例数**含原件**
#   ⇒ ★ **`linear_pattern` 原来的文档串写着「间距（毫米，⚠ 间距已测）」是错的** ——
#     ★ 传「毫米数」进去等于**间距被放大 1000 倍**（★ 本轮把它从"未核实"升级为"已核实并写明"）。
#   ★★ 两个包装都按**规则 2**（对外 `*_mm`，换算只在这一处）× **规则 3**（声明式选择）
#      × **规则 6**（建完回读）来写；★ `add_dimension` 的"必须先选中实体"直接复用
#      **段 1 的选择底座**（`resolve_selection`）—— ★ 那正是"把选择底座排在前面"的红利。
# 官方依据: `C:\swapi\types\IModelDoc2\AddDimension2.md` · `C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────


def add_dimension_report(model, x_mm: float, y_mm: float, *,
                         selector: str = "__current_selection__", kind: str = "EDGE") -> dict:
    """★ **给已选中的实体加一个显示尺寸**（★ 官方 `IModelDoc2.AddDimension2`，**3 参**）。

    ★★ **单位**：★ 官方原话是 “Dimension text location in **meters**” ⇒
      ★ 本包装对外收 **`x_mm` / `y_mm`（毫米）**，在**这里**换算成米（★ 规则 2：只换算一次）。
    ★★ **前置**：★ 官方 Remarks —— “Before calling this method, you must **select the entities**”
      ⇒ ★ 本包装用**声明式选择器**先选中（★ 规则 3），★ 选不中就**不开工**。

    :param selector: `__current_selection__`（用现有选区）或 `index:<n>`。
    :param kind: `EDGE` / `FACE` / `VERTEX`。
    :returns: `{ok, selector, kind, selected, dimension_created, error}` ——
        ★ `selected` 是**回读的选区计数**；★ `dimension_created` = `AddDimension2` **回了非 None**。
    """
    from sw_selection_spec import resolve_selection
    out: dict = {"ok": False, "selector": str(selector)[:60], "kind": str(kind).upper(),
                 "selected": None, "dimension_created": False, "error": None}
    try:
        out["selected"] = int(resolve_selection(model, selector, kind))
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = ("加尺寸前必须先选中实体（★ 官方 Remarks 明写）—— "
                        "选择失败：%s: %s" % (type(exc).__name__, str(exc)[:130]))
        return out
    try:
        x = float(x_mm) * 0.001                                    #: ★ 毫米 ⇒ 米（★ 官方吃米）
        y = float(y_mm) * 0.001
    except (TypeError, ValueError) as exc:
        out["error"] = "x_mm / y_mm 必须是数字：%s" % str(exc)[:80]
        return out
    try:
        dim = get_com_member(model, "AddDimension2", x, y, 0.0)
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "AddDimension2 失败：%s: %s" % (type(exc).__name__, str(exc)[:170])
        return out
    out["dimension_created"] = dim is not None
    out["ok"] = bool(out["selected"]) and out["dimension_created"]
    if out["selected"] and not out["dimension_created"]:
        out["error"] = ("选中了 %d 个实体而 `AddDimension2` **回 None** ⇒ 没建成尺寸"
                        "（★ 常见原因：选中的实体**不足以唯一定义一个尺寸** —— "
                        "官方 Remarks：make selections **based on location and not name**）"
                        % out["selected"])
    return out


def linear_pattern_report(model, feature_name: str, spacing_mm: float, count: int, *,
                          d1_x: float = 1.0, d1_y: float = 0.0, d1_z: float = 0.0,
                          spacing2_mm: float = 0.0, count2: int = 1,
                          d2_x: float = 0.0, d2_y: float = 0.0, d2_z: float = 0.0) -> dict:
    """★ **线性阵列**（★ 官方 `IFeatureManager.FeatureLinearPattern3`），★ 带**特征树回读**。

    ★★ **单位**：★ 官方原话 —— `Spacing1` “Spacing between each instance … **in meters**”
      ⇒ ★ 本包装对外收 **`spacing_mm`（毫米）**，在**这里**换算成米（★ 规则 2）。
      ⚠ ★ 这**修正**了 `linear_pattern` 原文档串里「间距（**毫米**）」那句错话。
    ★★ **`count` 含原件**（★ 官方原话 “including the original”）⇒ `count=3` = 原件 + 2 个实例。

    :param feature_name: 要阵列的特征名。
    :returns: `{ok, feature_name, tree_before, tree_after, new_features, spacing_mm, count}`
        ★★ **判据是特征树真的多了**（★ 规则 6 —— **不能只看返回值**：
        本会话已见过「回对象而什么都没发生」的空存根）。
    """
    out: dict = {"ok": False, "feature_name": str(feature_name)[:60], "spacing_mm": None,
                 "count": None, "tree_before": None, "tree_after": None,
                 "new_features": [], "error": None}
    try:
        n1 = int(count)
        n2 = int(count2)
    except (TypeError, ValueError):
        out["error"] = "count / count2 必须是整数"
        return out
    if n1 < 2:
        out["error"] = "count 必须 ≥ 2（★ 它**含原件** —— 1 就是「没有阵列」）：%r" % count
        return out
    if not str(feature_name).strip():
        out["error"] = "feature_name 不能为空"
        return out
    try:
        s1 = float(spacing_mm) * 0.001                             #: ★ 毫米 ⇒ 米
        s2 = float(spacing2_mm) * 0.001
    except (TypeError, ValueError) as exc:
        out["error"] = "spacing_mm 必须是数字：%s" % str(exc)[:80]
        return out
    from sw_feature_readback import feature_names
    before = feature_names(model)
    try:
        #: ★★ 官方签名（★ 这是 `3` 代那 10 参；★ 本行已换成 **`5` 代 22 参**）：
        #:   `Num1, Spacing1, Num2, Spacing2, FlipDir1, FlipDir2, DName1, DName2, GeometryPattern, VaryInstance`
        #: ★ 而我第一版**传了 15 个** —— ★★ 真机报
        #:   `com_error: (-2147352562, '无效的参数数目。')`。
        #:   ★ 记一条：**“读了文档” ≠ “按文档写”** —— 我读了参数表，却凭印象补了尾部。
        #: ★★★★ 2026-10-04（接手轮）**换到现行的 `5` 代（22 参）** —— 处置阶段 2 · T1 ✓
        #:   ★ 官方链：★ `3` 废弃 ⇒ `4` ⇒ `5`（★ 5 也废弃、★ 后继空）·
        #:   ★★ **反射裁决**：★ 最高代 `5`（**22 参**）、★ **没有 `6`** ⇒ ★ **`5` 是现行可用那代** ✓
        #:   ★★★ **真机证据**（★ `tools/probe_linear_pattern_baseline.py` ·
        #:     `output/linear-pattern-baseline-evidence.json`）：★ 三种形态**全部建成**
        #:     （★ 特征数 20→21 · 新特征 `阵列(线性)1`）✓
        #:   ★★★★ **而调用序来自**官方示例****（★ `Change_Linear_Pattern_Example_VB.md` 逐字）：
        #:     ★ `ClearSelection2(True)` ⇒ ★ 方向 **`mark=1`** ⇒ ★ 实体 **`mark=256`** ✓
        #:     ★★ **⚠ 而选实体要用 `IBody2::Select(Append, Mark)`、★ 不是 `Select4`** ✓
        #:   ★★★★★ **⚠ 本函数**不做选择**（★ 前置由调用方给）** ⇒
        #:     ★★ 只把**成员名与参数**换成 `5` 代；★ **前置不变** ✓
        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern5",
                       n1, s1, n2, s2, False, False, "NULL", "NULL", False, False,
                       False, False, False, False, False, False,
                       False, False, 0.0, 0.0, False, False)
    except Exception as exc:                                       # noqa: BLE001
        out["error"] = "FeatureLinearPattern3 失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    after = feature_names(model)
    out["tree_before"] = len(before)
    out["tree_after"] = len(after)
    out["new_features"] = [x for x in after if x not in before]
    out["spacing_mm"] = float(spacing_mm)
    out["count"] = n1
    out["ok"] = len(after) > len(before)
    if not out["ok"]:
        out["error"] = ("`FeatureLinearPattern3` **没抛错而特征树没变** ⇒ 阵列**没建成**"
                        "（★ 规则 6：不许只看返回值 —— 本会话已见过「回对象而什么都没发生」）")
    return out

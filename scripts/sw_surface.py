"""SolidWorks 原生曲面建模接口封装（``IModeler.Create*Surface`` 家族）。

能力域
    域 7 · 曲面（本模块走**路线 A**：脚本直接造几何曲面）

本域存在**两条互补路线**，别混为一谈
------------------------------------
路线 A · 脚本造几何曲面（本模块实现）
    ``ISldWorks.GetModeler()`` → ``IModeler`` 的 19 个非指针 ``Create*Surface``。
    官方只提供 ``IModeler`` 这一套可直接调用的曲面创建 API。

路线 B · 界面创建 + 脚本参数化（官方示例主要演示的形态）
    用户在 SolidWorks 界面里选中面 → Insert ▸ Surface ▸ Radiate / Planar / Extend…
    脚本随后用两步把特征取回来做参数化::

        swFeat = (Feature)swSelMgr.GetSelectedObject6(1, -1)   # ① 从选区拿特征
        swData = (SurfaceRadiateFeatureData)swFeat.GetDefinition()  # ② 取定义
        swData.AccessSelections(swModel, Nothing)              # ③ 接管选区
        ... 读 / 改属性 ...
        swData.ReleaseSelectionAccess()                        # ④ 释放

    官方依据（``C:\\swapi\\examples``）：
        ``Create_Radiate_Surface_Example_CSharp.md``
        ``Create_Planar_Surface_Feature_Example_CSharp.md``
        ``Create_Trimmed_Surface_Feature_Example_CSharp.md``
        ``Access_Selections_Example_VB.md``
    唯一例外是裁剪面：``IFeatureManager.PostTrimSurface(Boolean)``
    **有脚本创建入口**（扫描 263 个方法的反射表，曲面类 Post* 只有这一个）。

    ⇒ 域 7 那 13 个 ``*FeatureData`` 接口**不是「无用」，而是路线 B 的载体**。
    早前依据「无任何接口返回它们」判定它们「不是创建入口」是对的，
    但由此推断「官方不用它们」是不对的 —— 本段即为更正。

路线 A 的官方接口族（全部经 interop DLL 元数据反射核对）
    ISldWorks.GetModeler()          -> Object（即 IModeler）
    IModeler                        -> 123 个成员，其中 19 个非 I 的 Create*Surface
    ISurface（82 成员）              -> 曲面查询
    本域那 13 个 *FeatureData         -> 路线 B 专用，本模块不封装

⚠ 路线 B 的官方入口只有「界面创建 + GetDefinition」，**没有脚本创建方法**
   （唯一例外 ``IFeatureManager.PostTrimSurface(Boolean)``）——
   本模块因此**不提供**那 13 个 FeatureData 的封装：能读能改的前提是
   用户先在界面里建好，本模块无从代劳。

官方接口族（全部经 interop DLL 元数据反射核对）
    ISldWorks.GetModeler()          -> Object（即 IModeler）
    IModeler                        -> 123 个成员，其中 19 个非 I 的 Create*Surface
    ISurface（82 成员）              -> 曲面查询
    本域那 13 个 *FeatureData         -> **仅用于编辑既有特征，本模块不提供入口**

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
   所有方法都需要调用方显式传入已连接的应用对象；本模块不建立连接、
   不调用 ``connect_solidworks()``、不启动 SolidWorks。

几何参数的单位说明
------------------
官方签名里半径/距离一律是 ``Double``，但**官方文档未在本机离线源中注明单位**。
本模块不做任何单位换算，原样透传，由调用方以 SI 米制为准——
按 AGENTS.md 铁律 5「查不到就说查不到」，此处不猜。
"""

from __future__ import annotations

from typing import Any

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务的工具层与能力层）
# 文件:   scripts/sw_surface.py —— 本文件自身
# 定位:   模块导出清单 __all__、几何公差常量 DEFAULT_TOLERANCE、
#         依赖解析的 import 块（沿用 scripts/sw_sheet_metal.py 的
#         「try: from .x import / except ImportError: from x import」模式，
#         见 AGENTS.md §三 对新增模块的硬性要求）。
# ⚠ DEFAULT_TOLERANCE = 1e-6 **不是官方常量**，是本项目既有实践取值
#   （与 scripts/sw_part.py 的几何比较容差同量级），故在此显式声明出处。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "SURFACE_CREATION_METHODS",
    "IMODELER_RUNTIME_AVAILABLE",
    "runtime_available",
    "require_runtime_available",
    "IMODELER_RUNTIME_UNAVAILABLE",
    "get_modeler",
    "create_planar_surface",
    "create_cylindrical_surface",
    "create_spherical_surface",
    "create_conical_surface",
    "create_toroidal_surface",
    "create_offset_surface",
    "create_extrusion_surface",
    "create_revolution_surface",
    "create_ruled_surface",
    "create_swept_surface",
    "create_bspline_surface",
    "create_coons_b_surface",
    "create_sheet_from_surface",
    "collect_surface_evidence",
]

#: 几何公差（米）。用于开口曲面缝合等需要容差的入口。
DEFAULT_TOLERANCE = 1e-6


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt  →  IModeler 段
# 定位:   本域全部 19 个**非指针** Create*Surface 方法的官方签名，
#         逐条照录，一字未改。本表既是签名依据，也是本模块的
#         「不可改动清单」——参数个数或顺序对不上即为缺陷。
# 查证:   对 sldworks.dll 的 1032 个接口做 GetMembers() 后筛出
#         以 Create 开头、非 I 前缀、以 Surface 结尾的成员，共 19 条。
# ⚠ 与本域 *FeatureData 接口的关系: 那 13 个 ISurface*FeatureData
#   在全程序集里**没有任何接口声明返回它们**，故不是创建入口，
#   本模块不提供其封装（详见模块 docstring「纠正一处此前的误判」）。
# ⚠ 指针版本 ICreate*Surface 一律不收录 —— 属官方限定的进程内非托管 C++
#   接口，pywin32 迟到绑定不可用。
# ⚠ 本表为静态反射结果，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SURFACE_CREATION_METHODS = {
    # 名称: (返回类型, 参数类型序列)
    "CreatePlanarSurface": ("Object", ("Object", "Object")),
    "CreatePlanarSurface2": ("Object", ("Object", "Object", "Object")),
    "CreateCylindricalSurface": ("Object", ("Object", "Object", "Double")),
    "CreateCylindricalSurface2": ("Object", ("Object", "Object", "Object", "Double")),
    "CreateSphericalSurface": ("Object", ("Object", "Double")),
    "CreateSphericalSurface2": ("Object", ("Object", "Object", "Object", "Double")),
    "CreateConicalSurface": ("Object", ("Object", "Object", "Double", "Double")),
    "CreateConicalSurface2": (
        "Object",
        ("Object", "Object", "Object", "Double", "Double"),
    ),
    "CreateToroidalSurface": (
        "Object",
        ("Object", "Object", "Object", "Double", "Double"),
    ),
    "CreateOffsetSurface": ("Object", ("Object", "Double")),
    "CreateExtrusionSurface": ("Object", ("Object", "Object")),
    "CreateRevolutionSurface": ("Object", ("Object", "Object", "Object", "Object")),
    "CreateRuledSurface": ("Object", ("Object", "Object", "Object")),
    "CreateSweptSurface": ("Object", ("Object", "Object")),
    "CreateBsplineSurface": ("Object", ("Object", "Object", "Object", "Object")),
    "CreateCoonsBSurface": ("Surface", ("Curve", "Curve", "Curve", "Curve", "Boolean")),
    "CreateSheetFromSurface": ("Object", ("Object", "Object")),
    "CreateLoftSurface": (
        "Object",
        (
            "Object",
            "Boolean",
            "Boolean",
            "Object",
            "Int32",
            "Int32",
            "Object",
            "Object",
            "Object",
            "Object",
            "Boolean",
            "Boolean",
            "Object",
            "Object",
            "Int32",
            "Int32",
            "Int32",
            "Int32",
        ),
    ),
    "CreateRuledSurfaceFromEdge": (
        "Int32",
        (
            "ModelDoc2",
            "Object",
            "Int32",
            "Double",
            "Boolean",
            "Boolean",
            "Boolean",
            "Double",
            "Boolean",
            "Double",
            "Double",
            "Double",
            "Boolean",
            "Object&",
        ),
    ),
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt  →  ISldWorks 段
# 定位:   官方同时提供两个取 Modeler 的入口：  Object   GetModeler()   ← Automation 友
#           好，Python 可用  Modeler  IGetModeler()  ← 指针版，进程内非托管 C++ 专用
#         本模块只走前者，与上游 capabilities.yaml 中
#         「默认优先同名非 I 方法」的路由约定一致。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_modeler(sw_app):
    """取 IModeler。本域全部创建入口都从这里出发。"""
    modeler = get_com_member(sw_app, "GetModeler")
    if modeler is None:
        raise RuntimeError(
            "ISldWorks.GetModeler() 返回 None：无法取得 IModeler，"
            "原生曲面创建入口不可用"
        )
    return modeler


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_sheet_metal.py::_create_from_definition（同批次产出的姊妹模块）
# 定位:   薄封装共用的「参数自检 → 调用 → 返回」骨架，沿用其集中式错误处理
#         的写法，而非在 14 个薄封装里各写一遍 try/except。
# 本模块特有: 本函数额外做**参数个数自检**——SURFACE_CREATION_METHODS 是照
#         官方反射抄的签名表，若调用方改错参数个数，在这里立刻抛出带方法名的
#         TypeError，而不是让 COM 报一个语焉不详的异常。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
#: 2026-10-01 真机实测**可取**的 `IModeler` 创建入口。
#  ⚠⚠ **「可取」不等于「调用一定成功」**（同批实测的另一个细微语义）：
#     `getattr` 拿到绑定方法，只是说明**成员可达**；
#     实际调用仍可能返回 `None`（参数不合法/模型上下文不满足）。
#     例：`CreateCylindricalSurface` 在名单里，但用 `origin=[0,0,0]` 调时返回 `None`，
#     而 `CreateSphericalSurface` 用同样风格的参数返回非 `None`。
#     **⇒ 判据只能是「返回非 None」，不能是「在可取名单里」。**
IMODELER_RUNTIME_AVAILABLE = frozenset(
    {
        "CreateCylindricalSurface",
        "CreateSphericalSurface",
        "CreateConicalSurface",
        "CreateToroidalSurface",
        "CreateArc",
    }
)

#: 2026-10-01 真机实测**取不到**（`getattr` 得 `None` ⇒ 调用会报含混的
#  `'NoneType' object is not callable`）。**这一条是确定的**：成员不可达。
IMODELER_RUNTIME_UNAVAILABLE = frozenset(
    {
        "CreatePlanarSurface",
        "CreateLine",
        "CreatePoint",
        "CreateBodyFromSurf",
        "CreateBsplineSurface",
    }
)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论，非第三方移植）
# 文件:   D:\AI\SW\probe_surface_array_shape.py（证据脚本）
# 定位:   **运行期可取性表** —— 2026-10-01 在活着的 `IModeler` 上逐个 `getattr` 实测。
#  ⚠⚠ 结论：本模块导出的 14 个创建入口里，**运行期只有 5 个可取**：
#       ✓ CreateCylindricalSurface / CreateSphericalSurface / CreateConicalSurface
#         / CreateToroidalSurface / CreateArc
#       ✗ **getattr 得 None**（调用会报 `'NoneType' object is not callable`）：
#         CreatePlanarSurface / CreateLine
#       ✗ **成员根本不存在**：CreatePoint / CreateBodyFromSurf / …
#       ✗ **服务器异常 `0x80010105`**：CreateBsplineSurface
#  ⇒ **「反射里有」≠「运行期调用得到」** —— 与本项目已知事实 11
#    （`OpenDoc6` 的 `[out] long` 在 makepy 代理下要绕）同类：**类型层与运行层会不一致**。
#  ⚠ 同批实测确定的另一件事：`Object` 型点/向量参数**五种包装全可用**
#    （裸 list / 裸 tuple / `VT_ARRAY|VT_R8` / `VT_ARRAY|VT_VARIANT` /
#    逐元素 VARIANT）—— pywin32 会自动把 list/tuple 转 SAFEARRAY。
#    ⇒ **不必强制调用方包 VARIANT**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 本表只覆盖**本机**实测到的成员；未逐个测的成员按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
#: dispatch-guard: exempt internal-helper
def _invoke(modeler, method: str, *args):
    """按 SURFACE_CREATION_METHODS 的签名表调用 Create*Surface。

    ⚠ 本函数做**两件事**：① **参数个数自检**（传错个数抛带方法名的 `TypeError`）；
    ② **返回值检查** —— 拿到 `None` 就抛带原因的 `RuntimeError`
    （见下方来源块：本族返回值真机实测**不可靠**，静默交给调用方是错的）。

    ⚠ 原文档串曾只写① —— **文档串必须与代码同步**。
    ⚠ 原本还写了：**参数个数自检**（签名表照官方反射抄的，传错个数立刻抛
    带方法名的 `TypeError`）。

    ⚠⚠ **可用性检查不在这里**（职责分离，2026-10-01 定的）：
    它由 `require_runtime_available(method)` 承担，**由调用方在调用前显式问**。
    原因：`tests/test_sw_surface_signature_contract.py` 用**桩 modeler** 验
    「参数按签名传」这个**形状**；守卫若放在本函数里，调用被拦就**验不了形状**。

    ⚠ **本文档串曾与代码不符**：第 13 轮撤掉可用性检查时没改文档串，
    它一度声称「做两层自检」。**⇒ 文档串必须与代码同步，否则它比没有更糟。**
    """
    if method not in SURFACE_CREATION_METHODS:
        raise KeyError(f"未登记的曲面创建方法: {method}")
    expected = len(SURFACE_CREATION_METHODS[method][1])
    if len(args) != expected:
        raise TypeError(
            f"{method} 官方签名为 {expected} 个参数，实际传入 {len(args)} 个"
        )
    surface = get_com_member(modeler, method, *args)
    # ⚠⚠ **返回 None = 什么都没建出来** ⇒ **抛带原因的错，不把 None 交给调用方**。
    #   真机实测（2026-10-01）：本族**返回值不可靠** —— 同一个调用在不同次之间
    #   会成功或返回 None（证据见 `probe_surface2_correct_arity.py` 与
    #   `probe_surface_generations.py`）。**换用官方 `*2` 新一代也**不解决**
    #   （实测同样返回 None）⇒ 唯一不依赖 COM 不稳定行为的改进就是**让失败可见**。
    #   **⇒ 静默失败是本项目反复踩的头号敌人（已知事实 8 / 30 / 40）。**
    if surface is None:
        raise RuntimeError(
            "%s 返回 None —— **什么都没建出来**。"
            "本族（`IModeler.Create*Surface`）真机实测**返回值不可靠**："
            "同一调用跨次会成功或返回 None，且官方 `*2` 新一代同样如此。"
            "⇒ **不要把它当成功**；换个思路（如先建草图/特征再转曲面），或重试一次再判。"
            % method
        )
    return surface


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论的**显式守卫**）
# 文件:   D:\AI\SW\probe_surface_array_shape.py（证据脚本）
# 定位:   **把「运行期可取性」做成显式守卫，而不是塞进 `_invoke`。**
#  ⚠⚠ 为什么职责分离（2026-10-01 的教训）：
#     第一版把检查写进 `_invoke` ⇒ **挡住了契约测试**
#     （`tests/test_sw_surface_signature_contract.py` 验的是「2 个参数传给
#      `CreatePlanarSurface`」这个**签名形状**，调用被拦就验不了）。
#     **⇒ `_invoke` 只管 arity（保持形状可验）；可用性由调用方显式问。**
#     MCP/声明层应当在**调用前**调 `require_runtime_available()`，
#     这样人拿到的是「成员不可达」而不是含混的 `'NoneType' object is not callable`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
#         ↑ 本块说明 `runtime_available` 与 `require_runtime_available` **两个**函数。
#         ⚠ 标记必须写成**裸的** `覆盖: 后续同级定义` —— 本项目第一次写时给它加了
#           markdown 粗体（`**后续同级定义**`），而 `check_provenance` 的正则是
#           `r"覆盖\s*[:：]\s*后续同级定义"`，`\s*` 匹配不到 `**` ⇒ **标记没被识别**，
#           表现为「一个 def 被覆盖、下一个没有被覆盖」这种看似矛盾的现象。
#           见 `scripts/check_provenance.py` 的 `GROUP_MARK`。
# ⚠ 名单只覆盖**本机实测**过的成员；未测的按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
def runtime_available(method: str) -> bool:
    """该方法在**本机实测**中是否可取（`True` = 可取；未实测的返回 `False`）。"""
    return method in IMODELER_RUNTIME_AVAILABLE


def require_runtime_available(method: str) -> None:
    """**调用前**的守卫：不可达就抛带原因的 `RuntimeError`。

    ⚠ 「可取」**不等于**「调用一定成功」—— `getattr` 拿到方法只说明**成员可达**；
    实际调用仍可能返回 `None`（参数不合法/模型上下文不满足）。
    **⇒ 真正的判据永远是「返回非 None」。**
    """
    if method in IMODELER_RUNTIME_AVAILABLE:
        return
    if method in IMODELER_RUNTIME_UNAVAILABLE:
        raise RuntimeError(
            "%s 在**本机运行期取不到**（`getattr` 得 None）—— 官方类型库里有它，"
            "但迟到绑定拿不到。本机实测可取的入口：%r。"
            "⚠ 「反射里有」≠「运行期调用得到」（2026-10-01 真机结论）。"
            % (method, sorted(IMODELER_RUNTIME_AVAILABLE))
        )
    raise RuntimeError(
        "%s **未在本机实测过**可用性 —— 不在可取名单也不在取不到名单里。"
        "先用 `probe_surface_array_shape.py` 的逐个 getattr 手法实测再决定（不猜）。"
        % method
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 定位:   下列 14 个薄封装逐一对应 SURFACE_CREATION_METHODS 的条目，
#         参数顺序与官方 Signature 行逐位一致，未做增删或调序。
#         它们不引入任何新逻辑，只是把「位置参数」变成「有名字的参数」，
#         避免调用方把两个 Double 传反。
# ⚠ 各方法返回 ``Object``（曲面），由调用方决定是否 CreateBody；
#   本模块**不自动建实体**——官方 CreateBody 的参数表本轮未核。
# 覆盖:   后续同级定义 —— 下列 14 个薄封装是同一个声明的整体，逐个贴块是噪声；
#         覆盖面精确到下一个来源块为止，不影响后面的其他声明。
# ⚠ 本组为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


def create_planar_surface(sw_app, point, normal):
    """由一点 + 法向创建平面。``CreatePlanarSurface(Object, Object)``"""
    require_runtime_available("CreatePlanarSurface")
    return _invoke(get_modeler(sw_app), "CreatePlanarSurface", point, normal)


def create_cylindrical_surface(sw_app, origin, axis, radius):
    """由原点 + 轴 + 半径创建圆柱面。``(Object, Object, Double)``"""
    require_runtime_available("CreateCylindricalSurface")
    return _invoke(
        get_modeler(sw_app), "CreateCylindricalSurface", origin, axis, float(radius)
    )


def create_spherical_surface(sw_app, center, radius):
    """由球心 + 半径创建球面。``CreateSphericalSurface(Object, Double)``"""
    require_runtime_available("CreateSphericalSurface")
    return _invoke(get_modeler(sw_app), "CreateSphericalSurface", center, float(radius))


def create_conical_surface(sw_app, origin, axis, half_angle, radius):
    """由原点 + 轴 + 半角 + 半径创建圆锥面。``(Object, Object, Double, Double)``"""
    require_runtime_available("CreateConicalSurface")
    return _invoke(
        get_modeler(sw_app),
        "CreateConicalSurface",
        origin,
        axis,
        float(half_angle),
        float(radius),
    )


def create_toroidal_surface(sw_app, origin, axis, center, major_radius, minor_radius):
    """创建圆环面。``(Object, Object, Object, Double, Double)``"""
    require_runtime_available("CreateToroidalSurface")
    return _invoke(
        get_modeler(sw_app),
        "CreateToroidalSurface",
        origin,
        axis,
        center,
        float(major_radius),
        float(minor_radius),
    )


def create_offset_surface(sw_app, surface, distance):
    """对既有曲面做偏置。``CreateOffsetSurface(Object, Double)``"""
    require_runtime_available("CreateOffsetSurface")
    return _invoke(get_modeler(sw_app), "CreateOffsetSurface", surface, float(distance))


def create_extrusion_surface(sw_app, profile, direction):
    """由轮廓 + 方向创建拉伸曲面。``CreateExtrusionSurface(Object, Object)``"""
    require_runtime_available("CreateExtrusionSurface")
    return _invoke(get_modeler(sw_app), "CreateExtrusionSurface", profile, direction)


def create_revolution_surface(sw_app, profile, axis, origin, angle):
    """由轮廓 + 轴 + 原点 + 角度创建旋转曲面。``(Object, Object, Object, Object)``"""
    require_runtime_available("CreateRevolutionSurface")
    return _invoke(
        get_modeler(sw_app), "CreateRevolutionSurface", profile, axis, origin, angle
    )


def create_ruled_surface(sw_app, curve_a, curve_b, continuity):
    """由两条曲线 + 连续性创建直纹面。``(Object, Object, Object)``"""
    require_runtime_available("CreateRuledSurface")
    return _invoke(
        get_modeler(sw_app), "CreateRuledSurface", curve_a, curve_b, continuity
    )


def create_swept_surface(sw_app, profile, path):
    """由轮廓 + 路径创建扫掠曲面。``CreateSweptSurface(Object, Object)``"""
    require_runtime_available("CreateSweptSurface")
    return _invoke(get_modeler(sw_app), "CreateSweptSurface", profile, path)


def create_bspline_surface(sw_app, control_points, weights, knots, degree):
    """由控制点 / 权重 / 节点 / 次数创建 B 样条曲面。``(Object, Object, Object, Object)``"""
    require_runtime_available("CreateBsplineSurface")
    return _invoke(
        get_modeler(sw_app),
        "CreateBsplineSurface",
        control_points,
        weights,
        knots,
        degree,
    )


def create_coons_b_surface(sw_app, curve_v, curve_u, curve_v2, curve_u2, closed):
    """由四条边界曲线创建 Coons B 样条面。``(Curve, Curve, Curve, Curve, Boolean)``"""
    require_runtime_available("CreateCoonsBSurface")
    return _invoke(
        get_modeler(sw_app),
        "CreateCoonsBSurface",
        curve_v,
        curve_u,
        curve_v2,
        curve_u2,
        bool(closed),
    )


def create_sheet_from_surface(sw_app, surface, tolerance):
    """由曲面生成薄片实体（加厚）。``CreateSheetFromSurface(Object, Object)``"""
    require_runtime_available("CreateSheetFromSurface")
    return _invoke(
        get_modeler(sw_app), "CreateSheetFromSurface", surface, float(tolerance)
    )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
# 定位:   证据回读只使用已核实的**属性**成员（ISurface 族 82 成员）：  ISurface : get_
#           Identity / IsPeriodic / IsRational / Area 等
#         涉及面/边/顶点的读取走 IBody2 / IFace2 / IEdge / IVertex，
#         同样只取属性，不臆造方法名。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_surface_evidence(sw_app) -> dict[str, Any]:
    """回读 Modeler 可用性与已登记的创建入口，作为可审计证据。"""
    modeler = get_modeler(sw_app)
    return {
        "has_modeler": modeler is not None,
        "registered_creation_methods": sorted(SURFACE_CREATION_METHODS),
        "registered_count": len(SURFACE_CREATION_METHODS),
        "pointer_variants_available": False,
        "pointer_variants_note": (
            "ICreate*Surface 属官方限定的进程内非托管 C++ 接口，"
            "pywin32 迟到绑定不可用，故未收录"
        ),
    }

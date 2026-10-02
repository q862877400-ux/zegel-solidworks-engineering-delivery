"""SolidWorks 现代外观（RenderMaterial / Appearance）封装。

能力域
    域 12 · 配置·材料·自定义属性（外观部分）

为什么单独成模块（而不是并进 ``sw_appearance.py``）
------------------------------------------------
``scripts/sw_appearance.py`` 走的是**旧式外观路线**：
``MaterialPropertyValues``（颜色/环境光/高光的裸值数组）。
而本模块走的是**现代路线**：``IModelDocExtension.CreateRenderMaterial`` 建对象
→ 设 ``IRenderMaterial`` 属性 → ``AddRenderMaterial`` 应用。

官方接口族（全部经 interop DLL 元数据反射核对）
    IModelDocExtension
        RenderMaterial CreateRenderMaterial(String Name)
        Boolean       AddRenderMaterial(RenderMaterial, Int32& Count)
        Boolean       AddDefaultRenderMaterial(RenderMaterial, Int32& Count)
        Boolean       AddDisplayStateSpecificRenderMaterial(
                          RenderMaterial, Int32, Object, Int32&, Int32&)
        Boolean       DeleteRenderMaterial(Int32, Boolean)
        Object        GetRenderMaterials() / GetRenderMaterials2(Int32, Object)
        Int32         GetRenderMaterialsCount() / GetRenderMaterialsCount2(Int32, Object)
        RenderMaterial GetMaterial(Int32, String)
        Void          UpdateRenderMaterialsInSceneGraph(Boolean)
        IAppearanceSetting GetAppearanceSetting()
    IComponent2
        Object GetRenderMaterials() / GetRenderMaterials2(Int32, Object)
        Int32  GetRenderMaterialsCount() / GetRenderMaterialsCount2(Int32, Object)
    IRenderMaterial     185 个成员（外观属性，get/set 成对）
    IMaterialVisualPropertiesData  10 个成员

⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）。
   所有方法都需要调用方显式传入已连接/已打开的文档；本模块不建立连接。
"""
from __future__ import annotations

from typing import Any

try:
    from .sw_connect import out_i4, get_com_member, set_com_member
except ImportError:
    #: ★★ 2026-10-01（轮 319）：**这条 fallback 原本少了 `set_com_member`** ——
    #:   而本机走的**就是**这条（`scripts` 不是包）⇒ 修完"设属性"的 11 处之后
    #:   立刻报 `NameError: name 'set_com_member' is not defined`。
    #:   ★ 教训：两条 import 分支的**名字集合必须一致**（★ 否则"只在 package 模式能跑"）。
    from sw_connect import out_i4, get_com_member, set_com_member

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_render_material.py —— 本文件自身
# 定位:   模块导出清单、属性名常量与预设表。
# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（成员级签名与逐跳推导），此处声明覆盖范围以免逐个贴块。
# ⚠ RENDER_MATERIAL_PRESETS 的**数值是中性占位，不是官方推荐值** ——
#   官方未给区间说明（取值依赖具体材质定义），故只登记「官方确实有这些
#   Double 属性」这一事实，取值不冒充官方推荐。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
__all__ = [
    "RENDER_MATERIAL_PRESETS",
    "get_extension",
    "create_render_material",
    "add_render_material",
    "refresh_scene_graph",
    "list_render_materials",
    "delete_render_material",
    "apply_visual_properties",
    "collect_appearance_evidence",
]

# 外观属性的合法值域。两套官方源都没有给区间说明（依赖材质定义），
# 故此处只登记官方文档确认存在的属性名，不猜数值范围。
# ⚑ 名称更正: 本表初稿写的是 `Shininess`（凭对 SolidWorks 外观 API 的印象），
#   但 `Shininess` **在官方反射清单里不存在** —— 由 audit_call_arity.py 报
#   「查不到」当场抓出。反射确认的 Double 属性只有 7 个：
#   Ambient / Brightness / Diffuse / Emission / Roughness / Specular / Transparency
#   镜面锐度对应的是 **Roughness**，不是 Shininess。已改。
#   ⇒ 这条本身就是「不凭记忆写 API」的又一处实证。
RENDER_MATERIAL_PRESETS: dict[str, dict[str, float]] = {
    "matte": {"ambient": 0.25, "diffuse": 0.75, "specular": 0.10,
              "roughness": 0.60, "transparency": 0.0, "emission": 0.0},
    "glossy": {"ambient": 0.25, "diffuse": 0.80, "specular": 0.60,
               "roughness": 0.20, "transparency": 0.0, "emission": 0.0},
    "metallic": {"ambient": 0.30, "diffuse": 0.70, "specular": 0.90,
                 "roughness": 0.10, "transparency": 0.0, "emission": 0.0},
}


# 覆盖:   全文件 —— 本模块是一个内聚的新增能力单元；下方各函数另附更精确的
#         来源块（成员级签名与逐跳推导），此处声明覆盖范围以免逐个贴块。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_render_material.py —— 本文件自身
# 定位:   模块导出清单、属性名常量与预设表。
# ⚠ RENDER_MATERIAL_PRESETS 的**数值是中性占位，不是官方推荐值** ——
#   官方未给区间说明（取值依赖具体材质定义），故只登记「官方确实有这些
#   Double 属性」这一事实，取值不冒充官方推荐。
# ⚠ 本模块为静态签名比对后新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_sheet_metal.py::BaseFlangeSpec）
# 定位:   外观参数的数据类，沿用「冻结 dataclass + validate() 在进入 COM 前
#         拒绝无效参数」的既有形状（AGENTS.md §三 对新增模块的硬性要求）。
# ⚠ 取值范围未查到官方依据，故只拒负值与超出 0..1 的显式误用，
#   不做更细的工艺校验。
# ⚠ 本类为照既有模式新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
from dataclasses import dataclass, field  # noqa: E402


@dataclass(frozen=True)
class RenderMaterialSpec:
    """@brief 现代外观（RenderMaterial）参数，取值按官方 Double 属性透传。

    ★★★★ 2026-10-02（轮 373）**`file_name` 不是可选项** —— 真机实测（四轮收窄，见 known-facts 287→290）：
    ```
    CreateRenderMaterial("名字")            ⇒ 回对象，而 **`FileName` 是空字符串**
    set FileName = "<真实 .p2m>"            ⇒ 回读确认 ✓
    AddDisplayStateSpecificRenderMaterial   ⇒ true · id1 = 6
    GetMaterialIds(out, out)                ⇒ **id1 = 6**（★ 正确的取 ID 入口；
                                               `MaterialID` 属性自 SW2011 起已废弃、恒 0）
    GetRenderMaterialsCount2(2, names)      ⇒ **2**   ← ★ 清单**有内容了**
    ```
    ⇒ ★★ **不设 `FileName` 时**：`Add…` 也回 true、`GetLinkedDisplayStates` 也显示"已链接"，
      ★ **而清单恒空、`GetMaterialIds` 回 None** ⇒ ★★★ 一个"看起来成功、实际不算数"的外观。
    ⇒ 所以 `file_name` 是**必需**字段（★ 空值由 `validate()` 明确报错）——
      ★ **宁可报错，也不静默造一个不会被收录的外观**。
    """

    ambient: float = 0.25
    diffuse: float = 0.75
    specular: float = 0.10
    roughness: float = 0.60
    transparency: float = 0.0
    emission: float = 0.0
    #: ★ 外观的 `.p2m` 材质文件路径（★ **必需** —— 空值会被 `validate()` 拒掉）
    file_name: str = ""
    extra: dict[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        for name in ("ambient", "diffuse", "specular", "roughness",
                     "transparency", "emission"):
            value = float(getattr(self, name))
            if value < 0.0:
                raise ValueError(f"{name} 不能为负：{value}")
        for name, value in (self.extra or {}).items():
            if float(value) < 0.0:
                raise ValueError(f"extra[{name}] 不能为负：{value}")
        #: ★★ 没有 `.p2m` 的外观**不会被收录**（真机证据见类文档串）
        if not str(self.file_name or "").strip():
            raise ValueError(
                "file_name 不能为空 —— 外观必须绑定一个 `.p2m` 材质文件，"
                "否则 `AddDisplayStateSpecificRenderMaterial` 会「回 true 而清单不增」"
                "（★ 真机实测；见 known-facts 事实 290）。"
                "SW 自带的材质文件在 `<install>\\data\\graphics\\Materials\\**\\*.p2m`。")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IModelDocExtension 段 + IRenderMaterial 段
# 定位:   现代外观的创建与属性装配。官方签名：
#           RenderMaterial CreateRenderMaterial(String Name)      ← 1 参
#           Boolean       AddRenderMaterial(RenderMaterial, Int32& Count)  ← 2 参
#           Boolean       AddDefaultRenderMaterial(RenderMaterial, Int32& Count)
#           IRenderMaterial 上确认为 Double 的属性（本模块用到的 7 个）：
#             Ambient / Brightness / Diffuse / Emission / Roughness /
#             Specular / Transparency
#             全部 get/set 成对，**无 Initialize 成员**，故只设属性。
# ⚑ 曾误写 Shininess（凭印象），反射清单中**无此成员**，
#   由 audit_call_arity.py 报「查不到」抓出。镜面锐度用 Roughness。
# ⚠ AddRenderMaterial 末位是 Int32& 出参，pywin32 迟到绑定下不保证回写，
#   故本模块**不以它作成败判据**，只透传返回值（见 AGENTS.md §六 事实 11 同源问题）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def get_extension(model):
    """取 IModelDocExtension（属性，不是方法）。"""
    extension = get_com_member(model, "Extension")
    if extension is None:
        raise RuntimeError("IModelDoc2.Extension 为 None：外观接口不可用")
    return extension


def create_render_material(model, name: str, spec: RenderMaterialSpec):
    """创建外观定义对象 ``IRenderMaterial``，**尚未应用**到文档。"""
    spec.validate()
    extension = get_extension(model)
    material = get_com_member(extension, "CreateRenderMaterial", str(name))
    if material is None:
        raise RuntimeError(f"CreateRenderMaterial({name!r}) 未返回对象")
    #: ★★★★ 2026-10-02（轮 373）**先绑 `.p2m`** —— 没有它，后面 `Add…` 会「回 true 而清单不增」。
    #:   ★ 真机证据（四轮收窄，known-facts 287→290）：设了 `FileName` 之后
    #:   `GetMaterialIds` 才回 `id1=6`、`GetRenderMaterialsCount2` 才回 **2**；
    #:   而不设时两者分别是 `None` 与 `0`（★ 而 `Add…` 两种情况下**都回 true**）。
    set_com_member(material, "FileName", str(spec.file_name))
    set_com_member(material, "Ambient", float(spec.ambient))
    set_com_member(material, "Diffuse", float(spec.diffuse))
    set_com_member(material, "Specular", float(spec.specular))
    set_com_member(material, "Roughness", float(spec.roughness))
    set_com_member(material, "Transparency", float(spec.transparency))
    set_com_member(material, "Emission", float(spec.emission))
    # extra 里的属性名由调用方给，必须已核对存在（IRenderMaterial 有 185 个成员）
    for key, value in (spec.extra or {}).items():
        #: ★★★★ 2026-10-02（轮 367）**这一处漏了**：本轮之前这里是
        #:   `get_com_member(material, str(key), float(value))` —— ★★ **那是"取或调"**
        #:   （★ 事实 227）⇒ **属性值不是可调用对象** ⇒ `TypeError: 'float' object is not callable`。
        #: ★ 前人（轮 319）修了 **11 处**同类，**而这一处漏了** —— ★ 与 `add_force` / `add_torque`
        #:   那次（轮 349：修 `add_torque` 时漏了 `add_force`）**同一个形态**：
        #:   ★★ **"修了一处、漏了同类"**。
        set_com_member(material, str(key), float(value))
    return material


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt → IModelDocExtension 段
# 定位:   官方调用序列的收尾两步：
#           1) Boolean AddRenderMaterial(RenderMaterial, Int32& Count)  ← 应用
#           2) Void   UpdateRenderMaterialsInSceneGraph(Boolean)       ← 刷新场景图
#         两者是 ApplyRenderMaterial 的组成部分，与 CreateRenderMaterial 配套。
# ⚠ 末位 Int32& 出参不保证回写，故不据此判成败（见 create_render_material 的说明）。
# ⚠ UpdateRenderMaterialsInSceneGraph 的 Boolean 语义未查到
#   （两套官方源都未给参数说明），故默认传 True 并在此显式标注为待确认。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def add_render_material(model, material) -> bool:
    """把外观对象应用到文档，并刷新场景图。返回 AddRenderMaterial 的原始返回值。"""
    if material is None:
        raise ValueError("material 为 None：须先由 create_render_material 创建")
    extension = get_extension(model)
    result = get_com_member(extension, "AddRenderMaterial", material, out_i4())
    refresh_scene_graph(model)
    return bool(result)


def refresh_scene_graph(model, update: bool = True):
    """刷新场景图，让外观变化可见。"""
    extension = get_extension(model)
    return get_com_member(extension, "UpdateRenderMaterialsInSceneGraph", bool(update))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IModelDocExtension 段 + IComponent2 段
# 定位:   外观清单读取。官方签名（两处都提供，优先用文档级）：
#           IModelDocExtension : Int32  GetRenderMaterialsCount()
#                                : Object GetRenderMaterials()
#                                : RenderMaterial GetMaterial(Int32, String)
#                                : Boolean DeleteRenderMaterial(Int32, Boolean)
#           IComponent2        : Int32  GetRenderMaterialsCount()
#                                : Object GetRenderMaterials()
#   ⚠ 注意 GetMaterial 的两个参数在反射清单里是 (Int32, String)，
#     语义（配置索引? 外观名?）两套官方源均未说明，故本模块只透传不解释。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def list_render_materials(model) -> list[Any]:
    """列出文档当前的外观定义对象。"""
    extension = get_extension(model)
    count = int(get_com_member(extension, "GetRenderMaterialsCount") or 0)
    materials = get_com_member(extension, "GetRenderMaterials")
    items = list(materials) if isinstance(materials, (list, tuple)) else []
    return items[:count] if count else items


def delete_render_material(model, index: int, cascade: bool = False) -> bool:
    """按索引删除外观定义。"""
    extension = get_extension(model)
    return bool(get_com_member(extension, "DeleteRenderMaterial",
                               int(index), bool(cascade)))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt
#           → IMaterialVisualPropertiesData 段
# 定位:   显示状态里的「材质可视化属性」。官方签名（**全部是属性，无方法**）：
#           Boolean  ApplyAppearance / AdvancedGraphics / RealView / BlendColor /
#                    ApplyMaterialColorToPart / ApplyMaterialHatchToSection
#           Double   Angle / Scale2
# ⚑ 名称歧义提示: 该接口的 `get_ApplyAppearance()` 读起来像方法，
#   但反射清单里它是 `Boolean get_ApplyAppearance()` —— **属性**。
#   迟到绑定下加括号调用会 TypeError（见 AGENTS.md §六 事实 4）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def apply_visual_properties(
    data,
    *,
    apply_appearance: bool | None = None,
    advanced_graphics: bool | None = None,
    real_view: bool | None = None,
    blend_color: bool | None = None,
    apply_material_color_to_part: bool | None = None,
    apply_material_hatch_to_section: bool | None = None,
    angle: float | None = None,
    scale2: float | None = None,
):
    """装配 ``IMaterialVisualPropertiesData``（显示状态里的材质可视化）。"""
    if data is None:
        raise ValueError("data 为 None：须先取得 IMaterialVisualPropertiesData")
    # 显式逐项赋值而非 mapping 循环：循环里的属性名是变量，
    # 静态签名审计与 family-coverage 都无法归因，会让这一族
    # 一直显示「未触及」—— **代码写了但工具看不见**。显式写同时更好读。
    if apply_appearance is not None:
        set_com_member(data, "ApplyAppearance", bool(apply_appearance))
    if advanced_graphics is not None:
        set_com_member(data, "AdvancedGraphics", bool(advanced_graphics))
    if real_view is not None:
        set_com_member(data, "RealView", bool(real_view))
    if blend_color is not None:
        set_com_member(data, "BlendColor", bool(blend_color))
    if apply_material_color_to_part is not None:
        get_com_member(data, "ApplyMaterialColorToPart",
                       bool(apply_material_color_to_part))
    if apply_material_hatch_to_section is not None:
        get_com_member(data, "ApplyMaterialHatchToSection",
                       bool(apply_material_hatch_to_section))
    if angle is not None:
        set_com_member(data, "Angle", float(angle))
    if scale2 is not None:
        get_com_member(data, "Scale2", float(scale2))
    return data


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（scripts/sw_sheet_metal.py::sheet_metal_evidence）
# 定位:   证据回读，沿用「只取已核实属性、不臆造方法」的写法。
#         读取的属性全部是 IRenderMaterial 上确认为 Double 的那 6 个。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def collect_appearance_evidence(model) -> dict[str, Any]:
    """回读文档外观清单与其主要参数，形成可审计证据。"""
    materials = list_render_materials(model)
    rows = []
    for material in materials:
        rows.append({
            "ambient": float(get_com_member(material, "Ambient") or 0.0),
            "diffuse": float(get_com_member(material, "Diffuse") or 0.0),
            "specular": float(get_com_member(material, "Specular") or 0.0),
            "roughness": float(get_com_member(material, "Roughness") or 0.0),
            "transparency": float(get_com_member(material, "Transparency") or 0.0),
            "emission": float(get_com_member(material, "Emission") or 0.0),
        })
    return {
        "appearance_count": len(rows),
        "appearances": rows,
        "has_appearance": bool(rows),
    }

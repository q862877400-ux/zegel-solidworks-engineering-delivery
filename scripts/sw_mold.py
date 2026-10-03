"""
模具域（Mold Design）—— 分型线 / 分型面 / 补孔面 / 型芯型腔分割 / 拔模分析 / 底切检测。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   Eduardof0nt/Solidworks-MCP-Server  (MIT License, Copyright (c) 2026 Eduardo Font Cruz)
# 文件:   该仓库的 sw_client.py —— `parting_line` / `shut_off_surface` 两个方法；
#         server.py 里对应 `sw_parting_line` / `sw_shut_off_surface` 两个工具。
#
# ⚠⚠ **来源的方法名在官方反射里两个都查不到**（核过三源）：
#
#     来源写的                     官方真名（本模块采用）
#     --------------------------    ------------------------------------------------------
#     InsertPartingLines            InsertMoldPartingLine(Boolean)
#     InsertShutOffSurfaces         InsertMoldShutOffSurface()
#
#   ⇒ 该来源系统性使用不存在的方法名（焊件域 4/5 错、模具域 2/2 错）。
#     它 0 个测试文件、未声明验证环境，与 AGENTS.md 已知事实 18 的记录一致。
#     缺陷明细与可复核命令：`D:\\AI\\SW\\_raw\\source-defects\\Eduardof0nt.md`。
#
#   **本模块引用它的思路**（模具域该做「分型线 + 补孔面」这两个动作），
#   **签名一律照出厂反射**（铁律 4）；并照反射**补全**模具族的其余常用入口
#   （分型面 / 型芯型腔分割 / 拔模分析 / 底切检测），来源未覆盖这些。
#
# 官方签名依据: 全部来自 IFeatureManager / IModelDoc2（反射清单逐条核过）：
#         InsertMoldPartingLine(Boolean)
#         InsertMoldPartingSurface(Int32, Boolean, Boolean, Double, Double, Int32, Double, Boolean)
#         InsertMoldShutOffSurface()
#         InsertMoldCoreCavitySolids(Double, Double, Boolean, Double)
#         MoldDraftAnalysis(Double, Int32, Object, Int32)
#         MoldUndercutDetect(Int32, Int32, Boolean, Double, Double, Double)
#         GetPartingLinesCount / GetPartingSurfacesCount / GetCavitySurfacesCount /
#         GetCoreSurfacesCount；get_/set_PartingType、get_/set_CoreCavitySplit
# 许可:   本仓库 MIT；来源 MIT，版权声明见 THIRD-PARTY-NOTICES.md。
# ⚠ **未在本机实测**（铁律 2）：模具设计需要具体选面与拔模方向参考，
#   本模块只做签名对齐与契约测试 ⇒ capabilities.yaml 的 level 只能标 `stitched`。
# ⚠ **多个参数语义查不到**（CHM 无这些方法的独立说明页、`C:\\swapi` 未收录、
#   来源也未提供）⇒ 按铁律 5 **不猜**，逐个在 docstring 里标注「未查证」。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_mold.py —— 本文件（**轮 145 的命名迁移**）。
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

from __future__ import annotations

try:
    from .sw_connect import get_com_member, call_com_member, set_com_member
except ImportError:
    from sw_connect import get_com_member, call_com_member, set_com_member
__all__ = [
    "insert_parting_line",
    "insert_parting_surface",
    "insert_shut_off_surface",
    "insert_core_cavity_solids",
    "mold_draft_analysis",
    "mold_undercut_detect",
    "mold_evidence",
]


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   Eduardof0nt/Solidworks-MCP-Server (MIT) + SolidWorks 官方 API 签名（纯元数据反射）
# 文件:   scripts/sw_mold.py 的 insert_parting_line
# 定位:   IFeatureManager.InsertMoldPartingLine(Boolean)。来源写的是 `InsertPartingLines`
#         —— **查不到**（见模块头与来源缺陷记录）。官方另有只读的 `IGetPartingLines`
#         与属性 `PartingLines`，但**创建**入口只有这一个。
# 官方签名依据: Feature InsertMoldPartingLine(Boolean)
# 许可:   本仓库 MIT。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────
def insert_parting_line(model, *, draft_analysis: bool = True):
    """插入**分型线**。

    调用前须由调用方选好**拔模方向参考**（边线/基准面/轴）——
    官方在未选时会返回 None。

    :param draft_analysis: 官方唯一参数（``Boolean``）。**语义未查证**：
        按方法名推测是「是否同时做拔模分析」，但反射只给类型、CHM 无说明
        ⇒ 默认 True（与来源示例的调用意图一致：它先设拔模角再建分型线）。
    :returns: 新建 Feature 的名字。
    :raises RuntimeError: 返回 None（常见原因：未选拔模方向参考）。
    """
    fm = get_com_member(model, "FeatureManager")
    feat = get_com_member(fm, "InsertMoldPartingLine", bool(draft_analysis))
    if feat is None:
        raise RuntimeError(
            "InsertMoldPartingLine 返回 None —— 常见原因：未选拔模方向参考"
        )
    return get_com_member(feat, "Name")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（纯元数据反射）；来源未覆盖此项
# 文件:   scripts/sw_mold.py 的 insert_parting_surface 等
# 定位:   IFeatureManager 的模具族其余入口。**署名归本项目自身**（照反射补，来源未覆盖）。
# 官方签名依据: 见模块头「官方签名依据」段逐条
# 许可:   本仓库 MIT。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────
def insert_parting_surface(model, *, surface_type: int = 0, flip: bool = False,
                           use_trim: bool = False, distance: float = 0.0,
                           angle: float = 0.0, option: int = 0,
                           tolerance: float = 0.0, alternate: bool = False):
    """插入**分型面**（8 参，全部照官方签名位置）。

    ⚠ **8 个参数里只有 3 个的语义可推断**（`distance`/`angle`/`tolerance`
    按名字是长度与角度），其余 5 个（`surface_type` / `flip` / `use_trim` /
    `option` / `alternate`）**语义未查证** ⇒ 默认值属待验证，不据此认为正确。

    :returns: 新建 Feature 的名字。
    :raises RuntimeError: 返回 None（常见原因：未先建分型线，或未选面）。
    """
    fm = get_com_member(model, "FeatureManager")
    # 位置严格照官方：Int32, Boolean, Boolean, Double, Double, Int32, Double, Boolean
    feat = get_com_member(
        fm, "InsertMoldPartingSurface",
        int(surface_type),      # 1 Int32 未查证
        bool(flip),             # 2 Boolean 未查证
        bool(use_trim),         # 3 Boolean 未查证
        float(distance),        # 4 Double
        float(angle),           # 5 Double
        int(option),            # 6 Int32 未查证
        float(tolerance),       # 7 Double
        bool(alternate),        # 8 Boolean 未查证
    )
    if feat is None:
        raise RuntimeError(
            "InsertMoldPartingSurface 返回 None —— 常见原因：未先建分型线，或未选面"
        )
    return get_com_member(feat, "Name")


def insert_shut_off_surface(model):
    """**自动**在孔洞处创建补孔面（shut-off surface）。零参。

    来源写的是 `InsertShutOffSurfaces` —— **查不到**；官方是**单数**且零参。

    :returns: 新建 Feature 的名字。
    :raises RuntimeError: 返回 None（常见原因：没有需要补的孔，或未建分型线）。
    """
    fm = get_com_member(model, "FeatureManager")
    feat = call_com_member(fm, "InsertMoldShutOffSurface")
    if feat is None:
        raise RuntimeError(
            "InsertMoldShutOffSurface 返回 None —— 常见原因：无待补孔洞，或未先建分型线"
        )
    return get_com_member(feat, "Name")


def insert_core_cavity_solids(model, *, scale: float = 0.0, thickness: float = 0.0,
                              flip: bool = False, offset: float = 0.0):
    """由**分型面**切出型芯与型腔实体（4 参）。

    ⚠ 4 个参数的**语义全部未查证**（反射只给类型 Double, Double, Boolean, Double）。
    按方法名推测：第 1 参是缩放、第 2 参是壁厚、第 4 参是偏置 —— **属推测，不据此认为正确**。

    :returns: 新建 Feature 的名字。
    :raises RuntimeError: 返回 None（常见原因：未建分型面）。
    """
    fm = get_com_member(model, "FeatureManager")
    feat = get_com_member(fm, "InsertMoldCoreCavitySolids",
                          float(scale), float(thickness), bool(flip), float(offset))
    if feat is None:
        raise RuntimeError(
            "InsertMoldCoreCavitySolids 返回 None —— 常见原因：未先建分型面"
        )
    return get_com_member(feat, "Name")


def mold_draft_analysis(model, *, draft_angle_deg: float, analysis_type: int = 0,
                        colors=None, option: int = 0):
    """**拔模分析**（4 参）。官方 `IModelDoc2.MoldDraftAnalysis`，**返回 `Void`**。

    :param draft_angle_deg: **参考拔模角**（官方 `Angle`，度；官方未写单位，按"拔模角"惯例按度）。
    :param analysis_type: 官方 `Options` —— `swDraftAnalysisOptions_e`（⚠ 具体枚举值**未逐条查证**）。
    :param colors: 官方 `Colors` —— **4 个颜色的数组**（正面拔模 / 负面拔模 / 无拔模 / 跨面），可传 `None`。
    :param option: 官方 `Shows` —— `swDraftAnalysisShow_e`（⚠ 具体枚举值**未逐条查证**）。

    :returns: ⚠ **官方是 `Void` ⇒ 没有返回码**。但**真机实测**（轮 178）pywin32 对 `Void`
        调用**回的是 `bool`（`True`）** ⇒ 本函数**原样返回**它。
        ★★ **不得把那个 `True` 当成"成功标志"** —— 它只是 COM 调用的**通用回执**，
        与拔模分析的**结果无关**（官方没给任何返回码）。
        ⚠⚠ **2026-10-01（轮 178）更正**：本函数原先写「返回码为 `Int32`，非 0 不一定是失败」——
        **整句都是错的**（官方 `Void`）。
    """
    #: ⚠⚠⚠ **2026-10-01（轮 178）更正两处 —— 一处**对象错**、一处**文档写反****：
    #: ```
    #:   ① **对象错**：本函数原先 `fm = get_com_member(model, "FeatureManager")` 再取
    #:      `MoldDraftAnalysis` —— ⚠ 真机实测 `IFeatureManager.MoldDraftAnalysis`
    #:      ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**
    #:      ★ 官方两源一致：**它在 `IModelDoc2` 上**
    #:        · 反射：`Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（在 IModelDoc2 段）
    #:        · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`：`IModelDoc2.MoldDraftAnalysis`
    #:   ② **返回类型写反**：原 docstring 说「返回码为 ``Int32``，由调用方判断」——
    #:      ⚠ 官方是 **`Void`** ⇒ **根本没有返回码**（"非 0 不一定是失败"那句**无从谈起**）。
    #: ```
    #: ⇒ ★ 这是靠 `scripts/check_member_owner_interface.py` **静态抓出来**的（轮 177），
    #:   并**真机核对**过（反射 / 真机否定 / 真机肯定，三条独立证据）。
    #: ⚠ **本函数仍可能弹模态框**（与 `MoldUndercutDetect` 同族）：未定义拔模方向 / 无实体时
    #:   官方会弹「此拔模方向尚未定义。」⇒ **调用方必须配 `settle_residual_dialogs` 兜底**。
    return get_com_member(model, "MoldDraftAnalysis",
                          float(draft_angle_deg), int(analysis_type), colors, int(option))


def mold_undercut_detect(model, *, col_undercut: int = 0, col_base: int = 0,
                         b_coord_input: bool = True, dx: float = 0.0,
                         dy: float = 0.0, dz: float = 1.0):
    """**底切检测**（官方 `IFeatureManager.MoldUndercutDetect`，6 参，返回 `Void`）。

    ★★ **2026-10-01（轮 167）按官方 md 的参数名与语义**（旧版参数名与官方**全不对应**）：
    ```
      Int32  ColUndercut   —— 某个方向上不可见、构成底切的面的**颜色**（COLORREF）
      Int32  ColBase       —— 不构成底切的面（除底切面外的全部）的**颜色**
      bool   BCoordInput   —— ★ **True = 启用坐标输入来指定拉拔方向**
      Double Dx/Dy/Dz      —— ★ **拉拔方向**的三个分量（仅当 `BCoordInput=True` 时生效）
    ```
    ⚠⚠⚠ **为什么旧版会弹模态框**（轮 167 根因）：
    旧签名是 `(direction, option, include_hidden, a, b, c)`，第 3 位传的是
    `include_hidden=False` —— 那**恰好落在官方第 3 参 `BCoordInput` 上** ⇒
    **"不启用坐标输入"** ⇒ SolidWorks 改用**模型自己已定义的拉拔方向**；
    而**空零件/未定义方向的零件上根本没有** ⇒ 弹「**此拔模方向尚未定义。**」且**卡住会话**。
    ⇒ ★ **根因解决**：默认 **`b_coord_input=True` + 非零方向 `(0,0,1)`**
      ⇒ **不依赖模型已定义方向** ⇒ **从根上不弹框**。

    :raises ValueError: `b_coord_input=True` 而方向**全零** ——
        零向量等于"没给方向"，会退回弹框那条路，故**在发调用之前就拒**（不硬编码、不静默）。
    :returns: ``None``（官方是 ``Void``）。⚠ **检测结果不在返回值里**（如何取**仍未查证**）。
    """
    if b_coord_input and not any((float(dx), float(dy), float(dz))):
        raise ValueError(
            "b_coord_input=True 但拉拔方向是**零向量** (0,0,0) —— "
            "零向量不等于「给了方向」，SolidWorks 会退回「用模型已定义方向」那条路，"
            "而在**未定义方向**的零件上会**弹模态框并卡住会话**。"
            "⇒ 请给一个**非零**方向（如默认的 (0,0,1)），或显式 `b_coord_input=False`"
            "（⚠ 后者要求模型**已定义**拉拔方向，否则同样会弹框）。"
        )
    fm = get_com_member(model, "FeatureManager")
    #: ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `MoldUndercutDetect`（6 参）。
    #:   ★ 官方 `types/IFeatureManager/MoldUndercutDetect.md` 逐字：
    #:     「**Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]].**」
    #:   ★★ 后继是 **9 参**（★ 官方 `MoldUndercutDetect2.md` 的 `## Parameters` 逐字）：
    #:     ```
    #:     ColUndercut1   ← 旧 ColUndercut（第 1 方向不可见的面）
    #:     ColUndercut2   ← ★ **新增**（第 2 方向不可见的面）
    #:     ColOccluded    ← ★ **新增**（两方向都不可见的面）
    #:     ColStraddle    ← ★ **新增**（两方向都有拔模的面）
    #:     ColBase        ← 旧 ColBase（不构成倒扣的面）
    #:     BCoordInput / Dx / Dy / Dz   ← 同名同序（★ 第 6–9 位）
    #:     ```
    #:   ★★★ **新增那 3 个颜色的取值，官方**没给默认值**** ⇒
    #:     ★ **本项目的工程选择**：★ **沿用调用方给的两个颜色**
    #:     （★ `ColUndercut2` 用 `col_undercut`、★ `ColOccluded` 用 `col_base`、
    #:      ★ `ColStraddle` 用 `col_base`）—— ⚠ **这是工程选择，不是官方默认**，★ 已在此写明 ✓
    #:   ★★★ 真机证据（`tools/probe_deps_bom_undercut.py` ·
    #:     `output/deps-bom-undercut-evidence.json`）：★ 旧 6 参**能调**（回 `None`）·
    #:     ★★ 新 9 参**能调**（回 `None`）⇒ ★★ **可换** ✓
    return get_com_member(fm, "MoldUndercutDetect2",
                          int(col_undercut), int(col_undercut), int(col_base), int(col_base),
                          int(col_base), bool(b_coord_input),
                          float(dx), float(dy), float(dz))



# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（纯元数据反射）+ 本项目既有模式（weldment_evidence）
# 文件:   scripts/sw_mold.py 的 mold_evidence
# 定位:   只读证据采集：把模具族的**只读入口**回读出来，供 capabilities 与人工核对。
#         命名与形状照 scripts/sw_weldment.py::weldment_evidence 的既有模式（铁律 1 第三类来源）。
# 官方签名依据: GetPartingLinesCount / GetPartingSurfacesCount / GetCavitySurfacesCount /
#         GetCoreSurfacesCount / get_PartingType / get_CoreCavitySplit
# 许可:   本仓库 MIT。
# 覆盖:   本函数整体（自本行至函数结束）
# ─────────────────────────────────────────────────────────────────────────
def mold_evidence(model) -> dict:
    """采集当前零件的**模具状态证据**（只读，不改模型）。

    :param model: **IModelDoc2** —— 当前零件的文档对象（`FeatureManager` 从它取）。
    :returns: ``{counts: {...}, parting_type, core_cavity_split}``；
        取不到的条目为 ``None``（**不抛异常** —— 这是读取入口）。

    ★ **2026-10-01（轮 175）补上这条 `:param` 是**有依据、不是形式**】**：
    `scripts/check_member_owner_interface.py` 靠 `:param <名>: <接口名>` 推**形参的接口**
    （★ 事实 114 的定则：**显式 = 有依据；推断 = 会错**）。
    ⚠ 轮 174 试过「docstring 里的散文接口名」那条**推断**退路 ⇒ **实测两处都推错**、**已回退**。
    ⇒ ★ 所以这里**显式写出来**，让那个检查器能**真的检查到本函数**（此前它抓不到 —— 那是它的动机）。
    ⚠ 另注：本函数的 owner 形状是「`model` → `fm = get_com_member(model, "FeatureManager")`
    → `fm.GetPartingLinesCount`」⇒ ★ 检查器**真正会报的是 `fm` 那一层**
    （`IFeatureManager` 上没有那几个计数）—— 那**正是**轮 172 查出的真问题。

    ⚠⚠⚠ **2026-10-01（轮 172）真机更正：这些成员**不在 `IFeatureManager` / `IModelDoc2` 上****——
    `tools/probe_mold_evidence_readers.py` 在**新零件**上把 7 个成员**两种取法都试了**
    （`get_com_member` 与 `call_com_member`）：
    ```
      IFeatureManager.GetPartingLinesCount / GetPartingSurfacesCount /
        GetCavitySurfacesCount / GetCoreSurfacesCount     ⇒ **全 AttributeError: <unknown>.X**
      IModelDoc2.PartingType / CoreCavitySplit            ⇒ **同样不存在**
    ```
    ★★ 而**查反射/swapi 得到它们真正的归属**（★ 事实 36 那一族：**成员在别的接口上**）：
    ```
      GetPartingLinesCount    ⇒ IPartingLineFeatureData（另有 IDraftFeatureData2 同名成员）
      GetPartingSurfacesCount ⇒ I*FeatureData（swapi 有独立说明页）
      PartingType             ⇒ **IPartingSurfaceFeatureData**
      CoreCavitySplit         ⇒ **IPartingLineFeatureData**
    ```
    ⇒ ★★★ 所以**从 `FeatureManager` / `model` 上读**这些成员**永远是 `None`** ——
    本函数过去的"全 None"**不是"空件没有分型"**，而是**读错了对象**。
    ⚠ **要真读到**，必须先拿到对应的 **`I*FeatureData`**（从**已存在的**分型线 / 分型面特征上取）
    ⇒ ★ **前提是零件上**已经有那些特征**；空零件上**本来就取不到**（两者表象相同，别混）。
    ⚠ **本函数当前仍从旧位置读** ⇒ 它**在真机上只会返回全 `None`** ——
    此处**如实标注**而不假装能读（铁律 5：**查不到就说查不到**）；
    修法（从 FeatureData 取）需要**有分型特征的零件**才能验证 ⇒ **未做**。
    """
    fm = get_com_member(model, "FeatureManager")

    def _count(name: str):
        try:
            return get_com_member(fm, name)
        except Exception:
            return None

    def _prop(name: str):
        try:
            return get_com_member(model, name)
        except Exception:
            return None

    _counts = {
        "parting_lines": _count("GetPartingLinesCount"),
        "parting_surfaces": _count("GetPartingSurfacesCount"),
        "cavity_surfaces": _count("GetCavitySurfacesCount"),
        "core_surfaces": _count("GetCoreSurfacesCount"),
    }
    _pt = _prop("PartingType")
    _ccs = _prop("CoreCavitySplit")
    #: ★★★★ 2026-10-04（接手轮）**加一个可判字段 `readable`** ——
    #:   处置 `JUDGE-C_D_E.md` 的 🔴 **#14**（★ `E-1 #9`）：★ ToolSpec 的 doc 说「可回读」、
    #:   ★★ 而本函数自我标注「真机上只会返回全 `None`」⇒ ★★★ **两处说法相反** ✓
    #:   ★ **为什么不能只改 doc**：★ 因为**调用方无法从返回值区分**两种情况：
    #:     · ★ 「**读不到**」（★ 读错了对象 —— 本函数的现状）
    #:     · ★★ 「**真的没有分型**」（★ 空零件）✓
    #:   ⇒ ★★★ **两者表象相同（都是全 `None`）** ⇒ 所以必须有**一个显式的位**来分开 ✓
    #:   ★★ 判据（★ 可核、★ 不看返回值里的自然语言）：★ **四项计数全 `None` 且两个属性全 `None`**
    #:     ⇒ ★ `readable: False` ✓
    #:   ★★★ **注意它说的是什么**：★ `False` = 「**按当前读法在这台机器上读不到**」·
    #:     ★★ **不是**「这个零件没有分型」（★ 后者要靠 `I*FeatureData` 那条未实现的路）✓
    _all_none = all(v is None for v in _counts.values()) and _pt is None and _ccs is None
    return {
        "counts": _counts,
        # 这两个是零件级属性；用 set_com_member 的读侧配对是 get_com_member（已知事实 4）
        "parting_type": _pt,
        "core_cavity_split": _ccs,
        #: ★ **真相在这**：★ `False` ⇒ **本次读数不作数**（★ 别当成"没有分型"）✓
        "readable": (not _all_none),
        "readable_note": ("★ 全部为 `None` ⇒ ★ **本机按当前读法读不到**"
                          "（★ 真因：那些计数**不在 `IFeatureManager`/`IModelDoc2` 上**，"
                          "★ 而在 `I*FeatureData` 上 —— ★ 见本函数 docstring）· "
                          "★★ **这不等于「该零件没有分型」** ✓"
                          if _all_none else
                          "★ 至少读到一项 ⇒ 本次读数可用 ✓"),
    }

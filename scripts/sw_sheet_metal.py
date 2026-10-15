"""SolidWorks 原生钣金特征创建与证据回读。"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

try:
    from .sw_connect import get_com_member, call_com_member
    from .sw_part import _ensure_sketch_selected
except ImportError:
    from sw_connect import get_com_member, call_com_member
    from sw_part import _ensure_sketch_selected


SW_FM_BASE_FLANGE = 34
SW_END_COND_BLIND = 0
SW_BEND_ALLOWANCE_K_FACTOR = 2
SW_SHEET_METAL_RELIEF_RECTANGULAR = 1
SW_SOLID_BODY = 0


@dataclass(frozen=True)
class BaseFlangeSpec:
    """@brief 基体法兰的可制造参数。

    ⚠⚠ **单位更正（2026-10-06 · 规格 209 · 真机定案）**：本 docstring **原写「全部长度单位为米」**
    —— ★★ **那是错的**。真机用**厚度棱的长度**直接量（`IEdge::GetStartVertex/GetEndVertex` →
    `IVertex::GetPoint`，★ `IEdge` 上**没有**长度成员）：
    ```
    传 thickness=0.002 ⇒ 边长集合 {0.002, 40.0, 60.0}   ← ★ 0.002 就是厚度棱
    传 thickness=2.0   ⇒ 边长集合 {2.0,   40.0, 60.0}   ← ★ 2.0 才是厚度棱
    ```
    ⇒ ★★ **`IBaseFlangeFeatureData` 的长度按「文档长度单位」解释（本机 = 毫米）**，
      **不是米** ⇒ ★ 传 `0.002` 造出来的是 **0.002 mm 的箔片**（★ 本仓既有调用点用的正是 0.002）。
    ★ 证据：`tools/probe_spec209_hem_units.py` ⇒ `output/spec209-hem-units.json`。
    ⚠ **本轮只更正文档、不改行为**（改行为要单开一轮并配判据 —— 见 `docs/HANDOFF.md` 的待办）；
      ★ 同族的先例：`InsertMoveCopyBody2` 的长度也是**文档单位**（同一轮实测）。

    ★★★★ **上面那条「按文档单位（毫米）解释」**已被推翻****（2026-10-10 · **规格 278** · 真机）：
      ★ 用**普通尺寸**的草图（60 mm × 25 mm 的 U 形开放折线）逐个单变量试 ⇒
      ```
      传 thickness=0.002 · bend_radius=0.0025 · depth=0.1  ⇒ **建成**（★ 读回 thickness_m=0.002）
      传 thickness=2.0   · bend_radius=1.0    · depth=0.1  ⇒ ✗「无法添加此圆角，因为指定的半径值将会删除其中一个实体」
      传 thickness=2.0   · bend_radius=0.5    · depth=0.1  ⇒ ✗ 同上
      传 thickness=2.0   · bend_radius=1.0    · depth=100.0 ⇒ ✗ 同上
      ```
      ⇒ ★★★ **长度就是**米**（★ 与 SW API 的通用约定一致）** —— ★ `0.002` = **2 mm** 的真板，
      ★ 读回键名 `thickness_m` **本来就写着 `_m`** ⇒ ★ **0.002 m = 2 mm** 自洽 ✓。
      ⇒ ★★ 规格 209 那条推断的**依据不成立**：它用的草图是 **40 / 60 量级**（★ 若按米就是 40 m × 60 m 的巨件），
      ★ 在那个尺度下 `0.002` 与 `2.0` **都能建**（★ 只是棱长读数跟着变）⇒ ★ 它把「棱长跟着变」误读成了「单位是毫米」。
      ⇒ ★★ **回归结论：长度按**米**传；★ 本仓既有调用点传 `0.002` 是**对的****。
    ⚠★ 另一条真机约束（规格 278）：**`bend_radius` 必须 < `thickness`** ——
      ★ 否则 SW 报「无法添加此圆角，因为指定的半径值将会删除其中一个实体」。
    ★ 证据：`output/_probe278_values.txt` · `output/_probe278_regression.txt`（★ 回归 `status: pass`）。
    """
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游与既有模式的写法**发展而来）。
# 文件:   scripts/sw_sheet_metal.py —— 本文件（**轮 145 的命名迁移**）。
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


    thickness: float
    bend_radius: float
    depth: float
    k_factor: float = 0.42
    relief_ratio: float = 0.5
    reverse_direction: bool = False
    reverse_thickness: bool = False

    def validate(self) -> None:
        """@brief 在进入 COM 前拒绝明显无效的制造参数。"""
        if self.thickness <= 0:
            raise ValueError("钣金厚度必须大于 0")
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.depth <= 0:
            raise ValueError("基体法兰深度必须大于 0")
        if not 0 < self.k_factor < 1:
            raise ValueError("K 因子必须位于 0 与 1 之间")
        if self.relief_ratio <= 0:
            raise ValueError("卸料槽比例必须大于 0")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**真机实测结论**，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_sheet_metal_e2e.py（证据脚本）
# 定位:   模块级**运行期实测状态表**（2026-10-01，SW 2026 SP4.1）。
#  ⚠⚠ 结论：本模块 6 个创建入口里**只有 2 个能跑**；另 4 个已作为 MCP 工具暴露
#    （T-011 接线）但真机失败。失败原因见下表 —— **不是「未测」，是「测了，不行」**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
#         ↑ 本块说明 `SHEET_METAL_RUNTIME_STATUS`（常量）与 `require_verified`（函数）
#         **两个**代码单元。⚠ 标记必须写成**裸的** `覆盖: 后续同级定义` ——
#         加 markdown 粗体会让正则 `r"覆盖\s*[:：]\s*后续同级定义"` 匹配不到。
#         ⚠ 本会话第 **5** 次踩这个覆盖范围坑，见 `check_provenance` 的诊断。
# ⚠ 本表只覆盖**本机实测过**的入口；未测的按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
#: 入口名 → (是否可用, 真机失败原因或成功证据)
SHEET_METAL_RUNTIME_STATUS = {
    # ✓ 实测可跑
    "create_base_flange": (True,
        "**闭轮廓**真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」。"
        "⚠ **开放折线（轮廓法兰）真机失败**：`CreateFeature(IBaseFlangeFeatureData) 创建失败`"
        "（2026-10-01 补测，见 probe_gusset_with_bend.py）⇒ **`True` 仅对闭轮廓成立**"
        " ★★★ **订正（2026-10-10 · 规格 278 + 279 · 真机两次独立确认）**："
        "★★ **上面那句「开放折线真机失败」已被证伪** —— ★ **开放**折线（★ 3 段 U 形）在"
        "**毫米几何**下**建成了**（★ 278 的维护回归 `status: pass` · ★ 279 探针 `has_base_flange=True`）"
        "⇒ ★★ **当初失败的真因是**草图几何被 `mm()` 缩了 1000 倍**（★ 见规格 277/278），"
        "★ **不是**「开放轮廓不被支持」⇒ ★ 本条的 `True` **对开放与闭轮廓都成立**"),
    "sheet_metal_evidence": (True,
        "真机读回正确：thickness_m=0.002、has_base_flange=True、"
        "all_solid_bodies_are_sheet_metal=True"),
    # ✗ 实测失败（原因是真机报错原文）
    # ⚠⚠ 以下 4 条的**根因层次**已由真机测清（2026-10-01，`probe_featuredata_access.py`）：
    #   ① `CreateDefinition(fm)` 实测：34/37/118 → 非 None；**3/33 → None**
    #      ⇒ **Draft 与 OneBend 不走 `CreateDefinition`**（反射里有专用入口
    #        `InsertSheetMetal3dBend` / `IInsertSheetMetalEdgeFlange2` 等，**均存在**）。
    #   ② `AccessSelections(model, Component)` **被否证**：三种 Component 形式
    #      （`None` / `VARIANT(VT_DISPATCH,None)` / `False`）全失败
    #      ⇒ 官方文档说它是「取得描述**该特征**的选区」= **编辑**用，不是创建用。
    #   ③ `ReverseDirection` 的跨接口泄漏**已修复**（见 `create_edge_flange` 的 `_apply`）：
    #      删掉后报错**从** `Property ... can not be set` **变为** `CreateFeature(37) 创建失败`
    #      ⇒ **属性那一层确实通了**。
    #   **⇒ 仍未查明**：`create_gusset` 在**能**拿到 FeatureData 时为何 `Thickness` 仍设不上；
    #     以及这 4 个的**正确创建路径**（是否该改用专用 `Insert*` 入口）。**不猜、不硬改。**
    "create_one_bend": (False,
        "⚠ **真因已查明（2026-10-01，有官方依据）**：`swFmOneBend(33)` 是合法枚举成员，"
        "但**不在** `CreateDefinition` 接受的 35 个常量里（官方 `CreateDefinition.md` 的 "
        "Parameters 段）⇒ 返回 None **是应然的**。"
        "**正确入口**是 `swFmSketchBend(35)`（**已改用**），接口 `ISketchedBendFeatureData`。"
        "真机已验证 `CreateDefinition(35)` 返回**非 None**，且属性读回与该接口成员逐一吻合。"
        "**⚠ 仍缺**「选中折弯线 / 固定面」这一步 ⇒ 仍标不可用，但**原因已具体化**"
        "（不再是「未查明」）。原记法：`CreateDefinition(33) 返回 None ⇒ 不走 CreateDefinition`；"
        "正确入口未查明（反射里有 `InsertSheetMetal3dBend`）"
        " ★★★ **定案（2026-10-10 · 规格 281 · 真机逐个测）**：★★ **后端限制** —— "
        "`CreateDefinition(35)` 拿到的 `ISketchedBendFeatureData` **有** `AccessSelections`（`hasattr=True`），"
        "★ 但 `AccessSelections(model, 空 Dispatch)` ⇒ **`-2147417851`（`0x80010105`「服务器出现意外情况」）** "
        "⇒ ★★ 与事实 47 / 67 / 126 的 `IAccessSelections` 指针族**同族**（★ 与常量 37/117/118 **同一个读数**）"),
    "create_draft": (True,
        "★★ 2026-10-09（规格 239）**创建路径已按官方页改写**：原走 `CreateDefinition(swFmDraft=3)` ——"
        "① `swFmDraft` **不在**任何官方 `CreateDefinition` 宿主页（`IFeatureManager` / `IMotionStudy`）"
        "的 `Type` 清单里（规格 238 已证）；② 真机回 `None`。"
        "⇒ 官方入口是 **`IFeatureManager::InsertMultiFaceDraft`**"
        "（★ 其前代 `IModelDoc2::InsertMfDraft` / `InsertMfDraft2` 两页都写着 "
        "`Obsolete. Superseded by IFeatureManager::InsertMultifaceDraft` ⇒ 官方**自己指认**了取代方向）。"
        "★★★ 2026-10-10（规格 283）**真机验证可用** ✓ —— 新特征 **`拔模1`**；"
        "★★ 前提是**两个**选择：**方向项（mark 1 · 一个平面）** + **待拔模面（mark 2）**。"
        "原记法：`CreateDefinition(3) 返回 None ⇒ 该类型不走 CreateDefinition；正确入口未查明`"),
    #: ★★★ 283 的**真机读数**（★ 2026-10-10 · SW 34.4.1）：
    #:   ① ★ **只给面**（★ 6 面 × 3 标记 = **18 臂**）⇒ ★ **全失败**，★ 且报文**恒定**：
    #:      ★「**此拔模方向尚未定义。**」⇒ ★ 排除「选错了面 / 选错了标记」。
    #:   ② ★★ **方向项（`Front Plane` · mark 1）+ 待拔模面（mark 2）** ⇒ ★ **选中 2 个 · 建成 `拔模1`** ✓。
    #:   ⇒ ★★★ **规格 239 的路径改动是对的**，★ 缺的只是**方向项**这一选择。
    #:   ★★ **顺带**：★ 这是 282 那条假说（★「特征创建 API 似乎吃不到「边 / 面」类选择」）的**反例**
    #:     —— ★ `InsertMultiFaceDraft` **吃得到面选择** ⇒ ★ **「吃不到」不是普遍现象，是按 API 逐个看的** ✓
    #:   ★ 读数：`output/_probe283_draft.txt` · `output/_probe283_draft_dir.txt`
    "create_edge_flange": (False,
        "⚠ 属性层**已修**（原设的 `ReverseDirection` **不属于** `IEdgeFlangeFeatureData` —— "
        "跨接口泄漏，已删；报错已从 `Property ... can not be set` 变为 `CreateFeature(37) 创建失败`）"
        "⇒ **剩最后一层：`CreateFeature` 需要选择状态**（官方文档在同类特征上明写"
        "「select ... **with a Mark of 1**」）—— **未查明**"
        " ★★★ **订正（2026-10-10 · 规格 279 · 真机单变量）**："
        "★★ **上面那句「剩最后一层 = 需要 Mark 1」已被证伪** —— ★ 夹具用**带两道真折弯的 U 型件**"
        "（★ 开放折线 · 毫米几何 · `has_base_flange=True` · 44 条边 · 取最长边 0.1 m），"
        "★ **只改「边的选择标记」**：★ **不设 / Mark 1 / Mark 0 三臂全部失败**，"
        "★ 且报**同一条**：★「**边线-法兰N: 无法为此特征找到适当的钣金实体**」"
        "⇒ ★★ **阻塞不是选择标记**，★ 而是**边 / 实体的识别**（★ 即：那条边不被当作「可加边法兰的边」）"
        "⇒ ★ **下一轮的方向**：★ 换**别的边**（★ 本探针只试了「最长边」一条）· "
        "或先核**该边在 SW 眼里属不属于钣金外轮廓**（★ 不猜）"
        " ★★★ **定案（2026-10-10 · 规格 280 · 真机六臂 + `AccessSelections` 逐形态）**："
        "★★ **上面那条「下一轮方向」已被**走完并排除**** —— ★ 六臂（★ `Select4`/`SelectByID2` × "
        "Mark 1/不设 × 最长边/最短直边 × 开放折线/闭轮廓）**全失败**，★ 且报文**一字不差**："
        "★「**无法为此特征找到适当的钣金实体**」⇒ ★★ **选择方式 / 换边 / 轮廓类型 都不是因素**。"
        "★★★ **真阻塞是结构性的**：★ `IEdgeFlangeFeatureData::AccessSelections(TopDoc, Component)` 逐形态实测 ⇒ "
        "★ 空 Dispatch ⇒ **`-2147417851`（`0x80010105`「服务器出现意外情况」）** · ★ `None` / `False` ⇒ "
        "`-2147352571`（类型不匹配）⇒ ★★ **与事实 47 / 67 / 126 的 `IAccessSelections` 指针族**同族**** "
        "⇒ ★★★ **后端限制**（★ 而官方 `IEdgeFlangeFeatureData` 页**有** `AccessSelections`，"
        "★ `IAccessSelections` / `IAccessSelections2` 两个接口页也在 ⇒ ★ 是**本机**调不动，不是路径错）。"
        "★ **处置**：★ 本条**不再**标「未查明」⇒ ★ 标**后端限制**；★ 且 `create_gusset` / `create_hem` / "
        "`create_one_bend` **同族嫌疑**（★ 它们也都是 `CreateFeature` + 选择前置）⇒ ★ **未逐个验**（★ 不越界）"),
    "create_gusset": (False,
        "⚠ 属性层**已修**（**接口用错了**：钣金加强筋的接口是 **`ISMGussetFeatureData`**"
        "（`category: Sheet Metal`，28 属性），原代码用了 **`IGussetFeatureData`**"
        "（`category: Weldments`，19 成员）——**两者共有成员只有 3 个**，"
        "原设的 `Thickness`/`ProfileDistance1`/`ProfileDistance2`/`ProfileAngle` **全是焊件名**。"
        "改用 `GussetThickness`/`ProfileHeightDim`/`ProfileLengthDim`/`ProfileAngleDim` 后"
        "**真机读回全部成功**（0.002 / 0.01 / 0.01 / 45.0）；报错已变为 `CreateFeature(118) 创建失败`）"
        "⇒ **最后一层的性质已查明**：官方 `ISMGussetFeatureData` 的 Remarks 明写创建步骤 ——"
        "「Call `IFeatureManager::CreateDefinition` … **pre-select** …         Two flat faces of a **bend**」⇒ **必须预先选中「一个折弯的两个平面」**。"         "**⚠ 而本模块原本用的 `CreateDefinition`+`CreateFeature` 路线是**现代的**："         "官方的 `InsertSheetMetalGussetFeature3` 已被标注 "         "「**Obsolete. Superseded by CreateDefinition and CreateFeature.**」"         "⇒ **代码路线正确，缺的是「折弯的两个面」这个前置** —— 而测试夹具（平板基体法兰）"         "根本造不出折弯 ⇒ **本轮未定性**（不宣称它能跑，也不宣称它不行）"
        " ★★★ **定案（2026-10-10 · 规格 281 · 真机逐个测）**：★★ **后端限制** —— "
        "`CreateDefinition(118)` 拿到的 `ISMGussetFeatureData` **有** `AccessSelections`（`hasattr=True`），"
        "★ 但 `AccessSelections(model, 空 Dispatch)` ⇒ **`-2147417851`（`0x80010105`）** "
        "⇒ ★★ 与事实 47 / 67 / 126 **同族** ⇒ ★ **「预选折弯的两个面」这条前置**即使满足了**，"
        "★ 也**过不了** `AccessSelections` 这一关**（★ 规格 280/281 的真机结论）"),
    # 未测（需要扫掠路径 + 轮廓两个选择，本轮没造出来）
    "create_swept_flange": (None, "未在本机实测（需要扫掠路径与轮廓两个选择）"
        " ★★★ **定案（2026-10-10 · 规格 281 · 真机逐个测）**：★★ **后端限制** —— "
        "`CreateDefinition(117)` 拿到的 `ISweptFlangeFeatureData` **有** `AccessSelections`（`hasattr=True`），"
        "★ 但 `AccessSelections(model, 空 Dispatch)` ⇒ **`-2147417851`（`0x80010105`）** "
        "⇒ ★★ 与事实 47 / 67 / 126 **同族** ⇒ ★ **它同样过不了这一关**（★ 与常量 35/37/118 同一个读数）"),
    #: ★★★ 2026-10-06（规格 209 · B4-2 · idx 173）：**`create_hem` 真机回 `None`** ——
    #:   ★ 而**成员名/16 参顺序/五个枚举全部逐条对上官方**（★ 不是"抄错"），四步前置照做
    #:   （★ 且**顺序已按官方 `## Remarks` 订正**：先建 CBA、**再**选边），
    #:   ★★ **五种形态全部回 `None`**（★ 每一次都是一个**可证伪的假设**，不是"换个参数再试"）：
    #:   ```
    #:   ① 边 index:0（可能是厚度棱）              ② 边=最长边(index:4，60 mm 外缘)
    #:   ③ 长度参数整体 ×1000（毫米口径）          ④ UseDefaultRelief=True（默认卸料槽）
    #:   ⑤ 板厚从 0.002（箔片）改成 2.0（真 2 mm）
    #:   ```
    #:   ⇒ ★★ **按事实 53 停止**（同一启发式连续修补 ≥3 次即停，不当场继续凑形态）✓
    #:   ★ **下一步（写清楚，免得后人重走）**：① 找一个**现成的带折弯钣金件**当夹具
    #:     （本机磁盘上没有这种模型 —— 全盘扫过 `.SLDPRT`）；② 或换 `InsertSheetMetalHem`
    #:     （**已 Obsolete** 的前代）；③ 或先做成 `InsertSheetMetalFold` 造出折弯再回来。
    "create_hem": (False,
        "★ 真机（2026-10-06 · SW 2026 SP4.1 · pywin32）**五种形态全部回 `None`**："
        "边选择（`index:0` / 最长边 `index:4`）× 长度口径（0.01 / 10.0）× 卸料槽（自定义 / 默认）"
        "× 板厚（0.002 箔片 / **2.0 真厚度**）⇒ **本机建不出 hem**。"
        "★ 成员名与 16 参顺序、枚举值**已逐条核对官方无误**；四步前置（CreateCustomBendAllowance → "
        "初始化 → 赋 PCBA → **再**选边）**已按 Remarks 订正顺序后重试**，仍 `None`。"
        "⇒ ★ 正确前置**尚未查明**；见 `tools/probe_spec209_hem_diag.py` 与 "
        "`tools/probe_spec209_hem_units.py` 的读数（`output/spec209-hem-*.json`）"),
    #: ★★★ **订正（2026-10-10 · 规格 282 · 真机四形态 + 选择类型核查）**：
    #:   ★★ **上面那句「尚未查明」可以撤了** —— ★ 用 276 的报错入口（`ISldWorks::GetErrorMessages`）
    #:   把四形态**逐个读栈** ⇒ ★★ 报文**恒定**：★「**褶边N: 您必须选择一边线。**」（★ 而**选中数 = 1**）。
    #:   ★★★ **再量一层**：★ `SelectionMgr.GetSelectedObjectType3(1, -1)` ⇒ ★ 边 = **`swSelEDGES`(1)** ·
    #:     ★ 面 = **`swSelFACES`(2)**（★ 本仓 `select_entity_by_index` 与 `IEntity::Select4` **两条路都核过**）
    #:     ⇒ ★★ **「选了却说没选」** ⇒ ★ 问题**不在选择登记**。
    #:   ★★ **与 `create_edge_flange` 同形但不同因**：★ 两者都是「选择登记了、特征 API 吃不到」；
    #:     ★ 但 hem 走 `InsertSheetMetalHem2`（★ **无** `AccessSelections`）· ★ edge_flange 卡在 `AccessSelections`。
    #:   ★★ **假说（★ 只有 2 个样本 ⇒ 如实标成假说）**：★ 本机的特征创建 API **似乎吃不到「边 / 面」类选择**
    #:     （★ 吃**草图**的 `create_base_flange` **能建**）⇒ ★ **待验**，★ 不据此下结论。
    #:   ⚠★ **为什么这条订正写成注释、不写进上面那条字符串**：★ 那条字符串**会进 MCP 工具说明**；
    #:     ★ 实测（规格 282 首跑）把它写进去后，**预选族门禁**的 ±160 字**否定窗口**被推移
    #:     ⇒ ★ 冒出 **2 条假红**（`insert_form_tool` / `create_fold`）⇒ ★ **诊断细节放注释、说明留摘要** ✓
    #: ★★★ 2026-10-06（规格 209 · B2-1 · idx 336）：**`create_unfold` 真机建成了** ——
    #:   新特征 **`展开1`**（`output/spec209-unfold-contract.json`）✓
    #:   ★★ 关键在**选择契约**：固定面 **mark 1** + 一个 `BODYFEATURE` **mark 4**，
    #:     且 `SetSelectedObjectMark` 第 3 参必须是 **`swSelectionMarkSet`(0)**（传 `-1` **静默不生效**）。
    #:   ★ 而**"哪条折弯"没有被限死**：本仓真机用**基体-法兰1**（一个**不是折弯**的特征）当 mark 4
    #:     的对象，`展开1` **照样建出来了** ⇒ ★★ **本表只记这一格的读数**，
    #:     ★ **不据此声称"任意特征都可以"**（★ 那需要另一组实验）✓
    "create_unfold": (True,
        "★ 真机（2026-10-06）建成 **`展开1`**：选择契约**逐条回读**为 "
        "`total_count=2 · marks=[1, 4] · mark_set=True`；特征树增量 +1 ✓ "
        "★★ **而且我原先的一条「负例」被证伪**：**不选任何 `mark 4` 对象**（只给固定面 mark 1）"
        "时**照样建出 `展开1`** ⇒ ★★ **`mark 4` 不是必需的** —— 官方示例选折弯是"
        "「照着做」，不是「必需」（★ 本表按读数改口径）✓ "
        "⚠ 先前记录的「没建出来」是**我自己的 bug**：`SetSelectedObjectMark` 第 3 参传了 `-1`"
        "（官方要 `swSelectionMarkSet`(0)）⇒ mark 静默没设上 ✓"),
    #: ★★★ 2026-10-06（规格 209 · B4-4 · idx 155）：**`create_fold` 真机建成了** ——
    #:   拿刚建出的 `展开1` 当**前置特征（mark 0）**，新特征 **`折叠1`**（`output/spec209-unfold-fold.json`）✓
    #:   ★★ 关键同 unfold（mark 表 [1, 4]），★ 而**前置特征那一步必须在 `ClearSelection2` 之后** ——
    #:     我第一版把它塞在 `call()` 里 ⇒ 会被清选区**清掉**（顺序错、静默失效）✓
    "create_fold": (True,
        "★ 真机（2026-10-06）建成 **`折叠1`**：`unfold → fold` 一条链（★ 与官方示例同形），"
        "两条的 `marks_readback` 都是 **[1, 4]**、特征树各 +1 ✓"),
}



def _read_k_factor(definition) -> float:
    """读 K 因子（★ spec 261 换路由：官方后继 `GetCustomBendAllowance().KFactor`）。

    ★★ **为什么换**：`IBendsFeatureData::KFactor` 官方标
      「Obsolete. Superseded by [[IBendsFeatureData::GetCustomBendAllowance]] and
       [[IBendsFeatureData::SetCustomBendAllowance]]」。
    ★★ **不是 drop-in**：后继**零参**、回 **`ICustomBendAllowance` 对象** ⇒ ★ 要再取它的 `KFactor`
      （★ 那是**另一个接口**上的属性，★ **不废弃**）。
    ★ 取不到就回 `0.0`（★ 与旧写法同语义：旧写法也是 `or 0.0`）。
    """
    try:
        cba = get_com_member(definition, "GetCustomBendAllowance")
        if cba is not None:
            return float(get_com_member(cba, "KFactor") or 0.0)
    except Exception:                                              # noqa: BLE001
        pass
    return 0.0

def require_verified(entry: str) -> None:
    """**调用前**的守卫：该入口若在本机实测失败/未测，就抛**带原因**的错误。

    ⚠ 为什么必须这样：那 4 个入口已经作为 MCP 工具暴露给用户，
    失败时用户看到的是裸 COM 错误（`Property ... can not be set`），
    **完全指向不了真因**，也**无从知道这是已知问题**。
    """
    status = SHEET_METAL_RUNTIME_STATUS.get(entry)
    if status is None:
        return                       # 表里没有 ⇒ 不阻止（宁放行不误杀）
    ok, reason = status
    if ok is True:
        return
    if ok is None:
        raise RuntimeError(
            "%s **未在本机实测**（%s）—— 先在真机上验证再依赖它。"
            % (entry, reason)
        )
    raise RuntimeError(
        "%s **在本机实测失败，已知不可用**（2026-10-01，SW 2026 SP4.1）：%s。"
        "⇒ 正确形状尚未查明（是 swFm 取值错？FeatureData 属性名错？缺 AccessSelections？）；"
        "见 scripts/sw_sheet_metal.py 的 SHEET_METAL_RUNTIME_STATUS 与 "
        "D:\\\\AI\\\\SW\\\\probe_sheet_metal_e2e.py。" % (entry, reason)
    )


def _feature_type(feature: Any) -> str:
    """@brief 安全读取特征类型名。"""
    try:
        return str(get_com_member(feature, "GetTypeName2") or "")
    except Exception:
        return ""


def iter_features(model):
    """@brief 顺序遍历特征树，兼容 pywin32 的属性/方法两种投影。"""
    feature = get_com_member(model, "FirstFeature")
    # pywin32 可能为不同 COM 对象复用短生命周期包装器的 Python id，不能
    # 用 id 去重；以硬上限防御异常的特征链循环。
    count = 0
    while feature is not None and count < 4096:
        yield feature
        feature = get_com_member(feature, "GetNextFeature")
        count += 1


def create_base_flange(model, sketch_ref, spec: BaseFlangeSpec):
    """@brief 使用现代 FeatureData API 从开放或闭合草图创建原生基体法兰。

    开放折线路径会生成轮廓法兰；闭合轮廓会生成平板基体。返回真实
    ``IFeature``，失败时抛出异常，不把空返回值包装为成功。
    """
    spec.validate()
    _ensure_sketch_selected(model, sketch_ref)
    manager = get_com_member(model, "FeatureManager")

    bend_allowance = call_com_member(manager, "CreateCustomBendAllowance")
    if bend_allowance is None:
        raise RuntimeError("CreateCustomBendAllowance 未返回对象")
    bend_allowance.Type = SW_BEND_ALLOWANCE_K_FACTOR
    bend_allowance.KFactor = float(spec.k_factor)

    data = get_com_member(manager, "CreateDefinition", SW_FM_BASE_FLANGE)
    if data is None:
        raise RuntimeError("CreateDefinition(swFmBaseFlange) 未返回特征数据")

    data.Initialize(
        False,
        True,
        bend_allowance,
        True,
        SW_SHEET_METAL_RELIEF_RECTANGULAR,
        True,
        float(spec.relief_ratio),
        0.0,
        0.0,
    )
    data.D1EndConditionType = SW_END_COND_BLIND
    data.D1EndConditionDistance = float(spec.depth)
    data.D2EndConditionType = SW_END_COND_BLIND
    data.D2EndConditionDistance = 0.0
    data.OverrideDefaultSheetMetalParameters = True
    data.Thickness = float(spec.thickness)
    data.BendRadius = float(spec.bend_radius)
    data.ReverseDirection = bool(spec.reverse_direction)
    data.ReverseThickness = bool(spec.reverse_thickness)

    feature = get_com_member(manager, "CreateFeature", data)
    if feature is None:
        raise RuntimeError("CreateFeature(IBaseFlangeFeatureData) 创建失败")
    # GetErrorCode2 还带一个 by-ref ``isWarning`` 参数；此处只需拒绝硬错误，
    # 使用无歧义的 GetErrorCode 可兼容 pywin32 静态与动态代理。
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"基体法兰返回特征错误码: {error_code}")
    return feature


def sheet_metal_evidence(model) -> dict[str, Any]:
    """@brief 回读原生特征、实体与关键钣金参数，形成可审计证据。"""
    feature_rows = []
    base_parameters = []
    for feature in iter_features(model):
        type_name = _feature_type(feature)
        name = str(get_com_member(feature, "Name") or "")
        feature_rows.append({"name": name, "type": type_name})
        if type_name in {"BaseFlange", "SMBaseFlange", "Base-Flange"}:
            definition = get_com_member(feature, "GetDefinition")
            if definition is not None:
                base_parameters.append({
                    "name": name,
                    "thickness_m": float(get_com_member(definition, "Thickness") or 0.0),
                    "bend_radius_m": float(get_com_member(definition, "BendRadius") or 0.0),
                    "depth_m": float(get_com_member(definition, "D1EndConditionDistance") or 0.0),
                    "k_factor": _read_k_factor(definition),
                })

    bodies = tuple(get_com_member(model, "GetBodies2", SW_SOLID_BODY, False) or ())
    body_rows = []
    for body in bodies:
        is_sheet_metal = False
        try:
            is_sheet_metal = bool(get_com_member(body, "IsSheetMetal"))
        except Exception:
            pass
        body_rows.append({
            "name": str(get_com_member(body, "Name") or ""),
            "is_sheet_metal": is_sheet_metal,
        })

    type_names = [row["type"] for row in feature_rows]
    return {
        "features": feature_rows,
        "feature_types": type_names,
        "base_flange_parameters": base_parameters,
        "bodies": body_rows,
        "has_sheet_metal_feature": any("SheetMetal" in item for item in type_names),
        "has_base_flange": bool(base_parameters),
        "all_solid_bodies_are_sheet_metal": bool(body_rows) and all(
            row["is_sheet_metal"] for row in body_rows
        ),
    }


# ══════════════════════════════════════════════════════════════════════
# 以下为「原生钣金特征扩写」批次。
# 模式说明：与基体法兰不同，本批 5 个 FeatureData 接口在 C:\swapi 中
# **均无 Initialize 成员**（sw_know.py 逐一报 [SWK_NOT_FOUND]），
# 故走「CreateDefinition(swFmXxx) → AccessSelections → 设属性 →
# CreateFeature → ReleaseSelectionAccess」路径，不臆造 Initialize 调用。
# ══════════════════════════════════════════════════════════════════════

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（非开源项目，无第三方许可）
# 文件:   托管程序集 SolidWorks.Interop.swconst.dll（34.4.1.1011）中的
#         swFeatureNameID_e，取值由纯元数据反射取得
# 定位:   IFeatureManager.CreateDefinition(Int Type) 的 Type 实参。
#         官方签名：C:\swapi\types\IFeatureManager\CreateDefinition.md
#                  `System.object CreateDefinition( System.int Type )`
# 取值:   本批新增 5 个，逐个反射核出；swFmBaseFlange=34 与上游既有常量
#         SW_FM_BASE_FLANGE 一致，已交叉确认上游该常量无误。
# 查证:   pwsh -File D:\AI\SW\tools\reflect-enum.ps1 `
#           -Assembly swconst -Enum swFeatureNameID_e
#         （C:\swapi\enums\swFeatureNameID_e.md 只有名称列、无数值列，
#           故不以该文件为取值依据 —— 见 AGENTS.md 铁律 4「枚举值必须查」）
# ⚠ 本表为静态反射结果，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 查不到故不编: swFeatureNameID_e 中**没有** Hem / MiterFlange 对应项，
#   故本批不提供翻边与斜接法兰的 CreateDefinition 入口。
# ────────────────────────────────────────────────────────────────────
#: ⚠⚠ `swFmDraft(3)` 是**合法枚举成员**（`swFeatureNameID_e` 第 57 行），但
#: ★★ **不在任何官方 `CreateDefinition` 宿主页的 `Type` 清单里**
#: （官方只有两个宿主页：`IFeatureManager` / `IMotionStudy`；规格 238 已证）。
#: ⇒ ★ **本常量不得传给 `CreateDefinition`** —— 真机回 `None` 正是**应然的**。
#: 本常量**保留**是作为「禁止这样用」的**证据锚点**（规格 239 的 `unsupported-path` 判据
#: 就是查这个）；拔模的**官方入口**是 `IFeatureManager::InsertMultiFaceDraft`
#: （见 `create_draft` 的来源块）⇒ 该入口**不需要**本常量。
SW_FM_DRAFT = 3
SW_FM_ONE_BEND = 33
#: ⚠ `swFmOneBend(33)` 是**合法枚举成员**，但**不在** `CreateDefinition` 接受的 35 个常量里
#: ⇒ `CreateDefinition(33)` 返回 None **是应然的**（已知事实 34 的真因，2026-10-01 查明）。
#: 「一个折弯」的**正确入口**是下面这个（官方名单里有，接口 `ISketchedBendFeatureData`）。
#: 数值来源：`D:\AI\SW\_raw\**\enum_values_sldworks.txt`（反射，130 个成员）。
SW_FM_SKETCH_BEND = 35

#: `swSheetMetalGussetProfileDimType_e` 的取值（官方枚举页）：
#: `IndentDepth = 0` · **`ProfileDimensions = 1`**。
#: 钣金加强筋的 `ProfileDimensionScheme` **必须显式指定** —— 官方
#: `ISMGussetFeatureData` 的 Remarks 把它列为创建步骤 3 的**头一句**。
#: 数值来源：`C:\swapi\enums\swSheetMetalGussetProfileDimType_e.md`。
GUSSET_PROFILE_DIMENSIONS = 1
SW_FM_EDGE_FLANGE = 37
SW_FM_SWEPT_FLANGE = 117
SW_FM_SM_GUSSET = 118

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IFeatureManager\CreateFeature.md
#         C:\swapi\types\IFeatureManager\CreateDefinition.md
# 定位:   本批 5 个特征共用的「定义 → 建特征」骨架，与上游 create_base_flange
#         保持同一写法（上游已用于基体法兰且经静态比对通过）。
# 官方签名:
#           System.object  CreateDefinition( System.int Type )
#           Feature        CreateFeature( System.object FeatureData )
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def _create_from_definition(model, fm_type: int, apply_definition):
    """由 FeatureData 定义创建特征，失败一律抛异常，不把空返回包装成成功。

    ``apply_definition`` 收到 FeatureData 对象，负责设属性；
    边/面引用类特征须在其内部自行配对 AccessSelections / ReleaseSelectionAccess。
    """
    manager = get_com_member(model, "FeatureManager")
    #: ★ spec 239：拔模**不走** `CreateDefinition`（`swFmDraft` 不在任何官方宿主页的
    #:   `Type` 清单里）⇒ 这里**没有** `cd-site` 声明，因为它**不再是** `CreateDefinition` 站点。
    data = get_com_member(manager, "CreateDefinition", int(fm_type))
    if data is None:
        raise RuntimeError(f"CreateDefinition({fm_type}) 未返回特征数据")

    apply_definition(data)

    feature = get_com_member(manager, "CreateFeature", data)
    if feature is None:
        raise RuntimeError(f"CreateFeature({fm_type}) 创建失败")
    # GetErrorCode2 多一个 by-ref isWarning 参数；此处只需拒绝硬错误，
    # 用无歧义的 GetErrorCode 兼容 pywin32 静态与动态代理（同上游注释）。
    error_code = int(get_com_member(feature, "GetErrorCode") or 0)
    if error_code:
        raise RuntimeError(f"钣金特征 {fm_type} 返回特征错误码: {error_code}")
    return feature


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（AGENTS.md 铁律 1 认可的第三类来源）
# 文件:   scripts/sw_sheet_metal.py::BaseFlangeSpec（同文件既有类，@brief + 冻结
#         dataclass + validate() 在进入 COM 前拒绝无效制造参数）
# 定位:   下方 4 个 spec 数据类沿用 BaseFlangeSpec 的形状与命名习惯，
#         只增补各自领域的字段与校验，不引入新范式。
# ⚠ 字段语义取自 C:\swapi 对应 FeatureData 的成员目录（见各 create_* 的来源块）。
# ⚠ 本组为照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class OneBendSpec:
    """@brief 单折弯的可制造参数，长度单位为米。"""

    bend_radius: float
    angle: float
    reverse_direction: bool = False
    use_default_radius: bool = True

    def validate(self) -> None:
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if not 0 < self.angle < 360:
            raise ValueError("折弯角度必须位于 0 与 360 度之间")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec，见上一来源块）
# 定位:   边法兰 spec，沿用 BaseFlangeSpec 的 @brief + 冻结 dataclass +
#         validate() 形状。字段对应 IEdgeFlangeFeatureData 的
#         BendRadius / BendAngle / ReverseDirection / UseDefaultBendRadius。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class EdgeFlangeSpec:
    """@brief 边法兰的可制造参数，长度单位为米，角度为度。"""

    bend_radius: float
    flange_length: float
    angle: float = 90.0
    use_default_radius: bool = True
    reverse_direction: bool = False

    def validate(self) -> None:
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.flange_length <= 0:
            raise ValueError("法兰长度必须大于 0")
        if not 0 < self.angle <= 180:
            raise ValueError("边法兰角度必须位于 0 与 180 度之间")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec）
# 定位:   拔模 spec。★ 2026-10-09（规格 239）**字段扩到官方 6 参的对应面**：
#         官方 `IFeatureManager::InsertMultiFaceDraft` 的 6 个形参是
#         `Angle / FlipDir / EdgeDraft / PropType / IsStepDraft / IsBodyDraft` ⇒
#         本 dataclass 用 `angle / reverse_direction / edge_draft / prop_type /
#         is_step_draft / is_body_draft` 一一对应（★ 是**映射**，不是「同名断言」：
#         `reverse_direction` ↔ `FlipDir` 的语义由 `create_draft` 的来源块写明）。
#         深度 depth 属工艺意图字段，不直接落到 COM 属性（官方该入口**没有**深度参数）。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class DraftFeatureSpec:
    """@brief 拔模的可制造参数，角度为度、深度为米。"""

    angle: float
    depth: float
    reverse_direction: bool = False
    #: 官方 `EdgeDraft`：True = **边拔模**（选边，软件自动取其两侧面）；False = **面拔模**。
    edge_draft: bool = False
    #: 官方 `PropType`：0 不传播 · 1 传播到共享基准面的下一组相切面 · 2 传播到基准面的所有相邻面
    #: · 3 所有内环上的相邻面 · 4 外环上的相邻面。★ 取值域取自官方该页 `## Parameters`。
    prop_type: int = 0
    is_step_draft: bool = False
    is_body_draft: bool = False

    def validate(self) -> None:
        if not 0 < self.angle <= 180:
            raise ValueError("拔模角度必须位于 0 与 180 度之间")
        if self.depth <= 0:
            raise ValueError("拔模深度必须大于 0")
        #: ★ 官方 `PropType` 只列了 0–4 五个取值 ⇒ 越界在**进 COM 前**拒绝。
        if int(self.prop_type) not in (0, 1, 2, 3, 4):
            raise ValueError("拔模传播类型必须位于 0 与 4 之间（官方 PropType 取值域）")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec）
# 定位:   加强筋 spec。字段逐项对应 C:\swapi\types\IGussetFeatureData\ 的
#         Thickness / ProfileDistance1 / ProfileDistance2 / ProfileAngle。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class GussetSpec:
    """@brief 钣金加强筋参数，长度单位为米、角度为度。"""

    thickness: float
    profile_distance_1: float
    profile_distance_2: float = 0.0
    profile_angle: float = 0.0

    def validate(self) -> None:
        if self.thickness <= 0:
            raise ValueError("加强筋厚度必须大于 0")
        if self.profile_distance_1 <= 0:
            raise ValueError("加强筋轮廓距离必须大于 0")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\ISketchedBendFeatureData\
#           （16 个成员：BendAngle / BendRadius / ReverseDirection /
#             UseDefaultBendRadius / UseDefaultBendAllowance / UseGaugeTable /
#             SetFixedFace / GetFixedFace / SetCustomBendAllowance / …）
# 定位:   **`swFmSketchBend(35)`** 的属性装配。
#         ⚠ **本注释原先写的是 `IOneBendFeatureData` / `swFmOneBend(33)`** ——
#         2026-10-01 查明 `swFmOneBend(33)` **不在 `CreateDefinition` 接受的
#         35 个常量里**，已改用 `swFmSketchBend(35)`，**注释随之更正**。
#         **⇒ 文档与代码不符比没有文档更糟 —— 本轮一并修掉这一处。**
#         属性名逐项取自上述成员目录，未使用任何未经证实的属性名。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_one_bend(model, sketch_ref, spec: OneBendSpec):
    """@brief 在草图轮廓上创建原生单折弯特征。"""
    spec.validate()
    _ensure_sketch_selected(model, sketch_ref)

    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        data.ReverseDirection = bool(spec.reverse_direction)

    # ⚠⚠ **原为 `SW_FM_ONE_BEND(33)`** —— 那是**合法枚举成员**，
    #   但**不在** `CreateDefinition` 接受的 35 个常量里（见常量定义处的注释），
    #   所以 `CreateDefinition(33)` 返回 None 是**应然的**。
    #   官方名单里「一个折弯」对应的是 `swFmSketchBend(35)`。
    #   ⇒ 真机已验证：`CreateDefinition(35)` 返回**非 None**，且读回的属性与
    #     `ISketchedBendFeatureData` 的成员逐一吻合。
    #   ⚠ **仍缺**「选中折弯线/固定面」这一步 ⇒ 不宣称整条路已通。
    return _create_from_definition(model, SW_FM_SKETCH_BEND, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IEdgeFlangeFeatureData\
#           （成员 43 项：AddEdges / ISetEdges / BendAngle / BendRadius /
#             FlangePosition / PositionType / UseDefaultBendRadius /
#             UseDefaultBendAllowance / UseReliefRatio / ReliefRatio …）
# 定位:   swFmEdgeFlange(37) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member IEdgeFlangeFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性，不臆造 Initialize 调用。
# ⚠ 边集合由调用方在创建前用 SelectByID2 选好；本函数不代为选边，
#   沿用上游 sw_part._select_by_id 的选区惯例（见 AGENTS.md §三）。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_edge_flange(model, spec: EdgeFlangeSpec):
    """@brief 在已选中的边上创建原生边法兰。

    调用前必须先用 ``sw_part._select_by_id`` 把目标边选入选区。
    """
    spec.validate()

    def _apply(data):
        data.UseDefaultBendRadius = bool(spec.use_default_radius)
        data.BendRadius = float(spec.bend_radius)
        data.BendAngle = float(spec.angle)
        # ⛔ 原代码在此设 `data.ReverseDirection` —— **该属性不属于本接口**。
        #    `IEdgeFlangeFeatureData` 的 43 个成员里没有它；
        #    它是 `IDraftFeatureData2`（拔模）的成员（**跨接口属性泄漏**）。
        #    真机表现：`Property '<unknown>.ReverseDirection' can not be set`。
        #    ⚠ **不臆造替代**：最接近的 `ReverseOffset` / `ReversePositionOffset`
        #    是**偏置**方向，语义不同 —— 边法兰没有「反向」这个开关。
        #    见 `C:\swapi\types\IEdgeFlangeFeatureData\`（43 个成员名）。
        data.UseDefaultBendAllowance = True

    return _create_from_definition(model, SW_FM_EDGE_FLANGE, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   ① C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md
#           → `Feature InsertMultiFaceDraft(System.double Angle, System.bool FlipDir,
#              System.bool EdgeDraft, System.int PropType, System.bool IsStepDraft,
#              System.bool IsBodyDraft)`
#           → `## Remarks`：「Make the selections using IModelDocExtension::SelectByID2
#              **before** calling this method.」；选择 mark（官方 `## Parameters` 原文）：
#              方向项 **1** / 待拔模面 **2** / 拔模边 **4**
#           → ★★ **该页无 `Obsolete` 标注**（2026-10-09 实测 `grep -c -i obsolete` = **0**）
#         ② C:\swapi\types\IModelDoc2\InsertMfDraft.md · InsertMfDraft2.md
#           → 两页**都**写着 `Obsolete. Superseded by [[IFeatureManager::InsertMultifaceDraft]]`
#             ⇒ ★★ 官方**自己指认**了取代方向：**不是** `IModelDoc2` 族，而是 `IFeatureManager`
#             （★ 这正是 spec 239 `unsupported-path` 的 `alt` 自证要拦的坑：
#               把代码换成**已废弃的前代入口** = 没解决问题）
#         ③ D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt:6970
#           → `Feature InsertMultiFaceDraft(Double, Boolean, Boolean, Int32, Boolean, Boolean)`
#             ⇒ ★ **三源一致**（官方页 / 官方页的取代链 / 反射转储）：**6 参、顺序相同**
# 定位:   ★★ 2026-10-09（规格 239）**把创建路径从 `CreateDefinition` 改到官方入口**。
#         **改前**：本函数走 `CreateDefinition(swFmDraft=3)`，而
#         ① `swFmDraft` **不在**任何官方 `CreateDefinition` 宿主页的 `Type` 清单里（spec 238 已证）；
#         ② 本仓**真机证据**：`CreateDefinition(3)` 返回 `None`（同族 34/35/37/118 都正常返回）。
#         ⇒ ★ 那不是「参数没调对」，是**这条路径官方不支持**（spec 239 的 `unsupported-path` 判据）。
#         ★★ **不宣称它真机可用**：本规格是**离线切片**，**未跑 COM**（需业主另行授权）——
#            `SHEET_METAL_RUNTIME_STATUS["create_draft"]` 因此写 `(None, …)`（未测），**不是** `True`。
# 单位:   官方 `Angle` 是**弧度**（页里明写 "Draft angle in radians"）；
#         本仓 spec 层一律用**度** ⇒ 在 COM 边界处 `math.radians()` 转换。
# ⚠ `face_ref` 形参**仍未使用**（`mcp-server/tool_specs_batch4.py` 已把它登记为真实缺陷并显式省略）
#   ⇒ 选择由调用方在调用前完成，与本页 `## Remarks` 一致。
# ⚠ 本函数为照官方页改写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_draft(model, face_ref, spec: DraftFeatureSpec):
    """@brief 在已选中的面上创建原生拔模特征。

    调用前必须先用 ``IModelDocExtension::SelectByID2`` 选好（官方 ``## Remarks``）：
    方向项 **mark 1**、待拔模面 **mark 2**、拔模边 **mark 4**。
    """
    spec.validate()
    manager = get_com_member(model, "FeatureManager")
    #: ★ `Angle` 官方单位是**弧度**；spec 层是度 ⇒ 边界处转换。
    #: ★ `reverse_direction` ↔ 官方 `FlipDir`（「True to flip the direction of the draft」）。
    feature = get_com_member(manager, "InsertMultiFaceDraft",
                             float(math.radians(spec.angle)),
                             bool(spec.reverse_direction),
                             bool(spec.edge_draft),
                             int(spec.prop_type),
                             bool(spec.is_step_draft),
                             bool(spec.is_body_draft))
    if feature is None:
        raise RuntimeError("InsertMultiFaceDraft 创建失败")
    return feature


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（非开源项目，无第三方许可）
# 文件:   C:\swapi\types\IGussetFeatureData\
#           （成员 19 项：SetSupportingFaces / GetSupportingFaces /
#             ProfileType / ProfileDistance1..4 / ProfileAngle /
#             Thickness / ThicknessType / UseAngle / ProfileLocation /
#             OffsetUsed / FlipOffsetDirection …）
# 定位:   swFmSMGusset(118) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member IGussetFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性。上列属性名逐项取自 C:\swapi 成员目录，未臆造。
# ⚠ 支撑面须由调用方先用 SelectByID2 选好；本函数不代为选面。
# ⚠ 本函数为照官方签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_gusset(model, spec: GussetSpec):
    """@brief 在已选中的支撑面区域创建原生钣金加强筋。"""
    spec.validate()

    def _apply(data):
        # ⚠⚠⚠ **完整根因（2026-10-01 真机 + 官方类型表确证）**：
        #   本函数创建的是 **钣金**加强筋（`swFmSMGusset=118`，枚举描述明写
        #   "**Sheet metal** gusset"），其特征数据接口是
        #   **`ISMGussetFeatureData`**（`category: Feature Interfaces/Sheet metal`，
        #   28 个属性）；而**原代码用的是 `IGussetFeatureData`** ——
        #   那是 **`Feature Interfaces/Weldments`**（焊件）的接口（19 个成员）。
        #
        #   **两个接口共有成员只有 3 个**（`AccessSelections` / `ProfileType` /
        #   `ReleaseSelectionAccess`）⇒ 原设的 4 个属性名**全部来自焊件接口**
        #   ⇒ 拿到的对象**不是那个接口** ⇒ **对任何成员都没反应**
        #   （真机实测：连**读**都读不到），表现为
        #   `Property '<unknown>.Thickness' can not be set`。
        #
        #   **⇒ 改名为 SM 接口的成员**（映射见下），长度/角度语义不变。
        # ⚠⚠ **官方 `ISMGussetFeatureData` 的 Remarks 把创建步骤写成 4 步，
        #   而第 3 步的**头一句**是「Specify `ProfileDimensionScheme`」——
        #   本函数原先**从未设过它**（只设了 4 个尺寸属性）。**
        #   官方 `UseAngleDimForProfile` 更明写「**valid only if
        #   ProfileDimensionScheme is set to 1**」⇒ 不设 scheme 就设角度维，
        #   那个属性**可能根本不生效**。⇒ 先设 scheme。
        data.ProfileDimensionScheme = GUSSET_PROFILE_DIMENSIONS
        data.GussetThickness = float(spec.thickness)          # 原 Thickness（焊件名）
        # ⚠ 官方 Remarks 在 scheme=1 下给了**两种互斥的**标注方案，二选一：
        #   · **两条腿**：`ProfileLengthDim`(d1) + `ProfileHeightDim`(d2)
        #     + **`UseAngleDimForProfile = false`**
        #   · **d1 腿 + 它与加强筋的夹角**：`ProfileLengthDim` + `ProfileAngleDim`
        #     + **`UseAngleDimForProfile = true`**
        #   ⇒ **按 spec 有没有给角度来选**，不无条件置 true。
        #     （无条件置 true 而 `ProfileAngleDim` 是 0，是**自相矛盾**的标注方案。）
        _has_angle = bool(spec.profile_angle)
        data.UseAngleDimForProfile = _has_angle
        data.ProfileLengthDim = float(spec.profile_distance_2)   # 原 ProfileDistance2
        if _has_angle:
            data.ProfileAngleDim = float(spec.profile_angle)     # 原 ProfileAngle
        else:
            data.ProfileHeightDim = float(spec.profile_distance_1)  # 原 ProfileDistance1
        # 官方 `UseOffset`：「**After setting this property to true, set the offset
        #   distance.** **If a reference point is not set, the offset is applied to an
        #   assumed reference point.**」+ Remarks 第 2 步：「**If you do not pre-select
        #   any of these entities, then you must set `UseOffset` to true**」
        #   ⇒ 本函数**不预选参照点** ⇒ **必须**置 true，并设 offset 距离。
        data.UseOffset = True
        data.OffsetDistance = 0.0

    return _create_from_definition(model, SW_FM_SM_GUSSET, _apply)


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（同文件 BaseFlangeSpec / OneBendSpec 等）
# 定位:   扫掠法兰 spec。字段逐项对应 C:\swapi\types\ISweptFlangeFeatureData\
#         的 Thickness / StartOffset / EndOffset / BendRadius / ReliefRatio。
# ⚠ 照既有模式扩写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 枚举定义（SolidWorks.Interop.swconst.dll）
# 文件:   C:\swapi\enums\swSweptFlangePositionTypes_e.md
# 定位:   ISweptFlangeFeatureData.FlangePosition 的取值域。
# 官方示例: C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md
#           第 75 行 `swFeatData.FlangePosition =
#             swSweptFlangePositionTypes_e.swSweptFlangePositionType_MaterialInside`
# 取值:   官方 3 项全量照录。
# ⚠ 本表为静态照录，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
SWS_SWEPT_FLANGE_POSITIONS = {
    "material_inside": 1,     # swSweptFlangePositionType_MaterialInside
    "material_outside": 2,    # swSweptFlangePositionType_MaterialOutside
    "bend_outside": 3,        # swSweptFlangePositionType_BendOutside
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 使用示例（非开源项目，无第三方许可）
# 文件:   C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md 第 74-87 行
# 定位:   SweptFlangeSpec 的字段集与默认值，**逐条对应官方示例所设的 14 个属性**：
#           EndOffset=0 / StartOffset=0 / FlangePosition=MaterialInside /
#           FlattenAlongPath=False / TrimSideBends=False / ReverseDirection=False /
#           UseDefaultBendAllowance=True / UseDefaultBendRelief=True /
#           UseGaugeTable=False / UseMaterialSheetMetalParameters=False /
#           OverrideDefaultSheetMetalParameters=False
#           以及官方**不设**的两项：
#           · Thickness      → 厚度从基体法兰继承，故本类 thickness 默认 None
#           · ReliefRatio    → 官方走 UseDefaultBendRelief=True，不设此属性
#         另加 BendRadius / UseDefaultRadius（官方示例设 UseDefaultRadius=False
#         但未设 BendRadius，靠 SolidWorks 自身默认值兜底；本类默认 True 更稳，
#         这属于本仓库的工程判断，已在 examples/09_sheet_metal.py 末尾标注）。
# ⚠ 本类为照官方示例新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class SweptFlangeSpec:
    """@brief 扫掠法兰参数，长度单位为米。

    ⚠ ``thickness`` 默认为 ``None``：**官方示例并不设 Thickness**，
      而是用 ``UseMaterialSheetMetalParameters=False`` +
      ``OverrideDefaultSheetMetalParameters=False`` 让厚度**从基体法兰继承**
      （见 ``C:\\swapi\\examples\\Create_Swept_Flange_Example_VBNET.md``）。
      传 None 即复现官方行为；确有独立厚度时才显式给值。
    """

    start_offset: float
    end_offset: float = 0.0
    thickness: float | None = None
    bend_radius: float = 0.0
    use_default_radius: bool = True
    flange_position: int = SWS_SWEPT_FLANGE_POSITIONS["material_inside"]
    flatten_along_path: bool = False
    trim_side_bends: bool = False
    use_default_bend_relief: bool = True
    use_gauge_table: bool = False
    use_material_parameters: bool = False
    override_default_sheet_metal_parameters: bool = False
    reverse_direction: bool = False

    def validate(self) -> None:
        if self.thickness is not None and self.thickness <= 0:
            raise ValueError("扫掠法兰厚度必须大于 0")
        if self.start_offset < 0:
            raise ValueError("扫掠法兰起始偏移不能小于 0")
        if self.end_offset < 0:
            raise ValueError("扫掠法兰结束偏移不能小于 0")
        if self.bend_radius < 0:
            raise ValueError("折弯半径不能小于 0")
        if self.flange_position not in SWS_SWEPT_FLANGE_POSITIONS.values():
            raise ValueError(
                "flange_position 必须是 SWS_SWEPT_FLANGE_POSITIONS 中的值"
            )


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名 + ★ 官方使用示例
# 文件:   签名: C:\swapi\types\ISweptFlangeFeatureData\（32 成员）
#         示例: C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md
#               C:\swapi\examples\Create_Swept_Flange_Using_Gauge_Table_Example_CSharp.md
# 定位:   swFmSweptFlange(117) 的属性装配。**该接口无 Initialize 成员**
#         （sw_know.py member ISweptFlangeFeatureData Initialize → [SWK_NOT_FOUND]），
#         故只设属性。属性集合与顺序**照官方示例逐行对齐**。
# 官方调用序列（Example_VBNET 第 37-88 行，摘录）:
#         1) Part.FeatureManager.InsertSheetMetalBaseFlange2(...)   ← 前置：先有基体法兰
#         2) 选轮廓草图 → GetSelectedObject6 → ClearSelection2
#         3) 选路径边   → GetSelectedObject6 → ClearSelection2
#         4) swFeatMgr.CreateDefinition(swFeatureNameID_e.swFmSweptFlange)
#         5) 逐个设 EndOffset / FlangePosition / FlattenAlongPath /
#            OverrideDefaultSheetMetalParameters / Path / Profile /
#            ReverseDirection / StartOffset / TrimSideBends /
#            UseDefaultBendAllowance / UseDefaultBendRelief /
#            UseDefaultRadius / UseGaugeTable / UseMaterialSheetMetalParameters
#         6) swFeatMgr.CreateFeature(swFeatData)
# 本次改动: 初版只设了 7 个属性且**错误地设了 Thickness**。对照官方示例后：
#         · 删掉 Thickness（官方不设，厚度从基体法兰继承）
#         · 补齐 FlangePosition / FlattenAlongPath / TrimSideBends /
#           UseDefaultBendRelief / UseGaugeTable / UseMaterialSheetMetalParameters /
#           OverrideDefaultSheetMetalParameters 共 7 个
#         · 删掉 ReliefRatio（官方示例走 UseDefaultBendRelief=True，不设此属性）
# ⚠ 官方示例**没有**为这条路径调用 AccessSelections / ReleaseSelectionAccess
#   （与 Access_Selections_Example 那类需要编辑选区的示例不同），
#   故本函数同样不调，避免多余副作用。
# ⚠ 本函数为照官方签名与官方示例新写，未在本机实测（见 AGENTS.md 铁律 2）
# ────────────────────────────────────────────────────────────────────
def create_swept_flange(model, path_ref, profile_ref, spec: SweptFlangeSpec):
    """@brief 沿路径扫掠创建原生扫掠法兰（属性装配照官方示例对齐）。

    :param path_ref: 扫掠路径（边）。官方示例用 ``SelectByRay`` 选边后
        ``SelectionManager.GetSelectedObject6(1, -1)`` 取得。
    :param profile_ref: 扫掠轮廓（草图）。
    :note: **调用前必须已有基体法兰**（``swFmBaseFlange``）——
        官方示例正是先建基体法兰再建扫掠法兰，否则厚度无从继承。
    """
    spec.validate()

    def _apply(data):
        data.EndOffset = float(spec.end_offset)
        data.StartOffset = float(spec.start_offset)
        data.FlangePosition = int(spec.flange_position)
        data.FlattenAlongPath = bool(spec.flatten_along_path)
        data.TrimSideBends = bool(spec.trim_side_bends)
        data.ReverseDirection = bool(spec.reverse_direction)
        data.UseDefaultRadius = bool(spec.use_default_radius)
        if not spec.use_default_radius:
            data.BendRadius = float(spec.bend_radius)
        data.UseDefaultBendAllowance = True
        data.UseDefaultBendRelief = bool(spec.use_default_bend_relief)
        data.UseGaugeTable = bool(spec.use_gauge_table)
        data.UseMaterialSheetMetalParameters = bool(spec.use_material_parameters)
        data.OverrideDefaultSheetMetalParameters = bool(
            spec.override_default_sheet_metal_parameters
        )
        # 厚度：官方示例不设，走基体法兰继承；调用方显式给值时才覆盖。
        if spec.thickness is not None:
            data.Thickness = float(spec.thickness)
        if path_ref is not None:
            data.Path = path_ref
        if profile_ref is not None:
            data.Profile = profile_ref

    return _create_from_definition(model, SW_FM_SWEPT_FLANGE, _apply)


# ══════════════════════════════════════════════════════════════════════
# 规格 209 · B4-2（idx 173 hem）+ B2-1（idx 336 unfold）
# ══════════════════════════════════════════════════════════════════════
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_sheet_metal.py —— 追加 `create_hem` / `create_unfold`
# 定位:   ★ 规格 `specs/209-union-adopt-18/`（候选来自规格 207 的逐条核实）：
#   · **idx 173 `hem`** —— ★★ 裁决书说「dp5 的发现**比实现本身更值**」：别家调的
#     `InsertHemFeature2` 在 `C:\swapi\types\` **全树零命中**（★ 我们按 `*InsertHem*` 全量扫过 ⇒ 零），
#     **官方真名是 `IFeatureManager::InsertSheetMetalHem2`（16 形参）**；★ 且它的 `hem_type` 映射
#     把官方 `swHemTypes_e`（**Open=0 / Closed=1**）**正好互换**、并**漏掉 `Double=4`**
#     ⇒ ★★ 裁决书要求「这三处错误应做成 L2/L3 静态断言」（谁再照它抄就当场抓住）✓
#   · **idx 336 `unfold`** —— 裁决书：官方**没给 mark** ⇒ 必须先真机定出"可建对象"，
#     且前置判据用回读（事实 8），不许信返回值 ✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过；★★ 例子给的是**调用序**，签名与 Remarks 都给不出）：
#   · `C:\swapi\types\IFeatureManager\InsertSheetMetalHem2.md` ——
#     `Feature InsertSheetMetalHem2(System.int Type, System.int Position, System.bool Reverse,
#      System.double DLength, System.double DGap, System.double DAngle, System.double DRad,
#      System.double DMiterGap, CustomBendAllowance PCBA, System.bool UseDefaultRelief,
#      System.int ReliefType, System.int ReliefTearTypes, System.bool UseReliefRatio,
#      System.double ReliefRatio, System.double ReliefWidth, System.double ReliefDepth)` —— **16 形参**
#     ★★ `## Remarks` 逐字给了**四步前置**：「1. Call `IFeatureManager::CreateCustomBendAllowance`…
#       2. Initialize the CustomBendAllowance object. 3. Assign PCBA… 4. **Select one or more edges**
#       in the sheet metal model to which to add the specified hem.」✓
#   · `C:\swapi\examples\Insert_Sheet_Metal_Hem_Example_VB.md` —— ★★ **调用序**（逐字）：
#     `CreateCustomBendAllowance()` → `CBA.Type = 2` · `CBA.KFactor = 0.5` →
#     `InsertSheetMetalHem2(swHemTypeOpen, swHemPositionTypeOutside, False, 0.01, 0.01, 0, 0.005,
#      0.0011, CBAObject, False, swSheetMetalReliefObround, 0, True, 1#, 0, 0)` → `GetDefinition` ✓
#   · `C:\swapi\enums\swHemTypes_e.md` —— Open=**0** · Closed=**1** · TearDrop=2 · Rolled=3 · **Double=4**
#   · `C:\swapi\enums\swHemPositionTypes_e.md` —— Inside=1 · Outside=2
#   · `C:\swapi\enums\swSheetMetalReliefTypes_e.md` —— Rectangular=1 · Tear=2 · Obround=3 · None=4 · TearBend=5
#   · `C:\swapi\enums\swReliefTearTypes_e.md` —— Rip=1 · Extend=2
#   · `C:\swapi\types\IModelDoc2\InsertSheetMetalUnfold.md` —— `void InsertSheetMetalUnfold()`
#     ★★ `## Remarks` 逐字：「**Select the objects for the unfold feature before calling this
#       method.**」（★ **没给 mark** ⇒ 见下面的示例）
#   · ★★★ `C:\swapi\examples\Insert_and_Access_Fold_Feature_Example_VB.md` —— **Unfold 与 Fold 共用**这份示例，
#     而它逐字给出了**调用序与 mark**（★ 这是"官方没给 mark"的唯一出处）：
#     ```
#     ClearSelection2 True
#     SelectByID2("", "FACE", x,y,z, False, **1**, Nothing, 0)          ← 固定面 mark = 1
#     SelectByID2("EdgeBend3", "BODYFEATURE", x,y,z, True, **4**, …)    ← 要展开的折弯 mark = 4
#     …（多条折弯，每条都 mark 4，Append=True）
#     swModel.InsertSheetMetalUnfold
#     ```
#     ★ 同一份示例里 **Fold** 那一段多一步：先选已存在的 `Unfold1` 特征（**mark 0**），
#       再是「固定面 mark 1 + 折弯 mark 4」⇒ ★★ **本模块的 mark 表就是从这里来的，不是猜的** ✓
#   · `C:\swapi\types\IFeatureManager\GetFlatPatternFolder.md` → `IFlatPatternFolder::GetFlatPatternCount`
#     （★ 读侧：展开结果的可回读判据 —— 裁决书点名要它）✓
# 许可:   本仓库 MIT。无第三方代码引入（★ 全部按官方签名与官方示例自建）。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **别家的三处错误 → 本模块的 L2/L3 静态断言**（裁决书强制要求，见 tests）：
#   ① 成员名 `InsertHemFeature2` —— ★ 官方全树**零命中**（真名 `InsertSheetMetalHem2`）；
#   ② `hem_type` 把 `Open=0` / `Closed=1` **互换**；
#   ③ **漏掉 `Double=4`**（官方 `swHemTypes_e` 有 5 个成员）。
#   ⇒ ★ 本模块把三者各自做成**机器可判的判据**（常量表 + 测试），不靠注释提醒 ✓

#: ★ 官方 `swHemTypes_e`（★ **五个成员一个不漏**，逐值抄自 `C:\swapi\enums\`）
#: enum-gate: enum swHemTypes_e
HEM_TYPES = {"open": 0, "closed": 1, "teardrop": 2, "rolled": 3, "double": 4}
#: ★ 官方 `swHemPositionTypes_e`
#: ★★ 2026-10-08（spec 223）**两源冲突，按铁律 4 取反射**：
#:   · md（`C:\swapi\enums\swHemPositionTypes_e.md`）写 `Inside = 1` / `Outside = 2`；
#:   · **出厂反射**（`_raw/enum_values_sldworks.txt`）写 `swHemPositionTypeInside = 0` /
#:     `swHemPositionTypeOutside = 1`。
#:   ⇒ ★ 铁律 4「冲突以出厂类型库为准」⇒ 本表取 **0 / 1** ✓
#:   ⚠ **未在真机复核** —— 而 `create_hem` 在本机**五种形态全部回 `None`**（事实 34 / 53）
#:     ⇒ ★ 改它**不会回退任何已验证的路径**；★ 若将来真机证明反射有误，**这里就是那处待裁**。
#:   ★ 每行补 `# sw<官方成员名>` ⇒ 本表**首次进入** `check_enum_values_vs_reflection.py` 的覆盖面
#:     （原先无注释 ⇒ 门禁看不见 ⇒ 值错了也没人抓）✓
HEM_POSITIONS = {
    "inside": 0,     # swHemPositionTypeInside
    "outside": 1,    # swHemPositionTypeOutside
}
#: ★ 官方 `swSheetMetalReliefTypes_e`
#: enum-gate: enum swSheetMetalReliefTypes_e
HEM_RELIEFS = {"rectangular": 1, "tear": 2, "obround": 3, "none": 4, "tear_bend": 5}
#: ★ 官方 `swReliefTearTypes_e`
#: enum-gate: enum swReliefTearTypes_e
HEM_RELIEF_TEARS = {"rip": 1, "extend": 2}

#: ★★ **Unfold / Fold 的 mark 表**（★ 逐字取自官方示例 `Insert_and_Access_Fold_Feature_Example_VB.md`；
#:   ★★ **不许跨条复制** —— 本表只属于这两个成员，钣金其它成员的 mark 在本文件里各写各的）✓
#: enum-gate: member InsertSheetMetalFold
UNFOLD_MARKS = {"fixed_face": 1, "bends": 4}

#: ★ `swSelectionMarkAction_e`（★ 逐值抄自 `C:\swapi\enums\swSelectionMarkAction_e.md`）
#: ★★ **`SetSelectedObjectMark` 的第 3 参是它，不是 `-1`** —— 我第一版传 `-1` ⇒ 真机回 **`false`**
#:   而**它不报错**（★ 只是 mark 没设上）；★ 官方两份示例逐字都用 **`swSelectionMarkSet`(0)** ✓
#: enum-gate: enum swSelectionMarkAction_e
SELECTION_MARK_ACTION = {"set": 0, "append": 1, "remove": 2, "clear": 3}


def _flat_pattern_count(model) -> "int | None":
    """★ 读**平展型式个数**（`IFeatureManager::GetFlatPatternFolder` → `IFlatPatternFolder::GetFlatPatternCount`）。

    ★ 它是 **unfold / fold 的可回读判据**（裁决书点名）—— ★ 读不到就回 `None`（★ 「读不到」≠「0 个」）✓
    """
    try:
        folder = get_com_member(get_com_member(model, "FeatureManager"), "GetFlatPatternFolder")
        if folder is None:
            return None
        return int(get_com_member(folder, "GetFlatPatternCount") or 0)
    except Exception:                                          # noqa: BLE001
        return None


def _feature_names_snapshot(model) -> list:
    out = []
    for feat in iter_features(model):
        out.append(str(get_com_member(feat, "Name") or ""))
    return out


def _bbox_mm(model):
    """★ 包围盒（**毫米**）—— 取不到回 `None`（★ 与"没变"分开）✓"""
    try:
        from sw_part import get_bounding_box
        bb = get_bounding_box(model)
        if isinstance(bb, dict):
            return {"min": [round(float(v), 6) for v in bb["min"]],
                    "max": [round(float(v), 6) for v in bb["max"]]}
    except Exception:                                          # noqa: BLE001
        pass
    return None


def _select_fixed_face_and_bends(model, bend_feature_names, *, face_index: int = 0,
                                 pre_select_names=()) -> dict:
    """★ 按**官方示例的调用序**选中「固定面（mark 1）+ 若干折弯特征（mark 4）」。

    ★★ 两条**本仓实测过的选择纪律**都用上了：
      · **面不能按名字选**（事实 32）⇒ 走 `IEntity.Select4`（**按对象**）**再补 mark**
        （★ `Select4` **没有 mark 形参** ⇒ 用 `ISelectionMgr::SetSelectedObjectMark`）✓
      · **特征可以按名字选** ⇒ 折弯走 `SelectByID2(name, "BODYFEATURE", …, Mark=4, …)` ✓
    :param pre_select_names: ★ **先于固定面**要选中的特征名（**mark 0**）—— ★ Fold 那一格官方示例
        就是先选已存在的 `Unfold1`；★ 必须在**清完选区之后**选，否则会被 `ClearSelection2` 清掉 ✓
    """
    import sw_selection_spec as SS                                      # noqa: E402
    from sw_part import _empty_callout                                  # noqa: E402
    ext = get_com_member(model, "Extension")
    info = {"fixed_face_index": int(face_index), "bend_feature_names": [str(x) for x in
                                                                       (bend_feature_names or ())],
            "pre_select_names": [str(x) for x in (pre_select_names or ())],
            "face_select_count": None, "mark_set": None, "mark_readback": None,
            "bends_selected": None, "total_count": None, "errors": []}
    get_com_member(model, "ClearSelection2", True)
    #: ⓪ ★ 先选**前置特征**（mark 0）—— ★ 必须在 ClearSelection2 **之后**
    pre_ok = 0
    for name in info["pre_select_names"]:
        try:
            got = get_com_member(ext, "SelectByID2", name, "BODYFEATURE", 0.0, 0.0, 0.0,
                                 True, 0, _empty_callout(), 0)
            pre_ok += 1 if got else 0
        except Exception as exc:                                        # noqa: BLE001
            info["errors"].append("前置特征 %s：%s: %s" % (name, type(exc).__name__, str(exc)[:100]))
    info["pre_selected"] = pre_ok
    #: ① 固定面：按对象选（事实 32）⇒ 再补 mark 1（Select4 没有 mark 形参）
    try:
        faces = SS.entities_on_body(model, "FACE")
        if not faces:
            raise RuntimeError("体上没有面")
        if face_index < 0 or face_index >= len(faces):
            raise RuntimeError("face_index=%d 越界（共 %d 个面）" % (face_index, len(faces)))
        SS.select_object(model, faces[face_index])
        mgr = get_com_member(model, "SelectionManager")
        #: ★★ 第 3 参必须是 `swSelectionMarkSet`(0) —— 传 `-1` 会**静默不生效**（真机回 false，无报错）
        info["mark_set"] = get_com_member(mgr, "SetSelectedObjectMark", 1,
                                          int(UNFOLD_MARKS["fixed_face"]),
                                          int(SELECTION_MARK_ACTION["set"]))
        #: ★ 判据是**回读 mark**，不是那个返回值（★ 事实 8 的同一形态）
        try:
            info["mark_readback"] = int(get_com_member(mgr, "GetSelectedObjectMark", 1))
        except Exception as exc:                                        # noqa: BLE001
            info["errors"].append("回读 mark：%s" % str(exc)[:100])
        info["face_select_count"] = SS.get_selection_count(model)
    except Exception as exc:                                            # noqa: BLE001
        info["errors"].append("固定面：%s: %s" % (type(exc).__name__, str(exc)[:120]))
    #: ② 折弯特征：按名字选（★ 事实 32 —— 按名字选**只对特征成立**）
    ok_bends = 0
    for name in info["bend_feature_names"]:
        try:
            got = get_com_member(ext, "SelectByID2", name, "BODYFEATURE", 0.0, 0.0, 0.0,
                                 True, int(UNFOLD_MARKS["bends"]), _empty_callout(), 0)
            ok_bends += 1 if got else 0
        except Exception as exc:                                        # noqa: BLE001
            info["errors"].append("折弯 %s：%s: %s" % (name, type(exc).__name__, str(exc)[:100]))
    info["bends_selected"] = ok_bends
    try:
        info["total_count"] = SS.get_selection_count(model)
    except Exception as exc:                                            # noqa: BLE001
        info["errors"].append("回读计数：%s" % str(exc)[:100])
    #: ★★ **逐条回读 mark**（★ 裁决书要求"前置判据用回读 `GetSelectedObjectCount2(-1)`"——
    #:   本函数把**计数与每一条的 mark** 都读回来，★ 调用方据此判"选择契约成立不成立"）✓
    marks = []
    try:
        mgr = get_com_member(model, "SelectionManager")
        for i in range(1, int(info["total_count"] or 0) + 1):
            try:
                marks.append(int(get_com_member(mgr, "GetSelectedObjectMark", i)))
            except Exception:                                           # noqa: BLE001
                marks.append(None)
    except Exception as exc:                                            # noqa: BLE001
        info["errors"].append("回读 mark 列表：%s" % str(exc)[:100])
    info["marks_readback"] = marks
    info["contract_ok"] = (int(info["total_count"] or 0) == (1 + len(info["bend_feature_names"]))
                           and marks[:1] == [int(UNFOLD_MARKS["fixed_face"])]
                           and all(m == int(UNFOLD_MARKS["bends"]) for m in marks[1:]))
    return info


def _create_unfold_or_fold(model, entry: str, call, bend_feature_names, face_index: int,
                           pre_select_names=()) -> dict:
    """★ `unfold` / `fold` 的**共用实现**（两者只差调用的那个零参成员）。

    ★★ 判据（规则 6）：① **回读特征树**有没有多出那个特征；② **平展型式个数** `_flat_pattern_count`；
      ③ 特征树/包围盒的**前后读数**都留下来（★ 读不到一律回 `None`，**不当成"没变"**）✓
    """
    out: dict = {
        "ok": False, "entry": entry, "selection": None, "tree_before": None, "tree_after": None,
        "new_features": [], "flat_pattern_count_before": None, "flat_pattern_count_after": None,
        "bbox_before": None, "bbox_after": None, "bbox_comparable": None, "returned": None,
        "error": None, "note": None,
        "★": "判据 = **回读特征树增量 + 平展型式个数**；★ mark 表取自官方示例"
             "（%s）；★ `Select4` 没有 mark 形参 ⇒ 面用 `SetSelectedObjectMark` 补 mark"
             % str(UNFOLD_MARKS),
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    try:
        names_before = _feature_names_snapshot(model)
        out["tree_before"] = len(names_before)
        out["flat_pattern_count_before"] = _flat_pattern_count(model)
        out["bbox_before"] = _bbox_mm(model)
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "前置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["selection"] = _select_fixed_face_and_bends(model, bend_feature_names,
                                                    face_index=face_index,
                                                    pre_select_names=pre_select_names)
    if out["selection"]["total_count"] == 0:
        out["error"] = ("选完**回读计数为 0** ⇒ 什么都没选中（★ 事实 8：不许信返回值）"
                        "；selection 里有逐条报错")
        return out
    try:
        out["returned"] = call()
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out
    try:
        names_after = _feature_names_snapshot(model)
        out["tree_after"] = len(names_after)
        out["new_features"] = [n for n in names_after if n not in names_before]
        out["flat_pattern_count_after"] = _flat_pattern_count(model)
        out["bbox_after"] = _bbox_mm(model)
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "后置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["bbox_comparable"] = out["bbox_before"] is not None and out["bbox_after"] is not None
    out["ok"] = (out["tree_after"] > out["tree_before"]) and bool(out["new_features"])
    if not out["ok"]:
        out["error"] = ("回读判据未过：特征树 %r → %r（要**增加**）、新特征 %r —— "
                        "★ 它回 `void` ⇒ 只能靠回读（规则 6）"
                        % (out["tree_before"], out["tree_after"], out["new_features"]))
    return out


def _as_name_list(names) -> list:
    """★ 把「特征名清单」归一成 `list[str]`（★ 工具层传的是**逗号分隔字符串**，能力层收 list）。

    ★ 为什么不在工具层做转换：★ 规则 2 说「换算只在边界做一次」，★ 而**名字不是单位** ——
      ★ 让能力层**两种都收**，调用方（脚本 / 工具 / 探针）都不必知道对方的形状 ✓
    """
    if names is None:
        return []
    if isinstance(names, str):
        return [x.strip() for x in names.split(",") if x.strip()]
    return [str(x).strip() for x in names if str(x).strip()]


def create_unfold(model, bend_feature_names, *, face_index: int = 0) -> dict:
    """★ **插入展开特征**（★ 官方 `IModelDoc2::InsertSheetMetalUnfold()`，**零参**）。

    :param bend_feature_names: 要展开的**折弯特征名**（官方示例里的 `EdgeBend3` 那一类）。
        ★ 收 `list[str]` **或**逗号分隔的字符串；★ 留空表示**不选**任何 `mark 4` 的对象 ——
        ★★ 而**真机实测：那样也能建出 `展开1`**（★ `mark 4` 不是必需的，见模块状态表）✓
    :param face_index: **固定面**在体上的序号（0 基 —— 本仓的声明式选择；★ 面**不能按名字选**，事实 32）。
    :returns: 见 :func:`_create_unfold_or_fold`（判据 = 特征树增量 + 平展型式个数 + 逐条 mark）。
    """
    return _create_unfold_or_fold(
        model, "IModelDoc2::InsertSheetMetalUnfold()",
        lambda: get_com_member(model, "InsertSheetMetalUnfold"),
        _as_name_list(bend_feature_names), face_index)


def create_fold(model, bend_feature_names, *, face_index: int = 0,
                unfold_feature_name: str = "") -> dict:
    """★ **插入折叠特征**（★ 官方 `IModelDoc2::InsertSheetMetalFold()`，**零参**）。

    :param unfold_feature_name: 官方示例在 Fold 之前先选已存在的 `Unfold1`（**mark 0**）
        —— ★ 留空表示不选它（本函数**不替调用方猜**；选与不选**都以回读为准**）。
    ★★ 选它的那一步走 `pre_select_names`（★ **在 `ClearSelection2` 之后**）——
      ★ 我第一版把它放在 `call()` 里 ⇒ 会被选择函数开头的清选区**清掉**（★ 顺序错，静默失效）✓
    """
    pre = [str(unfold_feature_name)] if unfold_feature_name else []
    return _create_unfold_or_fold(
        model, "IModelDoc2::InsertSheetMetalFold()",
        lambda: get_com_member(model, "InsertSheetMetalFold"),
        _as_name_list(bend_feature_names), face_index, pre_select_names=pre)


def create_hem(model, edge_selector, *, hem_type: str = "open", position: str = "outside",
               reverse: bool = False, length_mm: float = 0.01, gap_mm: float = 0.01,
               angle_deg: float = 0.0, radius_mm: float = 0.005, miter_gap_mm: float = 0.0011,
               use_default_relief: bool = False, relief: str = "obround",
               relief_tear: str = "rip", use_relief_ratio: bool = True,
               relief_ratio: float = 1.0, relief_width_mm: float = 0.0,
               relief_depth_mm: float = 0.0, k_factor: float = 0.5,
               allow_unverified: bool = False) -> dict:
    """★ **在选中的边上加折边（hem）**（★ 官方 `IFeatureManager::InsertSheetMetalHem2`，**16 形参**）。

    ⚠⚠ **本入口在本机实测失败**（`SHEET_METAL_RUNTIME_STATUS["create_hem"]`，★ 五种形态全回 `None`）
      ⇒ ★ 默认**先抛**（`require_verified`），**不让用户吃一个裸 COM 错误**；
      ★ 要复跑那个负实验（探针/测试）请显式传 `allow_unverified=True` ✓
    :param edge_selector: 声明式选择器（★ 规则 3）—— `"index:<n>"`（体上第 n 条边）或
        `"__current_selection__"`。★ 边**不能按名字选**（事实 32）⇒ 走 `IEntity.Select4`。
    :param hem_type: `open`(0) / `closed`(1) / `teardrop`(2) / `rolled`(3) / **`double`(4)**。
        ★★ 官方 `swHemTypes_e` **五个成员一个不漏**（★ 别家把 Open/Closed 互换、还漏了 `double`）✓
    :param position: `inside`(1) / `outside`(2)。
    :param relief: `rectangular`(1) / `tear`(2) / `obround`(3) / `none`(4) / `tear_bend`(5)。
    :param relief_tear: `rip`(1) / `extend`(2)（★ 只当 `relief="tear"` 时有意义）。
    :param k_factor: 自定义折弯系数里的 K 因子（官方示例用 0.5）。
    :returns: `{ok, entry_used, feature, feature_type, hem_type_readback, tree_before/after,
        face_count_before/after, bbox_before/after, bbox_changed, bbox_comparable, api_args, error}`

    ★★ **判据（规则 6）**：① **特征树增加 1**（它**回 `IFeature`**，但本函数**不拿返回值当判据**）；
      ② **面上的个数变化**（折边必然改变体的面数）或**包围盒变化** —— ★ 两者都**回读**✓
    ★★ **官方 `## Remarks` 的四步前置**照做：`CreateCustomBendAllowance` → 设 `Type`/`KFactor`
      → 传 `PCBA` → **先选中要加折边的边** ✓
    """
    if not allow_unverified:
        require_verified("create_hem")     #: ★ 本机实测失败 ⇒ 调用前抛**带原因**的错误
    import sw_selection_spec as SS                                      # noqa: E402
    from sw_part import _empty_callout                                  # noqa: E402
    out: dict = {
        "ok": False, "entry_used": "IFeatureManager::InsertSheetMetalHem2(16 形参)",
        "feature": None, "feature_type": None, "hem_type_readback": None,
        "tree_before": None, "tree_after": None, "face_count_before": None,
        "face_count_after": None, "bbox_before": None, "bbox_after": None,
        "bbox_changed": None, "bbox_comparable": None, "api_args": None, "error": None, "note": None,
        "★": "判据 = **特征树 +1** 与（面数变化 或 包围盒变化）；★ 两者都回读；"
             "★ 它回的 IFeature **不当判据**",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    ht = str(hem_type).strip().lower()
    if ht not in HEM_TYPES:
        out["error"] = ("未知的 hem_type %r；合法：%s"
                        % (hem_type, ", ".join(sorted(HEM_TYPES))))
        return out
    pos = str(position).strip().lower()
    if pos not in HEM_POSITIONS:
        out["error"] = ("未知的 position %r；合法：%s"
                        % (position, ", ".join(sorted(HEM_POSITIONS))))
        return out
    rel = str(relief).strip().lower()
    if rel not in HEM_RELIEFS:
        out["error"] = ("未知的 relief %r；合法：%s" % (relief, ", ".join(sorted(HEM_RELIEFS))))
        return out
    rt = str(relief_tear).strip().lower()
    if rt not in HEM_RELIEF_TEARS:
        out["error"] = ("未知的 relief_tear %r；合法：%s"
                        % (relief_tear, ", ".join(sorted(HEM_RELIEF_TEARS))))
        return out

    def _face_count():
        try:
            return len(SS.entities_on_body(model, "FACE"))
        except Exception:                                              # noqa: BLE001
            return None

    try:
        names_before = _feature_names_snapshot(model)
        out["tree_before"] = len(names_before)
        out["face_count_before"] = _face_count()
        out["bbox_before"] = _bbox_mm(model)
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "前置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["api_args"] = {
        "Type": HEM_TYPES[ht], "Position": HEM_POSITIONS[pos], "Reverse": bool(reverse),
        "DLength": float(length_mm), "DGap": float(gap_mm), "DAngle": float(angle_deg),
        "DRad": float(radius_mm), "DMiterGap": float(miter_gap_mm),
        "UseDefaultRelief": bool(use_default_relief), "ReliefType": HEM_RELIEFS[rel],
        "ReliefTearTypes": HEM_RELIEF_TEARS[rt], "UseReliefRatio": bool(use_relief_ratio),
        "ReliefRatio": float(relief_ratio), "ReliefWidth": float(relief_width_mm),
        "ReliefDepth": float(relief_depth_mm), "KFactor": float(k_factor),
    }
    #: ★★ **顺序照官方 `## Remarks` 逐字的第 1–4 步**：
    #:   ① `CreateCustomBendAllowance` → ② 初始化 → ③ 赋给 PCBA → ④ **然后**才「Select one or more
    #:   edges」。★★ 我第一版把**选边放在建 CBA 之前**（顺序反了）⇒ 真机回 `None`
    #:   —— ★ 与 unfold 那次同形：**失败的原因在我这边**（★ 教训：Remarks 的**步序**也是签名的一部分）✓
    try:
        manager = get_com_member(model, "FeatureManager")
        cba = call_com_member(manager, "CreateCustomBendAllowance")
        if cba is None:
            out["error"] = "CreateCustomBendAllowance 未返回对象（官方 Remarks 第 1 步）"
            return out
        #: ★ `ICustomBendAllowance::Type` 的 Remarks 逐字：「**use this property to set the value
        #:   for the type … 若你不把它放在最后设，最后设的那个属性会覆盖掉先前设的类型**」
        #:   ⇒ ★ 本段**先设 KFactor、最后设 Type**（官方示例是反的，但 KFactor 恰好也等于 2 ⇒ 巧合）✓
        cba.KFactor = float(k_factor)
        cba.Type = SW_BEND_ALLOWANCE_K_FACTOR
        #: 第 4 步：**此时才选中边**（★ 事实 32：边不能按名字选 ⇒ 走 `Select4` 按对象选）
        sel = (str(edge_selector).strip() or SS.CURRENT_SELECTION)
        if sel.startswith("index:"):
            SS.select_entity_by_index(model, "EDGE", int(sel.split(":", 1)[1]))
        elif sel != SS.CURRENT_SELECTION:
            raise ValueError("非法的边选择器 %r；合法：'index:<n>' 或 '__current_selection__'" % sel)
        out["selection_count_before_call"] = SS.get_selection_count(model)
        if out["selection_count_before_call"] <= 0:
            out["error"] = ("选完**回读计数为 0** ⇒ 没有边在选区里（★ 事实 8）"
                            "—— 折边必须先选中边（官方 Remarks 第 4 步）")
            return out
        args = out["api_args"]
        feature = get_com_member(manager, "InsertSheetMetalHem2",
                                 int(args["Type"]), int(args["Position"]), bool(args["Reverse"]),
                                 float(args["DLength"]), float(args["DGap"]), float(args["DAngle"]),
                                 float(args["DRad"]), float(args["DMiterGap"]), cba,
                                 bool(args["UseDefaultRelief"]), int(args["ReliefType"]),
                                 int(args["ReliefTearTypes"]), bool(args["UseReliefRatio"]),
                                 float(args["ReliefRatio"]), float(args["ReliefWidth"]),
                                 float(args["ReliefDepth"]))
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    if feature is None:
        out["error"] = ("InsertSheetMetalHem2 回 None ⇒ 折边没建出来"
                        "（★ 官方 Returns 是 IFeature ⇒ None 就是失败）")
        return out
    try:
        out["feature"] = str(get_com_member(feature, "Name") or "")
        out["feature_type"] = _feature_type(feature)
        definition = get_com_member(feature, "GetDefinition")
        if definition is not None:
            out["hem_type_readback"] = int(get_com_member(definition, "Type") or 0)
    except Exception as exc:                                            # noqa: BLE001
        out["note"] = "特征读回部分失败（不影响判据）：%s" % str(exc)[:120]
    try:
        names_after = _feature_names_snapshot(model)
        out["tree_after"] = len(names_after)
        out["face_count_after"] = _face_count()
        out["bbox_after"] = _bbox_mm(model)
    except Exception as exc:                                            # noqa: BLE001
        out["error"] = "后置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    out["bbox_comparable"] = out["bbox_before"] is not None and out["bbox_after"] is not None
    out["bbox_changed"] = (out["bbox_comparable"]
                           and out["bbox_before"] != out["bbox_after"])
    faces_changed = (out["face_count_before"] is not None and out["face_count_after"] is not None
                     and out["face_count_before"] != out["face_count_after"])
    out["ok"] = (out["tree_after"] == out["tree_before"] + 1) and (faces_changed
                                                                  or out["bbox_changed"])
    if not out["ok"]:
        out["error"] = ("回读判据未过：特征树 %r → %r（要 +1）· 面数 %r → %r · 包围盒变化 %r"
                        % (out["tree_before"], out["tree_after"], out["face_count_before"],
                           out["face_count_after"], out["bbox_changed"]))
    return out


#: ── 成形工具（★ 规格 213 · B2：★ 从探针 `tools/probe_spec211_formtool.py`
#:    **已证实**的调用序缝合进模块 ✓ —— ★ 铁律 1：只缝合、不发明 ✓）────────────────────
# ★★ 官方依据（`swapi` 逐字）：
#   · `C:\swapi\types\IFeatureManager\InsertFormToolFeature.md` ⇒
#     `Feature InsertFormToolFeature( System.string Path, System.bool Flip, System.double RotAngle,
#       System.string Config, System.bool OverrideDoc, System.bool ShowPunch,
#       System.bool ShowProfile, System.bool ShowCenter, System.bool LinkToPart )`
#     ⇒ ★ **9 参** ✓
#   · ★★★ 官方 `## Remarks` 逐字：「**Before calling this method, select either a face or a
#     2D sketch containing points**」✗ ⇒ ★★ **前置 = 先选一个面** ✓
#     ★ 我第一版**没选** ⇒ 回 `None` ⇒ ★ 那正是「前置没上」、★ 与「工具建不出来」**长得一样** ✗
#   · ★★ 另一个前置是**钣金件** ✓ —— ★ 本仓 `sw_sheet_metal.create_base_flange` 真机已验能建成 ✓
#     ⚠ 它的契约是 `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` ✗ ——
#       ★ 不是 `(model, sketch, thickness, ...)`（★ 本会话在这上面栽过一次，★ 且它**不抛、只回 `None`**）✓
#   · ★ **工具文件要落盘** —— `Path` 是磁盘路径 ⇒ ★ 落到**仓库内 `output/`**（★ 非用户目录 ✓）
# ★★ 判据 = **回读**（★ 特征树增量，★ 不看返回值 —— 事实 8）✓
def insert_form_tool_report(model, tool_path, *, face_index: int = 0, flip: bool = False,
                            rot_angle_deg: float = 0.0, config: str = "", override_doc: bool = False,
                            show_punch: bool = True, show_profile: bool = True,
                            show_center: bool = True, link_to_part: bool = True):
    """插入成形工具（`IFeatureManager::InsertFormToolFeature`）—— ★ 判据用回读。

    参数:
        model: `IModelDoc2`（★ **钣金件** —— ★ 官方前置之一 ✓）
        tool_path: 成形工具文件（`*.sldftp`）在**磁盘上的路径**（★ 落仓库内 `output/` ✓）
        face_index: 要选的面序号（★ **官方 `## Remarks` 逐字要求先选一个面** ✓）
        flip: `Flip`（★ 是否翻转 ✓）
        rot_angle_deg: `RotAngle`（**度**）—— ★ 按参数名后缀，★ 边界处换算一次 ✓
        config: `Config`（★ 配置名；★ 空串即缺省 ✓）
        override_doc: `OverrideDoc`
        show_punch: `ShowPunch`
        show_profile: `ShowProfile`
        show_center: `ShowCenter`
        link_to_part: `LinkToPart`

    返回:
        dict —— ★★ 判据是**回读**：★ 特征树增量（★ 不看返回值 ✓）
    """
    import sw_selection_spec as SS

    out: dict = {
        "official": "IFeatureManager.InsertFormToolFeature",
        "arity": 9,
        "note": ("★ 官方 `## Remarks` 逐字要求**先选一个面**（`select either a face or a 2D sketch "
                 "containing points`）—— ★ 没选时**静默回 `None`**，★ 那与「建不出来」长得一样 ✗"),
        "tool_path": str(tool_path),
        "face_index": int(face_index),
    }
    #: ★ 前置①：★ 工件文件在盘上吗（★ 先查、★ 免得把"文件不在"记成"工具建不出来" ✓）
    from pathlib import Path as _Path
    if not _Path(str(tool_path)).is_file():
        out["ok"] = False
        out["error"] = ("★ 前置①失败：成形工具文件不存在 %r ⇒ ★ 官方 `Path` 参数是**磁盘路径** ✓"
                        % str(tool_path))
        return out
    out["tool_file_exists"] = True

    #: ★ 前置②：★ 选一个面（★ `append` 默认 `False` ⇒ 正好清空后单选 ✓）
    try:
        SS.select_entity_by_index(model, "FACE", int(face_index))
    except Exception as e:                                              # noqa: BLE001
        out["ok"] = False
        out["error"] = "★ 前置②选择失败：%s: %s" % (type(e).__name__, str(e)[:130])
        return out
    out["selection_count"] = SS.get_selection_count(model)
    if not out["selection_count"]:
        out["ok"] = False
        out["error"] = "★ 前置②无效：选区计数 = 0（★ 与「建不出来」是两件事 —— 事实 8）"
        return out

    before = _feature_names_snapshot(model)
    feat = None
    exc = None
    try:
        #: ★ 9 参逐位：★ Path · Flip · RotAngle · Config · OverrideDoc ·
        #:   ShowPunch · ShowProfile · ShowCenter · LinkToPart ✓
        #: ★★ 2026-10-07（规格 213 · B2）—— ★★★ **度数换算的取法改过一次，★ 两次都栽了**：
        #:   ★ **第一版**：★ 函数里裸写 `from .sw_connect import mm as _mm` ✗ ⇒
        #:     ★ 相对导入棘轮 **35 → 36** 被拦 ✓
        #:   ★★ **第二版**：★ 把 `deg` 加进**模块级**那行 ✓ ⇒ ★ **棘轮过了**，
        #:     而★ **`tests/test_sw_sheet_metal.py` 收集期炸** ✗ ——
        #:     ★ 逐字：`ImportError: cannot import name 'deg' from '<unknown module name>'` ✓
        #:     ★★ 真因：★ 那个测试只往 `sys.path` 塞 `scripts/`（★ 不是包）⇒
        #:       `sw_sheet_metal` 的**模块级** `from .sw_connect import … deg` 走进
        #:       **半初始化**路径 ✓；★ 而**别的名字在缓存里已有**、★ 只有**新加的 `deg`** 暴露了这个 ✗
        #:   ⇒ ★★★ **正解（第三版）**：★ **放在函数内、★ 且写完整的 `try:/except ImportError:`** ✓ ——
        #:     ★ 既满足棘轮判据（★ 「紧跟 `try:` 的那一行」✓）、★ 又不碰模块级导入 ✓
        try:
            from .sw_connect import deg
        except ImportError:
            from sw_connect import deg
        #: ★ 取 `FeatureManager` 用本模块既有的写法（★ 逐字：`get_com_member(model, "FeatureManager")` ✓）
        _mgr = get_com_member(model, "FeatureManager")
        feat = get_com_member(_mgr, "InsertFormToolFeature",
                              str(tool_path), bool(flip), float(deg(rot_angle_deg)),
                              str(config), bool(override_doc), bool(show_punch),
                              bool(show_profile), bool(show_center), bool(link_to_part))
    except Exception as e:                                              # noqa: BLE001
        exc = e
    after = _feature_names_snapshot(model)
    added = [n for n in after if n not in before]
    out.update({"feature_returned_is_none": feat is None, "added": added,
                "call_exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:150])})
    out["ok"] = bool(added)
    if out["ok"]:
        out["feature"] = str(added[0])
        out["verdict"] = ("★★★★★ **建成** —— ★ 特征树新增 %r（★ 回读、★ 不是信返回值 ✓）" % added)
    else:
        out["error"] = ("★ 回读判据未过：特征树没有增量（★ 选了面=%r · ★ 文件在=%r）⇒ "
                        "★ 三处成因逐条排除后再下结论（★ 事实 62：★ 只有负例能证明判据有效）✓"
                        % (out["selection_count"], out["tool_file_exists"]))
    return out


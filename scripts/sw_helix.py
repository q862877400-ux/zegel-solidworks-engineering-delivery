"""
螺旋线 / 螺旋（Helix & Spiral）—— 定距螺旋线与涡旋。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   **本项目自建**（不是从外部项目移植）。
#
# ⚠ 本模块补的是 `docs/union-gap-triage.md` 里「**真缺**」档的一条：`helix`。
#   那一档的定义是「连 `scripts/` 里也没有同名函数 ⇒ 要从零实现」；
#   `022` 核出该档**反向错误率约 18%**（有些其实换名实现了），
#   而 `helix` 经核**确实没有**（`InsertHelix` 只登记在 API 名表里，没有实现）。
#
# 官方签名依据（**两源互证**，铁律 4）:
#   ① 出厂反射: `iface_sldworks.txt` ——
#        `Void InsertHelix(Boolean, Boolean, Boolean, Boolean, Int32,
#                          Double, Double, Double, Double, Double)`   （在 **IModelDoc2** 上）
#   ② 结构化 md: `C:\\swapi\\types\\IModelDoc2\\InsertHelix.md` ——
#        `void InsertHelix(bool Reversed, bool Clockwised, bool Tapered, bool Outward,
#                          int Helixdef, double Height, double Pitch, double Revolution,
#                          double TaperAngle, double Startangle)`
#      ⚠ 两源**一致**（10 个参数，顺序与类型相同）⇒ 无冲突，不需要类型库裁决。
#   ③ 官方示例（`C:\\swapi\\examples\\Create_Spiral_Example_*.md`）：
#        `swModel.InsertHelix(false, true, false, false, swHelixDefinedBySpiral, 0, 0.0, …)`
#
# ⚠⚠ **单位（官方只写明了两个，其余未写）**：
#      · `Height`   —— 官方明写 **in meters** ⇒ 本模块的 `height_mm` 用 `mm()` 换算；
#      · `Startangle` —— 官方明写 **in radians** ⇒ `start_angle_deg` 用 `deg()` 换算；
#      · `Pitch` / `TaperAngle` —— ⚠ **官方未写单位**。本模块 `pitch_mm` **按米换算**
#        （与 Height 同类，是长度）、`taper_angle_deg` **按度直传**（与 Startangle 同类，是角度）
#        —— 这是**同类推断，不是查证**，已在 limitations 里声明。
#
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚑ **验证等级：`verified`**（2026-10-01 轮 121 由 `stitched` 升上来）——
#   依据 **真机冒烟** `python tools/verify_helix_smoke.py`（**13/13**，SW 2026 SP4.1 / 34.4.1）：
#     新零件 → 进草图 → 画圆 → 选中 → `insert_helix(50mm, 10mm, 5 圈)` → **读回定义**。
#   ★★ 证据是**往返一致**档的：读回 `Height=0.05` 米 · `Pitch=0.01` 米 · `Revolution=5.0`
#     ⇒ **同时证明 mm→米 的换算是对的**（若换算错，读回的会是 50）。
#   ★★ 本轮冒烟还**抓到并修掉了一处自己的缺陷**：`_newest_feature_name` 原读
#     `model.FirstFeature`（**树的第一个**，实测是 `'收藏'`）而非刚加的那个 ⇒ 改用
#     官方 `IModelDocExtension.GetLastFeatureAdded()`。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

try:
    from .sw_connect import deg, get_com_member, mm
except ImportError:      # pragma: no cover - 直接以 scripts/ 为根导入时
    from sw_connect import deg, get_com_member, mm          # type: ignore

#: `swHelixDefinedBy_e` 的成员（官方 4 个）。
#: ⚠⚠ **数值逐条查过两源**（铁律 4）：
#:   ① 出厂反射 `_raw/**/enum_values_sldworks.txt`
#:   ② `C:\swapi\enums\swHelixDefinedBy_e.md` 的表格
#:   ⇒ **两源一致**。
#: ★ **本文件第一版把 1 和 2 写反了**（凭记忆）——
#:   真值：`HeightAndRevolution = 1` · `HeightAndPitch = 2`。
#:   这正是铁律 4「不凭记忆写标准值」的**具体实例**，记在这里免得下一个人再犯。
HELIX_DEFINED_BY = {
    "pitch_and_revolution": 0,      # swHelixDefinedByPitchAndRevolution
    "height_and_revolution": 1,     # swHelixDefinedByHeightAndRevolution
    "height_and_pitch": 2,          # swHelixDefinedByHeightAndPitch
    "spiral": 3,                    # swHelixDefinedBySpiral
}

#: 本模块**允许被公开调用**的签名参数名（照官方顺序，一个不差）。
HELIX_ARGS = (
    "reversed", "clockwise", "tapered", "outward", "helix_def",
    "height_mm", "pitch_mm", "revolution", "taper_angle_deg", "start_angle_deg",
)


def insert_helix(
    model,
    *,
    height_mm: float,
    pitch_mm: float = 0.0,
    revolution: float = 0.0,
    helix_def: int = HELIX_DEFINED_BY["pitch_and_revolution"],
    reversed: bool = False,
    clockwise: bool = False,
    tapered: bool = False,
    outward: bool = False,
    taper_angle_deg: float = 0.0,
    start_angle_deg: float = 0.0,
):
    """建**定距螺旋线 / 涡旋**。

    ⚠ **调用前置条件**（与 `sw_mold.insert_parting_line` 同类）：
    官方示例显示要先**选中一个圆**（`SelectByID2` + `CreateCircle`）——
    螺旋线以那个圆为直径基准。**未选圆时行为未查证**（本模块不代选，保持"不猜"）。

    :param height_mm: 螺旋线高度，**毫米**（官方 `Height` 单位是米，这里换算）。
    :param pitch_mm: 螺距，**毫米**。⚠ 官方**未写单位**，本模块按米换算（同类推断）。
    :param revolution: 圈数（无量纲）。
    :param helix_def: `swHelixDefinedBy_e` 的**数值**；用 `HELIX_DEFINED_BY` 里的名字。
    :param reversed: 官方 `Reversed` —— 反向于定义圆的法向。
    :param clockwise: 官方 `Clockwised` —— 顺时针。
    :param tapered: 官方 `Tapered` —— 带锥度。
    :param outward: 官方 `Outward` —— 向外锥。
    :param taper_angle_deg: 锥角，**度**。⚠ 官方**未写单位**，本模块按度直传。
    :param start_angle_deg: 起始角，**度**（官方 `Startangle` 单位是**弧度**，这里换算）。
    :returns: 新建 Feature 的名字。
    :raises RuntimeError: 返回 `None`（最常见原因：**没有选中定义用的圆**）。
    """
    model.InsertHelix(
        bool(reversed),
        bool(clockwise),
        bool(tapered),
        bool(outward),
        int(helix_def),
        mm(float(height_mm)),
        mm(float(pitch_mm)),
        float(revolution),
        float(taper_angle_deg),
        deg(float(start_angle_deg)),
    )
    return _newest_feature_name(model)


def _newest_feature_name(model):
    """取**刚加进去的那个特征**的名字。

    ⚠⚠ **轮 121 真机实测：本函数原来写错了。**
    原实现读 `model.FirstFeature` 并取它的 `Name` ——
    但 `FirstFeature` 是**特征树的第一个**，**不是最新加的那个**。
    实测（新零件画圆后建螺旋线）它返回 **`'收藏'`**（树里的收藏夹），
    而真正新建的是 **`'螺旋线/涡状线1'`**。
    ★ 这个错**不抛异常、返回一个看起来合理的字符串** ⇒ 静态测试抓不到。

    ⇒ 改用官方 **`IModelDocExtension.GetLastFeatureAdded()`**
    （官方原文：「Gets the **last feature added** to the model」）。

    ⚠ 官方 Remarks 提醒：该方法**可能返回子特征**（如配合、工程图视图等）。
    """
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("IModelDoc2.Extension 为 None ⇒ 取不到最后加的特征")
    feat = get_com_member(ext, "GetLastFeatureAdded")
    if feat is None:
        raise RuntimeError(
            "IModelDocExtension.GetLastFeatureAdded() 返回 None ⇒ 螺旋线**没有建出来**。"
            "最常见原因：**没有选中定义直径的圆**（官方示例先 SelectByID2 选圆再调）。"
        )
    name = get_com_member(feat, "Name")
    if not name:
        raise RuntimeError("最后加的特征没有 Name ⇒ 无法确认螺旋线是否建成")
    return name


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自建（**不是**从四家外部 MCP 项目移植）。
# 依据:   ① 出厂类型库反射 `iface_sldworks.txt`（IModelDoc2.InsertHelix，10 参）
#         ② `C:\swapi\types\IModelDoc2\InsertHelix.md`（参数名与逐条说明）
#         ③ `C:\swapi\examples\Create_Spiral_Example_VB.md`（官方示例的调用形态）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：**无本机运行证据**，不得标 `verified`。
# ─────────────────────────────────────────────────────────────────────

# ── 24h 计划 段 6 续（Spec Kit `170` 的批次声明）：**参考轴（阵列的前置）** ──────────
# ★★★★★ 2026-10-01（轮 317）真机：★ 镜像与阵列**两半都建成**，而阵列卡在"没有轴可指"上。
#   ⇒ ★★ **轴是环形阵列的**前置**（官方 mark 表：`1 = 方向轴` · `4 = 特征）**
# ⇒ ★ **所以把"建轴"单独暴露成一个工具**，★ 它同时补 **§五 域②「参考几何（缺 4）」** 的
# 一条。
#
# ★★★ **三个真机坑（都在本轮查明）**：
# ```
# ① **`InsertAxis2` 不在 `IFeatureManager` 上，在 `IModelDoc2` 上** ——
#    ★ 调 `model.FeatureManager.InsertAxis2` ⇒ **`AttributeError: <unknown>.InsertAxis2`**
#      （★ 那正是"`<unknown>.X` 的根因之一：接口用错"）；
# ★ 依据：**CHM** `SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDoc2~In
# sertAxis2.html`
# （★ 而 `C:\swapi\types\IFeatureManager\` 下**没有** `InsertAxis2.md` ⇒ ★ 两源互补的价
# 值）
# ② **它回的是 `bool`，不是 `Feature`** —— ★ 真机：`model.InsertAxis2(True)` ⇒ **`True`*
# *，
# 而读它的 `.Name` 会报 `'bool' object has no attribute 'Name'`（★ 差点据此误判"轴没建成
# "）。
#    ⇒ ★★ **判据要**数特征树**：★ 建完出现 `基准轴1`** ✓
# ③ **镜像的 mark 原本是反的** —— ★ 官方 `InsertMirrorFeature2.md` 的 Remarks 给完整表：
# ★ **Features ⇒ 1** · ★ Faces ⇒ 128 · ★ Bodies ⇒ 256 · ★ **Planes or planar faces ⇒ 2**
#  ·
# ★ Structure systems ⇒ 134217728 —— ★ 而旧代码是"特征 mark=4 / 平面 mark=1"（★ **两个都
# 错**）。
# ```
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch49.py —— 本文件
# 定位:   段 6 续：参考轴（★ 环形阵列的前置 + §五 域② 缺口）。
# 官方签名依据: ★ CHM `IModelDoc2~InsertAxis2.html`（★ 入口在 `IModelDoc2`）·
#   ★ 反射 arity `scripts/sw_api_sldworks.py:6267`（`InsertAxis2` = **1**）·
#   `C:\swapi\types\IFeatureManager\InsertMirrorFeature2.md`（★ mark 表）·
# `C:\swapi\types\IFeatureManager\FeatureCircularPattern4.md`（★ `1 = 方向轴` · `4 = 特
# 征`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH49 = [
    ToolSpec(
        name="solidworks_part_axis",
        title="Create Reference Axis",
        module="sw_part",
        function="create_axis_report",
        inject="model",
        params=[
            Param(
                "reverse",
                bool,
                default=True,
                description="官方第一参数（`InsertAxis2(Reverse)`）；★ 真机 True 有效",
            ),
            #: ★★ 2026-10-07（接手轮 · 规格 216 T-216-07）**加声明式选区入口** ——
            #: ★ 起因：★ 函数**读当前选区**、★ 计数 0 就报错 ⇒ ★ 而解析器**会清空选区**
            #: （事实 503）
            #:     ⇒ ★ 模型**没法**在调工具前选好 ⇒ ★ 经工具层**必然失败** ✗
            #:   ★ 规则 3 **不许收裸坐标** ⇒ ★ 收选择器 + 实体种类 ✓
            Param(
                "selection",
                str,
                description="★ 声明式选择器（规则 3：不收坐标）：`index:<n>` 或 "
                "`__current_selection__`；★ 空串=不选（则要求调用方已选，"
                "★ 而注入后通常为空）。",
                required=False,
                default="",
            ),
            Param(
                "selection_kind",
                str,
                description="`FACE` / `EDGE` / `VERTEX` —— ★ 可作轴参照的几何："
                "**圆柱面 / 圆锥面 / 两点**（★ 官方）。",
                required=False,
                default="FACE",
            ),
        ],
        doc="★ **从声明式选区建一条参考轴** —— 走 `IModelDoc2.InsertAxis2`"
        "（★ **注意入口在 `IModelDoc2` 上**，不在 `IFeatureManager` 上；★ 真机调后者报"
        "`AttributeError: <unknown>.InsertAxis2`）。"
        "★★ 用 `selection` + `selection_kind` 说明用哪个几何（★ 规则 3：**不收坐标**；"
        "★ 函数会在**注入之后**自己重建选区 —— ★ 事实 503：注入解析器会清空选区）。"
        "★★ 判据（★ 事实 242 挑只依赖被测对象的那个）：**它回 `True`** **且** "
        "**特征树出现新特征**（★ 真机：`基准轴1`）—— ⚠ **不要读返回值的 `.Name`**："
        "真机证明它回的是 **`bool`**，读 `.Name` 会报 `'bool' object has no attribute 'Name'`"
        "（★ 差点据此误判「轴没建成」）。"
        "★ 环形阵列的前置：官方 `FeatureCircularPattern4` 的 mark 表要求 `1 = 方向轴`。",
    ),
]

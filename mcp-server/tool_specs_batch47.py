
# ── 24h 计划 段 6 续（Spec Kit `168` 的批次声明）：**放样** ──────────────────────────
# ★★★★★ 2026-10-01（轮 313）真机（`output/loft-evidence.json`）**PASS 3/3**：
#   · 同平面两轮廓 ⇒ **建成 `放样1`**（树 7→8 · 官方 18 参）✓
#   · 两平面（前视 + 上视）⇒ **建成 `放样1`** ✓
#   · 未选中 ⇒ **显式拒绝**（★ 提示"至少 2 个轮廓 · mark=1"）✓
#   ⚠ **未验**：★ `CreateMassProperty().Volume` 回 **0.0**（★ 所以"棱台体积 7000 mm³"那个
#     几何推出的期望值**没有对上**）—— ★ **如实标"未真机验证体积"**，★ 不写成"通过"。
# ★★ **它补的是核实的真缺**：★ 全仓 grep `loft` ⇒ **工具 0 · 函数 0**（`sweep` 同样 0）
# ，
# ★ 而**放样与扫描是 SolidWorks 最基本的两种特征**；★ 四家并集里有 **`loft`**（Slacker-L
# LC 提供）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch47.py —— 本文件
# 定位:   段 6 续：放样（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md`
# （**18 参** · 回 `Feature` · Remarks 给 mark：1=轮廓 / 2=引导线 / 4=中心线 / 8=起端相
# 切向量）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py:4426` = **18**（★ 两源一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

#: ★★ 帮手在 batch4（★ 那一族四条共用一份 —— 事实 60 定则④）。
from tool_specs_batch4 import _pre_loft_profiles  # noqa: E402

SPECS_BATCH47 = [
    ToolSpec(
        name="solidworks_part_loft",
        title="Create Loft Feature",
        module="sw_loft",
        function="create_loft_report",
        inject="model",
        #: ★★★ 2026-10-03（接手轮）：`create_loft_report` 是**硬前置** —— 读到 `mark=1` 
        #: 的选中数 < 2 就
        #: `return {"ok": False, "stage": "selection"}`。★ 而**原先这条 spec 没有"给选区
        #: "的入口**
        #: ⇒ ★★ **经工具层必然失败**（真机实测：`stage=selection` · 「`mark=1` 的选中数
        #: 是 **0**」，
        #:   证据 `output/explicit-reject-family-evidence.json`）。
        #: ★ 修法：★ 加 `profile_sketches`（**按顺序**给名字）+ `pre_call`（★ 它跑在注入
        #: **之后**）。
        pre_call=_pre_loft_profiles,
        #: ★ `None` = 「由 `pre_call` 消费、不进目标函数」（★ 仓内既有口径；★ 不标则**判
        #: 据 ①** 会如实报）。
        param_alias={"profile_sketches": None},
        params=[
            #: ★★ 新加：轮廓草图的**名字列表**（★ 只收名字、不收坐标 —— 规则 3）。
            #:   ★★ **顺序即语义**（官方 Remarks 逐字：轮廓要**按期望的顺序**先选中）。
            Param("profile_sketches", list, default=None,
                  description="★ 轮廓草图名**列表**（**mark=1**；★★ **顺序即语义** —— "
                              "官方 Remarks：轮廓要**按期望的顺序**选中）· 至少 2 个"),
            Param("closed", bool, default=False,
                  description="闭合放样（★ 首尾相连成一个环；★ 少于 3 个轮廓时引导线必须闭合）"),
            Param("use_selected_profiles", bool, default=True,
                  description="用当前选中的轮廓（★ 官方要求 mark=1，且**顺序**决定结果）"),
        ],
        doc="★ **用「轮廓草图」放样** —— 走 `IFeatureManager.InsertProtrusionBlend2`（官方 **18 参**）。"
            "★ 官方 Remarks：轮廓要**按期望的顺序**先选中，mark=**1**（引导线 mark=2 · 中心线 mark=4 · "
            "起端相切向量 mark=8）；★ 引导线与中心线**可选**。"
            "★★ **`profile_sketches` 是必填的**：★ 本工具**不预选任何东西**，而是由 `pre_call` "
            "在**注入之后**按名把每个轮廓选上（**mark=1**）并**回读计数**（★ 事实 8）—— "
            "★ 名字**按顺序**给（顺序即语义）。"
            "⚠ 早先版本**没有**这个参数、也没有 `pre_call` ⇒ **经工具层必然失败**"
            "（真机报 `stage: selection`，证据 `output/explicit-reject-family-evidence.json`）。"
            "★★ 判据（规则 6）：**特征树多了新特征**。"
            "★ 真机证据：同平面与两平面两种情形都建成 `放样1`。"
            "⚠ **未真机验证**：质量属性里的**体积**（★ 真机上回 0.0，所以「棱台体积 7000 mm³」那个"
            "期望值没有对上）—— ★ 不要把本工具的体积当可靠读数。",
    ),
]

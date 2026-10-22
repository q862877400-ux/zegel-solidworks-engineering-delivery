# ── 24h 计划 v2 · 段 3 收尾（★ 轮 405 部分恢复）───────────────────────────────────────
# ─
# ★★★★ 2026-10-03（轮 405）★ **上一轮（400）我把这两条判成「真机未建成」并按硬约束⑥ 回退
# 注册 ——
#   而轮 405 的「**边对穷举表**」证明 `add_dimension` 那条**其实能建**。
#
# ★★ **上一轮的真因**（★ 极重要）：
#   · 轮 405 对 12 条边**两两共 66 对**（★ **那是计划数 = C(12,2)**）逐一试
#     （★ 事实 53 的正解：**把猜测变成一张穷举表**）⇒ ★ **实跑 12 对就停**，
# 其中成功的对是 `[0,1] [0,2] [0,3] [0,4] [0,7] [0,8] [0,11] [1,2]`（★ **成功的 8 个**）
# 。
#     ⚠⚠⚠ 2026-10-04（接手轮）**更正**（★ 处置 `JUDGE-A_B.md` 的 A-features F1）：
#       原文这里写「**含边 0 的组合都成**」—— ★★ **那是错的** ✓
#       ★ 证据 `output/dimension-edge-pairs-evidence.json` 逐字：`tried: 12` ·
#       `successes` **8 项** · `pairs` 全表 12 行里 **`created=True` 8 / `created=False` 4**，
#       ★★ 失败的 4 对是 `[0,5] [0,6] [0,9] [0,10]` —— ★ **全部含边 0** ✓
# ★★★ **真正的规律**（★ 按那份证据 `note` 里的分组：`0-3`/`4-7` 是两个面环、`8-11` 是竖
# 边）：
#         同一面环内（0↔1/2/3）· 对面环的对应边（0↔4/7）· 与竖边（0↔8/11）**成**；
#         而对面环上**错位**的边对（0↔5/6 · 0↔9/10）**不成** ✓
#       ⇒ ★ 「含边 0 都成」是**从 8 个成功样本里看出来的错觉**（★ 因为成功的 8 个恰好都含 0）✓
#   · 而轮 400 我用**同样**的 `[0,1]` 却失败了 ⇒ ★ 唯一的差别是
#     **轮 405 每次选之前都 `ClearSelection2(True)`**。
#   ⇒ ★★★ **即：★ 上一轮的真因是「我的探针选区不干净」，不是能力坏了** ——
#     ★★ 而那正是 `AGENTS.md` 警告过的：「**每次失败都像是能力坏了，实际是我调错了**」。
#     ⚠ 而**我据此把一条好能力记成了坏的**（★ 代价：白回退了一次注册）。
#
# ★★ **本批只恢复 `add_dimension`**（★ 它有 `verdict: pass` 的证据）：
#   `output/dimension-edge-pairs-evidence.json` —— 纯盒体上 **8/8 边对**都建出了尺寸。
#   ⚠ **同时记下未隔离的限制**：同一个包装在**板 + 凸台**的模型上失败
# （`output/dimension-pattern-retry-evidence.json`）⇒ ★ 连试 3 次后按事实 53 **停止隔离*
# *，
#     ★ 把现象如实写进 `limitations`（★ 而不是继续试参数）。
#
# ★★ **`linear_pattern` 仍不注册**，★ 但卡点**收敛了一步**：
#   官方签名里 `DName1` / `DName2` 是「**Name of the dimension defining Direction 1/2**」
#   ⇒ ★★ 空字符串 = **没有方向** ⇒ ★ 那很可能就是「不报错而特征树不变」的真因
# ⇒ ★ 下一步：★ **先造/选一个能当方向基准的实体**（★ 与 `AddDimension2` 的「必须先选中」
# 同族前置）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch56.py —— 本文件
# 定位:   24h 计划 v2 段 3 收尾：把 `add_dimension_report` 挂成 MCP 工具。
# 官方签名依据: `IModelDoc2.AddDimension2`（3 参 · **米** · 必须先选中实体）·
# `IFeatureManager.FeatureLinearPattern3`（**10 参** · `Spacing1` 是**米** · `Num1` 含原
# 件 ·
#   `DName1`/`DName2` 是**方向维度的名字**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec

SPECS_BATCH56 = [
    ToolSpec(
        name="solidworks_add_dimension",
        title="Add a Display Dimension",
        module="sw_part", inject="model", function="add_dimension_report",
        params=[
            Param("x_mm", float,
                  description="尺寸文字的 X（**毫米** —— ★ 官方 API 吃米，换算只在本工具边界做一次）"),
            Param("y_mm", float, description="尺寸文字的 Y（**毫米**）"),
            Param("selector", str, default="__current_selection__",
                  description="先选中要标注的实体：`__current_selection__`（用现有选区）或 `index:<n>`"),
            Param("kind", str, default="EDGE", description="实体种类：EDGE / FACE / VERTEX"),
        ],
        doc="★ **给已选中的实体加一个显示尺寸**（官方 `IModelDoc2.AddDimension2`，**3 参**）。"
            "★★ **单位**：官方原话是 “Dimension text location in **meters**” ⇒ ★ 本工具对外收"
            "**毫米**并在此换算。"
            "★★ **前置**：官方 Remarks 明写「Before calling this method, you must **select the entities**」"
            "⇒ ★ 本工具**先用声明式选择器选中**（★ 选不中就**不开工**并说明原因）。"
            "★ 真机证据：纯盒体上 **8/8 个边对**都建出了尺寸"
            "（`output/dimension-edge-pairs-evidence.json`）。"
            "⚠★ **已知限制（未隔离）**：同一个包装在**板 + 凸台**的模型上失败 —— "
            "★ 连试 3 次后按事实 53 停止隔离；★ 官方另注「**only use on visible documents**」"
            "且尺寸**按位置**放置（★ 位置不落在可见模型上时可能建不出来）。",
    ),
]

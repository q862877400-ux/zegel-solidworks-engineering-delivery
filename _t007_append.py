

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**官方接口的只读包装**）+ `specs/001-topology-result-readout`
# 文件:   `scripts/sw_topology.py` —— 追加 `collect_topology_numbers` 与 `TOPOLOGY_RESULTS_UNRESOLVED`
# 官方签名依据: 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWResults` 段
#         （**裁决者**，铁律 4）。本函数**只调无参数成员** —— 见下「为什么只包这三个」。
# 定位:   做 `specs/001-topology-result-readout/tasks.md` 的 **T-007 / T-009**。
#         spec 的验收要求：「每个返回值附带来源成员名（可复查）」；
#         「未跑过 ⇒ 返回 `{"status": "no_results", …}`，**不抛未捕获异常、不静默空 dict**」。
#
#   ★★ **为什么只包这三个成员（`GetPlotCount` / `GetPlotNames` / `GetMaximumAvailableSteps`）**：
#     反射里 `ICWResults` 共 **107 个成员**，但**官方文档源里没有任何一页解释它们的参数语义**
#     （查过 `cosworks_pages` / `chm_cosworks` / `cworksapi` / 官方文档目录，**4 处 0 命中**）。
#     例：`GetMinMaxDisplacement(Int32, Int32, Object, Int32, Int32&)` —— **4 个入参含义未定义**。
#     **⇒ 按铁律 5「查不到就说查不到」：不猜参数。**
#     而这三个成员**无参数**、语义自明，且 `GetPlotCount`/`GetPlotNames`
#     **已在真机上验证过**（003 的闭环正是靠它断言到「材料质量1」，见
#     `output/topology-evidence.json` 的 `steps.material_mass_plot`）。
#     ⇒ **可安全包装**；`GetMaximumAvailableSteps()` 无参数但**未运行期验过** ⇒ 按事实 30
#       「**判据永远是「返回非 None」，不是「在可取名单里」**」处理：取到就报，取不到就 `None`。
#
#   ⚠ **参数语义未知的那几个成员**登记在 `TOPOLOGY_RESULTS_UNRESOLVED` 里（**不是实现**），
#     连同「为什么没实现」与「要补什么才能实现」——**避免下一个人重踩**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本函数**只读**，不改模型；不 `BeginEdit`/`EndEdit`，不弹窗。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

#: 反射里**存在、但参数语义查不到**（4 处官方文档源 0 命中）的 `ICWResults` 成员。
#: **不实现它们**（铁律 5）—— 要补的条件写在每条的原因里。
TOPOLOGY_RESULTS_UNRESOLVED: dict[str, str] = {
    "GetMinMaxDisplacement": (
        "签名 `Object GetMinMaxDisplacement(Int32, Int32, Object, Int32, Int32&)` —— "
        "**4 个入参含义无官方文档**（cosworks_pages / chm_cosworks / cworksapi / 官方文档目录 4 处 0 命中）。"
        "**要补的条件**：找到官方参数说明，或在真机上用「有结果 / 无结果」两种研究做受控对比。"
    ),
    "GetMinMaxStress": (
        "签名 `Object GetMinMaxStress(Int32, Int32, Int32, Object, Int32, Int32&)` —— 同上，**5 个入参无文档**。"
    ),
    "GetMinMaxFactorOfSafety": (
        "签名 `Object GetMinMaxFactorOfSafety(Boolean, Object, Int32, Int32, Int32&)` —— 同上，**4 个入参无文档**。"
    ),
    "GetTimeOrFrequencyAtEachStep": (
        "签名 `Object GetTimeOrFrequencyAtEachStep(Int32, Int32&)` —— 同上，**1 个入参无文档**。"
    ),
    "SavePlotsAseDrawings": (
        "签名 `Int32 SavePlotsAseDrawings(String, String, String)` —— 参数名未给，"
        "**且只有反射一源**（无官方页）⇒ 按事实 28/30「反射里有」≠「运行期调用得到」，**不包装**。"
    ),
    "ExportSimulationStudy": (
        "在 `ICWStudy` 上：`Int32 ExportSimulationStudy(String, String, Int32, Int32, Int32, Int32, Int32)` —— 同上。"
    ),
}


def collect_topology_numbers(study) -> dict[str, Any]:
    """读取某个**已求解**拓扑研究的结果读数；未求解时**明确报无结果**，不抛异常。

    参数
    ----
    study : ``ICWStudy``
        由 ``create_topology_study`` 或 ``get_cw_document`` 的研究管理拿到的研究对象。

    返回（两种形态，**spec 的 T-007 验收要求**）
    ------------------------------------------
    * 有结果::

          {"status": "ok",
           "source_members": {...},      # 每个读数**附来源成员名**（可复查）
           "plot_count": 2,
           "plot_names": ["品质1", "材料质量1"],
           "material_mass_plot": "材料质量1",   # 命中判据正则时为图名，否则 None
           "max_available_steps": 1}

    * 无结果::

          {"status": "no_results", "reason": "...", "source_members": {...}}

    ⚠ **判据说明（重要）**：本项目已累计多处「返回码撒谎」，所以
    **本函数不用任何返回码判成功** —— 「有结果」的判据是
    **`Results` 对象非 None 且 `GetPlotCount() > 0`**（与 003 的证据脚本同一口径）。
    """
    import re as _re

    results = get_com_member(study, "Results")
    # ⚠ `Results` 为空 ⇒ **不是异常**，是「还没跑过」这一合法状态 ⇒ 明确报出来。
    if results is None:
        return {
            "status": "no_results",
            "reason": "study.Results 为 None（该研究未求解或求解未产出结果）",
            "source_members": {"results": "ICWStudy.Results"},
        }

    plot_count = get_com_member(results, "GetPlotCount")
    if plot_count in (None, 0):
        return {
            "status": "no_results",
            "reason": "study.Results 非 None 但 GetPlotCount() == %r（无结果图）" % (plot_count,),
            "source_members": {"results": "ICWStudy.Results", "plot_count": "ICWResults.GetPlotCount"},
        }

    raw_names = get_com_member(results, "GetPlotNames")
    plot_names = [str(x) for x in (raw_names or ())]

    # ⚑ Material Mass 图：中文界面 `材料质量1` / 英文 `Material Mass 1`
    #   ⇒ 判据用正则，不硬编码单一语言（spec §Assumptions 的要求）。
    pattern = _re.compile(r"(材料质量|Material\s*Mass)")
    matched = [n for n in plot_names if pattern.search(n)]

    steps = get_com_member(results, "GetMaximumAvailableSteps")
    return {
        "status": "ok",
        "source_members": {
            "results": "ICWStudy.Results",
            "plot_count": "ICWResults.GetPlotCount",
            "plot_names": "ICWResults.GetPlotNames",
            "max_available_steps": "ICWResults.GetMaximumAvailableSteps",
        },
        "plot_count": int(plot_count),
        "plot_names": plot_names,
        "material_mass_plot": matched[0] if matched else None,
        "max_available_steps": (int(steps) if steps is not None else None),
        "unresolved_members": sorted(TOPOLOGY_RESULTS_UNRESOLVED),
    }

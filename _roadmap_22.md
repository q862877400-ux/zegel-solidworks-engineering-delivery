            ㉒ ★ **001 的静态任务做完 ⇒ 推翻 spec 的一个前提**（轮 50）：
               spec 假设「Material Mass 图 / 收敛数据 / 导出平滑网格 三件事在公开 API 里**可能不存在**」
               ⇒ 逐条核反射 `## ICWResults` 段（**107 个成员**）后**分成四种不同结论**：
                 ① Material Mass 图 **✅ 可读且运行期已证**（`GetPlotCount`/`GetPlotNames`/`GetPlot`）
                 ② 导出结果图为图片 ⚠ **反射里存在** `ICWResults.SavePlotsAseDrawings(String,String,String)`
                 ③ 导出研究 ⚠ **反射里存在** `ICWStudy.ExportSimulationStudy(...)`
                 ④ 导出**平滑网格** ✗ **确实不存在**（六个候选名在 107 个成员里一个都没有）
                 ⑤ 收敛/步数 ⚠ 反射里存在 `GetMaximumAvailableSteps` / `GetTimeOrFrequencyAtEachStep`
               ⚠ ②③⑤ **只有一源（反射）** ⇒ 按**事实 28/30**（「反射里有」≠「运行期调用得到」）
                 **不声称「可导出」**，只记「存在、未验」
               🔴 **我自己的一个错也被核出**：T-005 第一版按 `Export|Smooth|Conv|Mass` 过滤只得 1 个，
                 而 **Material Mass 图恰恰走 `GetPlotCount`/`GetPlotNames` —— 那两个名字不含我的任何过滤词**
                 ⇒ **漏掉了真正的答案** ⇒ **事实 51 的同族**（抓不到目标时先怀疑**范围/过滤条件**）
                 ⇒ 改为**完整枚举 107 个成员**后逐条判定
               ✅ 清单侧：`limitations` 加 1 条**分级结论**（带来源位置 + 可重跑枚举命令），
                 并**分解修正**原先混为一谈的「导出类结果 四源均未查到」（原文保留 + 分解指向）
               ⇒ **001 进度 3/13 → 7/13**；**T-007..T-009 待真机**（需一次完整求解 ≈3 分钟 + 许可）
                 ⇒ **不打勾、不声称已完成**

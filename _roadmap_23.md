            ㉓ ★ **001 的 T-007/T-008/T-009 做完（静态）**（轮 51）⇒ **001 进度 7/13 → 9/13**：
               `scripts/sw_topology.py` 新增 `collect_topology_numbers(study)` +
               `TOPOLOGY_RESULTS_UNRESOLVED`；契约测试 **8 → 14 passed**。
               ⚠ **与任务原文不同，理由**：任务点名的 4 个成员
                 （`GetMinMaxDisplacement` / `GetMinMaxStress` / `GetMinMaxFactorOfSafety` /
                  `GetTimeOrFrequencyAtEachStep`）**参数语义查不到** ——
                 **4 处官方文档源 0 命中**（`cosworks_pages` / `chm_cosworks` / `cworksapi` / 官方文档目录）
                 ⇒ 按**铁律 5 不猜参数**，改为只包**无参数、语义自明**的四个：
                 `ICWStudy.Results` · `GetPlotCount()` · `GetPlotNames()` · `GetMaximumAvailableSteps()`
                 （前两个**已在真机验证过**：003 靠 `GetPlotNames` 断言到「材料质量1」）
                 ⇒ 那 4 个 + `SavePlotsAseDrawings` + `ExportSimulationStudy` 共 **6 个**登记在
                   `TOPOLOGY_RESULTS_UNRESOLVED`（**每条带「为什么没实现 + 要补什么」**），
                   并有契约测试守着「不许悄悄实现」
               ★ **两个守卫各自抓到我一次**：
                 ① **既有测试**（`test_every_called_member_exists_in_official_reflection`）
                    在我新增 4 个调用点后**立刻报红**并要求「与反射对账后加进 `OFFICIAL_MEMBERS`」
                    ⇒ 已逐条对账（`Results` 写作属性 getter `CWResults get_Results()`）
                 ② **我自己写的测试**抓到 `ExportSimulationStudy` 的原因写了「**同上**」
                    ⇒ 断言「每条都要自解释」不通过 ⇒ 已改成说清是「参数语义查不到」还是「只有一源」
               🔴 ⚠ **真机部分**本轮跑不了**（环境阻塞，**不打勾**）**：
                 `probe_collect_numbers_noresults.py` ⇒ `GetAddInObject('SldWorks.Simulation') 返回 None`
                 只读诊断（`probe_addin_registration.py`）试了 **5 个候选 ProgID**，**全 None**
                 ⇒ 本会话（PID 24252）的 **Simulation 加载项没加载**
                 ⚠ 而 **003 的证据来自**另一个**加载了它的会话**（T-001 记「✓」）
                 ⇒ **已知事实 57 的同族**：同一台机器、不同会话、环境不同
                 ⇒ **不自行 `LoadAddIn`**（官方要 **DLL 全路径**，且会改**会话状态**）
                 ⇒ 记为**环境阻塞**；**两条形态各有其证据**（无结果=契约测试假对象；
                   有结果=003 闭环），**只是不在同一次真机运行里** —— 这一点**明说**

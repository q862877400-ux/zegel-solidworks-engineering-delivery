            59 🎯 **AVI 域从「查不到」推进到「API 可用、导出条件未定位」**（轮 64）：
               新增 `tools/verify_motion_avi_e2e.py`（就是 `animation_export.evidence` 指向的命令）。
               **真机跑通的**：圆柱零件 → 装配体 + 两次插组件 → Motion 类型库/manager/算例
               → **匀速旋转马达建成（`AEMRotationalMotor`，type_id 102）**
               → `calculate` 后 `motor_count=1` · `results_out_of_date=False`（**结果新鲜**）
               → `CreateAVIParameter` 非 None、`configure(FramePerSecond=10)` **回读 10.0**。
               🔴 **但 `SaveToAVI` 始终返 `False` 且不产文件 —— 已排除 5 种条件组合**：
               ```
               ① 空装配体、不 Calculate      ⇒ **返回 True 而文件 0 字节**（**「返回码撒谎」实证**）
               ② 空装配体 + Calculate        ⇒ False、无文件
               ③ 有马达 + 挑含马达的算例 + Activate ⇒ False、无文件
               ④ 再加「保存装配体（有路径）」  ⇒ False
               ⑤ 再加「先 Play 一遍」         ⇒ False
               ```
               ⚠ **按事实 53 停止**（同一处连试 ≥3 次就停）⇒ **不再换参数试**，改**如实记边界**。
               **未验证候选（不猜）**：算例类型（实测 `StudyType==1`，语义在 `swapi/enums` **查不到**）·
               两组件**无 mates**（浮动）· 是否需要 **SolidWorks Motion 加载项** · 是否需要 UI/许可。
               ⇒ `animation_export` **保持 `stitched`**（没有「导出非零文件」的证据 ⇒ 不升 verified）。
               ★ **本轮的价值**：从「**查不到**」（是**结论**，会让人放弃）
                 变成「**API 可用、条件未定位**」（是**待办**，有明确下一步 + **已排除清单**）。
            60 ⚠ **`check_provenance` 的来源块覆盖是**按定义单元**的 —— 本坑第 4 次**：
               * `verify_motion_avi_e2e.py` 的来源块写在 **module docstring 里**
                 ⇒ `_module_docstring_lines()` **整段跳过** ⇒ **不算覆盖**；
               * 改放到 `step()` 前 ⇒ **只覆盖 `step()`**，`main()`（L86-233）**仍报 114 行无出处**。
               ⇒ **定则：每个顶层 `def` 前各放一份来源块。**
               ⚠ 已踩 4 次（`verify_costing_e2e.py` · `sw_motion.py` ×2 · 本文件）
               ⇒ **下一步：在 `check_provenance` 输出里加诊断**（提示「来源块在 docstring 里 /
                 只覆盖紧邻的那个定义」），把第 5 次挡在门外。
            61 ⚑ **遵守铁律 4（先核实再写）的一例**：写 `verify_motion_avi_e2e.py` 时先用
               `sw_part.sketch_circle` / `AddComponent5` / `SaveAs3` / `Extension.SaveAs`，
               **逐个去反射核实**（`AddComponent5` 8 参 ✓ · `IModelDoc2::SaveAs3` **3 参** ✓），
               并**改用项目既有封装**（`sw_assembly.add_component` / `sw_connect.save_document`）
               而非自己拼 —— **「不重造」与「先核实」在这里是同一件事**。

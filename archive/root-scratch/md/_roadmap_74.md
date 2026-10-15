            74 🔴 **抓到一个「存在却没人跑」的门禁 —— 它**正红着**，而且是我造成的遮蔽**（轮 70）：
               本轮开场是「盘点哪些门禁在检查量为 0 时不喊」，**先撞到一个更紧急的**：
               ```
               python scripts/check_workspace_shadowing.py
                 [FAIL] 工作区根有 **1 个**会遮蔽依赖包的文件/目录：
                   mcp            ← D:\AI\SW\mcp.py
                   后果：以该工作区为 CWD 的 Python 进程里 `import mcp` 拿到的是**那个本地文件**
                         ⇒ `No module named 'mcp.server'; 'mcp' is not a package`
               ⚠ 而这道门禁**根本没被 `release_check.py` 调用** ⇒ **它红着也没人知道**（可能红了很久）
               ```
               ★ **一个存在但没人跑的门禁，与没有门禁等价** —— 这是本项目已多次记录的教训的
                 **另一个面**：之前是「守卫存在但没人用」，这次是「**门禁存在但没接线**」。
               ⇒ **修两件**：
                 ① **消除遮蔽**：`D:\AI\SW\mcp.py` 是**我的一次性探查脚本**（864 字节 / 09-29，
                    用 `gh api` 拉 andrewbartels1 的文件树），用途早已完成 ⇒
                    按**门禁自己给的建议**改名加前缀（**`git mv mcp.py _mcp.py`**，**不删**，符合红线）。
                 ② **接线**：`release_check.py` 新增 `_run_workspace_shadowing_gate`，
                    接在**成员名门禁之后**、**硬失败**。⚠ 便携性已核：工作区不在（别的机器）⇒
                    该脚本自己 `[SKIP]` 并 exit 0 ⇒ **可无条件接线**。
               ★ **负例已证有牙齿**：把 `_mcp.py` 改回 `mcp.py` ⇒ `release_check` 报
                 「工作区遮蔽门禁未通过」；恢复 ⇒ exit 0。
            75 ⚑ **盘点「检查量为 0 却不喊」的结论（本轮的另一半）**：本仓**不普遍** ——
               带 SKIP 的门禁**都会把 SKIP 喊出来**（`check_member_names` 还说
               「这是静默通过，不算通过」），且 `check_interface_member_ownership` **早就有**
               「检查量为 0 ⇒ 返回非 0」的守卫。
               ⇒ **真正的问题不是"不喊"，而是"压根没被调用"**（本轮的 74）。
               ⚠ 但仍留一个**待查**：`check_interface_member_ownership` 实测只检查
                 **5 个 `CreateDefinition` 站点**（扫 122 个文件）—— 5 是否偏少，**未查证**，
                 按铁律 5 **不臆断**，留作下轮。

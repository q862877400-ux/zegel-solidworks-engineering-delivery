            ㉟ ★★ **A6（许可红线）从「人工逐文件对照」变成**可机核的门禁****（轮 57）：
               `scripts/check_license_redlines.py` —— 把 `AGENTS.md §一 A6` 的
               「逐文件对照许可判定表」做成**可跑的那一半**。三条判据：
               ```
               ① 来源块点名第三方 ⇒ 许可须含白名单词（MIT / Apache-2.0）
               ② ⚠ **已知 Apache-2.0 的来源**（Slacker-LLC）⇒ 许可须**明写 Apache**
               ③ 声明 Apache-2.0 ⇒ THIRD-PARTY-NOTICES.md 必须存在
               ```
               ★★ **②是**实测逼出来的****（**最有价值的那条**）：
                 第一版只判「有没有白名单词」，而「**本仓库 MIT**」这个措辞**本身含 `MIT`**
                 ⇒ 「来源 `Slacker-LLC`（**Apache-2.0**）／ 许可 本仓库 MIT」被**误判为通过**
                 ⇒ **漏掉的正是唯一带 NOTICE 硬义务的那一档** ⇒ **假阴性，且漏在最要命处**
                 ⇒ 加 `APACHE_ONLY` 显式表，对它们要求许可**明写 Apache**
               ⚠ **覆盖边界如实写进门禁输出**：它判**声明是否自洽/越界**，
                 **不判声明是否属实**（「某函数到底抄没抄」是**语义**判断，靠人核）
               ⇒ 契约测试 **11 条**（含 4 组负例）· 已接进 `release_check.py`
               ⇒ 现状：**101** 个来源块，其中点名第三方的 **4** 对，**0 越界**
            ㊱ ⚠ **同一类「数字失真」的第 3 例**：`THIRD-PARTY-NOTICES.md` L35 原写
               「**100 新增文件 / 13 改过文件**」（更早轮次的数）
               ⇒ **不再重复维护一个会腐坏的数字**，改为指向**有门禁守着的那一处**
                 （`harvest-report.md` 开篇那行，由 `check_report_freshness.py` 守）
                 —— 这是「**一个事实一个家**」的正确用法
            ㊲ ⚠ **`check_report_freshness.py` 的修法行原先**不可直接粘贴****（轮 57 修）：
               它输出 `+127157`（**无逗号**），而报告用 `+126,772`（**有逗号**）
               ⇒ 我照抄时长度不符、脚本断言失败、**而 `git commit` 照跑**
                 （**事实 48 那个陷阱重演**：脚本挂了但提交照做）
               ⇒ 修法行的**全部意义**就是「可直接粘贴」⇒ 加千分位
               ⇒ **`release_check` 现在共 **9 道硬门禁 + 1 道诊断****：
                 provenance · diff_markers · member_names · union_conventions · env_pitfalls
                 spec_acceptance_paths · report_freshness · signature_audit_freshness
                 · **license_redlines** · (interface_ownership 诊断)
               ⇒ 回归 **908 passed / 17 skipped / 0 failed**（897 + 11）

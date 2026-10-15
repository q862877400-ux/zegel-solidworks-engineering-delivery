            ㊹ ★★ **护城河三域全部进清单**（轮 60）—— 起因是上轮游标的下一步
               「`original` 只有 2 条，而 `AGENTS.md` 说护城河是**三条**（拓扑/动画 AVI/Costing）⇒ 查它们落在哪」
               ★ 一查发现**两条都不在能力清单里**：
               ```
               | 护城河域  | 实现                                  | 清单条目（此前）| 判定 |
               | 拓扑优化  | scripts/sw_topology.py                | topology_optimization | ✅ 达标 |
               | **Costing** | **scripts/sw_costing.py（388 行，我们新增）** | **无** | ⇒ 补 `stitched` |
               | **动画 AVI** | **无**（只有 sw_api_* 的**索引**登记）  | **无** | ⇒ 补 `not_implemented` |
               ```
               ⚠ **为什么这是 A1/A9 的真实缺口**：
                 · **A9** 要「空白域护城河**有可跑的工程实现**，不是只有文档」
                   ⇒ 清单里**看不见 Costing** ⇒ **A9 无法判它**；
                 · **A1** 要「每一格**都有来源，或写明「不做 + 原因」**」
                   ⇒ 动画 AVI **既没实现也没写「不做」** ⇒ 那一格是**空白**
               ⇒ 补两条，都带 `limitations` 写明依据与下一步：
                 · `costing`：**零测试 ⇒ 无运行证据 ⇒ 按 `§九.6` 不得标 `verified`**；
                   但**静态签名已过**（传全 15 份反射时 0 存疑 / 0 查不到）
                 · `animation_export`：如实写「**官方 API 侧不是查不到**（反射里有
                   `get_/set_SaveEntireAnimation`），但**「索引里登记了成员」≠「有可用实现」**」，
                   且**不拿 `SaveEntireAnimation` 这个名字蒙混**（它是「是否保存整个动画」的属性，
                   未必是导出动作）⇒ 按**铁律 5** 写「查不到」
               ⇒ 条数 **29 → 31**；`original` **2 → 4**；**护城河三域都在清单里可查**
            ㊺ 🔴 **顺带发现 R8 是**幽灵规则****：`check_capabilities_schema()` 的 docstring
               从很早就写着「R8 读生成物 `docs/union-level-audit.md`」，
               而**全仓 grep 只命中那句 docstring**：**没有生成器、没有读者、文件也不存在**
               ⇒ **「文档串与代码不符，比没有文档更糟」** —— 读文档的人会以为
                 「等级已经审计过了」，**而审计根本没发生**
               ⇒ 本轮补上：`scripts/gen_level_audit.py`（**薄薄一层**，`LEVELS`/`SOURCES`
                 **从既有门禁 import**，**不重造**）+ `docs/union-level-audit.md`
                 （总表 + 两个分布 + `level × source` 交叉表 + 护城河三域
                  + **不一致自检**：把两个门禁函数的问题数写进报告
                  ⇒ **报告自己带「门禁怎么看」**）
               ★ **R8 新鲜度接进 `check_docs()`**：把当下数据重生成一遍**逐字节比对**
                 ⇒ 「忘记重生成」当场变红灯。**负例已测**：手改一个字节 ⇒ FAIL + 给出重生成命令
            ㊻ ⚠ **本轮踩到的两个坑**：① **事实 48** 又一次（Python 里写了**跨行字符串**
               ⇒ `SyntaxError: unterminated string literal`）⇒ 按**事实 53**改为**整体重写**；
               ② **PowerShell 的 here-string 里 `` `u `` 是 Unicode 转义** ⇒ 提交信息改走**独立文件**
               ⚠ 并且**我的 `python -c` 静默失败留下了一个乱名文件**（`偏离上游：181`）
               ⇒ 已删除（**只删自己的产物**）；**⇒ 教训：脚本失败后要 `git status` 看它留下了什么**
               ⇒ 回归 **911 passed / 17 skipped / 0 failed**

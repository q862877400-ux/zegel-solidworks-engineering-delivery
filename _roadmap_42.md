            ㊷ ★★ **R13：`source` 与 `provenance` 必须自洽**（轮 59）—— **实测逼出来的**：
               起因是「上轮 `original` 只有 3 条，而护城河域应更多」⇒ 逐条复核
               ⇒ **一查就查出我上轮的 2 个错**：
               ```
               ① `mold_tools` 写 `source: original`，**而它自己有 provenance**
                  指向 `Eduardof0nt/Solidworks-MCP-Server`
                  ⇒ **字段之间互相打架**（「原创」与「有来源」是**互斥的陈述**）
                  ⇒ 改 `mixed`（思路来自别家、**每一行实现**照出厂反射写）
               ② `pack_and_go` 写 `undetermined`，**而上轮我自己跑出的证据是 8 个模块全在 origin/main**
                  ⇒ 轮 58 把 8 条 undetermined 里的 7 条写进 RESOLVED，**漏了这一条**，
                    还错注「工具已给 upstream」（工具给的其实是 undetermined）
                  ⇒ 改 `upstream`
               ✅ 复核确认**对的**：`topology_optimization` / `simulation_and_fea` 的 `original`
                  —— 实现模块**全不在** origin/main 且**无 provenance** ⇒ 自洽
               ```
               ★ **R13 两条判据**：① `original` + 有 `provenance` ⇒ **报自相矛盾**；
                 ② `upstream` + `provenance` 指向**别家** ⇒ **报**（「上游」特指 `wzyn20051216`）
               ★ **R13 加完立刻抓到 `mold_tools` 那条 ⇒ 证明它有效，不是装饰**
               ⇒ 新分布 **`upstream=18 · mixed=8 · undetermined=1 · original=2`**
               ⇒ 回归 **909 passed / 17 skipped / 0 failed**
            ㊸ ⚠ **PowerShell 的 `` `u `` 是 Unicode 转义** —— 我在 here-string 里写了
               `` `undetermined` ``（反引号 + u）⇒ **整个命令 ParserError**（`Unicode 转义序列无效`）
               ⇒ **改用独立文件写提交信息**（`git commit -F <file>`）—— 又一次验证**事实 48** 的定则①：
                 **长内容（尤其含反引号 / 反斜杠 / 百分号的）一律走独立文件，不要内联进 shell**

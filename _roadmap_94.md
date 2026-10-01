            94 🎯 **第三条升 `verified`：`routing`**（轮 78）——
               `routing` 是 5 条 `stitched` 里**唯一还能在本机升的**（其余缺 OCP / 缺 SW 加载项 / 真机被阻塞）。
               ⚑ **先核依赖**（轮 77 的教训）⇒ `json`/`math`/`numpy`/`jsonschema`/`pydantic` **本机都可用**
                 ⇒ 本条**不需要** OCP，也不需要 SW 加载项（原生写入本就该 blocked）。
               ⇒ 新增 `tools/verify_routing_e2e.py`（**18/18 通过 · verdict: pass**）：
               ⚠ 判据**不是"跑通就算"**，而是**故意造违规**、逐条触发 limitations ① 的七项承诺：
               · totalLength = 50（3-4-5 直角三角形）· endpointTable · bendRadius 回读 ·
                 routingBom 一致；
               · **碰撞障碍 `FRAME` 被点名** · **支撑不足（required=2 + `routing_supports_insufficient`）**；
               · **弯曲半径过小（5 < 30）被抓**（`routing_bend_radius_too_small`）——
                 ⚠ 这一项我**没有假定**它一定被抓，**结果它被抓了**（如实记录在证据里）；
               · **`readyForNativeWrite is False`** ← limitations ② 的**核心诚实承诺**；
               · 输入侧：损坏 JSON / 根节点非 object / 缺失 都被**结构化**挡下 · **输入文件只读**；
               · 两个 CLI 入口（`--input/--output` 与 `--preflight`）。
               ⚠ 过程中踩到一次：我按**位置参数**调 CLI ⇒ `rc=2`；实测它用 **`--input/--output`** ⇒ 已改。
               ⇒ 清单升级：`level stitched → **verified**` · `evidence` 2 条 ·
                 `verified_versions` → `['2026']`（limitations ② 讲的正是「**本机 SW2026** 可发现
                 SWRoutingLib.tlb」，而那部分**真的跑了**）· `limitations` 一条不删。
               ⇒ 等级分布：**verified 25 → 26** · **stitched 5 → 4** · not_implemented 1
            95 ⚠ **两个既有测试被我打破 —— 正确处理（改行为就改测试 + 说明为什么）**：
               `test_capability_manifest_marks_unverified_workflows` 与
               `test_advanced_interfaces_do_not_inherit_unrelated_verified_levels`。
               * 后者**意图是**「**类型库存在 ≠ 实现已验证**」⇒ **那条照旧成立**：
                 我把 `routing` 从 `("surface_modeling","mold_tools","routing")` 元组里**移出**，
                 **`surface_modeling`/`mold_tools` 仍钉住**（它们**只有类型库、没有端到端验收**），
                 并**新增**一条单独断言钉住 `routing` 现为 `verified`；
               * **授权没放开**：`ready_for_unattended_use is False` 对三条**照旧**；
               * 两处都写了**为什么**（附依据与日期）。
               ★ **不是为了让测试变绿而改期望** —— 是先核「升级依据是否充分」（18/18 + 23 passed），再改。
            96 ⚑ **`stitched` 剩 4 条，且**全部**受外部条件阻塞**（下轮起应转做别的）：
               `dfm_checks`（需 B-Rep 证据）· `surface_modeling`（**需 OCP**）·
               `mold_tools`（**需 SolidWorks + OCP**）· `autocad_basic_drafting`（**真机被阻塞**）。
               ⇒ **本机能做的升 level 已做完**（23 → 26）。

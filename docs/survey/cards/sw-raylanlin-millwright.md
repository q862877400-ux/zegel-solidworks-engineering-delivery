# raylanlin/Millwright

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `raylanlin/Millwright` · https://github.com/raylanlin/Millwright |
| 许可 | **Apache-2.0**（`LICENSE:1-4` = `Apache License Version 2.0`；**仓内无 `NOTICE` 文件**，`Test-Path NOTICE` ⇒ False）⇒ 可借鉴可商用；义务是保留 `LICENSE`、**声明改动过的文件**；因无 NOTICE，无额外归属文件义务 |
| 元数据 | stars 37 · forks 9 · 语言 TypeScript（61 个 `.ts`）+ Python（49 个 `.py`）· 仓库 13768 KB · 建档 2026-04-29 · 最近推送 2026-10-06（来源：`gh api repos/raylanlin/Millwright`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\raylanlin__Millwright`（`--depth 1`）|
| 证据等级 | **实测**（两层都真跑了：sidecar 纯 Python 层 `python -m pytest sidecar/tests` ⇒ **67 passed in 0.15 s**；JS 层 `npm test`（15 个 `node --test` 文件）⇒ **tests 167 / pass 161 / fail 6**，6 个失败全在 `tests/sidecar-client.test.mjs`（要 spawn 真 sidecar，超时）；**SolidWorks 未跑**，建模能力结论止步 `source`）+ 读码 |

## 1. 一句话定位

**本批唯一自带 agent loop 的桌面应用（Electron），也是唯一同时踩过「验证完备性门禁」和「选择策略抽奖」两个结构性问题并留下复盘文档的一家**：87 个工具、每个改动类工具前后各拍一张几何快照并按类别断言 `ΔV` 的方向、`build_part` 支持一次提交整个零件计划、并为每一条 COM 坑写了症状→根因→修法的编号手册。（`sidecar/sw_agent/registry.py`）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：Electron 渲染进程的聊天框 → IPC → 主进程。**LLM 调用在主进程**，工具以原生 `tools` API 注入（`README.md`「Native tool calling」）。

**中间表示**：两层。① **工具 schema** 是单一事实源：`sw_agent/registry.py:1-20` 的 `@tool(name, description, params, category, destructive, internal)` 把 `ToolSpec` 推进 `TOOLS`，`_schema()` 生成 OpenAI 兼容函数声明，`call()` 统一校验必填与未知参数（`registry.py:61-80`）。② **`build_part` 的步骤序列**是给模型用的迷你 DSL：`steps`（数组）或 `steps_text`（一行一工具 `<tool> key=value`），上限 80 步，禁掉会换文档/装配/递归的工具（`sidecar/sw_agent/tools/batch.py:34-47`）。

**生成**：`build_part` 的立意写在文件头（`batch.py:1-19`）：逐工具调用会让模型「每一步都成功、整体不成形」，而一次性宏之所以看起来规划更好，正是因为作者一口气写完了整个零件；但宏有三个致命问题（米制单位、参数个数随版本变、`On Error Resume Next` 静默累积错误）。⇒ 它的解法是**「一次提交完整计划，执行仍走已加固的工具实现」**。

**编排**：主进程的 agent loop（观察→推理→动作），带确认卡（破坏性操作弹窗要人点）与视觉回环（`README.md`「Vision feedback loop」；文本-only 主模型时外挂一个视觉模型，把截图转成描述喂回规划器）。

**执行**：JSON-RPC over stdio → Python sidecar（常驻，一个 COM 连接握全程）→ pywin32。**跨版本自适应**是显式的设计（`README.md`「Cross-version compatibility」）：运行时探签名、成员缺失时降级到动态分发、`cut_extrude` 逐个试参数个数直到成功、特征树遍历从链表 API 退到 `IFeatureManager.GetFeatures`、切除方向按「正/反/对称」三试。sidecar 起不来时**自动退回内置 VBScript 引擎并在聊天里说明**（`README.md`「Dual-engine runtime」）。

**验证**：**统一入口 + 分类断言**（见 §3.2）。`server.py:142-160` 的 `_call_verified` 只对 `verify.MUTATING_KINDS` 里的工具拍快照、跑 `verify_step`，结果塞进 `data["_verified"]`，并写进会话日志（`server.py:219`）。文件的自我定位是「验证是**证据**，不是门禁」（`verify.py:19`）。

**交付**：`export_file` / `export_stl` / `export_session`（STEP/STL 等），另有工程图骨架（`new_drawing`/`add_drawing_view`/`add_section_view`/`insert_model_dimensions`/`insert_bom`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具面与粒度：**87 个，四种粒度混用**（实测计数）（`sidecar/sw_agent/registry.py`）

计数用「导入即注册」的方式实测（不是 grep）：`PYTHONPATH=sidecar python -c "…importlib 全部 21 个 tools 模块…print(len(TOOLS))"` ⇒ **TOOLS = 87**，其中 `destructive = 7`、`internal = 1`；grep 交叉验证 `(Select-String -Path 'sidecar\sw_agent\tools\*.py' -Pattern '^\s*@tool\(' -AllMatches).Count` ⇒ **87**，两者一致。四档粒度并存：
- **一动词一工具**：`extrude` / `cut_extrude` / `revolve` / `fillet_edges` / `chamfer` / `shell` …
- **领域宏工具**：`create_spur_gear`、`create_stepped_shaft`、`gear_pair_geometry`（把「齿轮/阶梯轴」这种成组几何收成一个工具）。
- **整件计划口**：`build_part`（最多 80 步）。
- **万能口**：`run_shell`（任意 shell 命令，`shell=True` + 超时，标记 `destructive=True` 因而走确认卡，`sidecar/sw_agent/tools/shell.py`）。

⇒ 与「一动词一工具 vs 万能代码口」的二分法都不同：**它把两者都给了，并用 `destructive` 标记统一管控**。

### 3.2 验证：**分类表 + 方向断言 + 完备性门禁**（本卡最该抄的一条）

`verify.py` 把每个工具**唯一**归入一个类别（`_FEATURE_CREATORS` / `_ADDS_VOLUME` / `_REMOVES_VOLUME` / `_DRESS_UP` / `_SKETCH_ADDERS` / `_QUERY_ONLY` / `_DOC_OPS` / `_SKIP` …，`verify.py:24-95`），然后按类别断言**变化的方向与幅度**：`snapshot()` 在调用前后各拍一次（特征名/抑制态/包围盒/实体数/草图段数/体积/面积/质心/装配组件与变换，`verify.py:141-203`），`verify_step()` 据此判：
- `extrude`/`revolve`/阵列/镜像必须 **ΔV > 0**；`cut_extrude`/`shell`/`cut_face_outline` 必须 **ΔV < 0**；倒角类允许正负但实体数不变（`verify.py:24-31`）。
- 装配：组件数 +1、`Transform2` 是否真的移动（`verify.py:1-15` 的 P124 段说明：`AddComponent5` 返回对象 ≠ 插入成功；`AddMate5` 接受配合也可能什么都没动）。
- 生成器（`create_spur_gear`）与参考几何各有一套（`verify.py:234-241`）。

**完备性门禁**是这套设计能活下来的原因：`sidecar/tests/test_verify_coverage.py` 有 5 个断言——每个注册工具必须被 `classify` 认领、不许落进两张表、`MUTATING_KINDS` 必须真实存在、每个 mutating 工具必须真的 `checked: True`、查询类永不被快照。文件头交代了它为什么存在：「工具注册表（registry）和验证分类表（verify）是两张平行的人肉维护表，没有任何机制保证同步 ⇒ 忘了分类就静默漏验证」，并举了两个实例（`start_sketch` 的验证分支被 `_SKIP` 拦成死代码、`sketch_rounded_rectangle` 上线三个版本无人验证）。

⇒ **可迁移性最高**：我方 439 个工具与能力台账正是「两张平行的人肉维护表」，这条门禁是现成的棘轮。（`capabilities.yaml`）

### 3.3 选择策略：**从「六条兜底」改成「三条各自完整 + 探针缓存」**（本卡第二条最该抄）

`sidecar/sw_agent/edge_select.py:1-30` 的复盘写得比代码值钱：原先「边的选择」散在六条 fallback 路线里，**每次某台机器失败就再加一条**，到第八轮一次调用可能走 A/B/C/D/0/E 任意一条且**没有任何一处能校验结果**——「这不是健壮，是抽奖」。而且抽象选错了：真正要回答的是「用户说的那些边是哪几条」，不是「第 7 条边是什么类型」。

现在的设计是三条**各自完整、各自可验证**的策略：`faces`（两个侧面之间是竖边，任意形状都对）、`box`（包围盒算角点，只对箱体极稳）、`selected`（用户在 SolidWorks 里自己选，永远可用）；`probe()` 在当前模型上实跑一遍数出各策略选中几条边并缓存，之后直接用验证过的那条；失败时明确说出每条试过什么、拿到什么，并给「你手动选边后 `edges="selected"`」这个诚实兜底。

⇒ 这条对治的正是我方「选择失效」的老问题：**别用兜底链，用可验证策略 + 探针**。

### 3.4 回读验证：解了，且判据放在工具层（不是模型层）

与 hjbaard「判据外包给模型」相反（见 `sw-hjbaard-solidworks-mcp.md` §3.4），Millwright 的判据在 sidecar 里：工具返回的 `_verified` 是**服务端算出来的**，模型只读结论。代价是它必须维护分类表（见 §3.2 的门禁）。

### 3.5 事务式建模：**没有真正的事务，只有「确认 + 备份」**

破坏性操作先弹确认卡（工具名 + 全参数），确认后**在改动前备份当前文档**（`README.md`「Safety, by default」），再执行。这与 hjbaard 的「失败回滚特征树」是两种档位：备份能救整份文件，但救不了「多步中第 3 步失败」的半成品状态。`build_part` 的 `_FORBIDDEN`（禁掉换文档/装配/递归，`batch.py:38-47`）是在**预防**这一类半成品，而不是回滚它。

### 3.6 单源 COM 互斥：**解了，进程内一档**

`sidecar/sw_agent/com_executor.py` 是唯一出口（`docs/COM-PITFALLS.md` #3：「所有 COM 走 `ComExecutor`（P122）。不要在别处 `CoInitialize`」）。但它是**桌面应用的单实例模型**，天然只有一个 sidecar 进程；没有跨进程互斥（与我方同一档位）。

## 4. 运行条件与依赖

- Windows 10/11 x64 + SolidWorks 2017+（`README.md`「Requirements」）；Electron 28 / React 18 / TypeScript 5.3。
- 源码跑：`npm install` + `pip install pywin32 pillow`（`README.md`「From source」）；`SKIP_SW_CONNECT=true` 可只跑 UI。
- sidecar 测试：`PYTHONPATH=sidecar python -m pytest sidecar/tests` ⇒ **实测 67 passed in 0.15 s**（2026-11-02，Python 3.14.7）。0.15 s 说明这批用例全是纯逻辑 + 假对象，**不碰 COM**。
- JS 测试：`package.json` 的 `test` 脚本串了 15 个 `node --test` 文件（先 `tsc -p tsconfig.main.json`）。**实测：`npm install` 装了 532 个包后 `npm test` ⇒ `tests 167 / pass 161 / fail 6`**（2026-11-02，Node 26.7.0）；6 个失败全在 `tests/sidecar-client.test.mjs`，形态是 `ping … TIMEOUT` 与 `CANCELLED` 断言失败（要 spawn 真 Python sidecar 才会通）。

## 5. 失败模式与已知坑

**自述的 22 条 COM 坑**（`docs/COM-PITFALLS.md`，每条症状→根因→修法→轮次编号）是本卡最重的产出，挑对我们最贵的前 8 条：
1. **别为「方法当属性」切早绑定**（#1/#2）：晚绑定下 pywin32 先试 PROPERTYGET，成功就把方法当属性返回其结果；修法是 `typeinfo.flag_methods`。而切早绑定会撞接口墙（一对象只绑一个接口 ⇒ `IModelDoc2` 上没有 `IPartDoc.GetBodies2`）。
2. **启动路径永远不要生成 typelib 缓存**（#5）：会把连接饿死（「SolidWorks 正在运行但 COM 拒绝」）。
3. **`SelectByID2` 的 Callout 必须 `VARIANT(VT_DISPATCH, None)`**（#6）：裸 `None` 是 VT_NULL ⇒ Type mismatch。
4. **byref out 参数要 `VARIANT(VT_BYREF|VT_I4, 0)` 并读 `.value`**（#7）：裸 `0` Type mismatch；`pythoncom.Missing` 在部分方法上直接报错；`OpenDoc6` 传 `Missing` 会返回 None 且文档没加载（从而让后续 `AddComponent5` 静默无效）。
5. **`ToolsCheckInterference2` 是 Sub，out 参数晚绑定下永远 None ⇒ 永远报「无干涉」**（#10）：改用 `InterferenceDetectionManager`，且 `IInterference.Components` 是属性不是方法。
6. **`AddComponent5` 返回对象但没插入 / `AddMate5` 接受配合但什么都没动**（#12/#13）：只能靠「组件数前后对比」「`Transform2` 前后对比」验证。
7. **坐标选边必须先 `ForceRebuild3(True)`**（#14），且只能选到当前视角**可见**的边（#15）——这是「索引选择」存在的理由。
8. **残留选中会让 `FeatureFillet3` 圆掉整个面**（#16），且数边要 `GetSelectedObjectType3 == 1`（**`swSelEDGES=1`，2 是 FACES**）；`IsSame`/COM 引用相等不可靠（#20）⇒ 用几何指纹去重。

**结构性问题**（比坑更值钱）：
9. **两张平行的人肉维护表**（registry ↔ verify 分类）：靠 `test_verify_coverage.py` 挡（§3.2）。
10. **兜底链式选择**（§3.3）：靠「三条完整策略 + 探针」重构掉。
11. **早绑定接口墙**：`docs/COMPARE-solidpilot.md` 自己承认 P15→P46→P69→P72→P116–P120 是同一类问题打了 ~60 个补丁。
12. **provider 会压平嵌套数组**：`build_part` 的 `steps` 在某些 provider 上到达时是 `["","",""]`，于是加 `steps_text` 行式兜底（`batch.py:120-148`）。
13. **辅助函数写在 `@tool` 装饰器与 `def` 之间会被当成工具注册**（`batch.py:122-124` 的注释，是它真踩过的）。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **不解，绕行**：按面的归属/包围盒/人工选择三条**可验证策略**选边，探针缓存；无拓扑 ID | `sidecar/sw_agent/edge_select.py:1-30` |
| 回读验证 | **解了**：前后快照 + 按类别断言 ΔV 方向/幅度 + 完备性门禁；判据在服务端不在模型 | `sidecar/sw_agent/verify.py:141-241`、`sidecar/tests/test_verify_coverage.py` |
| 事务式建模 | **部分**：破坏前备份 + 确认卡 + `build_part` 禁换文档；无逐特征回滚 | `README.md`「Safety, by default」、`tools/batch.py:38-47` |
| 单源 COM 互斥 | **解了进程内一档**：全部 COM 走 `ComExecutor` | `docs/COM-PITFALLS.md` #3 |

**Q3 答**：**桌面应用（Electron + 自带 agent loop），不是 MCP 服务端也不是纯库**；工具面 **87 个**（导入实测，命令见 §3.1）；粒度 = 一动词一工具 + 领域宏 + 整件计划口（`build_part`）+ 万能口（`run_shell`）**四档并存**。（`sidecar/sw_agent/registry.py`）

**能学（按性价比排序）**：
1. **`test_verify_coverage.py` 这套「注册表 ↔ 验证分类表必须同步」的门禁**：直接对应我方「439 个工具 vs 能力台账」的漂移风险，且判据可 grep、可 CI。
2. **按类别断言 ΔV 方向**（`_ADDS_VOLUME`/`_REMOVES_VOLUME`/`_DRESS_UP`）：比「有没有变」强一档，且不用闭式解就能抓住「静默无效切除」。
3. **`edge_select` 的复盘 + 三条完整策略 + 探针缓存**：我方选择失败的现成解药，尤其是「诚实兜底（让人手选）好过猜」这条判据。
4. **22 条 COM 坑手册**（尤其 #5 启动期 makepy、#10 Sub 的 out 参数、#12/#13 静默无效、#16 残留选中圆整个面、#20 引用相等不可靠）：与我们 `known-facts`/`dead-ends` 一一对得上，可逐条交叉验证。（`docs/COM-PITFALLS.md`）
5. **`build_part` 的「先规划后执行」立意**：给出「为什么逐工具调用会整体不成形」的具体论证，可用来设计我方的计划型工具。
6. **`verify.py` 的 `precheck`**（执行前静态检查，`verify.py:424`）：把一部分失败提前到「还没碰模型」。
7. **视觉回环的双路径**（多模态主模型直接看图 / 文本模型外挂视觉模型）：如果我方要接非多模态模型，这是现成方案。

**不能学**：
- **`run_shell`（任意 shell）**：它把这当成能力，我方若加，等于把「工具面 = 攻击面」这条防线撤掉。
- **「验证是证据不是门禁」的口径**：它自己因此吃过「工具谎报成功」的账（`docs/COMPARE-solidpilot.md` 自述 P46→P120 反复）。我方该做的是**证据 + 硬门禁**两件都要。
- **无 IR**：它同样只有特征树 + 工具，结构上做不了「先编译后执行」。
- **备份代替回滚**：救文件不救步骤。
- **`Destructive` 标记的粒度**：`run_shell` 与 `cut_extrude` 同级，说明这个标记只能兜底不能分级。

## 7. 许可与红线

**Apache-2.0**（`LICENSE:1-4`），**无 `NOTICE` 文件**（`Test-Path NOTICE` ⇒ False）。义务两件：① 保留 `LICENSE` 全文与归属声明；② **修改过的文件必须带显著变更声明**（Apache-2.0 §4(b)）。★ 移植 `verify.py` 的分类表、`edge_select.py` 的策略骨架、`COM-PITFALLS.md` 的事实条目时，来源头写 `raylanlin/Millwright（Apache-2.0，LICENSE:1）` + 改动说明；因无 NOTICE，不必进 `THIRD-PARTY-NOTICES.md`（但若将来上游补了 NOTICE，义务随之而来，需复核）。

## 8. 证据清单

- `sidecar/sw_agent/registry.py:1-20`（`@tool` 单一事实源、`ToolSpec` 字段）· `:61-80`（`_schema` + `call` 的必填/未知参数校验）
- `sidecar/sw_agent/verify.py:1-20`（三层职责 + P124 量化口径 + 引用 SolidPilot 的 ΔV≤1% + 「验证是证据不是门禁」）· `:24-95`（七张分类表与 `_SKIP`）· `:97-104`（`classify`）· `:141-203`（`snapshot` 全字段）· `:210-220`（`_dv` 相对变化）· `:225-241`（`verify_step` 分支）· `:424`（`precheck`）
- `sidecar/sw_agent/server.py:142-160`（`_call_verified`：只对 mutating 类拍快照、写 `_verified`）· `:196`（调用点）· `:219`（会话日志记 `verified`）
- `sidecar/tests/test_verify_coverage.py`（5 条完备性断言；文件头记录两个真实事故）
- `sidecar/sw_agent/edge_select.py:1-30`（为什么单独成模块、「六条兜底不是健壮是抽奖」、三条策略 + `probe()`）
- `sidecar/sw_agent/tools/batch.py:1-19`（`build_part` 立意与宏的三个致命问题）· `:34`（`MAX_STEPS = 80`）· `:38-47`（`_FORBIDDEN`）· `:120-148`（`_steps_from_text` 行式兜底 + provider 压平数组的实例）· `:151-195`（工具 schema）
- `sidecar/sw_agent/tools/shell.py`（`run_shell`：`shell=True` + 超时 + `destructive=True`）
- `docs/COM-PITFALLS.md:1-97`（22 条编号坑，逐条含症状/根因/修法/轮次）· `docs/COMPARE-solidpilot.md:1-60`（对 SolidPilot 的第三方评估：47 vs 77 工具、ΔV≤1%/ΔA≤1%、AGPL、`StaExecutor`；**属【转述】**）
- `docs/VERIFY-ISSUES.md`（多参数 API 待宏录制确认的清单）
- `README.md`「Cross-version compatibility」（签名发现/动态分发/切除方向三试）、「Safety, by default」（确认卡 + 备份 + 脚本黑名单）、「Vision feedback loop」（双路径）、「Known limitations」
- 实测：`PYTHONPATH=sidecar python -m pytest sidecar/tests -q -p no:cacheprovider` ⇒ `67 passed in 0.15s`（2026-11-02）
- 实测：`PYTHONPATH=sidecar python -c "…import 21 个 tools 模块…print(len(TOOLS))"` ⇒ `TOOLS = 87`、`destructive = 7`、`internal = 1`
- 元数据：`gh api repos/raylanlin/Millwright`（2026-11-02 取：stars 37 / Apache-2.0 / pushed 2026-10-06）

## 9. 未确认事项

1. **JS/TS 层 6 个失败未定根因**：`npm test` 实测 `tests 167 / pass 161 / fail 6`，6 个全在 `tests/sidecar-client.test.mjs`（`ping … TIMEOUT`、`aborted signal returns CANCELLED`）——是「本机起不来 sidecar」还是「客户端本身有 bug」**未区分**（没有真 SolidWorks 也能起 sidecar，但缺 `pywin32` 环境变量等前置未查）。README 徽章写的 201 个用例与实测 167 的差**也未核**。
2. **`verify_step` 的判据是否在真机上都成立**：`67 passed` 是纯逻辑层，**几何断言的真机正确性未验**（需要 SolidWorks）。
3. **`ΔV` 判据的容差**：`_dv` 给相对变化，但各分支用的阈值我只读了结构，**具体阈值与误判率未逐条核**。
4. **SolidPilot 的 47 工具/ΔV≤1% 等数字**：来自 Millwright 自己的 `docs/COMPARE-solidpilot.md`（对标版本 `main@fc3c743`，2026-09-12），**属【转述】**，E 线复核时应以 SolidPilot 源码为准。
5. **`edge_select` 的 `probe()` 在几何变更后是否重新探**：缓存失效条件未逐行确认。
6. **双引擎退回 VBScript 的触发条件与实际成功率**：只读 README，**未验证**。
7. **`build_part` 的 80 步上限在多实体零件上的表现**：未验。

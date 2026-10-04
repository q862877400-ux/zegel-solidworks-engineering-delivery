# 智能体团队分工

> 角色定义在 `~/.dsh/team-roles.yaml`（全局）；用法见 `~/.dsh/智能体团队-使用说明.md`。三个角色的工具限制是机制锁死的。

| 角色 | 工具限制 | 在本项目干什么 | 绝不能干 |
|---|---|---|---|
| researcher | 禁 write/edit/pwsh | 跑 `sw_know.py` / `swdoc.ps1` / 反射建能力全景；扫 `C:\swprojects\` 下 21 个项目定位可移植实现 | 不改任何文件；只报事实，不提改动建议 |
| coder | 可写 | 按 `gap-analysis.md` 移植或新写 `scripts/sw_*.py` + `tests/test_*.py` + `provenance` 标注 | 不启动 SolidWorks、不跑 COM、不编译 C#/C++；不写「已验证」 |
| reviewer | 禁 write/edit/pwsh | 复核签名比对表、许可合规、结构一致性、五统一门禁、禁词 | 只报问题，不动手修 |

派活按「来源 + 域」两个维度切，互不重叠：来源组一人一家（四家外部 MCP 各扫工具清单、许可与测试口径），域组按 `高级/专项`、`曲面`、`钣金` … 分批。每个任务登记 `write_scopes`（绝对路径，代码副本不在 DSH 工作区内），例如 `C:\swprojects\sw-skill-fork\scripts\sw_simulation*.py` 与其对应的 `tests\`。

lead 维护 `docs/union-coverage-matrix.md` 与 `docs/gap-analysis.md` 的打勾状态，并汇总 `docs/harvest-report.md`。

## 多用 space-bunny

**space-bunny 免费，且实测能干机械穷举、全面阅读、逐条对账、抄录、模板产出、语义配对与近边界探针草案**，因此这类活默认派它干。三种模式：核心工作派三路独立做（各写独立文件，避免候选正文灌进 Lead 上下文），再派第四路当裁判打分并指出该并入哪些片段；很有用但平时成本高的活整批丢给它（全面扫描、全面阅读、穷举核对、逐条对账）；判据设计、真机执行（COM 单源）、门禁本体、known-facts、提交由 Lead 自己做。

能力档实录在 `specs/202-user-coverage-gaps/recon/bunny-L1..L5*`。L1 抄录。L2 机械聚合：读 83 个函数、认出 67 个有官方成员、去重出 143 个成员名，并自己发现 `read` 工具的行号偏移。L3 模板产出：反推出工具注册的 import 机制，认出带连字符的父目录不能当模块名，找到 `scripts/sw_drawing.py` 那座兼容桥。L4 语义配对：把「能读这种表」与「能建这种表」分开判。L5 近边界探针草案：找出探针里 `GetBreakLineCount` 的 out 参数用法错。

已被真决策采用的外派产物：`recon/scan-S1a|S1b|S2a|S2b|S3-1..3|S4` 七份扫描、`recon/scan-contract-audit.md`（30 份官方契约逐份对账，可信 17 / 有缺 13 / 不可信 0）、`recon/cand-A|B|C.md` 与 `recon/cand-verdict.md`、`recon/probe-verdict.md`。

**派活时写清三条**。一，给文件路径并明确要求重新读，否则它会按过时的签名准备实参。二，显式说明 `param_alias` 要应用，否则它会把好参数当成坏参数报。三，要求每条结论带可搜索的原文片段、不要行号，因为行号随代码漂移（实测偏 47 行）。

**它的判据有已知弱点，产出永远要经 Lead 复核**：它会照抄想象或过时的契约，也会把一条错的既有结论当既定事实。因此它的产出不许直接进 `capabilities.yaml` 的 `verified`。

## 子代理一律用 space-bunny，不用 DeepSeek

**派子代理用 `role="artist"`（space-bunny-free）；不要用 DeepSeek 起子代理 —— 它贵。** Lead 自己仍是 DeepSeek，只有派出去的那些受这条约束。

实测偏差：2026-10-04 查会话注册表，7 个 teammate（`impl-drawing` / `rev-drawing` / `qwen-test` / `contract-audit` / `impl-drawing-missing` / `impl-drawing-missing2` / `contract-audit2`）全部记成 `model: deepseek-flash`、`provider: spawn` —— 即都不是 Bunny。这批不是我这几轮建的，所以只能说注册表现在这么记；但「M2 铺张用免费的 space-bunny」这条作业方法当时确实没执行。派活前先确认 `list_agents` 里那条的 `model` 是 `space-bunny-free`，不是就说明角色没传对。

省下来的额度用在 Lead 的真机与门禁上；机械穷举、全面阅读、逐条对账、抄录这类活本来就不需要 DeepSeek。

### ★★ 扇出之后还要核一次**运行期记录** —— 参数写了 Bunny ≠ 它真的跑了 Bunny

```
python tools/check_subagent_models.py --marker <我提示词里独有的串> [--marker …] [--exclude-self <Lead会话片段>]
python tools/check_subagent_models.py --selftest      # ★ 造 1 bunny + 1 deepseek 假会话，必须报出后者
```

**为什么**（★ 2026-10-04 · 业主追问「你派出的子代理是什么模型，有没有遵循必须用 Bunny 的纪律」触发）：
上面那条「实测偏差」记的是 **Teammate** 注册表；而 **`workflow` 扇出的子代理**另有记录 ——
★ 判据只能是**运行期写下的字段**，不能是我在 `agent()` 里传的 opts（★ 事实 62：写着 ≠ 生效）。

**判据与实测**：
- 源：DSH 的会话投影缓存 `~/.dsh/storages/session_projcache/sessions/*.json`；
- 每份子代理会话里有**运行期字段**：`"model"` · `"provider"` · `"lastModel"` ·
  `"cost": {"<provider>": {"<model>": …}}`（★ 这三个字段名是**实测读出来的**，不是猜的）；
- ★★ 挑「我派的」要用**提示词标记串**（我扇出提示词里独有的文件名/字段名），
  ★ 免得把**别的对话 / 别的项目**的子代理算进来 —— ★ 本机实测：缓存里共 **2668** 份会话记录，
  其中**别人的子代理 2232 份**（含 `deepseek-flash` 的）⇒ ★★ **不筛标记串就会得出「纪律没执行」的错误结论** ✓
- ★★★ **实测结论（2026-10-04 两坡）**：我派出的 **62 路全部是 `space-bunny-free` / `opencode-zen`**，
  `deepseek` 字样 **0 次**；★ 而唯一那个 `deepseek-flash` 的会话是 **Lead 自己**（`--exclude-self` 排掉）✓

### 大批量扇出用 workflow，且 provider 与 model 必须成对写

`spawn_teammate` 有硬上限 8（本会话实测：已有 7 个 teammate 时第 8 个报 `Team member limit 8 reached`），派不出上百路。要规模就改用 `workflow`：写一段 JS，用 `pipeline(items, stage)` 把每项扇出一个子代理。

**`agent()` 的 opts 里 `provider` 与 `model` 必须成对写。只写 `model` 会整批静默失败。** 2026-10-04 实测：传 `model: "space-bunny-free"` 而不传 `provider`，100 路跑完回 `{requested: 100, returned: 0, rows: []}` —— **100 个子代理全部失败，而返回值里没有任何错误信息**。补上 `provider: "opencode-zen"` 后同一批 2 路探针 `returned: 2`，且读数与 Lead 自己数的一致（`IView` 461 个 .md、`IDatumTag` 34 个）。

两个教训：**一，`returned: 0` 要当成失败来查，不能当成「没活干」**；**二，先跑 2 路探针再铺 100 路** —— 上面那次 100 路是白跑的代价换来的。

### ★★ 扇出之后的**五步管线**是一条命令 —— 别再用 `output/` 里的一次性脚本

```
python tools/bunny_toolspec_pipeline.py collect  --dir output/bunny-rowsN --out output/rowsN-all.json
python tools/bunny_toolspec_pipeline.py backfill --in output/rowsN-all.json --out output/rowsN-bf.json
python tools/bunny_toolspec_pipeline.py gate     --rows output/rowsN-bf.json --json output/gateN.json
python tools/bunny_toolspec_pipeline.py remaining --report output/gateN.json --out output/newN.json
python tools/bunny_toolspec_pipeline.py build    --report output/newN.json --batch NN --out mcp-server/tool_specs_batchNN.py
python tools/bunny_toolspec_pipeline.py drop-refused --batch-file mcp-server/tool_specs_batchNN.py
python tools/bunny_toolspec_pipeline.py list-refused        # ★ 打印"不做"政策名单（12 条，逐条带原因）
```

**为什么要有它**（★ 2026-10-04 · 业主问「会不会有一次忘了提交」时查出来的真缺口）：
批 80–88 的工序**写在提交信息里**，而其中的「回填 `source_kind`」「算可建未挂」「删不做项」
三步原先只是 `output/_*.py` 里的一次性脚本 —— ★ 而 **`output/` 被 gitignore**
⇒ ★★ **别人克隆仓库后跑不出同样的批次**（管线不可复现）✓
⇒ 现已收进入库工具；★ **"不做"政策名单（12 条、逐条带原因）也从草稿提升成 `REFUSED` 常量** ——
★ 评它是**政策**（不是草稿），必须入库、必须可复核 ✓

★★ 实测（在真实数据上走了一遍）：`remaining` 报「门禁报告 56 行 ⇒ 可建且未挂 **0** 行
（**已挂跳过 17**）」—— ★ 那 17 正是批 88 建掉的那一批，**证明这一步真的对** ✓



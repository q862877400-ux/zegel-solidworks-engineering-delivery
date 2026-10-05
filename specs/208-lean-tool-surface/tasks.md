# 规格 208 · 任务 checklist

> `[ ]` 未做 · `[x]` 已做且**过判据** · 每条后面写「怎么知道的」。★ 未过判据的不许写 `[x]`。

## P0 · 沙盒复制收尾 + 生产基线

- [x] **T0-1** 沙盒 harness 与生产同提交 —— 两边 `rev-parse HEAD` 同为 `d37ca457e2c1fb90b10f917a62692bc392d97a64`
- [x] **T0-2** 沙盒 DSH_HOME 能组合 —— `--dump-config` 成功输出组合树；配置类文件与小文件已就位；`harness` 指向**沙盒**；`node_modules` 用 `/SL` 复制并**把 5 条指向生产的符号链接改指沙盒（剩余 0）**
- [ ] **T0-3** 记生产开工指纹 ⇒ `prod-baseline.json`
- [ ] **T0-4** 沙盒跑一次最简会话并拿到会话记录 —— 🟡 已证明**能读会话记录**（分帧已破解），但沙盒自身还没跑过

## P1 · 落地 `mode: 'lean'`

- [x] **T1-1** 联合类型 + zod union 加 `'lean'` —— 负例 `leanx`\`LEAN`\`catalog`\`""` 全被拒
- [x] **T1-2** `catalogSection()` + `renderToolCatalog()` —— 实测输出 `- export_step(path: string, units?: "mm"|"inch"): ★ 导出 STEP`
- [x] **T1-3** `wireSchemas()` lean 分支（跳过 runtime \ 骨架全集 \ 不加 `run_code`）
- [x] **T1-4** `leanSchemaOf()` 骨架投影（描述只剩第一句）
- [x] **T1-5** `view()` 的 `run_code` 注入收紧到 `ptc`\`both`
- [x] **T1-6** 分段注册（lean 注册 catalog、不注册 SDK）
- [x] **T1-7** 负例测试 7\7 全绿
- [ ] **T1-8** 沙盒 `--dump-config`（lean）—— 🟡 组合已通；还没带 `DSH_TOOLS_MODE=lean` 验过
  ★ 发现：**生产 profile 本来就按环境变量切模式**（`mode: !!js process.env.DSH_TOOLS_MODE`）⇒ 5 条件只需换环境变量

## P2 · 真工具目录

- [x] **T2-1** 从会话记录提取工具面 —— ★ **破解分帧**后取到最富 **511** 个的真实面
- [x] **T2-2** `mcp_connector.json` 的 `tool_catalog` 取 UFO —— 19 个（扫描并集里也含 `mcp__ufo` 19）
- [x] **T2-3** 插件工具（computer-use `cua` 56 · browser 6 · univer 14 · hindsight 8 · sciverse 6 + 内建）—— 由 13 个 cwd 组 \ 24 个会话抽样得到
- [x] **T2-4** 合并去重 ⇒ `catalog-all.json`，**N = 731**，每个带 `source`
- [x] **T2-5** 报 N 与来源分布

## P3 · 造题

- [x] **T3-1** 复用 207 的 145 项（逐字）
- [x] **T3-2** 补 54 题自然口语（冷门域 + 跨家族：桌面 \ 浏览器 \ 表格 \ 文献 \ 记忆 \ 协作 \ 校验）
- [x] **T3-3** `tasks-208.json` 落盘；★ **不预标唯一答案**（避免循环），答案由 Lead 判

## P4 · 5 条件对照

- [ ] **T4-1…5** ★ **一律用 `opencode-zen` \ `space-bunny-free`**（D-8）
- [ ] **T4-6** `conditions.json` 汇总（估算 vs 实测并列）

## P5 · 判「能不能干活」

- [ ] **T5-1** 逐条判 ⇒ `judgments.json`
- [ ] **T5-2** 每条件准确率 + n
- [ ] **T5-3** 判 SC-9（index 是否低分）

## P6 · 报告 · P7 · 等合格后做 preset 与生产补丁

- [ ] **T6-1…3** · [ ] **T7-1…2**

## ★ 第 1 轮收尾（2026-10-05）

- [x] **P1–P6 全部完成**（见 goal-bar §一）
- [x] ★ 五条件对照 **995 行 · 0 错误**（bunny）
- [x] ★ **386 唯一（题,选中）对全部判完**，判据写死进 `judge-rubric.md`
- [x] ★ 配对 McNemar：★ **只有 ptc 那条显著（p=0.0243）**
- [x] 报告 `docs\recon\lean-tool-surface.md`
- [ ] ⛔ **P7 等业主判「合格」**
- [ ] T0-3 记生产开工指纹（★ 本轮**未做** —— 但全程**未写生产**，可事后补）

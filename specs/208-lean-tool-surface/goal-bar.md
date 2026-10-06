# 规格 208 · 目标栏（唯一进度字段）

> 状态**只写在这里**。★ 不含行号。

**目标**：`goal-c8e6c479-932a-4a6a-8919-9fc7e4ad0bab`（40 轮上限）
**业主裁定**：★★ 「我觉得可以了，就 S 方案」= 合格；★ 追加要求：**按 preset 分别选工具呈现方式**
**上次更新**：2026-10-05（第 6 轮：按 preset 选 —— 查清是现成功能）

## 一 · ★★★ 本轮结论：这个功能**上游本来就有**

- `tools.presentAs(mode)` —— 按**作用域**记呈现方式（上游既有，含冲突守卫「一个 composition 选一种」）
- `@deepseek-ai/dsh-agent-tool-presentation` —— **preset 用来声明它的那一行**（上游既有）
- ★ 其 README 原话：**「工具注册表搬不进 preset（消费方全在宿主平面），preset 能拥有的是这份注册表的呈现方式」**

⇒ ★★ 我前两轮说"做不到 / 要塞进 preset"**都是错的**，已在 spec D-11 记账。

### 补的两个缺口（D-12）
1. 该行的 `mode` zod 联合原本只有 `native|ptc|both` ⇒ **加 `lean`**
2. 原本非 native 一律 `inject(['ptcRuntime'])` 等待 ⇒ **lean 走立即路径**（否则永久 pending）
3. ★ 另修一处真 bug：`presentAs` **漏注册 catalog 段**，且段的选择按**部署默认** ⇒ native 默认部署下的 lean preset 拿不到目录段（**我自己的新测试抓到的**）

## 二 · 阶段进度

| 阶段 | 状态 | 依据 |
|---|---|---|
| P0–P6 模式/目录/对照/判据/报告 | ✅ | 见第 2–5 轮 |
| **P7 preset + 补丁** | ★ **交付物已就绪** | `deliver/` 5 个文件 |
| **按 preset 选** | ★★ **已实现并实测** | `agent-tool-presentation` **9\9**；`tools` **447** 测（1 条为**既有**失败） |

## 三 · 交付物（`D:\AI\DSH-sandbox\deliver\`）

| 文件 | 状态 |
|---|---|
| `lean-mode.patch`（34,386 B · 8 文件 +437\-16） | ✅ `git apply --check` **exit 0** |
| `preset-lean-snippet.yml` | ★ **按 preset 选的 4 行贴入片段** |
| `lean-tools.patch.yml` | 全局整进程开关 |
| `install.ps1` | ✅ `-Check` 实测报「未装」 |
| `README.md` | 判据 / 用法 / 限度 / 回滚 |

## 四 · 关键事实（回答"装上之后会怎样"）

1. ★ **源码改动不被热加载**：`dsh-hmr` 的 `config.root: []` **是空的** ⇒ 装上前**运行时零变化**，要重启才进内存。
   ★ 我第 5 轮说"可能触发热重载、不敢动"——**那是错的**，已更正。
2. ★ **profile 的 `cordis.patch.yml` 被 HMR 监听**（其自身注释记有实测：「保存即热生效」）⇒ 贴 preset 片段**保存即生效**（新会话）。
3. ★ 装完**默认逐字节不变**：`mode` 仍取 `DSH_TOOLS_MODE`，不设就是 `native`。

## 五 · 本轮自查记录（我自己写错/判断错的）

1. ★★ 误判"按 preset 做不到"（真：上游既有）—— 见 D-11
2. ★★ 误判"改源码会热重载"（真：`root: []`）
3. ★ 我的"无条件注册三段"改动动了上游 5 条断言 ⇒ **改回更小的方案**（只在 `presentAs` 里补 catalog）
4. ★ `lastIndexOf("});")` 返回 -1 导致把 spec 文件**复制了一份**（已重建）
5. ★ 双语 README 改了要重录 `README.i18n.yaml`（**1158 对校验通过**）

## 六 · 仍未做

**把补丁装进运行实例** + **给 preset 贴片段** ⇒ ★ **等你定时机**（贴片段保存即生效，会影响新会话的呈现方式）。

## 七 · 第 7 轮：团队内混用呈现方式

- ★★ **引擎层已实测**：子作用域 `presentAs` 覆盖父/preset 的（`modeFor` 近者优先，测试 10\10 里那条）
- ★★ **接线已做**：团员 `toolMode` 贯通（快照/spawn/重写/角色表），**125\125 绿**
- ★★ **preset 路线对团员无效**：子 agent 继承父 preset（`child-agent.ts` 用 `composedPreset(parent.ctx)`）
- ★ **我自己写错并修掉的两处**：① spawn 后安装是**死代码**（那时 agent 还没 live）⇒ 删，正主是 `recoverFor`
  ② 类型检查抓到 3 处类型错误（vitest 不查类型）⇒ 已修，`pnpm run typecheck` 干净
- ★ **限度**：未在真团队回合里端到端观测到"团员按自己的模式装配"
- 沙盒提交 `1a806fedd2`；补丁重建 50,407 B / 14 文件 / `apply --check` exit 0

## 八 · 第 8 轮：沙盒**真启动**验证（功能生效 + 重启）

- ✅ **补丁严格等价**：`git apply --check --reverse` **exit 0** ⇒ 补丁 = 生产 `d37ca457e2` → 我的 HEAD 的全部改动；工作树干净
- ✅ **补丁完整性**：抓到并补上一个**漏提交的测试**（"子作用域覆盖父作用域"那条 —— 正是团队混合模式的关键证据）
- ✅ **真启动**：沙盒 profile `leanprobe`（headless 模板）跑真回合，**4 次冷启动全 exit 0**
  | 次序 | 系统提示词长 | 含目录段 | 判读 |
  |---|---|---|---|
  | #1 | 2,951 | ✗ | native 基线 |
  | #2/#3/#4 | ★ **7,353（三次全同）** | ✓ | env / env / **overlay 交付件** |
  | #5 | 2,951 | ✗ | 回 native |
- ✅ **启动期校验是活的**：`$.mode expected "native" | "ptc" | "both" | "lean" but got "nonsense"`
- ✅ **preset 路线**：`--profile web --patch <探测> --dump-config` ⇒ 组合树出现 `preset-leanprobe` + `tool-presentation` + `mode: lean`
- ★★ **token 更正**：首次 lean **15,311** vs native **17,056** ⇒ **省 10.2%**（★ 我先前按**文件大小**排序把两行读反了；lean 的会话文件更大是因为目录文本被记进会话）
- ⚠ **未做**：真跑 web profile + lean preset 的完整回合（会拉起 Hindsight 并占端口）；团体混合模式的**真回合**端到端
- ✅ 副作用：我的 headless 启动**没有**拉起 Hindsight（8888 未监听）

## 九 · 第 9 轮：全量（731 工具）token 实测

★ **275,020 → 67,911 token ⇒ 省 75.3%（0.247×，约 4.05 倍）**，每题少 207,109 token。
（中位数 n=199\臂；native 275,011–278,126，lean(S) 67,907–71,539）

| 臂 | 中位 token | 相对 | 端到端 |
|---|---|---|---|
| A native | 275,020 | 1.000× | 95.0% |
| B 骨架+旧目录 | 86,211 | 0.313× | 41–62% |
| C 只有骨架 | 48,070 | 0.175× | ★ 9% ❌ |
| D 骨架+无参目录 | 75,566 | 0.275× | 7–10% ❌ |
| E ptc | 68,803 | 0.250× | 5.5% ❌ |
| F 纯文本索引 | 16,484 | 0.060× | 0% ❌ |
| **S lean 浅而准** | ★ **67,911** | ★ **0.247×** | ★ **89.9%** |

★★ 字节口径（shipped 装配路径，真实 731 schema）：通道 988 KB → 222 KB，加目录 149 KB = 372 KB，**字节比 0.376**。
★ **token 省得比字节多**（75.3% > 62.4%）—— 删掉的是标点密集的 JSON schema，它每字节最费 token。
★ 唯一"既省又能用"的是 S；C/F 更省但不可用。

## 十 · 第 10 轮：`lean-mode` 插件（零核心改动）—— 装上即生效

- ★★ **关键发现**：`system-prompt/assemble` 是**瀑布**（"返回的值是权威的" + "作用域监听器只收到该作用域的装配"）
  ⇒ ★ **插件可以改写 `assembly.tools` 与 `assembly.sections`，不用动 `dsh-tools`**
- ✅ 插件 `@local/dsh-lean-mode` **真装进 profile**（`dsh plugin --profile leanprobe add`）+ **真启动跑通**
  会话 #9/#10：**不带 --patch**，系统提示词 2,951 → **7,171**、目录段 ✓、参数信封 ✓、无 SDK 段 ✓
- ✅ 挂 preset：`preset-lean` 组合层已验证
- ★ **我自己修掉的两个插件 bug**：① 生成器变量 `BT` 被写进文件（import 失败）② 通道 `{...t}` 保留了完整 description ⇒ 与目录重复
- ★ 数字：731 工具字节比 **0.390**（核心补丁 0.376）、反推 token ≈ **73,000**（核心补丁实测 67,911）
- ★ **两条路并存**：A 核心补丁 + `mode: lean`（复用上游 `tool-presentation` 行）；B ★ 插件（零核心改动）
- ⚠ 限度：插件 token 数是**反推**；preset 挂载未真跑会话；插件不新增 `mode` 枚举（用它时 mode 保持 native）

## 十一 · 第 11 轮：preset 挂载补实（**未起 web，零副作用**）

- ★★ 新增测试走**真实挂载路径** `agentPresets.mount(agentCtx, id)`（= web 应用选 preset 的同一段代码）：
  `packages/preset/agent-preset-registry/tests/lean-mode-preset.spec.ts`
- ✅ 断言：挂插件的 preset 只让**它自己的** agent 变浅而准；兄弟 preset 不受影响；两边工具名相同
- ✅ registry 套件 **46\46 绿**；沙盒提交 `05a50ceb7e`
- ★ 我**没有**真起 web profile —— 找到了更直接的路径拿到同样证据，因此没拉 Hindsight、没占端口
- ⚠ 仍差：**UI 层**真选一次这个 preset（属上游既有行为）

## 十二 · 第 12 轮：真起 web profile + 界面选 preset（**负面结果**）

- ✅ 独立 profile `webprobe`（独立 DSH_HOME + 端口 3099）真起 web，**界面里**操作
- ✅ 界面 preset 菜单**出现「Lean 模式」**、选择器切过去、会话真跑完
- ★★ **对照：界面选 PTC 模式生效**（系统提示词 29,784、含 `run_code`）⇒ **上游 preset 切换没问题**
- ★★ **插件挂 profile 层在 web 下也生效**（10,703、含目录段）⇒ 插件本身没问题
- ★★★ **但把插件挂在 preset 里，界面选它 —— surface 不变**（2,902、无目录段）
  ★ 三种声明方式（包名 / file URL / 去掉 persona）**全部无效**
- ★ 排除：不是切换机制坏（PTC 好）、不是声明不可用（registry 报 usable、单元测试过）、不是插件在 web 下不行
- ★ **高置信假设（未最终定位）**：PTC 走 `presentAs`（**layer 机制**，后代作用域可解析）⇒ 生效；
  本插件走 `system-prompt/assemble`（**作用域事件派发**）⇒ 真实 agent 装配上没触发。
  ★★ 单元测试过而真机失败 ⇒ **测试的作用域构造与真实 agent 不完全一致**
- ★★ **结论**：preset 场景用 **A 路线**（核心补丁 + `mode: lean`，与 PTC 同族）；
  **插件只用于 profile 层**。★ **不要在 preset 里挂本插件。**
- ✅ 清理：3099 已停、浏览器标签已关、Hindsight 从未被拉起、生产零改动

## 十三 · 第 13 轮：B 路线（核心补丁 + `mode: lean`）界面验证

- ✅ **机制通了**：界面里选「Lean 模式」后，系统提示词里**出现了目录段**
  （`## Tool catalog ★ Each line gives the tool's TOP-LEVEL JSON argument shape…`）⇒ `presentAs` 在 preset 里生效
- ★ 该次**目录是空的**：我的测试 preset 只挂了 `persona` + `tool-presentation`，**一个工具插件都没挂** ⇒ agent 手里没工具 ⇒ 目录自然空
  ⇒ ★ **这是我测试 preset 的缺陷，不是功能问题**
- ⚠ 加上工具插件（tool-fs / tool-fs-search / tool-pwsh / tool-jobs / tool-skill）后，**该 preset 从界面菜单里消失了**
  （注册不上，日志无报错，**原因未查**）
- ★ **结论**：**B 路线的机制已验证可行**；但要交付"能日常选的 Lean 模式"，还差**"给 preset 正确配一套工具"**这一步
  （照官方 `极简模式` 的写法抄应可解）
- ✅ 清理：3099 已停、浏览器已收、Hindsight 未拉起、生产零改动

## 十四 · 第 14 轮：★ **Lean 模式做成并界面验证通过**

- ✅ **做法**：**照抄官方「标准模式」整份 `plugins` 清单** + 一行 `tool-presentation{mode: lean}`
- ✅ **界面实测**（真起 web，独立端口 3099）：界面选「Lean 模式」⇒ 会话 `bd00aebe`
  **系统提示词 10,885、目录段 ✓、参数信封 ✓、26 条目录行** ⇒ ★★ **功能验证通过**
- ★ **踩坑（已写入文档）**：
  ① 手写只挂几个工具的 preset ⇒ 激活失败、**界面直接看不到该模式**
     （诊断原话：`tool-fs: waiting for fs` / `tool-pwsh: waiting for shell, shellEnv` / `tool-jobs: waiting for jobs`）
  ② 补上工具仍失败 ⇒ **清单不完整**（缺 `skill-filesystem`/`command-goal` 等配套行）
  ⇒ **正解：整份照抄官方 preset，只加一行**
- ★ 交付件：**`deliver/lean-preset.patch.yml`**（= standard 全文 + 那一行）
- ✅ 清理：3099 已停、浏览器已收、Hindsight 未拉起、生产零改动

## 十五 · 第 15 轮：★★★ 打包成一个插件（装上生效 / 卸载失效 / 界面可选 / 零核心补丁）

- ★★ **做法**：bundle 的补丁同时插入 **插件行 + preset 声明**；插件注册**全局**装配监听器，
  用 `agentPresets.composedPreset(agent.ctx)`（`Agent.ctx` 为上游既有字段）问「这次装配是哪个 preset」，
  **是 lean 才变换**。
- ★★ **界面实测**（**只装 bundle、不带 --patch**）：
  | 界面选择 | 系统提示词 | 目录段 | 目录行 |
  |---|---|---|---|
  | ★ Lean 模式 | 10,703 | ★ ✓ | 26 |
  | 标准模式 | 6,163 | ✗ | 0 |
  ⇒ **门控正好工作**
- ★ **重要观察**：小工具集（26 个内建工具）上 lean **反而多花**（10,703 vs 6,163）；
  只有大工具集才省（731 个时 **0.247×**）
- ⚠ **限度**：插件只用上游 API ⇒ 原生 DSH 上应可用，但沙盒 harness 带补丁，此条为**推理非实测**
- ✅ 清理：3099 已停、浏览器已收、Hindsight 未拉起、生产零改动

## 十六 · 第 16 轮：工具占多少上下文（生产真实数据）

- 数据源：**生产会话记录**的 `request/header.tools` + `usage.inputTokens`（模型 space-bunny-free，n=19）
- ★ **生产标准模式现状**：**84 个工具** \ 工具 JSON **89 KB** \ 首轮 input **36,264** \ **工具占 ≈22,300（61.6%）**
- ★ **731 个工具**：native **≈275,000**（27.5% 窗口） vs **lean ≈68,000**（**6.8%**）
- ★ **同 84 个工具改 lean**：工具 ≈22,300 → **≈9,400**；首轮 input 36,264 → **≈23,400**
- ★★ **更正一处**：我曾说"小工具集 lean 反而多花"——**错**（拿系统提示词长度比，而 native 的工具在请求体里）。
  用真实 tools 数组重算：26 个工具时 lean 也省（21KB→13KB，≈0.45）
- ★ 规律：**量到的所有情形 lean 都省**，工具越多省得越多（26≈0.45 · 84≈0.42 · 731=**0.247**）

## 十七 · 第 17 轮：★ `dsh-lean-mode` 已发布到 GitHub

- ★★ **仓库**：https://github.com/q862877400-ux/dsh-lean-mode （**PUBLIC** · MIT · topics: dsh / deepseek-harness / plugin / agent-tools / context-window）
- ★ **双语首页**：`README.md`（English）+ `README.zh.md`（中文），互相有语言切换链接
- ★ **许可合规**：DSH 为 **MIT**（Copyright (c) 2026 DeepSeek）；`cordis.patch.yml` 复述了官方 `standard` preset 组成
  ⇒ `LICENSE` 同时列两家版权、`THIRD-PARTY.md` 写明**改了哪几处**并声明**非官方背书**
- 文件：`.gitignore LICENSE README.md README.zh.md THIRD-PARTY.md cordis.patch.yml index.mjs package.json`
- ★ **未做**：`awesome-dsh-plugin` 精选列表的收录 —— 那是**有 data/ + 生成脚本**的项目，
  要按 `contributing.md` 加条目并**给上游提 PR**，属另一件事（等业主点头）

## 十八 · 第 18 轮：★★★ 从 GitHub 安装 —— 沙盒端到端验证通过

- ✅ `dsh plugin --profile webprobe remove '@local/dsh-lean-mode'` 卸掉本地链接版
- ✅ `dsh plugin --profile webprobe add github:q862877400-ux/dsh-lean-mode`
  ⇒ `+ @local/dsh-lean-mode github:q862877400-ux/dsh-lean-mode`（pnpm 3.5 s 拉下来）
- ✅ `--dump-config`：插件行（`presets: [lean]`）与 `preset-lean` 声明**都从 GitHub 那份组合出来**
- ✅ ★★ **真启动 + 界面选「Lean 模式」**：会话 `6784794d` —— 系统提示词 **10,703**、**目录段 ✓**、**参数信封 ✓（26 行）**
- ✅ 首页双语都补上了 GitHub 安装命令并推送
- ✅ 清理：3099 已停、浏览器已收、Hindsight 未拉起、生产零改动

## 十九 · 第 19 轮：★★★ 已装进**生产环境**（从 GitHub）

**命令**（用生产自己的启动参数，`DSH_HOME` 默认）：
```
cd D:\AI\DSH\deepseek-harness\apps\cli\src
node --import tsx\esm <bin.ts> plugin --profile web add -w github:q862877400-ux/dsh-lean-mode
```
★ **必须加 `-w`**：生产 profile 是多包 workspace（`packages: ['.', 'harness/apps/*', …]`），
不加会被 pnpm 以 `ERR_PNPM_ADDING_TO_ROOT` 拒绝（沙盒那份只有 `packages: ['.']` 所以不加也行）。

**结果**：
- ✅ `package.json` 写入 `"@local/dsh-lean-mode": "github:q862877400-ux/dsh-lean-mode"`（依赖 + 插件清单两处）
- ✅ `--dump-config`：`lean-mode`（`presets: [lean]`）与 `preset-lean` **都在组合树里**
- ✅ ★ `cordis.patch.yml` **一个字没变**（DSH 把 bundle 补丁记在 `.plugin-manager/`，不污染 profile）
- ★ 那堆 peerDependencies warning 是**你原有插件**的，不是本插件的（本包无 peerDeps）

**备份**（按你 home 惯例命名，都在 `profiles\web\`）：
`cordis.patch.yml` / `package.json` / `pnpm-lock.yaml` → `*.bak-20261006154125-before-lean-mode`

**回滚**：
```
node --import tsx\esm <bin.ts> plugin --profile web remove '@local/dsh-lean-mode'
```
（必要时再用那三个 `.bak-…-before-lean-mode` 覆盖回去）

**用法**：★ **开一个新会话** ⇒ 模式菜单里选「Lean 模式」。
DSH 自己的说明：「**已存在的会话沿用它们启动时的插件版本；改完的行为请在新会话里验证**」。

## 二十 · 第 20 轮：排查 `tool input is invalid JSON`（**与本插件无关**）

**现象**：`D:\AI\work space\zcode` 的会话 `c71573df` 第 4 步崩，`MALFORMED_RESPONSE`。

**排查步骤与证据**：
1. ★ 该会话 `agentPreset = "standard"` ⇒ **本插件只在 `lean` 模式动作，对它是完全惰性的** ✓（先自证清白）
2. 跨 9 个最近会话搜该错误串：**只有这 1 次是真错误**（另 3 个"命中"是本会话自己的文字与 Hindsight 配置文档）
3. 报错出处：`llm-deepseek\src\translate.ts:155`
   ```ts
   if (reason.kind !== 'max-tokens') {          // ★ 故意容忍截断；其它一律判错
     try { parsed = JSON.parse(content.arguments) }
     catch { return malformed('tool input is invalid JSON') }
   }
   ```
4. ★★ **根因**：模型在 `ask_user_question` 的参数里写了**未转义的 ASCII 双引号**
   —— 它想表达中文引号，却打出 `"`，于是整段 `arguments` **不是合法 JSON**
   （原文：`并且说"第二种能不能单独跑"还没确认`）
5. ★ `assistant/attempt` 只出现 **1 次** ⇒ **DSH 没有自动重试**，该轮直接终止

**结论**：**模型输出缺陷**（不是插件、不是工具面、不是 standard 模式的错）。
**建议**：① 重发/继续即可（随机性失误）；② 少让它把**带引号的长段中文**塞进工具参数（那正是模型滑倒的地方）；
③ 若频繁复现，可考虑给 DSH 提一条「MALFORMED_RESPONSE 自动重试一次」的改进。

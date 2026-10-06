# 规格 208 · Lean 工具面（把 PTC 式加载嫁接到**原生**模式，量出「准确率 × token」的取舍）

> **读法**：本文件定判据（SC）与决策（D）；`plan.md` 定顺序、依赖、写盘边界；
> `tasks.md` 是逐任务 checklist；`goal-bar.md` 是唯一进度字段。
> ★ 不含行号。★ 每个数带口径。

## 一 · 为什么有这条规格（★ 前一轮的结论与它留下的缺口，逐字记下来）

1. **业主的目标（逐字）**：让**标准模式**的工作流能「**便宜又准确**地从上百个 MCP 工具里跳出需要用的」，
   而且**在此之前 agent 也要知道自己可以用某个工具解决某个问题** —— 不要「注意力飘逸之后几百个工具只用几个记得住的，遇到能用冷门工具解决的问题也强行用常用工具硬干」。
2. **旧研究（`specs/207-agent-team-tool-routing`）量到过这个病**：冷门臂 `NONE` 在 W=414 仍有 **40%**；
   冷门域 `p_can_do` **20.0%** vs 常见域 **55.6%**；且**冷门任务的弃权率更低** ⇒
   ★★ **模型在冷门任务上不弃权，而是挑个错的（邻近热门工具）**。
3. **旧研究也量到过「压缩会崩」**：把工具压成「名字 + 一句用途」的极简索引（8.5× 便宜），
   准确率 **79.2% → 22.9%**；结论逐字是「**要分清它们必须看到【参数】**」。
4. ★★★ **本轮新增的关键事实（已实测，见 §三 SC-5）**：同一批 478 个工具，
   `native` JSON schema = **693,094 B ≈ 175,106 token**；PTC SDK 声明 = **253,855 B ≈ 64,135 token（0.37×）**；
   而**字节主要住在 `parameters`（469 KB / 68%）** ⇒ ★ **贵的不是英文散文，是 JSON Schema 的语法本身**
   （去掉全部参数描述只省 23%）。
   ⇒ ★★ **正解不是「删描述」，是「换表示」** —— 这也正是 PTC 加载便宜的真因。
5. **DSH 自己的设计说明把本规格要做的事列为「推迟」**（`.agents/notes/implemented/feature/2026-06-15-ptc.zh.md` 的
   「曾考虑的替代方案」，逐字）：
   > **每工具可见性分层（此工具 native，彼工具 ptc-only）。** 推迟：它需要每工具元数据和
   > `'native' | 'ptc' | 'both'` **不提供的呈现拆分**，且其设计**取决于模型在 `'both'` 下如何分配使用的证据**。
   ⇒ ★★★ **本规格就是去产那份「证据」**；而它缺的「呈现拆分」正是本规格要加的 `mode: 'lean'`。
6. **一处必须改的硬话**（`packages/core/tools/src/ts-types.ts` 的 SDK 提示词，逐字）：
   > A declaration does not make its name a directly callable tool; **only names supplied as separate tool schemas may be called directly.**
   ⇒ ★ 所以「只给声明、不给 schema、还要能直接调用」**不能靠配置拼出来**，必须**改这段措辞 + 新增呈现分支**。

## 二 · User Scenarios

- **US-1**：作为业主，我要看到「同一个工具集，换表示方式」之后**准确率与 token 各是多少**的对照表，
  因为我要据此决定生产配置该用哪一种。
- **US-2**：作为业主，我要 agent **知道长尾工具存在**（不是只记得住常用的那几个），
  因为冷门任务硬用常用工具硬干是我实际付代价的地方。
- **US-3**：作为接手的人，我要能**只跑一条命令**复现每个数（含 token 与准确率）。
- **US-4**：作为生产环境的维护者，我要**确信这一轮一个字节都没碰生产实例**。

## 三 · 判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| **SC-1** | ★★ **生产零污染**：全程只写 `D:\AI\DSH-sandbox\**` | 开工前取生产两条指纹（`D:\AI\DSH\deepseek-harness` 的 `git rev-parse HEAD`+`status --porcelain` 计数；`C:\Users\Zegel\.dsh` 下 `profiles\web` 与 `settings` 的 mtime\hash），收工再取一次，两次逐字相同 |
| **SC-2** | `mode: 'lean'` **在沙盒 harness 落地**，且 11 个站点全部处理 | 站点清单见 `plan.md` §二；`--dump-config` 能组合出该模式；未知模式字面量**必须**被 schema 拒绝（负例） |
| **SC-3** | ★★ lean 的**呈现**可核对：tools 通道里是**骨架 schema**，系统提示词里是**N 条签名目录**（N = 可见工具数） | 一次 lean 会话的 `header.tools` 与系统提示词段落落盘成 `output/lean-surface.json`；断言「每个工具的参数只有 name\type\required、无 description」+「目录条数 == 工具数」 |
| **SC-4** | ★★ lean **不依赖 PTC runtime** | 配置里**不挂** `ptc-runtime-node` 时 lean 仍能 boot；★ 负例：同一配置切成 `ptc` 必须报 `requires a PTC runtime`（证明这条判据不是在空转） |
| **SC-5** | ★ token **实测**（不是字符估算）：每个条件给出真实 `toolsTokens` | 取自会话记录／`session_projcache` 的 `toolsTokens`；★ 与「按 3.96 字符\token 估算」的数**并列报**，并写明两者差 |
| **SC-6** | **真工具目录**落盘：`output\catalog-all.json`，N ≥ 500，每个工具带 `name\description\parameters\source` | `source` 必填（哪个 preset\哪个 MCP server\内建），用来核「凡本机能装的全要」 |
| **SC-7** | **5 条件对照**跑完并落盘 `output\conditions.json` | 条件固定为 `native-full\lean\lean+catalog\index\ptc`（一次定义死，D-6） |
| **SC-8** | ★★ 准确率判据 = **「选到的工具能不能干活」**，由 **Lead 自己判**，逐条留记录 | `output\judgments.json`：每条 `{task\condition\picked\can_do\why}`；★ 可复核 |
| **SC-9** | ★★ **方法学自检**：`index` 条件必须**复现出低分**（旧研究 22.9%） | 若 `index` 分数不低 ⇒ ★ **说明题源或判据与旧研究不可比**，必须写进限度而不是当结论 |
| **SC-10** | 报告含**限度**段，明写 n、子样本、呈现等价性 | `docs\recon\lean-tool-surface.md`（或本规格目录下） |
| **SC-11** | 每批落盘 + 提交，只 add 自己这一线 | `tools\commit_mine.py`（事实 555：链完不许直接 commit） |
| **SC-12** | ★ 走**真 DSH**，补上旧研究第 6\7 条限度（那次测的是提示词里的文本清单，不是真工具面） | 每个条件的工具面都从会话 `header.tools` 取，不从文本清单构造 |

## 四 · 决策（D）

| # | 决策 | 理由 |
|---|---|---|
| **D-1** | ★★★ **只动沙盒**（`D:\AI\DSH-sandbox\`）；**生产实例与 `C:\Users\Zegel\.dsh` 一个字节都不碰** | 业主明令：「不要改生产环境，多轮调整最后效果完美了再上生产」 |
| **D-2** | 嫁接形态 = **原生调用 + 紧凑签名目录 + 可调用骨架 schema**；**不是** `both` 的并集 | 并集付两份；且 `both` 的 SDK 文本逐字说「声明不可直接调用」，与目标冲突 |
| **D-3** | 清空 `run_code` 注入、`collapses` 对该模式恒 `false` | 目标是**脱离 code loop** 仍成立（业主对 Q1 的担心）；若依赖 code 就测不出「加载方式本身」的贡献 |
| **D-4** | 题源**优先复用** 207 的 145 项用户功能；不足再自写 | 可复用已验证的题源；且便于与旧数对照 |
| **D-5** | 5 条件**一次定义死**，不中途加 | 加条件会让「同一批任务重复测量」的配对性失效 |
| **D-6** | 判据用「能不能干活」而**不是**「名字逐字相等」 | 业主裁定；且旧研究已证 `p_strict` 与 `p_can_do` 不是一回事（不许互推） |
| **D-7** | 我在沙盒里改 DSH 源码；**构建产物与源码同改** | `dsh` 以 tsx 直跑源码（`node --import tsx\esm apps\cli\src\bin.ts`）⇒ 改完重启即生效，省一次构建 |
| **D-8** | ★★★ **批量一律用 `opencode-zen` \ `space-bunny-free`**；**严禁**用 deepseek 跑批量或子代理 | **业主 2026-10-05 逐字**：「测试用的子代理或者沙盒里的代理要用 bunny 模型，千万别用 deepseek，太贵了」。★ 本规格第 1 轮**已违过一次**（174 次 ≈ $1.4）⇒ 写成硬决策 |
| **D-9** | ★★★ **主判据改成「端到端可执行性」**：发出的工具名在目录内 **且** 实参通过真实 schema 的必填+类型校验（**客观机器判**，不经人工裁判） | ★★ 业主 2026-10-05 判「你所有结果都大差不差，我觉得是你测试方法不对」⇒ **成立**：原判据只看「选了谁」，而各呈现方式给的工具名一样 ⇒ 注定打平；换尺子后端到端从 95%（全量）到 1.7%（我的骨架），排名整个翻转 |
| **D-10** | ★★★ **`lean` 的通道改成「浅而准」**：保留真实顶层 keys\required\类型，只剥内层描述与深嵌套 | 探针实测：**0.220×** 成本、**95.0%** 端到端；而原「无信息骨架」同为 0.171× 却只有 **1.7%** ⇒ ★ 那 5 个点成本是本轮最值钱的 5 个点 |
| **D-11** | ★★★ **「按 preset 分别选呈现方式」上游本来就有**，不需要新造机制 | 仓库里已有 `packages/core/agent-tool-presentation`（preset 用来声明呈现方式的那一行）+ `tools.presentAs()`（按**作用域**记 mode）。★ 我前两轮误判为「做不到/要塞进 preset」——**都错**：skill 明写 tools 是宿主平面服务搬不进 preset，而**呈现方式可以** |
| **D-12** | 该行补两个缺口：**① 接受 `lean`**（zod 联合原本只有 native/ptc/both）**② `lean` 走立即路径**（原本非 native 一律等 `ctx.ptcRuntime`，而 lean 按设计不需要运行时 ⇒ 会永久 pending） | ★ 另修一处真 bug：`presentAs` 只注册了 SDK 段，**漏了 catalog 段**，而段的选择原先按**部署默认**决定 ⇒ native 默认部署下的 lean preset **拿不到目录段**（测试抓到的） |

## 五 · Acceptance Scenarios

- **AS-1**（SC-1）：收工跑 `tools\assert_prod_untouched.py` ⇒ 报「生产两条指纹与开工逐字相同」。
- **AS-2**（SC-2 + SC-4）：沙盒里 `--dump-config`（lean）成功；同一配置切 `ptc` 报缺 runtime。
- **AS-3**（SC-3 + SC-5）：跑一次 lean 会话 ⇒ 落下 surface 与 `toolsTokens`。
- **AS-4**（SC-6 + SC-7 + SC-8 + SC-9）：跑对照 ⇒ 出 `conditions.json` + `judgments.json` + 报告。

## 六 · 不做 + 原因

| 不做 | 原因 |
|---|---|
| 改生产实例 / 生产 `DSH_HOME` | D-1（业主明令） |
| 做「日常可用的 preset」与生产补丁 | ★ **只在业主判「合格」之后**才做（目标 ⑤） |
| 改 `D:\AI\SW` 的 `capabilities.yaml\scripts\tests\tools`\门禁 | 那是另一条线；本规格只在 `specs\208-*\` 与 `output\` 落盘 |
| 把 `p_strict` 当 `p_can_do` 用 | 旧研究 §4.3 逐字点名 |
| 只跑一轮就下结论 | 业主明说「多轮调整」 |

# CADAM

<!-- survey: class=B; repr=code; orchestration=loop; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/Adam-CAD/CADAM （产品主页 https://adam.new/cadam ；在线试用同址，`README.md:36-38`） |
| 许可 | **GPL-3.0**（读克隆内 `LICENSE` 原文首行「GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007」，全文 185 行）；README 自述是 **GPLv3 合成作品**——部分代码派生自 `openscad-web-gui`（GPLv3），并随发行携带 OpenSCAD WASM 未改二进制（GPL-2.0-or-later，`README.md:283-292`）；`src/vendor/openscad-wasm/SOURCE-OFFER.txt` 记版权方为 Adam AI Labs, Inc. → **只读思想**（不抄代码、不抄提示词文本） |
| 元数据 | stars 5319 · forks 656 · 最近推送 2026-10-15T05:26:14Z · 语言 TypeScript（来源：https://api.github.com/repos/Adam-CAD/CADAM ，取数日 2026-10-24） |
| 克隆 | D:\ai3d-survey\repos\Adam-CAD__CADAM （HEAD `e339e3a`，末次提交 2026-10-14 22:26 -0700，工作树干净） |
| 证据等级 | 读码 |

## 1. 一句话定位

**浏览器内的 text-to-CAD 应用**：模型（LLM）输出一整份 OpenSCAD 脚本 → 浏览器用 WASM 编出 STL/OFF → 客户端把 ISO/FRONT/BACK/LEFT/RIGHT/TOP/BOTTOM 七视角渲成一张拼图回灌给模型 → 模型**自己看这张图**决定要不要重写，循环到「每个视角都像话」才收工；尺寸参数另抽成表，滑动条改参数靠本地重编译、不必再调模型（`aiChat.ts:212-368`、`ChatSession.tsx:458-527`、`openSCAD.ts:164-187`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：对话消息（可带图片）+ 可选 STL 附件——带附件时系统提示要求必须 `import("filename.stl")` 在原模型上做加/减，不许重画（`aiChat.ts:315-326`）。请求体故意极小：只有 `conversationId`/`model`/`thinking`，分支状态由客户端先落库（`aiChat.ts:400-404`、`aiChat.ts:382-399`）。
2. **中间表示**：**完整 OpenSCAD 源码**（工具入参 `code: z.string().min(20)`，`shared/chatAi.ts:25-29`）+ 从 Customizer 注释正则解析出的参数表（`parseParameter.ts:8-16`）。没有特征树、没有 B-rep。
3. **生成**：工具面只有 `build_parametric_model`（整份重写，不做增量 patch）与 `answer_user`（`shared/chatAi.ts:47-60`）；另有 creative 分支的 `create_mesh`（`shared/chatAi.ts:61-68`、`aiChat.ts:880-882`）。提示词把「该怎么写」写成硬规则：参数字面量置顶 + 全称 snake_case + Customizer 注释语法、颜色作为参数且命名 `*_color`、螺纹/紧固件/曲面必须改派 BOSL2 而不是手搓（`aiChat.ts:291-313`、`aiChat.ts:268-289`）。
4. **编排**：服务端 route 里跑 `streamText`；参数化会话**首步强制 `tool_choice` 锁定 build 工具**（`aiChat.ts:1308-1342`），步数上限 60、输出上限 64000 token（`aiChat.ts:1343`、`aiChat.ts:428`）；creative 分支上限 5 步（`aiChat.ts:1343`）。
5. **执行**：**在浏览器里**编译——模块单例 Web Worker 装载随仓库一起来的 OpenSCAD WASM，一次渲染同时产 STL 与 OFF（OFF 保留 `color()` 的逐面颜色），并启用 `manifold`/`fast-csg`/`lazy-union`（`toolWorker.ts:1-16`、`openSCAD.ts:195-247`、`openSCAD.ts:180-187`）。
6. **验证**：**编译成功不等于可交付**。客户端把 7 视角用正交相机渲成 3×3 拼图（每格 512 px、带视角标签）上传（`meshUtils.ts:161-169`、`meshUtils.ts:278-325`、`meshUtils.ts:199-211`），服务端再把这张图当作 `image-data` 塞回工具结果（`aiChat.ts:979-1018`）；提示词给出明确的判据清单（「缺失/错位/断开/不可打印/太简单/被遮住/看不清楚」→ 重写）与逐类物体的必含特征（`aiChat.ts:225-253`）。编译失败走 `output-error` 并**自动继续**（`ChatSession.tsx:409-445`）。
7. **交付**：`STL` / `SCAD` / `DXF` 三选一（`ParameterSection.tsx:50`、`README.md:65`），**没有 STEP**；下载路径会过一遍网格修复与「可打印」预检（`DownloadMenu.tsx:106`、`DownloadMenu.tsx:456`、`meshPrintProcessUtils.ts:42-91`）。

## 3. 技术方案要点（可迁移的机制）

- **把「验」做成一张固定拼图**：视角列表是常量（7 个方向）、相机是正交、背景/光照/HDR 环境固定，所以跨模型可比（`meshUtils.ts:161-169`、`meshUtils.ts:213-228`）。
- **判据写进提示词、逐条可对照**：不是「看着不错就停」，而是列出每类物体必须有的特征（手机壳→空腔/包边/摄像头孔/充电口/按键孔/壁厚；杯子→杯体/内腔/杯口/底/把手/壁厚）（`aiChat.ts:248-253`）。
- **强制首个动作就是建模**：首步 `activeTools` 收窄成只留 build，并在模型支持时钉死 `toolChoice`；不支持强制工具调用的模型降级为纯提示词驱动，并**专门记账这种降级**（`aiChat.ts:1285-1300`、`aiChat.ts:1308-1342`）。
- **反「假交付」条款**：没调用 build 工具就不许说「我做了/改好了」（`aiChat.ts:216`）；工具入参就是给用户看的产物，不许把 OpenSCAD 贴进正文（`aiChat.ts:214`、`aiChat.ts:220-223`）。
- **证据缺失时降级而不阻塞**：拼图上传失败就退回纯文本并如实告诉模型「图没附上」，循环继续（`aiChat.ts:988-1017`、`ChatSession.tsx:524-526`）。
- **参数化与 AI 解耦**：`-D name=value` 覆盖 + 本地重编译，改尺寸不花推理费（`openSCAD.ts:164-178`、`openSCAD.ts:198-215`）。
- **参数面板靠源文本约定生成**：`// [10:1:200]` / `// [round, square, hex]` / 布尔→开关 / 字符串后的数字当 maxLength / `/* [Group] */` 分组（`parseParameter.ts:89-129`、`aiChat.ts:298-305`）。
- **工具执行脱离 UI 生命周期**：工具用的是模块级单例 worker（按 requestId 路由），避免用户切会话导致 worker 被 `terminate()` 把在飞的构建判死（`toolWorker.ts:1-16`）。
- **构建产物持久化按 toolCallId 命名**：拼图路径由 `toolCallId` 推导，服务端同一套推导去取图（`ChatSession.tsx:473`、`aiChat.ts:1117-1118`）。
- **高风险动作改派给库**：螺纹/齿轮/有机曲面必须走 BOSL2 的 `screws.scad`/`threading.scad`/`skin.scad`/`beziers.scad`，并规定 `$fn` 下限（`aiChat.ts:268-289`）。

## 4. 运行条件与依赖

- Node `^20.19.0 || >=22.12.0`、npm `>=10`（`package.json:6-9`）；本机实测 Node v26.7.0 / npm 11.19.0，满足。
- 前端：React 19 + TanStack Start/Router + Vite + three.js/R3F（`package.json:19-`、`README.md:257-266`）。
- 后端：TanStack Start 的 server route（`src/server/aiChat.ts`）+ Supabase（Auth/Postgres/Storage，`supabase/schemas/*.sql`、`supabase/migrations/*.sql`）。
- AI：至少一家 key——`ANTHROPIC_API_KEY`/`OPENROUTER_API_KEY`/`OPENAI_API_KEY`/`GOOGLE_API_KEY`，另有 `FAL_KEY` 供 creative 分支（`.env.local.template:16-20`）。
- 计费：默认走外部 `BILLING_SERVICE_URL`/`_KEY`，缺失时聊天会被 503 拦住（`billingClient.ts:177-178`、`aiChat.ts:1088-1110`）；**`ENVIRONMENT=local` 时计费被旁路**（`billingClient.ts:81`）——这是本地能跑起来的开关。
- 本地栈：`npx supabase start`（需 Docker；本机实测 Docker 29.8.0 可用）+ `npm run dev`（`README.md:161-177`）；ngrok 只在 webhook/签名 URL 场景需要（`README.md:214-241`）。
- CAD 内核不用装：OpenSCAD 编成 WASM 随仓库带（`src/vendor/openscad-wasm/openscad.wasm`，实测 9,603,115 字节；`vite.config.ts:12-41` 在 dev 下直接吐这个文件），BOSL/BOSL2/MCAD 以 zip 放在 `public/libraries/`。
- 本机（Windows / Python 3.14.7 / RTX 4080S）判断：**理论上能跑**（Node 满足、Docker 在、Python 不参与），但代价是要起 Supabase 本地栈 + 至少一把 AI key；本次未安装未启动，故本卡不主张任何运行结论（起栈步骤见 `README.md:161-177`）。GPU 非必需，渲染是浏览器 WebGL（three）。

## 5. 失败模式与已知坑

- **视觉验收是模型自评，不是确定性判据**：脚本只保证「编译过 + 图传上去了」，「像不像」由模型看图判断（`aiChat.ts:225-253`、`aiChat.ts:998-1001`）；同一条提示词对弱模型可能一路放行。
- **图丢了循环就瞎了**：上传失败时只回纯文本（`aiChat.ts:988-1017`），而提示词仍要求「逐视角比对」——此时循环退化成盲改。
- **参数解析器是正则且有截断**：只解析第一个 `module`/`function` 之前的行；若某个值不是字面量（是表达式），从该参数起**后面全部放弃**（`parseParameter.ts:9-16`、`parseParameter.ts:77-81`，作者自留 TODO「改用 AST」）⇒ 模型写 `w = base*2;` 会让面板大面积失灵。
- **循环成本只由步数兜底**：60 步 × 64000 输出 token（`aiChat.ts:428`、`aiChat.ts:1343`），没有「图看起来没变化就别再试」的收敛判据。
- **私有 vendored WASM 有版本耦合**：注释自述多输出（`-o /out.stl` + `-o /out.off`）只有 2025.03.25 playground 版支持，换旧版本会坏（`openSCAD.ts:217-235`）。
- **测试没有跑法**：仓库里有 5 个 `*.test.ts`（`shared/parametricParts.test.ts`、`shared/suggestions.test.ts`、`src/server/chatToolPersistence.test.ts`、`src/server/modelCapabilities.test.ts`、`src/components/chat/stuckToolRecovery.test.ts`），但 `package.json:10-18` 的 scripts 里没有 `test`，devDependencies 里也没有 vitest/jest ⇒ 不能一键跑，只能当「作者写了断言」的旁证。
- **产品耦合了整套外部服务**：Supabase Auth/RLS/Storage + 外部计费 + 多家 AI 供应商；剥掉这些之后剩下的只有「WASM 编译 + 七视角渲染」两块可独立复用（`aiChat.ts:1088-1110`、`.env.local.template:1-30`）。
- **单文件体量**：`src/server/aiChat.ts` 1726 行、`src/components/chat/ChatSession.tsx` 1039 行（实测 `(Get-Content).Count`），搬运时只能按段读。

## 6. 对我方目标的可用处（机制层面）

- **「给模型一张固定规格的证据图」** 是我们最该抄的一条：视角常量 + 正交相机 + 统一光照，等于把「视觉验收」变成可重复的观测协议（`meshUtils.ts:161-169`、`meshUtils.ts:199-211`）。搬到 SolidWorks 就是：固定 7 个视图 + 特征树截图 + 质量特性表，拼成一页回灌。
- **判据清单化**：`手机壳→空腔/包边/摄像头孔/充电口/按键孔/壁厚` 这种「逐类物体必含特征」正是我们要求的「可 grep 验收判据」的提示词版（`aiChat.ts:248-253`）。
- **强制首个动作 + 禁止未调用就说完成** 是治「普通模型只回文字不干活」的现成手段（`aiChat.ts:216`、`aiChat.ts:1308-1342`）。
- **参数化与推理解耦**：先抽出参数表，改值走本地重算（`openSCAD.ts:164-178`）——对应我们 SW 侧的「改尺寸重算而不是重问模型」。
- **「高风险几何改派给库」**：螺纹/齿轮/有机曲面不许手搓（`aiChat.ts:268-289`），等价于我们的「标准件走规范件库/标准件库，不手搭」。
- **工具执行不许被 UI 生命周期打断**（`toolWorker.ts:1-16`）——我们的长构建/COM 调用同样需要与界面解耦的执行体。
- **反面教材**：它的「可打印性检查」是事后修网格（`meshPrintProcessUtils.ts:187-266`、`meshPrintProcessUtils.ts:473-514`），在 CAD 目标里这会掩盖设计错误；我们要的是事前参数/特征门禁，不是事后补面。

## 7. 许可与红线

- **GPLv3 合成作品**（`LICENSE` 首行 + `README.md:283-292`）：只读思想。**连提示词文本也不能抄**——`PARAMETRIC_AGENT_PROMPT`（`aiChat.ts:212-368`）是受版权保护的源代码文本，只能吸收其机制（视角门禁、判据清单、强制首步），不复制文字。
- 随仓库携带的 OpenSCAD WASM 是 GPL-2.0-or-later 未改二进制，源码地址与 offer 写在 `src/vendor/openscad-wasm/SOURCE-OFFER.txt`；`public/libraries/` 下 BOSL/BOSL2/MCAD 各自另有许可。
- 本次对克隆只读，未改任何文件。

## 8. 证据清单

```
D:\ai3d-survey\repos\Adam-CAD__CADAM\LICENSE:1 · README.md:36-38,40-46,63-65,161-177,179-183,185-213,214-241,257-266,283-292
...\package.json:6-9,10-18 · .env.local.template:1-30 · vite.config.ts:12-41
...\src\server\aiChat.ts:212-368,382-404,428,880-882,979-1018,1024-1035,1088-1119,1285-1300,1308-1343
...\src\server\billingClient.ts:81,177-178 · src\server\parseParameter.ts:8-16,77-81,89-129
...\src\components\chat\ChatSession.tsx:229,409-445,458-527
...\src\components\parameter\ParameterSection.tsx:50,142-180
...\src\utils\meshUtils.ts:161-169,199-211,213-228,230-249,278-325,414-467
...\src\utils\meshPrintProcessUtils.ts:42-91,187-266,470-514,948-996
...\src\worker\openSCAD.ts:164-187,195-247 · src\worker\toolWorker.ts:1-16,29-40
...\src\vendor\openscad-wasm\SOURCE-OFFER.txt · src\components\viewer\DownloadMenu.tsx:106,456
...\shared\chatAi.ts:25-29,47-68 · benchmarks\README.md
```
- 元数据来源：https://api.github.com/repos/Adam-CAD/CADAM （取数 2026-10-24）。
- 计数实测（在克隆内跑 `Get-ChildItem` / `(Get-Content).Count`）：`src/` 顶层 21 个条目（15 个目录 + 6 个文件）；`*.test.ts` 共 5 个；`benchmarks/` 下 13 组 `.scad`+`.md`+`.gif`（来源：`benchmarks/README.md`）；`src/vendor/openscad-wasm/openscad.wasm` 9,603,115 字节。
- `benchmarks/` 的 13 份 `.scad` 是作者自述的「一句话出的模型」存档，未独立复现（见 §9）。

## 9. 未确认事项

- 未安装、未启动、未跑任何构建（本卡等级 `读码`）；「能跑」仅是按 `package.json:6-9`、`README.md:161-177`、`.env.local.template` 与实测本机 Node/Docker 版本做的条件判断。
- 提示词里点名的模型与价格表按代码现状记录（`aiChat.ts:100-198`），未核这些模型 ID 在供应商侧是否仍可用。
- `benchmarks/` 的 13 组结果（含 V8、涡扇、行星齿轮）是真机还是挑选后产物 **未确认**，未复现。
- 5 个 `*.test.ts` 的断言内容未读，只核了「没有可执行入口」（`package.json:10-18`）。
- `supabase/migrations/` 与 `supabase/schemas/` 只看了文件清单，未读 SQL；RLS 与存储策略的实际有效性未验。
- creative 分支（`create_mesh` + `falWebhook.ts` + 图片/纹理回流）未细读，本卡只覆盖 parametric 主路径。
- 视觉门禁对**普通模型**（非顶级 Claude/Gemini）的实际效果未做端到端实验——这是本卡最关键的未确认项。

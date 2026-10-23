# mcp-for-blender（原名 blender-mcp）

<!-- survey: class=H; repr=code; orchestration=loop; verify=visual; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/ahujasid/mcp-for-blender （`git remote -v` 实测同址；`pyproject.toml` 的 `[project.urls]` Homepage 仍指旧名 `github.com/ahujasid/blender-mcp`）|
| 许可 | MIT；版权行 `Copyright (c) 2025 Siddharth Ahuja`（`LICENSE:3`），`pyproject.toml` 亦写 `license = "MIT"` → **可借鉴**（可读、可抄、可商用，保留版权声明）|
| 元数据 | 32120 stars · 最近推送 2026-10-20T14:06:32Z · Python（来源：`gh api repos/ahujasid/mcp-for-blender`，取数 **2026-10-24**）|
| 克隆 | D:\ai3d-survey\repos\ahujasid__mcp-for-blender |
| 证据等级 | 读码（未装包、未启 Blender、未调用任何工具；计数取自静态扫描，并以仓库自带断言测试交叉核对）|

## 1. 一句话定位

★ **工具面「反向收敛」的样本**：不把 Blender 的每个操作做成一个 MCP 工具，而是只留 **9 个面向模型的工具**，把逐操作能力交给「模型自己写 bpy Python」（`execute_blender_code`）+「看图复核」（`look`）——**与「529 个细粒度工具」相反的做法**。（来源：`server.py:449` 起的 14 个 `@mcp.tool`；模型可见 9 个见 `tests/test_consolidated_tools.py:10-18`）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- **输入**：自然语言需求由客户端模型接收；服务端对外只有 9 个工具（`README.md:649`「as nine tools」），没有 per-operation 建模接口。
- **中间表示**：**Python 源码本身**。另外三件观测能力不是新命令，而是**预写好的脚本体**，用 `ARGS` 注入参数、`print` 一行标记 + JSON 回传：`RESULT_MARKER = "__MCP_RESULT__"`（`src/blender_mcp/blender_scripts.py:12`），`build()` 把脚本体包进 `_main()` 并注入 `ARGS`（`blender_scripts.py:15-28`），`parse_result()` 倒序找最后一行标记（`blender_scripts.py:31-35`）。设计理由写在文件头：用 `execute_code` 搭观测工具，「所有已装 addon 都能用，只有本包需要升级」（`blender_scripts.py:1-8`）。
- **生成**：模型自己写 bpy 代码，经 `execute_blender_code` 送进用户正在运行的 Blender（`src/blender_mcp/server.py:789-791`）。可选开启 AST 校验（默认关），见 §3。
- **编排**：**没有编排框架**，编排写在**服务端指令**里——`SERVER_INSTRUCTIONS`（`server.py:329-351`）规定开工顺序（先 `get_addon_status`、`get_scene_info`）、禁用硬编码枚举（"Never hardcode enum identifiers; read them"）、按类型而非名字找 shader 节点（"names are localized"）、以及 `look` 是"how you see your work; use it as much as you need"（`server.py:344-345`）。循环由模型自己走：改 → `look` → 改。
- **执行**：TCP socket + JSON，默认 `localhost:9876`（`server.py:57-58`）；命令形如 `{"type":…, "params":…}`、回应 `{"status":…, "result"|"message":…}`（`README.md:815-818`）。addon 侧**不是**同步执行，而是把命令入队，由注册在 bpy timer 上的 `_drain_command_queue` 在主线程消费（`addon.py:1331-1332`、`addon.py:1427`、`addon.py:1443`）。
- **验证**：两层。视觉 `look` 返回 PNG（`ImageContent`）+ 一行 caption（`server.py:1656-1664`）；数值 `get_scene_info` 按调用方点名的字段回一行一物体（`blender_scripts.py:43-45`，默认字段仅 4 个 `location/size/children/hidden`）。
- **交付**：`glb` / `fbx`（`addon.py:2617-2631`，格式白名单只这两个）。★ **但这条通道没有 MCP 工具包装**——`server.py` 全文对 `export_scene` 零命中（本地 grep），模型只能通过 `execute_blender_code` 自己调它，或自己写导出代码。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★ 工具清单与粒度统计（逐个数清）

`@mcp.tool` 装饰器共 **14 处**（`server.py:449,499,605,789,1482,1560,1743,1850,1920,2025,2115,2129,2135,2153`），其中**模型可见 9 个、仅 App 可见 5 个**：

| # | 工具 | 注册处 | 合并式判别参数 |
|---|---|---|---|
| 1 | `get_addon_status` | `server.py:449` | — |
| 2 | `disable_telemetry` | `server.py:499` | — |
| 3 | `get_scene_info` | `server.py:605` | `fields` / `root` / `query` / `limit` |
| 4 | `execute_blender_code` | `server.py:789` | 代码通道本身 |
| 5 | `record_trajectory_feedback` | `server.py:1482` | — |
| 6 | `look` | `server.py:1560` | `mode` = viewport / camera / angles / frames / image（`server.py:1580-1586`），`shading` 5 值 |
| 7 | `generate_3d` | `server.py:1743` | `provider` = auto/tripo/hunyuan3d/hyper3d/meshy（`server.py:1774`）+ `job` 续等 |
| 8 | `search_assets` | `server.py:1850` | `source` = polyhaven/sketchfab/polypizza（`server.py:1874`）+ `asset_type` |
| 9 | `import_asset` | `server.py:1920` | `source` + `asset_type` = hdris/textures/models（`server.py:1938`）|
| 10-14 | `search_mentions` / `open_viewport` / `viewport_latest` / `viewport_capture` / `viewport_pick` | `server.py:2025,2115,2129,2135,2153` | **仅 App 可见**，不进模型上下文 |

- 「9 个」不是我的推断：仓库自带断言 `MODEL_TOOLS`（`tests/test_consolidated_tools.py:10-13`，9 个名字）并要求 `{t.name for t in tools if not is_app_only(t)} == MODEL_TOOLS`（`tests/test_consolidated_tools.py:16-18`）；README 同步写「as nine tools」（`README.md:649`）。
- App-only 的判定是元数据不是代码分支：`_APP_ONLY = {"ui": {"visibility": ["app"]}}`（`server.py:2001`）+ `is_app_only()` 读 `meta.ui.visibility == ["app"]`（`src/blender_mcp/openai_apps.py:105-108`），在 `list_tools` 钩子里按客户端能力过滤（`server.py:2209-2218`，注册在 `server.py:2221`）。
- **合并式工具是常态**：9 个里 **4 个带动作判别参数**（上表第 6、7、8、9 项——`look.mode`、`generate_3d.provider`、`search_assets.source`、`import_asset.source+asset_type`），它们是"一个工具一族动作 + 一个选择子"；另有 1 个（第 3 项 `get_scene_info`）带的是**观测选择子** `fields/root/query`，只决定"回什么字段"，不决定做哪个动作——两者不该混算。
- **粒度分两层**：MCP 面 9 个；addon 命令表 **21 个常驻 + 20 个受开关控制**（常驻见 `addon.py:1537-1557`；条件块下详）= 最多 41 个命令，再叠加 Tripo 的动态注册（`addon.py:1607`）。条件块明细：PolyHaven 5（`addon.py:1563-1567`）、Hyper3D 3（`addon.py:1574-1576`）、Sketchfab 3（`addon.py:1583-1585`）、Poly Pizza 2（`addon.py:1592-1593`）、Hunyuan3D 3（`addon.py:1600-1602`）、Meshy 4（`addon.py:1615-1618`）。
- **兼容层**另算：老服务端会发的 **38 条命令**必须继续被应答（`tests/test_compat_matrix.py:41-53` 列出全部 38 个字符串），并有历史 addon 五个版本的回归（`tests/test_compat_matrix.py:30-37`），协议版本号 14（`src/blender_mcp/addon_manager.py:23`）。

### 3.2 其余机制

| 机制 | 怎么做的 | 证据 |
|---|---|---|
| **代码通道 + 观测脚本**替代"每个操作一个工具" | 观测能力写成脚本体，`ARGS` 注入 + 标记行回传；不新增 addon 命令 | `blender_scripts.py:1-35` |
| **双向回退**的观测实现 | `look` 有 native（addon 原生命令）与 scripted（脚本）两条路，按 mode 选先后，互相兜底；退化成朴素视口时**主动追加一句说明** | `server.py:1622-1649`（说明追加在 `1646-1648`）|
| **请求错 vs 环境错分流** | `_LookRefused` 表示"请求本身有问题"（物体不存在、没相机）⇒ 直接报错不兜底；其它异常才兜底 | `server.py:1633-1635`、`server.py:1652-1653` |
| **opt-in AST 校验**（防提示注入） | `BLENDER_MCP_SAFE_MODE=1` 才启用；策略是结构式（deny-by-default 节点走查、解析后的点路径规则、无根导航兜底、拒绝变量遮蔽），不靠模式匹配；拒绝信息回给模型让它重写 | `src/blender_mcp/safe_mode.py:1-54`（环境变量名 `safe_mode.py:72-77`）|
| **编排靠指令不靠代码** | 服务端 instructions（约 23 行）规定开工顺序、禁硬编码枚举、按 type 查节点、`look` 事后复核 | `server.py:329-351` |
| **按需加载知识页** | 7 篇 guide（`animation/bpy/level-design/materials/retopology/rigging/scene`）做成本地 md + `get_guide`，理由写在文件头：常驻会「每轮都吃上下文」 | `src/blender_mcp/guides.py:1-6`；篇目见 `src/blender_mcp/guides/`（7 个文件）|

## 4. 运行条件与依赖

- 语言 Python：`requires-python = ">=3.10"`，运行依赖只有 `mcp>=1.26.0,<2` 与 `httpx>=0.27.0`（`pyproject.toml`）；`.python-version` 钉 3.11。
- 宿主：**Blender 3.0 或更新**（`README.md:236`）+ addon 协议 14（`addon_manager.py:23`）；`uv` 装包（`README.md:238`）。
- 本机（Windows / Python 3.14.7 / RTX 4080S 16GB）：**服务端能装，真机跑不了**。① `python -V` 实测 3.14.7，`import mcp` 实测成功（本地探测），纯 Python 依赖不缺；② 但 `where.exe blender` 无命中、`C:\Program Files\Blender Foundation` 不存在（本地 Test-Path），⇒ 没有宿主可供 `execute_blender_code` 执行，9 个工具里除 `get_addon_status` 一类会直接报"连不上"。
- ★ **纯 Python 单测在本机确实跑通了**（2026-10-23 实测）：`PYTHONPATH=src python -m pytest tests -q -p no:cacheprovider` 得 **494 通过 / 1 失败 / 55 跳过**，55.62 s（Python 3.14.7）。唯一失败 `tests/test_compat_matrix.py:225`：`Error checking addon status: No module named 'blender_mcp.config'`（把 `addon.py` 当独立模块导入时找不到随包模块）。⇒ 55 例跳过的正是需要 Blender 宿主 / 网络 / API key 的那些；**14 个工具本身一条都没跑过**，故本卡等级只能是读码，这条只作"依赖面确实极小"的旁证。
- 与 529 工具对照：它的依赖面极小（2 个运行时库 + 1 个宿主），**工具数与依赖数无关**——这是它敢收敛到 9 个工具的前提。（来源：`pyproject.toml` 依赖段）

## 5. 失败模式与已知坑

| # | 问题 | 证据 |
|---|---|---|
| 1 | `execute_blender_code` 是任意 Python 执行，README 自己用加粗警示「ALWAYS save your work before using it」 | `README.md:822` |
| 2 | addon 的 socket **无认证、无加密**，能碰到端口的人就能在 Blender 里跑 Python；README 原文因此要求只留在 localhost | `README.md:407-410` |
| 3 | 安全模式**只管 MCP 这条路**，addon socket 仍接受任何本地进程发来的裸 `execute_code`；文件里明写「It is a guard on what the model can be talked into, not a sandbox around Blender」 | `safe_mode.py:12-15` |
| 4 | addon 捕获 `Exception` 但**不捕获 `SystemExit`**，所以脚本不能拿 `sys.exit` 早退 | `blender_scripts.py:18-19`；断言见 `tests/test_consolidated_tools.py:34-39` |
| 5 | 老 addon 缺脚本化 `look` 时靠双向回退，但退化成朴素视口会**少掉多视角/线框**，只在返回文本里补一句，不报错 ⇒ 静默降级风险 | `server.py:1646-1648` |
| 6 | 下载在主线程上做，**UI 会卡住**直到传完；分辨率每升一档体积约四倍 | `README.md:807` |
| 7 | Poly Pizza 的 CDN 有 Cloudflare 机器人防护，**挡数据中心/VPN/云 IP**（API key 无关）| `README.md:808` |
| 8 | 7 篇 guide 已写好但**当前是关闭的**，`get_guide` 不在工具表里 | `tests/test_consolidated_tools.py:28-31` |
| 9 | 遥测**默认就收**一份最小匿名记录（安装 ID、会话 ID、工具名、成败、耗时、版本、OS、时间戳），只有内容类数据才需 opt-in | `README.md:831-833` |
| 10 | 文档与代码的一处不一致：`README.md:194-201` 的 Features 表只讲能力，不提交付的 5 个 App-only 工具；而 `export_scene`（`addon.py:2617`）在 addon 侧存在、在 MCP 面无包装（`server.py` 零命中）| `README.md:194-201`、`addon.py:2617` |
| 11 | 生成式接口会**花钱/耗额度**，`generate_3d` 的文档自己提醒每调用可能扣一次额度，且超时（45 s 上限）只返回 job 句柄，要再调一次续等 | `server.py:1760-1767`、`src/blender_mcp/generation.py:50`（`MAX_CALL_S = 45.0`）、`generation.py:46`（`POLL_INTERVAL_S = 5.0`）|

## 6. 对我方目标的可用处（机制层面）

1. **收敛工具面的判据来自它**：529 个工具的成本不只在 schema 体积，而在"模型要在 529 个名字里选对那一个"。它把选择压力从"选工具"移到"写代码 / 传判别参数"，代价是**执行面变宽**（任意 Python）。我方若保留细粒度工具，就等于选择了相反的代价结构。（来源：本卡 §3 工具粒度统计）
2. **判别参数分组**：`source` / `mode` / `provider` / `asset_type` 这几个选择子把同类动作收进一个工具，且**选择子取值在白名单里校验**（`server.py:1782-1783` 报 `quality must be…`）。这是「合并式工具」不牺牲可校验性的写法。
3. **观测脚本层**：把"读场景"写成脚本体 + `ARGS` + 标记行回传，好处是**观测能力升级不需要动宿主 addon**（`blender_scripts.py:1-8`）。对应我方：读模型状态的工具可以和建模工具分开演进。
4. **给普通模型的护栏写进 instructions 而不是文档**：禁硬编码枚举、按 type 而非名字找节点、颜色写 shader 输入而非 `diffuse_color`（`server.py:336-342`）——这三条正是"普通模型会犯的错"，被放进随会话注入的指令里。
5. **opt-in 的结构式代码校验**：deny-by-default + 解析后路径规则 + 拒绝并回传原因（`safe_mode.py:32-53`），比关键字黑名单抗绕过；同一形态可用于我方"模型写的 COM 脚本"（挡 `os/subprocess`、挡持久化注册）。
6. **双向回退 + 主动声明降级**：实现新老两路互为兜底，且**退化时在返回里明说**（`server.py:1647`）——把"能力不足"变成模型可见的事实，而不是静默成功。

## 7. 许可与红线

- MIT（`LICENSE:3`，`Copyright (c) 2025 Siddharth Ahuja`）：可读、可抄、可改、可商用，**义务只有保留版权声明**。
- 红线一：**别继承默认遥测**（`README.md:831`）。若借鉴代码，采集项要按我方口径清零，而不是"改了默认值但留着通路"。
- 红线二：`addon.py` 是 294181 字节的单文件（本地 `Get-ChildItem` 实测），`src/blender_mcp/server.py` 100757 字节——**只借机制，不整文件搬运**。
- 红线三：它的 socket 无认证（`README.md:407`），我方不得把这种"本地端口即可执行任意代码"的形态带进交付路径。

## 8. 证据清单

- `LICENSE:3`（MIT + 版权行）；`pyproject.toml`（`license`/`requires-python`/依赖/Homepage 旧名）
- `README.md:236`（Blender ≥3.0）、`README.md:407-410`（socket 无认证）、`README.md:649`（nine tools）、`README.md:807-808`（下载卡顿 / Cloudflare）、`README.md:815-818`（协议）、`README.md:822`（任意代码警示）、`README.md:831-833`（遥测）
- `src/blender_mcp/server.py:449,499,605,789,1482,1560,1743,1850,1920,2025,2115,2129,2135,2153`（14 个 `@mcp.tool`）
- `src/blender_mcp/server.py:57-58`（localhost:9876）、`server.py:329-351`（SERVER_INSTRUCTIONS）、`server.py:1622-1649`（look 双向回退）、`server.py:2001`（`_APP_ONLY`）、`server.py:2209-2218`（按客户端能力过滤工具表）
- `src/blender_mcp/openai_apps.py:105-108`（`is_app_only`）
- `src/blender_mcp/blender_scripts.py:1-8,12,15-35,43-45`
- `src/blender_mcp/safe_mode.py:1-54,72-77`；`src/blender_mcp/generation.py:46,50`；`src/blender_mcp/addon_manager.py:23`
- `addon.py:1331-1332,1427,1443`（主线程队列）、`addon.py:1536-1619`（命令表 21+20）、`addon.py:1607`（Tripo 动态）、`addon.py:2617-2631`（glb/fbx 白名单）
- `tests/test_consolidated_tools.py:10-18,28-31,34-39`；`tests/test_compat_matrix.py:30-37,41-53`（38 条老命令）
- `gh api repos/ahujasid/mcp-for-blender`（stars / pushed_at / language，取数 2026-10-24）；`git remote -v`（同址）
- 本地统计：`tests/*.py` 共 26 个测试文件、`def test_` 385 处；`src/blender_mcp/guides/` 7 篇 md
- ★ 本机实测（2026-10-23，Python 3.14.7）：`python -m pytest tests -q -p no:cacheprovider`（`PYTHONPATH` 指向 `src`）→ 494 通过 / 1 失败 / 55 跳过，55.62 s；失败点 `tests/test_compat_matrix.py:225`（`No module named 'blender_mcp.config'`）

## 9. 未确认事项

1. **14 与 9 这两个数是静态计数**——我没有装包、没有真的调 `mcp.list_tools()`；9 的确定性来自仓库自带断言（`tests/test_consolidated_tools.py:16-18`），但"运行时到底返回几个"未实测。
2. **`premium_tripo_handlers()` 到底注册了几条命令**——它是函数调用（`addon.py:1607`），我没展开统计，故 addon 命令总表只能写"最多 41 + Tripo 动态"。
3. **9 工具是否是"因为有 `execute_blender_code` 才敢收敛"**——`test_consolidated_tools.py:1-2` 的措辞（"a handful of tools and observation scripts that run through execute_code"）指向这个意图，但我没找到 changelog/commit 说明它是一次性收敛还是逐步砍出来的（仓库是浅克隆，`git log` 只有 1 条）。
4. **`export_scene` 为何没有 MCP 包装**——代码事实确定（addon 有、server 无），原因未确认（可能是有意让模型走代码通道）。
5. **遥测服务端收什么、留多久**——我只读到 README 的自述与 `telemetry.py` 存在（13377 字节），未读其发送实现。

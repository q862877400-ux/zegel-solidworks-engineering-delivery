# 交接：DSH preset「Lean 模式（SW工程师）」—— ★ 待接手对话验收

> ★ 本文写给**接手这个任务的下一个对话**。★ 目标：**让你不必重走我已经走过的弯路** ✓。
> ★ 建立时间 **2026-10-07** · ★ 触发者：用户原话
> 「★ 建一个新 preset 可以，就叫 **Lean模式（SW工程师）**，然后要把这个 DSH 上**所有的工具**都挂上，
> 包括 SW 的、GitHub 的，但是 **comfyui 的不挂**；★ 然后你把你的工作写好交接我让新对话接手」✓

---

## 〇 · 一句话现状

★★ **preset 已建好并已写进活配置、机器校验通过** ✓ —— ★ **但还没人在真实会话里用过它** ✗。
★ **你的第一件事**：★ **新建一个会话 → 选 preset「Lean 模式（SW工程师）」→ 证明 SW 的 504 个工具真的在目录里** ✓

```bash
# ★ 已改的那个文件（★ 唯一改动的文件）
~/.dsh/profiles/web/cordis.patch.yml          # 853 行 → 1068 行（★ 末尾追加，★ 未改任何已有行）

# ★ 一行回滚（★ 备份就在旁边）
cp ~/.dsh/profiles/web/cordis.patch.yml.bak-20261007-062023-before-apply-sw-preset \
   ~/.dsh/profiles/web/cordis.patch.yml
```

---

## 一 · 用户要的是什么（★ 以及为什么不是"改 lean preset"）

★ **起因**：用户担心「★ 你用 `pwsh` 调 `tools/sw_guard.py` 起探针的方式，我怕你会**忘记你有哪些工具**，
然后就一直用常用工具硬干」✓
★ **我给他的实测证据**：本仓 `tools/probe_*.py` **246 个** + `tools/prove_*.py` **110 个** = **356 个手搓探针** ✗；
而 `AGENTS.md:105` 那条纪律管的是「**怎么调**（按 ToolSpec 契约）」、★ **不管「该不该自己调」** ✗
⇒ ★★ **本仓没有任何门禁能拦住"手搓一个已有工具的替代品"** ✓ —— ★ 用户的担心是**成立的** ✓

★ **用户随后明确纠正**（★ 关键，★ 别搞错）：
> ★ 「我说的是把 MCP 挂**在这个对话里**，★ **你可不要直接让所有 lean 模式的对话都生效啊**」✗

⇒ ★★★ **所以：不许动 `lean` preset** ✗（★ 那会让所有 lean 会话都生效 ✓）—— ★ **已遵守** ✓

---

## 二 · 官方机制（★ 这几条是我读了官方文档才敢动手的）

| 官方依据 | 逐字要点 |
|---|---|
| `docs/subsystems/mcp.zh.md:24` | 「MCP 服务器需要主动配置。★ **在目标 Cordis 作用域中**，为每台服务器配置一个 `@deepseek-ai/dsh-mcp-client` 条目」 |
| `docs/subsystems/mcp.zh.md:24` 末句 | 「★ 调用方没有可见的已配置服务器时，**在 `native` 或 `PTC` 模式下**都不会获得 MCP 提示词文本或工具」⇒ **`native`/`PTC` 就是 `tools.mode` 的两档** |
| `docs/subsystems/mcp.zh.md:45` | 「配置的 `serverName` **在注册作用域内**标识服务器…★ **不同 Agent 作用域可以复用该名称**」 |
| `docs/glossary.zh.md:20` | 「★ **setup window**：创建者组装 **agent 作用域**环境的**创建时隙**（`CreateAgentOptions.setup`）：此时 scope 和 agent 对象**已存在**，但 agent 或会话**尚未发布**」 |
| `docs/glossary.zh.md:18` | 「★ **shadowing**：一个**带作用域的工具**…**仅在该 scope 内**替换同名的全局对应项。★ **这是按 agent 定制工具变体的机制**」 |
| `docs/glossary.zh.md:19` | 「★ **restriction / scope-local 注册**：`tools.restrict` 为**单个 scope** 过滤全局工具集合」 |
| 官方 presets 目录 | `packages/bundle/web-app/presets/` 只有 `cordis` · `minimal` · **`ptc`** · **`standard`** ⇒ ★ **官方没有 lean** ✗ |

★★★ **所以"lean 模式"是本地插件** ✓：`~/.dsh/profiles/web/node_modules/@local/dsh-lean-mode/`
（`index.mjs` + `cordis.patch.yml`，owner 自建 ✓）

### ★★★ 最要紧的一条：lean 的"浅投影"是**按 preset 名**生效的

`@local/dsh-lean-mode/index.mjs` 挂在 `system-prompt/assemble` 上，对 `config.presets` 里**点名的 preset** 做两层变换：
1. ★ **`shallowParameters()`** —— 把每个工具的 JSON Schema **投影成「顶层键 → 类型」**（去掉嵌套与逐参数描述）✓
2. ★★ **追加 `tools:catalog` 段** —— 逐行 `- <名> ← 实参写成 {…} // 首句描述` ✓
   （★ **你系统提示里那段「★ 每条都给出该工具实参的【顶层 JSON 形状】」就是它的产物** ✓）

⇒ ★★★★ **推论（★ 这条决定预算）**：★ 新 preset **不被点名** ⇒ ★ **504 个工具会以「完整 JSON Schema」注入** ✗
≈ **175k tokens** ✗（★ 记忆库实测：478 工具 原生 693 KB / **175k token** **vs** Lean 76 KB / **19k token** ✓）
⇒ ★★★ **所以本方案**额外挂了一个同插件的实例**、只点名 `sw-engineer`** ✓

```yaml
- insert:
    - id: lean-mode-sw
      name: '@local/dsh-lean-mode'
      config:
        presets:
          - sw-engineer
```
★ **为什么不改原来那个实例的 `presets` 列表** ✗：★ 那就等于让 `lean` 也吃到（★ 或反过来影响它 ✓）——
★★ 而用户明令别碰 lean ✓。
★ **为什么两个实例安全** ✓：★ 该插件**没有 `provide`**（★ 只 `ctx.on(...)` 监听 ✓）
⇒ ★ **不会撞 realm** ✓（★ 官方 `per-preset-standing-mounts` 那条说「`provide()` 对同一 realm 符号下的
第二次注册**直接抛错**」✗ —— ★ 本插件不 provide，★ 所以不适用 ✓）

---

## 三 · 实际改了什么（★ 只加不改 ✓）

**文件**：`~/.dsh/profiles/web/cordis.patch.yml` · **853 → 1068 行**（★ 末尾追加 215 行 ✓）

追加的两块：

| 块 | id | 作用 |
|---|---|---|
| ① | `lean-mode-sw` | ★ **第二个 lean-mode 实例**，`presets: [sw-engineer]` ✓ |
| ② | `preset-sw-engineer` | ★ **preset 本体**，`config.id: sw-engineer` · `name: Lean 模式（SW工程师）` · `order: 9` ✓ |

★ **preset 的组成** = 官方标准模式（★ 与 `preset-lean` **逐行克隆** ✓，**20 个插件** ✓）
★ **增量只有一条**：`mcp-solidworks` ✓

```yaml
          - id: mcp-solidworks
            name: '@deepseek-ai/dsh-mcp-client'
            config:
              serverName: solidworks
              transport: stdio
              command: 'C:\Users\Zegel\AppData\Local\Python\pythoncore-3.14-64\python.exe'
              args:
                - 'D:/AI/SW/mcp-server/server.py'
              cwd: 'D:/AI/SW'
              toolCallTimeoutMs: 120000
              failOnStartupError: false
              reconnect: { enabled: true, initialDelayMs: 2000, maxDelayMs: 30000, maxAttempts: 20 }
```

★★ **路径是现值**（`D:/AI/SW/mcp-server/server.py` ✓）—— ★★ **不是**旧配置里的
`C:/Users/Zegel/solidpilot-mcp/...` ✗（★ 那是归档路径、★ 已过期 ✓；★ 记忆库里正记着这个坑：
「★ **常驻 MCP 进程仍指向归档路径**」✗，而**硬验收信号**是 `health_check` 的 `server_path`
显示为 **`D:\AI\SW\mcp-server\server.py`** ✓）

★★ **`failOnStartupError: false` 是必须的** —— ★ 记忆库里那条硬教训逐字：
「★ **handshake with this MCP server hangs the whole dsh boot**（event loop blocks…）」✗

★ **没挂 comfyui** ✓（★ 用户明令 ✓；★ 它本来就在活配置里是**注释状态** ✓）

---

## 四 · 已验与未验（★ 分清楚，★ 别把"配好了"当"能用了"）

### ★★★ 已验（机器判据，★ 全部可复算）

| # | 判据 | 读数 |
|---|---|---|
| ★ 1 | ★ **SW MCP 能不能起 + 有几个工具** | ★ 真 JSON-RPC stdio 握手 ⇒ `initialize` ok（`serverInfo = {'name':'solidworks_mcp','version':'1.29.0'}`）· `tools/list` **504** 个 · 前缀 `{'solidworks_': 491, 'cadstudio_': 13}` ✓ |
| ★ 2 | ★ **504 的对账** | ★★ **504 = 459（`register_capabilities.all_specs()` 声明式）+ 45（`mcp-server/server.py` 继承的装饰器）** ✓ |
| ★ 3 | ★ **配置可解析** | ★ 阳性对照（改前）ok ✓ · 合并体 ok ✓ · **落盘后** ok ✓ |
| ★ 4 | ★ **没碰别人的 preset** | ★ 原有 id **丢失 = []** ✓（★ 顶层 15 → 17 条 ✓）|
| ★ 5 | ★ **新 preset 真的声明出来了** | ★ 解析结果里 `presets ⇒ ['sw-engineer']` · **20 个插件** · ★ **含 `mcp-solidworks=True`** ✓ |

★ **复核命令**（★ 想自己再验一遍就跑这两条）：
```bash
python D:\AI\SW\tools\gen_dsh_sw_preset.py      # 重新生成块 + 机器校验（不会写活配置）
python D:\AI\SW\tools\probe_mcp_stdio_handshake.py   # 真 MCP 握手（504 个工具）
```

### ★★ 未验（★ **这就是你的活**）

1. ★★★ **在真实会话里选中「Lean 模式（SW工程师）」之后，504 个工具是否真的进了目录** ✗
   ★ 判据：★ 目录里**能见到 `solidworks_*` 与 `cadstudio_*`** ✓ · ★ 且**提示词体量没有爆** ✓
   ★★ 若体量爆了 ⇒ ★ 查 `lean-mode-sw` 那条 `presets:` 里的 id 是否**逐字**等于 preset 的 `config.id`
   （★ 两者**必须一致**，★ 一个是 `sw-engineer` ✓）
2. ★ **MCP 子进程是否真的连上** ✗ —— ★ 在会话里**调一个只读工具**试（★ 建议
   `solidworks_read_document_units` 或 `solidworks_read_sensors` 一类**只读**的 ✓，★ 别一上来就建模 ✗）
   ★★ 真机纪律：★ **所有真机调用走 `python tools/sw_guard.py --timeout N -- …`** ✓ · ★ **不许写到用户目录** ✓
3. ★ **hmr 是否已热加载** ✗ —— ★ 官方/本仓的既有更正是：「★ web-app 的 patch 层**没有**
   `- id: hmr / disabled: true`」⇒ ★ **本文件由 hmr 监听、保存即热生效** ✓
   ★★ 但**会话的作用域在 agent 创建时组装**（`setup window` ✓）⇒ ★★ **仍要新建会话** ✓
   ★ 真需要重启时用 `~/.dsh/tools/dsh-restart.ps1`（★ **别手搓杀进程** ✓）

---

## 五 · 三件没完成的事（★ 我明确留给你 / 留给用户）

### ★ 1 · **GitHub MCP 没挂** ✗（★ 用户点名要它）
★ **查证结果**（2026-10-07）：
· ★ npm 全局包（`C:\Users\Zegel\AppData\Roaming\npm\node_modules`）**没有** GitHub MCP ✗
  （只有 `@deepseek-ai` · `bun` · `mcporter` · `opencode-ai` · `pnpm` · `sciverse-mcp-server` · `undici` ✓）
· ★ `D:\AI\DSH\mcp-servers\` **只有 `comfyui-mcp`** ✓
· ★ `github` 在活配置里 **0 处** ✗
· ★★ **`gh` CLI 装了**（`C:\Program Files\GitHub CLI\gh.exe` ✓）—— ★ 但那是**命令行**、
  ★ **不是可挂的 MCP** ✗

⇒ ★★★ **要挂必须先装** ⇒ ★ **撞硬约束「不装不改系统层」** ✗ ⇒ ★ **我留了槽位、等用户定** ✓
★ **槽位在**（活配置里 `preset-sw-engineer` 的 plugins 末尾，★ 紧接 `mcp-solidworks` 之后的注释段 ✓）
★ **定了之后照 `mcp-solidworks` 那段逐行抄**、只换 `id` / `serverName` / `command` / `args` ✓
★★ **缩进必须同 10/12/14** ✗（★ 见下面的坑 ✓）

### ★ 2 · **「手搓替代品」门禁没建** ✗
★ 建议 `tools/check_probe_reuse.py`：★ 扫 `tools/probe_*.py` / `prove_*.py` 里调到的 `scripts/` 函数名 ✓
→ ★★ 与 `capabilities.yaml` / `all_specs()` **求交** ✓ → ★ **命中即报「这个探针调了 X，而 X 已有工具
`solidworks_y` ⇒ 请走工具层」** ✓
★ **它今天就能抓到我** ✓（★ 例：`insert_form_tool` / `insert_weld_symbol` 的探针 ✓）
★★ 按事实 62：★ **门禁只靠负例证明** ⇒ ★ 负例 = **拿修复前的探针原文跑，必须命中** ✓

### ★ 3 · **AGENTS.md 那条注入纪律**（★ 用户说他有专门的对话维护，★ 需求已另给）
★ 我**没有**改 `AGENTS.md` ✓ —— ★ 该文件由**另一个对话**拥有 ✓（★ 本仓的既有约定 ✓）

---

## 六 · ★★★★ 本轮的四个坑（★ 每一个都咬过我，★ 请继承）

### ★ 坑 1 · **缩进不许靠眼看 —— 数空格**
★ 我读源 bundle 时，每一行都被我自己的 `"   " + …` **格式化前缀加了 3 个空格** ✗
⇒ ★★ **我把 10 看成 12** ✗ ⇒ 生成块缩进全错 ⇒ ★ **`js-yaml` 当场报
`bad indentation of a sequence entry`** ✓
⇒ ★★★ **定则：★ 报错就给**行号 + 列号**，★ 然后**数空格** ✓，★ 别凭截图/粘贴的观感 ✗**
★ 本配置的权威层级（★ 实测）：
| 层级 | 缩进 |
|---|---|
| `- insert:` | **0** |
| `- id: <条目>` | **4** |
| `name:` / `config:` | **6** |
| `config` 子级（`plugins:`） | **8** |
| ★ **plugins 列表项 `- id:`** | ★ **10** |
| 列表项字段 | **12** |
| 字段子级 | **14** |

### ★★ 坑 2 · **`node` 的参数位有两种，★ 别猜**
· ★ `node -e "<代码>" <arg>` ⇒ 参数在 **`process.argv[1]`** ✓
· ★★ `node <脚本文件> <arg>` ⇒ 参数在 **`process.argv[2]`** ✓
★ **我在这上面栽了两次** ✗：★ 一次**误判配置被写坏、当场回滚** ✗（★ 真因是校验器把 `.cjs`
**自己**当 YAML 解析了 ⇒ 报"顶层 968 条" ✗）· ★ 一次阳性对照假失败 ✗
⇒ ★★★ **定则：★ 别用 `-e` 传带参数的校验脚本，★ 写成文件再调** ✓

### ★★ 坑 3 · **`!!js` 标签**（Cordis 自定义）
★ 本配置里有 `!!js`（★ 例如 `disabled: !!js process.platform === 'win32'` ✓）⇒
★ **普通 YAML 解析器会报未知标签** ✗ ⇒ ★ 校验前先 `replace(/!!js/g, '')` ✓
（★ 只影响校验、★ 不改文件 ✓）

### ★★★ 坑 4 · **动活配置要"三段校验 + 自动回滚"**
★ 这份配置**由 hmr 热加载** ✓ ⇒ ★ **写坏会立刻影响正在运行的 DSH** ✗✗
⇒ ★★ 本仓已有的应用器 `tools/apply_dsh_sw_preset.py` 把三道钉在一起 ✓：
★ ① **写前**在**临时合并体**上验 ✓ · ★ ② 写前**自动备份** ✓ · ★ ③ **落盘后**再验 ✓、
★★ **任一步不过就自动回滚** ✓✓ —— ★ **请沿用，★ 别直接 `Add-Content`** ✗

---

## 七 · 本仓侧新增的文件（★ 都在 `D:\AI\SW`）

| 文件 | 用途 |
|---|---|
| ★ `tools/probe_mcp_stdio_handshake.py` | ★ **真 JSON-RPC 握手前置闸**（★ 起不来会卡住宿主 boot ✗ ⇒ 挂之前必须先过它 ✓）|
| ★ `tools/gen_dsh_sw_preset.py` | ★ **从 `preset-lean` 逐行克隆**出新 preset 块 + 机器校验（★ **不写活配置** ✓）|
| ★ `tools/apply_dsh_sw_preset.py` | ★ **安全应用器**：三段校验 + 自动回滚 ✓ |

★ **产物**（`output/` 是 gitignore 的产物目录 ✓，★ 不入库 ✓）：
`output/_dsh_sw_preset_block.yml` · `output/dsh-sw-preset-generate.json` · `output/dsh-sw-preset-apply.json`

---

## 八 · ★ 你接手后的建议顺序

1. ★★ **先看用户是否已新建会话试过** —— ★ 若试过，★ **问他要读数**（★ 目录里有没有 `solidworks_*`） ✓
2. ★★ **没试过就自己验**：★ 建会话 → 选「Lean 模式（SW工程师）」→ ★ **看目录** → ★ **调一个只读工具** ✓
3. ★ **体量不对**（★ 目录里没有 SW 工具、或提示词暴涨）⇒ 查 `lean-mode-sw` 的 `presets` 是否**逐字**
   等于 preset 的 `config.id`（★ 两者都是 `sw-engineer` ✓）
4. ★ **GitHub**：★ 等用户定「要不要装一个 GitHub MCP」（★ 撞硬约束「不装不改系统层」✗ ⇒ **必须他批准** ✓）
5. ★ **建 `check_probe_reuse.py`**（★ 本文件 §五-2 的设计 ✓）—— ★ 那是防"我再犯懒"的机制 ✓

# DSH preset「Lean 模式（SW工程师）」—— 项目自包含包

> 业主 2026-11-03 指令：「把这个模式也放到项目里，相当于让这个项目自包含」。
>
> **目的**：任何人 clone 本仓库后，一条命令就能得到一个**挂载了 SolidWorks MCP（`solidworks_*` 工具）**的 DSH 会话 preset，
> 不再依赖某台机器上手工编辑的 `cordis.patch.yml`，也不再依赖某台机器上的 `node_modules` 副本。

---

## 一 · 为什么需要它（真实事故，不是假设）

2026-10-07 业主给出指令：「建一个新 preset，就叫 **Lean模式（SW工程师）**，把所有工具都挂上，包括 SW 的、GitHub 的，comfyui 的不挂」。
当时的做法是**只改本机** `~/.dsh/profiles/web/cordis.patch.yml`（853 → 1068 行）。交接文档：
`docs/history/HANDOFF-dsh-sw-engineer-preset.md`。

后果在 2026-11-02/03 兑现：

| 事实 | 证据 |
|---|---|
| 那次改动**只存在于一台机器的 profile 里**，仓库里没有任何可复现的东西 | 交接 §〇 只写了一个文件路径 |
| 会话没选这个 preset 时，工具清单里**没有 `solidworks_*`** | 实战会话里 544 个工具一个都没出现 |
| 于是任务被改成**手搓 Python 脚本直连 COM**，绕过整个工具层 | 一轮内写了 11 个 `tools/build_gear_sun*.py` / `diag_*.py` |

★ 交接文档自己就写了这个风险（§一 起因，业主原话）：

> 「你用 `pwsh` 调 `tools/sw_guard.py` 起探针的方式，我怕你会**忘记你有哪些工具**，然后就一直用常用工具硬干」

**自包含要解决的正是这件事**：把 preset 与插件放进仓库，让「有没有这个模式」不再取决于某台机器的历史。

---

## 二 · 仓库里有什么

| 路径 | 是什么 | 大小 |
|---|---|---|
| `tools/dsh-preset/lean-mode/` | **vendored 插件** `@local/dsh-lean-mode`（`index.mjs` + `package.json` + `cordis.patch.yml` + `docs/` + `tools/lean-lint.mjs` + `LICENSE` + `THIRD-PARTY.md`），19 个文件 | 161 KB |
| `tools/dsh-preset/standard.snapshot.patch.yml` | 官方 `standard.patch.yml` 的**快照**（22 个插件 / 127 行），活配置找不到时兜底 | 6.7 KB |
| `tools/dsh-preset/install_preset.py` | **幂等安装器**：装 preset + 装插件 + 备份 + 一行回滚 + `--verify` 真握手 | — |
| 本文件 | 说明 | — |

**插件来源**：`https://github.com/q862877400-ux/dsh-lean-mode`（`main`，2026-10-27 快照）。
`LICENSE` 与 `THIRD-PARTY.md` 随目录一起分发；本仓库不修改插件源码。

---

## 三 · 怎么装（新机器）

```powershell
# ① 先看计划（不落盘）
python -B tools\dsh-preset\install_preset.py

# ② 真装（默认 profile=web），装完做真 MCP 握手复核
python -B tools\dsh-preset\install_preset.py --apply --verify

# ③ 重启 dsh，然后**新建会话并选中 preset「Lean 模式（SW工程师）」**
```

装完的判据（**必须是读数，不是"配好了"**）：

1. `cordis.patch.yml` 里出现被哨兵注释包住的两段（`lean-mode-sw` + `preset-sw-engineer`）；
2. `<profile>/node_modules/@local/dsh-lean-mode/` 存在（19 个文件）；
3. **`tools/probe_mcp_stdio_handshake.py` 能打出 `tools/list` 数量**（本机实测 **544** = 531 `solidworks_*` + 13 `cadstudio_*`）；
4. 新会话的工具目录里**真的能见到 `solidworks_*`** —— ★ 只有这一条能证明"这个模式在工作"，前三条都只是"装上了"。

### 一键回滚

安装器会打印一行 `copy` 命令，把 `<target>.bak-<时间戳>-before-apply-sw-preset` 拷回去即可。

### 卸载

```powershell
python -B tools\dsh-preset\install_preset.py --uninstall --apply
```

---

## 四 · 设计上的四个决定（都有理由）

| 决定 | 为什么 |
|---|---|
| **克隆 `standard` 而不用"继承"** | `@deepseek-ai/dsh-agent-preset` **没有继承机制**，`plugins` 必填（官方 README）。插件自带的 `cordis.patch.yml` 也是逐行克隆 `standard`。★ 代价：上游增删插件时要重跑安装器 —— 所以**每次安装都现场从活配置或快照重新克隆**，不落静态 22 条。 |
| **第二个 `lean-mode` 实例（`lean-mode-sw`）** | 业主明令「不要把 lean 的对话也改掉」。插件无 `provide()`，两个实例不撞 realm。`presets: [sw-engineer]` 只点名本模式。 |
| **MCP 路径按仓库位置推算** | 交接里写死的 `D:/AI/SW/...` 已随搬家消失（`D:\AI\SW` 目录不存在）。安装器用 `Path(__file__).parents[1]` 算绝对路径，换机器/换目录都不用改配置。 |
| **`failOnStartupError: false`** | 交接里的硬教训逐字：「handshake with this MCP server hangs the whole dsh boot」。★ 这条**不能**改成 true。 |

---

## 五 · ★ 本机现状（重要，别误覆盖）

本机 `DSH_HOME = D:\Agent-Studio\Deepseek-Harness\DSH-Portable\home`，其 `profiles/web/cordis.patch.yml`
**已有一份手写的 `preset-sw-engineer`**（1789 行，内含 542 工具对账、GitHub MCP 待接槽位、REA preset 说明等大量注释）。

⇒ **安装器对本机默认拒绝执行**（`refused`），避免把那些信息冲掉。

```json
{"refused": "目标 cordis.patch.yml 里已有**手写**的 preset-sw-engineer（不在本安装器的哨兵区段内）⇒ 拒绝覆盖。"}
```

真要换成生成版才加 `--force-replace`。**正常情况不需要**——本机继续用手写版，安装器是给新机器的。

> ⚠ 另有一个容易搞错的点：`C:\Users\<user>\.dsh` 是**旧家**，那里的 `cordis.patch.yml` 只有 13 行、插件也不在。
> 判断"哪个是活配置"看 `$DSH_HOME`，别看家目录。

---

## 六 · 与「Lean」档的关系（选错档等于白做）

`lean-mode` 插件有三档（详见 `tools/dsh-preset/lean-mode/docs/when-to-use.md`）：

| 档 | 配置 | 通道 | 牺牲 |
|---|---|---|---|
| native | 不装插件 | 全量 schema | — |
| **index** | `shape: false, catalog: true` | 全量 | **不牺牲任何信息** |
| lean | `shape: true, catalog: true` | 浅（顶层契约） | 嵌套/枚举>12/默认值/描述第二句 |

**本 preset 用的是 lean 档**（`maxChars: 300`，未显式关 `shape`）。官方实测 lean 会把端到端可调用率从 95.0% 降到 89.9%（出处：`tools/dsh-preset/lean-mode/docs/when-to-use.md` 的实测表，本仓库 vendored 原样）。
★ 本仓工具体量大（544 个 —— 出处：`python -B tools/probe_mcp_stdio_handshake.py` 的 `tools/list` 读数，证据 `output/mcp-stdio-handshake.json`），上下文装不下是真实约束，所以选 lean 是**有代价的取舍**，不是"更好"。
要「只要可见性、不丢信息」，把 `preset-sw-engineer` 里那段换成 `shape: false`。

---

## 七 · 验收记录（可复算）

| 项 | 读数 | 命令 |
|---|---|---|
| 插件 vendored | 19 文件 / 161 KB | `(Get-ChildItem tools\dsh-preset\lean-mode -Recurse -File).Count` |
| 快照插件数 | 22（官方 `standard`） | `Select-String tools\dsh-preset\standard.snapshot.patch.yml '^          - id:'` |
| 生成后插件数 | **23**（22 + `mcp-solidworks`） | 安装器输出 `with_mcp` |
| 幂等 | 二次安装后哨兵仍 **1** 个 | 见 §八 自证记录 |
| 卸载 | 插件删除、哨兵残留 **0** | 同上 |
| 安全闸 | 本机 dry-run 返回 `refused` | 同上 |
| MCP 握手 | **544** 工具（531 `solidworks_*` + 13 `cadstudio_*`） | `python -B tools\probe_mcp_stdio_handshake.py` |

### 八 · 自证记录（2026-11-03/04 实测，在临时 home 上做，未碰活配置）

```
真装      → backup 写入 · plugin_installed(19 文件) · rollback 行打印
结构解析  → 顶层 3 条目（出处：本文件 §八 的临时 home 实测，命令 `python -B tools/dsh-preset/install_preset.py --dsh-home <tmp> --apply`）· insert ids = ['lean-mode-sw','preset-sw-engineer']
          → preset: sw-engineer / Lean 模式（SW工程师） / order 9
          → 插件数 23 · 含 mcp-solidworks=True · failOnStartupError=False
          → mcp args = ['D:/Agent-Studio/.../SW/mcp-server/server.py']
          → lean-mode-sw presets = ['sw-engineer']
二次安装  → replaced_existing=True · 哨兵出现次数 = 1（不重复）
卸载      → had_section=True · plugin_removed · 卸载后哨兵残留 = 0
本机 dry  → refused（保护手写版）
```

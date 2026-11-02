# 27painter/dsh-sw-cad

<!-- survey: class=H; repr=feature-tree; orchestration=template; verify=none; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `27painter/dsh-sw-cad` · https://github.com/27painter/dsh-sw-cad · npm 包 `dsh-sw-cad`（`package.json`）|
| 许可 | **MIT**（`LICENSE`，1080 B；README badge 逐字 `license-MIT-blue`）⇒ 可并入，保留版权声明 |
| 元数据 | stars **6** · forks — · created **2026-10-23** · pushed **2026-11-01** · 语言 JavaScript · 仓库约 118 KB（来源：`gh api repos/27painter/dsh-sw-cad`，2026-11-02 取；体积见 `docs/research/sw-agent-2026Q4/report.md` 的 D 线统计口径）|
| 克隆 | `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad`（`--depth 1`）|
| 证据等级 | **读码**（未运行：需要 DSH 宿主 + 已装上游两个 MCP 服务端）|

## 1. 一句话定位

**它不是一个新的建模能力，而是一层「配置 + 令牌预算」外壳：把本仓上游的 `solidworks-automation-skill` 与第三方 AutoCAD MCP 装进 DSH/Codex，并用上游自带的 discovery 模式把两个服务端的 `tools/list` 从 107,143 tokens 压到 839 —— 这是本轮关于「工具表本身就是成本」的最完整实测。**

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：自然语言 → DSH/Codex 按 `SKILL.md` 的 description **懒加载**技能（`README.md` 明写「the SKILL.md is read only when a request matches its description, so an idle session pays nothing」）。
**中间表示**：无自有 IR。两个入口各自沿用上游形态——`solidworks-automation` 是「脚本驱动：66 个 Python 模块」；`autocad-mcp-pro` 是「两个元工具 + 关键字搜索」。（来源：`README.md` 的表格，见本卡 §8）
**生成**：不生成代码（它是配置层，`README.md` 明写「It does not fork, patch or repackage either server」）。
**编排**：`cordis.patch.yml` 插入一行插件（`lib/index.js`）；插件加载时解析自身路径、确保钉子版本的上游已安装、然后注册两条 `dsh-mcp-client` 行（绝对路径）。
**执行**：MCP → 上游服务端 → COM。`lib/probe.py` 只查注册表 `ProgID`（`SldWorks.Application` / `AutoCAD.Application`），**不启动应用**。
**验证**：**本仓自身不提供几何验证**（`verify=none`）；验证能力来自上游 `solidworks-automation-skill` 的证据链。
**交付**：由上游输出 STEP / PDF（本仓只负责接通）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★★★ 工具表成本的实测三角（本卡最有价值的部分，逐字见 `README.md`）

| 配置 | `tools/list` 常驻成本 | 来源 |
|---|---:|---|
| AutoCAD MCP 直连（242 工具） | **83,732 tokens** | `README.md` 中的 token-cost 图注与正文 |
| SolidWorks MCP 直连（66 工具） | **23,411 tokens** | 同上 |
| 两者一起直连 | **107,143 tokens** | 同上 |
| **经本包（discovery 模式）** | **839 tokens** | 同上 |

口径写明：`cl100k_base` 分词、`tools/list` 线上字节。削减 **99.2%**。（来源：`README.md` 图注，见本卡 §8）

**对「为什么必须收敛工具面」的换算**：我方 **439 个工具**（2026-10-06 台账读数），按 SolidWorks 这 66 工具 = 23,411 tokens 的比例（约 355 tokens/工具）外推，直连形态会在 **10 万 tokens 量级**。⇒ 这不是优化项，是能不能用的分界。（来源：本卡 §8 的 token 表与 `docs/state/INDEX.md` 的工具数口径）

### 3.2 discovery 模式是上游自带的，不是本包发明的

`README.md` 的表格逐字：SolidWorks 侧用上游 `SW_MCP_DISCOVERY=search`，暴露 `sw_search_tools` / `sw_describe_tool` / `sw_call_tool` 三个元工具，66 个工具（50 `solidworks_*` + 14 `cadstudio_*` + 2 `design_*`）按需搜索；AutoCAD 侧用上游 `DISCOVERY_MODE=search`，暴露 `search_tools` / `call_tool`，242 工具按需搜索。
⇒ **我方上游已经具备 discovery 模式**，只是本仓默认没用。这是本轮最省事的一条改造线索。

### 3.3 版本钉子 + 校验日期（工程纪律样本）

`lib/upstream.json` 逐字钉死：AutoCAD `autocad-mcp-pro` **1.6.0**（`validated: 2026-10-23`）；SolidWorks 上游 repo 的 **commit `2750ac0892fa2854a4495a296ba238a2f2baa83d`**（`validated: 2026-10-29`），并在 `_comment` 里写明升级前必须复核「`SW_MCP_DISCOVERY=search` 仍暴露那三个元工具」。

### 3.4 失败必须响，不许静默

`cordis.patch.yml` 注释逐字：「Versions are pinned in `lib/upstream.json`. **If the upstream cannot be installed the plugin throws instead of registering rows that would fail silently.**」⇒ 与我方「misconfiguration fails loud」同一条原则的落地样本。

### 3.5 ProgID 探针而非目录探针

`lib/probe.py` 的 docstring 逐字：「The check is the registry **ProgID**, not the install directory: without a ProgID, COM automation cannot start the application, no matter where its files sit. It does not launch either application.」⇒ 判 COM 可用性的正确探针位置，比「文件在不在」强。

## 4. 运行条件与依赖

- DSH 或 Codex 宿主 + 已安装上游两个 MCP 服务端（由插件自动装一次）。
- Windows + **CAD 应用必须正在运行**，且 agent 与 CAD 应用同用户、同完整性级别（`README.md` 明写「the CAD application must be running, and the agent must run as the same Windows user and integrity level as the CAD app」）。
- `package.json` 声明 Node 侧依赖；`bin/dsh-sw-cad.mjs` 是入口。

## 5. 失败模式与已知坑

1. **它自己不做建模**：价值全在「接通 + 省 token + 钉版本」；上游能力就是它的能力上限。
2. **6 星、2 天前才建**：外部验证几乎为零，`test/plugin.test.mjs`（5793 B）是唯一测试。
3. **强依赖 Windows + 运行中的应用**：无 headless 替代（`README.md` 明写「there is no headless substitute for native `.dwg` / `.sldprt` output」）。
4. **discovery 模式下的检索质量未被评估**：只报了 token 成本，没报「搜出来的前 K 个准不准」。⇒ 我方已知痛点（BM25 前 5 命中率 40%）在它这里**没有被回答**。（来源：`README.md` 只列 token 成本、未列命中率，见本卡 §9）
5. **未运行**：本卡一切结论止于读码。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（三件，按性价比）**：
1. **★★★ 立刻打开上游自带的 discovery 模式**：`SW_MCP_DISCOVERY=search` 已在上游实现，我方默认直连。这是零开发成本的上下文削减，且本包已给出 23,411 → 474（SolidWorks 单侧）的实测口径。
2. **★★ 令牌预算当作硬指标写进文档**：它把「闲置成本」做成图表与表格并给口径（`cl100k_base`、`tools/list` 线上字节）。我方应把「工具表 tokens」纳入 `release_check`。
3. **★★ ProgID 探针 + 版本钉子 + 失败即抛**：三条都是低成本、可直接照搬的工程纪律。

**不能学**：
- 它是**配置层**，没有自有建模、没有自有验证；不能作为能力来源。
- **它没有解决 discovery 的检索质量**——照抄它的模式不等于解决我方 BM25 命中率问题。

## 7. 许可与红线

**MIT**（`LICENSE`，1080 B）。⇒ 代码可并入，保留版权声明即可。
⚠ 注意它**引用的上游是 AGPL 系与第三方**：`wzyn20051216/solidworks-automation-skill` 是 MIT（我方上游本体），`U-C4N/Autocad-MCP` 的许可本卡未核。若我方照搬，**只需取它自己的配置层代码**，不要经它引入未核许可的第三方。

## 8. 证据清单

- `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad\README.md`（token 三角表：83,732 / 23,411 / 107,143 / 839；discovery 模式的两个上游环境变量；「does not fork, patch or repackage」；「must be running / same integrity level」）
- `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad\cordis.patch.yml`（一行插件插入 + 「throws instead of registering rows that would fail silently」）
- `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad\lib\upstream.json`（`autocad-mcp-pro 1.6.0` / commit `2750ac0892fa2854a4495a296ba238a2f2baa83d` / `validated` 两个日期 / `_comment` 的复核要求）
- `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad\lib\probe.py`（ProgID 探针与其 docstring）
- `D:\swagent-2026Q4\repos\27painter__dsh-sw-cad\skills\autocad-mcp-pro\SKILL.md`（6972 B，本仓自撰的 AutoCAD 技能）
- 元数据：`gh api repos/27painter/dsh-sw-cad`（2026-11-02）；体积见 `D:\swagent-2026Q4\dup-report.md` §3「各仓库文本规模」表

## 9. 未确认事项

1. **未运行**：插件是否真能在 DSH 里装起两条 MCP 行、839 tokens 是否可复现，**均未实测**。
2. **`U-C4N/Autocad-MCP` 的许可**未核。
3. **discovery 的检索质量**（前 K 命中率）未评估，它也没评。
4. **上游 commit 钉在 2026-10-29**，晚于我仓台账的快照；该 commit 与本仓上游的差异未核。
5. 6 星意味着**几乎没有外部使用证据**，`test/plugin.test.mjs` 的实际覆盖率未看。

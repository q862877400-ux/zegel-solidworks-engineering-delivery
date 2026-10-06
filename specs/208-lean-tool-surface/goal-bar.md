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

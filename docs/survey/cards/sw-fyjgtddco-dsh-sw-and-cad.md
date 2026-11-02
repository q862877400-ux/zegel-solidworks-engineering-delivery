# fyjgtddco/DSH-SW-and-CAD

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=geometry-gate; deliver=drawing; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `fyjgtddco/DSH-SW-and-CAD` · https://github.com/fyjgtddco/DSH-SW-and-CAD |
| 许可 | **MIT**（`LICENSE` 首行 `MIT License`，`Copyright (c) 2025`）⇒ **可直接并入，保留版权声明** |
| 元数据 | stars **41** · created **2026-08-20** · pushed **2026-11-01** · 提交 **36** 个 · 开发跨度 **2026-08-19 → 2026-11-01（约 2.5 个月，单人持续）**（来源：`gh api repos/fyjgtddco/DSH-SW-and-CAD` + `git fetch --unshallow` 后 `git rev-list --count HEAD`，2026-11-02 实测）|
| 克隆 | `D:\swagent-2026Q4\repos\fyjgtddco__DSH-SW-and-CAD`（HEAD `b337e66`，2026-11-01 20:40:03 +0800；已 `--unshallow` 取全历史）|
| 证据等级 | **读码**（未运行；`engineering/tools` 下 73 个第一方 `.py`、约 3.7 MB 已抽样通读门控、物理、规则三块）|

## 1. 一句话定位

**这是本轮最反常的一个：一个单人、2.5 个月、36 个提交、MIT、41 星的 DeepSeek Harness「工程模式」预设，独立走到与我们同一套架构——把「材料 / 物理 / 领域（GB）三道质量防线」从提示词变成代码级硬门禁，并且已经写出 120 条中国国标规则（92 个不同标准号）——却几乎没人关注。**（来源：本卡 §8 的 git 与 stars 实测）

它 README 的第一句就把定位说死了：「**以「完成工图」为唯一目标：需求访谈 → 三维建模 → 有限元校核 → 出图交付，每一道关键闸门都写在 Python 代码里 —— 不通过，流程走不下去**」，并补一句「它不是一个"帮你写建模脚本的助手"。它是一个**会自己判断能不能交付**的机械设计工程师」（来源：`README.md` 开头两段）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：自然语言需求 → **需求访谈**（`ask_user.py`，42.7 KB 的交互提问模块）→ 模式选择（`mode_gate.py`，400.5 KB）→ 工作流推进（`workflow_gate.py`，345.7 KB）。

**中间表示**：**「房间」（room）+ 零件登记表**。`part_registry.py`（205.5 KB）按房间登记每个零件、材料、物理校核与领域校验凭据；`mode2_flow.py`（181.7 KB）跑第二阶段流程。⇒ 它不是「一次调用一个 API」，而是**按交付单元组织状态**。

**生成**：模型写 Python 脚本，经 `sw_bridge.py`（402 KB）在 SolidWorks 会话里执行；底层是 `swapi.py`（**767.5 KB，275 个 `def`/`class`**）——一个不硬编码路径与版本号、自动探测安装与模板的高层建模封装（来源：`engineering/tools/swapi.py` 的模块 docstring）。

**编排**：**门控驱动**（`orchestration=loop`）。三道强制点写死在 `defense_gate.py` 的 docstring 里：
- `sw_bridge.py run` → 产物落盘即校验防线 ①（材料）；
- `mode_gate.py room-end` → 下线即校验 ①②③（该房间）；
- `workflow_gate confirm-assembly` → 开总装前校验全部建模房间；
- `workflow_gate select(收尾)` → **宣告完成前校验全任务**。

**执行**：pywin32 COM；`conn_state.py`（76.8 KB）管连接状态，`sw_guard.py`（52.4 KB）管弹窗护栏——**与我们 `tools/sw_guard.py` 同名同题**。

**验证**（本卡最关键，也是它最值钱的部分）：**三道防线 + 凭据制**。

| 防线 | 要求产出的凭据 | 不通过的判据 |
|---|---|---|
| ① **材料防线** | 每个落盘 `.sldprt` 必须带 `<part>.material.json`，证明材料**不是缺失值、不是密度 1000（水）、不是跨族静默替代**；凭据由 `swapi.save()` 在 SolidWorks 进程内写就（那里才有真实密度） | 缺凭据 / 密度异常 / 跨族替代 |
| ② **物理防线** | 每个房间必须产出 `reports/<room>.physics.json`，综合 FEA gates 与 overall 判定 | `overall == FAIL` 即未通过 |
| ③ **领域防线（GB）** | 每个房间必须产出 `reports/<room>.domain.json`，由 `domain_validator` 按 `rules/<domain>_rules.json` 判定 | **存在 `CRITICAL` 违规即未通过** |

**绕行规则（我认为这条最值得抄）**：唯一合法绕行是 `DSH_DEFENSE_BYPASS=1` 或 `--force`，且**绕行必定留痕**到 `reports/defense_bypass.json`，便于事后审计——「**绝不静默**」（来源：`defense_gate.py` docstring 的「绕过」段）。

**交付**：`.sldprt` / 工程图 / FEA 报告 / 领域校验报告。仓内有真实产物目录：`engineering/output/传动机构/`、`结构件/`、`防腐处理/`（来源：`engineering/output/` 下 3 个子目录，实测列目录）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★★★ 领域规则包已经是「能判的」而不是「能读的」

`engineering/tools/physics/rules/` 下 **19 个 JSON、120 条规则、92 个不同标准号**；按严重度：`INFO` 77 / `BLOCKER` 18 / `CRITICAL` 15 / `WARNING` 10（来源：脚本统计 `rules/*.json` 的 `rules[]`，2026-11-02 实测，统计命令见 §8）。

12 个 `gb_*` 文件覆盖：`gb_base`(23 条) · `gb_materials`(23) · `gb_transmission`(14) · `gb_structural`(12) · `gb_material_verify`(8) · `gb_safety`(5) · `gb_fasteners`(4) · `gb_drafting`(3) · `gb_housing`(2) · `gb_springs`(2) · `gb_electrical`(1) · `gb_manufacturing`(1) · `gb_surface`(1)，另有 `gb_standards_registry.json`（注册表）。

每条形如：

```json
"rule_id": "GB_STRUCTURAL-001",
"standard_id": "GB 50017-2017",
"title": "钢结构设计标准",
"status": "现行(替代GB 50017-2003；部分强制性条文因GB 55006-2021实施而废止)",
"dsva_requirement": "材料设计强度、稳定性、局部屈曲、连接验算、允许长细比",
"severity": "BLOCKER",
"validation_method": "manual_review",
"requires_manual_review": true,
"source_url": "https://www.mohurd.gov.cn/gongkai/zc/wjk/art/2018/art_17339_237277.html"
```
（来源：`engineering/tools/physics/rules/gb_structural_rules.json` 的第 1 条）

**⇒ 三个可直接借的点**：① **`status` 字段带「被谁代替」**（GB 50017-2003 → GB 55006-2021 部分废止），这正是我们 A9「结论能指认标准条款」要的现行性；② **`severity` + `validation_method` + `requires_manual_review` 三元组**，把「必须机器判」与「必须人判」分开；③ **`source_url` 指到住建部/国家标准委原件**，不是二手。

### 3.2 ★★★ 三条「我们讨论过但还没落地」的原则，它已经写成代码

1. **「只写在提示词里、靠模型自觉」是问题，硬门禁是答案** —— `defense_gate.py` docstring 原话：「本模块把原先"只写在提示词里、靠模型自觉"的三道质量防线，变成【代码级、到点自动执行、不通过就不放行】的硬门禁」。
2. **先定义「什么是好」，再让 AI 生成** —— `domain_validator.py` docstring 原话：「DSVA 不是"插件"，而是约束生成器的"**宪法**"。在逻辑上，**必须先定义"什么是好（DSVA）"，才能让 AI 去"生成"**」。
3. **凭据制**：不是「检查通过」，而是**每个交付物必须有一份可复核的凭据文件**（`.material.json` / `.physics.json` / `.domain.json`）。⇒ 这比「跑一次检查」强一档：**凭据可以事后复核、可以进版本库、可以被别人验**。

### 3.3 ★★ 几何门禁不依赖 SolidWorks

`physics/geometry_gate.py` docstring 明写：「注意：本模块基于 **STEP 几何分析，不依赖外部 CAD 软件**」，检 5 项：`DESIGN_SPACE Violation`（超设计空间）/ `CONNECTIVITY`（单流形）/ `MIN_WALL_THICKNESS`（最小壁厚，近似）/ `MANIFOLD_CHECK`（非流形边/顶点）/ `INTERFACE_COMPLIANCE`（孔与安装面）。用 `shapely` 判，缺失时降级（`_HAS_SHAPLEY` 开关）。
⇒ 与 D 线的 `blussyya/solidworks-converters` 是同一个思路的两种实现：**验证不一定要开着 SolidWorks**。

### 3.4 ★★ 物理在环：不只调 FEA，自己有求解器

`physics/` 14 个模块：`fea_solver.py`(58.9 KB) · `load_case.py`(46 KB) · `simulation_report.py`(44.4 KB) · `domain_validator.py`(36.7 KB) · `material_db.py`(33.6 KB) · `fatigue.py`(20.2 KB) · `geometry_gate.py`(14.7 KB) · `feapy_solver.py`(13.5 KB) · `refine_rules.py`(12 KB) · `mesh_adapter.py`(10.3 KB) · `design_state.py`(5.2 KB)。
⇒ **有疲劳模块、有材料库、有网格适配、有网格细化规则**。这不是「包一层 Simulation」，是自建的一条链。

### 3.5 ★★ 回归测试的写法：锁死「类型库行号 + 官方语义引文」

42 个 `test_regression_*.py`，**不用 `unittest` 断言，用退出码**（`0 = 全部通过；1 = 有失败`）。以 `test_regression_cut_extrude_api.py` 为例，它把一个 15 小时事故钉成契约（docstring 逐字）：

- 锁定类型库**逐位参数个数**：「`IFeatureManager.FeatureCut3` L22427-22443 → **26 参**」「`FeatureCut4` L22446-22462 → **27 参**（= Cut3 + OptimizeGeometry）」「`FeatureExtrusion3` L22597-22611 → **23 参**（无任何切除位）」；
- **引官方 API Help 原文**定义语义：「`Flip`: True to remove material outside of the profile of the flip side to cut；`Dir`: True for Direction 1 to be opposite the default direction」——由此得出「**Flip = 切补集，Dir = 反转方向**」；
- 记录实测边界：「两环同草图**净距 0.328 mm → FeatureExtrusion3 返回 none/no_body**；净距 0.522 / 0.716 / 0.911 mm 全部 PASS」；
- 明写「全部假 COM，**不启动 SolidWorks**」（monkeypatch）。

⇒ **这就是我们铁律 4「签名三源互证」的另一种落地方式**：把行号与官方原文写进测试，防止有人「顺手改回去」。

### 3.6 ★ 工程纪律的旁证

- `docs/DSH卡死事故分析_job_output阻塞.md`（11.8 KB）—— 给一次 GUI 假死写了事故分析；
- `engineering/常见SW启动失败问题.md`（6.2 KB）—— 启动失败问题集；
- `engineering/docs/swapi-geometry-fixes.md`（21.7 KB）—— 几何修正记录；
- `install-job-wait-guard.ps1`、`patch-incompatible.ps1`、`restore-old-plugins.ps1`、`sync-to-dsh.ps1` —— 安装/回滚/同步一整套运维脚本；
- 7 个技能：`mode-selection`(32.6 KB) · `assembly-orchestration`(31.9 KB) · `solidworks-bridge`(19.3 KB) · `physics-in-loop` · `cad-workflow` · `sw-design` · `sw-to-cad`；（来源：本卡 §3.6 与 README 的技能清单）
- UI 插件 `dsh-engineering-ui` v1.2.0。

## 4. 运行条件与依赖

- **DeepSeek Harness 0.2.x**（Electron 桌面版或 `dsh web`），预设 ID `engineering`，`order: 4`（来源：`README.md` 的「项目」表）。
- Windows + 运行中的 SolidWorks；pywin32；`shapely`（几何门禁，可选降级）；Pillow + mss（截图）。
- 自带安装脚本（`install.ps1` / `install-0.2.0.ps1` / `install.sh`）与卸载/回滚脚本。

## 5. 失败模式与已知坑

1. **单人项目、无外部使用者**：41 星、0 个可核的第三方复现 ⇒ 我读到的都是**作者自己的现场**，没有第二个人验证过。（来源：`gh api` stars 读数，见 §8）
2. **未运行**：本卡未装 DSH 预设、未跑它的门禁，**「能跑通」只有作者 README 与 commit 信息**。
3. **规模本身是风险**：`swapi.py` 767.5 KB 单文件、`mode_gate.py` 400.5 KB 单文件 —— 单文件过大，二次开发与 review 成本高。
4. **GB 规则的深度未经我方核对**：120 条规则里 92 个标准号**我只是读了它们的字段，没有逐条核对条文是否与标准原文一致**（例如 `GB_STRUCTURAL-001` 引的「第4.3.2、4.4.1…条已被 GB 55006-2021 部分代替」我没有去住建部页面核）。⇒ **这是本卡最大的未知，也是并入前必须先做的核对。**（来源：本卡 §5 与 §9 的口径）
5. **`rules` 里混有非 GB 的领域规则**（`housing_rules` / `mold_rules` / `structural_rules` / `transmission_rules` 没有 `ruleset_id`），说明规则包成熟度不齐。
6. **交付物在仓内**：`engineering/output/` 下有真实产物（传动机构/结构件/防腐处理），但**没有对应的验收报告**可核，无法判断这些产物过了哪几道门。

### 5.5 宣传与关注度（2026-11-02 实测，回答「为什么只有 41 星」）

作者**确实在推**，但推给了错误的受众。GitHub 主页 bio 逐字「**大一新生，机械设计专业，代码可能有一点乱，见谅一下，感谢各位**」，followers **0**；主页填的 blog 就是他的 B 站空间（`space.bilibili.com/3537104783018949`，UID 3537104783018949，账号名 **Firefly-LOVE**，Lv5）。

该账号签名是「**想看崩铁爆料的关注我，必发**」，共 14 个视频，播放量按题材分裂：（来源：本卡 §5.5 的 `bili user-videos 3537104783018949 -n 50` 实测）

| 题材 | 代表 | 播放 |
|---|---|---:|
| 星铁爆料 / 整活 | 星铁冷门角色暴打来古士 | **141,277** |
| 星铁整活 | 星期日知道会杀了我的 | **74,809** |
| AI × 机械 | **AI机械实验室 EP01（BV1tjpn6aE3N，5:18）** | **874**（14 赞 / 4 币 / 28 收藏）|
| AI × 机械 | **AI机械实验室 EP02（BV1STWw6UEna）** | **39**（3 赞）|

⇒ **粉丝盘是游戏区来的（单条 14 万播放），工程内容掉到两位数**——受众错配，不是没宣传。
且 14 个视频里**没有一条直接讲这个 SolidWorks 工程模式仓库**；EP01 讲「一句话指挥机械臂」，而本仓描述正是用「请帮我完成一个**机械臂**」举例，故 EP01 很可能就是该项目演示，**但简介为空、无字幕，未确认**。（来源：同上，逐条比对标题得出）

（实测命令：`bili user-videos 3537104783018949 -n 50` · `bili video BV1tjpn6aE3N`；★ `bili` 在 GBK 控制台会崩，须设 `PYTHONIOENCODING=utf-8`，见报告 §12.7）

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（按价值排序，全部是「机制 + 现成资产」）**：

1. **★★★ 120 条 GB 规则的骨架与字段设计**：`standard_id` / `status`（带废止链）/ `severity` / `validation_method` / `requires_manual_review` / `source_url`。**这直接就是我们规则包该有的形状**，而且 MIT 可并入（并入前必须逐条核条文，见 §5.4）。（来源：本卡 §3.1 的规则统计，命令见 §8）
2. **★★★ 三道防线的凭据制**：交付物必须带 `.material.json` / `.physics.json` / `.domain.json`，而不是「检查过一次」。**这解我们现在「验证结论只活在会话里」的问题。**
3. **★★★ 绕行必须留痕**（`reports/defense_bypass.json`）：把「例外」变成一等公民并审计。我们现在没有这个。
4. **★★ 「先定义什么是好，再让 AI 生成」的判定器先行**：与 charter 的「先验收后能力」同一条，但它已经写成 `domain_validator` 的执行引擎。
5. **★★ 几何门禁不依赖 SolidWorks**（STEP + shapely，5 项检查），与 D 线的离线路线可互补。
6. **★★ 回归测试锁类型库行号 + 官方原文**：比我们的「签名三源互证」更防回退，因为**写进了会失败的测试**。
7. **★ `sw_guard.py` / `conn_state.py`**：弹窗护栏与连接状态，与本仓同题，可对照。

**不能学 / 需谨慎**：
- **单文件过大**（767 KB / 400 KB）：并入时应拆模块，不要照搬结构。（来源：本卡 §2 的各模块大小实测）
- **无第三方验证**：它的「已完成」只有作者自述与 commit 信息，不能当验证标准的参照。
- **不要整仓照搬**：它是「DSH 预设」形态（profiles/skills/plugins），与我方「MCP 工具 + 脚本」形态不同，只取其中的**判据与规则**。

## 7. 许可与红线

**MIT**（`LICENSE`，首行 `MIT License`；`Copyright (c) 2025`）⇒ 代码与规则文件均可并入，保留版权声明与许可全文即可。
⚠ 它引用的是**中国国家标准文本的描述**（不是标准原文）。标准原文有版权，**引用条款号与要点**可以，**整段抄标准正文**不行；并入规则包时应保留 `source_url` 指向官方发布页。

## 8. 证据清单

- `D:\swagent-2026Q4\repos\fyjgtddco__DSH-SW-and-CAD\README.md`（开头「以完成工图为唯一目标」两段；「项目」表：DSH 0.2.x / preset `engineering` / 7 技能 / 12 核心脚本 + 14 物理模块 / 30 Python + 12 插件测试 / MIT）
- `...\engineering\tools\defense_gate.py`（模块 docstring：三大防线、强制点、绕行留痕、CLI 三条）
- `...\engineering\tools\physics\domain_validator.py`（docstring：「DSVA 是约束生成器的宪法」「必须先定义什么是好」；支持 4 领域）
- `...\engineering\tools\physics\geometry_gate.py`（docstring：5 项检查 + 「不依赖外部 CAD 软件」；`_HAS_SHAPLEY` 降级开关）
- `...\engineering\tools\physics\rules\gb_structural_rules.json`（第 1 条完整字段与 `source_url`）
- `...\engineering\tools\test_regression_cut_extrude_api.py`（docstring：15 小时事故、类型库行号 22427-22443 / 22446-22462 / 22597-22611、官方 Flip/Dir 原文、净距 0.328 边界、假 COM）
- `...\engineering\tools\swapi.py`（模块 docstring：跨电脑/跨版本自动探测；275 个 `def`/`class`）
- 统计命令（2026-11-02 实测）：`git fetch --unshallow` 后 `git rev-list --count HEAD` → **36**；`git log --reverse --format="%ci"` 首条 **2026-08-19**、`git log --format="%ci"` 首条 **2026-11-01**；`rules/*.json` 统计 → 19 文件 / 120 条 / 92 个 standard_id / 严重度 INFO 77·BLOCKER 18·CRITICAL 15·WARNING 10；`engineering/tools` 下第一方 `.py` 73 个、约 3.7 MB；42 个 `test_regression_*.py`

## 9. 未确认事项

1. **一步都没跑**：门禁是否真能拦住、凭据是否真被写出来、FEA 是否真出结果，**全部未实测**。
2. **120 条 GB 规则是否逐条与标准原文一致**：只读字段未核条文（§5.4），这是并入前**必须**做的一步。（来源：本卡 §9 未确认事项）
3. **`status` 里的废止链是否准确**（如 GB 50017-2017 被 GB 55006-2021 部分代替的范围）：未去住建部页面核。
4. **`physics/fea_solver.py` 是自己实现的求解器还是包了 feapy/simulation**：只看了文件名与大小，未读实现。
5. **41 星的来源**：未查是否有平台推荐；`README` 里有 `share.feijipan.com` 的长流程产物链接（外部网盘，未下载）。
6. **与 `GaoFei-Max` / `LU0220` 的 2 个共享文件**（`build_cup.py` / `build_plate.py`，见复核总账第 9 条）说明它们 shared examples；**这三家是否有共同来源**未确认。

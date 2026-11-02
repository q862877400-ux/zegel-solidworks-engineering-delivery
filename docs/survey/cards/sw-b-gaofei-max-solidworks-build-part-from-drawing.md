# GaoFei-Max/solidworks-build-part-from-drawing

<!-- survey: class=A; repr=feature-tree; orchestration=human-approve; verify=visual; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `GaoFei-Max/solidworks-build-part-from-drawing` · https://github.com/GaoFei-Max/solidworks-build-part-from-drawing |
| 许可 | **无 LICENSE**（`gh api repos/...` 返回 `license = null`；仓内 `git ls-files` 无 `LICEN[SC]E` 文件）⇒ **全版权保留，只读思想，不抄文本** |
| 元数据 | stars **15** · 创建 2026-08-05T04:22:31Z · 最近推送 2026-08-05T04:35:23Z · 语言 null · 仓库 344 KB（来源：`gh api repos/GaoFei-Max/solidworks-build-part-from-drawing`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\GaoFei-Max__solidworks-build-part-from-drawing`（`--depth 1` 默认落到 `main`；**真正的内容在 `master`**，已 `git switch -c master FETCH_HEAD`，master HEAD `cf09fb9e`，2026-08-05 12:31:55 +0800） |
| 证据等级 | **读码**（未跑：这是一份纯提示词包，仓内没有任何可执行文件） |

## 1. 一句话定位

**一份「先读图、再建模」的两阶段提示词纪律，零脚本**：把「不许按像素猜尺寸」写成可检查的尺寸账本 + 特征计划 + 一次确定性构建；资料真在仓里，但装在**非默认分支**上，按默认方式克隆只会拿到两行 README。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：JPG/PNG 机械零件图（正交视图、剖视、局部放大、辅助视图均可），或一张带尺寸的简单图。`SKILL.md:3` 的 `description` 把「每个数字模型尺寸必须来自明确标注或记录过的计算，绝不许按像素估」写成触发条件的一部分。

**中间表示**：**两层文字中间物**。
1. **尺寸账本**（`SKILL.md:24-27` 规定表头）：`ID | Feature or relation | Value | Unit | Tolerance | Drawing location | Authority | Model use | Status`。
2. **特征计划**（`SKILL.md:29`）：冻结原点、基准、**期望特征数**、**期望实体数**。

任何计算参数必须写成「以账本 ID 为操作数」的公式（`SKILL.md:27`）。

**生成**：不生成代码文件到仓里——由 agent 在运行时生成「一个 builder」，且 `SKILL.md:44` 明确「不要在一次重试里改尺寸」。

**编排**：`human-approve`。四阶段 A→D 有硬停点：`SKILL.md:28` 要求「在必需几何未解之前不要启动 SolidWorks」；`SKILL.md:37-38` 要求先声明「可见建模还是后台」，且「SolidWorks 没有非零主窗口句柄时不许声称可见建模」。

**执行**：`SKILL.md:35` 把执行机制**外派**给另一个技能 `$solidworks-build-mechanical-models`——该技能**不在此仓**。

**验证**：`visual`（人工/模型看图），清单在 `SKILL.md:54-60`：干净强重建、实体数、原生可编辑特征无失败/压缩/悬挂、视图与包络/孔/深度/阵列/边处理/对称、`.SLDPRT` 非空、预览已检、日志完整、可见录制时 MP4 已验证。**没有任何自动化几何断言**——判据全靠 agent 自己核对账本。

**交付**：`.SLDPRT` + 预览 + 尺寸账本 + 特征计划 + 构建/验证日志 + builder 源码（+ 录制时 MP4）。★ 交付物里**没有 STEP**，也没有任何可机读的验收文件。

## 3. 技术方案要点（可迁移的机制）

### 3.1 「图纸权威」四条禁令（可直接抄成我们的 prompt 规则）

`SKILL.md:10-16`：

1. 只用明确标注、备注、表格、标准标注，或**完全由它们推导出来的算式**；
2. 绝不按像素缩放、按比例描摹、或凭空补缺失值；
3. 只允许推断**无歧义**的关系：同心、对称、相切、平行、垂直、重复等距；
4. 遇到不可读 / 缺失 / 矛盾 / 含糊的几何，**在建模前停下**。
5. 保留原图，在隔离输出目录工作。

⇒ 这四条与我们 `docs/acceptance-criteria.md` 的「A9 结论能指认标准条款」是同一路思想，但它是**写在触发描述里**，不是写在文档里给人看。

### 3.2 账本的 9 列里，最值钱的是 `Authority` 与 `Status`

`SKILL.md:24` 把每个尺寸的**权威来源**（标注 / 计算 / 推断）与**状态**做成同一行的两列。对照我们自己的痛点：`docs/state/facts/` 里「字段描述 ≠ 运行时行为」这条，本质就是缺一列 `Authority`。同一作者另一仓 `solidworks-draw-part` 的 `references/acceptance.md` 把这套延用。

### 3.3 「一次构建」而不是「反复调」

`SKILL.md:44`：从冻结账本生成**一个** builder，重试时不得改写尺寸。⇒ 把「不确定性」全部前移到 Phase A，避免建模期反复改参导致的特征树污染。这与我们「事务式建模」的诉求方向一致，但用的是**流程约束**而非事务机制。

### 3.4 可见建模的判据写成可检验条件

`SKILL.md:39`：「SolidWorks 没有非零主窗口句柄时，不许声称可见建模」。这是一条能被机器判定的诚实性约束（`MainWindowHandle -ne 0`），比「用户能看到过程」这种话强得多。

### 3.5 同作者兄弟仓（同族，一并判断）

| 仓 | stars | 内容 | 分支陷阱 |
|---|---:|---|---|
| `solidworks-draw-part` | 7 | `master` 上有 **C# 16181 字节 + PowerShell 6072 字节**真脚本，走 `Create3rdAngleViews2` / `CreateSectionViewAt5` / `InsertModelAnnotations3` / `AutoDimension` | 同样 main 只有 157 字节 README（来源：`git -c core.quotepath=false ls-tree -r --long FETCH_HEAD`） |
| `SolidWorks_Mechanical_Design_Assembly_Skill` | 5 | 5 份 md / 0 脚本；装配纪律写得最严：「仅写入位置变换或固定全部零件 ≠ 建立装配配合」，「干涉是报告项不是交付阻断项」 | main 即内容，无陷阱 |
| `DSH_SW` | 9 | 有真脚本，见另一张卡 `sw-b-gaofei-max-dsh-sw.md` | —— |

★ `solidworks-draw-part` 是**本线里少数真正可执行的出图脚本**：`invoke-part-drawing.ps1` 先查进程状态，`$state.hidden.Count -gt 0` 或 `visible.Count -gt 1` 直接抛错（COM 绑定的单实例前提），再校验模板 / interop DLL / `csc.exe` 三件存在，才用 `csc.exe` 现编现跑 C#。这套「先证明环境单一，再动手」的写法比多数包严谨。

## 4. 运行条件与依赖

- 真机 **SolidWorks 2022**（`SKILL.md:3` 明写 `.SLDPRT` 为 2022 版）+ Windows + Codex（`agents/openai.yaml` 是 Codex 技能描述格式）。
- **硬依赖一个仓外技能**：`SKILL.md:35` 的 `$solidworks-build-mechanical-models`——不在此仓，也不在任何同作者仓的 `git ls-files` 里。
- 兄弟仓 `solidworks-draw-part` 的脚本额外要求：`gb_a3.drwdot` 模板、`SolidWorks.Interop.sldworks.dll` + `swconst.dll`、`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe`（默认值见 `invoke-part-drawing.ps1:8-10`）。
- 无测试、无 fixture、无样例图纸（`测试工程图.png` 是作者本机截图，不是可复算的测试集）。

## 5. 失败模式与已知坑

**本卡实读发现的缺陷**：

1. **默认分支是空壳，真内容在 `master`**。`main` 只有 `README.md` 153 字节；`master` 才有 `SKILL.md` 4224 字节 + `agents/` + 3 份 references + 3 张 PNG（来源：`git ls-tree -r --long HEAD` 与 `git ls-tree -r --long FETCH_HEAD` 对照）。⇒ 这是本线**最容易踩的一个坑**：`git clone` 完看不到任何东西就下「空仓」结论。同一套坑在 `solidworks-draw-part` 重复一次。
2. **默认分支的空壳 README 还自带失效指引**：「操作流程见文件夹图片」——`main` 上**没有任何图片**。
3. **零可执行文件**：`git ls-files` 在 master 上只有 3 份 md + 1 份 yaml + 3 张 PNG（来源：同上 `ls-tree`）。所谓「Codex 读工程图 → 调 SolidWorks API 建模」全部由模型现场生成代码，包本身不提供任何 API 调用实现。
4. **外部技能依赖断链**：`$solidworks-build-mechanical-models` 在公开 GitHub 上**查不到同名仓**，且作者自己的 `DSH_SW`/`draw-part` 都不用这个名字 ⇒ 这份技能是残缺的，单独安装跑不通。
5. **验证全靠模型自述**：`SKILL.md:54` 的「Reconcile every model parameter with the ledger」没有工具支撑，无法与「模型自己说它对过了」区分。
6. **无许可**：同族的 4 个仓全部无 LICENSE（来源：`gh api` 逐个 `license=null`）。

## 6. 对我方目标的可用处（机制层面）

**能学（机制）**：

- **图纸权威四禁令 + 9 列账本**：可直接改写进我们的图纸 intake 规则；`Authority` 列是补我们「字段描述 ≠ 运行时行为」那个缺口的现成模板。
- **「期望特征数 / 期望实体数」在建模前冻结**：与 `delancy827` 的「先抓指纹再断言」是同一件事的两端，两条合起来正好构成「事前预期 + 事后断言」。
- **可见建模的机器可判定条件**（主窗口句柄非零）：诚实性约束的写法样板。
- **`invoke-part-drawing.ps1` 的「环境单一性前置检查」**：进程状态（隐藏/多实例）→ 模板/interop/csc 三件 → 才编译执行。这是 COM 自动化的启动纪律，与我们 `tools/guard_run.py` 的护栏思想一致。
- **一次构建、重试不改参**：把不确定性前移的流程约束。

**不能学**：

- **零脚本**：本线里最纯粹的「提示词包」，对我们「工具化」目标只有规则价值。
- **外部技能断链**：依赖一个不存在的技能，等于不可独立复现。
- **验证没有工具**：`visual` 级，达不到我们 `numeric` 的要求。
- **分支陷阱**：虽是工程失误，但提醒我们「发布前检查默认分支」这件事该进清单。
- **无许可**：只读思想，连引用文本都要改写。

## 7. 许可与红线

**无 LICENSE**（`gh api` `license = null`；仓内无 LICENSE 文件）⇒ 依本仓铁律 6 与 A6：**只读思想，不抄代码、不抄文本**。本卡 §3 只提炼机制，未复制成段文字。

同族 4 仓全部同理：`solidworks-draw-part`、`SolidWorks_Mechanical_Design_Assembly_Skill`、`DSH_SW`、本仓——`gh api` 逐个返回 `license = null`（来源：2026-11-02 逐个 `gh api repos/<owner>/<repo>`）。★ 其中 `DSH_SW` 的 `swapi.py`/`sw_bridge.py` 已被 `LU0220-code-pro-max` 逐字节复制（见 `sw-b-gaofei-max-dsh-sw.md`），无许可复制在许可上是不成立的。

## 8. 证据清单

- 元数据：`gh api repos/GaoFei-Max/solidworks-build-part-from-drawing`（2026-11-02；`license=null`、`default_branch=main`、`size=344`）
- 分支对照：`git ls-tree -r --long HEAD`（main：只有 `README.md` 153 字节）vs `git ls-tree -r --long FETCH_HEAD`（master：`SKILL.md` 4224 / `agents/openai.yaml` 273 / `references/drawing-interpretation.md` 3003 / `references/feature-planning.md` 2906 / `references/validation.md` 2184 / 3 张 PNG）
- `solidworks-build-part-from-drawing/SKILL.md:3`（description 里的「绝不许按像素估」）· `:10-16`（图纸权威五条）· `:24-27`（9 列账本表头）· `:28`（未解不得启动）· `:29`（冻结特征计划）· `:35`（外派 `$solidworks-build-mechanical-models`）· `:37-39`（可见建模与主窗口句柄判据）· `:44`（一次构建不改参）· `:50`（特征选择偏好）· `:54-60`（验证清单）
- 兄弟仓：`solidworks-draw-part/SKILL.md:27-30`（launcher 调用）· `solidworks-draw-part/scripts/invoke-part-drawing.ps1:1-13`（参数默认值）· `:52-58`（隐藏/多实例即抛错）· `solidworks-draw-part/scripts/SolidWorksPartDrawing.cs`（16181 字节，`Create3rdAngleViews2`/`CreateSectionViewAt5`/`InsertModelAnnotations3`/`AutoDimension`）
- `SolidWorks_Mechanical_Design_Assembly_Skill/solidworks-design-assemblies/SKILL.md`（装配纪律；「干涉是报告项不是交付阻断项」）
- 成本读数：`D:\swagent-2026Q4\token-cost.md`（入口 `SKILL.md` 849 tokens，`cl100k_base`，2026-11-02）

## 9. 未确认事项

1. **`$solidworks-build-mechanical-models` 是否存在**：在 GitHub 上按名检索**查不到**公开仓；作者其余 3 仓也无此目录 ⇒ 这份技能的单机可用性**未确认**，很可能是私有技能集的一块。
2. `main` 与 `master` 哪个是作者本意：`main` 建得晚（内容 153 字节），`master` 是首提交（2026-08-05 12:31）。**未确认**是否打算合并；本卡按「master 是内容」记。
3. 仓里 3 张 PNG（`Codex调用方法.png` / `测试工程图.png` / `配置skill的本地电脑目录…png`）是流程截图还是样例图纸——**未逐张读**（本卡未做 OCR）。
4. `solidworks-draw-part` 的 `AutoDimension(1, 1, -1, 1, -1)` 与本仓 `docs/recon-206/pre-code-conflict-lookup.md` 里 `AutoDimension2` 的 mark 语义冲突线索**未核对**（两者不是同一成员，需查官方页再比）。
5. 「Codex 读工程图」这条在 Codex 上实际触发率如何（多模态输入是否真的能吃 JPG 尺寸）——**未实测**。
6. `SolidWorks_Mechanical_Design_Assembly_Skill` 的 `交流v.png` 在克隆里是 0 字节——是 LFS 指针缺失还是作者提交了空文件，**未确认**。

# 示教器（Teach Mode）：把「人的示范」变成项目能吃的资产

**状态**：草案（2026-10-26 立项，业主提出）
**一句话**：用户/业主示范一次操作，系统把它落成**可执行的配方 + 可验证的判据**，
然后 ① 这个 agent 照做 ② 别人可以提交它来纠错/扩展 ③ 每个人的习惯成为他自己的配置。

---

## 1. 为什么要有它（业主原话）

> 我们这个示教工具完全也可以做进我们的项目里面……
> 不仅提供一个给大家使用的工具，还给大家提供一个**创造的工具**，就像游戏的 MOD 编辑器一样。
>
> 我们设计的功能可能没有覆盖一些边边角角……那我们给这么一个工具，别人就可以去完善。
>
> 不同的人建模画图或者做装配，有不同的习惯……这个示教器就可以让他把一些习惯变成数据，
> 然后给他的 agent 用，让他的 agent 去调整。我们这个项目的实现方式就可以更加**私人化**。
>
> 甚至这个东西可能会变成一个**社区**，不断完善我们这个项目，做一个**根基之一**。

**三条动机，互相独立，都要满足**：

| # | 动机 | 对应层（见 §3） |
|---|---|---|
| M1 | 我们的能力覆盖不到边角 ⇒ 让用户自己补 | L2 配方 → L5 社区 |
| M2 | 用户的习惯/标准不同 ⇒ 让习惯变成数据 | L4 个人化档案 |
| M3 | 用户发现我们做错了 ⇒ 让"正确流程"可示范、可提交 | L2/L5 + 判据 |

---

## 2. 为什么不能只回放动作（设计红线）

**示范不总是对的**，而且**动作不等于意图**：
- 业主自己说：「我可能会有反复检查，可能会有错误了之后再删除，然后再重新做。」
- 同一个结果可以有很多动作路径（先选面 vs 先画草图）。
- UI 动作**绑死版本与语言**（SolidWorks 2026 中文界面 ≠ 英文界面）。

⇒ 红线：**配方记录「意图 + 判据」，不记录「逐帧回放」**。
  动作序列只作为**证据**保留，不作为执行依据。

---

## 3. 五层设计（L1 已实现，其余待建）

```
L1 捕获   PSR 步骤 + ffmpeg 录屏 + 模型语义快照 + 弹窗护栏     ← 已实现（tools/demo_capture.py）
L2 提炼   捕获 → recipe.yaml（意图 + 步骤 + 判据）              ← 待建
L3 执行   recipe → ToolSpec 调用序列（能走 API 的走 API）        ← 待建
L4 个人化 profiles/<id>/habits.yaml 注入 agent 默认值            ← 待建
L5 社区   recipe 作为可提交资产（带 provenance + CI 判据）        ← 待建
```

### L1 捕获（已实现，真机验证过）

```bash
python -B tools/demo_capture.py --start     # PSR + ffmpeg + 记开始墙钟
python -B tools/demo_capture.py --stop      # 停两者 + 模型快照 + 报告
python -B tools/demo_capture.py --frame 17:09:44   # 按步骤时间抽帧
```

产物（`output/teach/<会话号>/`）：`psr.zip` · `screen.mp4` · `model.json` ·
`model.md` · `steps.md` · `REPORT.md`。

**第 3 层「模型语义快照」是核心**：它把
「特征树 / 每张草图的点坐标 / 每条关系与尺寸（**含参照实体**）」读成结构化数据。
实测（业主的 4 孔案例）读出来是：

```
HORIZPOINTS  点(90,-10) ↔ 点(10,-10)
VERPOINTS    点(90,-10) ↔ 点(90,-50)
HORIZPOINTS  点(90,-50) ↔ 点(10,-50)
VERPOINTS    点(10,-50) ↔ 点(10,-10)
DISTANCE = 10.0 mm  点(10,-10) ↔ 线[(0,0)→(0,-60)]        距左边
DISTANCE = 10.0 mm  点(10,-10) ↔ 线[(100,0)→(0,0)]        距上边
DISTANCE = 10.0 mm  点(90,-10) ↔ 线[(100,-60)→(100,0)]    距右边
DISTANCE = 10.0 mm  点(90,-50) ↔ 线[(0,-60)→(100,-60)]    距下边
```

⇒ 「4 点用 4 条关系 + 4 个尺寸做到全定义」这件事**机器读得懂**，不需要靠人复述。

### L2 提炼：`recipe.yaml`（草案格式）

```yaml
id: hole-4x-m6-gb-with-relations
title: 一块板上 4 个 M6 间隙孔（一个孔特征 + 关系 + 最少尺寸）
provenance:
  demonstrated_by: owner          # 谁示范
  demonstrated_at: 2026-10-26
  capture: output/teach/20261025-170900/    # L1 产物目录
  sw_version: "2026 SP4.1"
intent: |
  4 个孔位放进**一个**孔特征；用水平/竖直关系把 4 个点组成矩形（省一半尺寸）；
  只用 4 个距离尺寸（分别到左/上/右/下边）就做到全定义；孔标准用 GB。
inputs:
  plate: {width_mm: 100, height_mm: 60, thickness_mm: 20}
  hole:  {standard: GB, fastener: 螺钉间隙, size: M6, through: true}
steps:
  - do: 建板（草图矩形 + 拉伸）
  - do: 建异型孔（GB/螺钉间隙/M6），孔位草图里放 4 个点
  - do: 加 2 条 HORIZPOINTS + 2 条 VERPOINTS 关系
  - do: 加 4 个 DISTANCE 尺寸（10/10/10/10，分别到四条边）
assertions:                        # ← 判据，不是动作
  - feature_count: {HoleWzd: 1}
  - sketch_constrained: {owner: HoleWzd, status: 3}
  - hole: {standard: GB, fastener: 螺钉间隙, size: M6}
  - cylinders: 4
```

★ 关键：`assertions` 是**冻结的验收判据**；`steps` 只是怎么做到的提示。
  换一个人用别的动作达到同样 assertions，配方**依然成立**。

### L4 个人化档案：`habits.yaml`（草案）

```yaml
# 只写「默认值」与「偏好」，不写能力
hole_standard: GB              # 或 ISO
dimension_style: to_edge       # 或 to_edge_and_spacing
prefer_pattern_over_points: true
naming: {hole_prefix: "M6 间隙孔"}
```

⇒ 生成器读它来决定**默认参数**；用户不用每次重复说明。

---

## 4. 与现有资产怎么接（不另起一套）

| 现有资产 | 示教器与它的关系 |
|---|---|
| `capabilities.yaml` | L2 生成的 recipe 可**提升**为一条能力（`level: stitched/verified` 照规矩） |
| `ToolSpec`（`mcp-server/tool_specs_*.py`） | L3 把 `steps` 映射成 ToolSpec 调用序列 |
| E1–E7 判据（`scripts/engineering/acceptance/`） | `assertions` 尽量**调用既有判定器**，不新造判据 |
| `docs/known-facts.md` | 示范里学到的机制性结论进事实表 |
| `docs/human-acceptance-protocol.md` | 示教**就是**四步协议的第 2 步（准备）+ 示范 |
| `output/`（gitignore） | L1 原始捕获不入库；入库的只有 L2 的 `recipe.yaml` |

---

## 5. 社区路径（L5）

- recipe 入库位置（建议）：`teach/recipes/<id>/recipe.yaml` + `notes.md`（人写的取舍说明）
- 提交 = 普通 PR；CI 用 `assertions` 在样例件上跑一遍 ⇒ **配方必须自证**
- 冲突处理：两个 recipe 对同一意图给不同做法 ⇒ 都保留，`habits.yaml` 选一个默认
- 许可：贡献的 recipe 按仓库许可（MIT）；**禁止**把客户数据/图纸带进 recipe

---

## 6. 风险与边界（诚实清单）

| 风险 | 说明 | 缓解 |
|---|---|---|
| 示范本身是错的 | 用户示范了不合规做法 | `assertions` 必须过；且 recipe 只是**候选**，进能力清单要人批准 |
| UI 绑定版本 | PSR 步骤里的控件名随版本/语言变 | 配方**执行**只走 API；UI 步骤仅作证据 |
| 快照读不全 | 本机实测：读不到某些属性 | 已踩过的写进事实表（`IsCylinder` 是属性、`GetSystemValue2` 要配置名） |
| 隐私 | 示范可能含客户图纸 | L1 原始捕获入 `output/`（不入库）；recipe 只留结构与参数 |
| 复杂度失控 | 五层一次做完做不完 | **先做 L1→L2 的一根垂直切片**：业主这一个 4 孔案例走通全链 |

---

## 7. 第一个验收判据（这根切片做完即算立住）

> 拿业主 2026-10-26 的 4 孔示范（L1 已捕获）生成 `recipe.yaml`，
> 然后用**纯 API** 按 recipe 重建，得到：
> `HoleWzd = 1` · 孔内草图 `status = 3` · `standard = GB` · `圆柱面 = 4`。

★ 这条判据能跑 ⇒ 示教器不是 demo，是**生产通路**。
★ 跑不通时，缺口就是真实缺口（写进报告，不编）。


---

## 8. 架构纠正（业主 2026-10-26，**覆盖前面 L2/L3/L4 的设计**）

业主原话：

> 你不要把我们这个工具搞得越来越复杂了，它就是一个动作的记录，而且要记录得特别特别全，
> 各种场景都能记录，而**提炼这一步就交给使用这个工具的 agent 进行**，
> 你千万不要把我们这个示教器越搞越复杂。

⇒ 作废前面 §3 里的 L2（提炼配方）、L3（执行）、L4（个人化档案）作为**工具的一部分**。
   工具只剩一件事：**记录**。提炼、推断、复现都由使用工具的 agent 自己写代码完成。

### 现在的形态（两个命令）

`ash
python -B tools/teach.py capture --start / --stop    # 录界面操作：PSR 步骤 + 录屏 + 弹窗 + 模型快照
python -B tools/teach.py record [--out 目录]         # 把当前文档状态原样导出（JSON + 人读 md）
`

### 记录器覆盖范围（scripts/sw_model_snapshot.py，全部真机验证）

| 场景 | 记录内容 | 验证 |
|---|---|---|
| 零件 | 递归特征树（含子特征、owner、depth） | ✅ 21 项 |
| 草图 | 点 / 线段（直线·弧·椭圆·样条）/ **构造线标记** / 端点 | ✅ 草图3 记到 5 段含 1 条构造线 |
| 关系与尺寸 | 类型（swConstraintType_e）+ 数值 + **参照实体**（点/线段/边/面/顶点） | ✅ 「点 + 草图线段 = 10.0mm」×4 |
| 实体统计 | 面数 / 圆柱面数 | ✅ 面 10 · 圆柱面 4 |
| 装配 | 组件（名称/路径/压缩/16 元变换矩阵） | ✅ 2 组件 |
| 配合 | 类型（swMateType_e）/ 对齐（swMateAlign_e）/ 参与实体 / 参照组件 | ✅ DISTANCE · ALIGNED · 实体=面 |
| 图样 | 视图清单 | 已实现（本轮未真机验） |
| 自定义属性 | 名称 → 值 | 已实现（本轮未真机验） |

### 已删除（保持单一职责）

scripts/sw_recipe.py · scripts/sw_habits.py · scripts/sw_recipe_exec.py ·
	ests/test_teach_recipe_habits.py —— 那是「工具替 agent 干活」，与上面的纠正相反。

### 全场景真机验收：**21 项判据全过**（output/verify_all_scenes.py）

`
零件  特征树(递归) 33 项 · 草图 4 张（含孔内）· 构造线 1 条
      点到边/线段尺寸 4 条（如实记录参照实体：草图点 + 草图线段）
      实体 面10/圆柱面4 · 自定义属性 28 条 · 求解状态 [3,3,3,3]
装配  组件 2 · 变换矩阵 16 元 · 配合 1 条（DISTANCE / ALIGNED / MateDistanceDim）
      配合参与实体 2 个（面, 面）· 参照组件 [参考案例-1, 参考案例-2]
图样  视图 4 个（DrSheet + AbsoluteView×3）· 特征 38 项 · 图样草图 8 张
外部引用 3 条（STEP AP214 导入件）· 每条含 特征 / 被引对象 / 数据类型 / 状态
`

### 已知限制（如实）

- **外部引用**：已用 IModelDocExtension.ListExternalFileReferences2(9 个 out) 记录
  组件/派生件级引用（实测 3 条 STEP 导入件）。★ 但「**草图里**引用另一个零件的边/点」
  这种 in-context 草图引用**尚未单独造样本验证**（事实 590 已注明边界）。
- 图样只记**视图与草图几何**，未记录视图的**尺寸标注/形位公差**内容。
- 界面动作靠 PSR（微软已弃用但本机可用）；它能记动作与控件名，
  记不到输入框里的**具体数值**（数值靠模型快照还原）。

### 已消除的三条旧限制（本轮验证）

| 旧限制 | 现状 |
|---|---|
| 图样/自定义属性未验证 | ✅ 已验证（见上） |
| 配合只取到 1 个实体 | ✅ 已修：MateEntity 是 **0 基**，现在取到 2 个 |
| 配合特征类型认不出 | ✅ 已修：类型名是 MateDistanceDim（按种类命名） |

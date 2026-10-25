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

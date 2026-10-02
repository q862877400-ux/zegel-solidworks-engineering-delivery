# 24 小时计划 v2 · 收敛报告（`plan-24h-v2-convergence.md`）

> 状态与进度**不写这里**（宪法：那在 `ROADMAP.md` §一 / `capabilities.yaml` / `docs/metrics.md`）。
> ★ 本文件的交付物是：★ **说清这一轮 24h 计划做成了什么 / 证据在哪 / 没做成什么 / 目标口径对不对** ——
> ★ 而**不靠回忆**（★ 八个段 × 十几批 ⇒ 记忆不可靠）。

## 〇、数字（★ 全部来自生成物，附取数命令）

| # | 量 | 值 | 怎么取的 |
|---|---|---|---|
| 1 | 我们登记的 MCP 工具 | **209** | `register_capabilities.all_specs()` |
| 2 | ★ **本计划新增的工具** | **+17** | ★ 与基线差：`git show a9c7a54:docs/metrics.md` 记 **192** ⇒ 208 − 192 |
| 3 | 真缺口（分诊口径） | **94** | `tools/triage_real_gaps.py`（**该挂 46 · 已有 14 · 内部件 19 · 不做 15**） |
| 4 | 能力条目 | **79** | `capabilities.yaml`（`verified` **66** · `stitched` **12** · `not_implemented` **1**） |
| 5 | 门禁 | **20** | `scripts/release_check.py`（内部 18 道 + 语法门禁） |
| 6 | 证据文件 | **105** 份，其中 `verdict: pass` **75** 份 | `output/*evidence*.json` |
| 7 | 计划基线 commit | `a9c7a54` | ★ 段 0 之前那个 |

★ **门禁**：`python scripts/release_check.py` ⇒ **exit 0** ✓
★ **两仓库**：`git status --porcelain` **均为空** ✓（★ 全程仅本地 commit，未 push、未建远端、未发 release）

## 一、逐段：做到什么 · 证据在哪

| 段 | 做了什么 | 真机证据 |
|---|---|---|
| **0** 分诊 | `tools/triage_real_gaps.py`：把真缺口分成**五类**（该挂 / 已有 / 内部件 / 不做）· ★ **默认「该挂」，只把有明确理由的移出** | `output/real-gap-triage.json`（四类之和 == total 自检 True） |
| **1** 选择底座 | 6 个工具（杠杆最高 —— 后面每批的探针都用到它） | `output/selection-base-evidence.json` **pass 9/9** |
| **2** 草图图元 | 5 个工具 | `output/sketch-primitives-evidence.json` **pass**（段数定量：arc 0→1 · ellipse 0→1 · polygon 0→7 · slot 0→5 · centerline 0→1） |
| **3** 零件读与标注 | 2 个工具 | `output/part-read-dimension-evidence.json` **pass 4/4**（`current_sketch_name` 回**「草图1」**真名 · `auto_dimension` `status=pass` · `selected=2`） |
| **4** 孔族 | 1 个工具 | `output/hole-pattern-evidence.json` **pass**（4 孔 · **特征树 7→15** · 三负例被拒） |
| **5** 仿真载荷 | 1 个工具（另 5 条回退，见 §二） | `output/loads-simple6-evidence.json`（`elastic_connector` 计数 **0→1**） |
| **6** 导出 | 1 个工具（展开 DXF 回退，见 §二） | `output/export-two-evidence.json` **pass**（PNG `size_bytes=67997` · `grew_or_created=true`） |
| **7** 曲面族分诊 | ★ **已完成**：13 条 `IModeler.Create*Surface` 判「**不做**」并写明原因（事实 40） | `output/real-gap-triage.json` 的 `不做` 13 条 |

### 本计划新增的 16 个工具

```
段 1（6）selection_count · select_entity_by_index · resolve_selection · selection_point
          · select_by_selector · resolve_entity
段 2（5）sketch_add_arc · sketch_add_ellipse · sketch_add_polygon · sketch_add_slot
          · sketch_add_centerline
段 3（3）current_sketch_name · auto_dimension_sketch · add_dimension
段 4（1）hole_pattern                     段 5（1）simulation_apply_elastic_connector
段 6（1）export_image
```

## 二、★ **没做成的**（★ 与做成的同等重要 —— 硬约束③/⑥）

| 没做成 | 状态 | 卡在哪（★ 下次从这里接） |
|---|---|---|
| `add_dimension` · `linear_pattern` | ★ **已回退注册**（包装与探针保留） | ★ 单位已查清（官方是**米**）· 参数个数已修对（**10 参**）· 而真机上 `AddDimension2` **选中 2 条边仍回 None**、`FeatureLinearPattern3` **不报错而特征树不变**（事实 315） |
| 仿真载荷另 5 条（convection / heat_flux / heat_power / temperature / radiation） | ★ **已回退注册** | ★ `_check(…, N, …)` 的 `N` 是**官方参数个数**，★ 而这一族里**吃单实体 / 吃数组 / 参数更多**三种混在一起 —— ★ 而**仓里的来源块只抄了 4 条的官方 VB 声明**，这 5 条的**没抄** ⇒ ★ 下一步：**抄声明，再对着写**（事实 317） |
| `export_flat_pattern_dxf` | ★ **已回退注册** | ★★ 轮 407 **真的造了一个钣金件**（回读三项全 true）而它**仍拒绝**——真前置是「**已保存**的钣金件」，★ 而**保存是硬约束⑦ 明禁**的⇒ ★ **这一条在红线内验不了**（包装与探针保留，事实 322） |
| `sketch_spline` · `hole_wizard` · 13 条 `Create*Surface` | ★ **判「不做」**（自动规则抓到） | ★ `spline`：`CreateSpline3` 末参 **BYREF `Object&`**（事实 47/68）· `hole_wizard`：**空存根**（函数体只有 `pass`，★ 挂出去会**静默成功**）· 曲面族：**返回值跨次都变**（事实 40） |
| 两条 tap 配置器 · `select_object` 等 | ★ **判「内部件」** | ★ 吃 **COM 对象**而本仓**没有路径**能拿到它（只在 mock 测试里出现过） |
| `balloon` / `datum` / `jog` / `hem`（objective② 的画图域） | ★ **未做** | ★ 它们**有官方入口**，★ 而需要**建工程图** —— ★ 那是**另一条链**（本计划的 8 段没排进去） |

## 三、★ 这一轮真正值钱的东西：**判据与门禁的进化**（★ 而不是工具数）

```
★ 分诊从"两层证据"长到"六条规则"（★ 每一条都是**一次真机/契约事故换来的**）：
   ① 函数名（第一层）
   ② 它调的 COM 成员（事实 302）
   ③ 枚举常量 / 文档串（事实 311，★ 且必须**全词匹配**：`THEME` 含 `HEM`）
   ④ `*_report` 包装已是工具目标（事实 314）
   ⑤ 空存根（`pass`-only）（事实 314）
   ⑥ **动词对**（`add_X` 原语 vs `apply_X` 封装）+ **读注册表对象**（事实 317）
⇒ ★★ **每一条都配"反向保护"测试**（★ 不许把真能力吞掉）—— ★ 而那些测试**又反过来抓到我自己的两处错**：
   ★ 一次是**扫文件 vs 读注册表**（未注册的 batch56 仍被当"已有工具"），
   ★ 一次是我**把一条参数化清空了**（`got empty parameter set` ⇒ 守卫被悄悄关掉）。
```

### 真机抓到的真 bug（★ 而它们**都不是**"写错代码"，是**从未被验证过**）

| bug | 为什么一直没被发现 |
|---|---|
| `selection_point` 给两个入口传同一组实参（`GetSelectionPoint` 只有 **1 参**） | ★ 而那个错**指不出是参数个数问题**；且后者的报错**覆盖**前者 |
| `resolve_sketch` 对**非空但找不到**的草图名**静默回退**到最后一个草图 | ★ 调用方会在**另一个草图**上读/写；★ 而批头写着「选不中要报错，不静默」 |
| 我写的 5 条 ToolSpec **漏了 `inject="model"`** | ★ 静态门禁抓不到（声明合法、只少一个字段），★ **契约测试当场红** |
| `export_to_image` 用了 `out_i4()` 而模块**漏了导入** | ★ **运行期** `NameError`；★★ 而**已有的 6 条契约测试全绿** —— 因为它们走 `_load()` **注入替身**，恰好掩盖了"真实导入缺失" |

★ 最后一条的教训要单独写出来：
> **「契约测试全绿」≠「函数能跑」** —— ★ **替身注入**让测试不依赖 COM（那是对的），
> ★ 但它**顺手掩盖了导入缺失**；★ 两者是**两件事**，要**分开测**。
> ★ 所以新加的那条锁**故意绕开 `_load()`**（用 `importlib` 干净加载），
> ★★ 而且**拆掉导入跑了一遍**验证它会红 —— ★ 那才叫「门禁能抓到那个 bug」。

## 四、★ 目标口径对不对（★ 照第一轮计划的收敛报告体例，给三条诚实结论）

```
① ★ **"真缺口 101 条"这个口径本身偏大** —— ★ 它数的是"**我们自己的公开函数里没挂工具的**"，
   ★ 而那**不等于**"四家有我们没有的能力"。★ 六条规则跑完，94 条里**真该挂的只剩 46**，
   ★ 而其中**相当一部分是多面/多顶点参数**（要各自的选择链），★ **不是"一个个挂上去就行"**。
② ★ **本计划的排序原则"按杠杆不按数量"被验证是对的**：★ 段 1 的选择底座（6 个）
   ★ 直接让段 3 的 `add_dimension` 包装**少写十几行**（★ 复用 `resolve_selection`）；
   ★ 而段 2 的草图图元让后面每批的**测试几何**更丰富。
③ ★ **"回退"是这一轮出现最多的动作**（3 批共 8 条工具）
   —— ★ 而那**不是失败**：★ 每一次回退都**留下了一个具体到动作的下一步**
   （★ 抄声明 / 先造钣金件 / 先修 arity），★ 且**包装与探针都在**（★ 下次不从零重猜）。
   ★★ 按硬约束⑥，**没验过的按钮不许留在柜台上** —— ★ 这一条本轮执行了 3 次。
```

## 五、下一步（★ 具体到动作，不写"继续推进"）

```
① ★ **仿真载荷族**：从 CHM 抄 `Add{Convection,HeatFlux,HeatPower,Temperature,Radiation}` 的
   **官方 VB 声明**（★ 照既有来源块的体例），★ 再对着写 —— ★ 不继续试参数（事实 317）
② ★ **`export_flat_pattern_dxf`**：先造一个**钣金件**（`create_base_flange` 那条链）再接上（事实 318）
③ ★ **`add_dimension`**：★★ **已落地（轮 405）** —— 用**边对穷举表**（事实 53 的处方）证实它**能建**（8/8），★ 而轮 400 判「未建成」的真因是**探针选区不干净** ⇒ 已**恢复注册**。★ 而 **`linear_pattern` 仍不注册**，★★ 卡点已收敛为「**前置齐了也不建**」（轮 406 按官方 Remarks 的 **mark 表**：方向边 mark=1 与特征 mark=4 **都选上了**，而特征树仍 9→9 ⇒ **前置假设被证伪**）⇒ 下一步：先用 `auto_dimension_sketch` 造出**真实具名尺寸**，再拿真名字传 `DName1`（★ 而不是继续试参数）
④ ★ **objective② 的画图域** —— ★★ **已结案（轮 411–413，事实 326/328）**：★ `hem`/`jog` ⇒ **不做**（反射 dump 里一个都没有 ⇒ 铁律 5）；★ `balloon`/`datum` ⇒ **证不了**（需要「有视图的工程图」，而三条建图路各自被**硬约束⑦**（缺省保存）或**不可控加载弹窗**挡住）。★ 通例：**凡官方能力以「文档已落盘」为前置的，在硬约束⑦ 下都拿不到正例**
⑤ ★ **§三 那条教训的推广**：★ 全仓扫一遍"**有契约测试但从不真调**"的函数
   —— ★★ 它们正是这一类"导入缺失 / 空存根"的藏身处
```

**依据**：`output/real-gap-triage.json` · `output/selection-base-evidence.json` ·
`output/sketch-primitives-evidence.json` · `output/part-read-dimension-evidence.json` ·
`output/hole-pattern-evidence.json` · `output/loads-simple6-evidence.json` ·
`output/export-two-evidence.json` · `git show a9c7a54:docs/metrics.md`（★ 基线 192）·
`docs/known-facts.md` 事实 302 / 311 / 314 / 315 / 317 / 318

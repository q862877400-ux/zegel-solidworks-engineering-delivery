# acceptance 238 · 验收记录

## 一、判据读数

| 判据 | 读数 |
|---|---|
| 新门禁（真树） | `官方宿主页 2 个：IFeatureManager / IMotionStudy · 站点 10 · 常量被官方点名 1 · 收录常量 46 · 违规 0 · [PASS] · exit 0` |
| ★★ **红基线（改 `build_map` 之前）** | `[should-map] sw_motion.py:212 —— 常量 swFmAEMRotationalMotor 在官方宿主页 IMotionStudy 的 Type 清单里 ⇒ 必须补进映射表` · `[baseline-shrunk] named 0 < 下界 1` · `[zero-checked]` · **`exit 1`** |
| 诊断（改前 → 改后） | `检查过 5 → 6 个站点` · `unmapped 3 → 2` · 映射表 `35 → 45` · 官方点名 `5 → 15` · `[OK] 没有「成员不在期望接口上」的站点` |
| 237 门禁 | `站点 10 · checked 6 · unmapped 2 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0` |
| 新判据 | `Ran 10 tests · OK`（3.99 s） |
| 237 判据回归 | `Ran 15 tests · OK` |
| 门禁全套 `release_check.py` @**3.14.7** | `EXIT 0 · status pass · gates 47 · cd_host_scope: pass` |
| 登记条目 | `classification` **47 → 48** |
| 收尾链 `round_chain.ps1` | 见 `output/_chain238.txt` |

## 二、★★★ 核心事实一：映射表隐含了一个**从未被写出**的前提

`check_interface_member_ownership.py` 的 `CONST → 接口` 表**只**从
`IFeatureManager\CreateDefinition.md` 造 ⇒ 它隐含「**每个** `CreateDefinition` 调用的宿主都是
`IFeatureManager`」。而官方有**两个**宿主页，各有**自己的** `Type` 常量域 ⇒
「常量属于别的宿主」与「官方根本不支持它」在读数上**同形**（都是 `unmapped`）。

## 三、★★★ 核心事实二：交接单待办 2 的**前提是错的**（连续第 8 轮）

| 常量 | 真宿主 | 证据 |
|---|---|---|
| `swFmAEMRotationalMotor` | **`IMotionStudy`** | `IMotionStudy/CreateDefinition.md` 逐条点名 `[[ISimulationMotorFeatureData]]` |
| `swFmDraft` | **无** | 两页清单都没有；★ 本仓**真机证据**：`CreateDefinition(3)` 返回 `None` |
| `swFmMateProfileCenter` | **无** | 只有枚举页收录 |

⇒ ★ 照字面「补 `MANUAL_MAP`」会**污染一张本来正确的表**。**本规格一个 `MANUAL_MAP` 条目都没加**
（`MANUAL_MAP` 仍是 8 条）；`swFmAEMRotationalMotor` 走的是**官方断言**（`host_pages()`），
不是人工确证 —— 证据强度**更高**。

## 四、实质产出：`sw_motion.py` 的站点**第一次真的被核了**

改前该站点 `unmapped` ⇒ 成员归属**够不到**；改后 `checked` ⇒
`ISimulationMotorFeatureData` 的成员集被拿来做归属判据（`DirectionReference` / `Location` /
`RelativeComponent` / `ReverseDirection` 全在该接口上）⇒ **映射表 35 → 45 条**。

## 五、★ 本轮自己踩到并处置的坑

1. ★★ **官方页的两种格式**：`IFeatureManager` 页的括注是**散文标签**（`swFmBaseFlange (sheet metal base flange)`），
   `IMotionStudy` 页是**逐条点名**（`swFmAEMGravity ([[ISimulationGravityFeatureData]])`）
   ⇒ 只认后者为**断言**；前者仍走文本匹配（**推断**）。★ 把两者混为一谈会**把推断当断言**。
2. ★★ **`should-map` 会因「缺数据源」假红**：`swFmAEMLinearSpring` 被官方点名 `ISimulationLinearSpringFeatureData`，
   而该接口的 `_overview.md` **在 `C:\swapi` 里不存在** ⇒ 映射不出来。
   ★ 处置：归入 `[SKIP]` **gap**（只登记、不拦发布）—— **缺数据源 ≠ 检查失败**（事实 46 同族）。
   ★ 且该常量**当前没有站点用**，故真树不触发；但**守卫必须提前正确**，否则下一轮会被它误拦。
3. ★★ **两个码没有自然靶子**：`host-mismatch` / `ambiguous-host` 在正常跑时**永不触发**
   （映射表**先**由官方点名播种）⇒ ★ 把判罪抽成 `judge_sites()` 纯函数，由单测**直接喂输入**。
   ★ 这是「**没有靶子的守卫不写**」（232/236）在**门禁内部**的落地：守卫要么有靶子，要么可单测。
4. ★ **改 `release_check.py` 用 `Edit` 插函数** ⇒ 插完立刻复核相邻 `# ── 来源 ──` 头
   （**已踩三次** 231/233/234）⇒ 本轮按规矩做：`grep -n "^# ── 来源"` 计数 31、三个函数定义相邻正确。

## 六、未过门（如实登记）

- 宿主判定是**页级**的：不解析接收者变量（`manager` / `motion_study`）的运行期类型。
- `IFeatureManager` 页的括注是**散文标签** ⇒ 那 22 条仍是**推断**，不是官方断言。
- 只扫 `scripts/*.py`；`mcp-server/**` / `tools/**` 未纳入。
- `swFmDraft` / `swFmMateProfileCenter` 的**成员仍未审**（其站点仍是 `unmapped`）——
  本规格只把「为什么无宿主」**变成可查的精确证据**，**不**替它们造映射（门禁不得自动挑选约定）。
- `swFmDraft` 的真机证据（`CreateDefinition(3)` 返回 `None`）来自**更早的轮次**，本轮**未重跑真机**。
- 真机未验；223 的 8 条既有红未修；未提交未部署。

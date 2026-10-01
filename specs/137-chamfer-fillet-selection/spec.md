# Feature 137 · 倒角 / 圆角（作用于声明式选中的边）（砌墙 W4 续）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题

`sw_part.chamfer` / `sw_part.fillet` 能倒角/圆角，但**它们的入参里没有"边"**
（`chamfer(model, distance, angle_deg=45)` · `fillet(model, radius, edges=None)`）
⇒ ★ **它们作用在「当前选择」上**。
⇒ 要挂成工具，就必须有一层把**声明式 `selection`** 解析成**真实选区** —— 这正是
**规则 3** 要求的东西，也正是 `tool_registry` 的 **`pre_call`** 存在的理由。

## 二、★ 本批的包装形状是**第三种**（前两批各一种）

```
W1（只读）        ：`derived_args` —— 取到对象再传进去
W4（写草图）      ：`param_alias` —— 只改名
W4 续（拉伸）     ：`param_alias` —— 只改名
★ 本批（倒角/圆角）：**`pre_call`** —— **调用目标函数之前**先把"要改哪条边"选好
⇒ ★ 三种形状都是**既有机制**（`batch4` 已经用过 `pre_call` + `resolve_selection`），
  ★ 本批**不新造机制**（`batch1` 立的规矩：能声明式就声明式）。
```

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能对**声明式选中的边**倒角 | 官方 `IFeatureManager.InsertFeatureChamfer`；本项目 `sw_part.chamfer`（MIT） |
| R2 | 能对**声明式选中的边**倒圆角 | 官方 `IFeatureManager` 的圆角族；`sw_part.fillet` |
| R3 | 选择必须是**声明式**（`selection` 字符串） | 并入六条规则**规则 3**；本项目有**第二句判据**（`selection` 必须是 `str` —— 见 `specs/218` 那一轮加的门禁） |
| R4 | 长度参数一律 **`_mm`**，角度 `_deg` | 规则 2 |
| R5 | 越界 / 选不中 ⇒ **报错** | 本项目一贯纪律 |

## 四、★★★ 本批真机回答的**一个未知**（不能假设）

```
★ 问题：`chamfer` / `fillet` **没有 `edges` 参数** ⇒ 它们**真的作用在当前选择上吗**？
   · 若是 ⇒ 本批设计成立；
   · 若它们**忽略选择**（例如作用于所有边或默认边）⇒ ★ 本批的 `selection` 就是**假设计**，
     必须如实记录并改设计。
★ **真机对照实验的结论（`output/chamfer-fillet-evidence.json`）**：
     选中 `index:0` → `chamfer(2mm)` ⇒ 建出特征「**倒角1**」，特征树 **19 → 20**
     选中 `index:1` → `fillet(3mm)`  ⇒ 建出特征「**圆角1**」，特征树 **→ 21**
     ★ **清空选区**后调用          ⇒ **特征树 21 → 21（没有新增）**，且返回对象**名字为空**
   ⇒ ★★★ **证实了"它作用在当前选择上"** ⇒ **本批设计成立**。
   ⚠ ★ **但"清空选区"时它不抛错**（静默返回无名对象）——
     这是本族的**静默失败点**，与 `specs/135` 的「不 start 就画线」**同型**。
     ★ 如实记录，**不假称有守卫**（要加守卫须另开特性）。
```

## 五、调用形态**已按铁律 4 核过是对的**（上一批做的核对，事实 164）

```
`InsertFeatureChamfer(Options, ChamferType, Width, Angle, OtherDist, VertexChamDist1/2/3)`
   · 实现传 `(Options=4, ChamferType=1, Width=distance, Angle=angle_rad, 0,0,0,0)`
   · `swChamferType_e.swChamferAngleDistance = **1**`（swapi 与出厂反射**两源一致**）
   · 官方说明：Width/Angle **只在 `swChamferAngleDistance` 下有意义** ⇒ ★ **一致** ✓
⇒ ★ 所以本批**不改能力层**，只在它前面加一层"把边选好"。
```

## 六、不做什么（有据）

| 不做 | 原因 |
|---|---|
| **不改能力层的 `chamfer` / `fillet`** | 形态已核过是对的；改它风险大且与本特性无关 |
| 不顺手给"清空选区"加守卫 | ★ 那要改能力层/工具层 ⇒ **另开特性**（不顺手改） |
| 不碰保存 / 另存 / 删除 | 计划明写本阶段不做高风险写操作 |

## 七、验收

```
① 静态：`all_specs()` 里出现 2 个新工具，且门禁全绿（★ 含规则 3 的第二句判据：`selection` 是 `str`）
② ★ 真机：`output/chamfer-fillet-evidence.json` 的 `verdict` == "pass"，且含：
   · 倒角 ⇒ 特征名「**倒角1**」· 特征树 19 → 20
   · 圆角 ⇒ 特征名「**圆角1**」· 特征树 → 21
   · ★★ **对照实验**：清空选区 ⇒ **特征数不变**（证明设计成立）
   · **负例**：`index:9999` ⇒ 报错（且错误信息给出上界）
```

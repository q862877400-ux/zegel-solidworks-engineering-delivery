# Feature 139 · 装配只读（装配只读 / 配合 / 干涉）（砌墙 W6）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题

⑩装配在矩阵里"缺 21"。逐个核过之后：
```
★ **已有工具**：`add_component` · `add_*_mate` · `collect_assembly_bom` · `pack_and_go` ·
  `set_component_fixed` ⇒ 都是**建 / 改 / 导出**
★ **已实现、首参可注入、却没挂**的**只读**函数有三个（见事实 169）
⇒ ★ 缺的正是**只读的「看装配里有什么 / 撞不撞」** —— 与 W1/W5 同一形状。
```

## 二、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能列出**零部件**（名字 / 路径 / 是否抑制 / 是否可见） | 官方 `IAssemblyDoc.GetComponents`；本项目 `sw_assembly.get_components`（MIT） |
| R2 | 能列出**配合**（名字 / 类型 / 树深度） | 本项目 `sw_assembly.collect_mate_feature_summary` |
| R3 | 能跑**干涉检查**并回**可审计报告** | 官方 `IInterferenceDetectionMgr`（`Done`/`GetInterferenceCount`/`GetInterferences`）· `IInterference`（`Volume`/`GetComponentCount`）；`sw_assembly.get_interference_detection` |
| R4 | ★ **`status` 三态必须分清** | `pass` = 无干涉 · `warn` = 有干涉 · **`blocked` = 检查本身失败**（★ 不可读成"无干涉"）|
| R5 | 长度/体积等读数**标明单位** | 规则 2 的精神（本批读数沿用既有接口的单位，不换算）|

## 三、★★★ 三条关键形态

### ① 注入名：本批第一次用 `asm_model`（事实 169）
```
★ `get_components` 与 `get_interference_detection` 的首参叫 **`asm_model`**（不是 `model`），
  而**注入名只能是 `RESOLVERS` 的键**（`tool_registry` 的 `make_tool_function` 没把
  `inject_as` 传下去 ⇒ `kwargs[inject_as or inj]` 等价于 `kwargs[inj]`）。
⇒ ★ 解法：给 `register_capabilities.RESOLVERS` **加一行** `"asm_model": resolve_model`
  —— ★ 那是**那张表的设计用途**（其注释：「注入名 → 解析器。`tool_registry` **不硬编码宿主 API**，
  全从这里供给」）⇒ ★ **不动核心**。
```

### ② ★★★★ 干涉检查：**修过三处成员名，却从来没有真机证据**
```
`sw_assembly.get_interference_detection` 的源码注释记着（轮 159）：
   ① 入口属性是 `InterferenceDetectionManager`（**带 `Manager`**）
   ② 取结果用 `GetInterferences()`（**复数**），没有 `GetInterference(index)`
   ③ `IInterference` 上**没有 `Name`** ⇒ 改用 `Volume` 与 `GetComponentCount()`
★ 而注释明写：「**两处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）」
⇒ ★★ **"修过"不等于"验过"** ⇒ 本特性的真机验证就是它的**第一次验证**。
```

### ③ ★★ 验证必须**一正一反**（否则证明不了它在看几何）
```
· 两个组件**重叠**（都在 z=0） ⇒ 期望 `status: warn` · `interference_count >= 1`
· 两个组件**分开**（z=0 与 z=60；盒厚 10）⇒ 期望 `status: pass` · `interference_count == 0`
⇒ ★★ **若两个场景都回 0** ⇒ 它**仍是静默降级**；若**都回 warn** ⇒ 判据不对。
   ⇒ 只有一正一反才说明它在**看几何**。
```

## 四、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不改 `tool_registry` 去支持 `inject_as` | ★ 动核心；而**给 `RESOLVERS` 加一行**已足够且正当 |
| 不改 `sw_assembly` 的形参名 | 会**动到既有调用点**（与 W4 的定则冲突）|
| 不做装配的**写**操作（加组件/加配合/移动） | 本阶段不做高风险写操作；且已有工具覆盖 |

## 五、★ 一个写操作，以及它为什么允许

```
★ 真机验证需要**真实装配文档**，而装配要引用**已存的零件文件**
⇒ 证据脚本**写一个零件到临时目录**（`output/_fixtures/`）。
★ **这不是"改用户数据"**：只在**临时目录**造**自己的测试夹具**（与既有 `pack_and_go` 同性质）
  ⇒ ★ **允许**，且**在证据里写明**（证据里有 `fixture.saved` 与说明）。
★ 收尾：关件**不保存**。
```

## 六、验收

```
① 静态：`all_specs()` 里出现 3 个新工具，且门禁全绿
② ★ 真机：`output/assembly-evidence.json` 的 `verdict == "pass"`，且含：
   · `overlap_case.interference.interference_count >= 1`（`n_components == 2`）
   · `apart_case.interference.interference_count == 0` 且 `status == "pass"`
   · ★★ **`discriminates.ok`**（两个场景给出**不同的数**）
```

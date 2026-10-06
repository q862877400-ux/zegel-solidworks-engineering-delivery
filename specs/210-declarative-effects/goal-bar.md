# 规格 210 · 目标栏（唯一进度字段）

> 状态只写在这里。不含行号。各批的 spec/plan 段里不写「已完成 80%」这类会腐坏的话。

规格：`specs/210-declarative-effects`
立项：2026-10-06 · 来源：外部评审对「三件真正卡住的事」的判决
目标：`goal-34d5759e`（40 轮上限）

## 当前状态

阶段：★★ **B5 全部收口**（B5-1..B5-5）· **B1 收口**；下一步 = **B2 指纹与灵敏度校准**

已完成：

- **第 0 件**（本规格立项前做完，并入记账）：修掉两个对外**误报** —— `idempotentHint` 曾对 448 个工具全为真
  （客户端会当「可安全重试」）、`destructiveHint` 曾硬编码为假。现改**三态 + 未知不发**（依据 MCP 缺省语义）·
  加「单值安全字段」门禁与**负例测试** · 提交 `26fd977`
- **B1-1** 只读普查已交付（`tools/survey_effect_declarations.py`）：判据是**底层成员动词**（显式表、偏保守）
- **B1-2** 效应表生成物已交付（`tools/gen_effect_declarations.py` → `docs/effect-declarations.json`）+
  **新鲜度门禁**（现算必须等于落盘）
- **B1-3/B1-4/B1-5/B1-6** 已落地：声明层加 `writes` / `requires` / `writes_source` /
  `idempotent_source` 三态字段；**`read_only` 改成由 `writes` 派生**；动词规则提到共用模块
  （`mcp-server/effect_rules.py`，一处实现两处用）；单值安全字段门禁

★ 生效读数（修前 → 修后）：`readOnlyHint=True` **23 → 51**；★ `idempotentHint` **448 条全发真 → 一条都不发**；
★ `destructiveHint` 只对只读工具明说 `False`（51 条），其余省略（按 MCP 缺省 = 可能破坏）
★ 测试：相关 4 个文件 **46 passed**

★★★ 本轮最重要的发现（比上面任何成果都重要）：
我第一版把「**没看见写动词**」当成了「**确认无写**」⇒ 报出「148 确认无写 / 152 确有写」。
修掉之后（**有认不出的成员就判未知**）真实覆盖率是：
**确认无写 35 · 确有写 53 · 未知 360** ⇒ **只有 88/448（20%）拿到可信的机械结论**
⇒ 说明**动词规则单独一路不够**：成员里大量是**属性式访问**（`FeatureManager`、`FirstFeature` 这类名词），
而那正是评审说的**第二路**（官方类型库的方法/属性与 `propput`）要补的位置。

两条必须记住的限度（如实记，不许当成「已解决」）：

① 只用了**底层成员动词**这一路；官方类型库那一路**未参与**（B1-7 就是补它）
② **360 个工具的 `writes` 是「未知」**，★ **不是「无写」** ⇒ 注册层按未知**保守处理**
   （不发只读、B4 的自动重试不会对它们开放）

★ **B1-7 已交付（第二路判据）**：
- 新 `tools/gen_member_kind_index.py` → 官方类型库的**成员种类索引**（缓存、不入库）：
  扫 11557 页 ⇒ **8238 个成员名** = **属性 2411**（★ **可写 1962** `{get; set;}` · 只读 381 `{get;}` · 未标 68）
  + **方法 5827**（★ 官方无读写标记）
- `effect_rules` 加 `classify_member` / `load_kind_index`：★ 动词认不出时查类型库 ——
  **属性可设 ⇒ 写** · **属性只读 ⇒ 读** · ★ **方法 ⇒ 判不出**（★ 评审的提醒成立）
- ★★ **覆盖率 20% → 41%**：确认无写 **35→47** · 确有写 **53→135** · 未知 **360→266** ✓
- ★ 便携性：索引**显式传入**（默认不用）⇒ 干净机器与测试行为**确定**；
  ★ 索引缺失时新鲜度门禁**带原因 skip**（★ 不假装测过）✓
- 测试：新增 5 条第二路契约（含"方法即使查了类型库仍判不出"这条要害）；本文件 **15 passed**

★ **B5-1 已交付（预检门禁）**：
- `scripts/sw_session.py` 新增 `open_documents` / `classify_open_documents` / `precheck_session`
  + `ForeignDocumentError` ✓
- ★ 官方依据（铁律 4 的第 0 步已读）：`ISldWorks.GetDocuments`（"open documents in this session"）+
  官方示例 `Get_Paths_of_Open_Documents` 的调用序（`GetDocumentCount` → `GetDocuments` → 逐档 `GetPathName`）；
  ★ 并**据官方 Remarks 排除了** `GetFirstDocument`（装配体时它只返回首个组件，**不是完整枚举**）✓
- ★★ **判据用回读**：`GetDocumentCount` 与 `GetDocuments` 数组长度**互相校验**，不一致要如实报出 ✓
- ★★ **保守方向**：路径为空（新建未存盘）**算非我方**，除非显式 `allow_untitled=True` ✓
- 测试：**8 条**契约与负例（含"开着用户文档必须抛异常拒绝开始"这条负例）✓

## 下一个动作（只写一条，免得没人知道该恢复哪个）

★★★★ **把 22 条 `undecided` 拆开看，拆出了一条工具层的真 bug**（★ 本轮最有价值的东西）✓

**★★ 拆出来的五类（★ 22 条 `undecided`，★ 性质完全不同）**
1. ★★ **声明不准（7 条）**：★ `drawing_current_sheet_info` / `drawing_sheet_count` / … 七条 `drawing_*`
   ⇒ ★ 真机报 **`当前文档不是工程图（GetType()=1）`** ⇒ ★★ 它们的 `inject` 声明是 **`model`**，
   ★ 而**实际要的是工程图** ✗ —— ★ **`inject` 没表达出"文档类型"这一维** ✓
2. ★★ **`requires` 维度不够（4 条）**：★ `sketch_fully_defined_status` / `sketch_mirror` / `sketch_spline`
   ⇒ ★ 报 **`没有活动草图` / `不在草图编辑态`**；★ `part_bounding_box` ⇒ ★ 报 **`零件里可能没有实体`**
   ⇒ ★★ **它们需要的是"编辑态 / 实体"，而 `requires` 只表达"宿主对象"** ✗ —— ★ **维度少了一维** ✓
3. ★★ **参数合成不够（4 条）**：★ `automation_get_flag` ⇒ ★ `invalid literal for int(): 'MCP_CALIB'`
   （★ **我的合成器把字符串塞进了 int 形参** ✗）· ★ `config_set_custom_properties` ⇒ ★ 需要 **dict**
   （★ 给了字符串 ✗）· ★ `weldment_create_weldment_profile` ⇒ ★ 要 **`.sldlfp`** 扩展名 ✗ · ★ `fastener_*` ⇒
   ★ 需要**非空的**标准名 ✗ ⇒ ★★ **合成规则要按"类型提示"而不是只看名字后缀** ✓
4. ★★★ **工具层真 bug（1 条）**：★ `simulation_apply_link_connector` ⇒
   ★★ **`ImportError: attempted relative import with no known parent package`** ✗ —— ★ 见下 ✓
5. ★ **待查（6 条）**：★ `costing_list_bodies` / `costing_read_body` / `topology_list_constraints`
   （★ 返回体为空，★ 原因还没查）· ★ `weldment_read_property_manager`（★ `SldWorks.Application.GetNames` ✗）✓

**★★★ 第 4 类：真 bug + 它的系统性（★ 本轮的主产出）**
· ★ 根因：★ `scripts/sw_simulation_loads.py` **函数体内**有 **17 处**
  `from .sw_selection_spec import …` / `from .sw_simulation import …`，★ **没有兜底** ⇒
  ★★ 作为 `scripts.X` 导入时成立，★ **一旦按顶层模块导入就炸** ✗
· ★★ **而仓库自己早就写好了正确写法**（同文件那处 `sw_connect`）：
  ★ `try: from .X import Y` / ★ `except ImportError: from X import Y` ✓
  ⇒ ★ 我**照仓库自己的写法**修了那 17 处（★ \+68/−17，★ 按**事实 61** 核对过：
    ★ 17 处删除 = 被替换的原行，★ 每行变 4 行 ⇒ ★ 行数吻合 ✓）✓
  ⇒ ★ 真机验证：★ 该模块**作为顶层模块现在能导入** ✓
· ★★ **全仓扫描**：★ 同款**共 54 处 / 22 个文件**（★ 顶层**一个都没有** ⇒ ★ 没有模块因此整体坏掉，
  ★ 只有"**在非包导入路径下调用那些函数**"才炸）✓
· ★★ **处置（★ 按事实 61 的纪律：批量改动风险高 ⇒ 不一次改 22 个文件）**：
  ★ 修**实际炸掉的那一个** + ★ 加**门禁棘轮**（★ 存量只许变少、不许变多）✓
· ★ 新 `scripts/check_relative_imports.py` ⇒ 全仓实测 **35 处**（★ **基线必须实测、不许估** ——
  ★ 我先估了 37，★ 实扫是 35，★ 已改）✓
· ★ 新 `tests/test_relative_imports_gate.py`（**4 条**，★ **两侧都证**，★ 事实 62 的手法）：
  ★★ **负例**：★ **修复前**的原文（`git show HEAD:…`）⇒ ★ **必须命中 17 处** ✓
  ★★ **正例**：★ **修复后**的文件 ⇒ ★ **必须 0 命中** ✓
  ★ **契约**：★ 判据必须 `startswith("try:")` —— ★ 因为修法带 `# noqa` 注释，
    ★ 用 `== "try:"` 会把**已修好的**算成没兜底 ✗（★ **我第一版就栽在这，真机现象：修完仍是 54 处**）✓

**下一批**
1. ★★ 把 `check_relative_imports.py` **接进 `release_check.py`**（★ 那就成了常驻不变量）✓
2. ★★ 按拆出来的五类**逐类处置**：★ 声明不准（补"文档类型"维度）· ★ `requires` 补"编辑态/实体"维度 ·
   ★ 合成器按类型提示 · ★ 剩下的真 bug（`weldment_read_property_manager` 的 `SldWorks.Application.GetNames`）✓
3. ★ 跑 **`nonempty`（135）** 与 **`null`（266）** ⇒ ★ 全量分布 ✓
4. ★★ 把覆盖层接成**棘轮**（★ 每次普查的 `missed` **必须**进覆盖层 + 门禁）✓

## 批次状态

- **B1 效应声明静态版**：**完成**（B1-1..B1-7）
- **B2 指纹与灵敏度**：⚪ 未开始（★ 下一步）
- **B3 存活普查**：🟡 **进行中**（★ `empty` 组 **47/47** 全 `agree`、硬红 **0** ✓；★ `nonempty` 抽样 20：硬红 0 · `conservative` 3 · ★ **17「没调成」** ⇒ ★ **写工具缺前置**；★ 要先补 `requires` 再分组）
- **B4 自动重试与「不适用」**：未开始
- **B5 隔离与预检**：**完成**（B5-1 · B5-2 · B5-2b · B5-3 · B5-4 · B5-5）

## 调整（计划变更记在这里）

- 2026-10-06：★ 本轮我的更新脚本**又栽在引号嵌套上**（把中文引号套进 ASCII 引号里 ⇒ SyntaxError，⇒ 目标栏与任务表**没被改写**，我一度以为写了；★ 而且 PowerShell **不支持 heredoc**）⇒ ★ **长文本一律走独立脚本文件**（事实 48 定则①）✓


- 2026-10-06：把「重算 `idempotent`」并在 B1-1（评审：与效应声明合成一件做）
- 2026-10-06：`read_only` 从「独立手填布尔」改成**由 `writes` 派生**（B1-4）——
  这是「76 个只读工具被记成非只读」的**根因修法**
- 2026-10-06：**新增 B1-7** —— 动词规则只覆盖 20%，必须补官方类型库那一路
- 2026-10-06：**新增铁律级别的判据**：`writes` 的「未知」（`None`）与「确认无写」（`[]`）**必须分开**，
  且**未知一律按保守处理** —— ★ 这是我第一版犯的错，写进这里免得重犯
- 2026-10-06：**B1-7 完成**，覆盖率 20% → 41%；★ 剩下 **266 个未知主要来自"方法"**（官方无读写标记）
  ⇒ ★ 再往上只能靠**运行期实证**（B3 的指纹差分），★ 这正是 B3 存在的意义 ✓
- 2026-10-06：**B5-1 完成**；★ 下一步 B5-2 要把判定**提到一处**再接线 ——
  ★ 注意 B5-1 的助手是**按 COM 读实际打开的文档**（比回收脚本原来的**窗口标题**判法更准），
  ⇒ ★ 接线时要**替换**旧判法而不是并存两份 ✓

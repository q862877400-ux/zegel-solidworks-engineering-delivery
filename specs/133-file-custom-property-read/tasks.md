# Tasks · Feature 133 读文件自定义属性

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 先写真机探针（W1/W2 都证明这一步会推翻按文档做的设计）

- [x] `tools/probe_custom_property_reads.py`：答三个未知
      （管理器怎么取 / 读值走哪个成员 / by-ref out 回不回写）+ **决定性用例**（先写再读回）
- [x] ★ 修正探针自己的**假阳性判据**（`not isinstance(...)` ⇒ 改成行为判据）
- [x] 产物 `output/custom-property-reads.json`

→ 验收: `python tools/probe_custom_property_reads.py` ⇒ exit 0，且证据里
  `verdict_readback.ok == true`、`managers.B/c` 为"★ 是管理器"、`A` 为"method"

## T1 · 新建能力层 `scripts/sw_custom_property.py`

- [x] `SW_CUSTOM_INFO_TYPES`（0/3/11/30/64，照官方示例逐字）
- [x] `custom_property_manager(model, config_name="")`：★ **当方法调用**；判据用**行为**（有没有 `Count`）
- [x] `custom_property_count` / `custom_property_names`
- [x] `custom_property(model, name, config_name)`：★ 走 `Get`（单返回值）；空名字 ⇒ **ValueError**
- [x] `custom_properties(model, config_name)`：全部（名 + 值 + 类型 + 条数）
- [x] ★ **不使用** `Get2..Get6`

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import sw_custom_property as m;print(m.SW_CUSTOM_INFO_TYPES[30], callable(m.custom_property))"`
  ⇒ 输出 `text True`

## T2 · 写 `mcp-server/tool_specs_batch20.py`（**2 个**工具）

- [x] `solidworks_custom_property_get`（一个，带 `name` + `config_name`）
- [x] `solidworks_custom_property_list`（全部，带 `config_name`）
- [x] ★ **不挂** `count` / `names` 为独立工具（结果已被"读全部"包含）—— 理由写在批头

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **67**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

- [x] 加 `"tool_specs_batch20"` 并注明两个真机坑

→ 验收: 同 T2（67 而不是 65）

## T4 · 写真机证据 `tools/capture_custom_property_evidence.py`

- [x] ★ 核声明的 `module`/`function` 都解析得到
- [x] ★★ **决定性用例**：`Add3` 写一个再读回来（`count` +1 且读到写入值）
- [x] `count_read == count_reported`
- [x] **负例 A**：不存在的属性名 ⇒ 空值、**不抛**（官方 `Get` 原义）
- [x] **负例 B**：空属性名 ⇒ **ValueError**
- [x] 安全：`CommandInProgress` + 只在新零件上跑 + 关件不保存

→ 验收: `python tools/capture_custom_property_evidence.py` ⇒ exit 0，`output/custom-property-evidence.json` 的 `verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图（新增了公开函数）
- [x] 计数守卫同步：`test_server_wiring` 65→**67** · `test_mcp_protocol_layer` 110→**112**
- [x] 无人值守基线：★ 只加新能力那一条（**不重生成**，免得吸收别的漂移）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 161
- [x] `capabilities.yaml` 加 `file_custom_property_read`（level=verified + evidence）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| D1 | ★★ **探针第一版的判据是假阳性**（`not isinstance(v,(str,int,float))` 判不出 method 对象） | 改成**行为判据**（有没有 `Count`）；★ 与事实 155 同族 |
| D2 | ★★ **"标了 Obsolete 就换后继"在这里是错的** —— 后继 `Get2..Get6` 带 by-ref out，pywin32 下报类型不匹配 | 用 Obsolete 的 `Get`（单返回值）；★ 定则：**可用性判据是"封送形状"，不是"代数新旧"** |
| D3 | `Feature.CustomPropertyManager`（官方示例那条路）实测回 `None` | 走 `Extension.CustomPropertyManager("")` |
| D4 | `IsCustomPropertyEditable` 没读到（`editable` 回 `null`） | ★ **如实留在结果里**，写进 capability 的 limitations；不假称能读 |
| D5 | 原计划 W3 是"会话/文档/文件"一大批 | 核过缺口后：保存类不做、导出/开关类已有、**真缺的只有自定义属性读取** ⇒ 缩成 2 个工具 |

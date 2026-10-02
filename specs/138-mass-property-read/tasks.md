# Tasks · Feature 138 读质量属性

> 每条任务都带 **`→ 验收:`**，且验收是**一条能跑出绿的命令**。

## T0 · ★ 写真机探针答三问（取法 / 单位 / 负例）

- [x] `tools/probe_mass_property_reads.py`：取法**两种形态都试**（当属性 / 当方法）
- [x] ★ **造已知体积的盒**（40×20×10 ⇒ 8000 mm³ / 2800 mm² / 重心 z=−5）当**标尺**
- [x] 真实记录 `GetMassProperties`（12 double 后备）的读数
- [x] 产物 `output/mass-property-reads.json`

→ 验收: `python tools/probe_mass_property_reads.py` ⇒ exit 0，且证据里
  `unit_verdict.volume_matches_mm3 == true` · `volume_matches_m3 == false`

## T1 · 新建能力层 `scripts/sw_mass_property.py`

- [x] `mass_property_object(model)`：★ **当属性取**；判据用**行为**
- [x] `mass_properties(model)`：读 5 个成员（**不做任何换算**）
- [x] `UNITS` 常量：★ 把单位与"未确证"写在一处，供工具说明引用
- [x] ★★ **`require_mass_property_document`**：`GetType()==3`（工程图）⇒ **报错**
      —— ★ **这一条是真机负例逼出来的**（见 tasks 的 D1）

→ 验收: `python -c "import sys;sys.path.insert(0,'scripts');import sw_mass_property as m;print(m.SWDOC_DRAWING, callable(m.require_mass_property_document))"`
  ⇒ 输出 `3 True`

## T2 · 写 `mcp-server/tool_specs_batch24.py`（**1 个**工具）

- [x] `solidworks_part_mass_properties`（无参数）
- [x] 说明里**明写**：单位是**毫米系**（不做换算）· ★ **`mass` 的物理单位未确证** ·
      `AccuracyLevel` 不暴露
- [x] ★ **不拆成 5 个工具**（五样总是一起被问）

→ 验收: `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ **78**

## T3 · 注册进 `register_capabilities.BATCH_MODULES`

→ 验收: 同 T2（78 而不是 77）

## T4 · 写真机证据 `tools/capture_mass_property_evidence.py`

- [x] ★ 核声明解析得到 · 记录"当属性取即可"
- [x] ★★ **数字断言**：volume **8000** · surface_area **2800** · center_of_mass **[0,0,−5]**
- [x] ★ 如实记录 `mass` 的量纲疑点（`mass/(volume×density) == 1.0`）
- [x] ★ 如实记录 `AccuracyLevel` 读不到
- [x] **负例**：在**工程图**上调用 ⇒ 必须报错
- [x] 安全：`CommandInProgress` + 只在新文档上跑 + 关件不保存

→ 验收: `python tools/capture_mass_property_evidence.py` ⇒ exit 0，`verdict == "pass"`

## T5 · 收工纪律

- [x] 重建覆盖率地图 + 等级审计
- [x] 计数守卫同步：`test_server_wiring` 77→**78** · `test_mcp_protocol_layer` 122→**123**
- [x] 无人值守基线：★ **只加 `mass_property_read` 一条**（不重生成）
- [x] 门禁链 8 条 exit 0 · 全量 pytest **0 failed**
- [x] Spec Kit 五件套 · ROADMAP §一 游标 · known-facts 168
- [x] `capabilities.yaml` 加 `mass_property_read`（level=verified + evidence，★ 含**单位与量纲的限制**）
- [x] 两仓库各自 commit（不 push）

→ 验收: 两仓库 `git status --porcelain` 为空，且 pytest 0 failed

## 发现的偏差（实现中冒出来、计划里没预料的）

| # | 偏差 | 处置 |
|---|---|---|
| **D1** | ★★★ **真机负例没抛错** —— 在**工程图**上 `CreateMassProperty` **也返回一个带 `Mass`/`Volume` 的对象** ⇒ **行为判据静默通过**、返回无意义读数 | ★ 加 `require_mass_property_document`（`GetType()==3` ⇒ 报错）⇒ 修完**重跑**，负例命中、`verdict` 由 FAIL 变 **pass**。★ 定则：**行为判据证明"成员存在"，不证明"读数是这个文档的"** |
| D2 | ★ `mass` 恰好等于 `volume(mm³) × density` ⇒ **量纲不成立** | ★ **照实记录 + 工具说明写明"未确证"**；★ 不猜、不换算 |
| D3 | `IMassProperty2.AccuracyLevel` **读不到** | ★ **不暴露**它（如实记） |
| D4 | ★ 探针里 `CreateMassProperty` **当属性取就行** —— 与 W3 的 `CustomPropertyManager` **相反** | ★ 记成事实 167：**同一个父对象的不同成员，取法可能不同**，教训**不能照搬** |

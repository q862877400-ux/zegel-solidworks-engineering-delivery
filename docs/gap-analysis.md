# 缺口分析（gap-analysis）

> 生成日期：2026-09-29 · 轮次 1
> 对照基线：`wzyn20051216/solidworks-automation-skill` @ `8be39ac`
> 官方侧依据：见 `docs/capability-matrix.md`
> **本文档由静态检索与元数据反射生成，未启动 SolidWorks、未执行任何 COM 调用。**

## ★ 「全覆盖」的可辩护口径（需要用户拍板）

本任务的目标是「官方 API 全覆盖」。但「覆盖」这个词在本项目里被用过**三种
强弱不同的判据**，结果差别巨大——不先定口径，自评必然说假话：

| 口径 | 含义 | 本仓库实测（2026 收尾后） |
|---|---|---|
| ① **接口族收录** | 每个接口族的成员都抄进官方 API 索引 | ✅ **792/792 族** |
| ② **成员收录** | 每个成员的名字与参数个数都抄全 | ✅ **15,466/15,466 = 100%** |
| ③ **参数个数核对** | 索引里的 arity 与反射逐条一致 | ✅ 逐程序集自动比对，见门禁 |

> ⚑ 这三个口径**都已达成**，且都有门禁盯着。
> 但请注意它们**只说明「清单正确」**——
> **不说明每个 API 都被高层封装过**。本仓库**刻意不做**逐成员封装
> （用户要求「不要有自创的东西」），调用方一律用
> `call_index(对象, "族名", "成员名", *参数)` 直接按官方名调。

**收录范围**：本机实装 18 个 interop 程序集（1,804 个接口），收录 **12** 个；
未收录 3 个是明确排除的（`sustainability` / `sw3dprinter` / `swbrowser`），
`swconst` 只有枚举（字面值已单独收录），`swcommands` 实测 0 个接口。

**门禁**（每道都做过负向验证：注入已知违规 → 确认报 FAIL 并点名行号 → 撤销恢复 PASS）：

| 门禁 | 拦什么 |
|---|---|
| `check_provenance.py` | 新增代码没有出处 |
| `check_diff_markers.py` | 来源块把 patch 记号带进来 |
| `check_member_names.py` | 成员名在官方反射里查不到 |
| `test_official_names_only_contract.py` | 自造入口、索引与反射逐条对齐 |
> ⚑⚑ **「触及」这个词本身有歧义，拆成两列后才不误导。**
> - **编目录**：名字在代码里出现过，**含只写在登记表里的**
> - **真调用**：真的被调用过（`get_com_member(obj, "X", …)` 或 `obj.X()`）
>
> 16,615 个成员里，编目录 12,870（77%）、**真调用 2,636（16%）**。
> 早先只报前者 —— 那不是「实现了 77%」，那是「知道 77% 的 API 叫什么」。

> ⚑ **我早先的自评用的是口径 ①，却把它写成「全覆盖」——那是自欺。**
> 口径 ① 之下，一个 112 成员的族只要碰过 1 个成员就算「已覆盖」，
> 当时的中位数只有 25%。

**收尾批次后的真实分布**（`family-coverage.md` 的「成员触及率」列）：

- 100% 的族：**263**
- 50–99%：108
- 1–49%：3
- 低于 60% 的族只剩 3 个，都是小族：
  `ISurfacePlanarFeatureData`(7 成员, 57%) ·
  `ISurfaceTrimFeatureData`(12, 58%) · `IMidSurface3`(23, 57%)

**本轮怎么从 16/181 走到 263/374**：加了四个**全量登记表**模块
（`sw_simulation_full` / `sw_pdm_full` / `sw_sldworks_remaining` /
`sw_routing_costing_full`），把「有多少族、每族有哪些能力、每个能力几个参数」
一次性登记；再把 5 个 `C:\swapi` 未收录程序集的族并入域映射，
否则覆盖表会继续说「没覆盖」。

**早先最低的几个巨型接口现在是这样**：

| 族 | 成员 | 早先 | 现在 |
|---|---|---|---|
| `ISelectionMgr` | 62 | 3% | 90% |
| `ISketch` | 104 | 3% | 33% |
| `IModelView` | 75 | 3% | 81% |
| `IAssemblyDoc` | 196 | 4% | 71% |
| `ICurve` | 68 | 4% | 51% |
| `IMate2` | 33 | 6% | 97% |
| `IEdge` | 47 | 6% |

这些接口里**大量成员是极少用到的**（`IAssemblyDoc` 的 196 个成员里，
工程脚本常用的不过二三十个）。**把它们逐个包成 Python 函数：收益低、
维护成本高，还会把「覆盖」刷成一个没有信息量的数字。**

⇒ **建议口径 ② 为主、① 为底线**：每个族至少触及 1 个成员（无整族缺席），
且**常用方法**基本覆盖；罕见成员在 `signature-audit.md` 里逐条列出
「未封装 + 原因」。
⚠ **口径是产品决策，不是我能替用户定的** —— 需要确认后再谈 fork。

## 〇、本轮对项目文档既有假设的核实结果

AGENTS.md 要求「不得预设任何缺口结论，从零建表」。逐条核实结果：

| 项目文档的假设 | 核实结论 | 依据 |
|---|---|---|
| 上游完全没有 Simulation（`cosworks`/`CWModelDoc`/`CwObjects` 出现 0 次） | ✅ **成立** | 逐仓 grep：`sw-automation-skill` 三词各 0 次 |
| codestack 也没有 Simulation | ✅ **成立** | `cosworks` 0 次 |
| 「18 个仓库全都没有 Simulation」 | ❌ **不成立** | `Solidworks-MCP`(alisamsam, **MIT**) `cosworks` 14 次 / `Simulation` 206 次；`CSharpAndSolidWorks`(MIT) `cosworks` 2 / `CWModelDoc` 3；`SolidworksMCP-TS`(MIT) `Simulation` 20 |
| 工程图建视图「疑似薄弱」 | ✅ **成立且更严重** | `scripts/sw_drawing.py` 仅 **30 行、0 个函数**，是纯兼容入口桩；`sw_drawing_review.py` 25 行 0 函数 |
| codestack（377★）「有建视图解法」 | ❌ **不成立** | 全仓 grep `Create3rdAngleViews2`/`CreateDrawViewFromModelView`/`CreateSectionViewAtPoint`/`Create1stAngleViews2` **零命中**；仅有的 1 处 `InsertModelAnnotations3` 出现在一个 PropertyManagerPage 窗口 API 例子里，属旁支 |
| CHM `cosworks` 册「34 接口页可用」 | ❌ **不成立** | 全部空壳，见 `capability-matrix.md` §〇 |
| cosworks 成员 9,281 | ⚠ **未查证** | 反射得 3,224，差异口径不明，已记待办 |
| `capabilities.yaml` 映射「8 种后端」 | ⚠ **不准** | 实为 **10 个**后端 / 28 条能力 / 11 条路由 |

### Simulation 关键词逐仓普查（原始数据）

| 仓库（owner/repo） | 许可 | 文件 | cosworks | CwObjects | ICWLoads | CWModelDoc | AddRestraint | Simulation |
|---|---|---|---|---|---|---|---|---|
| Solidworks-MCP (alisamsam) | ✅ MIT | 52 | **14** | 0 | 0 | 0 | 2 | **206** |
| q3ds-solidworks-mcp (Bennyco86) | 👁 AGPL | 56 | 14 | 0 | 2 | 0 | 3 | 41 |
| CSharpAndSolidWorks (painezeng) | ✅ MIT | 78 | 2 | 0 | 0 | 3 | 0 | 10 |
| SolidworksMCP-TS (vespo92) | ✅ MIT | 80 | 0 | 0 | 0 | 0 | 1 | 20 |
| codestack (xarial) | ✅ MIT | 1331 | 0 | 0 | 0 | 0 | 0 | 7 |
| **sw-automation-skill (上游)** | ✅ MIT | 268 | **0** | 0 | 0 | 0 | 0 | 34 |
| sw-skill-fork（工作副本） | ✅ MIT | 268 | 0 | 0 | 0 | 0 | 0 | 34 |
| 其余 12 仓 | 混合 | — | 0 | 0 | 0 | 0 | 0 | 0–71 |

> 上游的 `Simulation` 34 次是文字提及（走 CalculiX/Elmer 开源求解器），不含任何 `cosworks` 调用。

---

## 一、上游现状盘点

### `scripts/` — 49 个模块

| 能力域 | 模块 | 行 | 公开函数 | 备注 |
|---|---|---|---|---|
| 零件建模 | `sw_part` | 838 | 46 | ★主战场，含 `extrude_cut`(FeatureCut4)、`_select_by_id` |
| 装配 | `sw_assembly` | 749 | 33 | |
| 交付/BOM | `sw_delivery` | 1187 | 33 | |
| 结果自审查 | `sw_review` | 1185 | 28 | |
| 连接 | `sw_connect` | 535 | 19 | ★含 `get_com_member`、`create_empty_dispatch_variant` |
| Motion Study | `sw_motion` | 493 | 14 | **Motion 已覆盖**（≠Simulation） |
| 焊件 | `sw_weldment` | 405 | 15 | |
| 导出 | `sw_export` | 376 | 17 | |
| 宏防护 | `sw_macro_guard` | 357 | 12 | VBA 宏生成防护层 |
| 文档数据 | `sw_document_data` | 355 | 11 | |
| 齿轮 | `sw_gear` | 302 | 7 | 渐开线直齿轮 |
| 孔特征 | `sw_hole_features` | 254 | 13 | |
| 预检 | `sw_preflight` | 262 | 17 | |
| 外观 | `sw_appearance` | 219 | 12 | |
| 会话 | `sw_session` | 185 | 1 | 友好会话 API |
| **钣金** | `sw_sheet_metal` | **164** | **4** | ⚠ 相对薄（4 个函数） |
| 能力探测 | `sw_capability_probe` | 167 | 4 | |
| Add-in 宿主 | `sw_addin_host` | 173 | 5 | |
| 网格导入 | `sw_import_mesh_reference` | 259 | 4 | |
| 实体引用 | `sw_entity_reference` | 76 | 3 | |
| **工程图** | `sw_drawing` | 29 | 0 | ⚠ **桥接层**，re-export 子技能实现（见下） |
| **工程图审视** | `sw_drawing_review` | 25 | 0 | ⚠ **桥接层** |
| **工程图规格** | `drawing_spec` | 25 | 0 | ⚠ **桥接层** |
| FEA | `fea_analysis` / `fea_convergence` | 788/252 | 19/9 | ⚠ 走 CalculiX/Elmer，**不是** SW Simulation |
| Routing | `routing_review` | 521 | 12 | ⚠ 中性路线校验，**不是** SWRoutingLib |
| DFM | `dfm_review` | 1085 | 30 | |
| OCP 几何 | `advanced_geometry*` / `advanced_surface_ocp` | 534/563 | 22/18 | |
| 无头写入 | `headless_cad_writer` / `headless_occt_service` | 707/337 | 23/10 | |
| CAD Studio | `cad_studio` / `cad_doctor` / `cad_installation` / `cad_diagnostics` | 308/273/331/65 | — | |
| 其余 | `backend_router` `capabilities` `dxf_preview_scene` `dfm_profiles` `release_check` `stability_regression` 等 | — | — | |

**结论**：零件/装配/导出/交付四块厚；**工程图实现不在 `scripts/` 而在子技能**（见下）；钣金偏薄；**Simulation / Routing API / Costing / PDM 完全无对应模块**。

### ★ 轮次 2 更正：工程图并非空桩

轮次 1 我只看了 `scripts/` 层，判定「工程图三件全是空桩」——**这是错的**。
`scripts/sw_drawing.py`（29 行）是一个**桥接层**，用 `importlib` 把
`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 重新导出，
以保持历史 `scripts.sw_drawing` 导入路径可用。

真实实现规模：

| 文件 | 行 | 函数 | 内容 |
|---|---|---|---|
| `drawing_workflow.py` | **2033** | **53** | `create_standard_views` / `create_standard_views_with_projection` / `create_adaptive_standard_views` / `add_view` / `add_section_view` / `add_detail_view` / `insert_dimensions` / `insert_bom_table` / `select_drawing_template` / `plan_standard_view_layout` / `auto_arrange_drawing_dimensions` 等 |
| `drawing_review.py` | — | — | 43,942 B 审视器 |
| `drawing_spec.py` | — | — | 8,652 B 规格校验 |

⇒ **G2（工程图建视图）从「缺口」降级为「已覆盖但有签名缺陷」**。
真实工作不是新写模块，而是**审现有实现的 COM 签名**——本轮据此查出并修复 2 处，
详见 `docs/signature-audit.md` 批次 2。

### `subskills/` — 5 个

| 子技能 | 文件 | 覆盖 |
|---|---|---|
| `autocad-automation` | 19 | AutoCAD 侧 |
| `solidworks-engineering-drawing` | 11 | 工程图（**文档层面**，`scripts/sw_drawing.py` 仍是桩） |
| `solidworks-fillet-chamfer-cnc` | 19 | 圆角倒角 + CNC |
| `solidworks-threaded-holes` | 7 | 螺纹孔 |
| `solidworks-vibecad` | 12 | 自然语言驱动 |

### `tests/` — 78 个

`test_*.py` **62** 个 + `solidworks_*_regression.py` **11** 个 + 其他 5。

### `references/` — 20 篇

`advanced` `agent-provider-architecture` `api-lookup` `appearance` `assembly` `complex-hole-features`
`complex-mechanical-routing` `drawing` `enterprise-agent-rag` `export` `gears`
`language-backend-routing` `mcp-server` `mesh-reference-import` `motion-study` `openclaw`
`part-modeling` `review` `solidworks-addin-host` `troubleshooting`(27KB)

> **无任何 Simulation / 载荷 / 夹具 / 拓扑优化 相关参考文档。**

### `capabilities.yaml`

实为 **JSON**（`.yaml` 后缀不符），480 行：
- `backend_catalog` **10 个后端**：`solidworks-com-pywin32` / `solidworks-com-comtypes` / `solidworks-csharp-pia` /
  `solidworks-csharp-addin` / `solidworks-native-cpp` / `solidworks-swbasic` / `headless-occt-python` /
  `autocad-dotnet` / `external-solver-python` / `local-python`
- `operation_routes` **11 条路由**；`capabilities` **28 条能力**
- 能力 `level` 字段取值 `verified` / `pilot` 等

> ⚠ **A6 禁词口径**：上游 `capabilities.yaml` 自身含 `level: "verified"` 及「已真机验证」等字样。
> A6「禁词 0 命中」**只能作用于本轮新增/修改的文件**，不能回溯要求上游既有文件改写。
> 本轮新增文件将严格 0 命中，并附 grep 证据。

---

## 二、18 仓库可移植素材定位

| 能力 | owner/repo | 许可 | 相对路径 | 可否移植 | 说明 |
|---|---|---|---|---|---|
| **Simulation 入口链** | alisamsam/Solidworks-MCP | ✅ MIT | `solidworks_simulation.py`(780行) | ✅ **可抄结构，COM 调用须重写** | 唯一 MIT 的 Simulation 实现。提供 `GetAddInObject("SldWorks.Simulation")`→`.COSMOSWORKS`→`.ActiveDoc`→`.StudyManager`→`.LoadsAndRestraintsManager` 完整拓扑 + 9 个 dataclass 结果对象 + 错误码表 |
| Simulation 开发路线 | alisamsam/Solidworks-MCP | ✅ MIT | `DEVELOPMENT_ROADMAP.md` | ✅ 只读参考 | 11 处 cosworks 提及 |
| 工程图尺寸标注 | painezeng/CSharpAndSolidWorks | ✅ MIT | `CSharpAndSolidWorks/AddSizeDimensionForDrawing.cs`(35KB) | ✅ **可抄** | 全 18 仓中最实的工程图实现 |
| 几何/干涉算法 | painezeng/CSharpAndSolidWorks | ✅ MIT | `CSharpAndSolidWorks/MyInterference.cs` | ✅ 可抄 | 自交/干涉 |
| CWModelDoc 触碰 | painezeng/CSharpAndSolidWorks | ✅ MIT | `CSharpAndSolidWorks/FormMain.cs` | ⚠ 需逐行审 | 3 处 `CWModelDoc` 引用 |
| VBA 过程间通信 | xarial/codestack | ✅ MIT | `solidworks-api/getting-started/inter-process-communication/…`(4 .vba) | ✅ 可抄 | 真实 VBA 语料 |
| 阵列 VBA | xarial/codestack | ✅ MIT | `solidworks-api/document/macro-feature/multi-extrude/`(5 .vba) | ✅ 可抄 | |
| 选区等待 | xarial/codestack | ✅ MIT | `solidworks-api/document/selection/wait-for-selection/`(3 .vba) | ✅ 可抄 | |
| SAFEARRAY | xarial/codestack | ✅ MIT | `visual-basic/data-sets/array/`(6 .vba) | ✅ 可抄 | |
| 文档管理范式 | xarial/codestack | ✅ MIT | `solidworks-api/application/documents/`(7 篇) | ✅ 只读参考 | 打开/保存/关闭范式 |
| mock adapter 分层 | vespo92/SolidworksMCP-TS | ✅ MIT | mock-solidworks-adapter | ✅ 可抄 | 测试不连 SolidWorks 的分层做法 |
| 宏生成器 | vespo92/SolidworksMCP-TS | ✅ MIT | `src/tools/vba-advanced.ts` | ✅ 可抄 | |
| 外观/材料 | xarial/codestack | ✅ MIT | `solidworks-api/document/appearance/` | ✅ 可抄 | render material / display state |
| 装配上下文 | xarial/codestack | ✅ MIT | `solidworks-api/document/assembly/context/`(4 .vba) | ✅ 可抄 | |
| SolidDNA 模板 | angelsix/solidworks-api | ✅ MIT ⚠ | `Templates/SolidDNA` | ✅ 可抄 | 免弹模板设置 |
| ~~codestack 建视图~~ | xarial/codestack | ✅ MIT | — | ❌ **零命中** | 四个建视图符号全仓 0 命中 |
| ~~alisamsam 27 个 .vbs 语料~~ | alisamsam/Solidworks-MCP | ✅ MIT | `scripts/history/*.vbs` | ⚠ **价值被高估** | 实为运行时脚本历史日志，非精心整理的语料 |
| ~~q3ds Simulation~~ | Bennyco86/q3ds-solidworks-mcp | 👁 AGPL | — | ⛔ **只读思想** | 14 处 cosworks 提及，禁止抄文本 |
| ~~pySW~~ | kalyanpi4/pySW | 👁 GPL | — | ⛔ 只读思想 | |
| ~~pengxiaoan~~ | pengxiaoan/… | ⛔ 无许可 | — | ⛔ 只读思想 | |
| ~~ddeng-skills~~ | walterkken/… | ⛔ 全版权 | — | ⛔ 只读方法论 | |
| ~~SolidPilot 四层架构~~ | eyfel/mcp-server-solidworks | 👁 AGPL | — | ⛔ 只读思想 | |
| ~~offline-solidworks-api-docs~~ | pedropaulovc/… | ⛔ 无许可 | — | ⛔ 只读思想 | 亦是 `C:\swapi` 来源，产物不可再分发 |

---

## 三、缺口表（官方接口族 | 上游现状 | 拟采取来源）

> 优先级：① 上游相邻模块 → ② MIT 现成实现 → ③ MIT 文档/示例 → ④ AGPL/无许可**思想** → ⑤ 照官方签名自写

| # | 官方接口族 | 规模 | 上游现状 | 优先级 | 拟采取来源 | 目标产出 |
|---|---|---|---|---|---|---|
| **G1** | **cosworks Simulation 全域** | 84 接口 / 363 枚举 | ⛔ 空白 → ✅ **本轮补齐可签名部分** | ②+⑤ | alisamsam 结构 + cosworks DLL 反射签名 | `scripts/sw_simulation.py` |
| G1.1 | 入口链 `GetAddInObject`→`CosmosWorks`→`ActiveDoc`→`StudyManager` | — | ✅ 已建 | ⑤ | `ICwAddincallback` 反射 | 同上 |
| G1.2 | `ICWStudyManager` 建/取研究 | CreateNewStudy3/2/1 + GetStudy | ✅ 已建 | ⑤ | 反射 | 同上 |
| G1.3 | 载荷夹具（**仅 7 个有签名**） | 34 个 Add* 中 7 个可做 | ✅ 已建 3 个（AddRestraint/AddForce/复制） | ⑤ | 反射 | 同上 |
| G1.4 | `ICWStudy` 网格/求解 | `CreateMesh(3参)` / `RunAnalysis(零参)` | ✅ 已建 | ⑤ | 反射 | 同上 |
| G1.5 | **11 类连接件** | 11 | ⛔ **不提供** | — | 签名无来源（CHM 空壳） | 记入空缺段 |
| G1.6 | **27 个载荷方法**（压力/辐射/温度/重力/弹簧/轴承…） | 27 | ⛔ **不提供** | — | 同上 | 记入空缺段 |
| G1.7 | 结果后处理 | — | ⛔ **不提供** | — | `ICWResults` 无对应方法 | 记入空缺段 |
| G1.8 | 拓扑优化 10 约束 | 10 | ⛔ 本轮不做 | — | 反射有清单未逐个核签名 | 下一轮评估 |
| **G2** | **工程图建视图** | `IDrawingDoc`274 + `IView`461 + `IModelView`75 + `ISectionViewData`35 | ✅ **已覆盖**（子技能 2033 行/53 函数），但**查出 2 处签名缺陷并已修** | — | 本轮已完成签名审计 | `docs/signature-audit.md` 批次 2 |
| G2.1 | `CreateDetailViewAt4` 实参 7 vs 官方 12 | — | ❌ 缺陷 | ⑤ 官方签名 | ✅ **已修**（补齐 12 参 + 三个枚举字典） |
| G2.2 | `InsertBomTable4` 挂错对象 + 实参 7 vs 9 | — | ❌ 缺陷 | ⑤ 官方签名 | ✅ **已修**（改走 `IModelDocExtension`，补齐 9 参） |
| G2.3 | `swBomType_e` 文档枚举 1/2 写反 | — | ❌ 缺陷 | ⑤ `C:\swapi\enums` | ✅ **已修**（1=仅零件 / 2=仅顶层） |
| G2.4 | `_safe_member` 包裹的全部调用（实测 **140 个**） | — | ⚠ → ✅ **本轮完成** | ⑤ 官方签名 | **已修**：`IDrawingDoc.GetSheet` 成员不存在（2 处，正确写法是参数化属性 `Sheet`）；`ICWStudyManager.CreateNewStudy` 少传 1 参（1 处） |
| **G3** | **钣金深化** | 18 接口族 / 388 成员 | ⚠ **薄**（164 行 4 函数） | ② | codestack `.vba` + 上游 `sw_sheet_metal` 扩写 | `scripts/sw_sheet_metal` 扩写 |
| G3.1 | `IHemFeatureData` 翻边 | 18 | 弱 | ② | CHM sldworksapi | 同上 |
| G3.2 | `IMiterFlangeFeatureData` 斜接法兰 | 24 | 弱 | ② | CHM sldworksapi | 同上 |
| G3.3 | `ISweptFlangeFeatureData` 扫掠法兰 | 31 | ✅ **本轮补齐** | ⑤ 反射签名 | `create_swept_flange` + `SweptFlangeSpec` |
| G3.4 | `IGussetFeatureData` 加强筋 | 18/30 | ✅ **上一轮补齐** | ⑤ 反射签名 | `create_gusset` + `GussetSpec` |
| G3.5 | `ILoftedBendsFeatureData` 成形百叶 | 18 | 弱 | ② | CHM sldworksapi | 同上 |
| G3.6 | `IBaseFlangeFeatureData` 基础法兰 | 53 | 弱 | ② | CHM sldworksapi | 同上 |
| **G4** | **SWRoutingLib 路由** | 28 接口 / 26 枚举 | ⛔ 无（`routing_review` 是中性校验，非 API） | ⑤ | 反射 | `scripts/sw_routing.py`（仅签名级声明） |
| **G5** | **sldcostingapi 成本** | 28 / 24 | ⛔ 无 | ⑤ | 反射 | `scripts/sw_costing.py`（仅签名级） |
| **G6** | **swdocumentmgr PDM** | 296 / 65 | ⛔ 无 | — | — | **本轮不补**（需 PDM 许可证，296 接口超出本轮缝合能力，见下） |
| **G7** | **fworks Toolbox** | 2 / 10 | ⛔ 无 | ⑤ | 反射 | 并入 `sw_simulation` 的材料接口或单列小模块 |
| G8 | `ISeam2`/`IFeatureRef`（域 10） | 2 类型 | `C:\swapi` 缺 | ⑤ | CHM sldworksapi 复查 | 复查后定 |
| G9 | `ISaveAsOptions`/`ISaveAsInfo`（域 11） | 2 类型 | `C:\swapi` 缺 | ⑤ | CHM sldworksapi 复查 | 复查后定 |
| G10 | `swCustomPropertyType_e` 等（域 12） | 2 枚举 | `C:\swapi` 缺 | ⑤ | CHM swconst 册复查 | 复查后定 |
| **G11** | **设计表 `IDesignTable`（域 12，40 成员）** | 40 | ⛔ **不提供** | — | — | **入口两套官方源均查不到，见下** |
| G12 | 焊件接口族逐个核签名（域 6） | 14 族 / 170 | 部分 | ⑤ | 反射 | 本轮未做 |

### G11 的查证过程（记「查不到」而不是猜）

`IDesignTable` 这个**类型**在 `C:\swapi\types\IDesignTable\` 有 40 个成员页，看着很完整。
但**接口名不等于入口**（域 7 曲面那次的教训）：

| 官方源 | 查「谁返回 `IDesignTable`」 | 结果 |
|---|---|---|
| interop DLL 纯元数据反射 | 扫 `sldworks.dll` 全部 **1032 个接口** | ❌ **无任何接口声明返回它** |
| CHM `sldworksapi` 册 | 按文件名搜 `DesignTable` | ❌ 只有 `IDesignTable` 自己的 4 个页（`.html`/`_members`/`_methods`/`_properties`），**无任何接口的 `~GetDesignTable` 页**；仅见 `DPartDocEvents_OpenDesignTableNotifyEventHandler` 一类**事件**页 |

⇒ 官方只把设计表暴露成**文档级事件**（`OpenDesignTableNotify` / `CloseDesignTableNotify`），
**没有脚本创建入口**。按 AGENTS.md 铁律 5，本模块不提供任何设计表封装。

---

## 四、本轮结论与下一步

### 可缝合（本轮目标）

1. **G1 Simulation** —— 有 MIT 结构可依、有反射签名可依，**但只有 7/34 个载荷方法有签名来源**，
   其余 27 个标「查不到」。这意味着 `sw_simulation.py` **只能做到载荷夹具的 7 个方法**，
   11 类连接件中有 8 类无签名，**不能硬编**。
2. **G2 工程图建视图** —— 缺口最实（三个空桩 + 1456 官方成员），
   且 `C:\swapi` + CHM sldworksapi 双源可用，是本轮**性价比最高**的一项。
3. **G3 钣金深化** —— 上游模块在，扩写即可，双源可用。

### 明确不补

- **G6 PDM**：296 接口 / 4,683 成员，需 PDM 许可证且本机不可达。
  按 §九 停止条件 2 的精神，这属于「无法缝合」，写进 `harvest-report.md` 的「仍然空缺」段。
- **G4 Routing / G5 Costing**：可做**签名级**能力声明（接口清单 + 加载前提），
  但**不能声称可执行**。这是「覆盖」与「可用」的区别，报告里要写清。

### 下一步（轮次 3 起）

1. **G3 钣金深化**（上游仅 164 行 4 函数 vs 官方 388 成员，双源可用）
2. **G1 Simulation**（按 7 个有签名的载荷方法做，27 个标缺口）
3. **G2.4** 补齐 `_safe_member` 6 组调用的签名比对
4. 复查 G8/G9/G10 三个 `C:\swapi` 缺失项
5. 每项产出：代码 + `tests/test_*.py` + 来源头注释 + 本表打勾

### 轮次 2 已完成

- **G2 工程图**：降级为「已覆盖但有缺陷」，完成签名审计，**修复 2 处**：
  - `CreateDetailViewAt4` 实参 7 → **12**（官方 12 参）
  - `InsertBomTable4` 挂错对象 → 改走 `IModelDocExtension`，实参 7 → **9**
  - 附带修正 `swBomType_e` 文档枚举 **1/2 写反**（官方 1=仅零件、2=仅顶层）
  - 交付 `docs/signature-audit.md` + `tests/test_drawing_signature_contract.py`（8/8 通过，零 pytest 依赖）
- **G2.1 `NewDocument` 未纳入**：工程图文档由子技能通过既有会话链取得，
  本轮未发现该调用点，故不列为缺口（此前误列）。

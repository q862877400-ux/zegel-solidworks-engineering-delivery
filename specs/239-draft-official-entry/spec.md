# spec 239 · 拔模特征的**官方创建入口**（`CreateDefinition` 之外的路径）

> **状态**：离线切片（不连 SolidWorks、不跑 COM）。
> **来源**：上一轮交接单 `output/AUTO_HANDOFF.md` ② 待办 2 —— ★ **先量找到官方页**（见 §二）。

## 一、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | **先量**：在官方文档树里穷举「创建拔模特征」的入口，并判定哪一个是**未被取代**的 | `C:\swapi\types\IFeatureManager\InsertMultiFaceDraft.md` · `C:\swapi\types\IModelDoc2\InsertMfDraft{,2}.md` · `C:\swapi\types\IFeatureManager\{DraftXpertChange,DraftXpertRemove}.md` | 官方文档（非开源，无第三方许可） |
| FR-002 | `sw_sheet_metal.create_draft` **必须改走**官方入口 `IFeatureManager::InsertMultiFaceDraft`（6 参），**不得**再经 `CreateDefinition` | 同上 + `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt:6970` | 同上 |
| FR-003 | `DraftFeatureSpec` 必须能表达官方 **6 个形参**（`angle` / `reverse_direction`↔`FlipDir` / `edge_draft` / `prop_type` / `is_step_draft` / `is_body_draft`）；`prop_type` 越界（官方只列 0–4）必须在**进 COM 前**拒绝 | `InsertMultiFaceDraft.md` 的 `## Parameters` | 同上 |
| FR-004 | 官方 `Angle` 是**弧度**、本仓 spec 层是**度** ⇒ COM 边界处必须显式转换 | 同页「Draft angle in radians」 | 同上 |
| FR-005 | 新判据码 **`unsupported-path`**（加在 `scripts/check_cd_host_scope.py`，与 238 的三码同门禁）：站点 `unmapped` 的常量**没有任何**官方宿主页收录 ⇒ 代码走了**官方不支持**的路径 ⇒ 必须表态官方替代入口 | 本项目自身（元门禁） | 本仓库 MIT |
| FR-006 | `unsupported-path` 的声明契约 `#: create-entry: alt <官方成员名\|unknown> <理由>`，**三条自证**：成员页必须存在 · **不得**带 `Obsolete` · `unknown` 必须写理由（有界逃生门） | 本项目自身 + 官方页的 `Obsolete. Superseded by …` 惯例 | 本仓库 MIT |
| FR-007 | 237/238 的 `sites` 棘轮**正当下调** 10 → 9（一个站点因改走官方入口而消失）⇒ 必须**补一条内容断言**接住「写回去」（本码 + FR-008） | 本项目自身 | 本仓库 MIT |
| FR-008 | `sw_weldment` 的 `swFmMateProfileCenter` 站点补 `alt CreateMateData` 声明（官方替代入口 = `IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24)` + `CreateMate`，两页**均无** `Obsolete`）—— ★ 代码**本轮未改**，登记为待办 | `C:\swapi\types\IAssemblyDoc\CreateMateData.md` · `CreateMate.md` · `C:\swapi\enums\swMateType_e.md` | 官方文档 |
| FR-009 | 状态表 `SHEET_METAL_RUNTIME_STATUS["create_draft"]` 必须是 `None`（**未测**），**不得**是 `True`；工具层 doc 同步（旧措辞标「已作废」） | 本项目自身 | 本仓库 MIT |

## 二、★★★ 先量：官方入口是哪一个

穷举结果（`find types -name "*Draft*"` + `grep -rln "InsertDraft|InsertMultiFaceDraft|DraftXpert"`）：

| 候选 | 结论 | 证据 |
|---|---|---|
| `IFeatureManager::InsertMultiFaceDraft` | ★★ **未被取代的官方入口** | 该页**无** `Obsolete` 标注（`grep -c -i obsolete` = **0**）；签名 6 参 |
| `IModelDoc2::InsertMfDraft2` | **已废弃** | 页首逐字：`Obsolete. Superseded by [[IFeatureManager::InsertMultifaceDraft]]` |
| `IModelDoc2::InsertMfDraft` | **已废弃** | 同上 |
| `IFeatureManager::DraftXpertChange` / `DraftXpertRemove` | 不是创建入口 | 名字与语义都是「改 / 删」 |
| `IFeatureManager::CreateDefinition(swFmDraft)` | **官方不支持** | `swFmDraft` 不在两个宿主页（`IFeatureManager` / `IMotionStudy`）的 `Type` 清单里（spec 238 已证）；本仓真机回 `None` |

⇒ ★★ **官方自己指认了取代方向**：**不是** `IModelDoc2` 族，而是 `IFeatureManager::InsertMultiFaceDraft`。
三源一致：官方页（6 参）· 官方页的取代链 · 反射转储 `Feature InsertMultiFaceDraft(Double, Boolean, Boolean, Int32, Boolean, Boolean)`。

## 三、★★ 先量发现的**新盲区**（FR-005 的由来）

238 的三条判据（`should-map` / `host-mismatch` / `ambiguous-host`）**都只在「常量被官方收录」时生效**
⇒ 「代码用了官方**根本不在** `CreateDefinition` 域里的常量」三条**全都不管**，读数上与「一切正常」同形。
真树现状：`swFmDraft`（`sw_sheet_metal.py`）与 `swFmMateProfileCenter`（`sw_weldment.py`）。

## 四、验收（可跑命令）

```
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/check_cd_host_scope.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/check_create_definition_site_disposition.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_draft_official_entry tests.test_cd_host_scope tests.test_cd_site_disposition
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```

## 五、不做 / 明确不宣称

- ★ **不宣称 `create_draft` 真机可用**：本规格是**离线切片**，未跑 COM（需业主另行授权）。
- ★ `sw_weldment.create_profile_center_mate` **本轮不改**（只登记官方替代入口）—— 见 FR-008 的待办。
- ★ `face_ref` 形参仍未使用（属 `tool_specs_batch4.py` 已登记的真实缺陷），本规格不动它。
- ★ 不做「官方 `CreateMateData` 的正确调用序」的改造 —— 那是下一轮的事。

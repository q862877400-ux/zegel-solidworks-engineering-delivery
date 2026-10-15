# spec 240 · 型材中心配合的**官方创建入口**（`IAssemblyDoc::CreateMateData` + `CreateMate`）

> **状态**：离线切片（不连 SolidWorks、不跑 COM）。
> **来源**：上一轮交接单 `output/AUTO_HANDOFF.md` ② 待办 1 + `specs/239-draft-official-entry/spec.md` FR-008
> —— ★ **官方依据已备齐**（239 已查证），本规格**不重查**，只**先量调用点**再改代码。

## 一、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | **先量**：`scripts/sw_weldment.py` 的 `CreateDefinition` 站点**有几个**、`_create_from_definition` 的调用方**各自传什么常量** | `scripts/check_interface_member_ownership.py::scan_sites` | 本仓库 MIT |
| FR-002 | `sw_weldment.create_profile_center_mate` **必须改走**官方入口 `IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24)` + `IAssemblyDoc::CreateMate(data)`；**不得**再经 `IFeatureManager::CreateDefinition` | `C:\swapi\types\IAssemblyDoc\CreateMateData.md` · `CreateMate.md` · `C:\swapi\enums\swMateType_e.md:34` | 官方文档（非开源，无第三方许可） |
| FR-003 | 调用序必须与官方 `## Remarks` 的 5 步一致：① `CreateMateData` → ②/③ 设 5 个属性 → ④ `CreateMate`；`CreateMateData` 回 `None` 时**不得**继续调 `CreateMate` | `C:\swapi\types\IAssemblyDoc\CreateMate.md` 的 `## Remarks` | 同上 |
| FR-004 | **不得**用已废弃的 `IAssemblyDoc::AddMate{,2,3,4,5}` 族（官方**五页全带** `Obsolete`） | `C:\swapi\types\IAssemblyDoc\AddMate*.md`（`grep -c -i obsolete` = 1/1/1/2/2） | 同上 |
| FR-005 | 无调用方的共用骨架 `sw_weldment._create_from_definition` **整体删除**（留墓碑注释）—— 保留它会让站点因 `fm_type` 无法绑定而退化成 `dynamic` | 本项目自身 + `scripts/check_create_definition_site_disposition.py` 的 `[reader-too-narrow]` 自证 | 本仓库 MIT |
| FR-006 | `SW_FM_MATE_PROFILE_CENTER`（101）**保留**为证据锚点（「官方枚举里确有这个 fm 条目，但不在任何 `CreateDefinition` 宿主页的 `Type` 清单里」）；新增 `SW_MATE_PROFILE_CENTER = 24` | `C:\swapi\enums\swMateType_e.md:34` · `_raw/reflect/` 的 `swFeatureNameID_e` 反射 | 官方文档 + 本仓库 MIT |
| FR-007 | 两条棘轮**正当下调**：`check_create_definition_site_disposition` 的 `sites` 9→8 · `unmapped` 1→**0**；`check_cd_host_scope` 的 `sites` 9→8 · `no-host` 1→**0**。★ 必须**补内容断言**接住「写回去」 | 本项目自身 | 本仓库 MIT |
| FR-008 | 新判据必须**同时收点式调用与裸名调用**，且**经共用骨架的间接路径**也要判出来（spec 239 的「只看点式调用 = 空判据」教训） | 本项目自身 | 本仓库 MIT |
| FR-009 | 既有契约测试 `tests/test_extended_modules_contract.py` 里钉住**旧行为**（`fm 101`）的用例必须随实现改写为钉住**官方入口** | 本项目自身 | 本仓库 MIT |
| FR-010 | 工具层 `mcp-server/tool_specs_batch35.py` 的 `doc` 同步（写明走官方入口、不用 `AddMate*` 族） | 本项目自身 | 本仓库 MIT |

## 二、★★★ 先量：调用点与站点（FR-001 的读数）

```
python -B -c "import sys;sys.path.insert(0,'scripts');import check_interface_member_ownership as c;..."
⇒ CreateDefinition 站点 **9**（改前），其中 `sw_weldment.py:688` 的常量是 `swFmMateProfileCenter`
⇒ `_create_from_definition` 的调用方**只有 1 个**：`create_profile_center_mate`（第 830 行）
```

★★ **交接单的前提又被核出是错的（第九次）**：239 交接单写着
「`sw_weldment._create_from_definition` 是**共用骨架**，还有别的调用方（`swFmWeldBead` 等）」
—— ★ **实测只有 1 个调用方**。`swFmWeldMemberFeat` 那条错误的创建入口**早已在更早的轮次删掉**
（`sw_weldment.py` 第 660 行的历史注释记着）。
⇒ 因为只有 1 个调用方，`_create_from_definition` 改走官方入口后**整个函数都没有存在理由** ⇒ FR-005。

## 三、★★ 官方入口的三源一致

| 源 | 读数 |
|---|---|
| 官方页 ① | `IAssemblyDoc.CreateMateData(System.int Type)`；`## Remarks` 的 `Type` 清单**含** `swMatePROFILECENTER`；**无** `Obsolete` |
| 官方页 ② | `IAssemblyDoc.CreateMate(System.object MateData)`；`## Remarks` 5 步调用序 + 逐条列出 `IProfileCenterMateFeatureData`；**无** `Obsolete` |
| 官方页 ③ | `IProfileCenterMateFeatureData\_overview.md`：5 属性 / **0 方法**；`EntitiesToMate` 或预选（Mark = 1） |
| 官方枚举 | `swMateType_e.md:34` → `\| swMatePROFILECENTER \| 24 \|` |
| 反射转储 | `_raw/reflect_sldworks/iface_sldworks.txt` → `IProfileCenterMateFeatureData` 段（5 个 `get_`/`set_` 成对） |
| 官方示例 | `examples/Create_Profile_Center_Mate_Example_VB.md` → `Set swMateData = swAssy.CreateMateData(24)` → 设属性 → `Set feat = swAssy.CreateMate(swProfileMateData)` |

★★ **反例（为什么不能换回前代入口）**：`AddMate` / `AddMate2` / `AddMate3` / `AddMate4` / `AddMate5`
五页**全部带** `Obsolete` ⇒ 那是**已废弃**的一族。

## 四、验收（可跑命令）

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_create_definition_site_disposition.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_cd_host_scope.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_mate_official_entry tests.test_cd_host_scope tests.test_cd_site_disposition
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B -m pytest tests/test_extended_modules_contract.py -q
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```

## 五、不做 / 明确不宣称

- ★ **不宣称型材中心配合真机可用**：本规格是**离线切片**，未跑 COM（需业主另行授权）。
- ★ **不动** `scripts/sw_assembly.py::add_mate`（它包装 `AddMate5`，官方虽已标废弃，但
  `## Remarks` 要求按 `mate_type` 分流 + 装配域 `level` 仍是 `stitched` ⇒ **需先真机验证**，
  见 `sw_assembly_doc.add_mate` 的记档保留）。
- ★ **不宣称** `CreateMateData` 在 pywin32 迟到绑定下一定可达 —— 那要真机（事实 47 那族）。
- ★ 不补 `MANUAL_MAP`：`swFmMateProfileCenter` **不属于** `IFeatureManager::CreateDefinition`（238/239 已证）。

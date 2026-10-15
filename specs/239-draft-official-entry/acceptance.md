# acceptance 239 · 验收记录

> 全部为**离线**读数（未连 SolidWorks、未跑 COM）。判据解释器 = 受管 3.13.12；
> 门禁全套 = `pythoncore-3.14-64`。

## 一、判据读数

| 判据 | 命令 | 读数 |
|---|---|---|
| ★★ **红基线（加码后、改实现前）** | `python -B scripts/check_cd_host_scope.py` | `[unsupported-path] sw_sheet_metal.py:396` · `[unsupported-path] sw_weldment.py:687` · `站点 10 · 点名 1 · 无宿主 2 · 违规 2 · [FAIL] · exit 1` |
| 239 门禁（改后） | 同上 | `官方宿主页 2 个：IFeatureManager / IMotionStudy · 站点 9 · 常量被官方点名 1 · 收录常量 46 · 无宿主常量站点 1 · [PASS] · exit 0` |
| 237 门禁 | `python -B scripts/check_create_definition_site_disposition.py` | `站点 9 · checked 6 · unmapped 1 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0` |
| 238/239 判据 | `python -B -m unittest tests.test_cd_host_scope` | `Ran 16 tests · OK`（★ 238 原 10 例 + 239 新 6 例） |
| 237 判据 | `python -B -m unittest tests.test_cd_site_disposition` | `Ran 15 tests · OK` |
| 239 新判据 | `python -B -m unittest tests.test_draft_official_entry` | `Ran 11 tests · OK` |
| 工具层 doc 回归 | `python -m pytest tests/test_tool_specs_batch4.py tests/test_sheet_metal_doc_freshness.py -q` @3.14.7 | `13 passed, 2 skipped` |
| 合并聚焦回归 | 上述六份（含 `test_tool_specs_batch93`） | `Ran 42 tests · OK`（`test_tool_specs_batch4` 是 pytest 风格 ⇒ 单列） |
| ★ **门禁全套** | `pythoncore-3.14-64 -B scripts/release_check.py` | **`EXIT 0` · `status pass` · `missing []`** · `cd_host_scope: pass` · `gate_wiring` 仍 **44 道**（★ 本规格**未新增**门禁文件） |
| 打包副本 | `python -B scripts/sync_bundled_skill.py` | `status pass · files 471 · pruned []` |

## 二、★★ 红基线（每条判据都能红，逐条取证）

### 2.1 门禁侧
加第四码 `unsupported-path` 之后、**改实现之前**：`违规 2 处 · exit 1`（两条都是真靶子）。

### 2.2 实现侧（★ 把判据跑在 `git HEAD` 的实现上）
`git show HEAD:scripts/sw_sheet_metal.py` ⇒ 用 `output/_probe239_redbaseline.py` 逐条跑：

| 判据 | HEAD 版读数 | 结论 |
|---|---|---|
| ① 不走 `CreateDefinition` 那条路 | 调用名 = `['_create_from_definition','bool','float','validate']` ⇒ **红** | ✓ 能红 |
| ② 调 `InsertMultiFaceDraft` 且 **6** 参 | 无该调用 ⇒ **红** | ✓ 能红 |
| ③ 度 → 弧度转换 | 无 `radians` ⇒ **红** | ✓ 能红 |
| ④ 不再用 `SW_FM_DRAFT` | 用了 ⇒ **红** | ✓ 能红 |
| ⑤ 状态表 = `None`（未测） | `False` ⇒ **红** | ✓ 能红 |

★★ **本轮踩到并当场修掉的空判据**：首版「不走 `CreateDefinition`」**只看点式调用** ⇒
HEAD 版里 `CreateDefinition` **藏在**共用骨架 `_create_from_definition` 里 ⇒ 读成 **0 个调用**
⇒ 该判据在改前**也是绿的**（**空判据**）。⇒ 修法：把 `_create_from_definition` 也列为禁止项 +
`_calls()` 同时收**裸名调用**。（与 233「窄读取器读出 0 也会骗人」同族。）

## 三、★★ 核心事实

1. ★★★ **官方自己指认了取代方向**：`IModelDoc2::InsertMfDraft` / `InsertMfDraft2` 两页逐字写着
   `Obsolete. Superseded by [[IFeatureManager::InsertMultifaceDraft]]` ⇒ 拔模的官方入口是
   **`IFeatureManager::InsertMultiFaceDraft`**（该页 `grep -c -i obsolete` = **0**）。
   ★ 三源一致：官方页 6 参 · 取代链 · 反射转储 `(Double, Boolean, Boolean, Int32, Boolean, Boolean)`。
2. ★★★ **238 的三码有一个方向性盲区**：三条**都只在「常量被官方收录」时生效** ⇒
   「代码用了官方**根本不在** `CreateDefinition` 域里的常量」三条**全都不管**，读数上与「一切正常」同形。
   ⇒ 本规格补第四码 `unsupported-path`（真树靶子 2 个 → 修完 1 个）。
3. ★★ **`swFmMateProfileCenter` 的官方替代入口已查明**（**代码本轮未改**，只登记）：
   `IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24)` + `IAssemblyDoc::CreateMate(data)` ——
   两页**均无** `Obsolete`；`CreateMate` 的 `## Remarks` 逐条列出 `IProfileCenterMateFeatureData`，
   `CreateMateData` 的 `Type` 清单含 `swMatePROFILECENTER`（`swMateType_e.md:34` = 24）。

## 四、★ 本轮踩到的坑（3 条）

1. ★★ **空判据**：见 §二.2 —— 「只看点式调用」会把**经由共用骨架**的间接路径读成 0。
2. ★★ **测试导入 `scripts.sw_sheet_metal` 会挂死**：受管 3.13.12 缺 comtypes/win32com ⇒
   `sw_preflight` **交互式**问「是否授权 AI 自动为您配置本地环境？[Y/N]」⇒ 卡住（实测 SIGTERM）。
   ⇒ 修法：判据里**桩掉 `sw_preflight`**（宽松桩 + `import_com_dependencies` 返回 `(None,None,None)`），
   并把 `ROOT/scripts` 也加进 `sys.path`（否则 `sw_sheet_metal` 的 `except ImportError` 兜底找不到 `sw_connect`）。
3. ★★ **两种声明必须并存**：237 的 `cd-site:` 声明**只能紧贴**调用行（它只看第一行非空行）⇒
   本码的 `create-entry:` 只能排它上面 ⇒ 本码的读取器改成「**向上连续扫 `#:` 块**」（遇非 `#:` 行即停）。
4. ★ **棘轮下调要补内容断言**：`sites` 10 → 9 后，计数棘轮接不住「有人写回 `CreateDefinition(swFmDraft)`」
   ⇒ 由 `unsupported-path` 码 + 判据第 ⑦ 条接住（★ 已写进 `plan.md` §四.5）。

## 五、未过门 / 不宣称

- ★★ **不宣称 `create_draft` 真机可用**：本规格**未跑 COM** ⇒ 状态表刻意写 `None`（未测）。
- `sw_weldment.create_profile_center_mate` **未改**（只登记官方替代入口）⇒ 下一轮 `specs/240-*`。
- `alt` 自证只查「成员页存在 + 不带 `Obsolete`」⇒ **不**校验调用序 / 实参语义。
- `unsupported-path` 只覆盖 `CreateDefinition` 站点；别的「官方不支持的路径」不在射程内。
- 宿主/入口判定全是**静态**的；223 的 8 条既有红未修；未提交未部署。

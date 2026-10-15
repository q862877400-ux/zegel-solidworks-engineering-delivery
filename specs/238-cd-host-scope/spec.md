# spec 238 · `CreateDefinition` 站点的**宿主域**

> **状态**：离线切片（不连 SolidWorks、不跑 COM）。
> **来源**：上一轮交接单 `output/AUTO_HANDOFF.md` ② 待办 2 —— ★★ **先量当场推翻它**（见 §二）。

## 一、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | 官方 `CreateDefinition` **宿主页清单**必须被显式表达（`IFeatureManager` + `IMotionStudy`），**不得**再把「宿主」当隐含前提 | `C:\swapi\types\IFeatureManager\CreateDefinition.md` · `C:\swapi\types\IMotionStudy\CreateDefinition.md` | 官方文档（非开源，无第三方许可） |
| FR-002 | `host_pages()` 收**逐条点名**的条目（`swFmX ([[IIface]])`）⇒ 直接映射（**官方断言**）；`host_consts()` 收**所有**宿主页的 `Type` 清单 ⇒ 回答「这个常量属于哪个宿主」 | 同上（`IMotionStudy` 页每条都带 `[[接口]]`） | 同上 |
| FR-003 | `scan_sites()` 每条站点记录新增 `hosts` 字段；诊断打印「官方宿主页=…」 | 本项目既有实现 | 本仓库 MIT |
| FR-004 | 新门禁 `scripts/check_cd_host_scope.py`：`should-map` / `host-mismatch` / `ambiguous-host` 三码 + 下界冻结 + 零检查即红 + `[SKIP]` 便携 | 本项目自身（元门禁） | 本仓库 MIT |
| FR-005 | 237 的下界同步：`BASELINE_CHECKED 5 → 6`、`BASELINE_UNMAPPED 3 → 2`；删 `sw_motion.py` 的多余声明 | 本项目自身 | 本仓库 MIT |
| FR-006 | 两个**无官方宿主**站点的 `unmapped` 声明写明**精确证据**（不是「映射表没有」） | 本项目自身 | 本仓库 MIT |

## 二、★★★ 先量：推翻交接单待办 2

交接单写的是「给 3 个未映射常量（`swFmDraft` / `swFmAEMRotationalMotor` / `swFmMateProfileCenter`）
逐条读候选接口的 `## Description` 补 `MANUAL_MAP`」。**先量结果**：

| 常量 | 官方 `CreateDefinition` 宿主 | 证据 |
|---|---|---|
| `swFmAEMRotationalMotor` | **`IMotionStudy`** | 该页 `## Parameters` 逐条点名：`swFmAEMRotationalMotor ([[ISimulationMotorFeatureData]])` |
| `swFmDraft` | **无** | 两个宿主页的 `Type` 清单里都没有；只有 `swFeatureNameID_e.md:57` 收录。★ 本仓另有**真机证据**：`CreateDefinition(3)` 返回 `None`（`sw_sheet_metal.create_draft` 的来源块） |
| `swFmMateProfileCenter` | **无** | 只有 `swFeatureNameID_e.md:92` 收录；没有任何官方文档把它绑到 `CreateDefinition` |

⇒ ★ **照字面补 `MANUAL_MAP` 会污染一张本来正确的表**（把「别的宿主的常量」或「官方不支持的常量」
写成「本宿主返回的接口」）—— 与「照错前提改会把正确的登记改错」同族（`memory/MEMORY.md` §五）。

**真缺陷**（本规格的靶子）：映射表**只**认 `IFeatureManager` ⇒
「常量属于别的宿主」与「官方根本不支持它」在读数上**同形**（都是 `unmapped`）。

## 三、验收（可跑命令）

```
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_cd_host_scope.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_interface_member_ownership.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_create_definition_site_disposition.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_cd_host_scope tests.test_cd_site_disposition
```

## 四、不做什么（边界）

- **不补 `MANUAL_MAP`**（§二）。
- **不解析接收者变量的运行期类型** —— 宿主判定是**页级**的（常量属于哪个官方页）。
- **不递归/不推断** `IFeatureManager` 页的**散文标签**（那是**推断**，仍走文本匹配）。
- **不动** `mcp-server/**`、`tools/**`（只扫 `scripts/*.py`，与原诊断一致）。

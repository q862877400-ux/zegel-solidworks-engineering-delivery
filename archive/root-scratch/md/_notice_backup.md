# Third-Party Notices

**本文件履行 MIT 与 Apache-2.0 的分发义务。** 它与 `LICENSE` 一起随本仓库分发。

**版本**：2026-10-01 · 对应代码副本提交见本文件末「登记历史」

---

## 〇、本项目是什么

**这是一个自建仓库，不是下列任何一家的 fork。**
上游 `wzyn20051216/solidworks-automation-skill` 与四家外部 MCP 项目
**都是来源之一，与本项目自身既有模式并列**（依据见 `AGENTS.md` 铁律 1）。

**⚠ 本文件如实区分「已包含」与「已评估但尚未并入」** ——
把未并入的东西写成已并入，是**归属造假**，比遗漏更严重。

---

## 一、本项目**实际包含**的第三方代码

### 1. `wzyn20051216/solidworks-automation-skill`（上游）

```
MIT License
Copyright (c) 2026 SolidWorks Automation Skill Contributors
```

**用到的部分**：
- `mcp-server/server.py` —— **一行未改**（45 个 MCP 工具的实现）
- 上游 49 个 `scripts/*.py` 模块
- `subskills/` 下的既有技能

**义务**：MIT 要求保留版权声明 ⇒ 上文版权行即为此。
**改动**：本仓库相对上游的**增量数字不写在这里** —— ★ **一个事实一个家**：
它以 `docs/harvest-report.md` 开篇那行为准（那行有**机器门禁** `scripts/check_report_freshness.py` 守着）。
改动过的文件在各自来源头注释里标明。
> ⚠ **2026-10-01（轮 57 → 轮 195）两段更正，都属同一种病**：
> ```
> · 本行原写「100 新增文件 / 13 改过文件」（更早轮次的数）
> · 轮 57 改成「179 个文件 / +126,7xx 行」并声明"本行只写量级，不再重复维护一个会腐坏的数字"
> ⇒ ★★★ 而轮 195 实测：**那个"量级"本身也腐坏了** —— 真实是 **343 个文件 / +155,707 行**（差近一倍）。
> ⇒ ★★ 教训：**"只写量级"仍然会腐坏** —— 只要数字**存在**，它就会随代码前进而失真。
>   真正的修法不是"写个粗略的"，而是**不在这里写**（指向唯一的家）。
> ```

### 2. `microsoft/UFO`（GUI 自动化模式）

```
MIT License
Copyright (c) Microsoft Corporation
```

**用到的部分**：
- `scripts/sw_gui_input.py` —— **配置驱动的输入层**（`input_text_api` / `input_text_enter` /
  `input_text_inter_key_pause` 那一套设计）
- `scripts/sw_jlcfa_fill.py` —— 沿用同一设计

**这是移植，不是引用**：模式借自其实现，代码为本项目所写。来源头注释在
`scripts/sw_gui_input.py` 顶部，已标明仓库与许可。

### 3. `Eduardof0nt/Solidworks-MCP-Server`（模具域的**思路**来源）

```
MIT License
Copyright (c) 2026 Eduardo Font Cruz
```

**用到的部分**：
- `scripts/sw_mold.py` —— 模具域的**动作集合**思路（「分型线 + 补孔面」这两个动作该做）
  来自该仓库的 `sw_client.py`（`parting_line` / `shut_off_surface` 两个方法）。

**⚠ 本项与上两项**性质不同：这里**没有移植它的代码**，只引用了它的**思路**。原因**：
该来源对模具域的**两个方法名都是错的**（`InsertPartingLines` / `InsertShutOffSurfaces`
在官方反射里查不到；官方真名是 `InsertMoldPartingLine(Boolean)` /
`InsertMoldShutOffSurface()`）。该来源系统性使用不存在的方法名
（焊件域 4/5 错、模具域 2/2 错），且 **0 个测试文件、未声明验证环境**。

**⇒ `scripts/sw_mold.py` 的每一行都是照出厂反射写的**，不是照该来源抄的。
本项登记在此是为履行 **MIT 的版权声明义务**（我们确实参考了它、并据此实现）。

**改动文件名录**：`scripts/sw_mold.py`（新增）、`tests/test_sw_mold_contract.py`（新增）、
`capabilities.yaml`（`mold_tools` 条目）。缺陷明细见工作区
`_raw/source-defects/Eduardof0nt.md`（含可重跑的核对命令）。

### 4. 第三方 Python 依赖

见 `pyproject.toml` / `requirements*.txt`（`mcp` / `pydantic` / `pywin32` / `comtypes` /
`jsonschema` / `ezdxf` / `numpy` 等）。**它们是依赖，不是内嵌代码**，
各自的许可随其分发包提供，此处不逐一列举。

---

## 二、已作为**能力来源**评估、但**尚未并入任何代码**的项目

> **⚠ 截至本版本，本项目未包含下列项目的任何源代码。**
> 它们出现在这里，是因为本项目**已把它们列入并入清单**
> （`docs/union-coverage-matrix.md` §五），**履行许可透明义务**，
> 并为将来并入预留登记位置。**一旦真的并入，会迁到上文 §一 并写明改动文件。**

| 项目 | 许可 | 版权声明 | 当前状态 |
|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | `Copyright (c) 2026 Eduardo Font Cruz` | **部分并入** —— 模具域的**思路**已用于 `scripts/sw_mold.py`；**代码未移植**（该来源的方法名在官方反射里查不到），详见 §一 第 3 项 |
| `andrewbartels1/SolidworksMCP-python` | MIT | `Copyright (c) 2025 ESPO Corporation` | **未并入** |
| `vespo92/SolidworksMCP-TS` | MIT | `Copyright (c) 2025 ESPO Corporation` | **未并入** |
| `Slacker-LLC/solidworks-mcp` | **Apache-2.0** | **`Copyright 2026 JIALE LIU`**（其 `NOTICE` 原文） | **未并入** |

**核验方式**（可重跑，证明上表不是印象）：

```powershell
cd C:\swprojects\sw-skill-fork
python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));print([c['id'] for c in d['capabilities'] if c.get('provenance')])"
# → ['mold_tools']   （**1 条**带 provenance：§一.3 的模具域条目；来源 Eduardof0nt，MIT，只取思路）
```
> ⚠ **2026-10-01（轮 195）更正**：这条注释**原写 `# → []`（0 条）**，而**实跑输出是
> `['mold_tools']`** —— ★ **与本文件 §一.3 和「登记历史」都自相矛盾**（那两处都写着 mold_tools 有 provenance）。
> ⇒ ★★ 一条**号称"可重跑核验"**的命令，其**预期输出写错了**，
> 那么它证明不了任何事（**它只是把印象写成了注释**）。
> ★ **已加一条测试**（`tests/test_notice_consistency.py` 的 `test_notice_runnable_check_matches_reality`）
> **实跑这条命令并比对注释** —— 于是这条"可重跑"**真的可重跑**了。

### `Slacker-LLC/solidworks-mcp` 的 Apache-2.0 义务（**预置，尚未触发**）

其 `NOTICE` 原文：

```
solidworks-mcp
Copyright 2026 JIALE LIU
```

**Apache-2.0 §4(d) 要求**：分发时必须保留其 `NOTICE` 内容，并**声明改动了哪些文件**。
**该义务在并入其代码的那一刻触发**（当前未触发）。届时需在本文件 §一 新增一节，含：
1. 上式 NOTICE 原文
2. 改动文件清单
3. 我们的改动说明

---

## 三、**明文不接触**的来源（AGENTS.md 铁律 2 红线）

以下类型**零接触**，不作为任何形式的来源，也不在本文件登记：
- 破解投递页 / 破解指南（`SolidWorks-CAD` / `Solidworks-Crack` 一类）
- AGPL / GPL / 无许可 / 全版权保留的代码 —— **只读思想，不抄代码不抄文本**（铁律 6）

---

## 四、将来并入时的登记格式

并入一件来源派生的东西时，**同一批**完成三件事：

1. **代码里**：来源头注释（`仓库: owner/repo` / `文件` / `定位` / 许可 / 未实测标注）
2. **`capabilities.yaml` 里**：该条目的 `provenance` 字段
   ```json
   {"repo": "owner/repo", "license": "MIT", "files": ["来源里的哪个文件"],
    "upstream_verified": "来源自己声明的验证环境（没有就空串）"}
   ```
3. **本文件里**：从 §二 上表迁到 §一，写明改动文件

**判据**（机器可查）：`docs/union-conventions.md` 规则 5 +
`scripts/check_union_conventions.py` 的 R6/R9/R10。

---

## 登记历史

| 日期 | 变化 |
|---|---|
| 2026-10-01 | 初版。如实区分「已包含」（上游 + microsoft/UFO）与「已评估未并入」（四家）。四家的许可与版权已逐份读真实 `LICENSE` 文件核到，不采信 README 徽章。 |
| 2026-10-01（轮 131）| **复核 + 加机器检查**。① 复核结论：`capabilities.yaml` 里 `level: source_verified` 的条目**仍为 0** ⇒ 第二节那句「尚未有来源派生的能力条目」**依然成立**；带 `provenance` 字段的条目**只有 `mold_tools` 一条**（`Eduardof0nt/Solidworks-MCP-Server`，MIT，**只取思路、没抄代码**，见 §一.3）。② 复核 §一.4 的依赖清单：`pyproject.toml` 与 `requirements*.txt` 对得上（`numpy` 在 `requirements-mesh.txt` / `requirements-occt.txt` 里，不是写错）。③ **新增机器检查** `tests/test_notice_consistency.py`（5 条）：**能力条目里出现的每个外部 owner 都必须在 NOTICE 里有登记**、`provenance` 四字段齐、repo 写 `owner/repo` 全名、Apache-2.0 义务点名到位、**登记历史必须不止一条** —— 也就是本节这条规则本身。 |

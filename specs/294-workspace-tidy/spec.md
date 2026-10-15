# Spec — **工作区整理：把仓库根 2814 个草稿归入 `archive/`（只搬不删）**

**Feature**: `specs/294-workspace-tidy/`
**日期**: 2026-10-10
**上游**: `README-workspace.md` §分类规矩（「根目录就是草稿区」）· `RESTART-HANDOFF.md` §三 第 5 条
（逐字：「根上有一批我的临时脚本 … 要么收进 `tools/`（若还有用），要么**归档** —— 下次顺手做」）
**触发**: ★ 业主 2026-10-10 指令「**把工作区整理一下**」。

---

## 一、★★★★ 先量：仓库根有 **2843** 个文件

| # | ★ 读数 | ★ 值 |
|---|---|---|
| ① | 仓库根**文件**总数 | **2843** |
| ② | 其中 `.py` | **1773**（`_*.py` **1047**） |
| ③ | 其中 `.txt` | **883**（`_factNNN.txt` **234** · `_commit_msg_NNN.txt` **477**） |
| ④ | 其中 `.md` | **67**（`_roadmap_*.md` **88** 中在根的部分） |
| ⑤ | 其中 `.log` | **41** |
| ⑥ | 畸形目录 `（必填，无默认值）` | **18.3 MB / 6 文件** |
| ⑦ | `output/` | **223.6 MB** |

★★★ **根目录不是「代码落点」** —— ★ 它是本仓自 2026-10-01 起的**草稿区**（`README-workspace.md` 逐字）。
★★ 而**门禁的扫描根**（AST 实测）只有
`scripts` `tools` `tests` `mcp-server` `subskills` `apps` `dotnet` `examples` `mcp-server` 等
—— ★★ **一个门禁都不扫仓库根** ⇒ ★ 根上的 2814 个草稿**是惰性的**，★ 但它们让仓库**不可导航**。

---

## 二、★★★★ 先量：搬走它们**会不会破门禁**（四条独立核查）

| # | ★ 风险 | ★ 核查方法 | ★ 读数 |
|---|---|---|---|
| ① | **有活代码 `import` 根级模块** | AST 扫全仓 import，取根级模块名 | ★ **2 个**：`shot.py` · `ctl.py`（★ 被 `scripts/sw_jlcfa_gui.py` / `sw_jlcfa_select.py` / `sw_jlcfa_locate.py` import）⇒ ★★ **留根** |
| ② | **specs 的 `→ 验收:` 行点到根级脚本** | 复刻 `check_spec_acceptance_paths.py` 判据③（裸名按名搜） | ★ **0 处**（扫了 **865** 处验收行） |
| ③ | **门禁/生成器 `glob` 仓库根** | 枚举 `check_*.py` / `gen_*.py` 的 `ROOT.glob(...)` | ★ **2 处**：`check_official_md_claims.py`（扫 `scripts/`+`mcp-server/`，**不是根**）· `check_report_criteria_alignment.py`（扫 `ROOT.glob("*.md")`）⇒ ★★ 后者**会被搬动影响** |
| ④ | **打包器需要根文件** | 读 `sync_bundled_skill.TOP_LEVEL_FILES` | ★ **9 个**顶层文件 + `shot.py`/`ctl.py` ⇒ ★★ **留根** |

★★★ **③ 的后果**：`check_report_criteria_alignment.py` 扫 `ROOT.glob("*.md")`，
而根上只有 **1 个** `.md` 带 A1–A10 自评表（`_sec4_new.md`）⇒ ★ 搬走后该门禁**少扫一张表**
⇒ ★★ **实测：门禁仍 `[PASS]`（它只要求「每一张表的编号都对」，不要求张数）** ✓
★★ 但它**确实会改变门禁的覆盖** ⇒ ★ 本轮**把 `_sec4_new.md` 一并归档**，★ 并**如实记录覆盖变化**。

---

## 三、★★★★★ 真因：畸形目录 `（必填，无默认值）` 是**一个真 bug 的产物**

★ 它不是随便起的名字 —— ★ 它是 **MCP 工具的 `Param` 默认值被当成了路径**：

```
mcp-server/tool_specs_batch81.py:72
  Param("output_dir", str, default="（必填，无默认值）", description="…")
                                              ^^^^^^^^^^^^^^^^^^^^  ★ 这不是路径，是**给人看的错误提示**
```

★★ `tool_registry.Param` 的契约逐字（`tool_registry.py:299`）：
> `:param default: 默认值；给 ... 表示必填。`

★★ `is_required` 逐字（`:311-312`）：
```python
return self.required if self.required is not None else self.default is ...
```

⇒ ★★★ **`default` 给了一个非 `...` 的字符串 ⇒ 该参数被判为「可选」且默认值 = 那句中文提示**
⇒ ★★ `run_review(model, output_dir="（必填，无默认值）")` ⇒ `_expand_path` → `mkdir(parents=True)`
⇒ ★★★ **真机在仓库根建出一个叫「（必填，无默认值）」的目录**（★ 6 文件 / 18.3 MB 的现场）。

★ **本仓的既有正确写法**（全仓 **14** 处先例）：`Param("name", str, description="…")` —— ★ **不给 `default`**
（`Param.default` 的字段默认值**就是 `...`** ⇒ 自动判必填）✓
★ 而 `required=True` 在全仓 **0** 处 ⇒ ★ **本仓约定是「省略 `default`」**。

---

## 四、需求

### FR-001 ★★★ 仓库根只留「仓库门面 + 打包器要的 + 被 import 的」
- **验收场景**：`test_root_holds_only_the_allowlist` 通过（根文件 ⊆ 白名单）。

### FR-002 ★★★ 归档**不删任何文件**（红线）
- **验收场景**：`test_nothing_was_deleted` 通过（归档数 + 根保留数 == 整理前总数）。

### FR-003 ★★ 归档**不破任何门禁**
- **验收场景**：`release_check.py` @3.14.7 `status pass` · `EXIT 0` · `missing []`。

### FR-004 ★★★ `archive/` 必须按**铁律 3** 登记（它是白名单外的新顶层目录）
- **验收场景**：`test_archive_dir_is_registered_in_agents_md` 通过。

### FR-005 ★★★ **畸形目录的真因要修**（否则它会**再长出来**）
- **验收场景**：`test_no_param_default_is_a_chinese_placeholder` 通过（全仓 `Param` 的 `default` 不得是中文提示语）。

### FR-006 ★★ **边界冻结**：本轮**只搬文件 + 修那 1 处 `default`**，不动任何业务逻辑
- **验收场景**：`test_only_the_one_param_default_changed` 通过。

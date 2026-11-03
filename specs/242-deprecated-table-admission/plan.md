# plan 242 · 靶子表扩容的准入

## 一、三源与冲突裁决顺序

| 源 | 路径 | 本规格用它的哪一部分 |
|---|---|---|
| ① 官方文档 | `C:\swapi\types\<接口>\<成员>.md` | ★ **不直接读** —— 由 ② 代读（★ 本规格只消费索引，不重解析官方页） |
| ② 索引（官方页的解析产物） | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | ★ `(接口, 成员) -> successor` 全表 + `obsolete_line` |
| ③ 反射转储 | `scripts/sw_api_*.py` | ★ **本规格不用**（★ 转储是"成员名清单"，不是"废弃关系"） |

★ **冲突裁决顺序**：② 索引 > ① 官方页（★ 因为 ② 就是 ① 的确定性解析，且**在仓库里、可复跑**）。
★ 若将来发现 ② 与 ① 不一致 ⇒ ★ **先修 `tools/build_obsolete_index.py`**，不要在本规格里打补丁。

## 二、设计决定（每条都写"为什么不那么做"）

1. ★★ **链终点，而不是官方那句字面值** —— 官方 `Superseded by` 指向的后继**可能自己也已废弃**
   （`IModelDocExtension::SaveAs` ⇒ `SaveAs2` ⇒ `SaveAs3`）⇒ ★ 表里记的必须是**链终点**。
   ★ **不那么做**（按字面值判）会**假红**：`SaveAs` 会因为两条链的字面后继不同被误判成"歧义名"（★ 实测第一版就这么错了）。
2. ★★ **歧义按"链终点跨接口是否相同"判**，不按"后继字面值是否相同"——
   ★ `SaveAs` 的字面后继有两个（`IModelDocExtension::SaveAs` / `SaveAs2`），而**终点只有一个**（`SaveAs3`）
   ⇒ ★ 对**任何**接口按名问 `SaveAs` 答案都对 ⇒ **它不是危险名**。真危险名 **79** 个（`Select2` / `Name` / `GetType` …）。
3. ★★ **"不猜"要能被看见** —— `deprecated_successor` 回 `None` 只是"不猜"；★ **必须同时有
   `ambiguous_deprecated_members()` 把歧义报出来**，否则 `None` 与"不认识"**同形**（★ 静默降级）。
4. ★ **准入判据抽成纯函数** `_admission_failures(table, imap, called)` ——
   ★ 真树上不会自然触发的分支（自环 / 断链 / 未调用）**由单测直接喂合成输入**（★ 纪律：守卫要么有靶子，要么可单测）。
5. ★ **判据口径 import 不重写** —— 调用扫描直接用 `tests/test_deprecated_entry_interlock.py::_scan_calls`
   （spec 241 的**两形态**扫描器：字面量 + 点式 + `call_assembly_doc`）。
6. ★ **不改表** —— 现 4 条全过三关；★ 扩容是**下一件独立工作**（每条要读两边签名）。

## 三、改动面（★ 3 个文件）

| 文件 | 改动 |
|---|---|
| `scripts/sw_com_traps.py` | `deprecated_successor(member, interface="")` 改口径 + 新增 `ambiguous_deprecated_members(table=None)` |
| `mcp-server/tool_specs_batch80.py` | 该工具补 `Param("interface", str, default="")` + `doc` 说明 `None` 还表示"按名歧义" |
| `tests/test_deprecated_table_admission.py` | **新建**，8 例 |

★ **未改** `release_check.py` / `docs/gate-classification.json` / `DEPRECATED_ENTRIES` / 任何 `sw_*.py` 的调用点。
★ 改了 `scripts/` 与 `mcp-server/` ⇒ **必须跑生成器链**（打包副本会过期）。

## 四、风险

| 风险 | 处置 |
|---|---|
| `deprecated_successor` 是**公开 MCP 工具** ⇒ 改签名会影响工具输出 | ★ 新形参有默认值；★ `check_param_binding` 已核（479 个工具 `[PASS]`） |
| 打包副本（`apps/workbench-ui/.../skill/scripts/sw_com_traps.py`）会过期 | ★ 跑 `scripts/release_check.py`（头尾各一次） |
| 索引文件在 `specs/202-*/recon/` ⇒ 判据**跨规格依赖** | ★ 只读、不写；★ 用规模下界（≥1600 条）钉住它不许缩水 |

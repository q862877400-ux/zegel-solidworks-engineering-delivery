# spec 242 · 靶子表扩容的准入（按名歧义收口 + 三关过滤器）

> 上游输入：`specs/241-deprecated-entry-interlock-coverage/` 的交接单待办 1（「靶子表扩容」）。
> ★ 本规格**不改 `DEPRECATED_ENTRIES` 的内容**，只把「能不能收」变成**可跑的判据**。

## 一、为什么做（★ 先量推翻"直接灌表"）

`specs/202-user-coverage-gaps/recon/official-obsolete-index.json` 有 **1671 条 / 1455 个成员名**。
本轮**先量两样**（★ 纪律：① 目标规模 ② **加词的爆炸半径**）：

| 量 | 读数 | 口径 / 命令 |
|---|---|---|
| 目标规模 | **82** 个名 | 真树（`scripts/sw_*.py`，排除 `sw_api_*`）**真的在调用**的废弃成员名 —— `output/_probe242_calls.py` |
| 爆炸半径 | **115** 个名（字面后继口径）· **79** 个名（**链终点**口径） | 官方索引里「同名 · 后继不同」—— `output/_probe242_ambiguity.py` |
| 真树上危险名 | **11** 个（`Select2` 一名 **6** 个不同终点） | 同上 |

★★ **结论**：`deprecated_successor(member)` 是**公开 MCP 工具**（`mcp-server/tool_specs_batch80.py`），
它**只按成员名查** ⇒ 把歧义名收进表会让它**静默返回一个错的**后继
（★ 与「静默降级」同病：读出来的东西**看起来像答案**）。
⇒ **扩容的前置条件 = 先让「按名歧义」不可能静默存在。**

## 二、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | `deprecated_successor(member, interface="")`：给接口 ⇒ 按 `(接口, 成员)` **精确查**；不给接口 ⇒ **只有唯一后继时**才回它，★ **按名歧义回 `None`（不猜）** | 本项目自身（`scripts/sw_com_traps.py`） | 本仓库 MIT |
| FR-002 | `ambiguous_deprecated_members(table=None)`：把「同名 · 不同后继」**显式报出来**（★ 空 = 无歧义；★ `table` 可注入，供单测喂合成表） | 本项目自身 | 本仓库 MIT |
| FR-003 | **准入三关**判据（真树逐条 + 合成负例）：关 0 按名歧义 = 0 · 关 1 在官方索引里 · **关 2 后继 = 官方链的终点** · 关 3 后继**在仓库里真的被调用** | `specs/202-*/recon/official-obsolete-index.json`（`tools/build_obsolete_index.py` 生成，★ 只读官方 `C:\swapi\types\**\*.md` 的 `Obsolete` 段） | 本仓库 MIT（★ 索引是官方文本的**解析产物**，非第三方代码） |
| FR-004 | **边界冻结**：★「官方**链终点跨接口不同**」的名字，**未经表态不得进表**（豁免走 `_AMBIGUOUS_NAME_ALLOWLIST`，现为空） | 本项目自身 | 本仓库 MIT |
| FR-005 | MCP 工具 `solidworks_api_deprecated_successor` 补 `interface` 形参并**说明 `None` 还表示"按名歧义"** | `mcp-server/tool_specs_batch80.py` | 本仓库 MIT |

★ **不做**（★ 明写理由）：
- ★ **不灌表** —— 82 个候选里 **11 个真歧义**，且每条都要"读两边签名"；★ 先把准入立起来（★ 与 224/237 同族顺序）。
- ★ **不改 `sw_com_traps.DEPRECATED_ENTRIES` 的任何一条**（现 4 条，全过三关）。
- ★ **不加门禁文件** —— 与 spec 241 同形（判据进 `tests/`），`release_check` 的 `gates` 仍 **44**、`classification` 仍 **48**。

## 三、验收（可跑）

```bash
# ① 新判据（8 例）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
# ② 互锁族回归（26 例）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_tool_specs_batch80.py -q
# ③ 门禁全套（★ 必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```

## 四、未过门（★ 如实登记）

- ★ **准入判据只在"真树 + 合成表"上跑**；★ **不是** `release_check` 的门禁 ⇒ 只在 pytest 面生效。
- ★ 关 3「后继在仓库被调用」是**静态**读数（AST 两形态），不判运行期。
- ★ 关 2 依赖官方索引的**解析质量**（`build_obsolete_index.py` 的取段规则）；★ 索引本身**未经第二源复核**。
- ★ 真机未验；★ 未提交 / 未部署；★ 未删任何文件；★ 未调 COM。

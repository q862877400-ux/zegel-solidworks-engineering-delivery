# spec 243 · 准入口径的收口（关 4 / 关 5 / 关 6）

> 上游输入：`specs/242-deprecated-table-admission/` 的交接单待办 1（「用准入判据逐条筛那 82 个候选」）。
> ★ 本规格**不改 `DEPRECATED_ENTRIES` 的内容**（仍 4 条），只把 242 的三关**补严**。

## 一、为什么做（★ 先量：242 的三关**放行了表达不了的条目**）

真树在调用的废弃名 **82** 个，按 242 的三关（关 1 在索引里 / 关 2 链终点 / 关 3 后继被调用）逐条跑
（探针 `output/_probe243_admission.py`，★ 第一版我多加了一条"终点接口必须同源"的自造过滤器 ⇒ **不是规格口径，已删**）：

| 桶 | 数 | 是什么 |
|---|---|---|
| `successor-same-name` | **34** | ★ 官方那句 `Superseded by` 是**接口迁移**（`IModelDoc2::FeatureCut4` → `IFeatureManager::FeatureCut4`）—— **后继成员名与被废弃的一模一样** |
| `terminal-never-called` | 23 | 真替换，但后继在仓库里一次都没被调用（★ 关 3 的正当拒绝） |
| `admissible` | **15** | 242 三关下的"可收"候选 |
| `ambiguous-terminal` | 9 | 按名歧义（★ 242 已处理） |
| `chain-broken-all` | 1 | 断链 / 自环 / 超限 |

★★★ **问题**：那 **34** 个在 242 的三关下**全部"过关"**，而靶子表的值是**裸成员名**、
互锁判据也**按成员名比**（`tests/test_deprecated_entry_interlock.py` 硬断言 `succ != member`）
⇒ ★ **表根本表达不了"接口迁移"** ⇒ 照 242 的口径扩表会收进**无意义条目**（"用 `FeatureCut4` 代替 `FeatureCut4`"）。

★★★ **第二个问题（同一轮量出）**：`tools/build_obsolete_index.py` 用 `re.search` 抓后继
⇒ 官方写「`Superseded by A and B`」时**只留第一个**。索引 1671 条里 **254 条**是多后继。
真案例（★ 不是编的）：`C:\swapi\types\IModelDoc2\SketchTrim.md:12` 逐字
「`Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].`」
⇒ 索引只记 `SketchExtend` ⇒ ★ **错的**（`SketchTrim` 该换的是 `SketchTrim`，不是 `SketchExtend`）。

★★ **第三个问题**：`_chain_terminal` 把「后继页**不在索引里**」当成**终点** ——
而"不在索引里"有**两种**含义：① 页存在且不废弃 ✓ ② **页根本不存在** ✗ ⇒ **同形**（静默降级）。

⇒ ★★ **结论：本轮不灌表**（15 个"过关"候选里 `SketchTrim` 已被证是索引有损导致的**错后继**）
—— ★ 先补严判据，扩容留给下一轮。

## 二、需求（每条带来源与许可）

| # | 需求 | 来源 | 许可 |
|---|---|---|---|
| FR-001 | **关 4** `successor-same-name`：后继**成员名**必须 ≠ 被废弃的成员名（★ 相等 ⇒ 接口迁移 ⇒ 表表达不了 ⇒ 不得收） | 官方 `C:\swapi\types\**\*.md`（`Obsolete. Superseded by [[…]]` 段）· `tools/build_obsolete_index.py` 产物 | 本仓库 MIT（★ 索引是官方文本的**解析产物**，非第三方代码） |
| FR-002 | **关 5** `multiple-official-successors`：官方那句**只许点名一个**后继；多后继 ⇒ **必须人工表态**，不得自动放行 | 同上（★ 判据用 `obsolete_line` 的 `[[…]]` 链接数） | 本仓库 MIT |
| FR-003 | **关 6** `successor-page-missing` / `successor-still-obsolete`：后继页**必须存在**，且**自己不是废弃的**（★ 判据用**页首行**，口径同 `build_obsolete_index.py`；★ **不许**全文搜 `obsolete`） | `C:\swapi\types\<接口>\<成员>.md` | 本仓库 MIT |
| FR-004 | `_admission_failures(table, imap, called, entries)` 签名扩为**四参**（★ 关 5/关 6 要**原始索引条目**，`imap` 里没有 `obsolete_line`） | 本项目自身（`tests/test_deprecated_table_admission.py`） | 本仓库 MIT |
| FR-005 | **普查判据**：82 个候选分桶，★ **五个桶各自非空**（**下界**，不写精确数）—— 防"检查量为 0 判失败" | 本项目自身 | 本仓库 MIT |

★ **不做**（★ 明写理由）：
- ★ **不灌表** —— `SketchTrim` 已被证是**索引有损**导致的错后继；★ 扩容必须先逐条复核多后继条目（★ 下一轮）。
- ★ **不改 `scripts/sw_com_traps.py`**（`DEPRECATED_ENTRIES` 仍 4 条 · `deprecated_successor` 不动）。
- ★ **不改 `build_obsolete_index.py`** —— ★ 它是**生成器**，改它要重跑索引并复核全部 1671 条（★ 独立一件工作，未立项）。
- ★ **不加门禁文件** —— 与 241/242 同形（判据进 `tests/`），`release_check` 的 `gates` 仍 **44**、`classification` 仍 **48**。

## 三、验收（可跑）

```bash
# ① 新判据（12 例）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py -q
# ② 互锁族回归（30 例）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py tests/test_save_routing_interlock.py tests/test_tool_specs_batch80.py -q
# ③ 门禁全套（★ 必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
```

## 四、未过门（★ 如实登记）

- ★ 准入判据只在 pytest 面生效，**不是** `release_check` 的门禁（★ 与 241/242 同形）。
- ★ **254 条多后继条目仍未逐条复核** ⇒ 索引对它们**给不出"该用哪个"**；★ 生成器有损**未修**。
- ★ 关 3 是**静态**读数（AST 两形态），不判运行期；关 6 只看**页首行**，不判页内语义。
- ★ 15 个 `admissible` 候选**仍未读两边签名** ⇒ 仍**未收表**。
- ★ 真机未验；★ 未提交 / 未部署；★ 未删任何文件；★ 未调 COM。

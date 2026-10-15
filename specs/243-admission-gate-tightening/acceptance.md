# acceptance 243 · 准入口径的收口（关 4 / 关 5 / 关 6）

## 一、判据读数

| 判据 | 命令 | 读数 |
|---|---|---|
| ★ **红基线**（实现之前） | `pytest tests/test_deprecated_table_admission.py -q` | **`3 failed, 9 passed`** |
| 新判据（实现之后） | 同上 | **`12 passed`** |
| 互锁族回归 | `pytest test_deprecated_table_admission test_deprecated_entry_interlock test_save_routing_interlock test_tool_specs_batch80 -q` | **`30 passed`** |
| **门禁全套** @3.14.7 | `scripts/release_check.py` | **`EXIT 0` · `status pass` · `missing []`** |
| `gate_wiring` | 同上 | **44 个 `check_*.py`**（★ 未新增门禁文件） |
| `gate-classification.json` | — | **48**（★ 不变） |
| `param_binding` | 同上 | `pass`（**479** 个工具 · ★ 未改 `mcp-server/`） |
| `interface_ownership` | 同上 | `checked 6 · unmapped 0 · no-members-used 2` —— ★ **不变** |
| 生成器链 | — | ★ **未跑**（★ 本轮改动面只有 `tests/*.py` 与 `docs/*.md`，★ 生成物只依赖 `scripts/` 与 `mcp-server/`） |

★ **改动面**（★ 只有 2 个文件）：
`tests/test_deprecated_table_admission.py`（8 → 12 个 test）· `docs/known-facts.md`（事实 272）。
★ **未改** `scripts/sw_com_traps.py` / `mcp-server/**` / `scripts/release_check.py` / `docs/gate-classification.json`。

## 二、★ 量测读数（本轮**先量**的产出）

```
官方废弃索引 1671 条 / 1455 个成员名
真树在调用的废弃名 = 82

★ 按 242 的三关分桶（口径 = 关 1 在索引里 / 关 2 链终点 / 关 3 后继被调用）：
   successor-same-name    34   ← ★ 接口迁移（IModelDoc2::FeatureCut4 → IFeatureManager::FeatureCut4）
   terminal-never-called  23
   admissible             15   ← ★ 242 口径下的"可收"候选
   ambiguous-terminal      9
   chain-broken-all        1

★★ 索引里官方那句点名了**多个**后继的条目 = 254 / 1671
★ 真案例：C:\swapi\types\IModelDoc2\SketchTrim.md:12 逐字
    「Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].」
  ⇒ ★ 索引只记 SketchExtend ⇒ ★ **错后继**（SketchTrim 该换 SketchTrim，不是 SketchExtend）
```

## 三、★★★ 核心事实

1. ★★★ **242 的三关会放行"表表达不了"的条目** —— 34/82 是**接口迁移**
   （后继**成员名与被废弃的一模一样**）。靶子表的值是**裸成员名**、互锁判据也**按名比**
   ⇒ ★ 收了会同时踩 `tests/test_deprecated_entry_interlock.py::test_target_table_entries_all_have_successors`
   的 `succ != member` ⇒ ★★ **准入判据与消费端判据必须一起看**（关 4 补上）。
2. ★★★ **官方索引是"有损"的** —— `tools/build_obsolete_index.py` 用 `re.search` 抓后继，
   官方写「`Superseded by A and B`」时**只留第一个**（**254 条**受影响）
   ⇒ ★ **索引单独决定不了"该用哪个"**（关 5 补上）。
3. ★★★ **`_chain_terminal` 把"页不存在"与"页不废弃"判成同形** ——
   它用「后继页**不在索引里**」当终点，而"不在索引里"有两种含义（关 6 补上）。
4. ★★ **"全文搜 `obsolete`"是错的判据口径** —— `IModelDocExtension\SaveAs3.md` 正文里就有
   「the now obsolete [[…::SaveAs2]]」⇒ 全文搜会**假红**；★ 正解是**页首行**
   （★ 口径与 `build_obsolete_index.py` 的「标题之后、`## ` 之前」一致，★ **不重写**）。
5. ★★ **本轮**不灌表**是对的** —— 15 个"过关"候选里 `SketchTrim` 已被证是**索引有损导致的错后继**
   ⇒ ★ 扩容必须先逐条复核 254 条多后继条目（★ 独立一件工作）。

## 四、★ 踩到的坑

1. ★★ **第一版探针自造了一条过滤器**（"终点接口必须同源"）⇒ 不是规格口径
   ⇒ 读数从 **49 → 15**（★ 差 3 倍）。★ 教训：**量测口径必须逐字对齐被测判据**，
   自造过滤器会让读数**整体错位而看不出错**（与 234 的 `.items()`/`.get()` 取值语义同族）。
2. ★★ **关 6 必须用 `term`（链终点）而不是索引字面 successor** ——
   第一版我用了字面值 ⇒ 现表 `SaveAs` 会去查 `SaveAs2` 页（**它自己是废弃页**）⇒ **假红**。
3. ★ **`_admission_failures` 由三参改四参** ⇒ 4 处旧调用点必须同步（★ 实测会立刻 `TypeError`，不静默）。
4. ★ **关 4/关 5/关 6 加之前先核了现表 4 条**（单链接 + 后继页首行非 `Obsolete.`）⇒ 实测全过、不制造新红。

## 五、未过门（★ 如实登记）

- ★ 准入判据只在 pytest 面生效，**不是** `release_check` 的门禁（★ 与 241/242 同形）。
- ★ **254 条多后继条目仍未逐条复核** ⇒ 索引对它们给不出"该用哪个"；★ 生成器**有损未修**。
- ★ 关 3 是**静态**读数（AST 两形态），不判运行期；关 6 只看**页首行**，不判页内语义。
- ★ 15 个 `admissible` 候选**仍未读两边签名** ⇒ **仍未收表**（★ 下一轮）。
- ★ 真机未验；★ 未提交 / 未部署 / 未打 tag；★ 未删任何文件；★ 未调 COM / 真机。

# Plan — `Name` 的逐宿主表达式表态

**Feature**: `specs/248-name-host-adjudication/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 本轮用途 | 权威度 |
|---|---|---|---|---|
| 1 | **官方类型页** | `C:/swapi/types/<接口>/<成员>.md` | 判「该接口的这个成员是否 `Obsolete.`」+ 返回类型（判宿主接口） | ★★★ **最高** |
| 2 | **官方废弃索引**（由 1 生成） | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 取 `Name` 的两条废弃条目（`IComponent2::Name` · `IView::Name`） | ★★ 派生自 1 |
| 3 | **真树源码** | `scripts/sw_*.py`（AST 抽取） | 取站点的**宿主表达式**与**赋值来源** | ★ 事实来源 |

**冲突裁决顺序**：1 > 2 > 3。
- ★ 若 2 与 1 冲突（索引取错后继）⇒ **以 1 为准**，并登记到 244 的 `_KNOWN_WRONG`。
- ★ 若 3（真树）与 1 冲突（我们调了官方说废弃的成员）⇒ **不是冲突，是发现** ⇒ 记为 `real-hit`，
  ★ 但**不改调用点**（换路由必须真机验）。

★ **本轮的判读顺序**（每条站点）：① 读宿主表达式的**赋值来源**（同函数内向上找 `=`）→
② 由来源的**官方 Returns** 定接口 → ③ 拿接口去比索引里 `Name` 的两条 ⇒ 表态。

---

## 二、口径（逐字对齐，不许凭印象）

| 口径 | 真源 | 本文件怎么用 |
|---|---|---|
| 调用抽取（两种形态） | `tests/test_deprecated_entry_interlock._scan_calls` | ★ **import**，不重写（判据 6 自证一致） |
| 多后继条目集合 | `tests/test_obsolete_multi_successor._multi` | ★ **import**（245 的 `_hit_sites` 已封装） |
| 站点抽取（带宿主表达式） | `tests/test_obsolete_multi_successor_impact._member_calls` | ★ **import**（245 的产物，口径已自证） |
| 「非废弃」判据 | `tools/build_obsolete_index._first_body_line` 的口径 | ★ 245 已复刻为 `_first_body_line`；本文件**不重写** |

★★ **教训（244 踩过）**：量测口径**凭印象写** ⇒ 第一版把包装函数硬编码成 `("get_com_member", "get_com_member_raw")`，
**漏了 `call_com_member` / `call_assembly_doc`、还编了一个不存在的名** ⇒ 读数 78（真值 82）。
⇒ **定则：口径要么 `import`，要么逐字抄。**

---

## 三、实现步骤

1. **先量**（★ 一次性探针，放 `output/`）：`output/_probe248_name_sites.py`
   ⇒ 导出 `Name` 的 51 处站点 + 每个宿主表达式的分组 + 逐站点 ±2 行上下文（落 `output/_probe248_name_sites.txt`）。
2. **判读**：16 个宿主表达式逐个读**赋值来源**，由官方 Returns 定接口。
3. **先写能红的判据**（★ 改任何东西之前）：`tests/test_obsolete_name_host_adjudication.py`
   ⇒ 含**纯函数** `_adjudication_failures` + **三组合成负例**。
4. **证明它红**：清空表 ⇒ 16 条未表态；删 `av` ⇒ 1 条；翻 `view` ⇒ 矛盾。
5. **补 245 的登记**：`_HOST_REVIEW["Name"]` 的证据站点 2 → 5（4 真 + 1 假示例），依据改写为 51 处/16 宿主。
6. **回写四处**：ROADMAP §一 游标 · `memory/2026-10-09.md`（append）· `output/AUTO_HANDOFF.md`（覆盖）· `output/AUTO_RUN_*.md`。

---

## 四、改动面（预期）

| 文件 | 动作 |
|---|---|
| `tests/test_obsolete_name_host_adjudication.py` | ★ **新增**（6 例） |
| `tests/test_obsolete_multi_successor_impact.py` | ★ **只改** `_HOST_REVIEW["Name"]` 一条（证据 2 → 5 + 依据改写） |
| `docs/ROADMAP.md` | §一 游标追加 |
| `.workbuddy-ai/memory/2026-10-09.md` | append |
| `output/AUTO_HANDOFF.md` | 覆盖写四段 |
| `output/AUTO_RUN_2026-10-09-*.md` | 新增 |

★ **不改**：`tools/build_obsolete_index.py` · `scripts/sw_com_traps.py` · `scripts/release_check.py` ·
`docs/gate-classification.json` · `mcp-server/**` · `scripts/sw_*.py`（★ 一行不改真树）。

★ **不跑生成器链**：本轮没改 `scripts/`（★ 与 247 不同 —— 247 改了 `sw_com_traps.py`，故跑了 7 步）。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 宿主表达式随变量改名而变 ⇒ 判据红 | ★ **这正是设计意图**（新增/改名即红）；红时按新宿主补表态 |
| `C:/swapi/types` 不在本机 | ★ 判据 6 `pytest.skip`（缺数据源 ≠ 检查失败）；★ 但表里的表态是**离线判读结果**，仍在 |
| `cwStudy` / `ICableProperty` 等族在 `types/` 无页 | ★ 不靠「有页」判 —— 靠「**索引里 `Name` 只有两条**」这个**闭集**判 |
| 改 245 的登记会不会破坏 245 的判据 | ★ 只**增加**证据站点 + 改依据文字 ⇒ 245 的 7 例逐条复核（SC-3） |
| `release_check` 现约 2m40s，前台 120s 会 SIGTERM | ★ **后台跑 + 落盘日志**（`output/_gate248.log`） |

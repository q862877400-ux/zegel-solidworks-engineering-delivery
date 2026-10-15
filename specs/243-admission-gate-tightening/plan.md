# plan 243 · 准入口径的收口

## 一、三源与冲突裁决顺序

| 源 | 路径 | 用途 |
|---|---|---|
| ① 官方类型页 | `C:\swapi\types\<接口>\<成员>.md` | **第 0 步** —— `Obsolete.` 行 + 签名 + 「标题之后、`## ` 之前」那段 |
| ② 官方索引（解析产物） | `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | 1671 条 `(接口, 成员) → successor`；★ **只读、不重生成** |
| ③ 真树 AST | `scripts/sw_*.py`（★ 排除 `sw_api_*.py` 反射转储） | 「谁在调什么」（两形态：字面量 + 点式） |

**冲突裁决顺序**（★ 铁律 4/5）：
```
① 官方页 > ② 索引 > ③ 真树
★ 而 ② 是 ① 的**解析产物** ⇒ ② 与 ① 冲突时以 ① 为准；
★★ 本轮的三条关就是**把"② 会骗人"的地方显式判出来**：
   · ② 的 successor 字段**丢了**多后继里的第 2..n 个（关 5）；
   · ② 的 interface 字段会出现 `SketchManager::CreateLine`（掉 `I`）这类畸形（关 6 兜住）；
   · ② 的 successor 与 ① 的成员名相同时，**表表达不了**（关 4）。
★ 查不到 / 解析不出 ⇒ **不猜**（关 6 显式回 `successor-page-missing`，不静默当终点）。
```

## 二、施工顺序（★ 先写判据、确认能红、再改实现）

```
T1 先量（探针，放 output/，不进仓库代码）
   └→ output/_probe243_admission.py（分桶）· output/_probe243_verify.py（逐条对官方页取证）
T2 先写判据（★ 实现之前必须红一次）
   └→ 加 4 例新判据 + 改 4 处旧调用点为四参 ⇒ 实测 `3 failed, 9 passed`
T3 实现（★ 只改 `tests/test_deprecated_table_admission.py` 一个文件）
   └→ `_admission_failures` 四参 + 关 4/5/6 + `_successor_links` / `_successor_page` / `_page_first_body_line`
T4 判据转绿 + 互锁族回归
T5 文档同步（`docs/known-facts.md` 事实 272）
T6 门禁全套 @3.14.7（★ 未改 scripts/ 与 mcp-server/ ⇒ **生成器链不必跑**）
T7 收尾（ROADMAP 游标 / feature.json / memory / 交接单 / AUTO_RUN）
```

## 三、★ 本轮**没动**的东西（明写，防下一轮误判）

- ★ `scripts/sw_com_traps.py` —— **一行未改**（`DEPRECATED_ENTRIES` 仍 **4 条**）。
- ★ `mcp-server/**` —— **一行未改** ⇒ `param_binding` 仍 479 个工具。
- ★ `scripts/release_check.py` / `docs/gate-classification.json` —— **未改**（未新增门禁文件）。
- ★ `tools/build_obsolete_index.py` —— **未改**（★ 生成器有损是**已登记未修**，见 spec §四）。
- ★ **未跑生成器链** —— 判据：本轮的改动面只有 `tests/*.py` 与 `docs/*.md`
  （★ 生成器链的产物只依赖 `scripts/` 与 `mcp-server/`）。

## 四、可复用件（★ 下一轮扩容直接拿）

```
tests/test_deprecated_table_admission.py:
  _admission_failures(table, imap, called, entries)   ★ 六关纯函数准入过滤器
  _census(entries, imap, called)                      ★ 「真树在调的废弃名」分桶（纯函数）
  _chain_terminal / _index_entries / _index_map / _split / _called_names
  _successor_links(line) / _successor_page(iface, member) / _page_first_body_line(page)
  _AMBIGUOUS_NAME_ALLOWLIST                           ★ 歧义名豁免名单（现为空）
```

## 五、风险与止损

| 风险 | 止损 |
|---|---|
| 把 `SketchExtend` 当成 `SketchTrim` 的后继收进表（★ 本轮**已抓到**） | ★ 关 5 拦下；★ **本轮不灌表** |
| 关 6 全文搜 `obsolete` ⇒ `SaveAs3` 页假红 | ★ 判据用**页首行**；★ 已有**边界冻结**例钉住 |
| 关 4/5/6 让**现表 4 条**假红 | ★ 施工前**先核**：4 条官方那句都是**单链接**、后继页首行都不是 `Obsolete.` ⇒ 实测全过 |
| 四参签名改动漏改调用点 | ★ 实测 `TypeError` 立即暴露（★ 已逐处改完并复跑） |

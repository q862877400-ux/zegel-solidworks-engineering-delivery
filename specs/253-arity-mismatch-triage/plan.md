# Plan — 16 条 arity 不符的分桶定罪

**Feature**: `specs/253-arity-mismatch-triage/`
**日期**: 2026-10-09

---

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 用途 | 权威度 |
|---|---|---|---|---|
| 1 | ★★ **真机** | `SldWorks.Application` rev 34.4.1（★ 走护栏，只读） | 判「某种写法到底能不能调通」 | ★★★ **最高** |
| 2 | **反射转储** | `_raw/**/iface_*.txt`（★ 门禁用的源） | 形参数与类型 | ★★ |
| 3 | **真树源码** | `scripts/sw_*.py` | 实参个数与**封装写法**（`*args`？） | ★ 事实来源 |

**冲突裁决顺序**：1 > 2 > 3。★ 本轮真机**推翻**了门禁的静态判定（`all-byref` 桶）。

---

## 二、口径（★ 逐字对齐门禁，不重写）

| 口径 | 真源 | 怎么用 |
|---|---|---|
| `com_args` / `judge` / `find_dumps` | `scripts/check_dispatch_byref_guard.py` | ★ **import** |
| `scan` / `resolution` / `_entry_sites` / `_import_map` / `inner_wrapper_call` / `forward_slots` | `scripts/check_dispatch_entry_guard.py` | ★ **import** |
| `load_full_signatures` / `byref_variables` / `byref_alias_names` | `scripts/audit_byref_args.py` | ★ **import** |
| 真机三写法 | `output/_probe253_whatswrong.py` | ★ 真机读数（★ 已冻结进判据） |

★★ **教训（本轮踩的）**：★ 探针第一版**猜错** `load_full_signatures` 的来源模块（以为是 `check_arity_tables_vs_reflection`）
⇒ `ImportError`。★ 定则同 244：**口径要么 `import` 要么逐字抄**，★ 且**先读门禁的 import 段**。

---

## 三、实现步骤

1. **先量**：`output/_probe253_arity_sites.py` ⇒ 导出 16 条明细（文件/行号/成员/实参/反射/入口）。
2. **判桶**：逐条读**真树源码**判是 `*args` 还是普通转发；★ 按**差值**归桶。
3. **先写能红的判据**：`tests/test_arity_mismatch_triage.py`（★ 含**推翻旧结论**那条）。
4. **证明它红**：翻 `real-gap` ⇒ 报错；全判 −1 ⇒ 条数 16 = 旧断言 ⇒ 红。
5. **真机只读复核**：`output/_probe253_whatswrong.py`（★ 走护栏，临时零件用完关闭且不保存）。
6. **回写四处**：ROADMAP §一 · memory · `AUTO_HANDOFF.md` · `AUTO_RUN_*.md`。

---

## 四、改动面

| 文件 | 动作 |
|---|---|
| `tests/test_arity_mismatch_triage.py` | ★ **新增**（5 例） |
| `output/_probe253_arity_sites.py` / `.txt` · `output/_probe253_whatswrong.py` / `.txt` | ★ **新增**（一次性探针 + 读数） |
| `specs/253-arity-mismatch-triage/*.md` | ★ **新增**（四件齐） |
| `docs/ROADMAP.md` · memory · `AUTO_HANDOFF.md` · `.specify/feature.json` | 回写 |

★ **不改**：`scripts/check_dispatch_byref_guard.py`（★ 门禁口径缺陷**只登记不修**）· `scripts/sw_*.py` ·
`tools/goal_gate.py`（★ 新建的 Stop hook 判定器，本切片不动）。
★ **不跑生成器链**（★ 没改 `scripts/`）。

---

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 真机开文档会污染用户环境 | ★ 开**空零件**、★ `finally` 里**关闭且不保存**；★ 走护栏（预检「读到文档 N 个」） |
| ★ 关闭调用写错（★ 本轮踩到：`GetTitle` 是**属性**不是方法） | ★ 已记录；★ 探针结束后**再次护栏预检**确认 0 个文档 |
| 猜错 import 来源 | ★ 先读门禁的 `import` 段（★ 本轮已踩） |
| 门禁口径缺陷被误当「已修」 | ★ 明确写进「未过门」：**只定罪、不修** |
| `release_check` 约 2m40s | ★ 后台跑 + 落盘日志 |

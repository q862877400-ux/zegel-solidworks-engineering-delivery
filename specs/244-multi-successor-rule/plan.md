# Plan — 多后继条目的后继选取规则

**Feature**: `specs/244-multi-successor-rule/` | **日期**: 2026-10-09

---

## 一、官方源与裁决顺序（宪法 §II 要求）

| 源 | 路径 | 本特性用它做什么 | license |
|---|---|---|---|
| **`C:\swapi`（结构化 markdown）** | `C:/swapi/types/<接口>/<成员>.md` | ★ **主源** —— 读 `Obsolete.` 那句的**原文**与**全链接**；判后继语义 | 官方 API 文档（本机离线副本，内部使用） |
| **CHM 解包** | `D:\AI\SW\AI Solidworks\官方文档\` | 本特性**未用**（本特性只判「索引那句取错没」，语义已由 `C:\swapi` 的 Description 给出） | 官方 API 文档（内部使用） |
| **interop 反射转储** | `D:\AI\SW\_raw\` | 本特性**未用**（不涉签名与枚举值） | 本机反射产物 |

**冲突裁决顺序**：本特性**不产生签名冲突** —— 它判的是**官方那句散文里点了几个链接、哪个与被废弃成员同名**。
★ 唯一需要语义裁决的地方是「同名链接是不是真后继」，判据是**官方页的 Description**（例：`SketchTrim` 的 "Trims…" vs `SketchExtend` 的 "Adds to the length…"）。
★ **不碰出厂类型库**（那是对**签名**冲突的裁决者，本特性不涉签名）。

---

## 二、数据流（只读）

```
specs/202-user-coverage-gaps/recon/official-obsolete-index.json     ← 1671 条（索引）
        │  entries[].obsolete_line 里数 [[…]] 的个数
        ▼
    254 条多后继条目
        │  对每条：句中是否有「与被废弃成员同名」的链接？
        ├── 无（243 条）⇒ 索引取第一个是对的 ⇒ 本判据不管
        └── 有（11 条）⇒ 索引后继必须是那个同名链接
                ├── 是（5 条）⇒ 通过
                └── 否（6 条）⇒ ★ 必须在 _KNOWN_WRONG 登记（带真后继 + 依据）
```

**★ 只读**：本特性**不写**索引、**不改**生成器（FR-005）。

---

## 三、代码落点

| 文件 | 动作 |
|---|---|
| `tests/test_obsolete_multi_successor.py` | **新建** —— 4 个判据（张数下界 / 同名规则 / 登记表与索引一致 / 登记项须有依据） |
| `specs/244-multi-successor-rule/{spec,plan,tasks,acceptance}.md` | **新建** —— 本四件 |
| `output/_probe244_multi_successor.py` | 一次性探针（**不进仓库代码**）—— 量「真树在调的 82 名 ∩ 254 条」 |
| `output/_probe244_dump.py` | 一次性探针 —— 导出 14 条命中名的官方原句 |
| `output/_probe244_rule.py` | 一次性探针 —— 量「同名规则」在 254 条上的分桶 |
| `tools/build_obsolete_index.py` | ★ **一行不改**（FR-005） |
| `scripts/sw_com_traps.py` | ★ **一行不改**（`DEPRECATED_ENTRIES` 仍 4 条） |

---

## 四、口径纪律（本轮踩到的）

★★ **量测口径必须逐字对齐被测判据**（243 的教训，本轮**又踩了一次**）：
第一版探针把包装函数硬编码成 `("get_com_member", "get_com_member_raw")` ——
**漏了 `call_com_member` / `call_assembly_doc`，还编了一个不存在的 `get_com_member_raw`**
⇒ 「真树在调 ∩ 索引」读数 **78**，而真值 **82**（差 4）。

★ **定则**：口径**要么 import，要么逐字抄**，不许凭印象写。
（243 那次是「自造了一条不在规格里的过滤器」，读数差 3 倍；本轮是「凭印象写包装函数名」，差 4。）

---

## 五、宪法检查

| 宪法条 | 本特性 |
|---|---|
| §I 缝合优先（每条需求带来源） | ✅ spec §二 每条 FR 带「来源」 |
| §II 三源互证 + 裁决顺序 | ✅ 本节 §一 表 + 冲突顺序 |
| §III 查不到就写查不到 | ✅ §五 未过门段写清「未修」「未验证」 |
| §IV 许可红线 | ✅ §一 表每行带 license |
| §V 验收判据能跑 | ✅ tasks.md 每条带 `→ 验收:` |
| 老化模型 **Flow-forward** | ✅ 新开 `specs/244-*`，不改 243 |

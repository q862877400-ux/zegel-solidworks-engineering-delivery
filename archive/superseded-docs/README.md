# 已取代的文档（superseded）

本目录存放**已被取代**、但按仓库纪律（只搬不删）保留的文档。

---

## `external-review-brief-guide.md`

| 项 | 内容 |
|---|---|
| **原位置** | `docs/external-review-brief-guide.md` |
| **归档日期** | 2026-10-11 |
| **大小 / 行数** | 42,730 B / 838 行 |
| **SHA256** | `ce4ee0ea5b443d09abe1edeb952b0061aaf981de6d1dbbbd718ea2b4fa21a4b1` |
| **git 状态** | 从未被跟踪（untracked）⇒ 归档无历史损失 |

### 被什么取代

**`~/.agents/skills/external-review-brief-guide/`** —— 同名 DSH Skill（用户级）。

### 取代的原因

| | 本文件（旧） | Skill 版（新） |
|---|---|---|
| **形态** | 单文件 838 行 / 42.7 KB | `SKILL.md` **141 行** + 6 个 `references/*.md` + 1 个脚本 |
| **加载** | 全文一次性载入 | **渐进式披露** —— 入口只放入口与速查，详规按需读 |
| **可验证** | 无触发验证 | **`references/evals.md`**（正例 / 近似反例 / 显式调用 / 产出约束） |
| **脚本** | 内嵌在附录里 | 独立成 `scripts/check_brief.py`，**selftest 17 例**（旧版 11 例） |

### 内容保真

归档前做过逐条核对：**旧版的 35 条关键教训全部保留在新版中**（缺失 0 / 35）。

新版字符数 18,181（旧版 19,272）—— 是**压缩了冗余**，不是删了内容。

### 为什么还留着

- 仓库常驻纪律：**只搬不删**
- 它是这份 Skill 的**内容来源**，保留可用于对照「改了什么」
- 两个附件快照（`9d4bd060` 923 行原版 / `ce4ee0ea` 838 行）都与它有关，留着可追溯

### 不要再引用它

新稿一律引用 Skill：

```
C:\Users\Zegel\.agents\skills\external-review-brief-guide\SKILL.md
```

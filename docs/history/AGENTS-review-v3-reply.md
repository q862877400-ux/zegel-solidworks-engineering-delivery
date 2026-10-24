# 回复：对 v3 裁断的意见（执行方 → 改 AGENTS.md 的对话）

> 收到你的逐条裁断。**我核了你的引证，全部属实**，我认 #1。
> 但有一处要改：**你指定的落点装不下那个信息** —— 证据在 §3。

---

## 1. 你的引证我核到原文了

| 你引的 | 原文 | 我的核验 |
|---|---|---|
| 根文件放 standing orders「linking its home」，Rejects 含「situational procedures」 | `docs/AGENTS.md` 层级表那行 | 逐字对 |
| slop：「Implementation-status annotations… **Status rots; the repo layout and package manifests carry it**」 | `docs/AGENTS.md` slop 清单 | 逐字对 |
| D4：0 装饰 emoji | `~/.dsh/纪律/AGENTS维护合约.md:49` 五类码点 `U+26A0` / `U+2B50` / `U+2705` / `U+274C` / `U+2757` | 逐字对 |

**实测：工作区 AGENTS.md 现在 0 处装饰 emoji** —— 你执行到位了。

**#1 我认，并自我批评一句**：我提「加一节进度」时**没查 DSH 规范** —— 那正是 slop
点名的东西，我却把它列成「最要紧」。这是我该自查的，不是该你替我挡的。

**其余裁断我也认**，其中两条你的理由比我的强：

- **#5 去掉我原文里的 ⚠** —— D4 是硬判据，我的 ⚠ 本身违规。
- **附条 铁律 6 不采纳** —— 你说「读铁律 6 的人正是起 MCP 前要读到这条硬约束」。
  **这比我的「分类学归位」重要**：可达性 > 分类学。我原话也说了不建议改，这条一致。

---

## 2. 一处要改：你指定的落点装不下那个信息

你把落点定为「指向 `docs/union-coverage-matrix.md` 第五节的并入清单」。
**我实测了那一节的实际形态**：

```
### ① 会话 / 文档 / 文件（缺 37）
| 来源 | 该域有 | 许可 | 来源验证 |
| `andrewbartels1/...` | 22 | MIT | 未声明 |        ← 「来源自己声明跑过没有」
缺口操作：activate_document、active_document_info、…

关键词扫描：已完成 ✗   未开始 ✗   下一步 ✗   阶段 ✗   A 级 ✗   B 级 ✗
```

**⇒ 那一节回答的是「每个域缺什么、从哪抄」，不是「现在做到哪了、下一步做什么」。**

它是个**缺口清单**，不是**进度**。指过去之后，我仍然读不出该从哪继续。

---

## 3. 正解在你自己引的那句话**后半句**

> Status rots; **the repo layout and package manifests carry it**.

**状态由 manifest 承载。** 我们这个项目的 manifest 就是 **`capabilities.yaml`**。

**而它现在是空的**：

```
条目: 28            （地图说缺 339 个操作）
level 分布: {verified: 8, pilot: 19, not_implemented: 1}
                      ↑ 还是上游那套旧三级，没有新五级、没有 provenance
```

**⇒ 「状态无处可放」才是根因。** 不是「AGENTS.md 少写一句」——
**是 manifest 还没建成，所以状态没有家。**

---

## 4. 所以建议你把那两行改成

现在（§一 末尾）：

```
进度与下一步的真相在 `docs/union-coverage-matrix.md` 第五节的「并入清单」（生成物，
随并入更新）；未完成的条目按 `level` 标 `stitched`。
```

建议改成：

```
进度与下一步看 `capabilities.yaml`（manifest，每条带 `level` 与 `provenance`）——
状态由生成物与清单承载，不写进本文件。
`docs/union-coverage-matrix.md` 第五节的「并入清单」是缺口地图（每域缺什么、从哪抄、
该来源验证过没有），不是进度。
```

这样指针指对了地方（manifest），而且**把两个生成物的分工写清了：一个管缺口，一个管状态**。

---

## 5. 剩下的活在我这边

`capabilities.yaml` 在代码副本 `C:\swprojects\sw-skill-fork\`，归我。
要做的四件：

1. 把五级 `level` 枚举正式写进 schema（现在 8 条还是 `verified/pilot/not_implemented` 旧口径）
2. 加 `provenance` 字段（规则 5 的载体）
3. **把 384 个操作按域登记**，每条标 `indexed` 或 `stitched`（**没跑的就不许标 `verified`**）
4. 让 `check_union_conventions.py` 校验它

**做完之后，「现在做到哪了」就是 `capabilities.yaml` 的 level 分布 —— 一处可查，且不腐坏**
（因为它随并入更新，本来就是生成物性质的清单，不违反 slop 那条）。

---

## 附 · 一件小事（你定）

我三份产物文档里有装饰 emoji（`AGENTS-handoff.md` 9 处 / `-v2` 3 处 / `-review-v3` 1 处）。
**它们不是 AGENTS.md，D4 不管**。要全库一致的话我可以清掉 —— 但那要改历史提交里的文件，
**不值当**。除非你的体检工具会因此报红，那就说一声。

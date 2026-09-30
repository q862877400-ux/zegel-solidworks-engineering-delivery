# 要你裁一件事 + 知一件事（执行方 → 改 AGENTS.md 的对话）

> 迁移已完成（代码副本 `469064f`，全部门禁绿，测试零新增失败）。
> **详细版在 `docs/AGENTS-pilot-migration-report.md`，那是备查**，你复审 R1–R10 时再翻。
> 这里只有两件**非你不可**的。

---

## 一、要你裁：那 6 条自研的 `stitched` 填不出 `provenance`

**你的 B2**：

> `level` 是 `source_verified` / `stitched` / `indexed` 之一时，`provenance` 必须非空。

**但那 6 条是自研的，没有来源仓：**

```
dfm_checks · surface_modeling · mold_tools
autocad_headless_preview · dxf_preview_scene · routing
```

它们的 `provenance{repo, license, files, upstream_verified}` **四个字段一个都填不出真值**。

**⇒ R6 一落地就会在这 6 条上红。**

| | 做法 | 后果 |
|---|---|---|
| **A**（我倾向） | B2 加限定：**`provenance` 只在「来源派生」时必填**；自研但未运行的条目允许为空 | 语义准。判据就用 `provenance` 自身有没有 |
| **B** | 给它们填指向本仓库的 `provenance` | 违反你自己写的「本项目自身不作为 provenance 来源」 |
| **C** | 改别的 level | 没有更贴切的：不是 `verified`（没跑），不是 `indexed`（有实现） |

**现状**：我没给它们填任何 `provenance`（**填假值比空着坏**）；R6 还没实现在代码里，所以门禁当前是绿的 —— **但 R6 一写就红。**

---

## 二、要你知：这个仓库的测试基线**不稳定**

**我上一份报告说基线是 `2 failed`，那是错的。** 用 `git stash` 做干净对照后实测：

```
改动前:  6 failed / 734 passed / 15 skipped
改动后:  6 failed / 741 passed / 15 skipped    ← +7 是我新增的等价性测试
⇒ 失败列表逐条相同，零新增失败
```

**那 4 个 CLI 测试会跳**（`tests/test_cad_studio_cli.py` ×3 + `tests/test_dfm_review.py` ×1）：
它们 `subprocess.run` 起子进程，**同一份未改动的代码先后跑出 2 failed 与 6 failed**。

**⚠ 如果你的体检或验收判据里有「测试必须 N 绿」这类硬数字，它会误判。**
**建议判据改成「失败列表与基线逐条相同」。** —— 这不是本次引入的，未改动时也会跳。

---

## 三、一行现状（不用你做什么）

迁移把「证据强度」与「授权」拆开了：`verified 21 / stitched 6 / not_implemented 1`，
13 条由 `pilot` 升 `verified` 并补了**真实跑过**的 `evidence`（对应测试合跑 158 passed / 1 failed，
那 1 个是基线失败），**但一律不补 `unattended`** ⇒ 无人值守授权集合迁移前后逐条相同，由
`tests/test_unattended_equivalence.py` 对冻结基线守住。

**另**：授权判据在代码里有 **4 条**路径（不是我上一份报告说的 1 条），都已同批改完。
其中 2 条（队列门禁、能力探针）**只改 `unattended_allowed()` 是抓不到的** ——
是既有测试红了才暴露。**若你想把这条钉死，可在 R11 补一句「授权真源是 `allowed_modes`，
任何按 `level` 推断授权的写法都违规」**，形态归你判。

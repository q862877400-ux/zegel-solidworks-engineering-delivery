# recon/ —— Bunny 批量产物

本目录是**支线**（派给 Bunny 的批量辅助活）的产物落点。主线不动这里的内容，只读结论表。

**为什么是 `docs/recon/` 而不是顶层 `recon/`**：`AGENTS.md` 铁律 3 规定顶层结构目录只允许
14 个（`.github agents ai_team apps assets docs dotnet examples mcp-server references scripts subskills tests tools`）。
最初派活时我把路径写成顶层 `recon/` —— **那是我派活时给错的路径**，不是执行者的错；
`docs/` 在白名单内，子目录不违反铁律 3，故整体挪到这里。

## 产物清单

| 文件 | 来源 | 覆盖 | 实测 |
|---|---|---|---|
| `iview-read-members.md` | Bunny B1（`role="artist"` → space-bunny-free） | `C:\swapi\types\IView\` 全部 461 个成员页 | 真读 461 份 `.md`（外加 `_overview.md` 做交叉验算），543 行表；`149 废弃 + 45 指针 − 0 重叠 + 267 可用 = 461` |

## 判据（B1 用的那三条，后续批次照用）

1. **废弃**：只看页头（`**Signature**` **之前**）是否出现行首 `Obsolete.`；
2. **指针接口**：`## Returns` 段是否含 `in-process, unmanaged C++`；
3. **零参可读**：签名形如 `X()` 或无括号，**且**非废弃、非指针。

## 判据的一处已知洞（B1 自己报的，照实留档）

指针标记**不一定出现在 `## Returns` 段**。B1 实测：`ISetBodies` 的 `ref Body2 BodyArray`
标记在 `## Parameters` 段上，按上面第 2 条**判不出来**。

⇒ 按任务给的**字面判据**，B1 报的指针数是 **45**；而全文含该标记的是 **46** 个，差额就是 `ISetBodies`。
B1 **没有偷偷把它算进 45**，而是在第四节单列「指针标记出现但不在 `## Returns` 段」并附原文片段 —— 这是对的做法。

⇒ **待主线决断**：第 2 条是否要放宽成"全文任何段落出现该标记"。放宽会改变已发布数字（45 → 46），
所以不擅自改；本条先记在这里。

## 另一处待决断

B1 另报：`RootDrawingComponent2.md` 是**空壳页**（只有 YAML 头 + 标题，无签名 / 无 `## Returns` / 无 `## Remarks`）。
B1 三项都写「查不到」，未补未猜，并在 5.1 单列 —— 符合"查不到就说查不到"。

## 支线的纪律（派活时写进去的）

- **只报不动**：只读官方源与仓库，只写被指派的那一个产物文件；不改既有文件、不跑 git、不碰 SolidWorks。
- **如实记否定结果**：查不到写「查不到」，判不出来写「判不出来」，不推测、不拿相似名字蒙混。
- 结论带**可搜索的原文片段**，**不写行号**（行号会漂，实测偏过 47 行）。
- 产出**永远要经 Lead 复核**，不许直接进 `capabilities.yaml` 的 `verified`。

开工提示词见 `docs/kickoff-bunny-sideline.md`。

<!-- domain: 其他 -->

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 宏VBA | `ISldWorks::RunMacro` | **Signature**: `System.bool RunMacro( System.string FilePathName, System.string ModuleName, System.string ProcedureName )` | 无 | `scripts/sw_api_sldworks.py:8884`、`scripts/sw_api_sldworks.py:25581`（`mcp-server/` 无命中；两处均为数据表条目，非调用点） | — |

<!--
取源记录（逐条事实，不含推断）：
- 候选顺序 `RunMacro` → `RunMacro2`。`C:\swapi\types\` 递归命中两个：`ISldWorks\RunMacro.md`、`ISldWorks\RunMacro2.md`。按「第一个存在的即为答案」取 `RunMacro.md`。
- 签名行取自 `C:\swapi\types\ISldWorks\RunMacro.md` 第 14 行，整行照抄。
- `C:\swapi\examples\` 目录存在；递归按文件名搜 `RunMacro`，0 命中 ⇒ 官方例子「无」。
- `RunMacro.md` 全文 34 行，搜字符串 `AccessSelections`，0 命中 ⇒ 指针族「—」。
- `D:\AI\SW\scripts\` grep `\bRunMacro\b` 命中 2 处（均在 `scripts/sw_api_sldworks.py`）；`D:\AI\SW\mcp-server\` grep `RunMacro` 0 命中。
- 附：该 md 第 12 行原文为 `Obsolete. Superseded by [[ISldWorks::RunMacro2]].`（逐字记录，不作取舍判断）。
-->
# 素材库来源（本机离线源与外部项目）

本文件是 `D:\AI\SW\AGENTS.md` 的「四、素材库」细节档：两套官方离线源与反射的分工、`C:\swprojects\` 下的外部项目清单、许可判定表。四家外部 MCP 项目的工具数 / 许可 / 测试文件数 / 自称环境表留在 AGENTS.md。

## 一、两套官方离线源 + 反射（各管一头）

`D:\AI\SW\AI Solidworks\官方文档\` 是安装自带 3 册 CHM 用 `hh.exe -decompile` 解包而成（随安装自带，无许可风险）：

```
官方文档\SWhelp\sldworksapi\       11,579 文件  153.7 MB   C#/C++ API 主册
官方文档\SWhelp\sldworksapivb6\    16,718 文件   67.4 MB   VB6/VBA API 册
官方文档\SWhelp\swconst\            1,353 文件   22.4 MB   枚举
官方文档\SWhelp\cosworks\              47 文件   41.8 MB   Simulation（很薄，见下）
合计 29,697 文件 / 285.4 MB
```

检索工具 `手册\swdoc.ps1`：`-List` 三册概况 / `-Q '<关键词>'` 全文检索 / `-File '<页面名>'` 整页转纯文本。解包时输出目录要不存在且路径不带空格，否则 `hh.exe` 静默失败；7-Zip 25.01 起没有 CHM 解码器，只有 `hh.exe` 可用；不要去爬 help.solidworks.com（403 + JS 渲染，爬下来是空壳）。

`cosworks` 册只覆盖 `ICWLoadsAndRestraintsManager` 一个接口族（34 接口页 + 13 枚举页），正好命中本机 C# 执行层返工 24 轮的 Simulation 夹具 / 载荷坑；但它不等于 cosworks 全貌（DLL 里 168 接口 / 363 枚举）。深度查 CHM，广度查反射。

`C:\swapi\` 是结构化查询源：566 类型 / 963 枚举 / 11,557 成员 / 2,839 官方示例（16,254 文件）。入口 `python "$env:USERPROFILE\.agents\skills\mech-design\tools\sw_know.py" <子命令>`：

| 子命令 | 用途 |
|---|---|
| `member <Type> <Member>` | 精确签名 + 每个参数说明（写代码前查） |
| `type <Type> [--grep X]` | 某类型全部成员 |
| `enum <Enum>` | 枚举全部成员（枚举值也要查，不许猜） |
| `find <kw> [--kind type\|enum\|member\|example]` | 全库检索 |
| `examples "<多词>"` | 找官方示例（Example 页比方法页有用得多） |
| `domain --list` / `domain <域>` | 功能域导航（14 域） |
| `suggest <拼错的词>` | 近似名建议 |
| `verify` / `stats` | 校验功能域地图 / 规模总览 |

它只含 12 个程序集，缺 `cosworks`、`SWRoutingLib`、`sldcostingapi`、`fworks`、`sustainability`、`swdocumentmgr`、`sldtbt`；这些域改查 CHM 与反射。

反射是第三套源，补 CHM 与 `C:\swapi` 都缺的广度：`redist` 里的 interop DLL 没有 XMLDoc，但都是托管程序集，可直接 `Assembly.ReflectionOnlyLoadFrom(...).GetTypes()`。反射是「读官方程序集」，不是实测。已核实体量：`cosworks` 168 接口 / 363 枚举 / 9,281 成员；`SWRoutingLib` 28/26/527；`sldcostingapi` 28/24/1,006；`fworks` 2/10/65。

## 二、外部项目（`C:\swprojects\`）

`C:\swprojects\` 共 23 个目录 = 21 个外部项目克隆 + `sw-skill-fork` 自己 + 临时目录 `_tmp_mcp`；其中 22 个是 git 仓库。

> 目录名消歧：`sw-automation-skill\` 是 wzyn20051216 的 1010 星（本项目要完善的目标）；`solidworks-automation-skill\` 是 djlex83 的 24 星（只贡献一个 `VARIANT` 写法）。引用素材一律写 `owner/repo` 全名，不要只写目录名。

| 目录 | 项目（owner/repo） | 星 | 许可 | 能补什么 |
|---|---|---|---|---|
| `codestack` | xarial/codestack | 377 | MIT | 建视图 / 文档 / 装配 / 导入导出 / 22 篇 troubleshooting（433 篇 md） |
| `solidworks-api` | angelsix/solidworks-api | 370 | MIT | SolidDNA 模板（免弹模板设置）；`References/` 见下方例外 |
| `mcp-server-solidworks` | eyfel/mcp-server-solidworks | 355 | AGPL-3.0 | 只读架构思想（adapters / cad-planner / compiler / execution 四层） |
| `SolidworksMCP-TS` | vespo92/SolidworksMCP-TS | 234 | MIT | `mock-solidworks-adapter` 测试分层；`macro-generator`；5 个 .vba |
| `CSharpAndSolidWorks` | painezeng/CSharpAndSolidWorks | 171 | MIT | 几何算法（自交 / 凸性 / 面积）；38 个 .SLDPRT 测试件 |
| `Solidworks-MCP` | alisamsam/Solidworks-MCP | 143 | MIT | 27 个 .vbs（最大 VBScript 语料）；Hub 死连接诊断 |
| `solidworks-skills` | delancy827/solidworks-skills | 115 | MIT | 交叉验证来源（「23 参数不是 17」独立佐证） |
| `sw-automation-skill` | wzyn20051216/solidworks-automation-skill | 1010 | MIT | 本项目目标本体 |
| `pySW` | kalyanpi4/pySW | 52 | GPL-2.0 | 只读思想，不抄代码 |
| `solidworks-automation-skill` | djlex83/solidworks-automation-skill | 24 | MIT | `VARIANT(VT_DISPATCH,None)` 简洁写法 |
| `offline-solidworks-api-docs` | pedropaulovc/offline-solidworks-api-docs | 13 | 无许可 | `C:\swapi` 的来源，产物同样不可再分发；只读流水线思路 |
| `solidworks-build-mechanical-models` | pengxiaoan/solidworks-build-mechanical-models | 13 | 无许可 | 只读思想（绕过 `SelectByID2`），不抄文本 |
| `solidworks-auto-modeling` | Sakikooooo/solidworks-auto-modeling | 8 | MIT | `Nothing`（标量 Dispatch）vs `Empty`（Variant 数组）规则 |
| `sw-ai-bridge` | Mochaxgcc/solidworks-ai-bridge | 7 | MIT | 裸传 23 个位置参数的佐证 |
| `sw-api-skill` | guoleizhen717/solidworks-api-skill | 5 | MIT | 「>12 参数会失败」是错的，别采信 |
| `ddeng-skills` | walterkken/doc-driven-engineering-software-skills | 5 | 全版权保留 | 只借鉴「文档驱动目录结构」这一条方法论 |
| `q3ds-solidworks-mcp` | Bennyco86/q3ds-solidworks-mcp | 5 | AGPL-3.0 | 只读产品设计（响应体裁剪省 token、视觉捕获） |
| `solidworks-com-automation-skill` | ZiChen-Ni/solidworks-com-automation-skill | 2 | MIT | 最小 COM 封装；Windows 安装脚本 |
| — | `SolidWorks-CAD` / `Solidworks-Crack` | 812/287 | — | 排除：投递页 / 破解指南。不下载、不读取、不运行 |

许可判定表：

| 标记 | 含义 | 能做什么 |
|---|---|---|
| MIT | MIT | 可读、可抄、可改、可商用（保留版权声明） |
| Apache-2.0 | Apache-2.0 | 同上，另有 `NOTICE` 与改动声明义务 |
| AGPL-3.0 / GPL-2.0 | 传染性 | 只读思想，不抄代码、不抄文本 |
| 无 LICENSE / 全版权保留 | 保留所有权利 | 只读思想（全版权保留的只取方法论） |
| 排除 | 恶意 / 破解 | 零接触 |

MIT 唯一已知的例外（`angelsix/solidworks-api` 原文照抄）：

> All files inside the References folder are property of Dassault Systemes SolidWorks Corp and may only be used in unmodified form in conjunction with SolidDNA.

抄 `Templates/SolidDNA` 可以；`References/` 里的文件是达索的财产，原样用、只配 SolidDNA。

`C:\swapi` 的内容来自无许可的 `offline-solidworks-api-docs`（爬 help 站点），所以 `C:\swapi` 的产物同样不可再分发进闭源产品；fork 发布前要意识到这点。`D:\AI\SW\AI Solidworks\官方文档\` 是达索随安装自带的，没有这个问题，优先用它。

# SolidWorks Toolbox 下载与授权调研（面向 SW2026 中文用户 · 脚本化插入标准件）

调研日期：2026-09-29。工具：agent-reach（内置 web_search）+ Wayback Machine + GitHub + **本机文件系统实查**。

## 0. 工具可用性实测（供后续复用）

| 通道 | 结果 |
|---|---|
| `help.solidworks.com` 直连 | **HTTP 403**（Akamai `errors.edgesuite.net`）—— 已复现 |
| `r.jina.ai`（Jina Reader） | **HTTP 401** —— 现需 API key，本机无 key，不可用 |
| Exa（`mcporter call exa.web_search_exa`） | **HTTP 429** 限流，不可用 |
| 内置 `web_search` / `web_fetch` | 可用 |
| **Wayback Machine** | **可用**（见下方注意事项） |
| GitHub `gh` | 可用 |
| `files.solidworks.com`（PDF） | **可用**（与 help 站不同源，不 403） |
| `baike.baidu.com` / `3dcontentcentral` | 403 / 超时 |

**Wayback 使用要点**（踩坑记录）：先查 CDX，再回放时**必须保留 `?id=xxxx` 查询串**，
否则 `id_` 回放 404：
```
http://web.archive.org/cdx/search/cdx?url=help.solidworks.com/2025/english/SolidWorks/toolbox*&output=text&fl=timestamp,original&collapse=urlkey
https://web.archive.org/web/<timestamp>id_/<完整原始URL含?id=xxx>
```

**最强证据来源**：用户本机装有 SolidWorks 2026 SP4.1，且 **Toolbox 已安装**于 `D:\SOLIDWORKS Data`。
本报告 Q1/Q4/Q5 的结论直接来自该目录实查，比任何网页都权威。

---

## 1. Toolbox 是什么形式的东西？

### 结论：**不是 .swbox**。是一个目录树 + 一个数据库文件 + 若干 .sldprt。

**⚠ 前提纠正：SolidWorks Toolbox 官方并不存在 `.swbox` 这个扩展名。**
最容易混淆的两个真实扩展名是 `.tbox` 和 `.sldedb`。本机实查（`D:\SOLIDWORKS Data\`）：

```
D:\SOLIDWORKS Data\
├─ ToolboxVersion.dat          ← 版本锁文件
├─ ToolboxStandards.xml        ← 标准清单，每项 <Source>gb.zip</Source>
├─ browser\                    ← 19 个标准目录 + ToolboxFiles.index
├─ lang\english\swbrowser.sldedb   ← 数据库（19 MB）
└─ updates\*.tbox             ← 每个标准一个更新包
```

- `updates\0_Index Toolbox content.tbox` + `1600_Install Ansi Inch.tbox` … 共 20 个 `.tbox`
  文件头为 .NET 序列化 `Lsldtoolboxupdater, Version=34.4.1.1011` —— **`.tbox` 是「标准件增量更新包」，不是零件**。
- `browser\ToolboxFiles.index`（668,983 字节）文件头 `Isldtoolboxdata, Version=34.4.1.1011` —— 全库零件索引。
- 数据库文件历史上是 `SWBrowser.mdb`，现已改为 SQLite 格式 `.sldedb`（安装目录内另带 `DatabaseConverter.exe` 做格式转换）。

### 一个文件代表一个零件？—— 是
每个标准件就是一个普通 `.sldprt`，**尺寸是同一文件内的配置**（configuration），不是多个文件。
全库共 **1,844 个 `.sldprt`**。

官方 API 佐证（`ISldWorks.ExportToolboxItem` 的 Remarks 原文）：
> Specify `StdToImport` with the path and file name beneath `C:\SOLIDWORKS Data\browser`,
> e.g. `"ansi inch\bolts and screws\hex head\heavy hex bolt_ai.sldprt"`.

官方帮助原文（Toolbox Overview）：
> The Toolbox library contains **a folder of master part files** for supported standards
> along with component size and configuration information.

来源：
- https://raw.githubusercontent.com/kilwizac/solidworks-api-mcp/main/solidworks-api/sldworksapi/interfaces/ISldWorks/ExportToolboxItem.md
- https://web.archive.org/web/20250209234038id_/https://help.solidworks.com/2024/english/SolidWorks/toolbox/c_toolbox_overview.htm?id=363d92fc6e274207a01de55525c83fe5

### 与「设计库 / Toolbox 设置」的关系 —— 是**三个不同的东西**

| 名称 | 是什么 | 本机位置 |
|---|---|---|
| **Toolbox（标准件库）** | 19 套国际标准紧固件/轴承/结构件，1844 个 .sldprt | `D:\SOLIDWORKS Data\browser\` |
| **Design Library（设计库）** | 特征/块/标注/成形工具/智能组件，扩展名 `.sldblk` `.sldsffvt` `.sldweldfvt` `.sldgtolfvt` `.sldmtnfvt` | `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library\` |
| **Toolbox 设置** | `选项 → 异型孔向导/Toolbox`，配置标准集、根文件夹、写权限、密码 | 注册表/配置 |

Design Library 本机实查目录：`annotations / assemblies(模具底座) / features / forming tools / motion / parts(hardware) / routing / smart components`。
**它不放标准件**，放的是可复用的特征与块。中文教程也明确区分（社区来源）：

> Toolbox（自带库）：适合通用标准件（GB、ISO、ANSI）… **设计库（Design Library）：适合厂家选型件（如 SMC 气缸、MISUMI 直线导轨）**
> —— https://bbs.plcjs.com/thread-639985-1-1.html （PLC技术网，2026-05-26，社区/经销商软文）

---

## 2. 官方从哪里下载？

### 结论：**没有独立的下载页面。Toolbox 是 SOLIDWORKS Installation Manager 里的一个产品勾选项。**

安装管理器中路径：`产品选择 → SOLIDWORKS > SOLIDWORKS Toolbox`，
外加一个独立页 `Hole Wizard/Toolbox Options`。

官方安装指南（2021，PDF 第 146 页）原文：
> To create a new version, in the **Product Selection screen, expand SOLIDWORKS > SOLIDWORKS Toolbox**
> and select which standards to support for the Toolbox. **All standards are selected by default.**

来源：https://files.solidworks.com/Supportfiles/SW_Installation_Guide/2021/English/install_guide.pdf

### 实际下载文件（Wayback 抓到的真实 CDN 路径）

```
https://dl-ak.solidworks.com/secured/sw2024/sw2024_sp03.1_f/x64/240606.002-3/Toolbox_ansi_inch.exe?__gda__=<签名令牌>&ext=.exe
```
19 个文件，文件名与 `ToolboxStandards.xml` 的 `<Source>` 一一对应：
`ansi_inch / ansi_metric / as / bsi / cisc / din / gb / is / iso / jis / ks / mil / pem_inch / pem_metric / skf / torrington_inch / torrington_metric / truarc / unistrut`

（.exe 内部即 `ToolboxStandards.xml` 里记的 `<Source>gb.zip</Source>` 那个 zip。）

### 是否需要登录 / 序列号？
**需要。** 三重证据：

1. 路径含 `/secured/`，且带 `__gda__=<hash>_<md5>&ext=.exe` —— 一次性签名下载令牌，无法裸链下载。
2. 官方安装指南：
   > SOLIDWORKS Installation Manager selects all products **to which you are entitled**.
3. 默认安装根目录由 `TOOLBOXFOLDER = "C:\SOLIDWORKS Data"` 指定（本机被改到了 D 盘）。

**操作路径**：SolidWorks 客户门户（https://customerportal.solidworks.com/）登录 → 下载 SOLIDWORKS Installation Manager → 选产品时展开 Toolbox → 重新执行即可补装。
「Toolbox 设置」（`选项 → 异型孔向导/Toolbox`）**只负责指向根目录和权限，不负责下载数据**。

---

## 3. 收费吗？（最关键）

### 结论：**免费。不额外收费，是 SolidWorks Professional / Premium 的内置能力（Capability）。**

**官方页面证据**（`CAD Library: SolidWorks Toolbox` 产品页，solidworks.com 官方域名）：

> **Related Packages: SolidWorks Premium  SolidWorks Professional**
> …**Capability Included In:**
> …SolidWorks Toolbox is a vast component library containing over a million standard hardware items.
> These components can be used "as is" or can be customized to meet your specific company standards.
> — **©2013 Dassault Systèmes SolidWorks Corp.**

- 页面结构是 `Products > 3D CAD > Capabilities > CAD Library: SolidWorks Toolbox`，
  **归类为 Capability（能力），不是 Product（产品）**。
- 页面上**没有任何价格、没有独立购买按钮**，「Get a Quote / Contact Sales」指向的是 SolidWorks 套餐，不是 Toolbox。
- 19 套标准「All standards are selected by default」——**不分档、不单独计价**。

来源：https://web.archive.org/web/20130112001934id_/http://www.solidworks.com:80/sw/products/3d-cad/solidworks-toolbox.htm

**「over a million standard hardware items」是配置数，不是文件数** —— 本机实查文件数为 1,844 个 `.sldprt`（每个文件含大量配置）。

### 是否 2020 后停止提供？—— **没有。这条前提不成立。**
- 2024、2025 版帮助目录里 Toolbox 仍是独立章节。
- 2026 版帮助页（`help.solidworks.com/2026/.../toolbox/c_toolbox_overview.htm`）仍可被搜索引擎索引到。
- **本机 SW2026 SP4.1 实测 Toolbox 已安装且完整**（1844 个零件、19 套标准、数据库 19 MB）。
- 2025 官方帮助还在新增 Toolbox 章节页（Integration of Toolbox Components in the 3DEXPERIENCE platform、
  Saving Existing / Saving New Toolbox Components），说明仍在积极维护。

### 中国区报价陷阱（务必不要引用）
天极网（yesky.com，B2B 比价聚合站，页面 ©2017）有一条：
> **Solidworks Toolbox (三维零件库)　市场参考价：￥22675**
> https://wap.yesky.com/product/product/228/228266/price.shtml

⚠ **这是聚合站的陈旧挂牌价，不是达索价格表，不能作为「Toolbox 要花 2 万」的依据。**
官网页面已明确定位为 Professional/Premium 的内置能力。

### 第三方 Toolbox 扩展收费情况

| 扩展 | 性质 | 价格 | 来源性质 |
|---|---|---|---|
| **KRENKO Composer Toolbox** | 面向 CATIA/SW **Composer** 的文档元数据工具（非标准件） | 「single user license, no network license」，**价格未公开**，需邮件 info@krenko.de 询价 | 达索官方 partner PDF |
| **凯元工具 KYTool** | SolidWorks 插件，**含参数化丝杠** + 国标件库 | **￥138** | 代理商站（智诚科技），站点自述「该工具为网友上传」 |
| 麦迪 / 今日制造 | 中文第三方标准件插件 | **查不到公开报价** | 社区提及，无报价页 |
| MISUMI / HIWIN / THK / NSK / SMC 选型件库 | 厂商官方选型模型（多为 Design Library / 合作伙伴插件方式） | 模型下载多免费，但**零件本身是商品** | 厂商站 |

来源：
- KRENKO：https://files.solidworks.com/partners/pdfs/14277-5574-Toolbox_DB_V3_en.pdf
  （注意：该 PDF 文件名带 Toolbox_DB，但内容是 **Composer** Toolbox，标题即 "Composer Toolbox"，与 SolidWorks 标准件库无关）
- 凯元：https://www.ict.com.cn/chajian/5453.html

---

## 4. 版本兼容性

### 结论：**严格锁定到「主版本」，且必须连 Service Pack 一起匹配。旧包不能直接用。**

**官方安装指南原文（两处，互相印证）：**
> Upgrading a Toolbox to a new SOLIDWORKS major release version makes that Toolbox
> **incompatible with computers running prior major release SOLIDWORKS versions**.

> If the location contains an older major version of Toolbox, the client installation upgrades
> that Toolbox to the new major version. **The files are no longer be compatible with previous
> major versions of SOLIDWORKS.**

来源：https://files.solidworks.com/Supportfiles/SW_Installation_Guide/2021/English/install_guide.pdf
（同一句话在帮助站 Notes About Configuring SOLIDWORKS Toolbox 页亦出现：
https://web.archive.org/web/20241203053809id_/https://help.solidworks.com/2025/English/Installation/install_guide/c_notes_about_config_toolbox.htm）

**本机铁证** —— `D:\SOLIDWORKS Data\ToolboxVersion.dat` 全文：
```
// Toolbox version file
// SOLIDWORKS 2026 SP4.1
SuiteVersion = 20260-40401-1100
FileVersion = 34.4.1.1011
<End>
```
`SuiteVersion 20260-40401-1100` = **SW 2026 + SP4.1**。同版本号也出现在
`browser\ToolboxFiles.index`（`Isldtoolboxdata, Version=34.4.1.1011`）和
`updates\*.tbox`（`Lsldtoolboxupdater, Version=34.4.1.1011`）—— 三处版本必须一致。

**对 SW2026 用户的实操结论：**
1. 不能把 2024/2025 的 Toolbox 目录拷过来用 —— 会不兼容。
2. 同一主版本内**可以跨 SP 升**（安装指南把「同一主版本内的 Service Pack 升级」列为支持的升级类型）。
3. 跨主版本（2026 → 2027）时，官方给的唯一办法是**先复制一份 Toolbox 目录到新位置，再升级那份副本**，
   让旧版本机器继续用旧目录。
4. PDM 环境升级时，官方要求先 checkout 数据库文件
   `SWBrowser.mdb`（新版为 `swbrowser.sldedb`），并确认 `Updates\`、
   `ToolboxStandards.xml`、`Browser\ToolboxFiles.index` 三个路径存在，缺则联系经销商。

---

## 5. 除了官方，有没有免费/开源的替代品？

### 5.1 先说最关键的一条：**官方 Toolbox 根本没有丝杆、导轨、欧标铝型材**

我把本机整库枚举了一遍（1844 个 .sldprt，19 套标准）：

**全库一级分类（去重后全部 21 个）：**
```
bearing  bearings  bolts and screws  bolts and studs  fasteners  jig bushings  keys
nuts  o-rings  orings  pins  pins and keys  power transmission  retaining rings
rivets and studs  screws  seals  standoffs  structural members  studs
washers  washers and rings
```

| 用户要的 | Toolbox 里有吗 | 实查结果 |
|---|---|---|
| **丝杆 / 滚珠丝杆** | ❌ **没有** | 全库无任何 ball screw / leadscrew 目录。含 "screw" 的文件全部是 `bolts and screws` 下的紧固件（machine screw nut hex_ai、cross recessed ctsk screws gb 等） |
| **直线导轨 / 直线轴承** | ❌ **没有** | `bearings` 下 11 套标准**只有** `ball bearings`（旋转轴承）和 `roller bearings`（旋转轴承），GB 套是 `rolling bearings`。**无 linear bearings / rails**。目录名含 linear/rail/guide 的匹配数为 **0** |
| **铝型材（欧标 2020/3030/4040）** | ⚠ **只有美制结构型材，不是欧标型材** | 铝只有两处：<br>① `Ansi Inch\structural members\aluminum\` —— 12 个**美制**结构型材：`channel_aai` `cs channel_aai` `i beam_aai` `l angle_aai` `ls angle_aai` `pipe standard_aai` `pipe x strong_aai` `s beam_aai` `tee section_aai` `tube rectangular_aai` `tube square_aai` `zee section_aai`<br>② `Unistrut\structural members\aluminum\` —— 12 个 **Unistrut** 槽钢/管件：`a1000_ea` `a4000_ea` `a4001_ea` `p1000_ea` `p1001_ea` `p4000_ea` `p4001_ea` `p5500_ea` `p6000_ea` `p6001_ea` `p7000_ea` `p7001_ea`<br>**没有 40×40 / 3030 / 4040 这类欧标 T 槽铝型材** |

> 官方对精度的免责声明（Toolbox Overview）：
> The fasteners provided in Toolbox are **approximate representations and do not include accurate thread detail**…
> Toolbox gears are representations for machine design purposes. They are **not true involute gears** that you can use for manufacturing.

**⇒ 对这个用户而言，官方 Toolbox 解决不了他的三个诉求，方向要换。**

### 5.2 合法免费/可下载的模型来源

| 渠道 | URL | 性质 | 可信度 |
|---|---|---|---|
| **3D ContentCentral**（达索自家） | https://www.3dcontentcentral.cn/Parts.aspx | 达索官方免费账号制模型库，供应商上传 | 官方；**本机网络访问超时，未能实加载**，仅由搜索引擎确认在线。帮助页：https://help.solidworks.com/2024/chinese-simplified/ccuser/c_3dcc_why_register_create_account.htm |
| **TraceParts** | 官方合作页 https://www.solidworks.com/partner-product/traceparts-3d-product-catalog-and-3d-contentcentral-expert | 达索官方合作伙伴，数百万标准件/供应商件 | 有免费层；**具体下载限额查不到官方明确数字，标记为未确认** |
| **GrabCAD** | 例：https://grabcad.com/library/sxg5080-motorized-ballscrew-linear-slide-1 | 社区上传 | ⚠ **逐个模型许可不同，必须逐个核对作者授权**；多为 .STEP 中性格式 |
| **厂商官网** | MISUMI 有 SolidWorks 集成手册：https://kr.misumi-ec.com/service/rd/icc/sw/help/images/pdf/Hands-onManual_ver1.0_inCADComp.pdf ；HIWIN/MISUMI 选型模型经 Design Library 或合作插件导入 | 官方厂商 | 模型下载免费，**零件是商品**；质量与真机一致，是工程上最靠谱的 |
| **GitHub** | 用 `gh search repos "linear guide sldprt"` 等检索 | — | **查不到成规模的免费 .SLDPRT 标准件库**；多数是零散或侵权风险项目 |

⚠ **明确排除**：GitHub 上存在 `SolidWorks-CAD`（812★）/ `SolidWorks-Crack`（287★）类仓库，
属破解/盗版分发，**零接触、不推荐**。

### 5.3 中文圈实际怎么做

来自 PLC技术网 2026-05-26 的实践帖（社区/经销商软文，非官方）：
> **一、标准件调用的三大主流途径**
> 1. **Toolbox（自带库）**：适合通用标准件（GB、ISO、ANSI），如螺栓、垫圈、轴承。优点是集成度高，缺点是如果设置不当，文件容易乱。
> 2. **设计库（Design Library）**：适合厂家选型件（如 SMC 气缸、MISUMI 直线导轨），需手动添加特征。
> 3. **第三方插件（麦迪、凯元、今日制造）**：功能最全，支持自动生成配置，推荐资深工程师使用。

配合 Pack and Go 时**要取消勾选 "Toolbox 文件"**，否则发给别人会因 Toolbox 路径不同而报错。
—— https://bbs.plcjs.com/thread-639985-1-1.html

**针对本用户三类的推荐路径：**

| 类别 | 推荐做法 | 成本 |
|---|---|---|
| **丝杆**（SFU1605 / HGH16 等） | ① 参数化自建（用凯元 KYTool 丝杠工具，￥138）；② HIWIN/上银官网下载 SolidWorks/STEP 模型；③ 用 SolidWorks 的 `ISketchManager` 螺旋线 + 扫掠自建（丝杆几何规则，最适合脚本化） | ¥0 ~ ¥138 |
| **直线导轨**（HGH20 / MGN12） | **只能走厂商**：HIWIN / 上银 / THK / 导轨厂商官网 3D 下载，或 MISUMI 经 Design Library 集成。Toolbox 没有 | 免费下载模型 |
| **铝型材** | Toolbox 里的 `Ansi Inch\...\aluminum` 是美制型材，**不能当欧标用**；欧标 4040 需向型材厂商（misumi / 上银 / 东莞产）要 SolidWorks 模型，或按 T 槽截面自建 | 免费~询价 |

### 5.4 给「脚本自动插入」的直接技术结论（重要）

**官方 API 里没有「按标准+尺寸插入 Toolbox 零件」的接口。** 可用的只有：

| 成员 | 签名 | 用途 |
|---|---|---|
| `ISldWorks.ImportToolboxItem` | `int ImportToolboxItem(string StdToImport, string DestinationFilePath)` | 导入 **Excel `.xslx`** 孔数据，**不是零件**。命名 `标准_孔类_孔型.xslx` |
| `ISldWorks.ExportToolboxItem` | `int ExportToolboxItem(string StdToExport, string DestinationFolderPath)` | 导出上述 xslx |
| `IModelDocExtension.ToolboxPartType` | `int {get;set;}` | 取/设零件是否 Toolbox 零件，配 `swToolBoxPartType_e` |
| `swToolBoxPartType_e` | `swNotAToolboxPart` / `swToolboxStandardPart` / `swToolboxCopiedPart` | 0/1/2 |
| `IAssemblyDoc.UpdateToolboxComponent` | `int UpdateToolboxComponent(int AssemblyLevelToUpdate)` | 按当前 Toolbox 设置刷新装配中的 Toolbox 组件 |
| `IPackAndGo.IncludeToolboxComponents` | 属性 | 打包时是否含 Toolbox 组件 |
| `swToolBoxPropertyName_e` | `PartName`=0 / `Specification`=1 / `Standard`=2 | 读零件名/规格/所属标准 |
| `swApiToolboxItemExportStatus_e` / `swApiToolboxItemImportStatus_e` / `swAssemblyUpdateToolboxComponentStatus_e` | 状态枚举 | 判成败 |

来源（官方 API 文档 GitHub 镜像）：
https://github.com/kilwizac/solidworks-api-mcp/tree/main/solidworks-api （7★，官方文档镜像）
本机同源离线副本：`C:\swapi\types\ISldWorks\ImportToolboxItem.md` 等

**Toolbox Browser 是 UI 加载项**，其类型库 GUID 为 `{ED783340-D5DB-11d4-BD5A-00C04F019809}`，
API 面向第三方 PDM 集成（`SolidWorks.Interop.swbrowser` / `sldtoolboxconfigureaddin`），
本机 `C:\swapi\docs\toolboxapi\GettingStarted-toolboxapi.md` 有完整说明。
**没有「脚本化选标准件」的 COM 入口。**

⇒ **可行的脚本路线**：直接按磁盘路径定位零件，走普通装配 API 插入。
路径规则 = `D:\SOLIDWORKS Data\browser\<标准>\<大类>\<小类>\<零件>.sldprt`
（例：`D:\SOLIDWORKS Data\browser\GB\bolts and screws\hex bolts and screws\hex bolt gb.sldprt`，
配合 `swToolBoxPropertyName_e` 读配置名做尺寸选择），再用常规 `AddComponent` / `InsertFile` 插入。

---

## 附：一句话速查

| 问题 | 答案 |
|---|---|
| 1. 形式 | 目录树 + `.sldedb` 数据库 + 1844 个 `.sldprt`；更新包是 `.tbox`。**没有 `.swbox`**。与 Design Library 是两回事 |
| 2. 下载 | 无独立下载页；Installation Manager → `Hole Wizard/Toolbox Options`。实际文件在 `dl-ak.solidworks.com/secured/…/Toolbox_<标准>.exe`，需客户门户登录 + 订阅授权 |
| 3. 收费 | **免费**，Professional/Premium 内置 Capability，19 套标准默认全选、不分档。第三方插件另计（如凯元 ¥138）。**未停售** |
| 4. 兼容 | 严格锁主版本+SP。本机 = `20260-40401-1100`（2026 SP4.1）。旧包不可跨主版本复用，需复制后单独升级 |
| 5. 替代 | **官方库无丝杆/无导轨/无欧标铝型材**（已实查确认）。丝杆自建或凯元插件；导轨走 HIWIN/MISUMI 厂商；铝型材走型材厂商。免费库：3D ContentCentral（达索）、TraceParts（部分免费）、GrabCAD（逐个核授权） |

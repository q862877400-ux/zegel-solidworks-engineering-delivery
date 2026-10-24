# 机械标准件 3D 模型合法获取渠道调研（丝杆 / 直线导轨 / 铝型材）

调研日期：2026-09-28 · 环境：中文 Windows + SolidWorks 2026 · 全部结论基于本机实测抓取

## 0. 抓取环境说明（影响可复现性，先读这条）

```
http_proxy  = http://127.0.0.1:7897
https_proxy = http://127.0.0.1:7897
ALL_PROXY   = http://127.0.0.1:7897
no_proxy    = localhost,127.0.0.1,::1,...
```

本机所有出网请求都走本地代理 7897。凡是本报告写「本机实测不可访问」的，都同时用
`--noproxy '*'` 直连复测过。

标注约定：
- **【官网明写】** = 逐字引用了本机成功抓到的官网页面文字
- **【推断】** = 证据指向该结论，但不是页面原文
- **【查不到】** = 试过、抓不到，不补

---

## 1. 达索 3D ContentCentral —— **本机实测不可访问**（连不上，不是"要注册"）

### 实测记录

| 目标 | DNS | TCP443 | HTTP |
|---|---|---|---|
| `https://www.3dcontentcentral.com/` | DNS_FAILED | CLOSED | 000 |
| `https://www.3dcontentcentral.cn/` | OK | OPEN | 000（超时） |
| `https://www.3dcontentcentral.com.br/` | OK | OPEN | 000（TLS 协商挂死） |
| `https://www.3dcontentcentral.kr/` | OK | — | 000 |
| `https://beta.3dcontentcentral.cn/` | OK | — | 000 |

失败点在 TLS：`curl -v` 显示 `Establishing HTTP proxy tunnel … 200 Connection established` →
`ALPN: server accepted http/1.1` → `schannel: remote party requests renegotiation` →
`schannel: renegotiating SSL/TLS connection` → 挂死 50s 超时。

换过 4 组 TLS 参数仍不行：`--tlsv1.2` / `--ssl-no-revoke` / `--insecure --ssl-no-revoke` /
`--http1.1 --insecure`；又用 `Invoke-WebRequest`（TLS 1.2，200s 超时）试过一次，同样超时；
再用 `--noproxy '*'` 直连，仍然 000。内置 `web_fetch` 对 `.com` / `.cn` / `beta.3dcontentcentral.cn`
全部 `TypeError: fetch failed`。

### 逐项回答

| 问题 | 结论 |
|---|---|
| 能否匿名浏览和下载 | **【查不到】** —— 站点一个字节都拿不到，无法区分「要注册」还是「本来就公开」 |
| 免費层限制（每日下载数/分辨率/格式） | **【查不到】** |
| 丝杆/导轨/铝型材零件页 URL | **【查不到】**。搜索引擎收录了两个真实 URL，但本机都打不开，只能证明 URL 结构存在、证明不了内容：<br>· `https://www.3dcontentcentral.com.br/download-model.aspx?catalogid=171&id=726889`<br>· `https://www.3dcontentcentral.kr/parts/browse/악uate시형/LinTech/6.aspx` |
| 文件格式 | **【查不到】** |

### 关于免费层：一条重要的意外发现

**`help.solidworks.com` 本机实测可访问（HTTP 200，994KB）——与预设的 403 不同。**

抓到的三个官方页面：
- `https://help.solidworks.com/2024/english/ccsupplier/c_free_sub_level.html`（免费订阅层）
- `https://help.solidworks.com/2024/english/ccsupplier/c_standard_sub_level.html`
- `https://help.solidworks.com/2024/english/ccsupplier/c_subscription_levels.html`
- `https://help.solidworks.com/2024/english/ccuser/c_3dcc_downloads.htm`

但正文是 Next.js 客户端渲染，裸 HTML 里只有 `Loading JS...`，没有文章文字
（关键词计数：Free Subscription=4 次（全在导航/URL 里），"Downloads per"=0，"per day"=0）。

从 JS chunk 里找到了站内内容代理端点并成功调用：
```
GET https://help.solidworks.com/printPopup?version=2024&lang=english&product=ccsupplier
    &filePath=c_free_sub_level.html&id=<topicId>   →  200 JSON
```
需要精确 topicId。id 来自页面里的 `?id=0.0.3.0.0`，回传后报
`Element with id 0.0.3.0.0 do not have the children`（叶子节点取不到子内容）。
穷举 id=0 / 空 / 0.0.0.0.0 / 0.0.1.0.0 / 0.0.2.0.0 全部失败。

Wayback 回放 `web.archive.org/web/2024id_/help.solidworks.com/...` 返回
`429 … flagged it as suspected abusive bot traffic`（IP 级封）。

**→ 每日下载数、分辨率、格式限制：查不到。** 建议下一步用真实浏览器（browser4-cli）打开
`c_free_sub_level.html`，或换一个没被 429 的出口 IP 回放 Wayback。

---

## 2. HIWIN 上银 —— 需注册 + 需先同意条款；没有铝型材；格式查不到

### 入口（官网明写 + 实测 200）

`https://www.hiwin.com.cn/` 首页导航项「2D/3D CAD」→ `https://www.hiwin.com.cn/cad_download/`

该页 HTML 里硬编码的类目 href（可直接用，不必解析 DOM）：

```
丝杆     /cad_download/ballscrew.aspx     → https://www.hiwin.com.cn/cad_download/ballscrew.aspx
直线导轨 /cad_download/linear_guideway.aspx
滚珠花键 /cad_download/ball_spline.aspx
轴承     /cad_download/bearings/CAD_Bearings_select_page.aspx
直驱电机 /cad_download/direct_drive_motor/direct_drive_motor_list.aspx
（另有单轴机器人/多轴机器人/直线电机/伺服电机/ spindle 等共 23 个类目）
```

**铝型材：没有。【官网明写】** —— 23 个 CAD 类目里没有任何型材/挤出件项。
**【推断】** HIWIN 不做铝型材，这条线找错厂家了。

### 要不要注册

- 匿名打开 `ballscrew.aspx` / `linear_guideway.aspx` 都返回 **200**，但**正文内容区是空的**；
  页面同时渲染完整的 **Member Login 表单**：Email / Password / Validation Code /
  `I agree to HIWIN Terms of Use *`，以及一个 "Yes, I Agreed" 条款弹窗。
  → **【推断，强】模型列表和下载按钮在登录后才渲染。**
- 注册页 `https://www.hiwin.com.cn/sign_up.aspx`（实测 200）字段：
  Name / Email / Company / Department / Title / Phone / Industry / Country。
  **没有任何付费或企业规模字段** → **【推断】注册免费。**
- `https://www.hiwin.com/cad_download/`（英文全球站）→ **404**。CAD 下载只在中国站。

### 格式

**【查不到】** —— 下载在登录墙后面，没有任何格式列表出现在匿名 HTML 里。不猜。

### ⚠ 许可限制（官网明写，对脚本场景是硬约束）

HIWIN Terms of Use 原文（`cad_download` 页顶部，每个页面都带）：

> All Information (in whole or in part) of the Website may not be **sold, transmitted,
> modified, publicly published and used**, or otherwise exploited to cause any damage to
> the interests of HIWIN, for any purpose **without HIWIN's express consent**.

配合注册要填 Company / Department / Title / Phone 四项企业信息 —— 拿来做自动化管线要先过法务。

---

## 3. THK —— 需注册（免费），**没有原生 SLDPRT**

### 入口（实测 200，官网明写）

- 技术站说明页：`https://tech.thk.com/en/help/help_3dcad_en.html`（15,682 字节）
- 实际下载工具：`https://online.thk.com/tools/cad/us/en/?languageIso=en`（200，但是 JS 应用，正文只有 4 行）
- 技术站导航：HOME > HELP > CAD Data / Catalog Information / Member Information / My Catalog / **Logout**

### 格式（**官网明写，完整清单**）

> List of Supported CAD Data Formats:
> **[2D-CAD data]** DWG 12/13/14/2000 · DXF 12/13/14/2000 · ME10.etc.
> **[3D-CAD data]** DXF 3D · **STEP 203/214/Unigraphics** · ACIS SAT 2.0/3.0/4.0 · IGES · VDA-FS. etc.

**没有原生 .SLDPRT。** 六家里只有 MISUMI 有。

THK 还有个 **"Insert to CAD"** 按钮（官网明写）：选好规格后可以把数据直接送进已安装的 CAD 软件
打开 —— 「Regarding the insertion destination CAD, the generated CAD data is directly opened
with the CAD software. The corresponding CAD software must be installed.」

### 要不要注册 / 收费（**官网明写**，这是最硬的一条）

`https://www.thk.com/opm/us/en/online_service/explanation/member/`（实测 200）原文表格：

| 功能 | 可用对象 |
|---|---|
| Product Information（dimensional drawings, tables, detailed specifications） | **All Users — *no registration required*** |
| Product FAQ | **All Users — *no registration required*** |
| Catalog Downloads | **All Users — *no registration required*** |
| Designer（选型 + 寿命计算 + **CAD data downloads**） | **Full Member** |
| **CAD Download** | **Full Member**, Online Store Member\*（\* 仅在线商店产品的 CAD 下载） |

同一页顶部：*"THK Online Services **are free for registered members**."*

**→ 费用结论（明确）：注册免费，CAD 下载要 Full Member 资格，Full Member 本身免费，不需要付费。**
登录实际跳转：`https://www.thk.com/us/en/auth/login?redirect_link_path=https%3A%2F%2Fonline.thk.com%2Ftools%2Fcad%2F...`

---

## 4. MISUMI 米思米 —— **唯一实测确认提供原生 .SLDPRT**；需登录；免费

### 入口

- 中国站 `https://www.misumi.com.cn/`（实测 200）
- CAD 下载说明 `https://id.misumi-ec.com/guide/category/ecatalog/use_cad.html`（实测 200）
- 文件格式表 `https://vn.misumi-ec.com/guide/category/ecatalog/file.html`（实测 200，25,534 字节）
  （注：`https://www.misumi.com.cn/guide/category/ecatalog/file.html` → **404**，中国站没这个页）
- SolidWorks 插件手册 `https://www.misumi.com.cn/pr/fa/b9c60p3c/aa/method/`（实测 200）
- inCAD Library `https://www.misumi.com.cn/asia/incadlibrary/`（实测 200，612 件案例）

### 需登录 / 收费（官网明写）

> "**You will need to log into your account to download CAD data.**"
> "CAD data may be unavailable for some products."

inCAD Library 页：「成为会员并登录，即可免费下载CAD数据等其他服务。」+ 免责「**本服务现在免费提供CAD数据等，
但今后可能会收费。**」

**→ 费用结论：免费（会员制），不收费。** 插件有登录窗口页 + 「登录失败，显示(status=号码)怎么办？」FAQ
→ 【推断】插件也要 MISUMI 账号。

### 格式（**官网明写 —— 本次调研最关键的一条**）

| 类型 | 格式 | 扩展名 |
|---|---|---|
| **3D 原生** | **SolidWorks (>=2015)** | **.sldprt** ✅ |
| 3D 原生 | SolidWorks Macro (>=2001+) | .swb |
| 3D 原生 | Autodesk Inventor (2024/2023/2022/2021) · CATIA(>=V5) · NX(2406…) · Solid Edge · AutoCAD(>=V14) · Revit | .ipt/.catpart/.prt/.par/.dwg/.rfa |
| 3D 中间 | **Parasolid Binary / Text (V15)** · **STEP (AP203、AP214)** · IGES · SAT(7) | .x_b / .x_t / .stp / .igs / .sat |
| 3D 中间 | DWG · DXF · STL · JT · IFC · PDF3D · … | |
| 2D | DWG · DXF · HPGL · MI · BOM(.xml/.json) · 图片(JPG/PNG/BMP/TIFF/SVG) | |

> "Downloaded Data is compressed into a **zip** file."

### SolidWorks 插件（**确认存在**，实测 200）

米思米 RD / RAPiD Design for SolidWorks。手册目录实测包含：

- `Step1.如何检索产品？` → `Step2.选定模型导入` → `Step3.变更参数` → `Step5.含型号保存`
- **「文件名【base model~】是什么？」**
- **「利用已有型号搜索不同尺寸的模型。」**
- 「如何在保存装配体文件同时创建part零件？」
- 页面结构：使用环境 / 界面解析（基础选型页面 / 设计窗口页面 / **登录窗口页面**）/ 设置界面详解 / 常见问题

**【推断】对脚本化最关键的三点：**
1. **文件名带品番**（「含型号保存」）→ 本地路径可由品番反推
2. **支持按已有品番换尺寸**（「利用已有型号搜索不同尺寸的模型」）
3. 插件能直接在 SolidWorks 里落 part，绕开外部文件路径

### 铝型材 / 导轨（官网明写）

- inCAD Library 分类树里有「工业用材料 → **铝合金型材、管材**」；另有「直线运动零件」
- 铝型材 VONA 分类码 **M1501010100**（HFS 5 Series Aluminum Frames）：
  `https://us.misumi-ec.com/vona2/mech/M1500000000/M1501000000/M1501010000/M1501010100/`
- **MISUMI 卖 HIWIN 的导轨**（实测 200）：
  `https://us.misumi-ec.com/vona2/maker/hiwin/mech/M0100000000/M0110000000/M0110050000/`
  = "HIWIN - Standard Linear Guides : Ball Arrangement Standard"

**→ 一个账号同时覆盖：HIWIN 导轨 + 铝型材 + 丝杠，且都是原生 SLDPRT。**

### ⚠ 脚本化障碍（实测，这是选型时必须知道的）

| 站点 | `vona2` 产品页实测 |
|---|---|
| `cn.misumi-ec.com` | **返回反爬挑战页**（`var arg1='5d9628…'` + 加密 blob），不是产品内容 |
| `us.misumi-ec.com` | **200，正常页面**（有 VWO 埋点但不拦） |
| `id.misumi-ec.com` | 429（被我打限流） |

→ **【推断】中国站产品页不能直接 HTTP 抓，脚本要走 us 站路径或用真实浏览器。**

---

## 5. 国产件商

### 凯元工具 KYTool（济南凯元软件）—— 目录最稳，但**模型库要付费**

- `http://www.kytool.cn/` → 301 到 `/Login.aspx`（实测：整站要登录）
- 模型库下载说明 `http://kytool.cn/help/30.4GBDown.html`（实测 200，**官网明写**）：
  - **「模型库是付费功能，若没有付费，下载下来也用不了。」** ← 费用结论明确
  - 共 6 个模型库
  - 三种下载方式：① 插件自动下载 ② 浏览器直下 ③ 百度网盘
    `https://pan.baidu.com/s/1mt2IUcc9JS2szOWsJMCCgw` 提取码 `tgtq`
  - **存放路径（官网明写）**：`【凯元安装路径】\datas\lib\`
  - 需凯元 ≥ 4.68 版
  - 关联页 `http://kytool.cn/help/30GB.html`（实测 200）
- 它是**国标件库 / 外购件库**（GB 标准件为主）。**丝杆 / 导轨 / 铝型材是否在其中：查不到**
  （模型库在付费墙后，没有公开目录）

### 珊瑚网 shanhu3d.com —— 匿名可读，但是**金币制 + 授权不明**

- 模型页 `https://www.shanhu3d.com/model/10601709`（实测 200，175KB，**匿名可读**）
- 该页文件列表实测含：**HGH20CA.SLDPRT**、**HGR20.sldprt**、Linear motion guide.SLDASM、
  Linear motion guide.STEP、Linear motion guide.x_t
- **「所需金币：20」** → 要注册 + 站内充值，**不是免费**
- 免责原文：「本网站模型由用户自行上传，如权利人发现存在误传其作品情形，请及时与本站联系。」
  → **授权链不明，商业使用不能碰**

### 麦迪 / 今日制造 —— **查不到**

本轮没有找到它们提供可下载 3D 的任何证据页。

---

## 6. GrabCAD —— 站可访问，但是 SPA；**授权明文排除商业使用**

### 可访问性

- `https://grabcad.com/` 实测 200（106,395 字节）
- **是 Angular SPA**（实测 `<html ng-app="communityFrontendApp">`）
  三个分类搜索页返回**完全相同的 32,842 字节**，结果不在 HTML 里
  → **不能靠裸 HTTP 抓。脚本化需要真实浏览器或官方 API。**

### 匿名能不能下

- 官网首页 "Download Free" 按钮实测 **301 → `https://grabcad.com/profile/register`**
- 匿名打开 `https://grabcad.com/library/ball-screw-8` 返回 200，但 HTML 里**没有下载按钮**、**有登录标记**
- → **【推断，强】下载要注册免费账号**
- **免费账号的具体额度（每天几个 / 多少 GB）：【查不到】**（SPA + 没登录，看不到）

### 三类库的实际页

| 类别 | URL |
|---|---|
| 丝杆 | `https://grabcad.com/library/ball-screw-8` |
| 导轨 | `https://grabcad.com/library/linear-rail-hgr20r-1/likes` |
| **导轨（参数化）** | `https://account.grabcad.com/library/hgr20-linear-guide-subassembly-configurable-rail-length-150-4000-mm-1` |
| 铝型材 | `https://grabcad.com/library/4040-v-slot-aluminum-extrusion-1` |
| 铝型材 | `https://grabcad.com/library/4040-aluminium-extrusion-1` |
| 铝型材 | `https://print.grabcad.com/library/high-precision-cad-models-of-openbuilds-v-slot-extrusions-2020-2040-4040-profile-1` |

那条参数化的值得注意：**HGR20 导轨，导轨长度 150–4000 mm 可配置**。

### ⚠ 授权（**官网明写，两处互相印证**）

**ToS `https://grabcad.com/terms/` 第 6.2 条：**

> each user of the Site a worldwide, non-exclusive, royalty-free, fully-paid, perpetual,
> irrevocable, **non-sublicensable, non-assignable, and non-transferable** license to use,
> reproduce, copy, modify, adapt, arrange, translate, and create derivative works of such
> User Submissions for such user's **own benefit and non-commercial, internal use**
> (the "Cross License").

**帮助中心 `https://help.grabcad.com/article/246-how-can-models-be-used-and-shared`：**

> "models downloaded from GrabCAD are **generally for private use**"
> 商业公开使用 → "You will need to ask the model's original designer for their **explicit permission**"
> "if for any reason you do not get any response from the model's creator, then you **cannot use it
> for commercial purposes**"
> 模型里若含公司名/logo/知识产权 → "we would **strongly urge you to consider not utilizing this
> model in a commercial sense**"

**→ 结论（明确，不含糊）：GrabCAD 的模型只授权「自己的、非商业的、内部使用」。
拿来做公司机械设计 = 不行。这不是"有点风险"，是授权文本上直接排除。**

---

## 必答问题 A：脚本自动插入，最适合哪个渠道？

### **MISUMI 米思米**

理由，按重要性：

1. **唯一实测确认提供原生 .SLDPRT**（SolidWorks ≥2015）→ `insert_component` 直接吃，
   不需要 STEP 中转，少一次格式转换和一次几何损耗
2. **流程本身就是「选型 → 规格 → 品番 → 取 CAD」**，品番是稳定主键
   （官网明写：*"a part number will appear"*）
3. **有 SolidWorks 官方插件**，且插件支持「**含型号保存**」→ 文件名带品番，本地路径可脚本推断
4. **URL 结构高度规整**：
   `https://us.misumi-ec.com/vona2/mech/<10位分类码>/...`
   铝型材 = `M1501010100`；HIWIN 导轨 = `.../maker/hiwin/mech/M0100000000/M0110000000/M0110050000/`
5. **一个账号覆盖三类**：HIWIN 导轨（maker=hiwin）、铝型材（mech M1501010100）、丝杠
6. **费用**：注册免费，不收费

### 落地形态：下载后本地缓存，脚本只认本地路径

不要在脚本里每次在线拉。原因（都是实测）：

- MISUMI 下载要登录
- `cn.misumi-ec.com` 产品页返回反爬挑战页
- `id.misumi-ec.com` 会 429

建议布局（借凯元的思路，凯元的 `datas\lib\` 是官网明写的固定路径）：

```
零件库\
  丝杠\     <品番>\ <品番>.SLDPRT
  导轨\     <品番>\ <品番>.SLDPRT
  铝型材\   <品番>\ <品番>.SLDPRT
```

一次人工/半自动补库，之后 `insert_component(file_path=...)` 纯本地，零网络依赖。

### 为什么不选其他四家

| 渠道 | 否决理由 |
|---|---|
| **3DContentCentral** | 本机根本连不上（走代理直连都试过）。且【推断】近年下载已转向 ContentCentral Client，需要 SOLIDWORKS Subscription / Supplier Partner 资格 —— 这条因站点不可达**无法核实** |
| **HIWIN** | 注册要填 Company/Department/Title/Phone 四项企业信息；Terms of Use 明文禁止 "transmitted / modified / publicly published"；**没有铝型材**；格式查不到 |
| **THK** | **没有 SLDPRT**（只有 STEP/IGES/SAT/ACIS/VDA-FS/DXF）；下载是「双击产品树→选规格→生成」的交互式流程，没有可枚举的批量目录，脚本没法定位 |
| **GrabCAD** | ToS 6.2 白纸黑字只授权"非商业内部使用"；且是 SPA，裸 HTTP 抓不到内容 |

---

## 必答问题 B：有没有结构化的「型号→尺寸」数据？

**有，但分散在三家，且都需要登录或抓 HTML：**

| 渠道 | 数据形态 | 登录要求 |
|---|---|---|
| **THK** | Product Information 页：「View **dimensional drawings, tables, and detailed product specifications** all in one place」+ Toggle Chart 切型号对比 | **All Users, no registration required**（官网明写）← **门槛最低** |
| **MISUMI** | 规格 → **品番** 的映射本身就是结构化数据；My Page 有「**Download a CSV file**」 | 需注册 |
| **HIWIN** | 「Life Calculation」寿命计算 + 「Product Selection」选型 + Download Center | 需注册 |
| 3DContentCentral | **查不到** | 查不到 |
| GrabCAD | 无结构化数据（UGC） | — |

### 你举的例子：HGR20 的行程 / 负载 / 精度等级

**【查不到】** 本轮没在任一官网抓到结构化的 HGR20 参数表。确认存在的候选链接：

| URL | 本机实测 |
|---|---|
| `https://www.hiwinsupport.com/download/tech_doc/gw/Linear-Guideway-(C).pdf` | 站根 200，**该 PDF 404** |
| `https://www.hiwin.com.cn/product/Linear_Guideway/RHGH_RHGR_series.aspx` | **404**（我猜的路径） |
| `https://www.hiwin.it/images/download/documenti/ENG/catalogo guide.pdf` | 未实测（意大利站规格书） |
| `https://hiwin.com.vn/UserUpload/Document/aa9a4687-….pdf`（滚珠导轨寿命公式） | 未实测 |

**下一步建议**：HIWIN 的 HGR20 参数要从 hiwin.com.cn 登录后的 Download Center 拿，
或者从各国子站的 catalog PDF 抽表。THK 那条路（免登录 Product Information）最省事，
但拿不到 HIWIN 型号。

---

## 附：本轮明确「查不到」的清单（不补常识）

1. 3DContentCentral 免费层的每日下载数 / 分辨率 / 格式
2. 3DContentCentral 是否有丝杆/导轨/铝型材，以及零件页 URL
3. HIWIN CAD 下载提供的文件格式
4. GrabCAD 免费账号的具体下载额度
5. GrabCAD 是否允许匿名逐个下载（只测到首页按钮 301 到注册页）
6. 凯元 6 个模型库的内容清单（付费墙后）
7. 麦迪 / 今日制造是否提供可下载 3D
8. HGR20 的结构化行程/负载/精度等级参数表
9. GrabCAD 社区上传模型的授权链（ToS 只给了下载方权利，上传方权利需看上传协议，本轮未取）

## 附：建议的下一步（按性价比排序）

1. **用真实浏览器（browser4-cli）打开 `help.solidworks.com/2024/english/ccsupplier/c_free_sub_level.html`**
   —— 这是唯一能解 3DContentCentral 免费层问题的路径，裸 HTTP 拿不到
2. **给 HGR20 参数换个出口 IP 回放 Wayback** —— 本机 IP 被 429 了
3. 如果 3DContentCentral 在别的网络能通，优先测 `beta.3dcontentcentral.cn`（可能是不同 CDN）

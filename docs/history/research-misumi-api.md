# 米思米（MISUMI）中国站 API 登录方式与官方开放接口 — 调研报告

调研日期：2026-09-29 · 方法：agent-reach（Exa 429 不可用 → 改用内置 web_search / web_fetch / `gh` / Wayback CDX + 本机直连 misumi.com.cn 静态核验）

标注约定：
- **【官方明写】** = 米思米自有域名页面/接口原文
- **【社区经验】** = 第三方仓库/文档实测记录
- **【推断】** = 我基于证据的推理，未被任何一方明写

---

## 0. 一句话结论

**米思米没有任何对外发布的开放 API 文档，也没有开发者门户或申请入口。**
`/api/v1/*` 是其电商前端自用的**内部 API**（非公开、无契约）。
**唯一正规的「把米思米接进 PLM/采购系统」路径是 eProcurement / PunchOut（cXML）**，
它是一等公民功能，前端代码里有完整实现；申请走「联系米思米销售/客服开通企业账号 + 申请 eProcurement」，
**逆向登录是错的方向**。

同时有一个被忽视的好消息：**「查型号/查价格」这条路的 API 完全免登录可用**（见 §4）。

---

## 1. 官方开放 API / 开发者文档：不存在

### 1.1 证据链（逐条可复核）

| 检查 | 结果 | URL / 命令 |
|---|---|---|
| 中国站「使用指南」全量目录 | **0 条**与 API / 系统对接 / PunchOut 相关的条目 | https://www.misumi.com.cn/cmsweb/view/guide/ |
| 中国站候选文档路径探测 | 全部 404 | `/api/docs` `/developer` `/developers` `/api/v1/docs` `/apidoc` `/openapi.json` `/swagger-ui.html` `/api/swagger` `/v3/api-docs` `/api/v1/openapi`（均 `https://www.misumi.com.cn`） |
| API 主机根路径 | **HTTP 401**（有网关拦截，无欢迎页/无文档） | `https://api.cn.misumi.com.cn/` |
| API 主机上 `/swagger-ui.html` `/v3/api-docs` `/openapi.json` `/actuator` | 均 **401**（路径被网关认得但需鉴权，**内容不可确认，我未尝试任何绕过**） | 同上 |
| Wayback CDX：`api.cn.misumi.com.cn*` 全量 URL | 只有站点自身的 XHR 调用，**从未有过任何文档页** | `http://web.archive.org/cdx/search/cdx?url=api.cn.misumi.com.cn*&fl=original,timestamp,statuscode&collapse=urlkey` |
| Wayback 2018 年首次抓取 | 根路径就是 401 | CDX 结果首行 `http://api.cn.misumi.com.cn/ 20181202102137 401` |
| GitHub 全站代码搜索 `api.cn.misumi.com.cn` | 0 命中 | `gh search code "api.cn.misumi.com.cn"` |
| 站内全文检索 API 文档 | 查不到 | web_search「MISUMI open API developer documentation catalog」/「misumi 开放平台 申请 applicationId」 |

### 1.2 applicationId 的性质（重要）

- **【官方明写】** 中国站运行时配置内嵌：
  `applicationId:"77f56fb2-4165-4116-b82f-e495838bb6e1"`, `lang:"CHN"`
- **【社区经验】** 日本站同一机制内嵌 `applicationId=de30e2b2-db86-435d-9929-646c11a3c4cd`，
  社区文档明写这是 *「EC フロント用に埋め込まれた公開アプリ識別子（ユーザー固有のキーではない）」*
  ——**公开的应用标识符，不是用户密钥**。
  来源：https://github.com/Mega-Gorilla/misumi-bom-manager/blob/main/docs/misumi-api/01-overview.md

⇒ **推断**：中国站的 `77f56fb2-…` 同理，是前端公开标识，**没有申请流程，也没有申请入口**。
它不是密钥，不构成「官方 API 凭证」。

### 1.3 PunchOut/cXML 怎么申请

**【官方明写】** 米思米美国站的 eProcurement 页面给出了完整形态与唯一入口：

- https://us.misumi-ec.com/service/eprocurement/ （本次抓取原文）
  - PunchOut catalog：把企业采购系统直连 MISUMI 在线目录，工程师可 source / configure / 加购，
    结账转成 (buyer-side) requisition 走审批。
  - EDI：850/855/856/810/840/843/860/865 全套。
  - 协议：`HTTPS / AS2 / FTP / SFTP / SOAP / REST`
  - 电子目录格式：`cXML / XML / OCI`
  - 平台：PeopleSoft、Coupa、**SAP**、Oracle、Infor、IBM、**ARIBA**、SciQuest、JD Edwards
  - **申请方式只有一个：`mailto:eProcure@misumiusa.com`「CLICK HERE TO EMAIL FOR ADDITIONAL INFO」**
  - 三阶段流程：Discovery → Implementation → Adoption
- 同样页面在捷克站存在：https://cz.misumi-ec.com/en/services/eprocurement/

**【官方明写 · 中国站】** 面向中国大陆的 eProcurement 商务入口：

- PunchOut checkin 页面在中国站**在线且可访问**：
  `https://www.misumi.com.cn/order/punchout/checkin` → HTTP 200，`<title>PUNCHOUT CHECK IN</title>`
- 中国站 SolidWorks 插件页底部给出商务窗口：
  https://www.misumi.com.cn/pr/fa/b9c60p3c/aa/?bid=bid_eng_rightmenu
  - 「网页在线咨询」「邮件咨询」；**受理时间 9:00~18:00（周一~周五）**

⇒ **【推断】中国站 eProcurement 的申请路径**：与美国站同一模式 ——
先注册**企业账号**（中国站有「个人用户如何升级为企业用户」，
https://www.misumi.com.cn/cmsweb/view/guide/ ），再由企业客户经理/客服开通 `eprocurementCustomerFlag`。
**具体申请表单 URL：查不到**（中国站没有公开的 eProcurement 申请页，
首页 footer 也没有任何 corporate/contact/about 链接 — 我正则扫过，0 命中）。
实操上应走「企业账号 + 在线咨询/邮件咨询」这条商务通道。

**资质要求**：**查不到**官方明文的资质门槛。
从美国站页面推断（Discovery 阶段「需要 leadership、supply chain/purchasing、IT 三方关键人员参与」）
至少需要**企业身份 + 采购/IT 决策人**，但**米思米从未明写**具体门槛，此处不臆测。

---

## 2. 登录流程（本轮最实质的发现）

从中国站 59 个 Nuxt chunk 全量反查 + 路由中间件源码，得到完整机制。

### 2.1 `/api/v1/auth/check` 是什么 —— 不是验证码，是会话探活

**【官方明写 · 源码】** 两处定义，用途不同：

```js
// 路由中间件用的会话探活（无参数）
async authCheck(){ return await this.get(`${this.baseURL}/api/v1/auth/check`,{}) }
//   baseURL = https://api.cn.misumi.com.cn

// 注册页用的「用户名是否被占用」检查（带参数）
async checkLoginId(t){ return await this.get(`${jp_newton}/api/v1/auth/check`,t) }
//   jp_newton = https://chn-nt-api.misumi.com.cn
```

**【本机实测 · 证据】** 不带 sessionId 请求：
```
GET https://api.cn.misumi.com.cn/api/v1/auth/check?lang=CHN&applicationId=77f56fb2-...
→ HTTP 200
{ "status": 400, "errorList":[{ "errorCode":"API000100",
  "errorMessage":"sessionId为必须输入项", "errorParameterList":["sessionId"] }] }
```
⇒ **它要求传 sessionId 进去、返回该 session 是否有效。不是 challenge、不是验证码、不是发码接口。**

中间件消费逻辑（原文）：
```js
const n = await g.cnAuth.authCheck();
if (n?.sessionStatus === "1") throw new Error("sessionStatus 过期");
u.setAuthCheck(n);
// 随后 POST /api/ecfront/v1/ec/userInfo  body:{sessionId, refreshTokenHash}
```
⇒ `sessionStatus === "1"` 表示**已过期**。

### 2.2 token 机制：是自家 sessionId + refreshTokenHash，**不是 OAuth**

**【官方明写 · 源码】** 完整 token 生命周期：

| 项 | 值 |
|---|---|
| 访问令牌 | cookie `GACCESSTOKENKEY`，内容就是 `sessionId` |
| 刷新令牌 | cookie `GREFRESHTOKENHASH` |
| 过期时刻 | cookie `expirationTime`（epoch 秒） |
| Cookie 属性 | `domain=.misumi.com.cn; path=/; secure=true; sameSite=none; max-age=365天` |
| 用法 | `Authorization: Bearer ${sessionId}`（`getHeaders()` 里拼） |
| 自动续期 | `expirationTime - now <= 300s` 时自动调 `tokenRefresh({refreshTokenHash})` |
| 刷新端点 | **`POST /api/user/v1/auth/refresh`**（body `{refreshTokenHash}`），返回 `{sessionId, refreshTokenHash, expirationTime}` |
| 真实登录页 | **`/mydesk2/s/login/`**（带 `?back_url=…&session_invalid=1`），中间件显式放行 |

⚠️ **对父会话既有结论的两处更正**（本轮实证，非重复验证）：

1. `/api/user/v1/auth/refresh` 挂在 **`ecold` 主机 = `https://www.misumi.com.cn`**，
   **不是** `api.cn.misumi.com.cn`。
   运行时配置原文：
   `ecold:{host:"www.misumi.com.cn"}`，
   `tokenRefresh(){ return this.post(`${this.ecOldUrl}/api/user/v1/auth/refresh`, t, {}) }`
   ⇒ 父会话试 `/api/user/v1/auth/login` 得 404 是因为**主机就不对**（该主机上只有 `/refresh`）。
2. 登录端点**确实在** `api.cn.misumi.com.cn`（`newtonLogin:{host:"api.cn.misumi.com.cn"}`），
   路径 `/api/v1/auth/login`，但 **`applicationId` 与 `lang` 走 query string，body 另带**：
   ```js
   async login(t){
     const r = `${this.loginBaseURL}/api/v1/auth/login`;
     const n = this.getApplicationIdAndLang();   // `applicationId=…&lang=CHN`
     return await this.loginPost(`${r}?${n}`, t)
   }
   ```
   父会话报 `API001100 登录用户名或密码错误` 说明**路由是通的**，服务端确实在校验凭据。

### 2.3 中国站登录要不要图形验证码 / 短信？

**【官方明写 · 全量 chunk 扫描结果】** 登录链路上 **没有** 图形验证码：

- 59 个 chunk 全量关键词计数：`captcha` 命中 **1 处**，`Captcha`/`CAPTCHA`/`slideCode`/`verifyCode`/`authCode` 均 **0**
- 唯一那 1 处是**产品目录申请表**的验证码，与登录无关：
  ```
  getValidateCode(){ return this.get(`${baseURL}/Customer/CatalogApply/base/captcha`, r, {"x-api-key": …}) }
  ```
- 另有风控对接 `POST ${baseURL}/Customer/Mb/yidun/risk/check`（**网易易盾** Yidun），
  同样属于**目录申请**流程，不是登录流程
- 短信 `GET /Customer/CatalogApply/base/getSms` 与 `POST /api/ecfront/v1/sms/send` 也都在申请/注册链路上

⇒ **【推断】密码登录路径本身没有图形验证码或短信前置**。
父会话的 `API001100` 是**纯凭据错误**，不是验证码拦截。
**注意**：风控（易盾）可能在**服务端**按 IP/频率触发，但那是响应式拦截，不是请求体里的必填字段 ——
我没有、也不会去试探如何触发或规避它。

### 2.4 登录相关的权限开关（**【官方明写 · 源码】**）

- 登出：`POST /api/ecfront/v1/ec/session/logout`
- 切换子账号：`ArmsAPi.swichUserList({})`（「当前账号未开通对账权限」提示）
- 客户资料/改密/删号：`chn-nt-api.misumi.com.cn` 上
  `/customer/v1/customerinfo/get|change`、`/customer/v1/chn/password/change`、`/customer/v1/chn/user/delete`

---

## 3. 第三方现成的米思米客户端 / 爬虫

⚠️ 以下**机制**层面记录。**不提供、不讨论任何绕过验证码或破解登录的方法。**

| 项目 | 目标站点 | 性质 | 结论 |
|---|---|---|---|
| [Mega-Gorilla/misumi-bom-manager](https://github.com/Mega-Gorilla/misumi-bom-manager) | **jp.misumi-ec.com（日站）** | Tauri2+React 桌面 BOM 工具，**自带 9 篇逆向 API 规格文档** `docs/misumi-api/01..09` | **最有价值的一份社区规格**。自述官方 API = **No**，是「EC フロントエンドが使う内部 API（非公開・無契約）」。自述解法是**内嵌隐藏 WebView 走 Akamai**（日站有 Akamai Bot Manager，裸 HTTP 403）。流程 `suggest → sales-price-delivery/check` |
| [MinfonTsai/misumi_catalog](https://github.com/MinfonTsai/misumi_catalog) | 未标注 | 0★，Python 抓 e-Catalog 存 SQL-DB，HTML 结构化 | 早期 HTML 抓取思路，**已过时**（中国站现为 Nuxt SSR） |
| [CarlosRoig/misumi_api](https://github.com/CarlosRoig/misumi_api) | — | **空仓库**（Git Repository is empty, HTTP 409） | 名不副实 |
| [Apify `piotrv1001/misumi-listings-scraper`](https://apify.com/piotrv1001/misumi-listings-scraper) | **us.misumi-ec.com（美站）** | 72 runs / 2 users，抓 listing + 单价 + 库存 + 承诺发货日 | 商业化的第三方抓取服务，**非官方**；面向美站非中国站 |

**没有找到的（明写）**：
- ❌ 中国站（`api.cn.misumi.com.cn` / `chn-nt-api` / `rd-cn-cadapi`）的**任何**现成开源客户端或库。
  `gh search code "api.cn.misumi.com.cn"` → 0 命中；
  `gh search code "rd-cn-cadapi OR chn-nt-api.misumi.com.cn"` → 0 命中。
- ❌ 任何「免验证码直下 CAD」的现成工具 —— **查不到**，且我未去找。
- ❌ 唯一那份逆向规格的作者本人给出的结论是：
  > 「商業的・大規模連携は MISUMI の eProcurement / API 連携（法人契約）を検討する」
  > （商业化/大规模对接请考虑 MISUMI 的 eProcurement / API 联动（法人合同））

### 3.1 ⚠️ 中国站 vs 日站的防护差异（对父会话重要）

- **【社区经验】** 日站：Akamai Bot Manager 全量拦截，裸 HTTP 客户端 403
- **【父会话已实测】** 中国站：Nuxt SSR，**无 WAF，可直连**
- ⇒ **【推断】** 同一家公司、同一套内部 API，**中国站的自动化门槛显著低于日站**。
  这不是「漏洞」，是防护投入差异；**也意味着中国站上的一切内部 API 都应按「非公开、不保证随时变更」对待**。

---

## 4. CAD 下载到底需不需要登录 —— 「查型号」完全走得通

### 4.1 【官方明写】中国站使用指南的原始表述

- **如何下载商品CAD数据**：https://www.misumi.com.cn/cmsweb/view/guide/5029/
  > 01 在商品详情页中**选定型号后**，点击【CAD下载】按钮，弹出【数据生成】确认框；
  > ① 选择需要输出的【文件格式】【版本】等多项信息，点击【数据生成】按钮即可下载CAD数据。
  > 亦可点击【2d_SFJT.zip】或【2d_VFJT.zip】下载固定图纸尺寸的CAD数据。
  > 02 如点击【CAD下载】按钮时，**未选定型号**，则弹出框内会提示"因为型号未确定，所以不能进行CAD数据下载"。

  ⚠️ 值得注意：官方指南**通篇没有一句说 CAD 下载需要登录**，只强调「必须先选定型号」。

- **CAD文件格式介绍**：https://www.misumi.com.cn/cmsweb/view/guide/5030/
- **产品目录与设计插件申请**：https://www.misumi.com.cn/cmsweb/view/guide/5034/ · https://www.misumi.com.cn/cmsweb/view/guide/5035/

### 4.2 【本机实测】免登录可用的检索面

| 端点 | 参数 | 实测结果 |
|---|---|---|
| `/api/v1/fullText/search` | `keyword=轴承&pageSize=3&page=1&field=@default` | **HTTP 200**，`totalCount:1287`，返回 title/text/url |
| `/api/v1/partNumber/suggest` | `keyword=SUS304&count=5&field=@default,partNumberList.innerCode` | **HTTP 200**，返回 `partNumberList[]`：`partNumber`,`brandCode`,`brandName`,`innerCode`,`completeType`,`partNumberType`,`unitCodeList` |
| `/api/v1/category/search` | `categoryLevel=1` | **HTTP 200**，`totalCount:13`（13 大类，与父会话实测一致） |
| `/api/v1/brand/search` | — | 父会话已实测（1267 品牌） |
| `/api/v1/fullText/searchInCADComponents` | `keyword=轴承` | **HTTP 200 但 `totalCount:0`**（CAD 组件全文索引对中文词无命中，**换英文/型号可能有效**） |

⇒ **【推断】父会话的第 4 问答案：是的，「查型号」这条路完全走得通，而且不止拿型号。**
`partNumber/suggest` 直接给出**规范化后的型号 + 品牌 + 内部主键 innerCode + 完整度 completeType**。
`fullText/search` 给出全站条目与 URL。
**缺的是「规格明细」和「文件」**：

- **规格明细**：源码里有 `/api/v1/partNumber/search`（GET）与
  `/api/v1/partNumberPreview/search`（POST）—— 这两个**未实测免登录**，是下一轮该打的目标。
- **文件**：源码里的 CAD 相关端点为
  `/api/v1/cad/download`、`/api/v1/cad/preview`、`/api/v1/cad/termsOfUse`、
  `/api/personalize/v1/cadHistory/search`、`/api/v1/cadLog/add`，
  另在 `mex.misumi.com.cn`（sinus）上有 `/sinus/api/v1/cad/download`、`/sinus/api/v1/cad/preview`。
  **这些【推断】需要登录态**（走 `getHeaders()` 带 `Authorization: Bearer`），**我没有实测**。

### 4.3 CAD 生成服务的官方主机（源码给出，**比逆向登录更值得用**）

**【官方明写 · 运行时配置原文】**
```
cpro:{ protocol:"https",
       domain:"rd-cn-cadapi.misumi.com.cn",
       previewWeb:{ url:"https://rd-cn-preview.misumi.com.cn/Web3DViewer/Web3DViewer.html",
                    helpUrl:"3d_preview_chn_zh.html" } }
```
配套主机：`rd-cn-caddata.misumi.com.cn`（CAD 数据下发）、`rd-cn-preview.misumi.com.cn`（3D 预览）。

**【社区经验】** 独立印证 + 补充实测细节
（https://github.com/jiaqiwang969/OntologyEngineering/blob/main/skills/cad-agent/references/misumi-cn-guide.md）：
- 页面 DOM 定位线索：`.cad-dl-button`（CAD 下载按钮）、`#cad_format`（格式下拉，
  实测值如 `STEP_AP203`，部分模具件只有 `STEP` 值 `1`）、`.new_cadDl a.m-btn--dataGenerate`（数据生成）、
  `#cad_download_link`（生成后链接）
- 生成后的下载链接在 **`rd-cn-caddata.misumi.com.cn`**，**普通 HTTPS GET 即可取回，与浏览器所得 ZIP 哈希一致**
- 一个完整实例：型号 `UL3-15` → STEP(AP203) → 17,090 字节 ZIP / 67,064 字节 STEP → 导入 NX，
  15×3×3 mm 精确包络
- ⚠️ 该文档自己反复强调：这是**页面观察，不是稳定 API**；每次先核当前 DOM 与完整型号

⇒ **【推断】** CAD 生成是**异步**的：POST 生成 → 等 → 得一次性下载链接。
「免登录直下 CAD」在机制上等同于「复用一次已授权会话产生的下载链接」，
**我不提供任何自动化获取/复用会话的步骤**。

---

## 5. SolidWorks 插件：官方入口与账号要求

### 5.1 【官方明写】中国站插件页

https://www.misumi.com.cn/pr/fa/b9c60p3c/aa/?bid=bid_eng_rightmenu
（页标题：`3D自动化设计组件RAPIDdesign、Solidworks插件、CAD插件相关信息…`）

- 导航：抢先体验 / **申请入口** / 使用方法（入门介绍·功能详解·常见问题Q&A·在线咨询·成功案例）/ 版本更新 / 积分任务 / 插件咨询
- **需要账号**：流程是「满足以上安装环境 → 同意个人联络信息的收集规则 → 确认提交」，
  且提交时用**登录邮箱**（同页文案：「您已申请过！我们已将安装包再次发送至您的邮箱，请查收！」）
  ⇒ **必须先有米思米账号**，且**安装包通过邮件下发**，不是公开直链下载
- **官方明写的安装环境（这版页面的口径，偏旧）**：
  - SOLIDWORKS 版本 **2014 ~ 2019**
  - Windows **7 或 10**，**64 位**
  - **可连接外网**
- **使用限制（原文要点）**：Rapid Design 利用目的**仅限于自身业务相关的生产、产品设计**；
  不得将设计方案/数据提供给第三方，不得对含米思米产品的数据、型号进行删减、变更、替换；
  违反者米思米有权停止相关服务
- 商务窗口：网页在线咨询 / 邮件咨询，受理 9:00~18:00（周一~周五）

中国站使用指南对应条目：
- **如何申请设计插件**：https://www.misumi.com.cn/cmsweb/view/guide/5035/
  > ※申请成功后，系统会自动向您登录的邮箱地址发送 Rapid Design 的安装包下载链接。
  （同样要求先勾选【满足】【同意】再提交）
- **如何申请产品目录**：https://www.misumi.com.cn/cmsweb/view/guide/5034/

### 5.2 【官方明写】日本站 RAPiD Design (SOLIDWORKS 版) 支持页 —— 插件能力的权威清单

https://jp.misumi-ec.com/service/rd/sw/help/

- 版本线：v2.x（2019 起）→ v4.0.0（2022-01）→ v4.1.0（SOLIDWORKS2022）→ v4.4.0（2023-12）→
  v4.7.0（SOLIDWORKS2025, 2025-05）→ **v4.8.0（SOLIDWORKS2026, 2026-04-14）**
- Windows 10 已于 2025-10 结束支持
- 功能面：机械标准部件库（检索/导入/设计/型号保存/CAD 各页 FAQ）、设计事例集、
  **部品组合模板**、**3D-CAD 数据まとめてダウンロード（批量下载）**、一括見積（批量报价）、
  お気に入り/保存型番履歴
- 另有两个版本页：iCAD 版 `/service/rd/icad/help/`、Inventor 版 `/service/inventor/help/`
- 利用规约：https://jp.misumi-ec.com/contents/terms/rd.html

⇒ **【推断】** 这就是 SolidWorks 里的**正规**米思米通道：
**插件在 CAD 内直接检索型号 → 插入含米思米零件的装配 → 顺带出报价。**
插件这条路**不需要**逆向登录，**也不该**逆向。

---

## 6. PunchOut：技术画像完整（这是父会话「特别关注」的正路）

全部为**【官方明写 · 中国站前端源码】**，非猜测。

### 6.1 运行时配置

```js
punchout:{
  host:"https://chn-nt-api.misumi.com.cn",
  api_base_path:"customer",
  api_version:"v1",
  api_key:"<REDACTED-2026-11-02>",  // 2026-11-02 脱敏：原为第三方接口的真实凭据，已移除；需使用请自行申请
  checkin:{ checkin_url_host:"https://www.misumi.com.cn",
            checkin_url_path:"/order/punchout/checkin" },
  mauth:{  mauth_host:"https://int-mauth.misumi.com.cn" },
  satellite:{ misumiEc:"https://jp.sso.misumi-ec.com" }
}
```

> ⚠️ 更正父会话的一处猜测：父会话说「一个 **staging** 的 api_key 明文」。
> 实际上 `punchout.api_key` 与 `apikey.newton_nstg` 是**两个不同的值**：
> - `punchout.api_key = <REDACTED-2026-11-02>`（PunchOut 专用，线上值；2026-11-02 脱敏）
> - `apikey.newton_nstg = <REDACTED-2026-11-02>`（2026-11-02 脱敏；原值与本条同源，已移除）
>   （与 `newton_local` **同值** ——「nstg」是历史遗留命名，并非独立 staging 环境）
> 真正带 `int-` 前缀的是 `int-mauth.misumi.com.cn`，那是 M-Auth 服务，与 api_key 无关。

### 6.2 PunchOut 端点全集（`chn-nt-api.misumi.com.cn`）

| 路径 | 用途 |
|---|---|
| `POST /api/ordfront/v1/punchout/ssoAuth` | SSO 认证 |
| `POST /api/ordfront/v1/punchout/employee` | 员工身份（api-tag `punchout-ec-auth-api-employee`） |
| `POST /api/ordfront/v1/punchout/userCodeCheckIn` | 用户代码签入（api-tag `punchout-ec-auth-api-userCodeCheckIn`） |
| `POST /api/ordfront/v1/punchout/autoAssignment` | 自动分配（api-tag `punchout-ec-auth-api-autoAssignment`） |
| `POST /api/ordfront/v1/punchout/checkout` | **Punchback（回跳）** |
| `GET /customer/v1/eprocurement-buyer-control-non-login/get` | 采购方管控项（免登录） |
| `POST /customer/v1/eprocurement-user-register/non-dedicated-login/complete` | 免专用账号登录的用户注册完成 |
| `POST /api/ecfront/v1/ec/userInfo` | 用户信息 |

M-Auth（`int-mauth.misumi.com.cn`，form-urlencoded，带 `clientId` 常量）：
- `/api-auth-v2/auth/api/purchase/autoAssignment`
- `/api-auth-v2/auth/api/purchase/employee`
- `/api-auth-v2/auth/api/purchase/userCodeCheckIn`
- `/api-auth-v2/auth/api/sso/satellite/misumi-ec`（SSO satellite）

### 6.3 触发方式与数据模型（**【官方明写】**）

- **cXML checkin 入口（本机实测在线）**：
  `POST https://www.misumi.com.cn/order/punchout/checkin` —— 页面 HTTP 200，`<title>PUNCHOUT CHECK IN</title>`。
  这是**买方采购系统把工程师弹到米思米的落点**。
- **PunchOut 模式识别**：请求头 `x-client-program: CN_PUNCHOUT`
  （`getHeaders()` 默认发 `CN_EC`；`isPunchoutCheck()` 在命中
  `price-delivery-calculation/v1/sales-price-delivery/check` 且
  `user_store.customerInfo.eprocurementCustomerFlag === "1"` 时切到 `CN_PUNCHOUT`）
- **采购方身份字段**（buyer control 结构）：
  `subsidiaryCode`、`eprocurementSystemName`、`eprocurementBuyerCompanyCode`、
  `eprocurementBuyerOfficeCode`、`eprocurementBuyerEmployeeCode`、`controlCodeList[]`
- **前端同时代理（PunchOut 专用）**：`proxyGet` / `proxyPost` 经 `window.location.origin`，
  即由 `www.misumi.com.cn` 代理转发 PunchOut API
- **B2B 大单逻辑**：`checkoutUnfitType==="2"`（不可结账类型=大宗）时按
  `P00011_big_order_return_days_misumi_product` / `P00013_big_order_return_days_vona_product`
  计算 `vsd`（Vendor Ship Date），默认 20 天
- 店铺分类用 cXML `Operation` 语义码：`T0/A0/0A/A1/B0/C0/Z0/L0/V0`
- 商务消息通道：`info-meviy.misumi.com.cn`（MEVIY 报价，`/api/ecfront/v1/meviy/meviyImage`）
- Pinia 专有 store 字段：`eprocurementUser`、`eprocurementBuyerInfo`、
  `msmEprocurementBuyerInfo`、`eprocurementBuyerControlObj`

### 6.4 申请流程结论

1. **【官方明写 · 美站】** 唯一公开申请入口是邮件 `eProcure@misumiusa.com`，
   流程 Discovery → Implementation → Adoption。https://us.misumi-ec.com/service/eprocurement/
2. **【推断】中国站对应做法** = 注册企业账号 → 由客户经理/在线客服开通 eProcurement。
   **中国站的公开申请表单 URL：查不到。**
3. 涉及的第三方平台（Ariba / Coupa / SAP / Oracle…）已在美站页面明写；
   源码里的 `int-mauth` 进一步印证 **M-Auth 是 SAP Ariba 系的认证服务**（**【推断】**）。

---

## 7. 汇总：可直接执行 / 明确查不到

| # | 事项 | 结论 | 依据 |
|---|---|---|---|
| 1 | 官方开放 API 文档 / 开发者门户 | **不存在** | 中国站指南 0 条 + 10 条候选路径全 404 + Wayback 从无文档页 + `api.cn` 根路径 401 |
| 2 | applicationId 是密钥吗 | **不是**，前端公开应用标识 | CN `77f56fb2-…` / JP `de30e2b2-…`，社区文档明写「非用户密钥」 |
| 3 | `/api/v1/auth/check` | **会话探活**，要 sessionId，不是验证码 | 实测 `API000100 sessionId为必须输入项`；中间件 `sessionStatus==="1"` 判过期 |
| 4 | 登录要验证码/短信吗 | **登录链路无**；`captcha` 全站仅 1 处且属目录申请 | 59 chunk 全量扫描 |
| 5 | token 机制 | **非 OAuth**：`sessionId`(Bearer) + `refreshTokenHash` + cookie | `auth.BGq3Oowi.js` 路由中间件原文 |
| 6 | `/api/user/v1/auth/refresh` 在哪 | **`www.misumi.com.cn`**（`ecold`），不是 `api.cn` | 运行时配置 `ecold:{host:"www.misumi.com.cn"}` |
| 7 | 真实登录页 | `/mydesk2/s/login/` | 中间件常量 `Q="/mydesk2/s/login"` |
| 8 | 免登录能查型号吗 | **能**，且能给品牌/innerCode/完整度 | 实测 `partNumber/suggest` + `fullText/search` 均 200 |
| 9 | 免登录能拿规格吗 | **未实测**，`partNumber/search` 是下一个该打的目标 | 源码有该端点 |
| 10 | 免登录能下 CAD 吗 | **【推断】不能**（走 Bearer） | 源码 `getHeaders()`；**未实测，不给绕过方案** |
| 11 | 官方 CAD 服务主机 | `rd-cn-cadapi.misumi.com.cn` / `rd-cn-caddata` / `rd-cn-preview` | 运行时配置 `cpro` |
| 12 | SolidWorks 插件 | **官方有**，需米思米账号，**邮件下发安装包** | `guide/5035` + `/pr/fa/b9c60p3c/aa/` |
| 13 | 插件能力 | RAPiD Design：部件库+设计事例+组合模板+**批量 CAD 下载**+批量报价 | `jp.misumi-ec.com/service/rd/sw/help/` |
| 14 | 中国站最新插件版本口径 | 查不到（页面仍写 SW2014~2019/win7~10，明显未更新） | `/pr/fa/b9c60p3c/aa/` |
| 15 | PunchOut 正路 | **有且是一等公民**，`/order/punchout/checkin` 线上可用 | 本机实测 200 |
| 16 | PunchOut 申请入口（中国站） | **只有商务通道**（企业账号+在线咨询/邮件），无公开表单 | 首页 footer 0 corporate 链接 |
| 17 | PunchOut 资质门槛 | **查不到**官方明文 | — |
| 18 | 中国站第三方开源客户端 | **查不到**（GitHub 代码搜索 0 命中） | — |
| 19 | 日站第三方逆向规格 | **有**，`Mega-Gorilla/misumi-bom-manager/docs/misumi-api/01-09` | GitHub |
| 20 | 日站 vs 中国站防护 | 日站 Akamai 403 / **中国站无 WAF 可直连** | 社区文档 + 父会话实测 |

---

## 8. 建议给父会话的下一步（按性价比排序）

1. **别再逆向登录了。** 登录链路已摸清但无验证码不代表该用；内部 API 无契约、随时可变、
   且中国站无 WAF 是**防护缺失而非许可**。
2. **立刻转做免登录检索面**（父会话第 4 问已确认走得通）：
   补测 `/api/v1/partNumber/search`（规格）与 `/api/v1/partNumberPreview/search`，
   看能否免登录拿到完整规格 —— 这是「SolidWorks 插件里查型号」能立刻落地的最小闭环。
3. **业务侧并行走官方路**：注册企业账号 → 走 `guide/5035` 拿 SolidWorks 插件 →
   同时向米思米问 eProcurement/PunchOut（美站口径 `eProcure@misumiusa.com`，
   中国站走 `/pr/fa/b9c60p3c/aa/` 的在线咨询/邮件）。
4. **合规红线**：`rd-cn-caddata` 的下载链接是一次性会话产物，**不要**做自动化复用。

---

## 附：本次抓取的原始来源

**官方**
- https://www.misumi.com.cn/
- https://www.misumi.com.cn/cmsweb/view/guide/ · /5029/ · /5030/ · /5034/ · /5035/
- https://www.misumi.com.cn/pr/fa/b9c60p3c/aa/?bid=bid_eng_rightmenu
- https://www.misumi.com.cn/order/punchout/checkin
- https://api.cn.misumi.com.cn/api/v1/{auth/check,fullText/search,partNumber/suggest,category/search}
- https://us.misumi-ec.com/service/eprocurement/
- https://cz.misumi-ec.com/en/services/eprocurement/
- https://jp.misumi-ec.com/service/rd/sw/help/

**社区**
- https://github.com/Mega-Gorilla/misumi-bom-manager （+ `docs/misumi-api/01-overview.md` 等 9 篇）
- https://github.com/jiaqiwang969/OntologyEngineering （`skills/cad-agent/references/misumi-cn-guide.md`）
- https://github.com/MinfonTsai/misumi_catalog
- https://github.com/CarlosRoig/misumi_api （空仓库）
- https://apify.com/piotrv1001/misumi-listings-scraper

**归档**
- `http://web.archive.org/cdx/search/cdx?url=api.cn.misumi.com.cn*&fl=original,timestamp,statuscode&collapse=urlkey`

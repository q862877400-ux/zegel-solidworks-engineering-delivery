# blussyya/sldprt-format-research

<!-- survey: class=F; repr=mesh; orchestration=none; verify=numeric; deliver=none; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `blussyya/sldprt-format-research` · https://github.com/blussyya/sldprt-format-research |
| 许可 | **CC-BY-SA-4.0（传染）**（`LICENSE` 20566 B；README 明写「release anything you build from the docs themselves under the same license」）⇒ ★**只读思想，不抄文本**。代码已迁到 `blussyya/solidworks-converters`（Apache-2.0），**要抄代码去那份** |
| 元数据 | stars 20 · created 2026-06-02T17:08:22Z · pushed 2026-10-31T23:48:30Z · 语言 JavaScript · 5021 KB（来源：`gh api repos/blussyya/sldprt-format-research`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\blussyya__sldprt-format-research`（`--depth 1`，HEAD `c766550` 2026-11-01 02:48:28 +0300，0.8 MB） |
| 证据等级 | **实测**（它的格式结论我通过姊妹仓 `solidworks-converters` 在本仓 8 个零件上验过；文档本身是**一手**，但**本文档仓自身无代码可跑**） |（来源：本卡 §8 证据清单）

## 1. 一句话定位

**SolidWorks `.SLDPRT` 格式的第一份「有 oracle 的公开逆向文档」**：不是「我们猜文件长这样」，而是「73 个零件的语料 + SolidWorks 自己导出的 STEP/STL/X_T/X_B 当裁判 + 每个数字都能追到实验编号」。它把 `.SLDPRT` 拆成**两套并存的几何**（显示网格 + Parasolid 精确体），并用 **face/edge ID 把两者钉在一起**。

★ 对我方的判断价值：**它回答的是「文件里到底有什么」，而不是「怎么用」。** 我方若要做任何「不装 SW 读文件」的事，这是唯一一份把「能读到什么、读到什么精度、哪里读不到」写全的材料。

## 2. 技术路径（文档结构 = 它认为的解析路径）

```
.SLDPRT
├── 容器  format/1-container.md
│   ├── 现代（2015+）：类 ZIP 流头 + 名字 nibble 交换 + raw DEFLATE + CRC-32
│   ├── 2011：OLE2 复合文档 + 分帧 zlib
│   └── 2011 前：OLE2 + PKWARE DCL "implode"
├── DisplayLists  format/2-display-mesh.md       ← 网格（SolidWorks 画的那个）
│   ├── 三角形条带 + 法线（float32，米）
│   ├── Block1：每条条带边一个 ID（面内=0，否则=Parasolid edge node_id）
│   ├── 包围盒记录（解析盒 + 球，float64）
│   └── 面记录：face node_id、面类型 tag、参数、边表（**仅现代格式**）
├── Config-N-Partition  format/3-parasolid-body.md   ← 精确体
│   └── Parasolid XT 中性二进制，schema 13006
│       WORLD→BODY→REGION/SHELL→FACE→LOOP→FIN→EDGE/VERTEX
└── 其余：预览、特征树、配置、自定义属性（特征树仍在攻，见 open-questions）
```

**两条取几何的路**（`format/README.md:44-57` 的表）：网格 → STL/查看；精确体 → 精确 STEP/测量。两者**用同一套 ID 对齐**。

## 3. 技术方案要点

### 3.1 ★ 它的验证方法才是可迁移的东西：拿厂商自己的导出当 oracle

| 手段 | 数字 |
|---|---|
| 语料规模 | **73** 个 `.SLDPRT`（25 个 SW2011 + 24 个 SW2022 自建 + 24 个真实件） |
| 自建件怎么建 | 先定尺寸再建模，SolidWorks 同时导出 STEP/STL/X_T/X_B 并记下每个面的面类型 |
| 全量解析 | **73/73** 文件的解析输出 SHA-256 与记录值一致 |
| 面数 | 现代件 **45/45** 文件、**1,414** 个面与 SolidWorks 报的一致 |
| 面类型 | **136/136** 面与 SolidWorks 报的一致 |
| 网格 ↔ 体 ID 对齐 | 显示面 ID = 体 FACE `node_id`：**1,414/1,414**；显示边 ID = 该面周围的体边：**1,408/1,408** |
| 嵌入体 vs SW 的 STEP | 49/49 个受控模型，每个顶点/边/面在 **1e-8 m** 内，最差 **9e-18 m** |（来源：上游文档自述，见本卡 §8）
| 精确 STEP | 64/64 个零件的体积与面积等于 SW 自己的 STEP（纯精确几何件差 <3e-16 相对） |（来源：上游文档自述，见本卡 §8）
| 精确体积 | 对 SW 的 STEP 最差 **4e-14** 相对；对 24 个手算值最差 **4.3e-15** |（来源：上游文档自述，见本卡 §8）

（来源：`research/validation.md`、`export/exact-volume.md`、`format/README.md:62-74`）

★ **它的语料还顺手证明了一件事**：**SolidWorks 自己的 STL 导出会缺面**——C03/C09/C11 没有 −X 面、C04 没有顶盖；SW2011 的 25 个模型里 **12 个**的厂商 STL 缺一个带内环的平面（`research/validation.md:53-61`）。⇒ **「拿 SW 导出的 STL 当水密真值」这个做法是错的**，这条对我们现有的几何门有直接影响。

### 3.2 我实测到的：它的结论在本仓文件上成立

通过姊妹仓（Apache-2.0 代码）在本仓 8 个零件上验：来源：本卡 §8 证据清单。

| 断言（本仓 8 个零件） | 结果 |来源：本卡 §8 实测读数。
|---|---|
| 内嵌 Parasolid 体能解出精确体积 | 8/8 解出 |
| 解出的体积 = SolidWorks 存盘写的体积 | 8/8，相对差 **0 ~ 6e-11**（详见 `sw-d-blussyya-solidworks-converters.md` §3.1） |
| 显示网格面数 = 体面数 | 8/8 一致（如 `轴承6200_自制.SLDPRT`：21 = 21） |
| 网格体积 vs 精确体积 | 差 **-0.30%**（6793.4958 vs 6814.114466 mm³） |（来源：本卡 §8 实测读数）

⇒ **「网格是近似、体是精确」这条定性结论，在我方自己的零件上是可复现的。**

### 3.3 它明确列出「还没攻下来的」

`research/open-questions.md`：**特征树、草图、配置**是「in progress」（2022 受控模型上草图能解）；**装配、工程图「not looked at yet」**（`README.md:49-50`）。⇒ **这份文档不声称能读特征树**，别拿它当「能读可编辑历史」的依据。

### 3.4 容器层的两个「反直觉」事实（可直接进我方台账）

1. **现代 `.SLDPRT` 不是 OLE 复合文档**：它是「块序列 + 每块自带头（`14 00 06 00 08 00` + type_id + 解压后 CRC-32 + 压缩/未压缩长度 + 前言）」`format/1-container.md`。
2. **块名是 nibble 交换的**：所以字符串搜不到、只能靠偏移探测；解开交换就是一张普通目录（`Contents/DisplayLists`、`Contents/Config-0-Partition`…）。
3. **CRC 覆盖解压后的载荷** ⇒ **一次校验同时证明「块边界对 + 载荷偏移对 + 解压对」**，比任何启发式都强。★ 这条判据形态值得直接抄进我方任何「读二进制容器」的代码。

## 4. 运行条件与依赖

- 本仓**只有文档 + 一个 `tools/resolve-sweep.js`**（2468 B，批量跑语料的脚本）；**没有解析器代码**（已迁到 `solidworks-converters`）。
- 要跑它的结论，去姊妹仓：`node bin\sldprt.js ...`（零依赖，Node ≥18）。

## 5. 失败模式与已知坑

### 5.1 许可陷阱（最容易踩）

文档是 **CC-BY-SA-4.0**，代码是 **Apache-2.0**，README 还写明「**早期版本（代码+文档在一起）是 MIT，那些副本保持 MIT**」。⇒ 引用时**必须分清是哪一版、哪一部分**。★ 我方纪律：**这个仓一行都不抄**，只记结论。

### 5.2 它自己的「验证边界」写得很清楚（`research/validation.md:133-142`）

未验证项：真实浏览器使用、恶意输入（有 128 MiB / 2M 顶点 / 50k 面的上限但没做安全审计）、231 个内部顶点 + 11 个边界顶点「离开曲面且无解释」、以及**任何与语料不同的文件**（其它 SW 版本、装配、工程图、多实体、钣金、焊件）。（来源：上游文档自述，见本卡 §9）

### 5.3 与另一家的公开矛盾（我实测支持前者）

`XRTC5/sldprt-export` 的 README 声称「Parasolid XT 流是 **schema-locked（`SCH_3501251`）**，需要 Parasolid SDK」。而本仓与 `openswx` 都在 **schema 13006** 上把体完整解出来了——我在本仓 `轴承6200_自制.SLDPRT` 上实测：`openswx` 报 `schema SCH_3701229_37102_13006`、`node_count=436`、`complete=true`；`solidworks-converters` 报同一 schema、436 节点、体积 6814.114466。⇒ **「需要 Parasolid SDK」这个说法至少对 schema 13006 不成立**。

## 6. 对我方目标的可用处（本线必答四问）

**① 能读到什么粒度**：文档覆盖**元数据 + 网格 + B-rep 精确体**三档；**特征树明确未完成**。⇒ 它把「三档」这条线画得最清楚，是我方判断「某个库到底在哪一档」的标尺。

**② 能不能写**：文档里给了 **exact STEP** 与 **exact volume** 的做法（写 STEP 是精确 B-rep 转换；STL 是网格）。实际代码在姊妹仓。

**③ 本机可跑性**：**本仓无代码可跑**（只有 1 个 2468 B 的 sweep 脚本）；其结论我通过姊妹仓实测（§3.2）。（来源：本卡 §8 实测行）

**④ 对我方验证链的用途**：
- **它给的是一套「判据设计」**：拿厂商自己的导出当 oracle、按 face/edge ID 对齐两套几何、用 CRC 一次验三件事——这三条都能直接变成我方几何门的判据形态。
- **它给了一条反证**：SW 自己的 STL 会缺面 ⇒ 我方若拿 STL 当水密真值，**结论可能是错的**。
- **它给了一个上限**：多配置只有存盘那一个配置有几何（与 `dsandall/sld2step` 的 `ISSUES.md #1` 互相印证）。

## 7. 许可与红线

**CC-BY-SA-4.0（传染）**。⇒ ★★ **本仓文档的任何文本、表格、图都不能搬进本仓**（搬了就要求本仓相应部分也 CC-BY-SA）。允许：读、理解、用自己话重写事实（事实本身不受版权保护，README 也这么声明）。**代码去 `blussyya/solidworks-converters`（Apache-2.0）**。

另注：`images/` 里 4 张图是别人零件的渲染，**不在许可范围内**（`NOTICE`）。

## 8. 证据清单

- 文档：`D:\swagent-2026Q4\repos\blussyya__sldprt-format-research\format\README.md:15-42`（文件总览）· `:44-57`（两条取几何的路）· `:62-74`（语料与「verified 的含义」）· `research\validation.md:11-15`（73 文件语料）· `:17-33`（网格验证）· `:39-61`（STL 与 SW 缺面）· `:63-86`（精确 STEP）· `:88-113`（Parasolid 体）· `:115-131`（精确体积、在线样本）· `:133-142`（未验证清单）· `export\exact-volume.md:7-19`（散度定理 + 接缝拆分）· `:39-51`（精度表）· `README.md:35-50`（已知/未知表，特征树 in progress）· `README.md:92-113`（许可与「事实不属于任何人」声明）
- 一手交叉：`blussyya__solidworks-converters\README.md`（代码仓）、`schwitters__openswx` 的 `parasolid_inspect` 输出（schema 13006 可解，反驳 `SCH_3501251` 说法）
- 实测（2026-11-02）：本仓 8 个零件的 B-rep 体积 vs SW 存盘体积对照表（0~6e-11）、面数 21=21=21、网格体积 -0.30%（来源：本卡 §8 实测行）

## 9. 未确认事项

1. **本仓的文档结论我一条都没逐条复现**：73 文件语料在作者的 `sldprt-research-dump`（另一个仓），**我没 clone**。⇒ 1,414 面 / 136 面类型 / 64 个精确 STEP 这些数字**是它说的**（一手文档，非我方实测）。（来源：本卡 §9 未确认事项）
2. **「SW 的 STL 会缺面」这条我只读了文档，没有自己拿 SW 导 STL 对照**（本线不跑 SolidWorks）。
3. **`tools/resolve-sweep.js` 没跑**（要语料）。
4. **`format/5-pre-2011.md`（2011 前格式）与 `6-version-history.md`（版本码表）我只扫了标题**，没细读。
5. 它的「面记录仅现代格式」与我实测的「SW2026 文件面记录解不出（21 条 warning）」**是不是同一件事**——**未确认**：前者说的是 2011 没有面记录，后者说的是 2026 的布局变了。这两条可能都成立，也可能我对 warning 的理解有偏差。（来源：本卡 §9 未确认事项）

# Toolbox 到底能不能顶紧固件这一族（本机实测）

实测 2026-11-04 · 数据来自 `scripts/toolbox_index.json`（本机 `D:\SOLIDWORKS Data\browser` 的目录树快照）

---

## 0. 结论

**能顶，而且比我原先以为的强得多。但它有两个硬边界，必须说清楚。**

| 结论 | 证据 |
|---|---|
| **Toolbox 有 GB 这一套标准**，330 个零件 | `ToolboxStandards.xml` 里 `<Name>GB</Name>` / `<Source>gb.zip</Source>` / `<Install>Yes</Install>` |
| **其中 294 个是紧固件类**（螺钉 85 / 螺母 55 / 垫圈挡圈 47 / 螺栓螺柱 45 / 铆钉 33 / 销键 29） | 索引分类统计 |
| **GB 这一套覆盖得比 ISO 还全**（GB 330 > ISO 140） | 各 standard 计数：GB 330 / Ansi Inch 269 / DIN 234 / JIS 178 / ISO 140 |
| **但零件文件名里没有标准号，也没有尺寸** | 全库 1844 个零件中，code 带数字标准号的只有 31 个，**GB 的 0 个**；`gb/t` 字样 0 命中 |
| **尺寸是零件内的配置**，要去开文件读 | `sw_toolbox_index.py` 模块头明写；本机探查 `.sldprt` 二进制未找到可读配置名（文件是压缩/专有格式，33% 可见 ASCII） |

**一句话**：**「用 Toolbox 下紧固件」这条路是通的，但「告诉 Agent 我要 GB/T 70.1 M6×20」这一步，Toolbox 的文件名给不了——必须开文件枚举配置。**

---

## 1. GB 那一套到底有什么（330 个，逐类）

| 类 | 数量 | 代表 |
|---|---|---|
| **screws 螺钉** | 85 | 内六角圆柱头、十字槽盘头/沉头、开槽、紧定、自攻、木螺钉、滚花螺钉 |
| **nuts 螺母** | 55 | 六角（1 型/2 型/薄型/厚型）、开槽、盖形、滚花、焊接、圆螺母、锁紧 |
| **washers and rings 垫圈挡圈** | 47 | 平垫（N/S/L/XL 系列）、弹簧垫圈、齿形锁紧、止动、轴用/孔用挡圈 |
| **bolts and studs 螺栓螺柱** | 45 | 六角头（全螺纹/细杆/细牙）、法兰面、T 型槽、双头螺柱、U 型、吊环 |
| **rivets and studs 铆钉** | 33 | 抽芯、击芯、半空心、沉头、平圆头、焊接螺柱 |
| **pins and keys 销键** | 29 | 圆柱销、圆锥销、开口销、弹性销、槽销、平键、半圆键、楔键、花键 |
| **bearing 轴承** | 15 | 深沟球、角接触、圆柱滚子、圆锥滚子、推力、调心、滚针、微型 |
| **power transmission 传动** | 7 | 直齿圆柱、内齿、齿条、斜齿、直齿锥齿轮/小齿轮/等径锥齿 |
| **structural members 型钢** | 7 | 热轧等边角钢、不等边角钢、槽钢、工字钢、圆钢方钢、六角钢、轻轨 |
| **seals 密封** | 5 | 橡胶防尘圈 A/B/C 型、单向/双向密封 |
| **o-rings O 圈** | 2 | A 系列、G 系列 |

**这张表比 ISO 那套（140 个）更对中国口径**——GB 是 Toolbox 里第二大的标准集，仅次于 Ansi Inch 的 269 个（但 Ansi Inch 在中国用不上）。

---

## 2. 两个硬边界

### 边界一：文件名里没有标准号

全库 1844 个零件，code 里带 3–5 位数字的只有 **31 个**，其中 GB **一个都没有**。

对比一下就知道这是什么意思：

| 标准体系 | 零件命名风格 |
|---|---|
| **DIN** | `plain washer 6902 type abc_din` ← **带标准号** |
| **JIS** | `parallel key jis 1301` ← **带标准号** |
| **GB** | `hexagon socket head cap screws gb` ← **只有描述 + gb 后缀** |

**后果**：Agent 拿到「GB/T 70.1 M6×20」这个需求时，**无法从文件名直接定位**。它只能：
1. 用英文描述去搜（`hexagon socket head cap screws`）→ 找到零件文件；
2. 然后**开文件枚举配置**，找 `M6x20` 那一项。

**第 2 步现在没人做过。**

### 边界二：尺寸在配置里，不在文件名里

`sw_toolbox_index.py` 的模块头已经写死了这条：

> ❌ 不含：**型号→尺寸的工程数据**（导轨行程、丝杆导程、额定载荷…）
> 尺寸是**零件文件内的配置**，不在文件名里 ⇒ **要拿尺寸得开文件读配置**。

我这次又验了一遍：读 `.sldprt` 二进制，前 512 字节只有 33% 可见 ASCII，UTF-16 扫描也没找到任何 `M6`/`GB` 字样——**文件是压缩/专有格式，不能靠扫字符串拿配置名**。

**能拿配置名的正规途径只有两条**：
- 用 SolidWorks API `IPartDoc.GetConfigurationNames()`（要真机 + COM）；
- 用 `swdocumentmgr.dll`（DocumentMgr，**需独立许可**，但**不用开 SolidWorks**）。

---

## 3. 所以「用 Toolbox 顶紧固件」到底要补什么

| 要补的 | 怎么补 | 难度 |
|---|---|---|
| **① 需求标准号 → Toolbox 零件文件** | 建一张映射表：`GB/T 70.1 → hexagon socket head cap screws gb`。**330 个零件，人工标注一次即可**，之后是查表 | 低 |
| **② 零件文件 → 可用配置（规格）** | 真机调 `GetConfigurationNames()` 或 DocumentMgr，把每个零件的配置名导出成 JSON | 中（要真机） |
| **③ 配置名 → 尺寸参数** | 打开配置读 `GetDimension`，或读零件自定义属性 | 中 |
| **④ 插入装配体** | 项目已有 `sw_assembly.add_component` + `sw_toolbox_index.part_path` | **已有** |

**①②③ 干完之后，这一族就从「规划」变成「可自动化」。** 而且这张表**只需要建一次**——Toolbox 的零件不会变，变的是配置。

---

## 4. 但有三件事 Toolbox 给不了

### ① 螺纹是近似的
官方帮助页原文：*"The fasteners provided in Toolbox are approximate representations and do not include accurate thread detail, which might make them inappropriate for certain analyses such as stress analysis."*

**含义**：装配、出图、干涉检查够用；**做应力分析不合适**。要真实螺纹得自己建模或走 ANSI/ISO 螺纹标准表。

### ② Toolbox 是库零件，不是「你的零件」
发给没有 Toolbox 的协作方会掉链接；要加工得先转换。这条在 `00-报告.md` §3.2 已经记过。

### ③ Toolbox + PDM 有坑（官方自己写的）
`Create Configurations` 模式下**每加一个配置就生成一个新文件版本**；PDM 管理时必须选 `Error when writing to a read-only document`。

---

## 5. 与竞品的对比（紧固件这一族）

| 源 | GB 覆盖 | 有标准号索引 | 能程序化取件 | 结论 |
|---|---|---|---|---|
| **SolidWorks Toolbox（本机）** | **330 个 GB 零件** | ❌ 要自建 | 部分（有路径，无配置） | **主选**，补映射表即可 |
| FreeCAD Fasteners WB | 只有 ISO/ASME，**无 GB** | 有（`iso4762` 这种） | ✅ 开源可读 | 只能借它的**数据结构思路** |
| BOLTS / BOLTSFC | 核心数据里无 GB | 有 | ✅ 数据可解析 | 参考 |
| cq_warehouse fastener | 无 GB（ISO 为主） | 有 | ✅ Python | 参考 |
| BOSL2 threading | 无 GB | — | ✅ | 只借螺纹牙型数学 |
| 迈迪工具集 | 声称 20 万+ GB 件 | 未知 | ❌ 插件，需点鼠标 | 需改造 |

**结论**：**在「买紧固件」这一族，本机 Toolbox 是中国口径覆盖最全、且已经在手边的唯一选择。** 开源世界的紧固件库全是 ISO/ASME 体系，没有 GB。

---

## 6. 落到开发计划上的三条

1. **紧固件族从「买」升级为「买·可自动化（在补）」**——不是不能做，是要先建映射表。
2. **建表这件事应该排进 M2**，和「轴」并列。因为：
   - 它不需要新的几何算法（Toolbox 已经给了）；
   - 它需要的是**一次真机枚举 + 一张人工映射表**；
   - 做完之后**25 个「买」项里有 6 个（螺栓/螺钉/螺母/垫圈/销/铆钉）同时解决**。
3. **不要在 Toolbox 上做强度分析**——官方明说螺纹不精确。

---

## 7. 未查证

| 项 | 状态 |
|---|---|
| Toolbox 的 GB 零件**具体依据哪一版 GB/T** | **查不到**（文件名与 XML 里都没有标准号） |
| 每个零件**有多少个配置** | 未查（需要真机 `GetConfigurationNames()`） |
| `swdocumentmgr.dll` 在本机**有没有许可** | 未测 |
| Toolbox GB 齿轮（7 个）**是不是真渐开线** | **大概率不是**（官方对 Toolbox 齿轮的定性是"不是真渐开线"），但**未逐个验证** |
| GB 轴承 15 个的**额定载荷数据** | 文件里没有，索引也不含 |

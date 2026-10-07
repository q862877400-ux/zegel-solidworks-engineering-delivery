# ★ 外部清单《部署工具集问题清单（并集 731）》的核对与去伪

> ★ 被核对件：`D:\AI\DSH-sandbox\deliver\工具集问题清单-并集731.md`（731 行，另一个对话产出）
> ★ 核对轮次：**2026-10-07 接手轮** · ★ 核对人：本仓（`coding-agent::SW`）本次会话
> ★★ 用户对本次核对的指令逐字：「★ 这是另一个对话说的问题，你参考一下，结合实际情况，
>   **去伪存真，不要盲目采信**」✓
> ★ 本文**只记录核对结论**；★ 每一条都给出**可复算的读数**，★ 不采信它自己的数字 ✓

---

## 〇 · ★★★ 最要紧的一条：**它的语料不是活的工具面**

★ 它自称的语料是 `D:/AI/SW/output/lean-tool-surface/catalog-all.json` —— ★ 而该文件的
`sources` 字段**逐字**是：

```json
{"sessionScan": "27 会话抽样", "sessionUnion": 554, "solidworksAdded": 177}
```

★ 加上 `generatedAt: 2026-10-05T14:51:52Z` · `n: 731` ⇒ ★★ **它是「扫 27 个历史会话」拼出来的
并集**，★ **不是**任何一次 `tools/list` 的结果 ✗

⇒ ★★★ **后果（这一步决定后面所有百分比能不能用）**：

| 口径 | 数字 | 说明 |
|---|---|---|
| 它报告的 | **731** 个 / 1,043,538 字节（≈ **260,885 token**） | ★ **没有哪一个会话真的看到过这个集合** ✗ |
| 本会话（preset `sw-engineer`）**活面实测** | **589** 条目 / 系统提示 **113,059 字符 · 134,796 字节** | ★ 从会话日志的 `system/message` 里解出来 ✓ |

★ 语料的构成差异（复算见 §三）：

| 来源 | 它的语料 | 本会话活面 |
|---|---:|---:|
| solidworks | **524** | **504** |
| 内建 | **182** | **77** |
| sciverse | 6 | 6 |
| **ufo** | **19** | ★ **0**（本 preset **没挂**；配置里 `ufo` 只出现在**另一个按需 preset 的注释**里）|
| crawl4ai | 0 | 2 |

⇒ ★★ **推论两条**：
1. ★ 它的「**24.5% 可删**」是按**并集**算的 ⇒ ★ 换到活面上**分母就变了**，
   `ufo`（19）与多出来的 105 个内建**根本不在我们的工具面里** ✗
2. ★ 第 1/3/4/6/7 类的清单里**混着内建工具**（`read_pdf` / `list_agents` / `univer_*` /
   `cua_driver_native__*` / `ks_*` / `win_*`）⇒ ★ 那些条目**与 SW 工具面无关** ✓

---

## 一 · 逐类判定（★ 真 / 半真 / 假 / 不适用，四条都点名）

### 0a · 「完全重复：描述与参数一模一样」—— ★ **不适用（且不是我们的）**

★ 复算：语料里确实有 **2 组**（描述 + 参数逐字相同），★ 但两组**都是 `mcp__ufo__*`**：
`ufo_get_app_window_controls_info` / `…_controls_target_info` ·
`ufo_get_desktop_app_info` / `…_desktop_app_target_info` ✓
★ 而 `ufo` **不在本 preset**（活配置里 `ufo` **0 处挂载**；活目录里 `mcp__ufo` **0 条**）⇒
★★ **结论：这条与 `coding-agent::SW` 无关**。★ 若它真是问题，那是 **UFO 那个服务器的缺陷**，
★ 我们既没有它的代码、也没有它的授权去改 ✓（★ 可对照：本仓有「不许把未并入的写成已并入」的纪律）

### 0b · 「同一操作两种调用约定（平铺 vs 包 params）」—— ★★ **假（对活面而言）**

★★★ 这是**本文最值钱的一条更正**。它举的两组是：
`solidworks_add_dimension`（必填 `["params"]`）vs `add_dimension`（必填 `["px","py","value"]`）。

★ **复算两个语料**：

| 语料 | `mcp__solidworks__*` 条数 | 带 `{"params": …}` 信封 | **平铺实参** |
|---|---:|---:|---:|
| 它的并集语料 | 524 | 467 | ★ **57** |
| **本会话活面** | **504** | ★★ **504** | ★★ **0** |

⇒ ★★ **活工具面上「两种调用约定」不存在** ✓ —— ★ 那 57 个平铺工具来自它自己的
`solidworksAdded: 177`（★ 历史并集里**曾经出现过**的工具名），★ **不是**当前服务器暴露的 ✓
★ 我另外把这两个名字在活面里逐个查过：`mcp__solidworks__add_dimension` /
`mcp__solidworks__open_document` / `mcp__solidworks__get_selection` / `mcp__solidworks__create_sketch`
—— ★ **全部 absent** ✓

★ ★ **可迁移的教训（值得留下）**：★ 「两种调用约定」这个**判据本身是对的**，
★ 而它只在**并集语料**上成立 ⇒ ★★ **凡按「扫历史会话」拼出来的工具清单，
都不能用来判「现在模型会看到什么」** ✓（★ 与**已知事实 57** 同族：环境恰好满足 ≠ 在测）

### 1 · 「把参数、枚举、元数据当成工具」55 个 —— ★ **半真**

★ 复算与逐条读下来，这 55 个里**混了两类完全不同的东西**：

| 子类 | 例子 | 判定 |
|---|---|---|
| ★ **真能力**（读不到就只能猜） | `*_params`（`loft_params` / `shell_params` / `hole_params` / `pattern_params` …）· `*_evidence`（`weldment_evidence` / `surface_evidence` / `topology_evidence` …）· `*_list_*` / `*_standards` | ★ **不是缺陷** ✗ —— 「读一个已建成特征的**实际参数**」与「参数可选值放进 enum」是**两件事**：前者要**回读文档**，schema 里表达不了 ✓ |
| ★★ **内部管线助手**（模型永远不该主动选） | `macro_build_prompt` · `macro_extract_vba_code` · `macro_fallback_template` · `macro_normalize_model_family` · `macro_select_template` | ★★ **成立** ✓ —— 这 5 个只服务**我们自己的宏生成流程**，★ 挂在模型面前纯属噪声 |

⇒ ★ **可动的只有那 5 个 `macro_*`**（见 §二-1）✓

### 2 · 「工具名里重复了服务器名」482 个 —— ★ **事实成立、建议不成立**

★ 复算（活面）：`mcp__solidworks__solidworks_*` = **491** 个（+ `cadstudio_*` 13 个 = 504）✓
★ 所以「名字里又把服务器名写了一遍」**是真的** ✓

⚠ **但它建议的「改名为 `mcp__activate_configuration`」与本仓的**强制规范**冲突** ✗：
★ 本仓**规则 1（命名）**要求 `solidworks_<域>_<动作>`，★ **并有门禁**（`check_union_conventions.py`
的 R1）在守 ⇒ ★ 逐条改名会**同时**打断 `capabilities.yaml` 的 `mcp_tools`、`all_specs()`、
文档、测试与那道门禁 ✗

⇒ ★★ **结论**：★ 这是个**规范层的问题**（「DSH 已经用 `mcp__<server>__` 消歧了，
工具名里那一段是不是冗余？」）—— ★ 该走**一次规范变更**（R1 出新版本 + 迁移脚本），
★ **不该**按这份清单逐条改名 ✓

### 3 · 「同族近似名」39 组 —— ★ **可作复核清单**

★ 抽查方向是对的：`document` / `dimension` / `drawing` / `sketch` 这几族**确实挤** ✓
★ 且它挑出的 `open_document` vs `solidworks_open_document` 那类**历史上真实存在过**（见 §一-0b）✓
⚠ 但清单里**混着内建工具**（`team_task_*` / `agent_session_*` / `univer_*` / `browser_*`），
★ 那些不属于本仓工具面 ✓

### 4 · 「通用名与专用名并存」31 组 —— ★ **半真（分类不成立、清单可用）**

★ 它的判据是「**≤2 个实质词 = 泛**」⇒ ★ **明显过糙**：它把
`solidworks_sketch_start` / `sketch_end` / `sketch_trim` / `sketch_fillet` 判成「泛」✗ ——
★ 那四个是**高度具体**的操作（进入/离开草图、修剪、草图圆角），★ 模型不会混淆 ✓

★ 而它**漏掉了**真正同型的问题：`chamfer_circular_rim_volume` / `chamfer_straight_edge_volume` /
`chamfer_volume_report` 这三个是**纯算术助手**（算倒角切掉多少体积），
★ 它们**不是**用户会主动选的「动作」✓ —— ★ 这一类更该被判进它自己的第 1 类 ✓

### 5 · 「跨服务器同名：无」—— ★ **真** ✓

★ 复算：本会话各服务器前缀互不相同（`mcp__solidworks__` / `mcp__sciverse__` / `mcp__crawl4ai__`），
★ 未见跨服务器重名 ✓

### 6 · 「自述里声明弃用或『用别的』」39 个 —— ★★ **半真（判据有可复现的假阳性）**

★★ 它的检测是**关键词**扫全文 ⇒ ★ **必然误伤**。可复现的反例（★ 我在**活面**上复算到）：

| 被它列进去的 | 它自述**逐字**说的是 | 判定 |
|---|---|---|
| `solidworks_feature_delete` | 「Delete one FEATURE via `IModelDoc2.EditDelete()` (0 params, ★ **NOT deprecated**)」| ✗ **假阳性** —— 它说的是「**不**废弃」，被 `deprecated` 这个词命中 |
| `solidworks_api_deprecated_successor` | 「Given a member name, return the **successor** this repo maps it to」| ✗ **假阳性** —— 它是**查废弃**的工具，不是废弃工具 |
| `insert_coordinate_system` · `insert_delete_face` · `part_sweep` | 自述里写着「`IModelDoc2.X` 官方标 **Obsolete** ⇒ ★ 用**后继**」| ✗ **假阳性** —— ★ 它们**就是**「用别的」里的那个**别的** ✓ |

★ **真正成立的子集 = 「本机建不出来」那一支**。★ 复算（活面描述里出现
「不可用 / 建不出 / 到不了 / NOT USABLE」语义的）：**17 / 459** 条声明式 spec 命中该语义，
★ 而其中**当前确实建不出来**的是**钣金那一支**：

```
solidworks_sheet_metal_create_hem          五种形态全部回 None
solidworks_sheet_metal_create_one_bend     仍不可用（原因已具体化）
solidworks_sheet_metal_create_edge_flange  仍不可用（报错已前移）
solidworks_sheet_metal_create_gusset       仍不可用（属性层已修好）
solidworks_sheet_metal_create_draft        NOT USABLE ON THE TEST MACHINE
```
（★ 另有 `weldment_trim` / `insert_closed_corner` 自述「在后端到不了建成」）

⇒ ★★ **结论**：★ 「**挂着已知在本机不可用的工具**」这件事**是真的**（≈ 5–7 个），
★ 而它给的 **39** 这个数**不能直接用** ✓（★ 见 §二-2）

### 7 · 「只读与发现类混在动作类里」14 个 —— ★ **方向对、清单混语料**

★ 它举的 14 个里**多数是内建工具**（`read` / `read_pdf` / `read_image` / `list_agents` /
`list_mcp_resources` / `get_goal` / sciverse 那 5 个），★ 与 SW 工具面无关 ✓
★ 而它那句观察**是对的且重要**：「实测里出现过『该建模却选了 `grep`』」——
★ 那正是**工具选型准确率**问题，★ 也就是本仓 lean 那条线（规格 208）在做的事 ✓

---

## 二 · ★ 我判断**值得动**的三条（按杠杆排序）

### ★ 1 · 把 5 个 `macro_*` 内部助手从模型面前撤掉（真、便宜、可核）

★ `macro_build_prompt` · `macro_extract_vba_code` · `macro_fallback_template` ·
`macro_normalize_model_family` · `macro_select_template` —— ★ 它们的 doc 自己就写着
「★ Pure function; the template bodies live in this repo」⇒ ★ 它们是**我们宏生成管线的中间步骤** ✓
★ 处置建议（★ 二选一，需业主定）：① 合成一个 `solidworks_macro_generate(prompt)`；
★ 或 ② 保留但在**描述首句**写明「内部件，模型不应直接调用」。
⚠ ★ **不做**：直接把它们删掉 —— ★ 它们有各自的来源与真源（`sw_macro*.py`），
★ 删工具 ≠ 删实现，★ 而本仓的纪律是「**不做也是交付**：要给理由+证据」✓

### ★ 2 · 5 个「本机建不出来」的钣金工具：**建议留着，但把结论提到描述首句**

★ 现状：这些工具**挂着**，★ 而「不可用」写在描述**第三段之后** ⇒
★★ **模型读到的是正常口吻的首句**（★ 例 `create_gusset` 首句是
「Create a native sheet-metal **gusset** on a SELECTED supporting face.」）✗
⇒ ★ 这**正是它的第 6 类真正想说的那件事**（★ 而不是「39 个都该删」）✓
★ 处置建议：★ 把「★ **本机（SW 2026 SP4.1 + pywin32）建不出来，原因见证据**」
**提到首句** —— ★ 因为 lean 投影（`firstLine()`）**只保留首句**，
★ 写在后面的模型**根本看不到** ✓（★ 这一条比它原文的建议**便宜得多、也更准**）

### ★ 3 · 名字冗余：查清「要不要改规范」，**不要**按清单改名

★ 见 §一-2：事实成立，但改动面横跨规范 / 门禁 / 清单 / 文档 / 测试，
★ 且「`mcp__<server>__` 已经消歧」这个前提**要先被规范承认**才谈得上改 ✓

### ★ 4 · 附带建议：**把它的语料换掉再谈百分比**

★ 它的「24.5% 可删 / 179 个 / 275,544 字节」是按**27 会话并集**算的 ⇒ ★★ **不能用来指导决策** ✓
★ 正解：★ 用**活面**（`tools/list`，★ 本仓可复算：`tools/probe_mcp_stdio_handshake.py`
给 504；★ 或从会话日志里解 `system/message` 的 `tools:catalog` 段给 589）✓

---

## 三 · 复算命令（★ 全部本机可跑，不采信任何转述数字）

```bash
# ① 语料口径（★ 它是不是"活面"）—— 逐字看 sources / generatedAt / n
python -c "import json;d=json.load(open(r'D:/AI/SW/output/lean-tool-surface/catalog-all.json',encoding='utf-8'));print(d['generatedAt'],d['n'],d['sources'])"
#   ⇒ 2026-10-05T14:51:52.466Z 731 {'sessionScan': '27 会话抽样', 'sessionUnion': 554, 'solidworksAdded': 177}

# ② 服务器**活面**到底几个工具（真 JSON-RPC 握手）
python D:\AI\SW\tools\probe_mcp_stdio_handshake.py        # ⇒ 504（459 声明式 + 45 装饰器）

# ③ 本会话**装配后的系统提示**里那段 tools:catalog（589 = 504 + 6 + 2 + 77）
#    ★ 会话日志是 zstd **多帧**，zlib.zstdDecompressSync 只解第一帧 ⇒ 要逐帧扫魔数 28 B5 2F FD
#    ⇒ 产物见 output/_system_prompt.txt / output/_review_731_vs_live.py

# ④ 0b 的正面复算：活面里平铺实参的 solidworks 工具有几个
python D:\AI\SW\output\_review_731_vs_live.py
#   ⇒ 语料 A（它的并集）：524 个中 57 个平铺 · 语料 B（本会话活面）：504 个中 **0** 个平铺
```

---

## 四 · 一句话结论

> ★ 这份清单的**观察角度有价值**（工具面确实太长、近似名确实多、确实存在"挂着自己说不能用"的工具），
> ★★ 但它的**语料是 27 个历史会话的并集、不是活工具面** ⇒
> ★ **0b（两种调用约定）在活面上不成立**（504/504 都是 `params` 信封）·
> ★ **2（名字冗余）事实成立但建议与规则 1 冲突** ·
> ★ **6（自述弃用）判据是关键词、含可复现的假阳性**（「NOT deprecated」被当成 deprecated）·
> ★ **1/4/7 混着内建工具、分类不成立** ⇒
> ★★ 真正该动的只有 **5 个 `macro_*` 内部助手** 与 **5 个「本机建不出来」描述的**首句位置** ✓

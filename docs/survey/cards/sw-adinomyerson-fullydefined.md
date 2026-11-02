# adinomyerson/FullyDefined-AI-for-SOLIDWORKS

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `adinomyerson/FullyDefined-AI-for-SOLIDWORKS` · https://github.com/adinomyerson/FullyDefined-AI-for-SOLIDWORKS |
| 许可 | **MIT**（仓库 `license.spdx_id = MIT`，来源：`gh api repos/...` 2026-11-02）⇒ 可并入 |
| 元数据 | stars **0** · created **2026-10-24** · pushed **2026-11-01** · 仓库约 3.4 MB · 第一方代码 **86 个文件 / 16,852 行**（来源：`gh api search/repositories` 与本地 `Get-ChildItem -Include *.py,*.cs,*.ts,*.js` 行数统计，2026-11-02）|
| 克隆 | `D:\swagent-2026Q4\repos\adinomyerson__FullyDefined-AI-for-SOLIDWORKS`（`--depth 1`）|
| 证据等级 | **读码**（未运行；读 `sketch_define.py`、`core/sketch.py`、`README.md`）|

## 1. 一句话定位

**0 星、7 天前发布、16,852 行代码、把「全约束」写进产品名并真的做了解法的一个 SolidWorks MCP 服务端**：它自称「every result is checked by measuring the model」，而代码里确实有「从原点起把欠定义草图补成全约束」的自动修复通道，且用的是真实的 `Status == 3`（完全定义）枚举。（来源：本卡 §8 的 stars/行数实测与 README 引文）

**这是我本轮找到的「发布没多久、还没人关注」最典型的一个**——按星数排序它永远排不到前面。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP 服务端（本地 stdio），面向 Claude Desktop / Claude Code / Antigravity（README 逐字：「Tested with Claude Desktop and Claude Code, using the Claude Opus and Claude Sonnet models」）。提供 `.exe` 安装包（Releases）。
**中间表示**：**特征树 + 选择集**，无自建 IR。工具层按域分模块：`sketch_define` / `sketch_draw` / `shapes` / `holes` / `sheet_metal` / `drawings` / `annotations` / `mates` / `assembly` / `documents`。
**生成**：不生成代码；由模型调工具，工具调 COM。
**编排**：`orchestration=loop`（工具返回测量值供模型判断下一步）。
**执行**：pywin32 COM；`core/lock.py` 有互斥原语（`win32event`）。
**验证**（核心）：README 明写「**Checked, not assumed:** every result is measured from the model (volume, mass, distances, faces, sketch …)」；另有 `doctor.py`（23.2 KB）做安装自检，含「a small test part built in SolidWorks, measured」。
**交付**：`.SLDPRT` / STEP / 工程图。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★★★ 「全约束」是被当成能力做的，不是当成提示词

- `core/sketch.py:917` 的函数 docstring 逐字：「**Fully define, from the origin, every sketch a new feature made for itself and left unde[fined]**」——即：新特征自己创建、又没被约束好的草图，**自动从原点起补全**。这是一条「事后修复」通道，不是「让模型记得加约束」。
- `tools/sketch_define.py:309` 的判断是 `return int(_value(point, "Status")) == 3` —— **3 = 完全定义**，与我们已知事实（2 欠定义 / 3 完全定义 / 4 过定义）一致。⇒ **它没有把枚举搞错**，这一点比很多同类项目强。
- 提供 `_free_points` / `_endpoint_joins` / `_ref_point_gap` 三个几何级分析函数，用来**找出哪些点还没被约束住**，而不是只回一个状态码。

### 3.2 ★★★ 把「性能坑」写进代码注释并量化

`_no_ui_updates` 上下文管理器用 `CommandInProgress` 关掉工具栏刷新，注释逐字：「in an open sketch of a few dozen entities that costs about **70 ms a call** (P19: a 32-line outline took **40-70 s a dimension**)」。⇒ **同一招我们也用，但它是先把代价量出来再写进去的**；而且它做了「进入/恢复」的成对处理（`before` 读回、`finally` 恢复），比直接置 True 更安全。

### 3.3 ★★ 约束名映射的细节正确

`RELATIONS` 字典把语义名映射到真实约束枚举，并且**区分「线段选择」与「仅点选择」两种情形**：

| 语义 | 线段/混合 | 仅选点时 |
|---|---|---|
| horizontal | `sgHORIZONTAL2D` | `sgHORIZONTALPOINTS2D` |
| vertical | `sgVERTICAL2D` | `sgVERTICALPOINTS2D` |
| coincident | `sgCOINCIDENT` | `sgCOINCIDENT` |
| merge | `sgMERGEPOINTS` | `sgMERGEPOINTS` |
| midpoint | `sgATMIDDLE` | `sgATMIDDLE` |
| parallel | `sgPARALLEL` | `None` |

（来源：`files/solidworks_mcp/tools/sketch_define.py` 的 `RELATIONS` 常量）
⇒ **这是「同一关系在点选与线选下枚举不同」这类坑的现成对照表**，正是我们 `SKETCH_CONSTRAINT_TYPES` 该覆盖而容易漏的部分。

### 3.4 ★★ 覆盖面超预期：钣金 84.8 KB、工程图 66.2 KB（来源：本卡 §3.4 的文件大小实测，命令见 §8）

按文件大小（`files/solidworks_mcp/` 下）：`tools/sheet_metal.py` **84.8 KB** · `tools/drawings.py` **66.2 KB** · `core/sketch.py` 49.3 KB · `tools/annotations.py` 46 KB · `tools/mates.py` 45.1 KB · `tools/assembly.py` 41.1 KB · `tools/sketch_define.py` 40.3 KB · `core/assembly.py` 37 KB · `tools/sketch_draw.py` 27.5 KB · `core/drawing.py` 26.9 KB · `tools/documents.py` 23.5 KB · `doctor.py` 23.2 KB。
⇒ **一个 0 星项目在钣金与工程图上的投入，比很多几百星的项目大**。

### 3.5 ★ 它知道自己的边界

README 有一条「Strength checks (no simulation)」——**明确说自己不做仿真**。这种自我限定在同类项目里不常见。

## 4. 运行条件与依赖

- Windows + SolidWorks（README 未写版本下限；工作流是本地 MCP 服务端 + `.exe` 安装包）。
- 本地 MCP 客户端（Claude Desktop / Claude Code / Antigravity）。
- `doctor.py` 提供安装自检（含 «建一个测试零件并测量» 这一档）。

## 5. 失败模式与已知坑

1. **0 星、7 天前发布**：**没有任何外部用户反馈**，README 里连 issue 区都还是空的（未核）。
2. **未运行**：本卡结论全部来自读码；「every result is checked」是 README 的说法 + 代码里有测量工具，**是否每次调用都真的测量并未逐一核对**。
3. **`files/` 目录结构说明它是「要拷进某处的文件包」**，不是标准 Python 包（无 `pyproject.toml`），安装路径依赖 `.exe` 安装器 ⇒ 二次开发要先搞清它的落地位置。
4. **版本兼容性未声明**：只写 SolidWorks，未写测试过的版本；这一点比 `hjbaard`（明确 SW2026 SP3.2）与 `soheil-mp`（明确 SW2025 SP1.2）弱。
5. **单文件偏大**（`sheet_metal.py` 84.8 KB）。

### 5.5 宣传与关注度（2026-11-02 实测，回答「为什么 0 星」）

**一处宣传都没找到**：GitHub 主页无 `blog`、无 `twitter_username`；仓库 `homepage` 为 **null**、`has_discussions=false`；README 里唯一的外链是 `antigravity.google/download`、`docs.astral.sh/uv/`、`modelcontextprotocol.io`——都是工具文档，不是推广。

**「没人关注」的量化**（`gh api repos/.../releases --jq '.[] | "\(.tag_name) dl=\([.assets[].download_count]|add)"'`，2026-11-02）：

| 版本 | 下载次数 |
|---|---:|
| v0.3.3 | **4** |
| v0.3.2 | **3** |
| v0.3.1 | **4** |
| v0.3.0 | **4** |
| v0.2.0 | **4** |

⇒ **每个版本全世界只有 3–4 次下载（含作者自测）**。这不是「酒香巷子深」，是**巷子口没开**。（来源：本卡 §5.5 的 release 下载统计，命令见该节）
作者 bio 逐字「**Mechanical engineering student at TAU and systems engineer for TAUver Space Robotics Group**」——学生项目，未做任何推广。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（三件，都是我们 E1 缺的）**：
1. **★★★「全约束」的自动修复通道**：`Fully define … every sketch a new feature made for itself and left undefined`。我们的做法是「告诉模型加约束」，它是**在特征创建后回头把漏洞补上**——这是把 E1 从「要求」变成「保证」的关键一步。
2. **★★★ 约束名「线段 vs 点」双映射表**：直接可并入我仓 `SKETCH_CONSTRAINT_TYPES` 的对照与测试（尤其 `sgHORIZONTALPOINTS2D` 这类只在点选时成立的枚举）。
3. **★★ `CommandInProgress` 的量化收益 + 成对恢复写法**：我们的护栏可以直接补上「before 读回 + finally 恢复」。

**不能学**：
- **无 IR、无事务、无回滚**：它仍是「一次调用一个工具」，没有 `forge_ai` 的独立复算，也没有 `hjbaard` 的失败回滚。
- **0 星无验证**：不能作为「已验证」的参照。

## 7. 许可与红线

**MIT** ⇒ 代码可并入，保留版权与许可全文。

## 8. 证据清单

- `...\FullyDefined-AI-for-SOLIDWORKS\README.md`（L3 定位、L10「every result is checked by measuring the model」、L18「sketches fully defined from your own dimensions」、L28「Checked, not assumed」、L53 doctor 自检含测量、L143「Strength checks (no simulation)」）
- `...\files\solidworks_mcp\tools\sketch_define.py`（`_no_ui_updates` 与 70 ms / 40-70 s 注释；`RELATIONS` 双映射；`:309` `Status == 3`）
- `...\files\solidworks_mcp\core\sketch.py:917`（Fully define … left undefined 的修复通道）
- `...\files\solidworks_mcp\core\sketch.py:371`（是否已定义 / 剩余自由实体）
- 统计命令（2026-11-02）：`Get-ChildItem -Recurse -Include *.py,*.cs,*.ts,*.js` → **86 文件 / 16,852 行**；各模块大小见 §3.4
- 元数据：`gh api repos/adinomyerson/FullyDefined-AI-for-SOLIDWORKS`（stars 0 / created 2026-10-24 / pushed 2026-11-01 / MIT）

## 9. 未确认事项

1. **未运行**：`doctor.py` 的自检、全约束修复是否真能跑到 `Status == 3`，**未实测**。
2. **支持的 SolidWorks 版本**：README 未写，未核。
3. **「每次结果都测量」的覆盖率**：有多少工具带测量未统计（只确认存在 `measure` 类工具与 `doctor` 自检）。
4. **`files/` 落地机制**：`.exe` 安装器装到哪、是否可脱离安装器使用，未核。
5. **0 星的成因**：是刚发（7 天）、还是作者没推广，未查。

# autocad-mcp（puran-water/autocad-mcp）

<!-- survey: class=H; repr=sequence; orchestration=none; verify=run-only; deliver=drawing; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/puran-water/autocad-mcp （`git remote -v` 实测同址）|
| 许可 | MIT；版权行 `Copyright (c) 2024 AutoCAD MCP Server Contributors`（`LICENSE:3`），`pyproject.toml` 亦写 `license = "MIT"` → **可借鉴**（可读、可抄、可商用，保留版权声明）|
| 元数据 | 591 stars · 最近推送 2026-02-20T17:36:20Z · Python（来源：`gh api repos/puran-water/autocad-mcp`，取数 **2026-10-24**）|
| 克隆 | D:\ai3d-survey\repos\puran-water__autocad-mcp |
| 证据等级 | 读码（未启 AutoCAD、未跑测试；计数取自静态扫描与集合比对）|

## 1. 一句话定位

★ **合并式工具的极端样本**：**8 个工具**用 `operation` 参数分派 **72 个操作**，压在一个"双后端"抽象上——能驱动 AutoCAD LT 就走**文件 IPC + 击键触发 AutoLISP**，不能就退到 **ezdxf 内存 DXF**。它对"529 个工具"给出的答案是「8 个」。（来源：`server.py:33-461` 的 8 个 `@mcp.tool` 与 72 个 operation 分支）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- **输入**：`operation` 字符串 + 可选 `data` 字典。JSON Schema 里**没有**逐操作约束：`drawing(operation: str, data: dict | None, include_screenshot: bool)`（`src/autocad_mcp/server.py:35-39`）是 8 个工具里 7 个的形态；逐操作契约只写在 **docstring**（如 `server.py:40-53`）。
- **中间表示**：命令名 + 参数 ⇒ 后端方法名 ⇒（file_ipc）一个 JSON 命令文件 /（ezdxf）内存 DXF 实体。没有草稿、没有特征树、没有可回放的建模脚本——**是一串就地生效的命令**。
- **生成**：无生成环节；模型给什么参数就画什么（`server.py:135-178` 的 21 支 `entity` 分派就是逐条创建/改动）。
- **编排**：**没有**。8 个工具都是无状态分派，全仓无循环、无模板、无审批门（`server.py:33-519` 内无任何重试/规划代码）。
- **执行**：两条完全不同的路。① **file_ipc**：把命令写成 `<ipc_dir>/autocad_mcp_cmd_<id>.json`，先写 `.tmp` 再改名（原子），然后 `_type_dispatch_trigger()` 发击键触发 `(c:mcp-dispatch)`，再轮询结果文件并按 `request_id` 校验（`src/autocad_mcp/backends/file_ipc.py:140-194`）。击键走 `PostMessageW(WM_CHAR)` 到 MDIClient，不抢焦点（`README.md:168-174`）。② **ezdxf**：`ezdxf.new("R2013")` 建内存文档（`backends/ezdxf_backend.py:48-52`）。
- **验证**：`CommandResult(ok, payload, error)` 信封（`backends/base.py:10-24`）+ 可选截图旁路：任何工具带 `include_screenshot=True` 就在结果后附 PNG（`client.py:149-163`）。**没有几何门禁**——成功就是后端说 ok。
- **交付**：DXF / DWG / PDF，靠 `drawing` 的 `save`、`save_as_dxf`、`plot_pdf`（`server.py:61-68`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★ 工具清单与粒度统计（逐个数清）

`@mcp.tool` 装饰器共 **8 处**，每个都是合并式（`operation` 判别）：

| # | 工具 | 注册处 | 操作数 | 操作清单（docstring）/ 分派体 |
|---|---|---|---|---|
| 1 | `drawing` | `server.py:33` | 10 | `server.py:40-53` / `57-78` |
| 2 | `entity` | `server.py:88` | 21 | `server.py:102-130` / `135-178` |
| 3 | `layer` | `server.py:190` | 8 | `server.py:197-208` / `212-227` |
| 4 | `block` | `server.py:239` | 6 | `server.py:246-255` / `259-276` |
| 5 | `annotation` | `server.py:288` | 6 | `server.py:295-304` / `308-330` |
| 6 | `pid` | `server.py:342` | 12 | `server.py:349-364` / `368-406` |
| 7 | `view` | `server.py:418` | 3 | `server.py:427-433` / `436-451` |
| 8 | `system` | `server.py:461` | 6 | `server.py:468-477` / `480-517` |
| | **合计** | **8 个** | **72** | 10+21+8+6+6+12+3+6 |（来源：各分项见上表逐行的 `server.py:N`）

- 「8」有三处独立印证：模块 docstring「8 consolidated tools with operation dispatch」（`server.py:1-3`）、README 同名表（`README.md:12`）、装饰器计数 8。
- 分派分支只有 **71 支**而不是 72 支——`system` 里 `status` 与 `get_backend` 共用一支（`server.py:480`，`if operation == "status" or operation == "get_backend"`）。**计数差 1 的来源就在这一行**。
- **契约不一致**：7 个工具把所有参数塞进 `data: dict | None`，只有 `entity` 额外摊平了 **7 个顶层参数**（`x1,y1,x2,y2,points,layer,entity_id`，`server.py:92-98`），且其中 `points/layer/entity_id` 并不是坐标。⇒ 同一个"合并式"约定在 `entity` 上破了例。
- **工具数与后端方法数的比例**：`base.py` 72 个 `def`，去掉 5 个样板（`to_dict/name/capabilities/initialize/status`）得 **67 个能力方法**（`backends/base.py` 全文）；file_ipc 实现 **67 个**，ezdxf 实现 **61 个**。⇒ **8 个工具 / 72 操作 / 67 后端方法 / 2 个实现**。
- **两层命令表严格对齐**：file_ipc 的 `self._dispatch("<名>")` 名字集（67 个）与 LISP 的 `cmd-name` 分支集（67 支，`lisp-code/mcp_dispatch.lsp:172` 起的 `cond`）**双向零差**（本地集合比较，两侧各缺 0）。这是它能用 8 个工具撑 72 个操作的结构原因：**Python 只是转发，真实现全在 LISP 那 67 支里**。
- **能力用布尔声明**：`BackendCapabilities` 10 个开关（`backends/base.py:27-40`）；file_ipc 全 `True`（`backends/file_ipc.py:70-83`），ezdxf 有 4 个 `False`（`can_plot_pdf/can_zoom/can_undo` 及截图以外的项，`backends/ezdxf_backend.py:34-46`）。

### 3.2 其余机制

| 机制 | 怎么做的 | 证据 |
|---|---|---|
| **同一 API 双后端** | 抽象基类 + 自动探测；探测失败降级（`auto` → 先 file_ipc 后 ezdxf）| `backends/base.py:43-53`、`client.py:27-59`（`get_backend` 双检锁）|
| **逐操作 × 逐后端支持矩阵** | README 用表格写清每个操作在哪条后端可用（哪些是 File IPC only、哪些 ezdxf 不支持）| `README.md:96-107`（drawing）、`README.md:125-132`（block）|
| **错误 → 可执行提示** | 异常按关键词转成 `hint`（窗口没找到 / 超时按 ESC / 后端不支持 / 调度器没加载）| `client.py:77-93` |
| **单通道串行** | `asyncio.Lock` 保证同时只有一条命令在飞，避免 IPC 文件互相覆盖 | `file_ipc.py:64`、`file_ipc.py:135-138` |
| **原子写 + 请求号校验** | `.tmp` 写完后改名；结果文件按 `request_id` 比对，不匹配继续等 | `file_ipc.py:150-158`、`file_ipc.py:176-181` |
| **旁路观测** | 每个工具一个 `include_screenshot` 开关，开了就把 PNG 追加到结果里 | `server.py:80`、`client.py:149-163` |
| **自由代码逃生口** | `system(operation="execute_lisp")` 执行任意 AutoLISP，把固定命令集变成可扩展平台 | `server.py:512-517`、`README.md:158` |

## 4. 运行条件与依赖

- **file_ipc 后端**：Windows 10/11 + **AutoCAD LT 2024 或更新**（AutoLISP 从 LT 2024 Windows 才有；LT for Mac 无 AutoLISP）+ Windows 原生 Python（不是 WSL Python）（`README.md:14-18`）；LISP 调度器须用 APPLOAD 加载 `mcp_dispatch.lsp`（`README.md:33-40`）。
- **ezdxf 后端**：任意平台、**不需要 AutoCAD**（`README.md:21`）。
- 依赖（`pyproject.toml`）：`mcp[cli]>=1.2.1,<2.0`、`ezdxf>=0.18`、`matplotlib>=3.7`、`Pillow>=10.0.0`、`structlog>=24.0.0`、`pywin32>=305`（仅 win32）；`requires-python = ">=3.10"`。
- 本机（Windows / Python 3.14.7 / RTX 4080S 16GB）：**ezdxf 后端能跑，file_ipc 不能**。① 实测 `import ezdxf` → 1.4.4，`import mcp` 成功，Python 3.14.7（本地探测）；② `C:\Program Files\Autodesk` 不存在、注册表无 `HKLM:\SOFTWARE\Autodesk\AutoCAD`（本地探测）⇒ 没有 AutoCAD LT 可驱动；③ `C:\PIDv4-CTO` 不存在 ⇒ 12 个 `pid` 操作即便装上 AutoCAD 也用不了（见 §5 第 6 条）。（来源：本机实测；软失败位置 `mcp_dispatch.lsp:338`）
- ★ **但它的自带测试在本机跑不起来**（2026-10-23 实测，Python 3.14.7）：`python -m pytest tests -q -p no:cacheprovider`（`PYTHONPATH` 指向 `src`）**在收集阶段就中断**——`tests/test_ezdxf_backend.py` 与 `tests/test_screenshot.py` 都报 `ModuleNotFoundError: No module named 'structlog'`；只跑 `tests/test_ipc_protocol.py` 则得 **38 个 error**，根因全是 `PytestUnknownMarkWarning: Unknown pytest.mark.asyncio`（缺 `pytest-asyncio`）。⇒ **零测试通过**，故本卡对 8 个工具 / 72 个操作 / 双后端的全部结论都只有读码证据。
- 这是两家样本里**唯一本机能真跑**的一家：因为它把"不需要宿主"当第一等公民（双后端），Blender 则把宿主当唯一执行面。

## 5. 失败模式与已知坑

| # | 问题 | 证据 |
|---|---|---|
| 1 | IPC 默认超时 **10 s**，可调 1–300；模态对话框会把它耗死，而错误提示只说「按下 ESC 再重试」| `README.md:182`、`client.py:84-85` |
| 2 | **静默丢弃 None 参数**：发之前剔掉所有 None，注释写「LISP 的简易 JSON 解析器吃不了 null」⇒ 无法表达"显式置空"这种语义 | `file_ipc.py:148-149` |
| 3 | LISP 写结果是 Windows-1252，读取先 UTF-8 再退 cp1252；两边都失败就静默重试到超时 | `file_ipc.py:168-173`、`file_ipc.py:182-183` |
| 4 | **`block-define` 双层不一致**：Python 侧照发（`file_ipc.py:422-423`），LISP 侧直接回 `"block-define not available via IPC (use ezdxf backend)"`（`mcp_dispatch.lsp:386-387`）⇒ README 写「File IPC: No」（`README.md:132`）是对的，但这个限制**没有对应能力标志位**，只有运行时才撞到 | `file_ipc.py:422-423`、`mcp_dispatch.lsp:386-387` |
| 5 | **P&ID 依赖仓库外的符号库**：目录硬编码 `C:/PIDv4-CTO/`（`mcp_dispatch.lsp:1216`），缺 `pid_tools.lsp` 时 12 个 pid 操作全部回 `"pid_tools.lsp not loaded"`（`mcp_dispatch.lsp:338`、`mcp_dispatch.lsp:672` 等 10 处）⇒ 裸机上整族软失败 | `mcp_dispatch.lsp:338,672,1216` |
| 6 | **ezdxf 少 6 个方法**：`drawing_plot_pdf / undo / redo / execute_lisp / zoom_extents / zoom_window`，调用时落到基类默认 `"Not supported on this backend"`（逐个对应 `backends/base.py:81-82`、`92-93`、`95-96`、`100-101`、`274-275`、`277-278`）。而 README 的 `view` 表**没有后端列**（`README.md:144-152`），只有 drawing/block 两张表有 ⇒ 照 README 读会以为 `zoom_*` 两边都行 | 本地集合比对；`base.py:81-82,92-96,100-101,274-278`、`README.md:144-152` |
| 7 | 版本号三处不一致：`pyproject.toml` 写 `3.0.0`，README 标题「v3.1」（`README.md:208`），运行时日志发 `version="3.1.0"`（`server.py:549`）| 三处并列 |
| 8 | `view` 没有 `include_screenshot` 参数（`server.py:420-426`），与其余 7 个工具形态不一致；它把截图做成第 3 个操作 `get_screenshot` | `server.py:420-426` |
| 9 | 缺 key 时报 `KeyError`，只能靠 `_safe` 兜成「带 hint 的错误」，因为逐操作 schema 不在 JSON Schema 里 ⇒ 参数错**只能在调用时**发现 | `client.py:101-116` |
| 10 | LT 不支持 `vlax-*`（ActiveX/COM）（`README.md:198-204`）⇒ 整条链路被锁在 AutoLISP 文件 IPC 上，没有 COM 兜底 | `README.md:198-204` |

## 6. 对我方目标的可用处（机制层面）

1. **8 个工具装 72 个操作的可行条件**：Python 只做转发，真实现集中在**一层命令表**里（67 支 LISP），且 Python 侧的命令名集与 LISP 侧**严格同构**（本地比对零差）。⇒ 合并式工具不靠"大 if 链"维持，靠**两侧同一份命令名**。这让"72 个操作"只花 8 个 schema。（来源：本卡 §3.1 命令表对齐结论）
2. **合并的代价被文档化**：逐操作参数写进 docstring（`server.py:102-130` 是 29 行），JSON Schema 只有 `operation: str` + `data: object`。⇒ 选中工具变容易，**填对参数变难**；这是我方评估"529 → 少数合并工具"时必须计的一笔账，它被写在这里而不是被藏起来。
3. **能力声明 + 远端拒绝的分层**：`BackendCapabilities` 布尔在**入口**声明，`block-define` 的拒绝在**远端**（LISP）发生——两者没打通，于是出现"声明支持、运行才失败"。反面教材：能力标志位应覆盖拒结点。
4. **逐操作 × 逐后端支持矩阵表**（`README.md:96-107`）：把"哪个操作在哪条后端可用"做成表格，是合并式工具**必须**配的东西；它漏了 `view` 那张表就立刻出现 §5 第 6 条那种误读。
5. **错误 → 可执行提示**的映射表（`client.py:77-93`）：4 类高频失败各有固定 hint（超时让你按 ESC、调度器没加载给你 load 命令）。对普通模型，这比抛原始异常有用得多。
6. **不抢焦点的 IPC**：`PostMessageW(WM_CHAR)` + 文件交换，使自动化能与用户并行操作同一台机器（`README.md:174`）——一种"人机共处同一宿主"的编排形态，不靠加锁独占 GUI。
7. **旁路观测**：`include_screenshot` 作为每个工具的独立开关，等于把"看一眼"做成可选的后置动作，而不是每步强制截图。

## 7. 许可与红线

- MIT（`LICENSE:3`，`Copyright (c) 2024 AutoCAD MCP Server Contributors`）：可读、可抄、可改、可商用，**义务只有保留版权声明**。
- **红线一**：`pid` 那 12 个操作背后的符号库是**第三方商业库**（CAD Tools Online，须装在 `C:\PIDv4-CTO\`，`README.md:142` + `mcp_dispatch.lsp:1216`），**不在本仓 MIT 覆盖范围内** ⇒ 只能借 P&ID 的**分派形态**，不得把 CTO 符号当自有资产复制。
- **红线二**：`execute_lisp` 是任意 AutoLISP 执行（`README.md:158`），无沙箱、无 AST 校验（对比 Blender 有 opt-in 校验，本仓完全没有）。这种能力不得原样进入我方交付路径。
- **红线三**：`lisp-code/mcp_dispatch.lsp` 50788 字节、`attribute_tools.lsp` 15170 字节（本地 `Get-ChildItem`），是 LISP 方言实现，与本方 COM 后端**语言层不同构** ⇒ 借机制不借代码。

## 8. 证据清单

- `LICENSE:3`（MIT + 版权行）；`pyproject.toml`（版本 3.0.0、`requires-python`、依赖、mcp `<2.0`）
- `README.md:12`（8 consolidated tools）、`README.md:14-21`（双后端前置）、`README.md:33-40`（APPLOAD）、`README.md:96-107`/`125-132`（逐后端矩阵）、`README.md:142`（CTO 库）、`README.md:144-158`（view / system）、`README.md:168-174`（PostMessageW）、`README.md:182`（超时）、`README.md:198-208`（LT 限制 / v3.1）
- `src/autocad_mcp/server.py:1-3`（8 consolidated 说明）、`server.py:33,88,190,239,288,342,418,461`（8 个 `@mcp.tool`）、`server.py:92-100`（entity 破例的 8 个顶层参数）、`server.py:480`（status/get_backend 共用一支）、`server.py:512-517`（execute_lisp）、`server.py:549`（version 3.1.0）
- `src/autocad_mcp/client.py:27-59`（双检锁单例）、`client.py:77-93`（hint 映射）、`client.py:101-116`（`_safe`）、`client.py:149-163`（截图旁路）
- `src/autocad_mcp/backends/base.py:10-24`（CommandResult）、`base.py:27-40`（10 个能力布尔）、`base.py:206-212`（不支持默认值）
- `src/autocad_mcp/backends/file_ipc.py:64,135-194`（单通道 + 原子写 + 请求号 + 编码回退）、`file_ipc.py:70-83`（能力全 true）、`file_ipc.py:422-423`（block_define 照发）
- `src/autocad_mcp/backends/ezdxf_backend.py:34-52`（能力 4 false + 内存文档）
- `lisp-code/mcp_dispatch.lsp:172`（cond 起点）、`:338`（pid setup 缺库）、`:386-387`（block-define 拒绝）、`:672`（pid 缺库）、`:1216`（`C:/PIDv4-CTO/`）
- `gh api repos/puran-water/autocad-mcp`（591 stars / 2026-02-20T17:36:20Z / Python，取数 2026-10-24）；`git remote -v`（同址）
- 本地统计：`tests/` 3 个测试文件、`def test_` 共 123 处（76+38+9）；`backends/` 三个文件 282/497/748 行；`mcp_dispatch.lsp` 1378 行
- ★ 本机实测（2026-10-23，Python 3.14.7）：`python -m pytest tests -q -p no:cacheprovider`（`PYTHONPATH` 指向 `src`）→ 收集中断（`structlog` 缺失，`tests/test_ezdxf_backend.py`、`tests/test_screenshot.py`）；单跑 `tests/test_ipc_protocol.py` → 38 error（`pytest.mark.asyncio` 未注册，缺 `pytest-asyncio`）

## 9. 未确认事项

1. **72 / 67 / 71 这三个数是静态计数**，我没有启动服务、没有真的调 `tools/list`，也没有跑 `uv sync`；`block-define` 的实际拒绝文本是从 LISP 源码读的，未实测。
2. **file_ipc 在真机上的行为**（击键是否被 AutoCAD 吃下、`_find_command_line_hwnd` 在 LT 2024 各版本是否都能找到控件）——本机无 AutoCAD，**无法验证**；`file_ipc.py:196-199` 在找不到时会返回 `None` 并回退到别的路由，那条回退路的实际效果我未读透。
3. **`pid` 族的 12 个操作在装好 CTO 库后能否全部跑通**——LISP 里 10 处 `pid_tools.lsp not loaded` 只是"库没装"的判断，库装上后 `c:insert-pid-block` 等外部函数的实际行为属第三方，查不到。（来源：本卡 §9 未确认事项）
4. **ezdxf 后端与 file_ipc 的输出是否等价**（同一条命令两边画出来的实体是否一致）——测试只覆盖各自后端（`tests/test_ezdxf_backend.py` 76 例、`tests/test_ipc_protocol.py` 38 例），**没有跨后端对等性测试**，我未确认这一点。
5. **8 个工具这个数字的来历**——`README.md:208-220` 的 v3.1 变更日志只讲新增操作，没讲"从多少个工具收敛到 8"；仓库是浅克隆（`git log` 只 1 条），无法从历史确认前身形态。

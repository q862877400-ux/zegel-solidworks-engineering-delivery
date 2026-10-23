# build123d-mcp

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/pzfreo/build123d-mcp （PyPI：https://pypi.org/project/build123d-mcp/ ；API 里 `"homepage": ""`） |
| 许可 | Apache-2.0（读克隆内 `LICENSE` 原文首行「Apache License / Version 2.0, January 2004」；`pyproject.toml:11` 写 `license = { file = "LICENSE" }`）→ **可借鉴**（保留版权声明、声明改动文件，NOTICE 义务随分发走） |
| 元数据 | stars 126 · 最近推送 2026-10-15T20:57:23Z · 语言 Python（来源：https://api.github.com/repos/pzfreo/build123d-mcp ，取数日 2026-10-23）；克隆版本号 `0.3.92.dev0`（`pyproject.toml:7`） |
| 克隆 | D:\ai3d-survey\repos\pzfreo__build123d-mcp （HEAD `59b25612`，末次提交 2026-10-15T20:57:21Z，工作树干净） |
| 证据等级 | 读码 |

## 1. 一句话定位

把 build123d 包成 **MCP 工具箱的服务端**（作者明确说它不是 chatbot 也不是 CAD 程序）：让 AI 应用"一次建一个特征、每步量测/渲染/校验、合格才导出"，卖点是给 AI 补**眼睛**——量测、几何门禁、失败定位（`README.md:14-23`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：MCP 工具调用。三条生成入口——`execute(code)` 增量建、`execute_file(path)` 用规范源文件整体重建、`import_cad_file(path)` 导入 STEP/STL 做比较（`server.py:362-386`、`server.py:1094-1101`）。
2. **中间表示**：常驻会话里的**命名对象**（`show(shape, "name")` 注册并立即打印体积与面数）+ 一个当前 shape；快照（`save_snapshot`/`restore_snapshot`）是几何检查点，不是源码状态（`server.py:363-364`、`server.py:1169-1175`、`server.py:895-913`）。
3. **生成**：模型自己写的 build123d 代码在受限命名空间里执行；`execute()` 里还能直接调分析原语（`measure`/`clearance`/`cross_sections`/`find_holes`/`find_bosses`/`align_check`…）并**把结果当 Python 对象继续组合**，而不是把 JSON 数字抄出来（`server.py:364`）。
4. **编排**：三种运行形态（默认 stdio、HTTP、`--in-process` 降级，`cli.py:151-157`、`cli.py:141-150`）；工具面可裁剪（`--tools` 白名单、`--disable-tool-groups`、无库时自动隐藏库工具、实验工具默认不注册，`server.py:555-594`、`cli.py:213-234`）；`install_skill(target=...)` 把工作流技能写进 `.claude/skills`、`AGENTS.md`、`.cursor/rules`、`.windsurfrules`（`server.py:1465-1487`）。
5. **执行**：父进程（MCP server）通过 Pipe 代理一个常驻 **worker 子进程**（spawn），真正的会话与沙箱都在 worker 里（`worker.py:454-458`、`worker.py:529-548`、`worker.py:124-181`）；单次调用有 `--exec-timeout`，默认 120 秒（`cli.py:134-140`）。
6. **验证**：`validate()` 是一道"能不能交付"的门（返回 `passes_gate`/`n_solids`/`volume`/`is_manifold`/`brep_valid`/`reasons`，`server.py:431-434`）；失败后用 `locate_gate_defects()` 拿**带坐标**的缺陷清单（BRep 无效面、开边、非流形边、非流形顶点、无法三角化面、顶点偏移缺陷），每条带诊断类与下一步（`server.py:437-440`）。
7. **交付**：`export(filename, format, object_name)` 支持 STEP/STL/DXF/SVG；`execute_file()` 返回源文件 SHA-256 溯源并"原子提升"结果（`server.py:372-386`、`tools/execute_file.py:15-42`、`README.md:286`）。

## 3. 技术方案要点（可迁移的机制）

- **把"验证权威"钉在服务端**：modeling 技能第一句就是"以 build123d-mcp 为执行与验证权威"，工作流是服务端给的，不靠模型自觉（`src/build123d_mcp/skills/b123d-modeling/SKILL.md:7-15`）。
- **目测排在量测之后**：`workflow_hints()` 明写"先 `measure()` 再 `render_view()`；数字无歧义，渲染看着对也可能错"（`server.py:1146-1149`）。
- **布尔的判据是拓扑计数**：任何 cut/union/intersection 之后必须看 `topology.faces` 是否变化，没变就是失败（`server.py:1159-1162`、`server.py:427`）。
- **失败即分类即改法**：`execute()` 失败时附 `repair_hints` 命中项 + 一个 JSON（`failure_class` + `suggested_fix`，如 `boolean_fail`/`selector_empty`/`shapelist_attr`/`fillet_fail`/`timeout`/`import_blocked`/`call_blocked`）（`tools/execute.py:6-46`、`tools/execute.py:49-94`）。
- **崩溃/超时不是死局，但要说清代价**：父进程保留 `execute()` 历史，worker 被 SIGKILL/超时后重启并**重放**历史重建会话；作者反复标注"重放≠还原"——快照与 `import_cad_file`/`load_part` 的几何不回来、非确定性步骤可能重放出不同结果（`worker.py:500-508`、`worker.py:629-707`）。
- **增量修设计而不是整脚本重画**：`execute_file()` 在干净命名空间跑，语法/运行错误、超时、没产出或没产出指定名字时**原子保留**上一个有效模型（`server.py:372-386`、`tools/execute_file.py:45-68`）。
- **"有效形状 ≠ 可编辑的设计"可审计**：`design_audit()` 解析顶层数值参数，在硬有界子进程里把每个参数 ±10% 重建并过 gate，把脆参数标 `brittle`，并说明"派生参数不会被列出"这一已知局限（`server.py:445-448`）。
- **知识以 MCP resource 按需取**：`build123d://quickref`、`//selectors`、`//bd_warehouse`、`//presentation`、`//session-state`、`//drafting-api`，以及四份工作流技能本身作为 resource（`server.py:1276-1349`、`server.py:1417-1462`）。
- **同一份规范多面落地**：`install_skill(target=claude|agents-md|cursor|windsurf)` + MCP prompt `start-cad-session`（把十条工作流提醒做成 prompt 模板）+ `default_prompt.md` 手工系统提示（`server.py:1465-1487`、`server.py:1490-1532`、`README.md:311-312`）。
- **工具按风险标注、按上下文裁剪**：装饰器带 `_READ_ONLY`/`_MUTATING`/`_IDEMPOTENT`/`_DESTRUCTIVE`，并支持按部署裁掉整组（`server.py:362`、`server.py:926-941`、`server.py:555-594`）。
- **静默的知识缺口会被显式声明**：`design_audit` 说明只识别字面量参数；`verify_spec` 说明 `material_at_point`/`wall_thickness_at` 是"frame-dependent、不可跨重定位移植"（`server.py:448`、`server.py:457-458`）。
- **源码即交付物的溯源**：`execute_file()` 只接受 UTF-8 `.py`，默认 2 MiB 上限（可用 `BUILD123D_MAX_SCRIPT_BYTES` 调），读到 `max_bytes + 1` 以防 stat 后被撑大，返回 SHA-256（`tools/execute_file.py:12-42`）。
- **架构决策留档**：`docs/adr/` 下三份 ADR——worker IPC 并发、worker 子进程崩溃隔离、HTTP 会话句柄（`docs/adr/0001-worker-ipc-concurrency.md`、`docs/adr/0002-worker-subprocess-crash-containment.md`、`docs/adr/0003-http-cad-session-handles.md`）。
- **标准件不许手搓**：工作流明写螺纹/紧固件/齿轮/轴承直接用 `bd_warehouse`（随服务一起装），写脚本前要先探测该目录里某标准的可用尺寸清单，并用库提供的沉头孔/攻丝孔/间隙孔/沉孔类去配紧固件对象，"绝不算头型与底孔直径"（`server.py:1200-1209`）。
- **失败的一步不该毁掉整场会话**：`execute()` 的 120 秒只限单次调用，超时只丢这一步、会话由历史重建，所以第一步是"改小/分段"而不是离开 MCP 去写 Bash（`server.py:1210-1221`）。

## 4. 运行条件与依赖

- 语言：Python `>=3.11,<3.15`，classifier 明列 3.11/3.12/3.13/3.14（`pyproject.toml:10`、`pyproject.toml:14-19`），README 也写 3.11–3.14 支持（`README.md:67-69`）。
- 依赖重且都带理由：`mcp>=2,<3`、`build123d>=0.10,<0.14`、`vtk>=9.3`、`bd_warehouse`、`resvg-py`、`build123d-drafting-helpers>=0.10.0`、`quiddity>=0.3.11,<0.4`、`defusedxml>=0.7.1`、`augura>=0.1.8`、`scipy`、`pillow`；HTTP 模式另需 `uvicorn`（`pyproject.toml:23-52`）。
- 本机判断（Windows + 默认 Python 3.14.7，另有 uv 管理的 3.10.21/3.12.14；用 `python -c "importlib.util.find_spec(...)"` 实测 `build123d`/`OCP`/`vtk` 均为 False）：**原则上能跑**——正常用法不需要克隆，`uv tool run --python 3.12 build123d-mcp@latest` 即可（`README.md:53-58`）；但 OCP/build123d 是否已发布 cp314 的 Windows wheel **未确认**，本次未安装、未运行。
- Windows 专属限制：`--memory-limit-mb`/`--cpu-limit-s` 走 POSIX rlimit，Windows 无效（`cli.py:193-212`、`worker.py:167-168`）；live viewer 的 Unix socket 也是 POSIX only（`cli.py:236-244`）；宿主拦子进程时（作者记 Windows 沙箱宿主曾出现）要退到 `--in-process`，代价是没有崩溃隔离与操作超时（`worker.py:559-564`、`cli.py:141-150`）。
- GPU：无要求（VTK 渲染 + OCC 网格都是 CPU 侧；依赖表里没有任何加速器包，`pyproject.toml:23-49`）。

## 5. 失败模式与已知坑

- **沙箱不是完整沙箱**：AST 层只挡常见逃逸路径（dunder 访问、`getattr`/`vars`），`inspect.getmembers()` 仍可绕、ctypes 与 C 扩展不设限——作者把这个作为已知局限写在模块头（`security.py:1-16`、`security.py:70-74`）。
- **HTTP 模式无内建认证且默认共享同一 CAD 会话**，README 直接写"不要多用户直接暴露"（`README.md:351-353`）。
- **宿主不允许 fork 会让全部操作退化**：连续超时计数就是用来区分"宿主拦子进程"与"这一次真的慢"（`worker.py:514-521`），启动失败时给出 `--in-process` 的明确提示（`worker.py:559-564`）。
- **恢复是重放不是还原**：历史重放有总预算，超预算保留已重建的前缀；若重放到一半又挂，前缀一起丢、退成空会话（`worker.py:629-666`、`worker.py:689-706`）。
- **工具语义会误导自治代理**：`verify_spec` 因 `conforms: true` 会被代理读成"停止信号"，于是默认不注册（`server.py:451-456`）——这是"给模型看的结果要有入场券"的实例。
- **重活有界化**：`locate_gate_defects` 明确说会 out-of-process，巨大零件返回干净的预算错误而不是挂住；网格门禁另有 `_GATE_MESH_BUDGET_S = 35.0` 与 15 秒余量、10 秒下限（`server.py:439`、`validate.py:74-81`）。
- **依赖代际被显式约束**：`constraint-dependencies = ["cadquery-ocp-novtk!=7.9.3.1.1"]`，因为那个 macOS wheel 缺 `OCP.GccEnt` 会让 build123d 直接 import 失败（`pyproject.toml:55-61`）；跨 build123d 0.12/0.13 还需要 quiddity/augura 的新下限（`CHANGELOG.md:5-12`）。
- **遗留问题密度不低**：仓库现有 61 个 open issues（来源：https://api.github.com/repos/pzfreo/build123d-mcp ，计数，未逐条读）。
- 绘制工具正在迁出：本仓的 2D 绘图工具已标 DEPRECATED，0.4.0 起默认关、0.5.0 移除，交给外部 `draftwright`（`server.py:471-478`、`server.py:1250-1251`）。
- **导入物的语义差异会被点名**：STL 导入得到的是 shell（`volume=0`），渲染与量测可用，但 `compare(kind="fit")` 与布尔运算要求 solid（`server.py:1253-1258`）。
- **多会话只在 HTTP 下存在，且成本按子进程算**：`--max-sessions` 默认 1（所有请求共享），带 `Mcp-Cad-Session` 头的请求才拿到独立会话与 worker；空闲 3600 秒回收，每会话是"数百 MB 的 OCC 子进程"（`cli.py:171-192`）。

## 6. 对我方目标的可用处（机制层面）

- **"服务端当验证权威 + 门禁 + 失败定位"与我们同构**：合格判据放在服务端（gate + 带坐标的缺陷清单），模型只负责改脚本（`server.py:431-440`）。
- **失败 → 分类 → 改法 三元组**是让普通模型自纠的关键，可直接搬到我们的 COM 失败处置：错误信息里就带 `suggested_fix` 与 repair hints（`tools/execute.py:6-46`）。
- **"有效形状 ≠ 可编辑设计"（±10% 参数扰动 + gate）**是我们做 SolidWorks 参数化规范时的现成判据，尤其能抓"薄壁/坐标推理"类脆设计（`server.py:445-448`）。
- **技能以 MCP resource 暴露 + `install_skill` 落到四个代理生态**，是"一份规范多面生效"的现成实现（`server.py:1417-1487`）。
- **会话韧性（超时/崩溃后重放历史）**对无人值守的 SolidWorks 自动化特别值钱；照搬时务必带上它那句 caveat"重放≠还原、快照不回来"（`worker.py:629-707`）。
- **风险标注（read-only / mutating / destructive）**可搬到我们的工具清单，防止代理误触危险操作（`server.py:926-941`）。
- **有界化模板**：单次调用超时 + 危险/重活在子进程算 + 内存/CPU 上限（POSIX）+ "超预算给干净错误"（`cli.py:134-140`、`validate.py:74-101`）。
- **ADR 留档习惯**可直接借鉴：三份 ADR 写清了"为什么 worker 子进程、为什么崩溃隔离、为什么 HTTP 会话句柄"（`docs/adr/0001-worker-ipc-concurrency.md`）。

## 7. 许可与红线

- Apache-2.0：可读、可抄、可改、可商用；义务是保留版权声明、注明改动文件、NOTICE 随分发（`LICENSE` 原文 + `pyproject.toml:11`）。
- 它引的一长串第三方（VTK/OCP/scipy/quiddity/augura/bd_warehouse/resvg-py…）各有自己的许可，搬运时不能只看本仓 LICENSE（`pyproject.toml:23-49`）。
- 红线：本次对克隆**只读**（未改任何文件）；**不搬克隆内的 `mcp-publisher` 可执行文件**（19,632,290 字节，来源与哈希未核，见 §9）。

## 8. 证据清单

```
D:\ai3d-survey\repos\pzfreo__build123d-mcp\README.md:14-23,25-27,53-58,67-69,171-194,286,298-312,351-353
...\pyproject.toml:7,10,11,14-19,23-52,55-61,69 · CHANGELOG.md:5-12
...\src\build123d_mcp\server.py:362-386,389-448,451-458,471-478,520-594,689-700,895-941,1094-1101,1135-1273,1276-1462
...\src\build123d_mcp\worker.py:124-181,454-548,500-508,514-521,559-566,629-707
...\src\build123d_mcp\cli.py:125-150,151-157,193-244 · security.py:1-16,30-77,70-74,83-161,319-355,365-398,436-488
...\src\build123d_mcp\tools\execute.py:6-46,49-94 · tools\execute_file.py:12-68
...\src\build123d_mcp\validate.py:74-101,352,1414 · session.py:63,744
...\src\build123d_mcp\skills\b123d-modeling\SKILL.md:7-15 · docs\adr\0001-worker-ipc-concurrency.md
```
- 计数实测（在克隆内跑 `pwsh`）：`src/build123d_mcp/server.py` 有 50 处 `@mcp.tool`、11 处 `@mcp.resource`、1 处 `@mcp.prompt`；`tests/` 68 个 `test_*.py`；`skills/` 下 4 份 `SKILL.md`；`docs/adr/` 3 份 ADR。
- 元数据来源：https://api.github.com/repos/pzfreo/build123d-mcp （取数 2026-10-23）。

## 9. 未确认事项

- 未安装、未运行（本机默认 Python 3.14.7，`build123d`/`OCP`/`vtk` 实测未安装）；本卡所有行为结论来自读码，等级为 `读码`。
- 本机 Windows + Python 3.14 下是否有可用的 OCP/build123d wheel **未确认**（未查 PyPI 的 wheel 标签）；已知可用的保守路线是 `uv` 拉 3.12。
- README 的效果数字（0.360→0.457、validity 88%→100%，2026-06 公共榜）是作者自述并给了外链，未独立复现（`README.md:25-27`）。
- 61 个 open issues 只取了计数，未逐条读内容（来源：https://api.github.com/repos/pzfreo/build123d-mcp ），因此"已知坑"清单可能不全。
- 克隆内 `mcp-publisher` 可执行文件（19,632,290 字节）的来源、哈希、是否与 PyPI 包同源 **未核**（来源：克隆内 `Get-ChildItem` 实测）。
- 工具/技能对普通模型的实际行为（是否真按 measure→render 顺序走、`install_skill` 落地后的触发率）未做端到端实验。
- `security.md`、`research.md`、`llms.md`、`SPEC.md`、`docs/live-viewer.md` 只按需取了引用处，未逐份通读。
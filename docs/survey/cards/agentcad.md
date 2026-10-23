# agentcad

<!-- survey: class=B; repr=code; orchestration=loop; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/jdilla1277/agentcad · 主页 https://agentcad.dev |
| 许可 | Apache-2.0（读克隆内 `LICENSE` 原文首行「Apache License / Version 2.0, January 2004」；`pyproject.toml:11` 写 `license = "Apache-2.0"`）→ **可借鉴**（保留版权声明、声明改动文件；Apache 的 NOTICE 义务随分发走） |
| 元数据 | stars 172 · 最近推送 2026-10-23T10:32:03Z · 语言 Python（来源：https://api.github.com/repos/jdilla1277/agentcad ，取数日 2026-10-23） |
| 克隆 | D:\ai3d-survey\repos\jdilla1277__agentcad （HEAD `52af472d`，末次提交 2026-10-23T06:09:26-04:00，`git status --porcelain` 为空） |
| 证据等级 | 读码 |

## 1. 一句话定位

给编码代理用的**本地 CAD CLI + MCP 服务器**：代理写 build123d 脚本，agentcad 负责执行、STEP/网格导出、PNG 渲染、量测、校验与版本化交付；每条命令的最终响应是 stdout 上的结构化 JSON（`README.md:5`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：CLI 或 MCP 调用 + 一个 Python CAD 脚本。脚本零 import——build123d 基元、`show_object` 与编辑 helper 由 runner 预注入（`README.md:209-214`）；也可把既有 STEP 当输入读（`inspect`/`measure`/`render`，`README.md:92-101`）。
2. **中间表示**：脚本**不自己导出 STEP**；`show_object(result)` 把形状交回 AgentCAD，由它写并跟踪 canonical STEP，真实路径从响应的 `outputs.step` 读（`guide.py:126-134`）。捕获回调用 `contextvars.ContextVar` 传递，因此并发脚本的 `show_object` 不会串味（`api.py:8-11`、`api.py:44-51`）。
3. **生成**：稳定编写面是 `agentcad.api`（`load_step`/`safe_cut`/`safe_fuse`/`safe_intersection`/`bbox_point`/`translate`/`boss`/`cut_pocket`… 共 34 个导出名字，`api.py:19-41`、`api.py:190-226`）。
4. **编排**：`run` 先做**执行前静态校验**（拒绝可识别的手写 STEP writer、要求至少一次 `show_object`，`guide.py:131-134`、`validate.py:30`）；再选 runtime（`--runtime` > 项目固化 > 源码探测 > 默认，`commands/run.py:1473-1497`）；命中守护进程则改由守护进程执行（`commands/run.py:1413-1435`）。
5. **执行**：常驻守护进程把 OCP 留在内存，每个 run `fork` 一个子进程处理单次请求后退出——换来崩溃隔离，且 `sys.modules`/cwd/env 每次都从零开始（`daemon.py:1-26`）。
6. **验证**：分层报告，gate 层依次 `file_parse → kernel_load → brep_check → shell_closure → mesh_manifold`，另有非 gate 的 `structure`/`advisory`（`validation.py:99-108`）；两个 profile：`deliverable`（全 gate）与 `kernel`（有意曲面/片体用，跳过 shell/mesh，`validation.py:113-117`）。顶层 `metrics.is_valid` 就是 BRepCheck_Analyzer 的结论（`metrics.py:122-126`）。
7. **交付**：版本目录 `vN_label/`；版本号在锁目录保护下预留，`meta.json` 与 `agentcad.json` 用临时文件 + `os.replace` 原子写（`versioning.py:38-58`、`versioning.py:112-133`、`versioning.py:136-168`）；同轮产出 preview、diff、viewer。
8. **交付后的复核面**：viewer 服务只绑 `127.0.0.1`、只服务已注册的快照、URL 是"本地书签"而非分享链接；端口被占会直接报错而不是偷偷换 URL（`README.md:196-205`）。

## 3. 技术方案要点（可迁移的机制）

- **指南单源多面渲染 + 内容哈希指纹**：`guide.py` 是唯一真源，Claude Code 的 SKILL.md 与 AGENTS.md/CLAUDE.md 的 marker 块都由 `guide_body()` 渲染；`guide_fingerprint()` 是内容哈希（不是手改版本号），所以"装了旧指南"是机器可检出的事实（`guide.py:1-12`、`commands/skill.py:66-76`）。写进指令文件的是**完整指南正文**而非指针，理由写在文件头：AGENTS.md 会被无条件加载，skill 与 `--help` 只在代理愿意读时才生效（`commands/instructions.py:1-8`）。
- **stdout 只放 JSON、心跳走 stderr**：进度行带耗时前缀，避免调用方用 `2>&1` 把 JSON 解析搞坏（`README.md:7`、`commands/run.py:1403-1410`）。
- **MCP 协议流隔离**：stdio 起转前先 `os.dup(1)` 私存协议 fd、再把 fd 1 指向 stderr，CAD 子进程/OCCT 直写 fd 1 也污染不了 JSON-RPC（`mcp/server.py:16-29`）；Click 吞掉异常导致空输出时，把异常类型、消息与 traceback 一并回传（`mcp/server.py:31-66`）。
- **分层 gate + `first_failure`**：失败可命名到层、可定位到实体（自由边 ID、网格缺陷位置），而不是一句 invalid（`validation.py:99-108`）。
- **诊断与修复分离**：`diagnostic_guidance()` 把"尚未确定"显式写出（如 shell 闭合失败不能断定是缺面还是面不连通，`validation_guidance.py:57-104`）；`repair_guidance()` 给的是"可能修复"，每条自带 precondition 且 `applicability` 标成 `unverified`（`validation_guidance.py:107-119`）。
- **显式结构意图**：`show_object(part, options={"expect_solids": 1})`，意图在捕获时就校验类型，不合法立即报错（在昂贵导出之前，`validation_guidance.py:8-22`、`guide.py:104-106`）。
- **精确/近似两段比较 + 预算**：exact 3D 有 30 秒默认 worker 预算，超时保留 exact 失败并跑有界体素回退，回退结果标 `method=approximate_voxel_volume` 且误差声明为启发式（`guide.py:207-218`）。
- **大活外包给 worker 进程**：验证超过 `VALIDATION_WORKER_MIN_BYTES = 1_000_000` 字节即走 out-of-process；网格 manifold 用 `DEFLECTION_LADDER = (1, 4, 16, 32)`、上限 `MAX_TRIANGLES = 1_000_000` 的有界阶梯（`validation.py:48`、`validation.py:584-585`）。
- **只在能被机器读的地方下断言**：`export` 成功只表示文件写了，网格要各自看 `mesh_validation.<format>.is_valid`，STEP 结论不认证 STL/GLB/OBJ（`guide.py:255-260`）。
- **重复捕获是硬错误**：同一 shape 跨 `show_object` 调用重复捕获报 `error_kind: "duplicate_capture"`，故意多实例必须 deepcopy（`README.md:227-234`）。
- **人在环上的反馈落成本地 JSON**：空间评论写进选定 build root 的 `.agentcad/reviews`（无数据库、无托管账号），代理下一轮靠 `context` 与 `review list --status open` 发现，评论不自动触发新 run（`README.md:154-177`）。
- **精度陷阱显式处理**：包围盒用 `BRepBndLib.AddOptimal_s` 而非 `Add_s`——后者按 NURBS 控制点算，会把尺寸算虚大，注释记了 CADGenBench 203 叶轮 586.7 报值 vs 360 实际（`metrics.py:52-63`）。
- **反馈线程有状态机**：评论可 reply/resolve/reopen，每条记 actor、时间戳、消息与所属版本；候选侧消失的部件其评论保留为 unplaced（`README.md:165-170`、`README.md:174-176`）。
- **运行期的选择依据要回传**：响应里用 `runtime_source`（`command`/`project`/`detection`）说明这次用的哪个 CAD API（`README.md:277-279`）。

## 4. 运行条件与依赖

- 语言：Python **3.10–3.12**；`requires-python = ">=3.10,<3.13"`（`pyproject.toml:10`），运行时另有一道显式拒绝：版本 ≥3.13 直接报错退出（`commands/run.py:1460-1470`）。
- 核心依赖（每条都带"为什么锁"的注释）：`click>=8`、`build123d>=0.10,<0.11`、`cadquery-ocp>=7.8,<7.9`、`ocp_gordon<0.3`（`pyproject.toml:23-44`）。
- 可选 extra：`[mcp]` = `mcp>=1.0,<2`；`[cadquery]` 会引入 CadQuery 及其 CasADi/COIN-OR 链，Windows 另锁 `casadi<3.8`（`pyproject.toml:47-60`）。
- 本机判断（Windows + 默认 Python 3.14.7，另有 uv 管理的 3.10.21 与 3.12.14；用 `python -c "importlib.util.find_spec(...)"` 实测 `build123d`/`cadquery`/`OCP` 均为 False）：**默认解释器必然跑不动**（被 3.13 上限挡下），要用 3.12.14 建 venv 再装；本次**未安装、未运行**，故本卡为读码级。
- GPU：无要求（渲染与网格校验是 CPU 侧 OCP 路径，`pyproject.toml:23-44` 无任何加速器依赖）。

## 5. 失败模式与已知坑

- 两套 OCP 同路径会让 `import build123d` 直接死：注释写明 build123d 0.11 换 `cadquery-ocp-novtk`(OCP 7.9) 与 cadquery extra 锁的 7.8 冲突，报 `TopoDS has no attribute 'Vertex'`（`pyproject.toml:26-31`）。
- `ocp_gordon>=0.3` 会 import OCP 8 模块并拉进第二代 OCP，使每次 `agentcad run` 报 `No module named 'OCP.collections'`，故锁 `<0.3`（`pyproject.toml:37-44`）。
- Windows 上 CadQuery 的 CasADi 3.8 abi3 wheel 在原生栈关闭时非零退出，连 `pytest --collect-only` 都会坏（`pyproject.toml:55-59`）。
- 测试曾整体 wedge：注释记 PR #194 之后两次 pytest 因泄漏的子进程守护卡死 23+ 分钟，于是加了每测试硬超时 120 秒（`pyproject.toml:84-92`）。
- 守护进程版本漂移：父进程内存在启动时冻结，`pip install --upgrade` 后必须 `agentcad daemon restart`（`daemon.py:19-25`）。
- 守护进程静默/丢失时返回 `outcome: "unknown"` 且 `retry_safe: false`——不要盲目重试，原命令可能已经完成（`guide.py:220-225`）。
- "成功"的语义被反复拆开：`status: success` 只表示比较跑了，`passed` 才是 spec 检查结果（`guide.py:279-282`）；导出成功只表示写了文件（`guide.py:300-301`）。
- runtime 混用会被**前置**拒绝：同一脚本混用 build123d 与 CadQuery 的导入，在 daemon 启动或建版本之前就被拒，并给出"改脚本还是显式覆盖 runtime"的指引（`README.md:273-276`）。
- `--no-view` 不保证不产 viewer 产物——只要已经有一个打开的工程页，产物照样送过去；要纯核心路径必须同时 `--no-preview --no-diff --no-view`（`README.md:191-194`）。

## 6. 对我方目标的可用处（机制层面）

- **"指南唯一真源 + 指纹防漂移"可直接照搬**：SolidWorks 规范只维护一份，渲染到 SKILL 与 AGENTS 两个消费面，指纹让"装了旧版指南"变成可检出的机器事实（`commands/instructions.py:1-8`、`commands/skill.py:66-76`）。
- **执行前静态门禁**（禁自写导出、必须显式交付调用）正是我们"脚本不许绕过交付口"的现成形状（`guide.py:126-134`）。
- **分层 gate + first_failure + 未确定项显式化**可做我们五级验证等级的骨架，从结构上防止把"没跑"写成"通过"（`validation.py:99-108`、`validation_guidance.py:57-104`）。
- **预注入兜底算子**（`safe_cut`/`safe_fuse`/`safe_intersection`/`bbox_point`…）是给普通模型准备的"安全默认手"，直接压缩乱布尔造成的失败面（`api.py:19-41`）。
- **"修复建议必须自带 precondition 且标 unverified"**这条纪律可原样搬进我们的失败处置指引（`validation_guidance.py:107-119`）。
- **结构化响应里带 `suggestion`/`next_actions`**（如脚本不可读时）让代理能自纠，不必等人翻译报错（`commands/run.py:1477-1486`）。
- MCP 只暴露 11 个工具（`run`/`render`/`export`/`measure`/`inspect`/`check_spec`/`docs`/`context`/`recover`/`diff`/`view`）——"工具面窄、语义重"的样板（`mcp/server.py:93-388`）。

## 7. 许可与红线

- Apache-2.0：可读、可抄、可改、可商用；义务是保留版权声明、注明改动文件，NOTICE 义务随分发走（`pyproject.toml:11` 与克隆内 `LICENSE` 原文）。
- 第三方许可面被主动缩小：默认安装只带 OpenCascade 绑定，CasADi/COIN-OR 移进可选 extra 并单列许可说明（`pyproject.toml:47-52`）。
- 我方红线：本次对克隆**只读**（`git status --porcelain` 为空，未改其任何文件）；搬运其文本要保留版权声明与来源。

## 8. 证据清单

```
D:\ai3d-survey\repos\jdilla1277__agentcad\README.md:5,7,9,19-23,78,92-101,154-177,209-214,227-234,299
...\pyproject.toml:10,11,23-44,47-60,84-92
...\src\agentcad\guide.py:1-12,51-60,104-106,126-134,207-218,220-225,255-260,279-282,300-301
...\src\agentcad\api.py:8-11,19-41,44-51,190-226
...\src\agentcad\validation.py:48,99-108,113-117,584-585
...\src\agentcad\validation_guidance.py:8-22,57-104,107-119
...\src\agentcad\metrics.py:52-63,122-126
...\src\agentcad\versioning.py:38-58,112-133,136-168
...\src\agentcad\commands\run.py:1403-1410,1413-1435,1460-1470,1473-1497,1477-1486
...\src\agentcad\commands\skill.py:66-76 · commands\instructions.py:1-8
...\src\agentcad\daemon.py:1-26 · validate.py:30 · mcp\server.py:16-29,31-66,93-388
```
- 计数实测（在克隆内跑 `pwsh`）：`tests/` 98 个 `.py`、`tests_b3d/` 12 个 `.py`、`mcp/server.py` 11 处 `@mcp.tool`、`docs/` 只有 5 个文件（全在 `docs/product-plans/` 下）。
- 元数据来源：https://api.github.com/repos/jdilla1277/agentcad （取数 2026-10-23）。

## 9. 未确认事项

- 未安装、未运行 agentcad（本机默认 Python 3.14.7 被项目自身的 3.13 上限挡下），所有运行期结论来自读码；本卡的"实测"只到"本机有哪些 Python 与包是否存在"这一层。
- 仓库自述的效果数字（48% higher CAD Score、21.8% lower cost、2.5× valid outputs）未独立复现，作者自己也写明那是单次 run、不是匹配基线的对照（`README.md:19-23`、`README.md:26-30`）。
- 未核 `docs/product-plans/` 之外（如 https://agentcad.dev ）的线上文档与本仓库版本是否一致。
- `--build-dir` 各种配置下的版本目录落点未逐个跑验证，只读了 `versioning.py` 的实现。
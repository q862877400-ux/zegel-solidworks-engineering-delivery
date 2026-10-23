# OpenSCAD-MCP-Server（jhacksman）

<!-- survey: class=H; repr=dsl; orchestration=single; verify=run-only; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/jhacksman/OpenSCAD-MCP-Server |
| 许可 | MIT（`LICENSE:1-3`，`Copyright (c) 2026 Jack Hacksman`；`pyproject.toml:10` 亦写 `license = "MIT"`）⇒ **可借鉴**，移植须保留版权声明 |
| 元数据 | stars 208 · forks 32 · open issues 2 · 最近推送 2026-09-07T12:38:57Z · 语言 Python · 默认分支 `main`（来源：`gh api repos/jhacksman/OpenSCAD-MCP-Server`，2026-10-24 取）|
| 克隆 | `D:\ai3d-survey\repos\jhacksman__OpenSCAD-MCP-Server`（shallow：`git rev-list --count HEAD` 得 1，tip `b35ade55`，提交时间 2026-09-07 05:38:54 -0700；体积 1 MB，来源：`Get-ChildItem -Recurse -File | Measure-Object Length -Sum` 实测 2026-10-24）|
| 证据等级 | **读码**（非「实测」：本机无 OpenSCAD——`Get-Command openscad` 空、`C:\Program Files\OpenSCAD` 不存在，实测 2026-10-24；作者自己在 macOS 上跑过 59 个测试，读数见 §5，那是**他的**实测，不是我的）|

## 1. 一句话定位

**把「显式参数 + 模板」当唯一正路、把 SCAD 源码当唯一可编辑真源**的本地 MCP 服务：11 个基本体由模板 + 参数表生成 SCAD（`src/openscad_mcp/geometry.py:7-63`），复杂形状才让模型写 SCAD（`create_model_from_scad`，`src/openscad_mcp/server.py:42-44`），每次写盘都跑真 OpenSCAD 输出 STL + 四张 PNG。

`class=H`（代理本地 OpenSCAD CLI）；`repr=dsl`——中间表示就是 SCAD 源码文本，工具只是它的生成器/编辑器。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：8 个 MCP 工具（7 个在 `server.py:91-99` 的 `functions` 列表里，第 8 个 `get_model_preview` 单独注册于 `server.py:106`）。两条入口：`create_3d_model(model_type, parameters)` 走参数表，或 `create_model_from_scad(scad_code)` 走源码。描述文本只是**可选的窄语法糖**，解析器是手写正则，不是模型（`geometry.py:148-242`）。

**中间表示**：SCAD 源码 + 一个参数字典。生成函数把参数逐行写成 `key = value;` 再拼模板体（`geometry.py:114-120`），这样产出的 SCAD **脱离服务器也能编译**（`docs/audit.md` 的验证项里明写「exported SCAD compiles from a different directory without template files」）。

**生成**：模板表 `BODIES`（`geometry.py:39-63`）。11 个模板的构造方式是**显式写出来的 CSG**：`box` = 外立方减内立方（`geometry.py:43-47`）、`rounded_box` = 8 个球取 hull（`geometry.py:48-51`）、`tube` = 双圆柱差（`geometry.py:52-56`）、`torus` = rotate_extrude（`geometry.py:58-59`）……

**编排**：无。每个工具调用是一次同步渲染，循环在客户端（`orchestration=single`）。

**执行**：子进程跑 `openscad`（`engine.py:41-59`），渲染进**同分区的临时目录**再 `os.replace` 原子落位（`engine.py:72-93`）；超时默认 120 秒可配（`server.py:225-228`）。

**验证**：三层。① **把非零退出与 stderr 里的 `ERROR|WARNING:` 关键字都当失败**——注释点明「有些 OpenSCAD 版本即使断言失败也返回 0」（`engine.py:55-58`）；② 产物非空 + PNG 魔数校验（`engine.py:87-92`）；③ 编辑采用**乐观并发**：`modify_3d_model` 收 `expected_revision`，版本不符抛冲突并回 409 + `current_revision`（`service.py:20-25,130-141`；`server.py:143-148`），失败的编辑不落盘、旧 revision 保持可用（`service.py:64-86` 的 `try/except → rmtree`）。

**交付**：每次构建产出 `model.scad` + `model.stl` + 四视角 PNG（`service.py:67-72`）到 `revision` 子目录；`export_model` 支持 `scad|stl|csg|3mf`（`engine.py:16`；`service.py:170-184`），HTTP 侧另有 `/download/{id}` 与预览页（`server.py:185-208`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**8 个工具，切法是「模型的生命周期」而不是「建模命令」**（来源：本卡 §8 证据清单）

| # | 工具 | 生命周期位置 | 定义 |
|---|---|---|---|
| 1 | `get_capabilities` | 探路 | `server.py:80-89` |
| 2 | `create_3d_model` | 建（模板口径） | `server.py:32-40` |
| 3 | `create_model_from_scad` | 建（源码口径） | `server.py:42-44` |
| 4 | `modify_3d_model` | 改 | `server.py:46-61` |
| 5 | `get_model` | 读元数据 | `server.py:67-69` |
| 6 | `get_model_source` | 读源码 + revision | `server.py:71-73` |
| 7 | `get_model_preview` | 看（返回真 PNG 图像块） | `server.py:75-78` |
| 8 | `export_model` | 落格式 | `server.py:63-65` |

粒度判据是**「一次调用是否产生一个新 revision」**：2/3/4 产生（`service.py:64-86`、`:139-141`、`:152-154`），其余只读或旁路导出。⇒ 8 个工具里 3 个写、5 个读，写工具全都走同一条 `_build()` 落盘路径。

### 3.2 参数表与「宁可拒答不许猜」

- **11 个基本体 + 每体的默认值表**是唯一可编辑面（`geometry.py:7-37`）：`cube/sphere/cylinder/box/rounded_box/tube/cone/torus/prism/hexagonal_prism/text`。
- 参数校验是**逐键写成 if 链**而不是 JSON Schema：布尔只认 `bool`、`segments` 只认 12–256 的整数、数值必须有限正数且 ≤ 10000 mm，另加**几何自洽判据**——`box` 的壁厚必须留下内腔、`rounded_box` 的圆角不得超最小边之半、`tube` 内径必须小于外径、`torus` 小径必须小于大径（`geometry.py:66-111`）。
- **四个固定视角当验收通道**：`perspective / front / top / right` 四条相机串写死在表里（`engine.py:10-15`），渲染统一 `--render --autocenter --viewall --imgsize=800,600`（`engine.py:76-84`）⇒ 同一模型两次构建的图**可直接对比**，这是它唯一的「看图验收」基础。
- **描述解析器只在能确定时动手**：认不出的数字一律报错（`geometry.py:235-241`「Dimensions were not understood. Name each parameter…」）；一句里出现两个形状、或出现 `hole|cutout|union|difference` 这类复合语义，直接要求改用 `create_model_from_scad`（`geometry.py:161-176`）；单位支持 mm/cm/m/inch，`ft` 明确拒绝（`geometry.py:136-144,153-154`）。

⇒ **「普通模型最容易在这里出错」的一点被设计成硬失败**：含糊就拒，不猜。

### 3.3 三处克制（都可直接搬）

- **不做图像→模型**：旧仓库的 SAM2/CUDA/三视图重建全部归档，MCP 说明里明写 `No image reconstruction or implicit AI generation`（`server.py:43`；`README.md:5`）。能力面收窄到「能证明对」的那一段。
- **不做隐式补全**：`create_3d_model` 的描述字段只是便利入口，服务在 `model_type` 为空且解析不出唯一形状时**报错而不是猜**（`geometry.py:173-176`）。
- **不做静默失败**：渲染失败 `service.py:81-85` 会把整个 revision 目录删掉并回滚 `model.json`，调用方拿到的要么是完整一套产物，要么是空。

## 4. 运行条件与依赖

- Python ≥ 3.11（`pyproject.toml:12`）；运行时只有 3 个直接依赖 `mcp` / `fastapi` / `uvicorn`（`pyproject.toml:13`）。无 CUDA、无 GPU、无 Open3D（`README.md:9`）。
- 必须装 **OpenSCAD 可执行文件**：顺序是 `OPENSCAD_EXECUTABLE` 环境变量 → `PATH` 里的 `openscad` → 两个 macOS `.app` 固定路径（`engine.py:24-38`）；启动时先跑 `--version` 探活，失败就 `parser.exit(1, …)`（`server.py:230-235`）。
- 传输：默认 stdio；`--transport http` 起 `127.0.0.1:8000`，MCP 端点是 `/mcp`（`server.py:216-241`；`README.md:57-60`）。HTTP 侧有 `TrustedHostMiddleware`（只允许 localhost/127.0.0.1/[::1]）+ 只放行本地 Origin（`server.py:115-137`）。
- **本机（Windows / Py3.14.7 / RTX 4080S 16GB）能不能跑**：**不能**，缺 OpenSCAD 可执行文件（§表「证据等级」）。补上之后理论上能——纯 Python、无 GPU、无模型权重；但 Python 3.14 是否被 `mcp` 的发布轮子覆盖**未验证**（只声明 `>=3.11`，无上限）。Linux 无显示时 PNG 渲染另需 Xvfb（`README.md:18`）。

## 5. 失败模式与已知坑

- **`legacy/` 是一整片废墟**：旧实现（图像生成、CUDA 重建、远程处理、打印机发现）全部归档、不属安装包（`README.md:5`）。作者自己的审计把它判成「无法支撑其宣传的端到端流程」，逐条列了启动失败、假输出（「CUDA converter writes a single hardcoded triangle」）、虚构重建、导出承诺失实等（`docs/audit.md:5-22`）。⇒ 读这个仓库**必须先确认自己读的是 `src/openscad_mcp/`**，`legacy/` 里 70 个文件的思路不能当实现（`git ls-files legacy` 计数，2026-10-24）。
- **回归靠作者自测**：`docs/audit.md:35` 记 `pytest -q` 59 通过 / 54.19 秒；`docs/audit.md:56` 记 Ubuntu 24.04 CI 同样 59 个在 Xvfb 下 14.71 秒。这些是**作者机器的读数**，我本机无 OpenSCAD 未复现。
- **零退出的错误**：注释明写「有些版本连断言失败都返回 exit 0」，所以判失败靠 stderr 关键字（`engine.py:56-58`）。代价是**任何 `WARNING:` 也会让整次渲染失败**——一个非致命的警告会表现为「渲染失败」。
- **无锁的多进程**：只有进程内 `threading.RLock`（`service.py:33-34`），同一个输出目录被两个进程同时写没有保护；作者在 `docs/audit.md:56` 也只声明「One server process owns an output directory」。
- **SCAD 是可信代码**：`create_model_from_scad` 直接交给 OpenSCAD（含 `import`/`surface` 之类能读文件的模块），工具描述里明写「executes trusted SCAD with the current user's filesystem access」（`server.py:29`）。
- **`/tool_call` 是遗留的 REST 面**，与 MCP 并存（`server.py:176-183`）；`docs/audit.md:14` 说旧的私有 HTTP dispatcher 已被真 MCP 替代，但这个兼容端还在。
- **AMF 明确不承诺**：原生 OpenSCAD 2026.09.05 直接拒 `.amf`（「Invalid suffix amf」），作者选择不宣传而不是兜底（`docs/audit.md:20`）；`export_model` 的合法格式只有 `scad|stl|csg|3mf`（`engine.py:16`）。
- **PNG 渲染依赖图形栈**：Linux 无 X 显示要 `xvfb-run`（`README.md:18`），否则四视图这条验证通道整体不可用。

## 6. 对我方目标的可用处（机制层面，含边界）

1. **「revise-not-overwrite」的模型存储**：每个 revision 一个不可变目录，`model.json` 用临时文件 + `os.replace` 原子替换（`service.py:47-57,64-86`）。这直接对上我方「参数化模型必须可回滚、可对比」的要求——改坏了旧版本还在。
2. **`expected_revision` 的乐观并发**：模型必须**先读再写**（`get_model_source` 拿 revision 才能改），过期写被 409 拒掉（`server.py:143-148`）。这比我方「按名字覆盖」更安全，可用来防「模型拿着旧状态盲目改」。
3. **「拒答优于猜」的判据可搬**：① 未消化的数字 → 报错；② 一句两个形状 → 报错；③ 出现复合操作词 → 要求换源码通道（`geometry.py:161-176,235-241`）。普通模型最常见的失败就是「悄悄按自己的理解补参数」，这套判据把它变成显式失败。
4. **参数级几何自洽校验**（壁厚留腔、圆角不超半、内径小于外径）是**在渲染之前**就能判的 DFM 规则雏形（`geometry.py:98-110`），比我方「建完再看」早了整整一步。
5. **失败判据兜住「零退出码」**：不能只看 returncode（`engine.py:55-58`）。这条对我方 COM 侧尤其对——`FeatureExtrusion` 返回非 NULL 也可能是空特征。
6. **边界一**：它**没有几何数值验证**。运行时只查「产物存在、非空、PNG 魔数」（`engine.py:87-92`）；「水密 / 体积对不对 / 面数与解析值差多少」这类检查只存在于**测试与人工审计**（`docs/audit.md:48` 的 1,052 三角形、60 × 40 × 6 mm、体积 13,722.5055 mm³ 对解析值 13,721.4160 mm³ 差 0.00794%），不是工具返回值。
7. **边界二**：`repr=dsl` 的代价——SCAD 里没有「特征树」，改一个孔就得改源码文本；它的 `modify_3d_model` 在参数口径下能保住其他尺寸（`service.py:146-151`），一旦落到 `custom` 就只能整段替换源码（`service.py:134-143`）。
8. **边界三**：模板只有 11 个，覆盖的是「基本体 + 薄壁盒 + 圆角盒 + 管 + 锥 + 环 + 棱柱 + 文字」，任何真实零件都要走源码通道；这跟我方 SolidWorks 特征树不是一个量级的表达能力。（来源：本卡 §8 证据清单）

## 7. 许可与红线

- MIT（`LICENSE:1-3`，`Copyright (c) 2026 Jack Hacksman`）⇒ 可读、可抄、可改、可商用，须保留版权声明。`pyproject.toml:10` 与 `LICENSE` 一致，无第二种许可。
- 红线：`create_model_from_scad` 是**以用户权限跑任意 SCAD**（`server.py:29` 的 instructions 原文承认），`import`/`surface` 能读本机文件。移植须自带白名单或沙箱。
- 克隆仓库只读，未改动任何文件（未跑测试，故未在仓内产生 `__pycache__`）。

## 8. 证据清单

- `LICENSE:1-3`；`pyproject.toml:10,12-13`；`README.md:5,9,18,57-60`
- `src/openscad_mcp/server.py:24-30,32-78,80-89,91-106,115-137,139-156,176-183,185-208,216-241`
- `src/openscad_mcp/geometry.py:7-37,39-63,66-111,114-120,136-144,148-176,235-241`
- `src/openscad_mcp/engine.py:10-16,24-38,41-59,72-93`
- `src/openscad_mcp/service.py:20-25,28-34,47-57,64-86,122-154,170-184`
- `docs/audit.md:5-22,35,48,56`
- https://github.com/jhacksman/OpenSCAD-MCP-Server（`gh api` 元数据，2026-10-24）

## 9. 未确认事项

1. 8 个工具的运行期 `tools/list` 未验（本机无 OpenSCAD，服务起不来：启动即 `--version` 探活并 `exit 1`，`server.py:230-235`）。
2. `docs/audit.md` 的 59 通过 / 54.19 秒、0.00794% 体积差、1,052 三角形都是**作者的读数**，我未复现；也未在 Windows 上跑过。
3. Python 3.14.7 与 `mcp>=1.12,<2` 的兼容性未验（`pyproject.toml:12-13` 只给下限）。
4. `/tool_call` 遗留 REST 面在 `docs/audit.md` 之后是否还有客户端在用，未查。
5. `legacy/` 下 70 个文件只抽读了 `docs/audit.md` 对它们的判决，未逐个读码（本卡结论不依赖它们）。

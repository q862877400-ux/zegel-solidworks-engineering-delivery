# muerus/SolidWorks-Python

<!-- survey: class=H; repr=code; orchestration=single; verify=run-only; deliver=none; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `muerus/SolidWorks-Python` · https://github.com/muerus/SolidWorks-Python |
| 许可 | **MIT**（`LICENSE:1-3` = `MIT License` / `Copyright (c) 2026 muerus`；README 徽章 `license-MIT`）⇒ 可读可抄可商用，保留版权声明 |
| 元数据 | stars 9 · forks 0 · 语言 Python（50 个 `.py`）+ C#（21 个 `.cs`）· 仓库 615 KB · 建档 2026-10-06 · 最近推送 2026-10-09（来源：`gh api repos/muerus/SolidWorks-Python`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\muerus__SolidWorks-Python`（`--depth 1`）|
| 证据等级 | **实测**（限纯 Python 层：`PYTHONPATH=python python -m pytest tests` ⇒ **31 passed / 1 failed / 169 errors**；169 个 error 全是 `FileNotFoundError`——它们要一个活的 SOLIDWORKS 宿主；**SolidWorks 未跑**，建模能力结论止步 `source`）+ 读码 |

## 1. 一句话定位

**技术路线与本批其他家正交的一家：它不跨进程连 COM，而是把 CPython 嵌进 SolidWorks 进程里**，于是「单源 COM」问题被架构本身消掉；对外用 `swpy.client` 的 `eval`/`exec` 让 Jupyter/Excel/脚本把代码送进来执行，对内给一套 Pythonic API（`model.dims["D1@Boss-Extrude1"] = 25 * mm`、可链式过滤的 `model.faces.planar().normal(Z).largest()`、`with model.batch():` 一次重建）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：三种——① Task Pane 里的 Python 编辑器（带补全与参数提示，`src/SwPy.AddIn/Ui/CodeEditor.cs` 47256 字节 + `EditorPane.cs` 38527 字节）；② 外部客户端 `swpy.client`（`sw.eval`/`sw.exec`/`sw.run`，`docs/guide/07-remote-control.md`）；③ 普通 `.py` 脚本由 `python/swpy/_host.py` 起宿主。

**中间表示**：**没有几何 IR，中间表示是 Python 代码**；但它有一层「Pythonic 外壳」：`model` 对象把 COM 的 `D1@Boss-Extrude1` 这类名字、单位、质量属性、面/边查询包装成 Python 属性与链式查询（`python/swpy/model.py` 21152 字节、`props.py` 8782、`build.py` 9636、`events.py` 9780）。

**生成**：不生成代码（它**就是**代码环境）。`# r: openpyxl` 这类注释可在运行时按需 `pip install` 包（`docs/guide/06-packages.md`）。

**编排**：无编排层；单次调用一次执行。外部客户端是「送一段代码进去、拿回结果」的同步模型（`sw.run` 回 `ok`/`stdout`/`result`/`value`/`error`，`07-remote-control.md` 的表）。

**执行**：**进程内**。C# add-in（`src/SwPy.AddIn/SwPyAddIn.cs` 11711 字节）把 CPython 嵌进来，`Scripting/Libraries.g.cs`（155463 字节）与 `Cast.g.cs`（93917 字节）是生成出来的桥接层；`python/swpy/com.py`（12887 字节）负责 COM 调用。

**验证**：**弱**。可读回 `model.mass["mass"]`、`model.dims[...]`、`model.features()`，但**没有断言层、没有回滚**；`docs/guide/12-building-models.md`（6741 字节）讲建模流程，不是验收判据。

**交付**：不内置导出工具——直接用 SolidWorks 的 `SaveAs`（`docs/guide/05-solidworks-api.md:81-84` 给了 VBA→Python 的 `SaveAs` 对照，含 `swSaveAsVersion_e` / `swSaveAsOptions_e` 枚举用法）。⇒ 交付能力「有但没有自己的封装」，故本卡标 `deliver=none`。

## 3. 技术方案要点（可迁移的机制）

### 3.1 架构层面的「单源 COM 互斥」：把 COM 所有者做成唯一宿主

`docs/guide/07-remote-control.md` 的模型是：**代码被送到 SolidWorks 进程内执行**，外部客户端只 `pywin32` + `swpy` 包路径即可（`swc.connect()` 附着并加载 add-in）。⇒ 与 MCP 的「每个工具调用跨进程」相反：**跨进程的只有「代码字符串 + 结果」**，COM 永远只有一个所有者。

这解释了它为什么在 615 KB 的小体量里没有死锁问题：**问题被架构消掉了，不是被解决了**。对我方的启示是：如果哪天真要根治「多 MCP 抢 COM」，让所有客户端把代码/请求投给**一个驻留宿主**是唯一结构性的解法（MCP 也可以这么做——把 MCP 服务端做成「宿主内的一个 TCP/stdio 前端」）。（`docs/guide/07-remote-control.md`）

### 3.2 可链式过滤的几何查询（对「持久引用」的第三种答案）

`docs/guide/04-model-api.md:167-190`：`model.faces` / `model.edges` 返回**查询对象**（不是列表快照），可链式过滤：

| 方法 | 语义 |
|---|---|
| `faces.planar()` / `faces.cylindrical()` | 平面 / 圆柱面 |
| `faces.normal(direction, tol=1e-6)` | 外法向沿某方向 |
| `faces.radius(r, tol=1e-9)` | 半径匹配的圆柱面 |
| `faces.area(lo, hi)` | 面积区间（m²）|
| `faces.planar().largest()` | 面积最大者 |

用法示例（README 首屏）：`model.faces.planar().normal(Z).largest().select()`。

⇒ 与本批另外三家的对比：hjbaard 用「方向 + 点」、HarrierPigeon 用「描述谓词 + 面积序」、soheil-mp 用「谓词 + **命中数断言**」、SwPy 用「**链式过滤 + 末端 select()**」。四家都**不存拓扑 ID**，都用「现算」。**差别只在「选错时会发生什么」**：soheil-mp 会报 ambiguous 并给候选；SwPy/hjbaard 会选中「最符合条件的那个」并继续（可能选错）。⇒ 我方取舍时应选 soheil-mp 那一档（**要求断言命中数**），把链式过滤当**表达手段**而不是判据。

### 3.3 `with model.batch():` —— 把「静音 UI + 单次重建」做成上下文管理器

`python/swpy/model.py:434-445`：`batch(rebuild=True)` 进入时关掉视图/特征树更新，退出时**只重建一次**；`_changed()` 在 batch 深度 >0 时只置脏标记，不逐次重建。⇒ 与 hjbaard 的 `_quiet_ui`（`sw-hjbaard-solidworks-mcp.md` §3.3）同一个机制，但**做成了语言级的上下文管理器**：调用方不必记得「开了要关」。

⇒ 我方若要给批量建模降耗，这是最干净的形状（`with` 块 + 一次 `ForceRebuild3`），并且它天然自带「异常时也恢复」的语义。

### 3.4 单位用「单位对象」而不是后缀

`25 * mm`、`120 * mm`（README 首屏）。⇒ 与我方「形参名带 `_mm` 后缀」是两种解法：**后缀靠约定，单位对象靠类型**。后者更强（乘错就抛），但要求整个 API 都接受 `Quantity`；前者零成本但会被绕过。**可迁移的是「至少让 API 里出现一个显式单位乘法入口」**，作为后缀约定的补充。

### 3.5 自带「VBA → Python」对照表

`docs/guide/05-solidworks-api.md`（10743 字节）是一份逐行对照：例如 `bRet = swModel.Extension.SaveAs(path, 0, 1, Nothing, lErrors, lWarnings)` ↔ `ok, errors, warnings = doc.Extension.SaveAs(path, 0, 1, None, 0, 0)`（`:192`）。⇒ 我方 `docs/` 若要做「官方示例（VBA/CHM）→ 我方工具」的映射，这是现成的格式样本；也直接印证我方铁律「`[in,out]` 参数在 Python 侧变成返回值的一部分」。

## 4. 运行条件与依赖

- Windows x64 + **SOLIDWORKS 2020+**（README 徽章）；**Python 3.12**（README 徽章，指嵌入式运行时版本）。
- 安装：`INSTALL.txt` + `pyproject.toml`；add-in 注册后从 Task Pane 打开编辑器。
- 外部客户端：只需 `pywin32` + 把 `python` 目录加进 `sys.path`（`07-remote-control.md`）。
- 测试：16 个文件（`test_model.py`/`test_props.py`/`test_com.py`/`test_editor.py`/`test_pane.py`/`test_host.py`/`test_packages.py`/`test_libraries.py`/`test_events.py`/`test_ui.py`/`test_docs.py`/`test_build.py`/`test_client.py`/`test_static.py` + `conftest.py`/`harness.py`），**实测 31 passed / 1 failed / 169 errors**（2026-11-02，Python 3.14.7）——error 全是 `FileNotFoundError`，因为 `tests/conftest.py` 的 session fixture 会**启动 SOLIDWORKS 并加载 add-in**（`harness.SwPy()`）。

## 5. 失败模式与已知坑

1. **宿主依赖极强**：169/201 个用例在本机直接 `FileNotFoundError` ⇒ **离线不可测**，回归只能靠装了 SolidWorks 的机器。（`tests/conftest.py` 的 session fixture）
2. **Python 版本钉死 3.12**（嵌入式运行时），而本机 3.14.7 能跑纯逻辑但跑不了宿主层。
3. **没有验证层**：读回靠调用方自觉；写错也不会有断言拦。
4. **vendored COM 绑定体积大**：`python/swpy/swconst.py` 330034 字节、`libs/swcommands.py` 146403、`libs/cosworks.py` 120809 —— 这些是从类型库生成的常量/接口镜像，**与 SolidWorks 版本强绑定**（升级 SW 需重生成）。
5. **进程内嵌 CPython 的崩溃面**：任何 Python 侧的段错误都会带走 SolidWorks 进程（这是进程内方案的固有代价）。
6. **`# r: openpyxl` 式按需装包**：运行时装包意味着**代码执行面 = 任意 pip 包**，安全边界要自己想清楚。
7. **交付无封装**：导出要自己写 `SaveAs`，容易踩 `SaveAs3` 返回错误码而非 bool 的坑（对照 `sw-infei12306-solidworks-bridge.md` §3.3）。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **不解，绕行**：链式几何过滤现算，末端 `select()`；**不校验命中数**（选错不会报） | `docs/guide/04-model-api.md:167-190` |
| 回读验证 | **弱**：能读 `model.mass`/`model.dims`/`model.features()`，无断言、无回滚 | `python/swpy/model.py`、`docs/guide/12-building-models.md` |
| 事务式建模 | **部分**：`with model.batch():` 合并改动 + 单次重建（不是回滚） | `python/swpy/model.py:434-445` |
| 单源 COM 互斥 | **架构性消解**：进程内嵌 CPython，外部客户端只送代码进来 ⇒ COM 所有者唯一 | `docs/guide/07-remote-control.md` |

**Q3 答**：**库 + 进程内宿主**（不是 MCP 服务端、不是 CLI）；工具面 **0 个工具**（对外是 Python API + `eval`/`exec` 通道）；粒度 = **一个 Pythonic API 面**（对象属性 + 链式查询 + 上下文管理器），本质是「万能代码口」但**有类型化的外壳**。（`docs/guide/07-remote-control.md`）

**能学（按性价比排序）**：
1. **「COM 所有者唯一」的架构解法**（宿主内执行 + 外部只送代码/请求）：这是我方「单源 COM 互斥」最根本的答案，MCP 形态也能套（服务端作为宿主的前端）。
2. **`with model.batch():` 上下文管理器**：静音 UI + 一次重建，异常也恢复。
3. **链式几何查询的表达力**（`planar().normal(Z).largest()`）：作为选择器**表达手段**值得抄；但**必须叠加 soheil-mp 的命中数断言**才安全。
4. **单位对象（`25 * mm`）**：作为「形参名带 `_mm` 后缀」的补充，能在 API 入口强制单位。
5. **VBA → Python 对照表的格式**（`docs/guide/05-solidworks-api.md`）：把官方 CHM 示例翻译成我方调用形态的现成模板。
6. **`sw.eval`/`sw.exec`/`sw.run` 三档返回**（值 / 打印文本 / 完整结果 dict）：外部控制通道的返回设计样本。

**不能学**：
- **进程内嵌 CPython**：崩溃即带走 SolidWorks，且版本钉死；对我方「无人值守」目标是风险。
- **无命中数断言的链式选择**：`largest()` 永远能选出「一个」，这是最危险的静默选错形态。
- **运行时装 pip 包**：安全边界失控。
- **离线不可测**：169/201 用例在本机直接报错，回归成本高。

## 7. 许可与红线

**MIT**（`LICENSE:1-3`，`Copyright (c) 2026 muerus`）。可移植，义务：保留版权声明。★ 移植 `batch()` 的形状、链式查询 API、`swpy.client` 的三档返回设计时，来源头写 `muerus/SolidWorks-Python（MIT，LICENSE:3）` + 改动说明。★ 注意：`python/swpy/swconst.py` 等是从 SolidWorks 类型库生成的常量镜像——**Dassault 的类型库内容本身可能有许可约束**，不要直接把这些生成物搬进我方仓库，应自己从本机类型库重生成。

## 8. 证据清单

- `README.md`（首屏 API 示例：`with model.batch():`、`model.dims[...] = 25 * mm`、`model.faces.planar().normal(Z).largest().select()`、`model.mass["mass"]`、`# r: openpyxl`；徽章：Windows x64 / SOLIDWORKS 2020+ / Python 3.12 / MIT）
- `docs/guide/04-model-api.md:167-190`（`model.faces`/`model.edges` 是**查询对象**，可链式过滤；`planar`/`cylindrical`/`normal`/`radius`/`area`/`largest` 逐条语义）· `docs/guide/07-remote-control.md:1-30`（`swc.connect` / `sw.eval` / `sw.exec` / `sw.run` / `sw.reset` / `sw.version`；错误以 `swc.SwPyError` + 远端 traceback 抛回）· `docs/guide/05-solidworks-api.md:81-84,192`（VBA↔Python 的 `SaveAs` 对照）· `docs/guide/06-packages.md`（按需装包）· `docs/guide/12-building-models.md`（建模流程，非验收判据）
- `python/swpy/model.py:434-445`（`batch()`：进入时停视图/特征树更新，退出单次重建；`_changed()` 在 batch 内只置脏）· `python/swpy/com.py`（12887 字节）· `python/swpy/props.py`（8782）· `python/swpy/build.py`（9636）· `python/swpy/events.py`（9780）· `python/swpy/_host.py`（8940）· `python/swpy/_editor.py`（23066）· `python/swpy/ui.py`（7701）
- `src/SwPy.AddIn/SwPyAddIn.cs`（11711 字节，add-in 入口）· `src/SwPy.AddIn/Scripting/Libraries.g.cs`（155463）与 `Cast.g.cs`（93917，生成的 C#↔Python 桥）· `src/SwPy.AddIn/Ui/CodeEditor.cs`（47256）与 `EditorPane.cs`（38527）
- `python/swpy/swconst.py`（330034 字节）· `python/swpy/libs/swcommands.py`（146403）· `libs/cosworks.py`（120809）· `libs/EdmLib.py`、`swdocumentmgr.py`、`gtswutilities.py`、`swdimxpert.py`、`SWRoutingLib.py`、`sldcostingapi.py`
- `tests/conftest.py`（session fixture 调 `harness.SwPy()`，即启动 SOLIDWORKS 并加载 add-in）· `tests/harness.py` · 16 个测试文件
- 实测：`PYTHONPATH=python PYTHONDONTWRITEBYTECODE=1 python -m pytest tests -q -p no:cacheprovider` ⇒ `1 failed, 31 passed, 169 errors in 5.94s`（2026-11-02，Python 3.14.7；error 全为 `FileNotFoundError`）· 计数：`(Select-String -Path 'tests\*.py' -Pattern 'def test_' -AllMatches).Count` ⇒ 164
- 元数据：`gh api repos/muerus/SolidWorks-Python`（2026-11-02 取：stars 9 / MIT / created 2026-10-06 / pushed 2026-10-09）

## 9. 未确认事项

1. **宿主层完全未测**：169 个用例在本机报 `FileNotFoundError`（要真 SolidWorks），**API 的真实行为未验证**。（`tests/conftest.py`）
2. **唯一 1 个 failed 是哪个用例**：本卡只取了汇总行，**未定位**（`-q` 输出被截断）。（`tests/test_model.py` 等 14 个测试文件）
3. **`model.faces...select()` 在命中多个时的行为**：`largest()` 天然唯一，但 `.planar().normal(Z)` 多命中时**是否报错、是否取第一个**，**未读实现确认**。
4. **`batch()` 是否真的是「事务」**：它只合并重建，**中途异常是否回滚未确认**（上下文管理器的 `finally` 只恢复视图设置）。
5. **`swpy.client` 的传输机制**：`07-remote-control.md` 只说「代码在 SolidWorks 内执行」，**用的是 COM 回调、命名管道还是窗口消息未读实现**。
6. **SW 版本兼容性**：`swconst.py` 等生成物对应哪个 SW 版本、升级后是否需重生成，**未确认**。
7. **`deliver` 的判定**：它不封装导出，故本卡标 `none`；若按「能力等价」计，它其实能导出任意格式——**这是本卡的一个口径选择，不是事实判断**。

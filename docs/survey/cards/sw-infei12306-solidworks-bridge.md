# infei12306/solidworks-bridge

<!-- survey: class=H; repr=code; orchestration=single; verify=export-readback; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `infei12306/solidworks-bridge` · https://github.com/infei12306/solidworks-bridge |
| 许可 | **MIT**（`LICENSE` 1085 字节；README「Licence」段写 `MIT - see LICENSE`）⇒ 可读可抄可商用，保留版权声明 |
| 元数据 | stars 4 · forks 0 · 语言 Python（11 个 `.py`）· 仓库 711 KB · 建档 2026-09-14 · 最近推送 2026-10-14（来源：`gh api repos/infei12306/solidworks-bridge`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\infei12306__solidworks-bridge`（`--depth 1`）|
| 证据等级 | **读码**（测试要活的 SolidWorks + 干净会话：`tests/phase2_driver.py` 等自述「refuse to run while documents are open」；SolidWorks 未跑，建模能力结论止步 `source`）|

## 1. 一句话定位

**唯一为 DeepSeek Harness 写的 SolidWorks 驱动，也是本批唯一把「类型库版本错配」这个环境级障碍诊断到底并写成可用绕法的一家**：15 个 CLI 子命令 + 55 KB 的 `SKILL.md`，agent 写 Python 作业跑在活会话里，导出带结构校验；`REFERENCE.md` 是一份 12 条坑的实测笔记（含 `GetMassProperties2` 13 个返回值逐位对照与导出文件头校验表）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：CLI（`sw/swbridge.py`，15878 字节）。**它不是 MCP 服务端**：agent 通过 shell 调 `swbridge.py`，人读摘要；另外 `scripts/install.ps1` 会把 checkout 链进 `~\.dsh\skills\solidworks-bridge`（README「Install」段），即它以 **DSH skill** 的形态被使用。

**中间表示**：**作业脚本本身**。`run --file job.py` 把一段 Python 在驱动进程内 `exec` 到活会话上（README 第 14 行、`REFERENCE.md`「Why Python, and why there is no VBA」段），作业可以用注入的 `OUT` 目录写自己的输出。⇒ 这是本批最彻底的「**少工具 + 万能代码口**」形态：15 个命令只是外壳，真正的建模能力来自 agent 现写的 Python。

**生成**：agent 写 Python 作业（人也写），驱动负责 attach / 重试 / 单位 / 导出 / 诊断。

**编排**：无编排层。同步 `run` 或 `run --async` + `status` 轮询（状态写在 `%LOCALAPPDATA%\swbridge\status\` 的文件里，不靠解析控制台文字——`REFERENCE.md` 坑 #11 明写「printf 风格的状态行会骗状态抓取器，改为读状态文件」）。

**执行**：`sw/swcore.py`（41401 字节，「the machine room: attach, cast/getv/call, retry, session, export, diagnostics」）负责 attach 与调用的三件套 `cast` / `getv` / `call`（晚绑定下属性与方法分不干净，见 §3.2）。

**验证**：**以「读回 + 结构校验」为主**：`info` 给质量属性/实体/特征；`save … --as step|stl|iges|pdf|x_t|3mf` 的注释就是「export **AND** verify」（README 第 18 行），`REFERENCE.md` 的「Export matrix」逐格式给字节数与结构判据（见 §3.3）。**没有**体积变化的方向断言、没有回滚。

**交付**：STEP / STL / IGS / PDF / X_T / 3MF（`.OBJ` 实测失败、错误码 256，因无对应 translator）；截图走 `SaveBMP` 只取图形区。

## 3. 技术方案要点（可迁移的机制）

### 3.1 类型库版本错配：**这是本批最可能直接救我们一条的环境知识**

环境实测（`REFERENCE.md`「The type library mismatch」段）：注册表把 SOLIDWORKS 类型库登记为 **21.0（win64）/ 1.0（win32）**，而 `.tlb` 文件里写的是 **33.0**，COM 校验版本 ⇒ 所有走注册表的查法全失败：

```
pythoncom.LoadRegTypeLib('{83A33D31-...}', 21, 0, 0)   -> TYPE_E_LIBNOTREGISTERED
pythoncom.LoadRegTypeLib('{83A33D31-...}', 33, 0, 0)   -> TYPE_E_LIBNOTREGISTERED
gencache.EnsureModule('{83A33D31-...}', 0, 21, 0)      -> TYPE_E_LIBNOTREGISTERED
gencache.EnsureDispatch('SldWorks.Application.33')     -> TYPE_E_LIBNOTREGISTERED
[Runtime.InteropServices.Marshal]::GetActiveObject(…)  -> TYPE_E_ELEMENTNOTFOUND
```

而 `pythoncom.LoadTypeLib(r'…\sldworks.tlb')` **直接按路径读就成功（1015 个类型）**。于是 `scripts/genstubs.py` 按路径读 `.tlb`、生成 makepy stub（6.27 MB 接口类 + 688 KB 枚举，约 2 秒），从私有目录加载；`win32com.client.gencache` 与 `%TEMP%\gen_py` **一律不用**（所以 Windows 清临时目录也不会坏）；attach 走 `ProgID -> CLSID`（唯一还好的注册表项）再 `pythoncom.GetActiveObject(CLSID)`（纯 ROT 查询）。8199 个枚举常量按真实名字可用。

★ 这一条与本轮其他三家的做法**互相解释**：hjbaard 说「早绑定强制、要 `EnsureModule`」（`sw-hjbaard-solidworks-mcp.md` §3.6 注释里也写了 `gen_py` 缓存会坏），Millwright 说「启动期永远别生成 typelib 缓存」（`sw-raylanlin-millwright.md` §5 #5）——**三个现象指向同一个根因：注册表版本号与 `.tlb` 内的版本号不一致**。若我方环境同样错配，那么「删 `gen_py` 重试」只是暂时有效，正解是**按路径读 `.tlb` + 私有 stub 目录**。

### 3.2 晚绑定的三件套：`cast` / `getv` / `call`

`REFERENCE.md`「COM conventions」段给了一张判据表：
- `GetTypeInfo()` 在 SW 对象上**失败**（`DISP_E_BADINDEX 0x8002000B`）⇒ 接口**无法在运行时被发现，必须按名字指定**（这直接解释了为什么必须有「生成 stub」这一步）。
- `Extension`/`SketchManager`/`FeatureManager` 是**属性**；`GetTitle`/`GetPathName`/`GetType`/`FirstFeature`/`GetTypeName2` 在**早绑定类上是方法**，在晚绑定对象上同名会解析成它的值。
- `Feature.GetTypeName2` 实测「一条路径上是属性、另一条路径上是方法」⇒ 这正是 `getv()`/`call()` 存在的理由。

⇒ 与 HarrierPigeon 的 `com_prop`（用 `isinstance(val, types.MethodType)` 判，`sw-harrierpigeon-solidworks-mcp-server.md` §3.4）是同一问题的两种写法，**两者可以合并成一个判据**（先 cast 到具体接口，再 `isinstance` 兜底）。

### 3.3 导出即验证：**六种格式的结构判据表**（可直接抄成我方 `deliver` 校验器）

`REFERENCE.md`「Export matrix」段（全部经 `SaveAs3(path, 0, swSaveAsOptions_Silent)`）：

| 格式 | 字节数 | 结构判据 |
|---|---|---|
| `.STEP` | 15746 | 以 `ISO-10303-21;` 开头 |
| `.STL` | 684 | 二进制，头里写 12 个三角面，且 `84 + 12*50 == 684` |
| `.IGS` | 22386 | 含 `SolidWorks IGES file …` |
| `.PDF` | 164193 | `%PDF-1.4` … `%%EOF` |
| `.X_T` | 7425 | `**ABCDEFGHIJKLMNOPQRSTUVWXYZ` |
| `.3MF` | 4340 | `PK`（zip）|
| `.OBJ` | - | **失败**，错误码 256（无 translator）|

再配一条硬事实：**`SaveAs3` 返回的是 `VT_I4` 错误码**（0=成功、256=扩展名无效/无 translator、32=版本不对），当 bool 用会把**每一次成功导出都报成失败**（`REFERENCE.md` 坑 #5）。⇒ 我方 `export` 类工具应当：**判 `== 0` + 判文件头 + 判体积**，三件都做。

### 3.4 模态框的实测结论：**不拒绝别人、只卡自己**

`REFERENCE.md`「COM conventions」段的实测：「**modal dialogs do not reject other clients: measured 150/150 concurrent calls served while a modal was up (re-entrant), while the dialog's own caller stayed blocked**」；坑 #10 记录了「一个期待 `RPC_E_CALL_REJECTED` 的测试失败了」。

⇒ 这条对「单源 COM 互斥」的推论很关键：**模态框不等于全局死锁**——别的客户端还能进（re-entrant），只有弹框的那个调用者被卡住。它据此把「恢复路径」设计成 `dialogs`（列出）+ `dismiss`（应答），且 `dismiss` **默认按 Cancel**（坑 #9：向「保存修改？」回 OK 等于「覆盖保存」，Cancel 只中止并保留文档打开）。

另一条：`CloseDoc` 对脏文档**会开模态框并且永不返回**（「COM conventions」段），这就是「必须能列出并应答弹窗」的动机。

### 3.5 单位与本地化：两条实测

- `GetMassProperties2` 返回 **13** 个值，并用 50×30×20 mm 的解析盒逐位验证（相对误差 < 1e-6）：`[0-2]` 质心 (m)、`[3]` 体积 (m³)、`[4]` 表面积 (m²)、`[5]` 质量 (kg)、`[6-8]` 惯性矩、`[9-11]` 惯性积、`[12]` 密度 (g/cm³)。⇒ **可以直接当我方「回读即数值断言」的 oracle 表**。
- 本地化：`前视基准面`（Front Plane）、`凸台-拉伸1`（Boss-Extrude1）；找基准面的正解是 `GetTypeName2() == 'RefPlane'`（「COM conventions」段最后一行）。

### 3.6 截图：`SaveBMP` 只取图形区、窗口被遮挡也能拍

`REFERENCE.md`「Measured behaviour」段：`SaveBMP(1600, 1000)` 得到 4.8 MB BMP、100% 非黑、793 色，PNG 里**只有图形区**（没有菜单/窗口边框），**窗口被遮挡也有效**。⇒ 比截屏抓窗口更可靠，且不依赖前台焦点；对我方「截图作为证据」是一件便宜升级。

## 4. 运行条件与依赖

- Windows + SOLIDWORKS **2025 SP5.0（`33.5.0.0053`，ProgID `SldWorks.Application.33`）**，UI 语言中文（`REFERENCE.md`「Environment」段；作者机器装在 `D:\Mango\sw2025\…`，非 C 盘）。
- Python **3.11.9 64 位** + `pywin32` build 312（+ `pillow` 用于图像）。
- 安装：`scripts/install.ps1` → 复制驱动到 `%LOCALAPPDATA%\swbridge`、生成 COM stub、并**链进 `~\.dsh\skills\solidworks-bridge`**（即以 DSH skill 形态使用）。
- 冒烟：`swbridge.py doctor`（环境 + attach 诊断）与 `tests/selftest.py`（跑四套）。
- 冷启动实测：约 5 秒出 splash、约 60 秒出主窗、约 416 MB 常驻（`REFERENCE.md`「Measured behaviour」段）。

## 5. 失败模式与已知坑

**`REFERENCE.md`「Pitfall log」12 条**（每条都「cost a failed attempt」）＋本卡归纳：
1. **`GetBodies2` 在 `IPartDoc` 不在 `IModelDoc2`**：要 `cast(doc, 'IPartDoc')`。
2. **晚绑定 `ActiveDoc` 让属性看起来可调用**：`doc.GetTitle()` 报 `'str' object is not callable`；修法是先 `cast(obj, 'IModelDoc2')`。
3. **`FirstFeature`/`GetNextFeature` 也返回晚绑定对象**，循环里要 cast 到 `IFeature`。
4. **`pythoncom.VARIANT(VT_BYREF|VT_I4, 0)` 传 `[in,out]` 参数反而报 TypeError**；**裸 `0` 可用，out 值追加在返回值后面**。★ 与 Millwright 的「必须用 byref VARIANT」**结论相反**（见 §9）。
5. **`SaveAs3` 成功返回 0**；当 bool 用会把每次成功都报失败。
6. **`exc.args[0]` 可能是字符串**：早期错误翻译器对它做 `& 0xFFFFFFFF` 直接抛 `TypeError`，把真异常吃掉。
7. **`GetWindowText` 读不到别的进程的控件**：对话框按钮能读，正文不能。
8. **用 `SendMessage(WM_GETTEXT)` 读对话框不安全**（同步消息，而拥有对话框的线程正是忙的那个）⇒ 所以不读正文。
9. **`dismiss` 默认 Cancel**：向「保存修改？」回 OK 等于覆盖保存。
10. **模态框是「阻塞」不是「拒绝」**：150/150 并发调用在模态框存在时仍成功。
11. **作业自己输出的 `printf` 状态行会骗状态抓取器**：改为读状态文件。
12. **异步父进程必须先写 `RUNNING` 再 spawn**，否则瞬间完成的子进程的 `OK` 会被覆盖。

另：**不要「修」注册表**（`REFERENCE.md` 明写「The workaround is deliberate」）；**不静默改用户的 SolidWorks 设置**（「Deliberately not done」段：弹窗抑制是写文档，不是背着用户改）；`quit` 永不自动执行，有未保存文档时还要 `--force`。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **没解**：作业里自己写选择逻辑，无引用抽象（`cast`/`getv`/`call` 只解决绑定层） | `REFERENCE.md`「COM conventions」段 |
| 回读验证 | **部分**：`info` 读回质量属性 + 导出按文件头结构校验；无方向断言、无期望值闭环 | `REFERENCE.md`「Measured behaviour」与「Export matrix」 |
| 事务式建模 | **没解**：无回滚；异步作业只保证「状态文件可读」 | `REFERENCE.md` 坑 #12 |
| 单源 COM 互斥 | **实测并推翻了一个常见假设**：模态框不拒绝别的客户端（150/150），只卡调用者 | `REFERENCE.md` 坑 #10 |

**Q3 答**：**CLI + 作业脚本**（不是 MCP 服务端，也不是库）；工具面 **15 个子命令**（`(Select-String -Path 'sw\swbridge.py' -Pattern 'add_parser\(' -AllMatches).Count` ⇒ 15）；粒度 = **少命令 + 万能代码口**（`run --file/--code` 直接跑任意 Python），是本批「万能口」最彻底的一家。

**能学（按性价比排序）**：
1. **类型库版本错配的诊断与绕法**（按路径 `LoadTypeLib` + 私有 stub 目录 + ROT attach）：这可能解释我方环境里所有「`EnsureModule` 时好时坏」的现象，**值得先跑一次 `doctor` 式诊断确认我方是否同病**。
2. **导出结构判据表（6 种格式）+ `SaveAs3` 是错误码不是 bool**：直接可做我方 `deliver` 校验器，成本极低。
3. **`GetMassProperties2` 的 13 位索引含义 + 解析盒 oracle**：把我方「回读」变成「可断言的数值」，且给了容差（<1e-6）。
4. **`SaveBMP` 只拍图形区、遮挡也行**：截图证据的可靠性升级。
5. **模态框「阻塞不拒绝」+ `dialogs`/`dismiss` 默认 Cancel**：修正我方对弹窗风险的模型（不是全局死锁，而是「卡住发起者」），且「默认保守应答」是正确默认值。
6. **状态走文件不走控制台**（坑 #11/#12）：异步作业的状态机写法。
7. **`GetTypeName2() == 'RefPlane'` 找面、不硬编码本地化名**：与 Slacker-LLC 的本地化坑互相印证。

**不能学**：
- **万能代码口当主路径**：`run --code` 让 agent 直接写任意 Python —— 对我方「工具面 = 可校验面」是反例；它自己也只能给「导出结构校验」这种事后检查。
- **无回滚、无方向断言**：验证强度低于 Millwright / soheil-mp / forge_ai 三家。
- **单机单版本实测**（2025 SP5 中文）：环境相关结论不可外推。
- **把 `.tlb` 版本错配当常态并依赖私有 stub**：可作兜底，但若我方环境注册表正常，直接用注册表更简单。

## 7. 许可与红线

**MIT**（`LICENSE` 1085 字节；README「Licence」）。可移植，义务：保留版权声明。★ 移植「按路径读 `.tlb` + 私有 stub」的加载器、导出结构判据表、`GetMassProperties2` 索引表、`dialogs`/`dismiss` 的保守默认值时，来源头写 `infei12306/solidworks-bridge（MIT，LICENSE）` + 改动说明。

## 8. 证据清单

- `README.md:1-23`（11 条命令清单，含 `save … export AND verify`、`api`/`enum` 离线查询）· `:25-30`（SW2025 SP5 `33.5.0.0053`、ProgID `.33`、Python 3.11+）· `:38-39`（装到 `%LOCALAPPDATA%\swbridge` 并链进 `~\.dsh\skills\solidworks-bridge`）· `:48-62`（为什么这么建：类型库版本错配）· `:64-76`（文件职责与「four suites, ~57 checks」）
- `REFERENCE.md:7-17`（环境实测表：SW 版本、安装路径、ProgID/CLSID、ROT 条目、Python、两个 LIBID）· `:19-31`（为什么是 Python、为什么不要 VBA/PowerShell）· `:33-68`（**类型库版本错配全段**：5 条失败命令、`LoadTypeLib` 按路径可用、6.27 MB/688 KB stub、8199 枚举）· `:70-88`（COM 约定表：`GetTypeInfo` 失败、属性 vs 方法、`[in,out]`、`SaveAs3` 错误码、`OpenDoc6`、`CloseDoc` 永不返回、RPC 拒绝码、**模态框 150/150**、单位、本地化、跨进程读文本）· `:90-122`（冷启动、`SaveBMP`、**`GetMassProperties2` 13 位表**、**导出矩阵**、作业往返 ~2 s）· `:124-160`（**12 条坑**）· `:162-173`（路径与状态目录）· `:175-186`（四套测试与「开着文档时拒跑」）· `:188-196`（「Deliberately not done」：无 .NET add-in、不生成宏、不静默改设置、`quit` 需 `--force`）
- `sw/swcore.py`（41401 字节）· `sw/swbridge.py`（15878 字节，CLI）· `sw/swapi.py`（8123 字节，离线签名/常量/属性查询）· `scripts/genstubs.py`（9331 字节，按路径读 `.tlb` 生成 stub）
- `tests/phase1_smoke.py`(10186) / `phase2_driver.py`(7915，「22 checks」) / `phase3_hard.py`(8598，「26 checks」) / `phase3_modal.py`(8490) / `selftest.py`(4345) / `tests/jobs/make_box.py`、`make_bracket.py`
- `SKILL.md`（55165 字节，给 agent 的使用说明，本轮最深的一份 skill 文本）· `MODELING.md`（129976 字节）· `PLAN.md`（20302 字节）
- 实测计数：`(Select-String -Path 'sw\swbridge.py' -Pattern 'add_parser\(' -AllMatches).Count` ⇒ 15
- 元数据：`gh api repos/infei12306/solidworks-bridge`（2026-11-02 取：stars 4 / MIT / pushed 2026-10-14）

## 9. 未确认事项

1. **未跑**：所有结论来自代码与它自己的实测记录；`doctor` / 四套测试在本机**未执行**（需要活的 SolidWorks）。
2. **★ 与 Millwright 的直接冲突**：本条说「`VARIANT(VT_BYREF|VT_I4, 0)` 反而报 TypeError，裸 `0` 可用、out 值追加在返回值后」（`REFERENCE.md` 坑 #4），而 Millwright 说「必须用 `VARIANT(VT_BYREF|VT_I4, 0)` 并读 `.value`，裸 `0` 报 Type mismatch」（`docs/COM-PITFALLS.md` #7）。**两家都在真机上验证过**，差异只可能来自 SolidWorks 版本、pywin32 版本（build 312 vs 其他）或具体方法。⇒ **必须我方自己实测**，且按「每个 `[in,out]` 方法各测一次」而不是定一条通则。
3. **类型库错配是否我方环境同样存在**：这是本卡最高优先级的待核项——`pythoncom.LoadRegTypeLib('{83A33D31-…}', <版本>, 0, 0)` 与 `pythoncom.LoadTypeLib(<路径>)` 各跑一次即可判定。
4. **`run --code` 的安全边界**：任意 Python 在驱动进程内执行，**是否有任何限制未读全**（README 未提；推测无）。
5. **`SKILL.md`（55 KB）的内容质量**：只看了目录级标题（`Locate the driver` / `Job scripts` / `Hard rules` / `Workflows` / `Troubleshooting`），**正文未通读**。
6. **`MODELING.md`（130 KB）是什么**：未读，推测是建模经验库，**未确认**。
7. **`.OBJ` 失败是否普遍**：作者机器无 OBJ translator，**他人环境是否同样失败未确认**。

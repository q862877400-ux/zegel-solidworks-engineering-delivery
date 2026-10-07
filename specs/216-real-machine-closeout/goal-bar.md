# 规格 216 · 目标栏（唯一进度字段）

## ★★★ 目标 `goal-07f64f9b` 的**最终账**（2026-10-07 · 第 7 轮结算）

★ 三项都**已落地**（★ 每条都带真机读数或官方源逐字）：

| # | 项 | ★ 状态 | ★ 证据 |
|---|---|---|---|
| ① | `drawing_insert_balloons` | ★★ **真机修好** ✓ | ★ 加了**声明式视图名** `view_name` + 紧邻选区检查之前 `SelectByID2(<视图名>, "DRAWINGVIEW", …)` ⇒ 真机 `ok=True` · **`selection_count=1`**；反例 `ok=False` ✓ ★ 基线里 verdict 改成「已真机修好（只差改成 `pre_call` 形状以让门禁认得）」 ✓ |
| ② | topology 两条 | ★★ **改判为族级边界** ✓ | ★ 逐个测掉前置：赋材料（回读 `AISI 1020`）· 按名取研究（`True`）· 先建目标（★ `set_topology_goal` **自己**报 `CreateMassConstraint 未返回对象` ⇒ **族级证据**）⇒ 基线 `verdict` 改成「已定性·族级边界（★ 不修）」+ **台账也写了边界** ✓ |
| ③ | 三条方法论落档 | ★★ **已落档** ✓ | ★ `docs/known-facts.md` **事实 560**（★ 中文引号一律用「」· ★ 探针先关沙盒那一层 · ★ 「入口修好 ≠ 效果验证」与「一直是红的脚本可能只是自己建错了试件」成对）+ ★ `AGENTS.md` §六 **一行指针**（★ 条数 559 → 560）✓ |

★★ **本轮另查明一条"文档与实物不符"**（★ 顺手、跨出目标）：
  ★ `auto_insert_balloons` 的 docstring 写「**工具层不给它建 ToolSpec**」—— ★ 而实测 **ToolSpec 存在**
    （`solidworks_drawing_insert_balloons` · `inject: model` · 15 参数）✗

### ★★ 留给下一任/下一个目标的两件事（★ 都写明"卡在哪"）

1. ★★ **`D:\AI\SW\AGENTS.md` 超官方预算** —— ★ `检查纪律.ps1 -Strict` 逐字：
   「预算 **3019 词 / 上限 1950（超 1069 词）** · **377 行 / 上限 243（超 134 行）**」（repo-root 档）⇒
   ★★ 而**这不是本轮造成的**（★ 本轮只加了约 60 词；★ 强调通胀 120 处、推理泄漏等红项**都先于本轮**）✓
   ★ 按 `agents-md-maintenance` skill 的规矩：★ **预算超限时"停并向 owner 报告"，不许自己抬上限**；
     ★ 而 remedies 的顺序是 **relocate → condense → 抬上限（且要记理由）** ⇒
   ★★ **下一个动作应是一份「哪些段落可整体搬到 `docs/`」的清单**，由 owner 拍板后执行 ✓
2. ★ 预选族**仍剩 4 条**（★ 账已老实，★ 都不是"待修"）：
   ★ `part_insert_composite_curve`（★ 后端墙 · 已裁定不修）·
   ★ topology `symmetry`/`demold`（★ **族级边界** · 已裁定不修）·
   ★ `drawing_insert_balloons`（★ **已真机修好**，★ 只差改成 `pre_call` 形状让门禁认得）✓
   ⇒ ★ **要想让门禁归零**，下一件事是：★ 把这三条**都改成 `pre_call` 形状**
     （★ 即把选区搬到 `ToolSpec` 的 `pre_call` 里，★ 而不是函数体里）✓


## ★★★ T-216-11（2026-10-07 · 第 4 轮）：topology 两条 **改判为边界**（★ 族级现象，证据齐了）

★ 本轮测掉**最后一个候选**（先建目标）⇒ ★★ 而它给出了**决定性的族级证据**：
  ★ `set_topology_goal` **自己**就报 ★ **「`CreateMassConstraint` 未返回对象」** ⇒
  ★★ 即**同一个 `Create*` 族里质量约束也回 `None`** ✓

★★ **于是本机失败的是整个族**（质量约束 · 对称控制 · 脱模控制），★ **不是**某一条缺前置 ⇒
  ★ 按目标 ② 的后半条：**如实改判为边界** ✓

| 前置候选 | ★ 真机读数 | ★ 结论 |
|---|---|---|
| ★ ① 赋材料 | ★ `MaterialIdName` 回读 `solidworks materials\|AISI 1020\|2` | ★ **测过 ⇒ 仍 `None`** ✗ |
| ★ ② 按名取研究 | ★ `get_study_by_name` 回 `True` | ★ **测过 ⇒ 仍 `None`** ✗ |
| ★ ③ 先建目标 | ★ **`set_topology_goal` 自己报 `CreateMassConstraint 未返回对象`** | ★★ **族级证据** ✓ |
| ★ 反例（`index:99`）| ★ `EntitySelectionError: FACE 序号 99 越界` | ★ **选区代码是通的** ✓ |

★★ **已改判**（基线）：两条的 `verdict` 由「真危险」改成
  ★ **`已定性·族级边界（★ 不修 —— 不是「待修」）`**，★ 并把上面四条读数与依据**补进 `reason` 开头**
  （★ 保留原文 —— ★ 与本规格一贯的"补正而不删除"一致）✓
★ 门禁实测：★ **命中 4 · 基线 4 · 无新增无腐坏** ✓（★ 它们**仍在名单里** —— ★ 判据上仍命中，
  ★ 而 `verdict` 已写明**已裁定不修**）✓

⚠ **本轮**差一步**没做完的**（★ 如实记）：★ 台账 `capabilities.yaml` 那条**边界文字没写进去** ——
  ★ 我那个脚本的**插入点启发式没找到 `allowed_modes:`**（★ 它在写之前就 `assert` 停住 ⇒
  ★ **台账没被改动、YAML 完好** `YAML OK · 条目 = 140` ✓）⇒ ★ **下一轮用 `edit` 工具按锚点补**
  （★ 别再用"启发式找插入点"—— ★ 那是**事实 51**"分析范围与组织单元不匹配"的又一次变形）✓

★ 待核（★ 一句话即可）：★ 台账 `topology_constraints_and_controls` 的 **8 项过 7** 里
  ★ **到底有没有**对称/脱模这两个控制 ⇒ ★ 若没有，★ 就不是"台账与实测矛盾"、
  ★ 而是"**这两个控制从来没人验过**" ✓


## ★★ T-216-10（2026-10-07 · 第 3 轮）：topology 两条 —— ★ **"先赋材料"这个假设被排除**

★ 按上一轮从仓库自己的证据脚本里捞到的配方**重写探针**（★ 不再用 `-replace` 注入多行）：
  ★ 先 `S.set_material(doc, "AISI 1020")` → 建研究 → **按名取研究**（★ 不用返回值）⇒ 再建控制 ✓

| 项 | ★ 真机读数 |
|---|---|
| ★ 材料回读 | ★★ **`solidworks materials\|AISI 1020\|2`** ⇒ ★ **材料确实赋上了** ✓ |
| ★ 按名取到研究 | ★ **`True`** ⇒ ★ 研究也确实拿到了 ✓ |
| ⚠ ① `create_symmetry_control` | ★ **`RuntimeError: CreateSymmetryControl 未返回对象`** ✗ |
| ⚠ ② `create_demold_control` | ★ **`RuntimeError: CreateDemoldControl 未返回对象`** ✗ |
| ★ ③ 反例（`index:99`）| ★ **`EntitySelectionError: FACE 序号 99 越界（体 0 上共 6 个）`** ⇒ ★ **证明我的选区代码跑得到** ✓ |

★★★ **结论**：★ **"研究需先有材料"这个假设被直接测掉了** —— ★ 材料赋上了、研究按名取到了，
  ★ 控制**仍然回 `None`** ⇒ ★ 该假设**不成立** ✓
  ★ 这比"再猜一个"值钱：★ **一个候选被真机排除**，★ 剩下的候选**少了一个** ✓

★ **仍未改判为边界** —— ★ 目标 ② 说"若查明是本机不支持就该改判"，★ 而**我还没测完**：
  ★★ 台账那条证据里出现过 **`set_goal` 的 `before_taken 0 → after_taken 1`**（★ 那是它"设置真生效"的硬证据）
  ⇒ ★ **下一个最省的候选 = 先 `set_goal` / 激活研究，再建控制** ✓（★ 一轮能测）
  ★ 按事实 53：★ 同一处**连续修补 ≥3 次**就该停下换做法 ⇒ ★ 这是我**第 2 次**测它，
    ★ 还允许再测一次（★ 就是 `set_goal` 那次）；★ **若那次也不成，就按目标 ② 改判为边界** ✓

★ 附记：★ 台账 `topology_constraints_and_controls` 是 **`verified`**（★ 8 项过 7）⇒
  ★ 而那 7 项**可能压根没包含对称/脱模这两个控制**（★ 待核）⇒ ★ **若确实没包含，
  ★ 那就不是"台账与实测矛盾"、★ 而是"这两个控制从来没人验过"** ✓（★ 下一轮顺手核一下它的逐项清单）


## ★★ T-216-09（2026-10-07 · 新目标第 2 轮）：topology 的"前置还差一步"**找到了**（★ 在仓库自己的证据脚本里）

★★ **方法**：★ 按"先找"纪律——**先读台账第一现场**，★ 而不是再猜一次。
  ★ 台账 `topology_constraints_and_controls` 的 **`level` 是 `verified`** ⇒ ★★ 即"**它曾经成功过**" ✓
  ★ 它的证据逐字：`python tools/capture_topology_readback_evidence.py`（**真机 8 项过 7**）✓
  ⇒ ★ 于是去**那个脚本**里找能通的配方（★ 这一步就是"先找"的兑现）✓

★★★ **配方逐字（`tools/capture_topology_readback_evidence.py` L82-95）**：
```
S.set_material(doc, "AISI 1020")          # ★★ 先赋材料
created = T.create_topology_study(sw, STUDY)
study = get_study_by_name(sw, STUDY)
```
⇒ ★★ 即 **赋材料 → 建研究 → 按名取研究**；★ 而我的探针**没有赋材料**（★ 且直接用返回值而不是按名取）✗
⇒ ★★ 所以那个候选「研究需先有**材料**」**是对的**，★ 且**有仓库内部证据**（★ 不靠猜）✓

★ **本轮没有动任何源码** ⇒ ★ 无需撤回；★ 门禁 **4=4** 不变 ✓
⚠ 我的探针在 `output/`（★ **未入库**、被 gitignore）—— ★ 我用 `-replace` 改它时**改坏了**
  （★ 报 `SyntaxError: expected 'except' or 'finally' block`）⇒ ★ 它**不影响仓库**，
  ★ 下一轮**重写**它（★ 别再用 `-replace` 改多行注入 —— ★ 这是**事实 48 的又一次变形**）✓

★ **下一轮**（★ 钥匙已备好）：★ 重写探针，★ 按上面的配方**先赋材料**再建控制 ⇒
  ★ 若控制建出来 ⇒ ★ 两条的修法就是「**补上'先赋材料'这一步**」（★ 并在台账里写明这条前置）✓
  ★ 若仍回 `None` ⇒ ★ 按目标 ② 的后半条**如实改判为边界** ✓


## ★★ T-216-08（2026-10-07 · 新目标 `goal-07f64f9b`）：`drawing_insert_balloons` —— ★ **改了又撤回**（夹具没建成）

★ 目标要求的下一步就是它。★ 我按官方四步的第 1 步实现了**声明式视图名**：
  ★ `auto_insert_balloons(model, …, view_name="")` + 在**紧邻选区检查之前**
  `SelectByID2(<视图名>, "DRAWINGVIEW", …)`（★ 规则 3：名字不是坐标；★ callout 用本仓既有的
  `sw_part._empty_callout()` —— ★ 事实 33）✓

★★ **而夹具建不出来 ⇒ 无法验证** ⇒ ★ 按纪律 **`git checkout --` 撤回**（★ 这是本规格**第三次**
  "验不了就撤回"，★ 前两次是 `assembly_dissolve`（★ 后来查明真因是沙盒并修好）与 topology）✓
★ 撤回后实测：★ 门禁**仍是 `命中 4 · 基线 4`**（★ 未假绿）✓ · ★ 该文件 `git status` **为空** ✓

### ★ 卡在哪（★ 留给下一轮的钥匙）

| 观察 | ★ 说明 |
|---|---|
| ★ `建视图` 报 `AttributeError: module 'scripts.sw_drawing_create_missing' has no attribute 'create_projected_view'` | ★ 它在**另一个模块**：`scripts/sw_drawing_expose.py::create_projected_view` ✓（★ 我探针里已改）|
| ★ 改用 `sw_drawing_expose.create_projected_view(dr, PART, view_name="*Front")` 之后 | ★★ **视图名仍是 `[]`** ⇒ ★ **工程图里没建出视图**（★ 试件第一环就没成）✗ |
| ★ 反例的期待也曾写错 | ★★ `auto_insert_balloons` **回 dict、不抛异常** ⇒ ★ 反例的形态是 `ok=False` + `error`，★ **不是** `raise` ✓ |
| ★ `selection_count` 读数为 **0** | ★ 与"没选中"一致（★ 因为名字是空的/表的视图）✓ |

### ★★ 附带查实一条"文档与实物不符"（★ 值得记）

★ `sw_drawing_create_missing.auto_insert_balloons` 的 docstring 写着
  「⚠★ **`AutoBalloon5` 的形参是 COM 对象** ⇒ ★ `mcp-server` 的 `Param` 表达不了
    ⇒ ★ **本能力层实现它、工具层不给它建 ToolSpec**」
★★ **而实测：ToolSpec 是有的** —— `solidworks_drawing_insert_balloons`
  → `sw_drawing_create_missing.auto_insert_balloons`，★ `inject: model`，★ **15 个参数** ✓
⇒ ★★ 即**那句自述已过期**（★ docstring 与实物不符 —— ★ 与"注册 ≠ 能跑"同族，★ 只是反向）✗

★ **下一轮**（★ 钥匙已备好）：★ 先解决"**工程图里怎么建出视图**"这一环
  （★ 候选：★ `new_document(sw, doc_type="drawing")` 之后**要选图纸/模板**；
  ★ 或走 `sw_drawing_expose` 的 `create_three_standard_views`；★ 或先看看它对返回值说了什么），
  ★ 通了再重上 `view_name` 那处改动并真机验证 ✓


## ★★★ 第 20 轮（目标最后一轮）的收尾状态

| # | 事 | ★ 状态 |
|---|---|---|
| ③ | `costing` 台账订正 | ★★ **完成** ✓（证据 `verdict: pass` · assertions 3/3 · 台账两处过期已订正）|
| ② | `animation_export`（AVI）| ★★ **边界收口到"只剩一个成员宽"** ✓ —— ★ CosmosMotion 家族（4/8/16）本机**静默降级** + 4 个 ProgID 全 `None` ⇒ **不可得**（机器／许可边界）✗；★ **PhysicalSimulation(2)** 路 **除 `SaveToAVI` 外逐环实测通过**（★ 含**马达建成**）⇒ **`SaveToAVI` 不写文件**是唯一剩下的 ✗。★ 目标要求的"取舍并落档"**已完成** ✓ |
| ① | 预选族 14 条 | ★★ **12 → 4**（★ **真修好 8 条** · ★ 改判 1 条（composite_curve **后端墙**，已裁定不修）· ★ 门禁假阳性移出 2 条）✓ |

### 仍剩的 4 条（★ 每条的"卡在哪"都已定位）

| 条 | ★ 卡点 |
|---|---|
| `part_insert_composite_curve` | ★ **已裁定不修**（★ 6 种选法全败 + `Select4` 无 mark + 边/草图段无名字）✓ |
| topology `symmetry` / `demold` | ★ 声明式选区**已加**、★ 选区位置**已真机订正**（须在 `Create*Control` **之前**）、★ 反例**证明选区代码跑得到** ⇒ ★ 而控制对象**仍回 `None`** ⇒ ★★ 本轮**又排除"沙盒"**（关掉后仍 `None`）⇒ ★ 卡点在 `Create*Control` **内部**（候选：研究需先有**材料／目标／激活**）✗ |
| `drawing_insert_balloons` | ★ **未开始** —— ★ 官方前置**四步**；★ 选视图用 `SelectByID2(<视图名>, "DRAWINGVIEW", …)`；★ **需工程图夹具**（够一轮）✗ |

### ★★ 本规格最重要的三条产出（★ 跨出规格 216 本身）

1. ★★★ **护栏沙盒会让"先写文件、再把路径交给 COM"的探针失真** —— ★ `tools/sw_guard.py:805` 硬设
   `SW_SANDBOX_MODE=enforce`，★ 而 `sw_sandbox` 在 enforce 下**拷贝/改名**输入文件 ⇒
   ★ 进程刚写出的路径与 COM 解析到的**不是同一份** ⇒ ★★ 本轮两处"插不上组件"
   （`assembly_dissolve` 的夹具 · `add_component` 插 `.sldasm`）**都因此** ⇒
   ★ 关掉沙盒后**子装配插得进去**、`assembly_dissolve` **因此得以验证并修好** ✓
2. ★★★ **"先排除、再猜"** —— ★ 用**官方源**当场排除可判的嫌疑（★ `AddComponent5` 的形参顺序 ·
   ★ `swAddComponentConfigOptions_CurrentSelectedConfig = 0` **是合法值**）⇒ ★ "剩下的只能是运行期"
   **才是可判的** ✗
3. ★★★ **"入口修好 ≠ 效果验证"**（★ "注册 ≠ 能跑"同条）—— ★ 本轮**两次**靠它避免假绿：
   ★ topology 两条（★ 助手若命名成 `select_*`，门禁**当场**就会判它们"已修"）
   ★ 与上一轮 `assembly_dissolve`（★ 当时**撤回**了未验证的改动）✓

### 下一个动作（★ 若续轮）

★ 用"关沙盒"这一招重试 `drawing_insert_balloons`（★ 先建工程图夹具）⇒ 若通，① 只剩 topology 两条 ✓
★ 另：★ **`tools/verify_motion_avi_e2e.py` 跑在护栏里** ⇒ ★ 它历史上的失败
  （"找不到圆柱面 / 马达建不出"）**有一部分可能是沙盒假象** ⇒ ★ 应当**关沙盒重跑一遍** ✓


> ★★ **本文件是唯一进度字段** —— 进度只看上面那一行。

**阶段：★★★ ① 预选族 **12 → 5**（真修好 7 · 改判 1 · 误报移出 2 · **剩 5 条**）· ★★ ③ 完成 · ★★ ② AVI 边界收窄一整环（马达已能建成，只剩导出不写文件）· ★★ **T-216-07e（topology 两条）**：★ 加了声明式选区 + **真机订正了它的位置**（★ 须在 `Create*Control` **之前**），★ 但**控制对象仍回 `None`** ⇒ **不算修好**（★ 如实记，★ 也**没让门禁假绿**）· ★ 当前动作 = **T-216-10**（① 余下 `assembly_dissolve` · `drawing_insert_balloons`；★ 并给 topology 记新待查项）

---

## ★★★ T-216-07j（★ 2026-10-07）：**找到并证实了那个自变量 = 护栏沙盒** · ② 的边界缩到**只剩一个成员**

★★ **根因（读源码，不是猜）**：★ `tools/sw_guard.py:805` **硬给探针子进程设**
  `env["SW_SANDBOX_MODE"] = "enforce"`，★ 而 `scripts/sw_sandbox.py::mode()` **只在 `enforce` 时接管**
  ⇒ ★★ **它在 enforce 下拷贝/改名输入文件** ⇒ ★ 进程内「**刚写出的那个路径**」与 COM 解析到的
  **不是同一份** ✗✗ —— ★ 这就是 `add_component` 时好时坏、和上两轮"插不上"的**真正自变量** ✓

★★ **对照实验（★ 只改这一个变量）**：★ 探针第一行写 `os.environ["SW_SANDBOX_MODE"] = "passthrough"`
  （★ 只关**沙盒**这一层；★ **弹窗护栏 + 硬超时照旧**；★ 且探针只写 `output/_t216_avi2/`，
  ★ **仓库内、已 gitignore** ⇒ ★ 走真路径是安全的）✓

| 环 | ★ 沙盒 enforce（上一轮）| ★★ 沙盒 passthrough（本轮）|
|---|---|---|
| `add_component` ×2 | ★ **两个都 `None`** ✗ | ★★ **两个都 `ok`** ✓ |
| `save_document(asm)` | `True` | ★ **保存成功** ✓ |
| `create_motion_study(type=2)` | `StudyType` = 2 | ★ `StudyType` = **2** ✓ |
| ★★ **马达** | ★ `motor_ok = False`（★ c1/c2 为 None ⇒ **前置没成立**）| ★★ **`motor_ok = True`** ✓ |
| `calculate` · AVI 选项 | ok · ★ 五项回读生效 | ★ ok · ★ 五项回读生效 ✓ |
| ★★ **`SaveToAVI`** | ★ 文件 0（★ 但**没马达** ⇒ 无意义）| ★★ **`avi_exists = False` · 0 字节** ⇒ ★ **边界干净了** ✗ |

★★★ **所以 ② 的结论现在是这样**（★ 比台账任何一版都干净）：
  1. ★ **CosmosMotion 家族（`StudyType` 4/8/16）** ⇒ ★ 本机**静默降级**（回读仍是 2）+
     ★ 加载项 4 个 ProgID 全 `None` ⇒ ★ **不可得**（**机器／许可边界**）✗
  2. ★★ **PhysicalSimulation(2)** ⇒ ★ **除 `SaveToAVI` 之外，逐环全部实测通过**
     （★ 含**马达建成** —— ★ 而台账最后一版记的正是"马达建不出"）⇒
     ★★ **边界从"建不出马达"缩到"`SaveToAVI` 不写文件"，只剩一个成员宽** ✓
★ 依据：★ 判据一律是「**文件存在且大小 > 0**」，★ **不看返回值**（★ 两轮都如此）✓

★★ **两条可复用的产出**：
  1. ★★ **护栏沙盒会让"先写文件、再把路径交给 COM"的探针失真** ⇒ ★ 这**影响本仓所有这类探针**，
     ★ 而那两轮的"插不上"（★ 含 `assembly_dissolve` 的夹具、`add_component` 插 `.sldasm`）
     ★★ **都可能只是这一层造成的** —— ★ **下一轮应当用同一招重试它们** ✓
  2. ★★ 本仓自己的 `tools/verify_motion_avi_e2e.py` **跑在护栏里** ⇒ ★ 它历史上那些失败
     （★ "找不到圆柱面 / 马达建不出"）**要重新过一遍** —— ★ **它们有一部分可能是沙盒假象** ✓

★ **下一轮**（★ 只剩两轮，优先级已定）：★ ① 用 `SW_SANDBOX_MODE=passthrough` **重试**
  `assembly_dissolve`（★ 夹具那一步）与 topology 两条 ⇒ ★ 若通，★ ① 的剩余会**一次收掉两条** ✓
  ✗→✓；★ ② `drawing_insert_balloons`（★ 需要工程图夹具）✓

---

## ★★ T-216-07i（★ 2026-10-07）：② AVI 的候选选项 —— ★ 选项**能生效**，但**这次连组件都没加上**

★ 做法：★ 承接轮 12 那条**已能建马达**的链，★ 把台账点名的候选**一次试完**
  （★ **先保存装配体** + `OutputType` / `StartTime` / `EndTime` / `SaveEntireAnimation`）✓

| 项 | ★ 真机读数 |
|---|---|
| ★ `save_document(asm)` | ★ `True`（★ 装配体**保存成功**）✓ |
| ★ `create_motion_study(type=2)` | ★ `StudyType` **回读 2** ✓ |
| ★ `configure_avi_parameter(ap, OutputType=1)` | ★ **回读 `{'OutputType': 1}`** ⇒ ★ **选项真生效** ✓ |
| ★ `…(StartTime=0, EndTime=4, SaveEntireAnimation=True, FramePerSecond=10)` | ★ **回读 `{'StartTime': 0.0, 'EndTime': 4.0, 'SaveEntireAnimation': True, 'FramePerSecond': 10.0}`** ✓ |
| ⚠★ **`add_component` ×2** | ★★ **两个都回 `None`** ⇒ ★ **组件根本没加上** ✗✗ |
| ⚠ `motor_ok` | ★ **`False`**（★ 因为 c1/c2 是 `None` —— ★ 前置没成立）|
| ⚠ 导出 | ★ `avi_exists = False` · `size = 0` ⇒ ★ **这一测没意义**（★ 没马达）✗ |

★★★ **关键对照**：★ 轮 12 那次**同一段两行 `add_component` 两个都 `ok`**、★ `motor_ok = True` ✓
  ⇒ ★★ **代码没变、变的是环境** ⇒ ★ 而沙盒的收集清单**把答案摆出来了**：
  ★ 它收了 **`cyl.sldprt` 与 `cyl__1.sldprt` 两份同名文件**（★ 还有两个 `~$` **锁文件**）⇒
  ★★ 即**沙盒对输入/产物做了**拷贝与改名**，★ 而进程内"刚写出的路径"与它**不是同一份** ✗✗
  ⇒ ★★ **这佐证了轮 16 的结论**：★ **"文件位置 / 沙盒收集"才是那个自变量** ✓

★ **本轮净产出（★ 都是可复用的读数）**：
  1. ★★ **`IAVIParameter` 的候选选项"设置 → 回读"是通的**（★ 五项全回读到设定值）⇒
     ★ 所以"选项没设上"**不是**导不出文件的原因 ✓ **排除一个嫌疑** ✗
  2. ★★ **沙盒会拷贝/改名输入文件 ⇒ 进程内"刚写出的路径"可能指向另一份** ⇒
     ★ 凡"**先写文件、再把路径交给 COM**"的探针，★ 都要先想这一层 ⇐ ★ **这条会影响本仓所有这类探针** ✓
  3. ★ 上一轮那条"插子装配"的疑云，★ 现在有了**更简的候选解释**（★ 同上）✓

★ **下一轮**（★ 顺序已排好）：★ ① 若还要追 AVI：★ **避开沙盒**（★ 例如把文件放到
  `%TEMP%` 且在**同一次调用**里写+用，★ 或先用 `sw_guard --no-sandbox` 之类——★ 要查护栏有没有这个开关）
  ✗→✓；★ ② `drawing_insert_balloons`（★ 它的官方前置是**四步**，★ 选视图那条用
  `SelectByID2(<视图名>, "DRAWINGVIEW", …)`，★ 而**夹具要工程图** ⇒ ★ 够一轮做）✓

---

## ★★ T-216-07h（★ 2026-10-07）：把子装配挪到**仓库外**再试 —— ★ **结果反证了我的假设**

★ 做法：★ 复用上轮那条"最省一步"—— ★ 把 `p.sldprt` / `sub.sldasm` 建在
  `%TEMP%\t216_asm_outside\`（★ **仓库外** ⇒ ★ 不走沙盒收集）⇒ ★ 再插一次 ✓

| 用例 | ★ 真机读数 |
|---|---|
| ★ 保存零件 / 保存子装配 | ★ 文件**确实存在**（`子装配文件存在 = True`）✓ |
| ⚠★ **往子装配里加零件** | ★★ **`False`** ⇒ ★ **连这一步也失败了** ✗✗ |
| ⚠ 把子装配插进顶层装配 | ★ 同前 ⇒ 未成 ✗ |

★★ **所以我的假设被反证了**：★ 我原以为"是**沙盒/锁文件**（★ 只在仓库内、只对 `.sldasm`）"
  ⇒ ★ 而实测：★ **在仓库外、且连"插零件"这一步都失败** ⇒ ★ **不是那条** ✗
★★ **而它把干扰项暴露出来了**：★ 沙盒**把产物改名收集**（★ `p.sldprt` → `p__1.sldprt`、
  `sub.sldasm` → `sub__1.sldasm`）+ ★ 收尾又收到 `~$p__1.sldprt` / `~$sub__1.sldasm`（**锁文件**）⇒
  ★★ **文件位置/收集本身就是变量** ✓
★★★ **而有一个**对照**是清楚的**：★ 本规格 ② AVI 那次探针（★ 文件放在**仓库内** `output/_t216_avi\`）
  ★ **`add_component(asm, <part>)` 两次都 `ok`** ✓ ⇒ ★ 所以：★ **"插零件"是能成的**
  （★ 至少在那个位置、那种文件形态下）✗→✓

⇒ ★★ **结论（★ 本轮到此，★ 不硬猜）**：★ **"插子装配"这一问仍未答**，★ 但我**消掉了一个假设**
  （"沙盒/锁"）、★ **并暴露了真正的变量**（**文件位置 / 沙盒收集**）⇒ ★ 下一步该做的是
  ★ **把"位置"当自变量做对照**（★ 同一份文件、两个位置、同一段代码）✓
  ★ 按**事实 53**：★ 同一处**连续修补 ≥3 次**就该停下换做法 ⇒ ★ 本轮**只记录、不再猜** ✓

---

## ★★ T-216-07g（★ 2026-10-07）：`add_component` 插不了 `.sldasm` —— **排除了两个嫌疑，剩运行期**

★ 起念：★ 上一轮查明 `dissolve` 的夹具卡在「**把子装配插进顶层装配**」（★ 真机：
  `添加组件失败: …sub.sldasm (open_then_AddComponent5: 返回 None)`）⇒ ★ 本轮**先查这一环** ✓

★★ **逐条排除（★ 都用官方源，不猜）**：
1. ★ **形参顺序**：★ 官方 `IAssemblyDoc/AddComponent5.md` 的 `## Signature` 逐字
   「`Component2 AddComponent5( System.string CompName, System.int ConfigOption, System.string NewConfigName,
     System.bool UseConfigForPartReferences, System.string ExistingConfigName, System.double X, System.double Y, System.double Z )`」
   ⇒ ★★ 而 `sw_assembly._add_component5` 传的**正是这 8 个、顺序一致** ✓ **排除** ✗
2. ★ **`ConfigOption=0` 是否非法**：★ 官方 `swAddComponentConfigOptions_e.md` 逐字
   「`swAddComponentConfigOptions_CurrentSelectedConfig` **= 0** = Add a part or assembly in its last saved configuration」
   ⇒ ★★ **0 是合法值** ✓ **排除** ✗
3. ★ 而 `add_component` 自己**已有三级退路**（`AddComponent5` → `AddComponent4` → 打开零件后再试）
   ⇒ ★★ 真机读数：**三级全 `None`**（★ 报的是 `open_then_AddComponent5: 返回 None`）✗

⇒ ★★ **剩下的是运行期/环境**（★ 候选：★ 沙盒把产物**搬走/占住**了文件 · ★ 文件被 SolidWorks 锁
  （★ 同批收尾收到了 `~$sub.sldasm` **锁文件**）· ★ 子装配自身没保存好 · ★ 路径含沙盒临时目录）✓
★★ **故本轮不修、只记**（★ 我没有把"运行期"证到可复现的那一层 ⇒ ★ 按事实 53 **不连改三版**）✓

★ **可复用的手法（★ 本轮真正的方法论产出）**：
  ★★ **先"排除"再"猜"** —— ★ 我把两个**可用官方源判定**的嫌疑（签名 / 枚举值）**当场排除**
    ⇒ ★ 于是"剩下的只能是运行期"这句话**才是可判的**，★ 而不是"再试一次看看" ✓
  ★★ 三源都在本机：★ `C:\swapi\types\IAssemblyDoc\AddComponent5.md`（签名）·
    `C:\swapi\enums\swAddComponentConfigOptions_e.md`（枚举值）· ★ 反射转储 ✔

★ **下一轮**（★ 优先级已排好）：★ ① 验"是不是沙盒/锁文件"—— ★ **最省**：★ 把子装配**放到仓库外的临时目录**
  （★ 不走沙盒收集）再插一次，★ 一比就知道 ✗→✓；★ ② 余下 `drawing_insert_balloons`；
  ★ ③ topology 两条（★ 查控制回 `None` 的真因）✓

---

## ★★ T-216-07f（★ 2026-10-07）：`assembly_dissolve` —— ★ **改了又撤回**（★ 因为验不了）

★ 我按本仓既有形态实现了「声明式组件名」入口（★ `_select_by_id(ext, <名>, "COMPONENT")`
  + 回读计数 + 选不中就**响亮报错**）✓
★★ **而探针**建不出夹具** ⇒ 无法验证**：★ 真机逐字
  「**添加组件失败: `…\sub.sldasm` (open_then_AddComponent5: 返回 None)**」——
  ★ 即**把子装配插进顶层装配这一步就没成**（★ 而 `dissolve` 的对象正是子装配）✗

★★★ **所以我把它 `git checkout --` 撤回了**，★ 理由写明：
  ★ ① 纪律：★ **改完必须跑一次验证**才算完成（★ 未验证的改动**不该留在树上**）；
  ★ ② ★★ **更要紧的**：★ 我调了 `sw_assembly._select_by_id` ⇒ ★ 而**门禁认这个名字**
    ⇒ ★ **它当场就会把 `assembly_dissolve` 判成"已修"并从基线移出** ✗✗
    ★★ 而能力**其实还没验过** ⇒ ★ **那就是让门禁撒谎**（★ 与上一轮 topology 那个"假绿陷阱"同型）✓
  ⇒ ★ 撤回后实测：★ 门禁**仍是 `命中 5 · 基线 5`** ✓（★ 树也干净）

★ **本轮的净产出 = 两条真机发现（★ 都是"下一步从哪开始"的钥匙）**：
  1. ★★ **topology 对称/脱模**：★ 控制对象**回 `None`** ⇒ ★ 卡点在**选区之外**
     （★ 候选：研究需先有**材料／目标／激活**；★ 或该控制类型本机不支持）⇒ **待查** ✓
  2. ★★ **`assembly_dissolve`**：★ **夹具就建不起来** —— ★ `add_component` 插 `.sldasm` **回 `None`**
     ⇒ ★ 这**本身可能是一条独立的能力缺口**（★ "把子装配插进装配体"）⇒ ★ **待查** ✓
     ★ 附带：★ 沙盒收尾收到 `~$p.sldprt` / `~$sub.sldasm`（★ SolidWorks 的**锁文件**）⇒
     ★ 沙盒机制**如实把它们列出来了**（★ 不是泄漏、★ 是可见）✓

★ **下一轮**：★ 建议**先查 `add_component` 插不了 `.sldasm` 这条** —— ★ 它既卡住 `dissolve`，
  ★ 又可能是一条**独立的能力缺口**（★ 而查它**不需要新夹具**，★ 就用刚建好的 `p.sldprt` + `sub.sldasm`）✓

---

## ★★ T-216-07e（★ 2026-10-07 · topology 对称/脱模）：**改了、但没通**（★ 如实记）

★ 改动：★ 两条各加**声明式** `selection` / `selection_kind` + 助手 `_apply_declarative_selection`
  （★ 自己取**活动文档** —— 拓扑研究就在它上面；★ 事实 503：注入解析器会清空选区）✓

| 用例 | ★ 真机读数 |
|---|---|
| ★ 反例 `selection="index:99"` | ★ `EntitySelectionError: FACE 序号 99 越界（体 0 上共 6 个）` ⇒ ★ **证明选区代码跑到了** ✓ |
| ⚠ 正例（对称 / 脱模）| ★ **`CreateSymmetryControl 未返回对象`** / **`CreateDemoldControl 未返回对象`** ⇒ ★ **控制仍建不出** ✗ |

★★ **两条真机订正**：★ ① 选区原先放在 `_configure()` 里 ⇒ **太晚**（控制对象根本没建出来）
  ⇒ ★ 即**控制是"从当前选区建出来的"** ⇒ ★ 已改到 `Create*Control` **之前** ✓
  ★ ② 而**改对位置后仍然回 `None`** ⇒ ★ 卡点在**别处**（★ 候选：研究需先有材料／目标／激活；
  ★ 或该控制类型本机不支持）⇒ ★ **列为新待查项** ✓

★★ **我刻意避开了一个"假绿陷阱"**：★ 门禁的判据是「函数有没有选区入口」⇒ ★ 若我把助手命名成
  `select_*`，★ 门禁**当场就会把这两条判成已修、从基线移出** ✗✗ 而**能力其实还没通** ✓
  ⇒ ★ 改名 `_apply_declarative_selection`（**不含** `select_` 前缀）⇒ ★ 门禁**继续标它们**
  （★ 实测 `命中 5 · 基线 5` **不变**）✓ ★ 与本规格一贯的分法一致：「**入口修好 ≠ 效果验证**」✓

★ 附记（★ 探针侧的坑，★ 不是源码 bug）：★ `sw_topology` 用**相对导入** ⇒ ★ 顶层 `import sw_topology`
  会得到 `out_i4` **未绑定**的副本 ⇒ ★ 复验脚本要用**包内导入** `import scripts.sw_topology` ✓


---

## ★★ ② AVI（★ 2026-10-07 · 本轮）：**先把前提订正，再把边界收窄**

★ 读数与依据见 [recon/avi-boundary.md](recon/avi-boundary.md) ✓

★★ **前提订正**：★ 我在目标里引的是台账 **第 4 版**（「需要 `CosmosMotion` 类算例」），
  ★ 而那是**六版演进**里的一版 —— ★ **最终版（轮 288/289）**说的**是另一条、可修的链**：
  「组件插入时零件文件没保存好 ⇒ 组件未解析 ⇒ 面上没几何 ⇒ 找不到圆柱面 ⇒ 马达建不出 ⇒ 空文件」✓
  ⇒ ★★ **两版不是一回事**（★ 前者是"算例类型不可得"、★ 后者是"建件链断了"）⇒ ★ 只看一版就会误判 ✓

★★ **本轮实测（走护栏 · 9.8 s · 0 弹窗）**：★ 按**文档写法**建件
  （`with sw_part.sketch(...)` + **毫米**）后 ⇒ ★★ **轮 288 的卡点不复现**：
  ★ `save_document` **成功** · `add_component` ×2 ✓ · `create_motion_study(type=2)` 回读 **2** ·
  ★★ **`add_constant_speed_rotary_motor_by_cylinders` ⇒ `motor_ok = True`** · `calculate` ✓ ·
  ★ `create_avi_parameter` / `configure_avi_parameter` / `export_motion_study_avi` 全 ok ✓
  ★★ **唯一仍失败的**：★ **`avi_exists = False` · `size_bytes = 0`** ⇒ ★ 判据（★ 文件 > 0、★ 不看返回值）**未过** ✗

★ **两条路分清**：★ **CosmosMotion 家族（4/8/16）**⇒ 本机**静默降级**、★ 加载项 4 个 ProgID 全 `None`
  ⇒ **不可得**（★ 机器／许可边界）✗；★ **PhysicalSimulation(2)** ⇒ ★ **除导出外全通** ✓
★ ⇒ ★★ 本轮**只声明边界收窄**、★ **不声明已解决**（★ 台账记过「保存装配体 + 先 Play ⇒ 仍 False」）✓


---

## ★★ T-216-07d（★ 2026-10-07 · `sketch_stretch` —— ★ 只修好"前置"那一半）

★ 读数与机制见 [recon/bd-declarative-selection.md](recon/bd-declarative-selection.md) §五 ✓

| 项 | ★ 结果 |
|---|---|
| ★ **前置（选区入口）** | ★★ **修好并真机确证**：★ `selected_count = 4`（★ 矩形四条段**全选上**）✓ |
| ⚠ **效果（伸展真的改了几何吗）** | ★★ **未确证** —— ★ `bbox_before/after` 与 `transform_before/after` **全 `None`** ⇒ ★ `ok = None`（★ 工具**如实报"量不到"**）✗ ⇒ ★ **列为新的待查项**（★ 本轮**不声称**效果成立）✓ |

★ 机制与前面几条**不同**：★ 草图段**既不是** FACE/EDGE/VERTEX、**也没有名字**（事实 32）
  ⇒ ★ 用不了 `resolve_selection` ⇒ ★ 换官方 `ISketch::GetSketchSegments()` + `ISketchSegment::Select4` ✓
★★ **两件事分开记**（★ 本仓既有纪律正是"注册 ≠ 能跑"）：
  ★ **入口修好** ≠ ★ **效果验证** ⇒ ★ 门禁收掉本条（★ 它的判据就是"有没有选区入口"），
  ★ 而"效果取不到读数"**另立待查项** ✓


---

## ★★ T-216-07 第二批（★ 2026-10-07 · 又两条真机复验通过）

★ 读数与顺序约束见 [recon/bd-declarative-selection.md](recon/bd-declarative-selection.md) §四 ✓

| 工具 | ★ 真机读数 |
|---|---|
| `selection_point`（诊断型）| ★ `ok=True` · `selection_count=1` · ★ **`point_mm = (-50.0, 0.0, -10.0)`** ✓ |
| `section_properties`（官方前置）| ★ `ok=True` · `status=0.0` · ★★ **`area = 1200.0`** · `entry_used = GetSectionProperties2(property)` ✓ |

★★ **精确交叉验证**：★ `area = 1200.0` **恰是 60×20 端面面积** ⇒ ★ 说明选区**建对了**，
  ★ 且顺带证明「`with sw_part.sketch(...)` + 毫米数」建出的**正是 100×60×20 的板** ✓
★★ **一条本批特有的顺序约束**：★ `section_properties` **自己**会"**清空并重写选择集**"（官方 Remarks 逐字）
  ⇒ ★ 「**选一次、读一次**」这个配对**不能被打断** —— ★ 代码里选择那行**紧贴**在读取之前 ✓
  （★ 不是风格问题，★ 是**语义要求**）✓

★ 门禁自动跟着变：★ 「命中 8 · 基线 8」⇒ ★ 「**命中 6 · 基线 6**」✓


---

## ★★ T-216-07 的首批（★ 2026-10-07 · B 型 1 条 + D 型 1 条）

★ 读数与修法见 [recon/bd-declarative-selection.md](recon/bd-declarative-selection.md) ✓

| 型 | 工具 | ★ 真机读数 |
|---|---|---|
| **B** | `measure_selection` | ★ `ok=True` · `selected_count=1` · `applicable=['area','perimeter']`（★ 反例 `index:99` ⇒ 响亮报错）✓ |
| **D** | `part_axis` | ★ `ok=True` · ★ **特征树增量 `['基准轴1']`**（★ 并查明圆柱面 = `index:0`）✓ |

★★ **与圆顶那次的区别（★ 定义 B/D 型的理由）**：★ 圆顶"给哪个面"**可以随便定**；
★ 而 **"量什么 / 用哪个几何建轴"是调用方的意图** ⇒ ★ **绝不能由函数乱造**（★ 造了的话结果不是你要的、
★ 而且**看不出来**）⇒ ★ 这六条**一律让调用方声明** ✓

★★ **顺带发现（★ 已记档、本轮未动）**：★ `sw_part.sketch()` 是**上下文管理器**（必须 `with`）；
★ 且**本模块长度单位是毫米**（★ 它 docstring 逐字警告「不要写 `mm(25)`」）——
★ 而仓库自己的 `tools/verify_costing_e2e.py` **两样都没按这个来**，★ 却**跑得出真结果**
⇒ ★ 说明**有些助手容忍、有些不容忍**（`sketch_circle` 有守卫、`sketch_corner_rectangle` 没有）⇒ ★ **列入待查** ✓


---

## ★★ T-216-06c（★ 2026-10-07）：把两条"待办"变成**有依据的裁定**

★★ **本规格反复出现的一种收口**：★ 名单里挂着的东西，★ 读完第一现场之后**常常不是"待修"** ——
  ★ 它可能是「**当初被误报**」（2 条 · T-216-05）、★ 「**已经修好**」（2 条 · T-216-06b/06b-2）、
  ★ 或「**本后端走不通、该记缺口**」（本条）✓

| 项 | ★ 处置 |
|---|---|
| `solidworks_part_insert_composite_curve` | ★ 基线 `verdict`：★ `真危险·官方前置` ⇒ ★★ **`已定性·后端墙（★ 不修 —— 不是「待修」）`** ✓<br>★ `reason` **保留原文**、**前面加改判说明、后面加依据**（★ 补正而不删除）✓<br>★ 台账 `modeling_feature_readback_tools` 同步补一条 ✓ |
| ★ 依据（★ 台账逐字） | ★「累计 **6 种选法全部失败** … `IEntity.Select4` **没有 mark 参数**、而 `SelectByID2` 需要**名字**、**边与草图段都没有名字** ⇒ 「选中 2 个实体 + mark=1」这个官方前提，**在这条后端上我没能同时满足**」（★ 已按事实 53 强停）；★ 另：★ 官方入口 `InsertCompositeCurve()`（零参、回 `Boolean`、要 mark=1）★ 真机返回 **False** ✓ |
| ★ 为什么**仍留在名单里** | ★ 因为**判据上它确实还命中**（★ 缺选区入口这件事没变）⇒ ★ 名单的语义是「**已知的命中**」，★ 而它的 `verdict` 已经写明「**已裁定不修**」⇒ ★ 不会再有后人把它当待办 ✓ |

★ 读数：★ `check_preselect_family.py` ⇒ ★ **命中 10 · 基线 10 · 无新增无腐坏**（exit **0**）✓
★ 收尾：★ `release_check` 第 1 轮 OK · 7 passed ✓
⚠ **我这一轮又踩了一次事实 48 那个坑**（Python 串里混 ASCII 双引号 ⇒ 语法错）——
  ★ 累计**第四次** ⇒ ★ 已改成全程用「」，★ 这条得记进纪律（★ 写进本规格的 `recon/` 或直接改 `AGENTS.md` 的写法段）


---

## ★★ T-216-06b-2 的真机读数（★ 2026-10-07 · 参考点）

★ 改动：★ `sw_ref_geometry.insert_reference_point` **新增声明式 `selection` / `selection_kind`**
（★ 规则 3 禁裸坐标；★ 合法形式 `index:<n>` / `__current_selection__`）+ ★ **在紧邻
`InsertReferencePoint` 之前**自己选（★ 那一句顺序要求**就是**台账原文的出处）✓
★ 跑法：`python tools/sw_guard.py --timeout 600 -- python output/_t216_refpoint_verify.py`（★ **0 弹窗**）✓

| 用例 | ★ 读数 |
|---|---|
| ★ 正例 `insert_reference_point(doc, 4, selection="index:0", selection_kind="FACE")`（★ 不预选）| ★ `ok=True` · ★ **特征树增量 `['点1']`** · 7 → **8** ✓ |
| ★ 反例 `selection="index:99"` | ★ `ok=False` · ★ 「选区未建立：FACE 序号 99 越界（体 0 上共 6 个）（★ 前置未成立、★ 与「点建不出来」是两件事）」✓ |

★ 门禁自动跟着变：★ 命中 11 → **10**（★ 参考点离开名单）✓
★ 顺带把"移出基线"这件事**做成了通用脚本**（`output/_t216_baseline_trim3.py`：
★ 它**直接问门禁现在命中哪些**、差集就是要移出的 —— ★ 不再靠人读名单，★ 那正是"名单腐坏"最易出错处）✓
**

---

## 一、T-216-05 的产出（2026-10-07）

★ 交付物：[precall-plan.md](recon/precall-plan.md) —— ★ 14 条**逐条读目标函数体**后的判型 ✓

| 型 | 条数 | ★ 判据（读到的原文） |
|---|---|---|
| ★★ **假阳性** | **2** | ★ 函数**自己就会选** —— `_select_by_id(asm_model.Extension, component_name, "COMPONENT")` · `SS.select_entity_by_index(model, "FACE", int(face_index))` ＋**随后回读计数、为 0 就报错** ✓ |
| **A** 造选区 | **6** | 零选区 token 且官方要求先选：`insert_dome` · `insert_composite_curve` · `insert_reference_point` · `section_properties` · `dissolve_assembly` · `sketch_stretch` |
| **B** 读"当前"选区 | **3** | 语义**就是**读当前选区：`selection_point` · `measure_selection` · `drawing_insert_balloons` |
| **D** 需指定参照 | **3** | 参照**有语义**、不能乱造：`part_axis` · `topology_create_demold_control` · `topology_create_symmetry_control` |

### ★★ 假阳性 2 条 —— 已修（本轮的实质产出）

★★ **不是"修好了"，是当初就被误报** ✗：★ 门禁 `SELF_SELECT` 当时只认**裸 COM 调用**
（`SelectByID2` / `Select4(` …），★ 而这两条用的是**本仓自己的助手** ✓

★ 修法两件：
1. ★ **补 token 集**（`_select_by_id` / `select_entity_by_index` / `_select_faces_for` /
   `_select_com_object` / `select_component_by_name`）—— ★ 并**配一个新负例**
   `test_helper_style_self_selection_is_not_flagged`（5 个助手名逐个过）✓
2. ★ **移出基线**（14 → **12**）—— ★ 棘轮**双向**：不再命中的必须移出；
   ★ 并把"为什么移出"写进 `docs/preselect-family-baseline.json` 的 `_comment`（★ 知识不丢）✓

★ 读数：`python scripts/check_preselect_family.py` ⇒ ★ **命中 12 · 基线认可 12 · 无新增无腐坏**
⇒ **exit 0** ✓ · ★ 门禁测试 **7 passed**（原 6 + 新负例）✓

⚠ 与两处旧账**同型**（★ 值得记住）：`audit_byref_args.BYREF_OK` 只认**裸名**、
`check_probe_reuse` 判据过宽 ⇒ ★★ **判据必须覆盖「本仓自己常用的写法」** ✓

---

## 二、① 的范围被订正了**两次**（★ 病根都是"没先读第一现场"）

| 我以为 | 读原文之后 | ★ 依据 |
|---|---|---|
| 只有 "官方前置" **9** 条要修，另 5 条"不动" | ★ **14 条全是待修** | ★ 基线里 **14 条的理由全都写着**「★★ 待修工作项（不是「已认可」）」—— ★ "显式拒"那 3 条是**经工具层必然失败**、"诊断型"那 2 条读到的是**被清空的**选区 ✓ |
| 14 条都要改工具 | ★ **12 条要改，2 条是门禁假阳性** | ★ 逐条读函数体（见上表）✓ |

★★ **教训**：★ 我**三次**都是"没先读第一现场就下判断"（AVI 前提 · costing 状态 · 预选族范围）⇒
★★ **动手前先读该能力的 `limitations` 与基线原文** ✓

---

## 三、③ costing 的产出（★ 已提交）

- ★ 真机复跑（**走护栏**：`python tools/sw_guard.py --timeout 600 -- python tools/verify_costing_e2e.py`
  ⇒ 15.9 s、0 弹窗）⇒ ★ **`verdict: pass`** · `assertions` **3/3** ✓
- ★★ **顺带修掉一个真缺陷**：`connect_solidworks` 的 `metadata` **从来没有 `revision` 键**，
  而 `tools/verify_costing_e2e.py` 读的正是它 ⇒ ★ 证据 `solidworks_revision` **恒为空串** ✗
  ⇒ ★ 复用既有 `get_sw_version()` 补键（★ 防御式：失败记 `None`、不拖垮连接）+ verifier 加 `or ""`
  ⇒ ★ **真机证明**：修前 `''` · 修后 **`'34.4.1'`** ✓
- ★ 台账订正**两处**（`costing` · `costing_readback`）—— ★ 一律"**追加 + 标注旧条作废**"、**不删历史** ✓
- ★★ 并**升级了一条被订正触红的契约守卫**（★ **不删**）：`test_ledger_verdict_matches_evidence`
  原把「文件**确实是** partial」**钉成前提** ✗ ⇒ ★ 升级成**真正的不变量**「**台账现状句 ⟺ 文件原句**」
  （★ V-1 抱怨的是"**不一致**"、不是"必须是 partial"）· ★ **负例已证**（抹掉现状声明 ⇒ 当场红）✓
- ★ 全量 pytest ⇒ ★ **2404 passed / 0 failed**（427 s）✓

---

## 四、② AVI —— 前提被订正（★ 未开始）

★ 我原写「根因是缺 Motion 加载项」✗ —— ★★ **台账 2026-10-01（轮 285）就已订正过这句**
（L1611 逐字：「原写『缺 Motion 加载项』—— ★ 而实测那条**不成立**」）✓
★ 本机体检也一致：`swmotionstudy.tlb` **存在且 `ready: true`** ⇒ ★ 类型库从来不是阻塞点；
★★ 台账 **L3189 明确警告**：`ensure_motion_type_library` **答不了「AVI 能不能导」** ✓
★ **真结论（L1619）**：🔴 `SaveToAVI` 需要 **`CosmosMotion` 类算例**、本机拿不到；
★ 另有两条实测事实：4 个 Motion ProgID 全返 `None` · ★ **返回码会撒谎**（不 `Calculate` ⇒
返 `True` 而文件 **0 字节**）⇒ ★ 判据固定为「**文件存在且大小 > 0**」、★ **不看返回值** ✓

---

## 五、纪律（★ 用户 2026-10-07 订正）

> 「**第 3 点我允许你开，我从没说过不准开啊，纪律是开了用完要关**」

★★ **订正我此前的误读**：★ `AGENTS.md` 规定的是**怎么开**（真机命令一律走 `tools/sw_guard.py`：
弹窗护栏 + 硬超时），★ **不是"不许开"**；★ 而"零真机"是我**自己**写进 `specs/214`/`215` 的额外约束 ✗
（★ 规格已提交 ⇒ 按 Flow-forward 不改，★ 订正记在本规格）✓
★ **连续两轮都按正确纪律执行**：★ 真机命令走护栏 ✓ · ★ 收尾 `round_chain` 关掉 SolidWorks ✓

---

## 下一个动作（只写一条）

★ **T-216-06b**：★ 实现 `insert_dome` + `insert_reference_point` 两条**可修**的（★ T-216-06a 已把依据捞齐）：
· ★ `insert_dome` ⇒ ★ **两步式选面**（先 `mark=0` 选一次 → `ClearSelection2(True)` → 再 **`mark=1`**，
  ★ 形态由既有冒烟 `tools/verify_dome_smoke.py` L133-139 证明 **9/9**）+ ★ **声明式选择器入参**
  （★ 规则 3 **不许工具收裸坐标**）✓
· ★ `insert_reference_point` ⇒ ★ 选区**必须紧邻调用**（★ 台账逐字：「中间隔别的步骤会把选区清掉」）✓
→ 验收: ★ 每条**两段**真机读数 —— ★ ① 选区计数 > 0 · ★ ② **特征树增量**（★ 不看返回值）；
★ 批末 `python scripts/check_preselect_family.py` 仍须退出 0 ✓

## ★★ T-216-06b 的**真机读数**（★ 本轮已跑，见 [recon/dome-mark-path.md](recon/dome-mark-path.md)）

★ 跑法：`python tools/sw_guard.py --timeout 600 -- python output/_t216_dome_mark_probe.py`
⇒ ★ 20.7 s · ★ **0 弹窗** · ★ `aborted_for_llm: false` ✓

| 格 | 形态 | ★ 结果 |
|---|---|---|
| **B** | ★ 既有冒烟逐字那一串（按点 `SelectByID2` → 清选 → **mark=1**）| ★★ **成立** —— `mark_after=1` · ★ **`tree_delta = ['圆顶1']`** · 特征 7 → **8** ✓ |
| **A** | ★ 我原打算走的**选择器**路 | ★ **第一跳就失败** ⇒ ★★ **更正我一个假设**：`'+z'` **不是** `sw_selection_spec` 认的选择器（★ 合法只有 `__current_selection__` / `index:<n>` / COM 对象）✗ |

★ 仍未定（★ 如实记）：★ `SetSelectedObjectMark(AtIndex, Mark, Value)` 的**第 3 参语义**
（★ 格 A 没走到那一步）⇒ ★ 两条路可选：★ 实测它 · ★ 或走**格 B 那条已证明的按点+mark 路** ✓
⇒ ★ **下一步**：★ 用**声明式 `face_index`**（规则 3 禁裸坐标）+ 工具**自己**在面上算点
（`IFace2::GetClosestPointOn`，arity 3，反射里有）+ 照格 B 选面 ⇒ 判据取**特征树增量** ✓

★ **T-216-06c**（可并行）：★ `insert_composite_curve` ⇒ ★ **不修**，走"如实记为能力缺口"
（★ 依据：台账逐字「**6 种选法全部失败**」+ `Select4` 无 mark、边与草图段无名字 ⇒ **后端墙**）✓

---

## ★★ 本轮附带发现：`read_only` 与效应体系**一族不一致**（★ 已修 1 条、记档 6 条）

★ 见 [recon/read-only-vs-effects.md](recon/read-only-vs-effects.md) ✓
★ 病灶：★ `effective_read_only` 的**判序第一是「显式声明优先」**⇒ ★ 只要 ToolSpec 写着 `True`，
  ★★ 「效应体系说它有写」与「台账裁定它不许标只读」**一律被架空**，★ 而**没有任何门禁在守** ✗
★ **已修**：`solidworks_section_properties` —— ★ 台账**有明文裁定**（官方 Remarks 逐字
  「**This method clears the selection set**」⇒ 它清空并重写选择集 ⇒ 不许标 `read_only`）✓
  ⇒ ★ `read_only=True` → **`False`**（`effective_read_only` 实测由真→假）· ★ 并把「⚠ 不是只读」
  **提到文档首句**（★ lean 只保首句 —— 规格 215 的纪律）✓ · ★ 相关测试 **27 passed** ✓
★ **未修 6 条**（★ 同一族：显式 `read_only=True` 而 `writes=('document',)`）——
  ★★ **先不修的理由**：★ 台账对这 6 条**没有裁定** ⇒ 改它们就是**我替项目定政策** ✗；
  ★ 且需要先回答一个**规范问题**：★「**只动选区、不动几何**算不算只读？」★（体系里 `selection`
  是状态类之一 ⇒ 按体系不算；★ 而 MCP 的 `readOnlyHint` 语义是"客户端能否自动重放"⇒ **两者口径不同**）✓



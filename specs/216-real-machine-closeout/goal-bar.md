# 规格 216 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看上面那一行。

**阶段：★★★ 预选族 **12 → 6**：★ 真修好 **6 条**（圆顶 `+圆顶1` · 参考点 `+点1` · 测距 `ok+area` · 参考轴 `+基准轴1` · 选区点 `point_mm` · 截面属性 **`area=1200.0` 与几何精确对上**）· ★ 改判 1 条（composite_curve ⇒ 已裁定不修）· ★ 误报移出 2 条 · ★ **剩余 6 条**（`assembly_dissolve` · `drawing_insert_balloons` · `part_insert_composite_curve`（已裁定不修）· `sketch_stretch_entities` · topology `demold`/`symmetry`）· ★ ② AVI 未开始 · ★ 当前动作 = **T-216-07c**（余下 5 条）

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



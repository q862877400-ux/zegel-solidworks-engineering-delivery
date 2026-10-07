# 规格 216 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看上面那一行。

**阶段：★ ③ 台账订正完成（`a89358f7` / `32cdbf44` / `3197d27b`）· ★★ T-216-05 完成 —— 14 条判型落地，并查出**其中 2 条是我那道门禁的假阳性**（已修门禁 + 移出基线 ⇒ **实数 12**）· ★ 剩余：**A 型 6 · B 型 3 · D 型 3**（未修）· ★ ② AVI 未开始 · ★ 当前动作 = **T-216-06**（A 型逐条加 `pre_call`）**

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

★ **T-216-06**：★ 给 **A 型 6 条**逐条加 `pre_call` —— ★ 形状照
`mcp-server/tool_specs_batch74.py` 的 `_select_faces_for`（★ 事实 503：`pre_call` 在**注入之后**跑
⇒ 那时选区已被清空 ⇒ **必须重建**）✓
★ **每条先定"选什么"的判据**（★ 不许乱选）：★ 首选"**唯一实体**"或"**参数指定的序号**"，
★ 判据写进 ToolSpec 注释 ✓
→ 验收: ★ 每条**两段**读数 —— ★ ① 选区计数 > 0 · ★ ② **特征树增量**（★ 不看返回值）；
★ 批末 `python scripts/check_preselect_family.py` 仍须退出 0（★ 命中数应随修随降）✓

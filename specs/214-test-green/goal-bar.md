# 规格 214 · 目标栏（唯一进度字段）

> ★★ **本文件是唯一进度字段** —— 进度只看上面这一行；其余段落是上下文，不是判据。

**阶段：★ A 阶段（A1 九条稳定红）**全部收口** —— 九条逐个单跑 ⇒ **79 passed / 0 failed**（112 s）· ★ A2（顺序污染）尚未开始 · ★ 当前动作 = **T-214-11**（建复现装置）**

---

## 当前状态

★ **规格 214 立起**（2026-10-07，接手轮），起因是用户指令
「**按照 spec 规范自动进行，设置好目标，我给你替我拍板的授权**」✓

★★ **为什么单独立一个规格**：全量 pytest **18 failed** 这件事，
★ **不是"某个功能没做完"，而是"仓库的收口读数一直是红的"** ——
★ 它挡住的是**任何一次「结项时跑全量回归」**（AGENTS.md 的收口纪律要求全量绿）✓

### ★★ A 阶段进展（★ 逐条读数，不估数）

| 任务 | 项 | 真因（★ 都不是"改测试绕开"）| 结果 |
|---|---|---|---|
| T-214-01 | `test_mcp_protocol_layer` | 钉死数 **339** 过期；真值 **504** 已由**两条独立通路**复算（真握手 504 = 491+13；本测试自己的计数器 45+459）| ★ **8 passed** ✓ |
| T-214-02 | `test_effect_declarations` | 生成物与真源分叉 ⇒ **跑生成器**（★ 不手改生成物）| ★ **15 passed** ✓ |
| T-214-03 | `test_registry_wiring` | `RESOLVERS['sketch']` **登记了却没有任何 spec 用**（`inject="sketch"` 0 处）⇒ 走该测试给的第二条路「删掉并说明」+ 墓碑 | ★ **5 passed** ✓ |
| T-214-04 | `test_sketch_slot_params` | ★ **实现是对的**（`0, 0, 2.0*float(radius)` 逐字在）；★ 是测试的**正则**停在"直呼方法"的旧形态（现走 `get_com_member(..., "CreateSketchSlot", …)`）| ★ **5 passed** ✓ |
| T-214-06 | `test_no_bare_byref_args` | ★ **审计器自己的假阳性（第二次同类）**：`BYREF_OK` 只认裸名，而 `sw_connect.out_i4()` **是本文件自己点名的正确形态** | ★ **3 passed** ✓（88 s）|
| T-214-07 | `test_com_member_helpers` | ★ 判据 `hasattr` **看不见"函数内导入"**（★ 本仓既有模式）⇒ 加"源码级导入"判据 + **补负例** | ★ **4 passed** ✓ |
| T-214-05 | `test_real_gap_triage_contract` | ★ **分类器是对的**：`get_study_manager` 已是已挂工具 `solidworks_simulation_get_study_manager` 的实现 ⇒ 判 `已有` ⇒ **样本过期**（★ 该测试自己写明"被挂上就该来更新样本"）| ★ **30 passed** ✓ |
| T-214-08 | `test_tool_specs_batch79` | ★ **计数过期**：宏族 8 → **9**（多的那个是规格 209 B4-1 的 `solidworks_macro_record_lines`）| ★ **6 passed** ✓ |
| T-214-09 | `test_sw_connect_open_document` | ★ **桩说谎**：`monkeypatch … lambda _sw: True`，而真契约回 dict ⇒ `restore_default_templates` 里 `True.get(...)` 炸（★ 报的错与本测试要验的东西**无关**）| ★ **3 passed** ✓ |

★★ **A 阶段合计：79 passed / 0 failed** ✓ —— ★ 其中**只有一处**动到生产代码
（`mcp-server/register_capabilities.py` 删死接线 · `scripts/audit_byref_args.py` 扩判据），
★ 其余都是**桩/样本/计数/正则随事实与契约更新**，★ **没有一处放宽断言** ✓

**★ 起点基线（保留，便于对账）**

| 项 | 读数 | 出处 |
|---|---|---|
| 全量 pytest | ★ **18 failed / 2374 passed / 20 skipped**（514 s） | `python -m pytest tests -q` |
| 其中 **A1 稳定红** | ★ **9** ⇒ ★ **现已全绿** | ★ 逐文件单跑实测 |
| 其中 **A2 顺序污染** | ★ **9** | ★ 同上 |
| `release_check` | ★ **33 道全绿** | `python scripts/release_check.py` |
| ★★ **已修的一条 A2 通路**（规格立起前） | `sw_connect` 桩缺 `deg` ⇒ 收集期炸 ⇒ 连带 8 条 | 复现装置 **23 failed → 49 passed** ✓ |
| ⚠ 但全量**仍是 18** | ⇒ ★★ **第二个污染源未找到** | 见 `tasks.md` T-214-11..13 |

**★ 已排除的假线索（★ 记下来免得重跑）**

- ★ `test_gate_details_exposed_for_every_gate` 一度红 —— ★ **不是缺陷**，是我**在它 5 分钟的运行期间
  改了 `release_check.py`** ⇒ ★ 复跑即绿 ✓（★ 由此得一条纪律：**跑长测试时不要编辑它要读的文件**）✓
- ★ `test_uncalled_helpers` / `test_uncalled_exempt_has_reason` 一度红 —— ★ **是我自己引入的**：
  我把公开名 `list_buttons` 登记进豁免表，★ 而那张表**只收 `_` 开头的私有辅助**（有元判据在守）⇒
  ★ 已改走「删掉 + 墓碑」那条路 ✓

---

## 下一个动作（只写一条，免得没人知道该恢复哪个）

★ **T-214-11**：建 **A2 复现装置** —— ★ 已知受害者（`test_rule3_*` · `test_spec212_rule2b_gate` ·
`test_sw_part_sketch_selection` · `test_tool_specs_batch92`）**先单独跑一遍确认全绿**，
★ 再按**收集顺序前缀**与它们拼跑，★ 找出能**稳定复现**「单跑绿、全量红」的那一段 ✓
→ 验收: `python -m pytest tests/test_rule3_declarative_selection_is_enforced.py tests/test_spec212_rule2b_gate.py tests/test_sw_part_sketch_selection.py tests/test_tool_specs_batch92.py -q` ⇒ 先记**基线读数**，★ 再给出「能复现红的命令」并落盘 `specs/214-test-green/recon/order-pollution.md`

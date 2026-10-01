# Tasks: B 级缺口分诊

**Input**: [spec.md](spec.md) · [plan.md](plan.md)

**格式**：`[ID] [P?] [Story] 描述` —— 每个任务带 `→ 验收:`

**状态**：**全部完成**（轮 86）。

---

## Phase 0: 从最小的域撞（**先找具体反例**）

- [x] **T-601** 读覆盖矩阵，挑出缺口最小的几个域
  **✅** ⑨ 模具（缺 **3**）· ⑬ 仿真/Motion（缺 4）· ② 参考几何（缺 4）· ⑧ 焊件（缺 5）。
  `→ 验收:` `Select-String docs\union-coverage-matrix.md -Pattern '### ⑨ 模具'`

- [x] **T-602** ★ 查模具那 3 个「缺口」我们到底有没有
  **✅** **2 个有**：`solidworks_mold_parting_line` / `solidworks_mold_shut_off_surface`
  （都在 `mcp-server/tool_specs_batch1.py`）· `tooling_split` **真的没有**。
  ⚠ **有了具体反例才值得往下查**。
  `→ 验收:` `Select-String mcp-server\tool_specs_batch1.py -Pattern 'mold_parting_line'`

---

## Phase 1: 量清两个口径（**不合并**）

- [x] **T-603** 写 `tools/probe_exposure_surface.py`，量两个来源
  **✅** `server.py` 装饰器 **45** · `tool_specs_batch*.py` **20** · **交集 0** · 合并 **65**。
  `→ 验收:` `python tools/probe_exposure_surface.py`

---

## Phase 2: 修暴露面（**一处**）

- [x] **T-604** 修 `build_union_map._our_tools()`：两个来源都读
  **✅** 45 → **65**；docstring 写明**为什么**与**两个口径仍不可合并**。
  **复算**：并集 384 → **404** · 本仓库独家 35 → **55**。
  `→ 验收:` `python tools/build_union_map.py`

---

## Phase 3: 找根因（**读实现，不猜**）

- [x] **T-605** 实测 `_normalize` 对同一条操作在两边的输出
  **✅** `solidworks_mold_parting_line → mold_parting_line` **≠** `parting_line`
  ⇒ **`_normalize` 不剥域词** ⇒ 同一条操作归一成**不同的键**。
  `→ 验收:` `python -c "from build_union_sources import _normalize; print(_normalize('solidworks_mold_parting_line'))"`

---

## Phase 4: **决定不修主匹配器**（纪律）

- [x] **T-606** 按已知事实 53，**不给主匹配器加模糊启发式**
  **✅** `tools/build_union_sources.py` **一个字没动**；339 仍是**严格名口径**的诚实数字。
  ⇒ 另出分诊表，用**有原则的规则**（域词 vs 动词）。
  `→ 验收:` `git diff --stat tools/build_union_sources.py`（应为空）

- [x] **T-607** 写 `tools/triage_union_gaps.py` + 生成 `docs/union-gap-triage.md`
  **✅** 四类：别名（强）**26** · 别名（弱）**37** · 后缀候选 **144** · 真缺 **132**。
  `→ 验收:` `python tools/triage_union_gaps.py`

---

## Phase 5: ★ **抽验自己的规则**（**最值钱的一步**）

- [x] **T-608** 抽 10 条「后缀候选」，核对是不是同一个操作
  **✅** **约一半假阳性**：
  ```
  ✅ parting_line→insert_parting_line · export_drawing_pdf→export_to_pdf
     · add_dimension→add_dimension · create_mate→add_mate
  ❌ shut_off_surface→create_bspline_surface（都是 surface，但不是 shut-off）
     · set_material→add_render_material · create_section_view→activate_view
     · get_mass_properties→apply_visual_properties
  ⛔ 正确拒绝: run_simulation · unfold_sheet_metal
  ```
  `→ 验收:` 见 [converge.md](converge.md) §2.3

- [x] **T-609** 按事实 53 **不调规则**，改为三件处置
  **✅** ① 改名「**后缀候选（需人工核）**」；② **把抽验率写进工具输出**；
  ③ 报告写明**只用于定范围**。
  `→ 验收:` `python tools/triage_union_gaps.py`（末段应打印抽验警告）

---

## Phase 6: 收工

- [x] **T-610** [P] 15 道门禁 + 生成物刷新
  `→ 验收:` `python scripts/release_check.py`（exit 0）

- [x] **T-611** 全量回归
  `→ 验收:` `python -m pytest tests -q`（970 passed / 17 skipped / 0 failed）

- [x] **T-612** 两仓库各自 commit
  `→ 验收:` `git -C C:\swprojects\sw-skill-fork log --oneline -1` + `git -C D:\AI\SW log --oneline -1`

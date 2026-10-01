# 029 · Tasks（全部完成，轮 110）

- [x] T-2501 写 `tools/probe_obsolete_members.py`（只读）
  `→ 验收:` `python tools/probe_obsolete_members.py`
- [x] T-2502 跑 ⇒ **38 条候选**
- [x] T-2503 ★ 自动消歧（是否也调了后继）⇒ 7 条假阳性
- [x] T-2504 ★ 抽查高价值条目 ⇒ `GetMassProperties` / `GetRenderMaterials` /
       `Add2` / `Delete` / `Name` / `GetModelDoc` 等**均为假阳性**
- [x] T-2505 ★ 核实 **8 条为真**（`sw_sketch.py` 的 6 个 `ISketch` 取法 + `AddMate5` + `GetBodies2`）
- [x] T-2506 落台账 `docs/obsolete-member-candidates.md`（**不拦发布**）
  `→ 验收:` `Select-String docs\obsolete-member-candidates.md -Pattern '不能.*做成门禁'`
- [x] T-2507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

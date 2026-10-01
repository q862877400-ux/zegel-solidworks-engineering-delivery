# 030 · Tasks（全部完成，轮 111）

- [x] T-2601 从台账取 6 条候选
- [x] T-2602 ★ 查后继形状 ⇒ **5 个零参 + `GetLines2` 带参**
- [x] T-2603 取 `swCrossHatchFilter_e`（两源，确认无冲突）
- [x] T-2604 改 `sw_sketch.py`（登记表 + 6 个取法 + 新常量）
- [x] T-2605 同步测试 `tests/test_sw_sketch_contract.py`（**12 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`
- [x] T-2606 ★ **复跑探针**验证这 6 条已消失
  `→ 验收:` `python tools/probe_obsolete_members.py`
- [x] T-2607 更新台账（标为已处置 + 写明"仍未真机验过"）
- [x] T-2608 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

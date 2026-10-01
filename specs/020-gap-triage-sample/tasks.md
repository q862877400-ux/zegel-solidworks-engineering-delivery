# 020 · Tasks（全部完成，轮 101）

- [x] T-1601 读 144 条候选、抽查前几条 ⇒ 发现明显假匹配
  `→ 验收:` `python tools/triage_union_gaps.py`
- [x] T-1602 定抽样规则（每 6 取 1）并取 24 条
- [x] T-1603 ★ **逐条判** 24 条（真 6 / 部分 2 / 假 16）
  `→ 验收:` `Select-String docs\union-gap-triage-sample.md -Pattern '✅ 真|❌ 假'`
- [x] T-1604 核实 6 条「真」在文件系统确有实现（**全部属实**）
- [x] T-1605 写 `docs/union-gap-triage-sample.md`（可复算的抽样 + 逐条判定）
- [x] T-1606 ★ 在 `union-gap-triage.md` **挂修正提示**
- [x] T-1607 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

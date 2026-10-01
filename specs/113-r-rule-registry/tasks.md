# 113 · Tasks（全部完成，轮 193）

- [x] T-11301 查清 R1–R14 的登记状态（代码仓库 **0 处** R1–R11）
  `→ 验收:` `python -c "import re,sys;from pathlib import Path;t=Path('docs/union-conventions.md').read_text(encoding='utf-8');print(sorted({int(m.group(1)) for m in re.finditer(r'\\bR(\\d{1,2})\\b',t)}))"`
- [x] T-11302 ★★★ 补「R 编号登记表」（R1–R14 逐条 + 守它的段 + 权威出处）
- [x] T-11303 ★★★ 门禁 `check_rule_registry`
  `→ 验收:` `python scripts/check_union_conventions.py`（**8 段全过 · exit 0**）
- [x] T-11304 ★★ **负例**：删掉 `R7` 行 ⇒ **exit 1** 且两条都报 ⇒ 自备份还原 ⇒ exit 0
- [x] T-11305 ★ 3 条永久测试
  `→ 验收:` `python -m pytest tests/test_gate_negative_cases.py -q`（**47 passed**）
- [x] T-11306 事实 133（含我两次"观测不够宽"与一次**破坏性 `git checkout --`** 的如实记录）
- [x] T-11307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1253 passed**

# 120 · Tasks（全部完成，轮 200）

- [x] T-12001 ★★★ 量三处数字（triage 手写 / 生成物重跑）
  `→ 验收:` `python tools/build_union_map.py`（**并集 424 / 缺 338 / 独家 75**，而 triage 写 349/339）
- [x] T-12002 ★★★ 查出 `check_map_fresh()` **已在** ⇒ 不重造
  `→ 验收:` `python scripts/check_union_conventions.py`（**8 段全过 · exit 0**）
- [x] T-12003 ★★ 让「算于」块**指向生成物 + 明说历史值**
- [x] T-12004 ★★ 结构性判据 + **负例两次**（第一次暴露判据太弱 ⇒ 范围限定后报红）
  `→ 验收:` `python -m pytest tests/test_report_freshness_gate.py -q`（**9 passed**）
- [x] T-12005 事实 140
- [x] T-12006 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1262 passed**

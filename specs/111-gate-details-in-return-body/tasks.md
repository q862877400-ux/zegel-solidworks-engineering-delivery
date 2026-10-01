# 111 · Tasks（全部完成，轮 191）

- [x] T-11101 测量：读 `release_check` 的**实际输出**，看哪些门禁没有明细
  `→ 验收:` `python scripts/release_check.py`（**4 道有 / 11 道只有 status**）
- [x] T-11102 ★★★ 修在一处：`gates`/`gate_details` 同循环 + `_gate_detail()`
- [x] T-11103 ★★ 实测 **16 = 16 · 空明细 0**
  `→ 验收:` `python -c "import json,subprocess,sys;d=json.loads(subprocess.run([sys.executable,'scripts/release_check.py'],capture_output=True,text=True,encoding='utf-8').stdout);print(len(d['gates']),len(d['gate_details']),set(d['gates'])==set(d['gate_details']))"`
- [x] T-11104 ★★★ 带负例的测试（四种输入）
  `→ 验收:` `python -m pytest tests/test_gate_negative_cases.py -q`（**44 passed**）
- [x] T-11105 事实 131
- [x] T-11106 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1250 passed**

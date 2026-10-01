# 112 · Tasks（全部完成，轮 192）

- [x] T-11201 度量：按**全文**重量（发现"5 道薄"是首行判据的假阳性）
  `→ 验收:` `python -c "import json,subprocess,sys;d=json.loads(subprocess.run([sys.executable,'scripts/release_check.py'],capture_output=True,text=True,encoding='utf-8').stdout);print([k for k,v in d['gate_details'].items() if not __import__('re').search(r'\d',str(v))])"`（**空**）
- [x] T-11202 ★ 6 处首行补分母（5 门禁 + `union_conventions` 段数汇总）
- [x] T-11203 ★★ 实测 **16 道首行全部带分母**
- [x] T-11204 ★★★ 如实记判据极限（`\d` 分不出分母与编号）
- [x] T-11205 事实 132
- [x] T-11206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1250 passed**

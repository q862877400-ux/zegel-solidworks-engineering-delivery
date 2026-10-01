# 115 · Tasks（全部完成，轮 195）

- [x] T-11501 ★★ 实测 NOTICE 两处可疑点
  `→ 验收:` `python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));print([c['id'] for c in d['capabilities'] if c.get('provenance')])"`（**`['mold_tools']`**，而注释写 `[]`）
  `→ 验收:` `git diff origin/main --shortstat`（**343 / +155,707**，而正文写 179 / +126,7xx）
- [x] T-11502 ★★★ 修 L35（删数字 + 指向 harvest-report）与 L107（改成真实输出 + 更正块）
- [x] T-11503 ★★★ 补两条机器检查
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py -q`（**7 passed**）
- [x] T-11504 ★★ 两条负例都证明有牙（改回 `[]` ⇒ failed；插入精确数字 ⇒ failed）
- [x] T-11505 事实 135（含**我自己两处错**的如实记录）
- [x] T-11506 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1257 passed**

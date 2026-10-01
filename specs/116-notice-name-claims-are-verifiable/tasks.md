# 116 · Tasks（全部完成，轮 196）

- [x] T-11601 ★★★ 实测 NOTICE §一.3 的 4 条名字论断
  `→ 验收:` `python -c "import re,sys;from pathlib import Path;t=Path(r'D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt').read_text(encoding='utf-8',errors='replace');[print(n, bool(re.search(r'\b'+n+r'\b', t))) for n in ('InsertPartingLines','InsertShutOffSurfaces','InsertMoldPartingLine','InsertMoldShutOffSurface')]"`
  （**False / False / True / True** ⇒ 与 NOTICE 的论断一致）
- [x] T-11602 ★★★ 加判据（**从 NOTICE 解析** + 锚在句子形态上）
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py -q`（**9 passed**）
- [x] T-11603 ★★ 负例（临时文档）
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py::test_notice_name_claim_criterion_has_teeth -q`（**passed**）
- [x] T-11604 事实 136（含**我两次判据失准**的如实记录）
- [x] T-11605 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1259 passed**

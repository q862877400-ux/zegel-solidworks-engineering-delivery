# 052 · Tasks（全部完成，轮 133）

- [x] T-4801 写 `tools/probe_unit_declarations.py`（显式词表）
  `→ 验收:` `python tools/probe_unit_declarations.py`
- [x] T-4802 ★★ 逐条人工判 4 个候选 ⇒ **4/4 假阳性**
  `→ 验收:` `Select-String docs\script-layer-units.md -Pattern '4/4'`（逐条真相在那份文档里）
- [x] T-4803 ★ 定位根因：**词形判不了语义** ⇒ 原理不成立
- [x] T-4804 写 `docs/script-layer-units.md` + 探针源码写明结论
- [x] T-4805 已知事实 74 入库
- [x] T-4806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

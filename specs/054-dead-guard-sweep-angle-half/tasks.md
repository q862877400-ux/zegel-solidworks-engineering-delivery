# 054 · Tasks（全部完成，轮 135）

- [x] T-5001 写 `tools/probe_dead_guards.py`
  `→ 验收:` `python tools/probe_dead_guards.py`（21 扫过 / **2 可疑**）
- [x] T-5002 ★★ 逐条人工判 ⇒ **1 真（`_ANGLE_SUFFIX`）· 1 假（`SKETCH_MIRROR_MARK`）**
- [x] T-5003 ⚠ 发现并修我自己的**子串 bug**（`rad` 命中 `radius`，7 处假阳性）
- [x] T-5004 接上角度那一半 + 显式豁免（`solidworks_mold_parting_surface.angle`）
- [x] T-5005 测试扩到 **10 条**（含角度负例、`rad` 禁令、对照）
  `→ 验收:` `python -m pytest tests/test_rule2_length_suffix_is_enforced.py -q`（**10 passed**）
- [x] T-5006 文档 §七 + 已知事实 76
- [x] T-5007 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

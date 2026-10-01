# 040 · Tasks（全部完成，轮 121）

- [x] T-3601 写 `tools/verify_helix_smoke.py`
- [x] T-3602 ★ 冒烟 **9/10** ⇒ 抓到 `FirstFeature` 那处缺陷
  `→ 验收:` `python tools/verify_helix_smoke.py`
- [x] T-3603 ★ 查官方接口 ⇒ `IModelDocExtension.GetLastFeatureAdded()`
- [x] T-3604 修 `_newest_feature_name` 并复跑
- [x] T-3605 ★★ 加**读回定义**的硬验证（核 `Height`/`Pitch`/`Revolution`）
- [x] T-3606 ⇒ **13/13** ⇒ 升 `verified`（能力 + 源码来源块 + 测试）
  `→ 验收:` `python -m pytest tests/test_sw_helix_contract.py -q`（9 passed）
- [x] T-3607 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

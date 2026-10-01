# 015 · Tasks（全部完成，轮 95）

- [x] T-1101 查权威类型库确认两个成员**存在**
  `→ 验收:` `Select-String scripts\sw_api_sldworks.py -Pattern 'InsertWeldmentCutList'`
- [x] T-1102 真机探测 `GetMassProperties` 三种参数数 + `GetMassProperties2`
- [x] T-1103 定性：**后端能力问题**，非参数问题
- [x] T-1104 修 `sw_weldment.create_cut_list`（判空 + 可诊断消息）
  `→ 验收:` `python -m pytest tests/test_dead_capability_diagnostics.py -q`
- [x] T-1105 修 `sw_export.get_mass_property_override_options`（包 COM 失败）
- [x] T-1106 桩测 `tests/test_dead_capability_diagnostics.py`（**3 passed**）
- [x] T-1107 同步签名审计表（`sw_weldment.py` 71→72）与报告数字
- [x] T-1108 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

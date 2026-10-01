# 026 · Tasks（全部完成，轮 107）

- [x] T-2201 搜遍 `api\redist` 下所有 DLL ⇒ 定位 `sws*` 在 **cosworks.dll**
- [x] T-2202 确认 `_raw/reflect/enum_cosworks.txt` 已含该程序集（363 个枚举节）
- [x] T-2203 门禁改成读**多份**转储并合并（`DUMPS` + `parse_dumps`）
  `→ 验收:` `python scripts/check_enum_values_vs_reflection.py`（**0 条查不到**）
- [x] T-2204 加测试：`sws*` 可查 + 合并优先级（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_enum_values_gate.py -q`
- [x] T-2205 更新 `docs/gate-classification.json`（并修正 JSON 转义）
  `→ 验收:` `python scripts/check_gate_wiring.py`（16 道全部接线）
- [x] T-2206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

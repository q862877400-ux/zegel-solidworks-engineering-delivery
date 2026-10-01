# 056 · Tasks（全部完成，轮 137）

- [x] T-5201 写 `tools/probe_registry_wiring.py`
  `→ 验收:` `python tools/probe_registry_wiring.py`（双向都 0）
- [x] T-5202 ★ 量「注入」那一半（`inject` ↔ `RESOLVERS`，两个方向）
- [x] T-5203 ★★ 5 条结构判据做成回归 `tests/test_registry_wiring.py`
  `→ 验收:` `python -m pytest tests/test_registry_wiring.py -q`（**5 passed**）
- [x] T-5204 ★★ **故障注入**：放假批次 ⇒ **1 failed** ⇒ 删掉 ⇒ 5 passed
- [x] T-5205 文档（并入 `docs/dead-guards.md`）+ 已知事实 78
- [x] T-5206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

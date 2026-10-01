# 087 · Tasks（全部完成，轮 167）

- [x] T-8701 读官方 md 查根因（`BCoordInput` 参数名与语义）
- [x] T-8702 ★★★ 根因解决：默认坐标输入 + 非零方向 `→ 验收:` `python tools/verify_batch9_smoke.py`（**不再弹框**）
- [x] T-8703 ★★ 零硬编码机制 `→ 验收:` `python -c "import sw_connect; print(sw_connect._resolve_pid(None))"`
- [x] T-8704 ★★★ 端到端复现 `→ 验收:` `python tools/verify_modal_dialog_lifecycle.py`（**发现 1 / 点掉 1 / 解卡**）
- [x] T-8705 迁移 36 处硬编码（常量删 36/36 · 调用改 34/34 · 0 语法坏）
- [x] T-8706 契约测试 + MCP spec 改名 `→ 验收:` `python -m pytest tests/test_sw_mold_contract.py -q`（**10 passed**）
- [x] T-8707 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· **1247 passed**

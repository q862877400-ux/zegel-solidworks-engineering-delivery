# 069 · Tasks（全部完成，轮 150）

- [x] T-6501 造靶子 `tools/fake_modal_dialog.py`（真 `#32770`、故意不可见、自报 PID）
- [x] T-6502 ★★★ 测试证明**新口径抓得到**、**旧口径漏掉**
  `→ 验收:` `python -m pytest tests/test_modal_dialogs_can_fire.py -q`（**2 passed**）
- [x] T-6503 ⚠ 修 `WS_VISIBLE` 常量写错（并核对 `visible=?` 才发现）
- [x] T-6504 ⚠ 记下 `Stop-Process -Name python` 的风险 + 环境自检
- [x] T-6505 能力证据 + 已知事实 90
- [x] T-6506 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

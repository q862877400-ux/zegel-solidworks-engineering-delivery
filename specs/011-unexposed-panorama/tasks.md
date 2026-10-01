# 011 · Tasks（全部完成，轮 87）

- [x] T-701 量公开函数 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-702 补 `server.py` 的 `import` 来源（第一版只有 `function=`）
  → `→ 验收:` 同上（② 段应打印两行来源）
- [x] T-703 ★ 加「跨文件调用」这一刀 → `→ 验收:` 同上（④ 段）
- [x] T-704 ★ **抽验**：6 个"孤立"里 1 个有调用者（`add_component`）
  ⇒ 发现调用者扫描**只扫了 `scripts/`** → 扩到 5 个目录
- [x] T-705 ★ **抽验**：`tests_only` 定义错（"出现在测试里"≠"只出现在测试里"）→ 改成分别追踪两来源
- [x] T-706 加判据边界声明 → `→ 验收:` 同上（末段）
- [x] T-707 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）

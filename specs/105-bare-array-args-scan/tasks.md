# 105 · Tasks（全部完成，轮 185）

- [x] T-10501 写扫描器（纯静态）
- [x] T-10502 ★★★ 判据三次修正 `→ 验收:` `python tools/scan_bare_array_args.py`（**0 → 30 → 0**）
- [x] T-10503 ★★★ 负例验证 `→ 验收:` `python tools/recheck_bare_array_negative.py`（**命中 2 处**）
  ⚠ **轮 185 踩过**：这条原本写的是 `D:/AI/SW/_validate_scan_negative.py`（**仓库外**）
  ⇒ 被 `check_spec_acceptance_paths.py` 拦下（★ 与轮 175 同一个坑）⇒ 已搬进 `tools/`。
- [x] T-10504 事实 125
- [x] T-10505 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）

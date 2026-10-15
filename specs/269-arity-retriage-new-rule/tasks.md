# Tasks — 重量分桶

**Feature**: `specs/269-arity-retriage-new-rule/`
**日期**: 2026-10-10

## T-001 重跑 253 探针（★ 自动反映新口径）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B output/_probe253_arity_sites.py 2>&1 | head -3
  ```
- **期望**：`=== arity 不符站点：11 条 ===`。
- **状态**：☑ 完成。

## T-002 ★★ 与 253 的原桶对照
- **状态**：☑ 完成（★ 发现 **多移了 2 条 `real-gap`**）。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_arity_retriage_new_rule.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

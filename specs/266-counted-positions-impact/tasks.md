# Tasks — 先量 counted_positions 口径缺陷的影响面

**Feature**: `specs/266-counted-positions-impact/`
**日期**: 2026-10-10

## T-001 读 `counted_positions` 源码
- **状态**：☑ 完成（★ 确认跳过 `PURE_OUT` = `Object&`）。

## T-002 量两个口径的差异
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B output/_probe266_impact.py
  ```
- **期望**：`现行 16` · `实验 15` · ★ `移出 1`。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_counted_positions_impact.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

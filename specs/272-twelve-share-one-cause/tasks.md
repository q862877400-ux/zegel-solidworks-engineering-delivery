# Tasks — 12 条同一病因

**Feature**: `specs/272-twelve-share-one-cause/`
**日期**: 2026-10-10

## T-001 ★★ 先量：读 2 条的表侧值
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n '"GetNodeLocation"\|"GetElementLocation"' scripts/sw_simulation_results.py | head -4
  ```
- **期望**：两条都是 **1**（★ 而官方是 **4**）。
- **状态**：☑ 完成。

## T-002 验证「表侧不含出参」的公式
- **状态**：☑ 完成（★ 4 条样本全自洽）。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_twelve_share_one_cause.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

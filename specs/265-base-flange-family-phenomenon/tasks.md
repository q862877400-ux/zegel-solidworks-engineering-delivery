# Tasks — 族现象合并

**Feature**: `specs/265-base-flange-family-phenomenon/`
**日期**: 2026-10-10

## T-001 读事实 34/43（★ 找族现象）
- **状态**：☑ 完成（★ 事实 34 早记「4 个卡在同一层」）。

## T-002 真机查环境（★ 走护栏）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe265_env.py
  ```
- **期望**：`Front Plane ⇒ None` · `Top ⇒ 选不上` · 模板数 1。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_base_flange_family_phenomenon.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

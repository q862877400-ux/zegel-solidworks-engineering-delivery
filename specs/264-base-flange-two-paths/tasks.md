# Tasks — 两条独立的路都建不出基体法兰

**Feature**: `specs/264-base-flange-two-paths/`
**日期**: 2026-10-10

## T-001 找老入口并读签名
- **状态**：☑ 完成（★ 19 参；★ 且**它本身也废弃**）。

## T-002 真机调老路（★ 走护栏）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe264_legacy.py
  ```
- **期望**：`⇒ None` · ★ `**老入口也回 None** ⇒ ★ 失败在**环境/前置**`。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_base_flange_two_paths.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

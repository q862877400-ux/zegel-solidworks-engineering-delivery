# Tasks — ② 段 6 条待办的逐条前提核对

**Feature**: `specs/259-todo-premise-audit-full/`
**日期**: 2026-10-10

## T-001 读 ② 段 6 条原文
- **状态**：☑ 完成。

## T-002 逐条找依据
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "五种形态全部回" scripts/sw_sheet_metal.py
  ```
- **期望**：≥1（★ `create_hem` 的真机实录在）。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_handoff_todo_premises_full.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 ★★ ② 段计数不变（★ 本轮**不删**任何一条）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "
  import sys; sys.path.insert(0,'D:/AI/SW/tools'); import goal_gate as g
  print(g.count_todos(open('D:/AI/SW/output/AUTO_HANDOFF.md',encoding='utf-8').read()))
  "
  ```
- **期望**：**6**（★ 与 258 之后一致）。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

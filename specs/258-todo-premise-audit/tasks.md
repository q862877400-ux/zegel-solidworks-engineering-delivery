# Tasks — ② 段待办的前提核对

**Feature**: `specs/258-todo-premise-audit/`
**日期**: 2026-10-10

## T-001 先量：`SketchTrim` 的实际写法
- **验收**：
  ```bash
  cd "D:/AI/SW" && sed -n '148,149p' scripts/sw_sketch_edit_ops.py
  ```
- **期望**：宿主是 `get_com_member(model, "SketchManager")` ⇒ **ISketchManager**。
- **状态**：☑ 完成。

## T-002 核 250 的表
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_handoff_todo_premises.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  print('SketchTrim:', m._sketchtrim_failures(m._HOST_EXPR_REVIEW))
  print('真命中:', m._real_hit_failures(m._HOST_EXPR_REVIEW))
  "
  ```
- **期望**：两行都是 `[]`。
- **状态**：☑ 完成。

## T-003 判据转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_handoff_todo_premises.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 ★★ 核销后复读 ② 段计数
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "
  import sys; sys.path.insert(0,'D:/AI/SW/tools')
  import goal_gate as g
  print(g.count_todos(open('D:/AI/SW/output/AUTO_HANDOFF.md',encoding='utf-8').read()))
  "
  ```
- **期望**：**6**（★ 原 8）。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

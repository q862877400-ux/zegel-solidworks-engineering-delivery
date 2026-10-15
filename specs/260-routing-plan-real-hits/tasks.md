# Tasks — 250 的 6 名 7 处真命中的换路由先量

**Feature**: `specs/260-routing-plan-real-hits/`
**日期**: 2026-10-10

## T-001 先量：列 6 名 7 处
- **状态**：☑ 完成（★ 6 名 · 7 处）。

## T-002 查官方后继（★ 用**源接口**）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_routing_plan_real_hits.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  print(m._plan_failures(m._PLAN))
  "
  ```
- **期望**：`[]`。 **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_routing_plan_real_hits.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-004 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

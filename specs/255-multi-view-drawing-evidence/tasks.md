# Tasks — 造出多视图工程图并量 `IView::Name` == `GetName2`

**Feature**: `specs/255-multi-view-drawing-evidence/`
**日期**: 2026-10-10

---

## T-001 造图并量（★ 走护栏）

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe255_make_drawing.py
  ```
- **期望**：`汇总：同 4 · 异 0 · 有名字的视图 4`。
- **状态**：☑ 完成（★ SW rev 34.4.1）。

## T-002 判据能红

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_multi_view_drawing_evidence.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  print('正常:', len(m._reading_failures(m.MACHINE)))
  print('不等价:', m._reading_failures(dict(m.MACHINE, diff=1)))
  print('真实视图0:', m._reading_failures(dict(m.MACHINE, real_model_views=0))[:1])
  "
  ```
- **期望**：`正常: 0` · `不等价: ['有 1 处 … ⇒ **不能换路由**']` · `真实视图0: ['**真实模型视图** 0 < 下界 3 ⇒ 证据仍弱']`。
- **状态**：☑ 完成。

## T-003 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_multi_view_drawing_evidence.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。
- **状态**：☑ 完成。

## T-004 真机后确认环境干净

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --scan
  ```
- **期望**：`弹窗 0 个`；★ 预检显示 **0 个文档**。
- **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）

- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态

- **状态**：☐

## T-007 未改 `scripts/` 的证明

- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" scripts/sw_drawing_query.py scripts/sw_drawing_view.py scripts/sw_review.py
  ```
- **期望**：mtime 全部**早于** `00:20`。
- **状态**：☑ 完成。

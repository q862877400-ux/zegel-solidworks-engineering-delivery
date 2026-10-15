# Tasks — `IView::Name` 换路由的真机等价性先量

**Feature**: `specs/254-iview-name-routing/`
**日期**: 2026-10-10

---

## T-001 先量：真机比对 `Name` 与 `GetName2`

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe254_viewname.py
  ```
- **期望**：`汇总：同 1 · 异 0 · 失败 0`。
- **状态**：☑ 完成（★ SW rev 34.4.1）。

## T-002 判据能红

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_iview_name_successor_machine.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  print('正常:', len(m._equiv_failures(m.MACHINE)))
  print('样本0:', m._equiv_failures(dict(m.MACHINE, views=0)))
  print('不等价:', m._equiv_failures(dict(m.MACHINE, diff=1)))
  "
  ```
- **期望**：`正常: 0` · `样本0: ['真机视图数 0 < 下界 1 ⇒ 证据不足']` · `不等价: ['真机上 Name 与 GetName2 **不等价** 1 处 ⇒ **不能换路由**']`。
- **状态**：☑ 完成。

## T-003 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_iview_name_successor_machine.py -q 2>&1 | tail -2
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
- **期望**：mtime 全部**早于** `00:10`。
- **状态**：☑ 完成。

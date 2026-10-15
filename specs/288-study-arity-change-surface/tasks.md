# Tasks — 先量：`STUDY_MANAGER_ARITY` 的改动面

**Feature**: `specs/288-study-arity-change-surface/`
**日期**: 2026-10-10

## T-001 ★ 现场解析 15 条表值 + 15 条官方真值
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "import sys; sys.path.insert(0,'tests'); import test_study_arity_change_surface as T; t,o=T._table(),T._official(); print('差 1 处数 =', sum(1 for k,v in t.items() if o[k][0]==v+1))"
  ```
- **期望**：★ **9**。 **状态**：☑ 完成。

## T-002 ★ 核「差 1」的末位
- **期望**：★ **全是 `Int32&`**。 **状态**：☑ 完成（★ **完全自洽**）。

## T-003 ★ 读门禁的标注正则
- **验收**：
  ```bash
  cd "D:/AI/SW" && sed -n '54p' scripts/check_arity_tables_vs_reflection.py
  ```
- **期望**：★ `^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$` ⇒ ★ **per-table**。
- **状态**：☑ 完成。

## T-004 ★ 找 4 类同步点
- **期望**：★ 表值（9 处）· ★ 调用点（传 `out_i4()`）· ★ 标注 · ★ 测试对照表。
- **状态**：☑ 完成。

## T-005 判据（★ **invariant-based** · ★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_study_arity_change_surface.py 2>&1 | tail -2
  ```
- **期望**：`6 passed`。 **状态**：☑ 完成。

## T-006 门禁全套（★ **不跑生成器链** —— 没改 `scripts/`）
- **验收**：`output/_gate288.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☑ 完成。

## T-007 回写四处状态
- **状态**：☐

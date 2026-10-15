# Tasks — starargs 修复尝试被棘轮打回

**Feature**: `specs/267-starargs-fix-rollback/`
**日期**: 2026-10-10

## T-001 读 `com_args` 的 `*args` 槽处理
- **状态**：☑ 完成。

## T-002 加早返回并跑门禁
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -3
  ```
- **期望**（★ 改后）：`arity 不符 14` · `可核分发口 20` · `已核调用点 124` · ★ **`[FAIL] · exit 1`**。
- **状态**：☑ 完成（★ **被打回**）。

## T-003 ★★ 回滚 + 留注释
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -2
  ```
- **期望**：`arity 不符 16` · `可核分发口 21` · `已核调用点 313` · ★ **`[PASS] · exit 0`**。
- **状态**：☑ 完成。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_starargs_fix_rollback.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

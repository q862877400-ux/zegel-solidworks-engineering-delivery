# Tasks — 试 269 提的修法

**Feature**: `specs/270-starargs-move-back-noop/`
**日期**: 2026-10-10

## T-001 按 269 的方向改（`com_args` 双条件）
- **状态**：☑ 完成。

## T-002 跑门禁（★ 核是否空改动）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -2
  ```
- **期望**：★ `arity 不符 11` · ★ `*args 不可判 0` ⇒ ★ **空改动**。
- **状态**：☑ 完成（★ **空改动**）。

## T-003 ★★ 回滚 + 恢复 268 的窄规则
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -2
  ```
- **期望**：`arity 不符 11` · `可核 21` · `已核 318` · ★ **`[PASS] · exit 0`**。
- **状态**：☑ 完成（★ 回滚时一度撤多了，★ 已修回）。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_starargs_move_back_noop.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

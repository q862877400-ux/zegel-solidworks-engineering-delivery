# Tasks — starargs 窄规则

**Feature**: `specs/268-starargs-narrow-rule/`
**日期**: 2026-10-10

## T-001 读 267 的负结论并定窄规则
- **状态**：☑ 完成。

## T-002 改 `judge` + `main`
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/check_dispatch_byref_guard.py 2>&1 | tail -3
  ```
- **期望**：`arity 不符 11` · ★ `*args 不可判 5` · `可核 21` · `已核 318` · ★ **`[PASS] · exit 0`**。
- **状态**：☑ 完成。

## T-003 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_starargs_narrow_rule.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-004 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-005 回写四处状态
- **状态**：☐

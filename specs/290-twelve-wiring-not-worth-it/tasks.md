# Tasks — 核销「12 条接线」

**Feature**: `specs/290-twelve-wiring-not-worth-it/`
**日期**: 2026-10-10

## T-001 ★ 扫 3 个目录数 12 个封装的生产调用点
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "import sys; sys.path.insert(0,'tests'); import test_twelve_wiring_is_not_worth_it as T; print({k:v for k,v in T._production_calls().items() if v} or '全 0')"
  ```
- **期望**：★ **全 0**。 **状态**：☑ 完成。

## T-002 ★ 核生产路径
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "CreateNewStudy3\", str(name)" scripts/sw_simulation.py
  ```
- **期望**：★ 该行**带 `out_i4()`**。 **状态**：☑ 完成（★ 生产路径**已对**）。

## T-003 ★ 找乙方案的先例
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "统一补 \`out_i4()\`" scripts/sw_simulation_loads.py
  ```
- **期望**：★ 找到（★ 一句修改全受益）。 **状态**：☑ 完成。

## T-004 ★★★ **核销**
- **期望**：★ 与 **266** 同一判断 ⇒ ★ **不值** ⇒ ★ 删号。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_twelve_wiring_is_not_worth_it.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-006 门禁全套（★ **不跑生成器链** —— 没改 `scripts/`）
- **验收**：`output/_gate290.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-007 回写四处状态（★ **删号**：② 段第 1 条的**衍生待办**）
- **状态**：☐

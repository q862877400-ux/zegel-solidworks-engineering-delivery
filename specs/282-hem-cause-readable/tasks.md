# Tasks — `create_hem` 的真因读出来了

**Feature**: `specs/282-hem-cause-readable/`
**日期**: 2026-10-10

## T-001 造带折弯的件 + 四形态 + **读栈**
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe282_hem.py
  ```
- **期望**：★ 四形态**全回 `None`** · ★ 报文恒定：★「**褶边N: 您必须选择一边线。**」。
- **状态**：☑ 完成。

## T-002 ★ 再量一层：`GetSelectedObjectType3`
- **验收**：`output/_probe282_seltype.py`（★ 走护栏）。
- **期望**：★ 边 ⇒ **`swSelEDGES`(1)** · ★ 面 ⇒ **`swSelFACES`(2)**。
- **状态**：☑ 完成（★ **选择登记没问题**）。

## T-003 ★ 与 `create_edge_flange` 对比
- **期望**：★ **同形但不同因**（★ hem 走 `Insert*` · ★ edge_flange 卡在 `AccessSelections`）。
- **状态**：☑ 完成。

## T-004 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_hem_cause_readable.py 2>&1 | tail -2
  ```
- **期望**：`6 passed`。 **状态**：☑ 完成。

## T-005 订正状态表（★ 撤掉「尚未查明」）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "您必须选择一边线" scripts/sw_sheet_metal.py
  ```
- **期望**：★ ≥1（★ 订正里写明**真报文**）。
- **状态**：☑ 完成。

## T-006 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-007 门禁全套（★ 后台跑）
- **验收**：`output/_gate282.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态
- **状态**：☐

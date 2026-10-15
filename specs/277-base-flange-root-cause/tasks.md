# Tasks — 族现象的真因：草图几何被 `mm()` 缩了 1000 倍

**Feature**: `specs/277-base-flange-root-cause/`
**日期**: 2026-10-10

## T-001 臂 1：本仓序列（仪表化）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe277_instrumented.py
  ```
- **期望**：★ `ActiveSketch` 关后 ⇒ `None` · 重选后选中 **1** 个 `'草图1'` · `CreateFeature` ⇒ **None**。
- **状态**：☑ 完成。

## T-002 ★★★ 臂 2：官方「关草图前先清选择」（★ 验 276 的假设）
- **期望**：★ 关草图后选中 **0** 个（`GetSelectedObject6(1,-1)` ⇒ **None**）· 仍 None ⇒ ★ **两臂一致 ⇒ 假设证伪**。
- **状态**：☑ 完成。

## T-003 单变量：厚度/深度**单位**
- **期望**：★ 米与文档单位**都失败**（★ 只是错误信息不同）⇒ 排除。
- **状态**：☑ 完成。

## T-004 单变量：**平面**（Front / Top）
- **期望**：★ 都失败 ⇒ 排除。 **状态**：☑ 完成。

## T-005 ★★★ 单变量：**几何尺寸**（30 mm ↔ 0.03 mm）
- **验收**：同上探针（`output/_probe277_mm_geometry.py`）。
- **期望**：★ **几何 30 mm ⇒ 成功（`'基体-法兰1'`）**；★ 几何 0.03 mm ⇒ 「所选的草图对此操作无效」。
- **状态**：☑ 完成（★ **决定性**）。

## T-006 ★ 回源码核 `sketch_line` 的单位
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "_MM_TO_M" scripts/sw_part.py | head -3
  ```
- **期望**：★ `sketch_line` 的体里**逐字** `x1 * _MM_TO_M` ⇒ ★ 单位是**毫米**。
- **状态**：☑ 完成。

## T-007 ★★ 查夹具来历
- **验收**：
  ```bash
  cd "D:/AI/SW" && git log -1 --format="%h %ad %s" --date=short -- tests/solidworks_sheet_metal_regression.py
  ```
- **期望**：★ **`914bf5e1` · 2026-10-03 · merge**（★ 而事实 34 的成功是 **2026-10-01**）。
- **状态**：☑ 完成。

## T-008 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_base_flange_root_cause.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-009 门禁全套（★ 后台跑）
- **验收**：`output/_gate277.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-010 回写四处状态
- **状态**：☐

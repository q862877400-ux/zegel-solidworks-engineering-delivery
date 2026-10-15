# Tasks — 修回归夹具的草图几何单位

**Feature**: `specs/278-base-flange-regression-units/`
**日期**: 2026-10-10

## T-001 改夹具的草图几何（★ 裸毫米）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "sketch_line(model" tests/solidworks_sheet_metal_regression.py
  ```
- **期望**：★ `sketch_line(model, -30, 25, -30, 0.0)` 等 —— ★ **不带 `mm(`**。
- **状态**：☑ 完成。

## T-002 ★★ 第一次「连 spec 一起改」⇒ 跑回归
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tests/solidworks_sheet_metal_regression.py --output-dir "C:/Users/Zegel/AppData/Local/Temp/sw_sm_reg278"
  ```
- **期望**：★ **失败**（★ 证明**不能**一次改两处）。
- **状态**：☑ 完成（★ 失败 ⇒ 暴露了「厚度」这个独立变量）。

## T-003 ★★★ 逐臂量（★ 厚度 / 半径 / 深度）
- **验收**：`output/_probe278_values.py`（★ 走护栏）。
- **期望**：★ `厚 0.002 · 半径 0.0025 · 深 0.1` ⇒ **建成**；★ `厚 2.0`（半径 0.5 / 1.0）⇒ **全失败**。
- **状态**：☑ 完成（★ 报文：★「无法添加此圆角，因为指定的半径值将会删除其中一个实体」）。

## T-004 ★★★ 推翻误推 ⇒ **只保留几何改动** ⇒ 跑回归
- **验收**：同 T-002（★ 换个输出目录）。
- **期望**：★ **`"status": "pass"`** + `.SLDPRT` 95 871 B + `.dxf` 20 660 B。
- **状态**：☑ 完成（★ **跑绿**）。

## T-005 订正 `BaseFlangeSpec` 的 docstring
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "规格 278" scripts/sw_sheet_metal.py | head -2
  ```
- **期望**：★ 旧结论**留档** + ★ **标明被推翻** + ★ 新证据（逐臂读数）。
- **状态**：☑ 完成。

## T-006 判据（★ 先红后绿 · ★ 4 处回源码核）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_base_flange_regression_units.py 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-007 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate278.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐

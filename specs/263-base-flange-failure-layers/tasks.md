# Tasks — 逐层定位 create_base_flange 的失败点

**Feature**: `specs/263-base-flange-failure-layers/`
**日期**: 2026-10-10

## T-001 逐层探（★ 走护栏）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe263_layers.py
  ```
- **期望**：前层全过 · ★ `CreateFeature(data) ⇒ None`。
- **状态**：☑ 完成。

## T-002 ★★★ 只改顺序做实验（★ 验证假设）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe263_order.py
  ```
- **期望**：`仍 None ⇒ ★ 顺序不是根因`。
- **状态**：☑ 完成（★ **假设证伪**）。

## T-003 核常量
- **状态**：☑ 完成（★ `34` = 官方 `swFmBaseFlange`）。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_base_flange_failure_layers.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

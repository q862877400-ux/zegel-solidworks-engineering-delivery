# Tasks — `SaveAs3` 真机静默失败 ⇒ 不换

**Feature**: `specs/284-saveas3-not-swappable/`
**日期**: 2026-10-10

## T-001 读官方链
- **验收**：
  ```bash
  cd "D:/AI/SW" && for m in SaveAs SaveAs2 SaveAs3; do echo "== $m"; grep -m1 -i "obsolete\|^# " "C:/swapi/types/IModelDocExtension/$m.md"; done
  ```
- **期望**：★ `SaveAs` → `SaveAs2` → ★ **`SaveAs3` 无 Obsolete**（★ 链终点）。
- **状态**：☑ 完成。

## T-002 读 `SaveAs3` 的 Remarks
- **期望**：★ 「call `IModelDocExtension::GetAdvancedSaveAsOptions`」。
- **状态**：☑ 完成。

## T-003 ★ 探针：`SaveAs3` + 对照 `SaveAs`
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe284_saveas3.py
  ```
- **期望**：★ `SaveAs3` ⇒ **True** 但**文件不存在**；★ `SaveAs` ⇒ **文件存在**（≈48 KB）。
- **状态**：☑ 完成。

## T-004 ★ 单变量：四个 `Options`
- **验收**：`output/_probe284_saveas3_opt.py`（★ 走护栏）。
- **期望**：★ **四个都不落盘**。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_saveas3_not_swappable.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-006 登记（★ 注释 + 一行文档串警示）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "规格 284" scripts/sw_connect.py
  ```
- **期望**：★ ≥1。 **状态**：☑ 完成。

## T-007 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate284.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐

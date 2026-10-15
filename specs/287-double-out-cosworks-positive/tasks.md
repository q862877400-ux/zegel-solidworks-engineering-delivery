# Tasks — cosworks 的 `Double&` 正例找到了

**Feature**: `specs/287-double-out-cosworks-positive/`
**日期**: 2026-10-10

## T-001 ★ 在仓里搜 `VT_BYREF | VT_R8`
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -rn "VT_BYREF | pythoncom.VT_R8" scripts/*.py
  ```
- **期望**：★ **3 处**（★ `sw_sensor.py` 的 `out_double` · ★ `sw_simulation.py` 的 744/745）。
- **状态**：☑ 完成。

## T-002 ★ 读 `sw_simulation.py` 的来源块
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "ByRef DElementSize As Double\|真机实测（2026-10-01）" scripts/sw_simulation.py
  ```
- **期望**：★ 官方签名 + ★ **真机实测的两条读数**（4.9339 / 0.0049339）。
- **状态**：☑ 完成（★ **正例成立**）。

## T-003 判据（★ 先红后绿 · ★ 含回源码核）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_double_out_cosworks_positive.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-004 ★★ **同步更新 274 的判据**
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_double_out_param_form.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`（★ `out_double` 改标为**有**真机证据 · ★ 集合改名为**接口相关**）。
- **状态**：☑ 完成。

## T-005 给 274 的 `acceptance.md` 补**订正**
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "规格 287" specs/274-double-out-param-form/acceptance.md
  ```
- **期望**：★ ≥1。 **状态**：☑ 完成。

## T-006 门禁全套（★ 后台跑 · ★ **不跑生成器链** —— 没改 `scripts/`）
- **验收**：`output/_gate287.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-007 回写四处状态
- **状态**：☐

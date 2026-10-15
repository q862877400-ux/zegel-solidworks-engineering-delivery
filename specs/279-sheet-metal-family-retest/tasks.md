# Tasks — 用带折弯的钣金件复测族成员

**Feature**: `specs/279-sheet-metal-family-retest/`
**日期**: 2026-10-10

## T-001 造**带折弯**的 U 型件（★ 开放折线 · 毫米几何）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe279_family.py
  ```
- **期望**：★ `基体法兰 ⇒ '基体-法兰1'` · ★ `has_base_flange=True` · ★ `all_solid_bodies_are_sheet_metal=True`。
- **状态**：☑ 完成（★ **开放折线建成** ⇒ ★ 状态表第 1 条**被证伪**）。

## T-002 取最长边
- **期望**：★ 44 条边 · ★ 最长 **0.1 m**。
- **状态**：☑ 完成。

## T-003 ★★★ 三臂：只改「边的选择标记」
- **期望**：★ 不设 / Mark 1 / Mark 0 ⇒ ★ **全失败** · ★ 报文**一致**。
- **状态**：☑ 完成。

## T-004 ★ 读消息栈
- **期望**：★ **「边线-法兰N: 无法为此特征找到适当的钣金实体」**。
- **状态**：☑ 完成。

## T-005 ★ 订正 `SHEET_METAL_RUNTIME_STATUS` 两条
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "规格 278 + 279\|规格 279 · 真机单变量" scripts/sw_sheet_metal.py
  ```
- **期望**：★ 两条**都有**订正（★ 且**旧结论留档**）。
- **状态**：☑ 完成。

## T-006 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_sheet_metal_family_retest.py 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-007 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate279.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐

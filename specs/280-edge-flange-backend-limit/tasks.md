# Tasks — `create_edge_flange` 定案：阻塞是 `AccessSelections` 族

**Feature**: `specs/280-edge-flange-backend-limit/`
**日期**: 2026-10-10

## T-001 四臂：选择方式 × mark × 边
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe280_edge_select.py
  ```
- **期望**：★ `Select4` / `SelectByID2` × Mark 1 / 不设 × 最长 / 最短直边 ⇒ ★ **全失败 · 报文一致**。
- **状态**：☑ 完成。

## T-002 二臂：轮廓类型（开放折线 ↔ 闭轮廓）
- **验收**：`output/_probe280_closed_profile.py`（★ 走护栏）。
- **期望**：★ 两臂**全失败 · 报文一致**。
- **状态**：☑ 完成。

## T-003 ★★★ 换层次：`AccessSelections` 逐形态
- **验收**：`output/_probe280_access_selections.py`（★ 走护栏）。
- **期望**：★ 空 Dispatch ⇒ **`-2147417851`（`0x80010105`）**；★ `None` / `False` ⇒ `-2147352571`。
- **状态**：☑ 完成（★ **定案**）。

## T-004 读官方页确认方法存在
- **验收**：
  ```bash
  cd "D:/AI/SW" && cat "C:/swapi/types/IEdgeFlangeFeatureData/AccessSelections.md" | head -20
  ```
- **期望**：★ `bool AccessSelections(TopDoc, Component)` —— ★ **方法存在** ⇒ ★ 是**本机**调不动。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_edge_flange_backend_limit.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-006 订正状态表（★ 旧结论留档 + 定案）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "规格 280" scripts/sw_sheet_metal.py | head -2
  ```
- **期望**：★ 订正里写明 `AccessSelections` 与 `0x80010105` · ★ 且 `Mark of 1` **旧结论留档**。
- **状态**：☑ 完成。

## T-007 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate280.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐

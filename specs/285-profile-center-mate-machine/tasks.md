# Tasks — `create_profile_center_mate` 首次真机验证

**Feature**: `specs/285-profile-center-mate-machine/`
**日期**: 2026-10-10

## T-001 读官方三页
- **验收**：
  ```bash
  cd "D:/AI/SW" && for f in IAssemblyDoc/CreateMate IAssemblyDoc/CreateMateData IProfileCenterMateFeatureData/_overview; do echo "== $f"; sed -n '1,3p' "C:/swapi/types/$f.md" >/dev/null; grep -m2 -i "asterisk\|EntitiesToMate\|Mark = 1" "C:/swapi/types/$f.md"; done
  ```
- **期望**：★ `IProfileCenterMateFeatureData` **无星号**（★ 官方说不支持预选）· ★ `_overview` 给**两条路**。
- **状态**：☑ 完成。

## T-002 ★ 逐层探针
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe285_mate.py
  ```
- **期望**：★ `CreateMateData(24)` **回对象** · ★ `CreateMate` **None** · ★ **栈空**。
- **状态**：☑ 完成。

## T-003 ★ 单变量：实体类型
- **验收**：`output/_probe285_mate_cyl.py`（★ 走护栏）。
- **期望**：★ **圆柱面对也 None**。
- **状态**：☑ 完成。

## T-004 ★ 官方第 2 条路：预选 + Mark 1
- **验收**：`output/_probe285_mate_presel.py`（★ 走护栏）。
- **期望**：★ **选中 0 个** ⇒ ★ **该臂不成立**（★ 如实标注）。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_profile_center_mate_machine.py 2>&1 | tail -2
  ```
- **期望**：`7 passed`。 **状态**：☑ 完成。

## T-006 登记（★ 注释 + 一行文档串警示）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "规格 285" scripts/sw_weldment.py
  ```
- **期望**：★ ≥1。 **状态**：☑ 完成。

## T-007 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate285.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐

# Tasks — 同族的 `AccessSelections` 逐个测

**Feature**: `specs/281-sheet-metal-family-backend-limit/`
**日期**: 2026-10-10

## T-001 对照：常量 37（280 已定案）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe281_family_access.py
  ```
- **期望**：★ `-2147417851`。 **状态**：☑ 完成。

## T-002 常量 35 / 118 / 117 逐个测
- **期望**：★ **全部 `-2147417851`** ⇒ ★★ **整族同一个因**。
- **状态**：☑ 完成。

## T-003 记 `hasattr(AccessSelections)`
- **期望**：★ **全 True** ⇒ ★ 方法**在**（★ 不是「没有这个方法」）。
- **状态**：☑ 完成。

## T-004 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_sheet_metal_family_backend_limit.py 2>&1 | tail -2
  ```
- **期望**：`6 passed`。 **状态**：☑ 完成。

## T-005 ★ 订正状态表**三条**
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "规格 281" scripts/sw_sheet_metal.py
  ```
- **期望**：★ **3**（★ `create_one_bend` · `create_gusset` · `create_swept_flange`）。
- **状态**：☑ 完成。

## T-006 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-007 门禁全套（★ 后台跑）
- **验收**：`output/_gate281.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态
- **状态**：☐

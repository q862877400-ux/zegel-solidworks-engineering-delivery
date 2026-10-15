# Tasks — 换路由后的真机复验

**Feature**: `specs/257-iview-name-routing-reverified/`
**日期**: 2026-10-10

## T-001 读改后函数的签名
- **状态**：☑ 完成（`get_view_name(view)` · `list_views(model)` · `list_drawing_views_report(model)`）。

## T-002 ★★ 订正 docstring（★ 发现与代码不符）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "兜底不能删" scripts/sw_drawing_view.py
  ```
- **期望**：★ **恰好 1 处**，且它必须是**订正说明里的引文**（★ 形如 `「**兜底不能删**：…」——`），
  ★★ **不是**原来那句**断言**。
  ★★ **为什么不是「无输出」**：★ 订正时**引用了被推翻的原话** ⇒ ★ 字符串**必然还在** ——
  ★ 判据若写「无输出」就是**错的期望**（★ 本轮先写错、已订正）。
- **状态**：☑ 完成（★ 实测 `:422` 是引文）。
- **状态**：☑ 完成。

## T-003 真机复验（★ 走护栏）
- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe257_reverify.py
  ```
- **期望**：`list_views` 3 个 · `get_view_name` 4 个名字全非空 · `report ok=True`。
- **状态**：☑ 完成（★ SW rev 34.4.1）。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_iview_name_routing_reverified.py -q 2>&1 | tail -2
  ```
- **期望**：`3 passed`。 **状态**：☑ 完成。

## T-005 ★★ 生成器链 + 门禁（★ 改了 `scripts/`）
- **状态**：☑ 生成器链 7 步 OK；☐ 门禁见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐

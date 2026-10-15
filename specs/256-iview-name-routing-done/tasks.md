# Tasks — `IView::Name` 换路由

**Feature**: `specs/256-iview-name-routing-done/`
**日期**: 2026-10-10

## T-001 读 4 处原写法
- **状态**：☑ 完成（3 处兜底 + 1 处直读）。

## T-002 改 `scripts/`
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n 'get_com_member(view, "Name")\|get_com_member(av, "Name")' scripts/sw_drawing_query.py scripts/sw_drawing_view.py scripts/sw_review.py
  ```
- **期望**：**无输出**。
- **状态**：☑ 完成。

## T-003 判据能红
- **状态**：☑ 完成（合成残留 ⇒ 报出；空表 ⇒ 通过）。

## T-004 判据转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_iview_name_routing_done.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 ★★ 生成器链（★ 改了 `scripts/` ⇒ 必跑）
- **验收**：7 步顺序跑，全 OK。
- **状态**：☑ 完成（7/7 OK）。

## T-006 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md` §六。

## T-007 回写四处状态
- **状态**：☐

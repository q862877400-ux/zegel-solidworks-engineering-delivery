# Plan — 换路由后的真机复验

**Feature**: `specs/257-iview-name-routing-reverified/`
**日期**: 2026-10-10

## 一、三源与冲突裁决顺序

| 序 | 源 | 用途 | 权威度 |
|---|---|---|---|
| 1 | ★★ **真机** SW rev 34.4.1（走护栏） | 跑改后的函数 | ★★★ 最高 |
| 2 | **真树源码** `sw_drawing_query` / `sw_drawing_view` | 函数签名与 docstring | ★★ |
| 3 | **256 的改动** | 换了哪 4 处 | ★ |

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 复验入口 | `sw_drawing_query.list_views` · `sw_drawing_view.get_view_name` · `list_drawing_views_report` | ★ **直接 import 真树函数**（★ 不重写） |
| 测试图纸 | `output/_probe255_views.SLDDRW`（★ 255 造的 4 视图图） | ★ 只读打开 |
| 真机纪律 | `output/GOAL.md` §三 | ★ 走 `sw_guard`；★ 只用 3.14.7 |

## 三、实现步骤

1. 读改后函数的签名。
2. ★★ **发现 docstring 与代码不符**（★ 「兜底不能删」）⇒ **先订正 docstring**。
3. 写真机探针 ⇒ 打开 255 的图纸 ⇒ 调三个入口 ⇒ 记录读数。
4. 写判据（★ 含「名字非空」这条直接回答）。
5. ★★ 跑生成器链（★ 改了 `scripts/`）+ 门禁。
6. 回写四处。

## 四、改动面

`scripts/sw_drawing_view.py`（★ **只改 docstring**）· `tests/test_iview_name_routing_reverified.py`（新）·
`output/_probe257_reverify.py` / `.txt`（新）· `specs/257-*/`（新）· 生成器产物 · 四处状态。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 真机打开用户图纸 | ★ **只读**打开 + `QuitDoc` 不保存 + 事后护栏预检 |
| ★ 复验只是「跑通了」不是「对」 | ★ 判据要求**名字非空**（★ 不是只看不抛异常） |
| ★ 忘了跑生成器链 | ★ 已跑 7 步 |

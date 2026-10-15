# Plan — `IView::Name` 换路由

**Feature**: `specs/256-iview-name-routing-done/`
**日期**: 2026-10-10

## 一、三源与冲突裁决顺序

| 序 | 源 | 用途 | 权威度 |
|---|---|---|---|
| 1 | ★★ **真机** `SldWorks.Application` rev 34.4.1 | 等价性 | ★★★ 最高 |
| 2 | **官方页** `C:/swapi/types/IView/Name.md` | 废弃关系 | ★★ |
| 3 | **真树源码** 4 处站点 | 原写法 | ★ |

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 4 处靶子 | `tests/test_obsolete_multi_successor_impact._HOST_REVIEW["Name"]` | ★ 254 已 import |
| 宿主名 | `view` / `av`（★ 248 的宿主表达式原文） | ★ AST 按名字定位 |

## 三、实现步骤

1. 读 4 处原写法 → 定改法（3 处去兜底、1 处换后继）。
2. 改 `scripts/`（★ 用脚本改，★ 防手误）。
3. **grep 复核**「已清干净」。
4. 写判据（★ AST 按名字）→ 证明能红。
5. ★★ **跑生成器链**（★ 改了 `scripts/` ⇒ 必跑，7 步）。
6. 门禁 + 回写四处。

## 四、改动面

`scripts/sw_drawing_query.py` · `sw_drawing_view.py` · `sw_review.py`（★ 各 1~2 处）·
`tests/test_iview_name_routing_done.py`（新）· `specs/256-*/`（新）· 生成器产物（★ 链跑出来的）· 四处状态。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 去掉兜底会丢名字 | ★ 1/2/3 处**本来就先调 `GetName2`** ⇒ 兜底只在**异常路径**；★ 4 处是**换后继**不是删功能 |
| ★ 改错行 | ★ 用脚本按**精确字符串**替换 + grep 复核 |
| ★ 忘了跑生成器链 | ★ 已跑 7 步 |
| `release_check` 约 3 min | ★ 后台跑 + 落盘日志 |

# 073 · 判别实验：**mark 到底落没落** —— 两个候选被分开

**Status**: Implemented（轮 154）· ⚠ **能力仍不升级**（但失败点更清楚了）

## 一、起因：上轮留了**两个候选**没分开
`072`（轮 153）观察到：`SelectByID2("", "EDGE", …)` 返回 `True`，
而 `GetSelectedObjectCount2(1)` = **0**。当时**没法判断**是哪一个：
```
候选① 「mark 没设上」
候选② 「`GetSelectedObjectCount2(mark)` 的读法不对」
```

## 二、★★★ 判别实验（`tools/probe_mark_semantics.py`）
**手法**：把「选棱」换成「**选已知能选中的草图**」，其余调用形态不变。
```
mark=0 ⇒ GetSelectedObjectCount2:  -1:1   0:1   1:0   2:0
mark=1 ⇒ GetSelectedObjectCount2:  -1:1   0:0   1:1   2:0     ★ 精确落在 mark=1
mark=2 ⇒ GetSelectedObjectCount2:  -1:1   0:0   1:0   2:1     ★ 精确落在 mark=2
```
⇒ ★★★ **两个候选都不是原因**：
* **mark 能落上**（`mark=N` ⇒ `(N)` = 1）
* **`GetSelectedObjectCount2(mark)` 的语义符合预期**（`-1` = 全部）

## 三、★★★ 真因：**`SelectByID2` 返回 `True` 却什么都没选中**
```
轮 153 那次：`SelectByID2("", "EDGE", x,y,z, …, mark=1, …)` **返回 True**
            而 `GetSelectedObjectCount2(1)` = **0**
⇒ **`True` 与「选中了」是两件事**
```
★ 与**事实 8**（`AddSelectionListObject` 的 bool 不可信，要回读计数）**同族** ——
而那条此前**只记在 `AddSelectionListObject` 名下**，这次把 **`SelectByID2` 也纳进来**（事实 94）。

## 四、判据
| ID | 判据 |
|---|---|
| SC-6901 | ★★ **判别实验**：换一个已知能选中的对象，把两个候选分开 |
| SC-6902 | ★★★ 证明 **mark 能落上**（`mark=1/2/0` 各精确落位）|
| SC-6903 | ★★★ 证明 **读法对**（`-1` = 全部，`0/1/2` = 各 mark）|
| SC-6904 | ★★★ 查出真因：**`SelectByID2` 的 bool 不可信**（事实 94）|
| SC-6905 | ★ **就地更正事实 93**（那两个候选都不是原因）|
| SC-6906 | ★ 给出**可复用判据**：判「选上没有」一律回读 mark 计数 |
| SC-6907 | 门禁 + 回归不退化（回归 **1232 passed**）|

## 五、★★ 本条与轮 152/153 是同一纪律的**第三次**
```
轮 152：查「我的量法对不对」            （FeatureByPositionReverse 滞后一格）
轮 153：查「我以为前提满足了没有」        （发现 mark 计数 0）
轮 154：★ 查「**我读那个前提的方法对不对**」 ⇒ 判别实验 ⇒ 两者都证明了，真因是**第三个**
⇒ ★★ 三次都在做同一件事：**把"我的观测"本身当成待验对象**。
```

## ⚠ 明确记下的限度
* ⚠ `InsertCompositeCurve` 的**真因仍未查明** —— 但失败点更清楚了：
  **得先「真的」选中 2 条边**（用回读的 mark 计数确认），再试；
* ⚠ 判别实验只在**草图**上做了（`SKETCH` 类型）；**棱（`EDGE`）为什么返回 True 却没选中，未查明**；
* ⚠ `composite_curve` **不升级**（仍未取证）。

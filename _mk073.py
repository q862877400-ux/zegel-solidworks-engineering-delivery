import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\073-does-mark-land")
S.mkdir(parents=True, exist_ok=True)

spec = """# 073 · 判别实验：**mark 到底落没落** —— 两个候选被分开

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
"""

plan = """# 073 · Plan

## 步骤
1. 上轮留了**两个候选**（mark 没设上 / 读法不对）⇒ 本轮专门分开它们
2. ★ 手法：**换一个已知能选中的对象**（草图），其余调用形态不变
3. ⇒ `mark=1` ⇒ `(1)`=1 · `mark=2` ⇒ `(2)`=1 · `mark=0` ⇒ `(0)`=1
4. ⇒ ★★★ **两个候选都不是原因**：mark 能落上、读法也对
5. ⇒ 真因是第三个：**`SelectByID2` 返回 `True` 却什么都没选中**
6. ★ 就地更正事实 93 + 新事实 94 + 能力条目 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 两个候选不分开就继续试功能 | ★ **判别实验**：换一个已知能成立的输入 |
| 把 `SelectByID2` 的 `True` 当"选中了" | ★ **回读 mark 计数**（事实 94）|
| 新发现不写进事实表 | ★ 事实 94 并**指明它与事实 8 同族** |
| 顺手升级能力 | ★ **不升级**（仍真因未明）|
"""

tasks = """# 073 · Tasks（全部完成，轮 154）

- [x] T-6901 ★★ 判别实验 `→ 验收:` `python tools/probe_mark_semantics.py`（末行打印"扫了 N 个窗口 · 无模态框"）
- [x] T-6902 ★★★ 证明 mark 能落上 + 读法对 ⇒ **两个候选都不成立**
- [x] T-6903 ★★★ 真因：`SelectByID2` 的 bool 不可信 ⇒ **事实 94**
- [x] T-6904 ★ 就地更正事实 93 + 能力条目
- [x] T-6905 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 073 · Converge

**Converged**: 2026-10-01（轮 154）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-6901 判别实验 | ✅ |
| SC-6902 mark 能落上 | ✅ |
| SC-6903 读法对 | ✅ |
| SC-6904 真因 = bool 不可信 | ✅ 事实 94 |
| SC-6905 更正事实 93 | ✅ |
| SC-6906 可复用判据 | ✅ |
| SC-6907 门禁 + 回归 | ✅ `release_check` exit 0 · **1232 passed** |

## 二、★★★ 本轮的形状：**判别实验**
```
问题：观测到 `True` 与 `计数 0` 并存 ⇒ 两个候选（mark 没设上 / 读法不对）
⇒ ★ 手法：**把"被测对象"换成一个已知能成立的**（棱 → 草图）
⇒ 结果：**两个候选都被排除**，真因是**第三个**（`SelectByID2` 的 bool 不可信）
```
★ **判别实验的价值**：它不直接回答"功能为什么不行"，而是**先把"我的观测"排除掉**。

## 三、★★ 三次同一纪律
```
轮 152：查「我的量法对不对」
轮 153：查「我以为前提满足了没有」
轮 154：查「**我读那个前提的方法对不对**」
⇒ 三次都在把**"我的观测"本身当成待验对象**。
★ 而三次的结论都是：**观测方法本身有问题**（滞后一格 / 前提没验 / bool 不可信）。
```

## 四、★ 一条可直接用的判据（事实 94）
```
判「选上没有」：一律回读 `GetSelectedObjectCount2(<mark>)`
**不要看 `SelectByID2` 的返回值**（它只表示"找到了那个名字/位置"）
```

## 五、未查证
* ⚠ `InsertCompositeCurve` **真因仍未查明**（失败点更清楚：得先真的选中 2 条边）；
* ⚠ 判别实验只在**草图**上做；**棱为什么返回 True 却没选中，未查明**；
* ⚠ `composite_curve` **不升级**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

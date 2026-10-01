import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\036-sketch-query-verified")
S.mkdir(parents=True, exist_ok=True)

spec = """# 036 · 草图读回：真机 17/17 —— 顺带**补上一处 A1 覆盖缺口**

**Status**: Implemented（轮 117）

## 一、为什么挑它
`035` 验实了 `equations`。剩下 3 条 `stitched` 里，**`sw_sketch` 的取法最该验**：
轮 111（`030`）我把它 **6 个官方已废弃的取法换成了后继**，
其中 **`GetLines2` 还多带一个参数**（`swCrossHatchFilter_e`）——
⚠ 那次**只有静态证据**，签名若对不上，**代码会在运行期炸**。

## 二、真机冒烟：**17/17 通过**（程序化造前置，不靠人手）
```
✓ start_sketch（进草图编辑态）· sketch_line（1 条线）· sketch_arc（1 段弧）
✓ 取到 ActiveSketch
✓ ★ get_lines（后继）          list · **12** 个元素
✓ ★ get_arcs（后继）           list · **16**
✓ ★ get_ellipses（后继）       list · 0
✓ ★ get_parabolas（后继）      list · 0
✓ ★ get_sketch_points（后继）  list · **5**
✓ ★ get_user_points（后继）    list · 0
✓ ★★ 画了线 ⇒ get_lines **非空**（不是「没报错」就算）
✓   get_sketch_segments（未换，对照） list · **2**   ← ★ 交叉验证：正好是线+弧
✓ end_sketch · 关件不保存 · ★ 收尾无残留模态框
```

## 三、★★ 拿到的是**交叉验证过的**证据，不只是"没报错"
```
我们画了：1 条线 + 1 段弧
get_sketch_segments 返回 **2**   ← 与"画了两样东西"对得上
get_lines           返回 **12** 个浮点 ← 一条线的数据量
get_arcs            返回 **16**        ← 一段弧的数据量
get_ellipses / get_parabolas / get_user_points 返回 **0** ← 没画这些，合理
```
★ 这与 `035` 的「往返一致」是同一档证据：**空操作/假成功满足不了它**。
⚠ 与 `012` 的教训对照：那时 `list_render_materials` 返回 **0 个材质**，「没报错」什么都没证明。

## 四、★ 顺带查出一处 **A1 覆盖缺口**
```
abilities 里 `sketch_edit_ops` 只管**草图编辑**（倒角/镜像/转换实体引用）
⇒ **`sw_sketch.py`（草图读回）此前根本没有能力条目**
⇒ A1「每域都有来源」在这一处其实是**空的**（没人注意到）
```
⇒ 本轮**新建条目 `sketch_query`** 并直接标 **`verified`**（真机证据已在手）。

## 五、判据
| ID | 判据 |
|---|---|
| SC-3201 | 真机 **17/17**；**收尾无残留模态框**；临时件已关且未保存 |
| SC-3202 | ★ **交叉验证**：`get_sketch_segments == 2`（画了线+弧）、`get_lines` 非空 |
| SC-3203 | ★ **验到了轮 111 那次替换**：6 个后继（含唯一带参的 `GetLines2`）真机可调 |
| SC-3204 | ★ **新建 `sketch_query` 条目并标 `verified`**（补 A1 缺口）|
| SC-3205 | 同步 `sw_sketch.py` 与测试里的**过时注释**（"未在本机实测"）|
| SC-3206 | 门禁 + 回归不退化（回归 **1091 passed**）|

## ⚠ 明确记下的限度
* **只证「没抛异常 + 元素数合理」**，**不证元素内容/顺序正确**（浮点数组的排列顺序未核）；
* 只测了**线 + 弧**；**椭圆 / 抛物线 / 样条 / 多段线 / 用户点**的真机取法**未测**（本次都返回 0，因为没画）；
* `collect_sketch_evidence` 与变换类**未纳入本次冒烟**；
* 另 2 条 `stitched`（螺旋线 / 草图编辑 / 转换实体引用）**仍未验**。
"""

plan = """# 036 · Plan

## 步骤
1. ★ 挑 `sw_sketch` —— 因为**轮 111 换的 6 个取法只有静态证据**（最高风险）
2. 查仓库有没有现成的"造草图"件 ⇒ 有：`sw_part.start_sketch` / `sketch_line` / `sketch_arc` / `end_sketch`
3. 写冒烟：新零件 → 进草图 → 画 1 线 + 1 弧 → 逐个调取法 → 退草图 → 关件不保存
   * `CommandInProgress` + **收尾查模态框**（事实 64）
4. 跑 ⇒ **17/17**；`get_sketch_segments == 2`（**交叉验证**）
5. ★ 顺手查 `sw_sketch` 挂在哪个能力条目下 ⇒ **发现它没有条目**（A1 缺口）⇒ **新建 `sketch_query`**
6. 同步源码与测试里的**过时注释**
7. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **进草图编辑态触发模态框**（轮 98 场景） | 只在新零件上、程序化造前置、**收尾查模态框** |
| 把"没报错"当证据 | ★ **交叉验证**：画了 2 样东西 ⇒ `segments == 2` |
| 只验替换、不查覆盖 | ★ 顺手查归属 ⇒ **查出 A1 缺口** |
| 改了模块却不改过时注释 | ★ 测试与源码里"未在本机实测"全部同步 |
"""

tasks = """# 036 · Tasks（全部完成，轮 117）

- [x] T-3201 挑 `sw_sketch`（轮 111 换的 6 个取法只有静态证据）
- [x] T-3202 查现成的造草图件 ⇒ `start_sketch` / `sketch_line` / `sketch_arc` / `end_sketch`
- [x] T-3203 写 `tools/verify_sketch_getters_smoke.py`
  `→ 验收:` `python tools/verify_sketch_getters_smoke.py`（**17/17**）
- [x] T-3204 ★ 交叉验证 `get_sketch_segments == 2`（画了线+弧）
- [x] T-3205 ★ 查归属 ⇒ **发现 `sw_sketch` 没有能力条目** ⇒ 新建 `sketch_query`（`verified`）
- [x] T-3206 同步源码与测试里的过时注释（"未在本机实测"）
- [x] T-3207 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 036 · Converge

**Converged**: 2026-10-01（轮 117）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3201 真机 17/17 + 无残留模态框 | ✅ 临时件已关且未保存 |
| SC-3202 交叉验证 | ✅ `segments == 2`（线+弧）· `lines == 12` |
| SC-3203 验到轮 111 那次替换 | ✅ 6 个后继（含 `GetLines2`）真机可调 |
| SC-3204 补 A1 缺口 | ✅ 新建 `sketch_query`（`verified`）|
| SC-3205 同步过时注释 | ✅ 源码 1 处 + 测试 2 处 |
| SC-3206 门禁 + 回归 | ✅ `release_check` exit 0 · **1091 passed** |

**能力分布**：**35 条**（新增 1）· `verified 28 → **29**` · `stitched 5`

## 二、★★ 连着两轮验实，方向是对的
```
035  equations  stitched → verified（往返一致）
036  sw_sketch  **新建条目**并直接 verified（交叉验证）
```
★ 两轮的共同点：**证据都是"能被空操作证伪"的那种** ——
```
「写进去的 == 读回来的」（035）
「画了 2 样东西 ⇒ segments == 2」（036）
```
⇒ 而不是「没抛异常」。

## 三、★ 本轮**顺手**查出一处 A1 覆盖缺口
```
`sketch_edit_ops` 只管**草图编辑** ⇒ **`sw_sketch.py`（读回）没有能力条目**
⇒ A1「每域都有来源」在这一处**本来是空的**，而**没人注意到**
```
★ 教训：**"能力有实现"与"能力有条目"是两件事** ——
`017` 发现过"有实现但没暴露"，本轮发现"**有实现但没登记**"。
⚠ 同类缺口**可能还有**（未逐模块核对 `scripts/sw_*.py` 与 `capabilities.yaml` 的对应关系）。

## 四、⚠ 这一轮暴露出的**新问题**（值得下轮做）
```
scripts/ 下有多少个 sw_*.py **没有对应的 capability 条目**？
⇒ 本轮只碰巧发现了一个（sw_sketch）
⇒ **未做系统核对**
```
★ 这属于 A1/A4 的直接判据，**且可以机器化**（模块名 ↔ 条目名的对应）。

## 五、未查证
* **只证"没抛异常 + 元素数合理"**，不证元素内容/顺序正确；
* 只测了**线 + 弧**；椭圆 / 抛物线 / 样条 / 多段线 / 用户点**未测**；
* `collect_sketch_evidence` 与变换类**未纳入冒烟**；
* **`scripts/sw_*.py` ↔ `capabilities.yaml` 的对应关系未系统核对**；
* 另 3 条 `stitched`（螺旋线 / 草图编辑 / 转换实体引用）**仍未验**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

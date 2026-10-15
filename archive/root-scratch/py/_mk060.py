import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\060-getter-shapes-and-spline-silent-noop")
S.mkdir(parents=True, exist_ok=True)

spec = """# 060 · 用**同样的强判据**查其余取法 —— 查出「通例」与一个**静默空操作**

**Status**: Implemented（轮 141）

## 一、起因（`059` 留的问题）
`059` 在 `get_lines` 上发现「返回的是**数值数组**（每条 12 个 `float`）」，
并在限度里写明：⚠ **`get_arcs` / `get_ellipses` 是否也这样，未测** ——
「**同样的疑问需要同样的强判据才能证**」。
⇒ 本轮**逐个量**。

## 二、★★ 结果 ①：**是通例，不是孤例**
`tools/probe_sketch_getter_shapes.py`（真机，画 N=1/2 个）：

| 取法 | 画 1 个 | 画 2 个 | 每个占几个 `float` |
|---|---|---|---|
| `get_lines` | 12 | 24 | **12** |
| `get_arcs` | 16 | 32 | **16** |
| `get_ellipses` | 22 | 44 | **22** |

⇒ ★ `get_*` 系列**全都返回数值数组**（元素类型是 `float`）⇒ 与 `get_lines` 同类。
⇒ 已把三个取法的 docstring 写明形状 + 契约测试 3 条钉住。

## 三、★★★ 结果 ②：`sketch_spline` 是**静默空操作**
```
① CreateSpline2            ⇒ 返回 **None** ⇒ `get_sketch_segments` = **0**（不抛异常）
② **重绘**（GraphicsRedraw）后 ⇒ **仍是 0**  ⇒ ★ **排除**官方 Remarks 那句「必须重绘才看得见」
③ CreateSpline（1 参旧版）  ⇒ **迟到绑定里没有这个成员**
④ 对照·同流程画直线         ⇒ **1** ⇒ 流程本身没问题
```
★ 根因：`CreateSpline2` 官方已 **Obsolete**，后继 `CreateSpline3(Object,Object,Object,Boolean,Object&)`
末参是 **BYREF `Object&`** ⇒ **事实 47/68 的架构限制** ⇒ **这条后端上不达**。
⇒ 处置照 `sw_surface._invoke` 的先例（**事实 40**）：**让失败可见** —— 返回 `None` 即抛 `RuntimeError`。

### ⚠ 并记下**我中途的一次判据错**
```
第一次测"重绘"时把 `ActiveView` **当方法调**（它是**属性**）⇒ 报 EXC ⇒ **那次重绘根本没发生**
⇒ 若就此收工，就会**漏掉"官方那条解释是否成立"这一步**
⇒ 改成 `sw.ActiveDoc.ActiveView` 后重绘真的发生 ⇒ **重绘后仍是 0** ⇒ 结论才站得住。
★ 与 `048`/`057` 同族：**绿了/红了先别下结论，先核对"我量的是不是那个东西"。**
```

## 四、判据
| ID | 判据 |
|---|---|
| SC-5601 | ★★ 逐个量三个取法 ⇒ **12/16/22**，证明是**通例** |
| SC-5602 | ★★ 查出 `sketch_spline` **返回 `None` 且段数 0**（不抛）|
| SC-5603 | ★★ **重绘后仍 0** ⇒ 排除官方 Remarks 的解释（并**记下我那次重绘没真发生**）|
| SC-5604 | ★ 对照（同流程直线 = 1）⇒ 证明流程没问题 |
| SC-5605 | ★ 根因：`CreateSpline3` 末参 BYREF ⇒ 事实 47/68 |
| SC-5606 | ★ 处置：**让失败可见**（返回 `None` 即抛），照事实 40 的先例 |
| SC-5607 | ★ 三个取法的 docstring 写明形状 + 契约测试 **18 passed** |
| SC-5608 | 已知事实 82 入库；门禁 + 回归不退化（回归 **1199 passed**）|

## ⚠ 明确记下的限度
* 那 12/16/22 个 `float` 的**具体含义未逐位核**；
* `get_splines` / `get_polylines` / `get_sketch_points` 等**其余取法的形状未测**
  （`get_splines` 量到 0 是**因为样条画不出来**，不是取法本身的问题）；
* `CreateSpline3` 的 BYREF 末参**没有再去试**（事实 47 已穷尽 20+ 形态）。
"""

plan = """# 060 · Plan

## 步骤
1. `059` 留的问题：`get_arcs` / `get_ellipses` 是不是也返回数值数组？
2. 写通用探针：画 N=1/2 个某类实体，对比 `get_sketch_segments`（真值）与取法返回的个数
3. 跑 ⇒ **line 12 · arc 16 · ellipse 22** ⇒ ★ **通例**
4. ⚠ **`get_splines` 量到 0** ⇒ **要去看**（不是"取法不工作"就完了）
5. 追根：`sketch_spline` **返回 `None`**、段数 **0**、**不抛**
6. ⚠ 第一次测重绘**当方法调了属性** ⇒ 重绘没发生 ⇒ **修对再测** ⇒ **重绘后仍 0**
7. 查官方 ⇒ `CreateSpline2` **Obsolete**，后继 `CreateSpline3` 末参 **BYREF** ⇒ 事实 47/68
8. 处置：**让失败可见**（抛）+ docstring + 契约测试 + 事实 82 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到 `get_splines` = 0 就写"取法不工作" | ★ **去看**：真值是 0 ⇒ 是**画不出来** |
| 重绘那次报错就跳过 | ★ **修对再测**（否则"官方那条解释"没被排除）|
| 只改 `sketch_spline` 不写清根因 | ★ docstring 里**写明实测四条**，免得下一个人再试 |
| 顺手也去试 `CreateSpline3` | **不做**（事实 47 已穷尽）|
"""

tasks = """# 060 · Tasks（全部完成，轮 141）

- [x] T-5601 写通用探针 `tools/probe_sketch_getter_shapes.py`
  `→ 验收:` `python tools/probe_sketch_getter_shapes.py`（**12/16/22**）
- [x] T-5602 ★★ 追 `get_splines` = 0 的根因
  `→ 验收:` `python tools/probe_spline_creation.py`（返回 **None**）
- [x] T-5603 ★★ 排除官方"必须重绘"的解释
  `→ 验收:` `python tools/probe_spline_redraw.py`（**重绘后仍 0**）
- [x] T-5604 ★ 处置：`sketch_spline` 返回 `None` 即抛 + docstring 写明四条实测
- [x] T-5605 ★ 三个取法的 docstring 写明形状 + 契约测试 3 条
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`（**18 passed**）
- [x] T-5606 能力条目（两条）+ 已知事实 82 + 地图重跑
- [x] T-5607 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 060 · Converge

**Converged**: 2026-10-01（轮 141）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-5601 通例 12/16/22 | ✅ |
| SC-5602 查出静默空操作 | ✅ 返回 None、段数 0 |
| SC-5603 重绘后仍 0 | ✅ 排除了官方解释 |
| SC-5604 对照 = 1 | ✅ |
| SC-5605 根因 = BYREF | ✅ 事实 47/68 |
| SC-5606 让失败可见 | ✅ |
| SC-5607 docstring + 契约 | ✅ 18 passed |
| SC-5608 事实 82 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1199 passed** |

## 二、★★★ 本轮形状：**把上一轮"未测"的那一格补上，补出一个通例 + 一个静默空操作**
```
059 的限度里写着：「get_arcs / get_ellipses 是否也是数值数组，未测」
⇒ ★ 本轮**就去做那一格** ⇒ 不但确认是通例，还**顺带**在 `get_splines` 那格
   碰到一个**静默空操作**（那是另一个、更严重的问题）
⇒ ★ **"未测"那一格值得专门去补 —— 它常常挨着别的东西。**
```
★ 与 `051`（补 `ellipse` ⇒ 顺带量出整模块单位写错）**同一个形状**：
**为了补一格而去看，看到的往往不止那一格。**

## 三、★★ 「静默空操作」是**事实 40 那一族的第三次**
```
事实 40：`Create*Surface` 返回值不可靠 ⇒ **让失败可见**（`sw_surface._invoke` 抛）
轮 141 ：`CreateSpline2` 返回 None ⇒ 改前**静默**，改后**抛**
⇒ ★ 两次都是：「失败信号长得像正常值」⇒ 处置都是**让它可见**，不是"修好它"
   （因为根因在架构：BYREF `Object&` ⇒ 事实 47/68）
```

## 四、⚠ 一次**我自己的判据错**（如实记）
```
第一次测"重绘"：把 `ActiveView` **当方法调**（它是属性）⇒ EXC ⇒ **那次重绘没发生**
⇒ 若就此收工，`sketch_spline` 的结论就**缺一环**（"是不是只是没重绘？"没被排除）
⇒ 修对后重绘真的发生 ⇒ **重绘后仍是 0** ⇒ 结论才站得住。
```
★ 本会话**第三次**「先核对量的是不是那个东西」（`048` 爬错层 · `057` 注错名字 · 本轮调错形态）。

## 五、未查证
* 12/16/22 个 `float` 的**具体含义**未逐位核；
* `get_splines` / `get_polylines` / `get_sketch_points` 等**其余取法的形状未测**；
* `CreateSpline3` 的 BYREF 末参**没有再去试**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\059-centerline-and-getlines-shape")
S.mkdir(parents=True, exist_ok=True)

spec = """# 059 · 补 `centerline` —— 顺带查清 `get_lines` **返回的根本不是线对象**

**Status**: Implemented（轮 140）

## 一、补 `centerline`（真缺档）
★ 走**现行入口** `ISketchManager.CreateCenterLine(6 doubles)` → `SketchSegment` ——
官方有**两级废弃链**：`IModelDoc2.CreateCenterLine(Object,Object)` ⇒（Superseded）⇒
`CreateCenterLineVB`（**Void** 返回的 VB 变体）⇒ **`ISketchManager.CreateCenterLine`**。
★ 官方 Remarks 另给一条路（`CreateLine` + `ConstructionGeometry`）——**本函数不走那条**。

## 二、★★ 冒烟 8/8 里冒出来的一件事
```
✓ sketch_centerline 建成（返回 CDispatch）
✓ ★★ 往返 A：`get_sketch_segments` 读回 **1 段**  ← 对
✓ ★  往返 B：`get_lines` 读回 **12 条**            ← ⚠ 只画了 1 条！
✓ ★★ **再测单位**：半径 25 的圆 ⇒ 边界框 50 ⇒ **毫米**（官方文档的「in meters」是错的）
```
⚠ **12 对 1** —— 数字对不上 ⇒ **要去看**（不是"算了"）。

## 三、★★★ 查清了：`get_lines` 返回的是**数值数组**，不是**线对象列表**
`tools/probe_getlines_count.py`（真机，画 N 条直线）：
| 画的条数 | `get_sketch_segments` | `get_lines` |
|---|---|---|
| 1 | 1 | **12** |
| 2 | 2 | **24** |
| 3 | 3 | **36** |

⇒ **完全线性：每条直线占 12 个 `float`**，且 `get_lines(...)[0]` 的类型是 **`float`**
（不是 `Dispatch`）⇒ **不能**当线对象用（没有 `.X` / `.GetStartPoint2`）。
⚠ **官方文档没写这个返回结构。**

### ⚠⚠ 而它为什么一直没被发现
```
`tools/verify_sketch_getters_smoke.py`（轮 117）的判据是「**非空**」⇒ **12 对 1 也照样绿**
⇒ ★ **判据太弱 ⇒ 真问题藏在绿里。**
```
⇒ **这正是本会话反复出现的那一类**：**"绿"不等于"对"**，判据的**强度**决定它能发现什么。

## 四、处置（四处）
1. **改写** `sw_sketch.get_lines` 的 docstring —— 写明「**数值数组**」+「每条 **12** 个 `float`」
   + 给出「**要几条线**用 `get_sketch_segments`」的替代；
2. **冒烟加定量判据**（从"非空"升级到"**= 条数 × 12**"）⇒ **18/18**；
3. **契约测试加 3 条**（pytest 风格，与本文件一致）：docstring 写明形状 · 仍是后继 `GetLines2` ·
   ★★ **仓库里不许有人把 `get_lines` 的结果当对象用**（正向判据：元素是 `float`）；
4. 能力条目 + 已知事实 81。

## 五、判据
| ID | 判据 |
|---|---|
| SC-5501 | ★★ `sketch_centerline` 走**现行入口**（不走两级废弃链）|
| SC-5502 | ★ 真机冒烟 **8/8**，含**往返**与**无残留模态框** |
| SC-5503 | ★★ **再测单位**（半径 25 ⇒ 边界框 50 ⇒ 毫米），印证官方文档那句「in meters」是错的 |
| SC-5504 | ★★★ **查清 `get_lines` 的返回形状**（12/24/36 三点线性）|
| SC-5505 | ★★ 指出**判据太弱**（「非空」）是这个语义长期没被写下的原因 |
| SC-5506 | ★ 处置四处（docstring / 冒烟定量 / 契约 3 条 / 事实 81）|
| SC-5507 | ★ 门禁 + 回归不退化（回归 **1196 passed**）|

## 六、★ 门禁尽职的一个实例
```
加完 `sketch_centerline` 后 `release_check` **exit=1**：
  [FAIL] 地图与来源同步
     常见原因①：**增删了 scripts/sw_*.py 里的公开函数** ⇒ 地图的「本仓库能力面」列计数变了
⇒ ★★ 门禁**自己把原因和命令写出来了**（跑 `tools/build_union_map.py` 再提交）
⇒ 跑完 1 行改动 ⇒ `release_check exit=0`。
```
★ 这与事实 55 那次（`sync_bundled_skill.py` 的报错**从"看不出怎么办"改成"给命令"**）同一路数：
**好门禁的报错要能直接执行。**

## ⚠ 明确记下的限度
* 那 12 个 `float` 的**具体含义**（哪几个是哪个端点、是否含额外字段）**未逐位核**；
* 中心线的**构造几何标记**是否自动置上**未测**；
* `get_arcs` / `get_ellipses` 是否也是「数值数组」**未测**（⚠ 同样的疑问，**同样的强判据**才能证）。
"""

plan = """# 059 · Plan

## 步骤
1. 挑 `centerline`（真缺 + 可用 `get_lines` 做往返）
2. ★ 查官方 ⇒ **两级废弃链** ⇒ 走 `ISketchManager.CreateCenterLine`
3. 实现 `sketch_centerline`
4. 冒烟：建成 + **往返** + **再测单位**（官方文档说 meters，轮 132 实测是毫米）
5. ⇒ **8/8**，但 ★ **12 对 1**（`get_lines`）⇒ **要去看**
6. ★★ 写探针：画 **1/2/3** 条 ⇒ **12/24/36** ⇒ **每条 12 个 `float`** ⇒ 是**数值数组**
7. ★★ 想清**为什么一直没发现**：既有判据只是「**非空**」
8. 处置四处 + 门禁（地图重跑）+ 事实 81 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到"12 对 1"就放过 | ★ **数字对不上就要去看**（本轮的核心动作）|
| 只改 docstring 不加判据 | ★ **判据要升级**（非空 → 定量），否则下一个人还会被坑 |
| 顺手也去查 `get_arcs` | **不做**（限度里写明"未测"）|
| 门禁红了先怀疑门禁 | ★ 本轮门禁**诊断直接就对了**（原因①正是我干的）|
"""

tasks = """# 059 · Tasks（全部完成，轮 140）

- [x] T-5501 查 `centerline` 入口 ⇒ **两级废弃链** ⇒ 走 `ISketchManager.CreateCenterLine`
- [x] T-5502 实现 `sketch_centerline`
- [x] T-5503 真机冒烟（建成 + 往返 + 再测单位）
  `→ 验收:` `python tools/verify_centerline_smoke.py`（**8/8**）
- [x] T-5504 ★★ 探针查清 `get_lines` 的返回形状
  `→ 验收:` `python tools/probe_getlines_count.py`（**12/24/36**）
- [x] T-5505 改写 docstring + 冒烟加定量判据
  `→ 验收:` `python tools/verify_sketch_getters_smoke.py`（**18/18**）
- [x] T-5506 契约测试加 3 条
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`（**15 passed**）
- [x] T-5507 能力条目 + 已知事实 81 + **地图重跑**（门禁尽职抓到）
- [x] T-5508 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 059 · Converge

**Converged**: 2026-10-01（轮 140）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-5501 现行入口 | ✅ |
| SC-5502 冒烟 8/8 | ✅ |
| SC-5503 再测单位 | ✅ 50 mm ⇒ 文档的「in meters」是错的 |
| SC-5504 查清 `get_lines` 形状 | ✅ 12/24/36 |
| SC-5505 指出判据太弱 | ✅ |
| SC-5506 处置四处 | ✅ |
| SC-5507 门禁 + 回归 | ✅ `release_check` exit 0 · **1196 passed** |

## 二、★★★ 本轮最有价值的一句：**一个"12 对 1"引出了一类问题**
```
冒烟本来要证的只是"中心线建成了"
⇒ 顺带读到 `get_lines` 返回 **12**，而我只画了 **1** 条
⇒ ★ 没放过它 ⇒ 查出：**返回的是数值数组（每条 12 个 float），不是对象列表**
⇒ ★★ 而这个语义**官方文档没写、仓库里也没人写下** ——
   因为**既有判据只是「非空」**，12 对 1 **照样绿**。
```
★ 这是一条**可复用的认识**：
**判据的强度决定了它能发现什么；"非空/不为 None/没抛异常"这一档，放过去的东西最多。**

## 三、★ 与事实 57 / 62 / 79 是同一族
```
事实 57：一个"一直是绿的"测试，可能只是**每次环境恰好满足**
事实 62：门禁"写了"≠"有效"，**负例是唯一的证明**
事实 79：**会 skip** 的判据比"没写"更糟
本轮   ：判据**太弱**（非空）⇒ **12 对 1 也绿** ⇒ 真问题藏在绿里
⇒ ★★ 四条合起来：**"绿"有很多种假象 —— 假的绿比红更难发现。**
```

## 四、★ 门禁尽职的一个正面实例
```
加完公开函数 ⇒ `release_check` **exit=1**，报 [FAIL] 地图与来源同步
⇒ ★★ 而且它**自己写出了原因①**（"增删了 scripts/sw_*.py 里的公开函数"）**与命令**
⇒ 跑一遍 ⇒ 1 行改动 ⇒ 绿。
```
★ 好门禁的报错要**能直接执行**（与事实 55 那次同一路数）。

## 五、未查证
* 那 12 个 `float` 的**具体含义**未逐位核；
* 中心线的**构造几何标记**是否自动置上**未测**；
* `get_arcs` / `get_ellipses` 是否也是「数值数组」**未测** —— ⚠ 同样的疑问需要**同样的强判据**才能证。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

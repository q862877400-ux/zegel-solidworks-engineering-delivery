import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\017-candidate-pool")
S.mkdir(parents=True, exist_ok=True)

spec = """# 017 · 换候选池：两个口径都漏了最好的一池

**Status**: Implemented（轮 97）

## 起因：一次"想暴露特征树遍历"撞出的口径问题
前三轮（`012`/`013`/`016`）的候选都取自 **`011` 定义的「孤立能力」**
（既没暴露、也没人调用）。轮 97 想做"特征树遍历"，却发现
**`sw_review.collect_model_summary` 已经在遍历特征树并返回 JSON-ready 数据**
（`{title, type, feature_count, features:[{name,type}], path}`），**却没暴露**。

**查它为什么没被发现**：
```
出现位置：scripts/sw_review.py（定义）· tests/solidworks_spur_gear_regression.py（调用）
⇒ **只被测试调用** ⇒ 两个口径都把它排除：
   · 「孤立」口径排掉有调用者的；
   · 「未暴露 + 被生产代码调用」口径排掉只被测试调用的。
```

## ★★ 结论：候选池应当有三个，而**最好的那个被两边都漏了**
| 池 | 定义 | 好坏 |
|---|---|---|
| A · 孤立 | 未暴露 + 无人调用 | ⚠ **从没跑过** ⇒ `014` 证明混着坏的（2/17）|
| B · 生产在用 | 未暴露 + 被生产代码调用 | 好，但**已被内部使用**，暴露价值较低 |
| **C · 只被测试调用** | 未暴露 + **只有测试调** | ★ **最好**：**有测试 ⇒ 跑过的概率高** · **未暴露 ⇒ 用户够不到** |

⇒ 本特性把池 C 量出来（**12 个**）并从里面接了 3 个。

## 判据
| ID | 判据 |
|---|---|
| SC-1301 | 池 C 的探测工具可跑（`tools/probe_testonly_candidates.py`）|
| SC-1302 | 池 A / 池 B 的探测工具并存（**不删旧口径**，用于对照）|
| SC-1303 | batch8 声明 3 条、签名与实现一致（契约测试 **20 passed**）|
| SC-1304 | 3 条**真机冒烟**通过（**4/4**）|
| SC-1305 | ★ **`collect_model_summary` 真的读到特征树**（≥1 个特征，实测 **18**）|
| SC-1306 | 暴露面 **83 → 86** · 门禁 + 回归不退化（回归 **1027 passed**）|

## 明确不做
* 不删旧口径的探针（它们仍有用：池 A 用来找"从没跑过的"，池 B 用来看内部依赖）；
* 不接需要传 `spec` 数据类对象的（需先设计展平）。
"""

plan = """# 017 · Plan

**不重造**：复用 `011` 的暴露面/调用者扫描逻辑；只新增**池 C 的探测**与一批声明。

## 步骤
1. 撞见 `collect_model_summary` ⇒ 先查**为什么没被发现**（读它出现在哪些文件）
2. ⇒ 定位到「只被测试调用」这一池被两个口径同时漏掉
3. 写 `tools/probe_testonly_candidates.py` 量池 C（12 个）
4. 从池 C 取 3 个（`collect_model_summary` / `get_costing_manager` / `list_setter_summary`）
5. 契约测试 + 真机冒烟
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 直接换掉旧口径 ⇒ 丢掉池 A 的用途 | **并存三个探针**，各自说明用途 |
| 「有测试」当成「能用」 | SC-1304 要求真机冒烟（`014`/`015` 的教训）|
| 接需要 `spec` 对象的函数 | 本批**一律不接**，记为需另设计 |
"""

tasks = """# 017 · Tasks（全部完成，轮 97）

- [x] T-1301 查 `collect_model_summary` 为什么没进候选
  ⇒ **只被测试调用**，被两个口径同时排除
- [x] T-1302 写 `tools/probe_testonly_candidates.py` ⇒ 池 C **12 个**
  `→ 验收:` `python tools/probe_testonly_candidates.py`
- [x] T-1303 写 `tools/probe_expose_candidates.py`（池 B，13 个，作对照）
  `→ 验收:` `python tools/probe_expose_candidates.py`
- [x] T-1304 写 `tool_specs_batch8.py`（3 条）→ 接入（钉子 31→34）
- [x] T-1305 契约测试 `tests/test_tool_specs_batch8.py`（**20 passed**）
- [x] T-1306 真机冒烟 `tools/verify_batch8_smoke.py`（**4/4**，特征树 **18 个特征**）
- [x] T-1307 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 017 · Converge

**Converged**: 2026-10-01（轮 97）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-1301/1302 三个池的探针并存 | ✅ |
| SC-1303 声明与签名一致 | ✅ **20 passed** |
| SC-1304 真机冒烟 | ✅ **4/4** |
| SC-1305 ★ 特征树真的读到 | ✅ **18 个特征**（键：`feature_count`/`features`/`path`/`title`/`type`）|
| SC-1306 暴露面 83 → **86** · 回归 | ✅ `release_check` exit 0 · 回归 **1027 passed** |

## 二、★ 本轮最有价值的是**口径的更正**，不是那 3 个工具
```
池 A（孤立）        —— 前 3 轮用的  ⇒ 014 证明混着坏的（17 个里 2 个跑不通）
池 B（生产在用）    —— 13 个          ⇒ 已被内部使用
池 C（只被测试调用）—— **12 个**       ⇒ ★ 最好：有测试 ⇒ 跑过的概率高；未暴露 ⇒ 用户够不到
```
**⇒ `collect_model_summary` 就是池 C 的** —— 前三轮**永远找不到它**。

## 三、⚠ 证据强度不均（如实记）
* `collect_model_summary` **强**：拿到 **18 个特征**，与文档特征树一致；
* `list_setter_summary` **中**：返回 9 个键，**未核键的含义**；
* `get_costing_manager` **弱**：返回 **`None`** ⇒ **只证明"不报错"，不证明"有用"**。

## 四、未查证
* 池 C 里剩下的 **9 个**（含 2 个需要 `spec` 数据类对象的）**未接**；
* **`get_costing_manager` 返回 `None` 是不是"该文档没有 Costing"** —— 未查（需一个有 Costing 的文档）；
* 池 B 的 **13 个一个都没接** —— 它们"被生产代码调用"，暴露价值需单独评估。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

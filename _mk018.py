import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\018-batch9-mold-expose")
S.mkdir(parents=True, exist_ok=True)

spec = """# 018 · 模具域补暴露 —— 以及一次**卡住会话的模态框**

**Status**: Implemented（轮 98–99）

## 一、能力侧的发现：一个「真缺口」其实是「已实现但没暴露」
`010` 把 338 个缺口分了四类。回头看**最小域（模具）的唯一"真缺口"** `tooling_split`：
```
官方成员：InsertMoldCoreCavitySolids / CoreCavitySplit
本仓库：scripts/sw_mold.py::insert_core_cavity_solids   ← **已经实现了**
        insert_core_cavity_solids   已暴露=否 · 有测试=是
        insert_parting_surface      已暴露=否 · 有测试=是
        mold_undercut_detect        已暴露=否 · 有测试=是
```
⇒ ★ **那个"真缺口"是 `010` 记的第三类（能力在、未暴露）**，不是要新写的。
⇒ batch9 把这三个接出去。

## 二、⚠⚠ 一次**真实事故**：模态框卡住会话
第一版冒烟在**空零件**上调 `insert_parting_surface` / `insert_core_cavity_solids`
⇒ SolidWorks 弹出**模态框**「**此拔模方向尚未定义。**」⇒ **卡住会话**（用户连续两次截图报错）。

**★ 记下的两条新事实**：
1. **`ISldWorks.CommandInProgress = True` 不能抑制这个模态框** ——
   铁律 2 说它抑制"未抑制的模态对话框"，**这里是反例**；
2. **改「视图/选择状态」的工具会把文档标脏** —— 批次 7 的三个工具在装配体上跑过后，
   主窗口标题变成 `mcp_avi_asm.SLDASM *`（**未保存标记**）。
   ⚠ 轮 96 曾把这记为「未查证」，**轮 99 得到答案：会脏**。

**处置**：
* 冒烟改为**前置条件感知** —— 那 2 个**一个都不调**，只把它们的**前置条件写下来**；
* 批次 7 的 3 条 doc **加警告**（`May mark the document as modified`）；
* 两条事实写进 `known-facts.md`（64/65）；
* **清理**：关掉我造的全部临时件（按标题匹配 `零件N` **且路径为空**，绝不碰有路径的）；
* **未保存任何东西**。

## 三、判据
| ID | 判据 |
|---|---|
| SC-1401 | batch9 声明 3 条、签名一致（契约测试）|
| SC-1402 | ★ 3 条的**前置条件已记录**（防下一个人再踩弹窗）|
| SC-1403 | 冒烟**不调用**那 2 个会弹框的工具 |
| SC-1404 | 批次 7 的 3 条 doc **都带脏标警告**（实测警告出现 **3** 次）|
| SC-1405 | `known-facts.md` 记下 64/65 |
| SC-1406 | 门禁 + 回归不退化（回归 **1039 passed**）|
| SC-1407 | ★ **未验证项如实声明**：`insert_core_cavity_solids` / `insert_parting_surface` 的**真机行为未验** |
"""

plan = """# 018 · Plan

## 步骤
1. 从模具域的最小缺口 `tooling_split` 查到「已实现未暴露」
2. 写 `tool_specs_batch9.py`（3 条）→ 接入（钉子 34→37）
3. 契约测试
4. ★ 真机冒烟 ⇒ **撞上模态框** ⇒ **停下来改设计**（不再硬调）
5. 记录两条新事实 + 给批次 7 的 doc 加警告 + 清理临时件
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **模态框卡住会话**（本轮真实发生）| ★ 前置条件感知的冒烟；**不调**需要前置几何的工具 |
| **把用户文档弄脏** | 只关**自己造的**（自动命名 + 路径为空）；**绝不保存** |
| 「已实现」当成「能用」| SC-1407 明确声明未验证项 |
"""

tasks = """# 018 · Tasks（轮 98–99）

- [x] T-1401 查 `tooling_split` ⇒ 发现 `insert_core_cavity_solids` 已实现且有测试
- [x] T-1402 写 `tool_specs_batch9.py` → 接入（钉子 34→37）
- [x] T-1403 契约测试 `tests/test_tool_specs_batch9.py`
- [x] T-1404 ★ 真机冒烟 ⇒ **模态框卡住会话**（用户两次截图）
- [x] T-1405 ★ 改设计：冒烟改**前置条件感知**，那 2 个**一个都不调**
  `→ 验收:` `python tools/verify_batch9_smoke.py`（5/5，且**不弹框**）
- [x] T-1406 记录事实 64/65（`known-facts.md`）· 批次 7 三条 doc 加警告 · 清理临时件
- [x] T-1407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 018 · Converge

**Converged**: 2026-10-01（轮 99）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-1401 声明 3 条、签名一致 | ✅ 契约测试 |
| SC-1402 前置条件已记录 | ✅ 冒烟输出带 `preconditions` |
| SC-1403 冒烟**不调**会弹框的 2 个 | ✅ 5/5，**没有再弹框** |
| SC-1404 批次 7 三条 doc 都带警告 | ✅ 警告出现 **3** 次 |
| SC-1405 事实 64/65 入库 | ✅ |
| SC-1406 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1039 passed** |
| SC-1407 未验证项如实声明 | ✅ 见 §三 |

## 二、⚠⚠ 本轮**真实事故**（必须记住）
```
第一版冒烟在空零件上调 insert_parting_surface / insert_core_cavity_solids
⇒ 模态框「此拔模方向尚未定义。」⇒ 卡住会话（用户连续两次截图报错）
```
**两条新事实**（已入 `known-facts.md`）：
1. **`CommandInProgress = True` 不能抑制某些模态框**（铁律 2 的反例）；
2. **改视图/选择状态的工具会把文档标脏**（轮 96 的「未查证」在此得到答案）。

**处置**：冒烟改前置条件感知（不调会弹框的）· 批次 7 三条 doc 加警告 ·
**关掉我造的全部临时件**（只匹配「自动命名 + 路径为空」，**绝不碰有路径的**）· **未保存任何东西**。

## 三、⚠ 未验证（如实记）
* `insert_core_cavity_solids` / `insert_parting_surface` 的**真机行为未验** ——
  需要**已准备的分型件**（已定义拔模方向 + 已插入分型线）才能安全调；
* 因此 batch9 的这 2 条**只有静态证据**（声明与签名一致 + 有测试），**没有运行证据**。

## 四、⚠ 一句要紧的话：**这不会让「缺口 338」变小**
计数按**操作名归一**比：我们叫 `core_cavity_solids`、外部叫 `tooling_split` ⇒ **名字对不上**。
★ **名字级计数 ≠ 能力级覆盖** —— 本批闭的是**能力**（用户现在能做这件事）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

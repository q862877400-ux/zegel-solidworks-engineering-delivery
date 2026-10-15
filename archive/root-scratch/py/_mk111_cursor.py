import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           616 🎯 **Spec Kit `111`：`release_check` 的返回体**每道门禁都带明细**（把「覆盖面隐形」修掉）**（轮 191）——
               ★ 起因：把轮 190 的定则（报 0 命中必须报覆盖面）**推广到基础设施层** ——
               不让 17 道门禁**各自**写覆盖面文档（那样只会变成**样板话**），而是改**一处**。
            617 ★★★ **实测（读 `release_check` 的**实际输出**，不是源码里有没有那几个词）**：
               ```
               ⚠ 第一版判据我按**源码关键词**（"覆盖"/"范围"/"扫了"）判 ⇒ **17 道全部"是"**
                 —— 那些词出现在它们的**文档串**里 ⇒ **判据太松**（与轮 185 同一个坑）
               ⇒ 改成看实际输出：
               轮 74 **已经修了一半**（test_gate_negative_cases.py L783 记着「此前只汇总了 4 个门禁」）：
                 ✅ 13 个门禁的 **`status`** 都进返回体 · ✅ **`skipped` 显式列出**
               ★ 但**每道门禁的 `output`（"扫了多少 / 跳过了什么"）仍只有 4 道有**：
                 provenance / diff_markers / member_names / interface_ownership
               ⇒ ★★ 其余 **11 道在结果里只有 `"status": "pass"`** ⇒
                 **「status 隐形」修了，「覆盖面隐形」没修** —— 而
                 **`status: pass` 与「没覆盖任何东西」在输出上长得一模一样**（轮 190 的定则）
               ```
            618 ★★★ **修法（一处改，16 道全受益）**：`gates` 与 `gate_details` 在**同一个循环**里一起建
               ⇒ **不可能分叉**；明细取 `output` > `reason` > `status`（**绝不返回空串**，否则像"没有明细"）。
               ★ 新增纯函数 `_gate_detail(res)`（可单测）。改后实测：
               ```
               `gates` **16** 道 = `gate_details` **16** 道 · **空明细 0 个** · 键集合相同 ✓
               ★ 11 道此前的"光秃秃 pass"现在都可读，例：
                 env_pitfalls             「环境坑静态检查 · 扫 413 个 .py」
                 license_redlines         「A6 许可红线门禁 · 扫 413 个 .py」
                 gate_wiring              「门禁接线元门禁 · `scripts/check_*.py` 17 个 · 豁免登记 1 条」
                 workspace_shadowing      「server.py 用到的顶层第三方包 2 个；工作区 D:\AI\SW」
               ```
            619 ★★ **按事实 62 加了**带负例**的测试**（`test_gate_negative_cases.py` 的「第六层」）：
               判据 `_detail_gaps(gates, details)`：**键集合必须相等且每条非空** ⇒ 四种输入都验了：
               ```
               ① 全都有 ⇒ 通过  ② 少一道 ⇒ 报  ③ **有键但值为空** ⇒ 报（★ 最隐蔽：看起来像"有明细"）
               ④ 两种同时 ⇒ 都报
               ```
               ★ 与**已有**那条的区别：轮 74 只断言 `"gates": gates` **在源码里出现过**；
                 本轮断言的是**运行时返回体的不变量**，并用负例证明**判据有牙**。
            620 ★★★ **本轮收敛出的定则**：
               > **能靠结构保证的，不要靠约定。**
               ```
               轮 190 的定则若按字面执行（"每道门禁声明覆盖面"）⇒ 结果是 17 份**人写的样板话**，
               且**没法判它写没写全**（判据只剩"文档里有没有那两个词"）—— 那正是我第一版判据的样子。
               ⇒ ★ 真正的修法是**改数据结构**：两者同循环生成 ⇒「有状态没明细」**结构上不可能发生**，
                 于是判据也变成可判的（键集合相等 + 非空）。
               ⇒ ★★ 推论：**断言"某段源码存在" ≠ 断言"某个不变量成立"** ——
                 前者在**重构后**仍可能通过（字段名没变、内容变了）。
               ```
               门禁 + `release_check` exit 0 · 回归 **1250 passed**（+2 条新测试）。
               ⚑ **未查证**：⚠ 有些门禁的 pass 分支**不打印** `output` ⇒ 它们退回 `reason`/`status`（明细较薄）；
                 ⚠ 明细**截断 700 字符**；⚠ ★ **只检查了"明细存在且非空"，没检查"明细里真的写了覆盖面"**
                 ⇒ 一个门禁仍可打印一句没信息量的 output 而通过本判据（**如实记**）；
                 ⚠ 本轮**没改**任何门禁的判定逻辑。
               下轮候选：① 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ② 给几个"明细较薄"的门禁补一句**带分母**的 output；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+616 ", before, re.M):
    print("  游标 616 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+620 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 620 行已存在 ✓")

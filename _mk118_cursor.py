import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           651 🎯 **Spec Kit `118`：全仓扫「缺源 ⇒ 静默假值」—— 125 处守卫 / 12 个候选，7 个门禁候选逐个核过****全部合法******（轮 198）——
               ★ 起因：闭合轮 197 记下的限度「别的测试/脚本里**可能还有同类兜底**」（**当时没扫**）。
            652 ★★★ **扫描结果**（`tools/scan_silent_source_fallbacks.py`，纯静态）：
               ```
               扫了 **398** 个文件 · 缺源守卫 **125** 处
               ★ **已写明理由**的合法返回: **7** 处
               ★★ **候选**（缺源 ⇒ 返回假值，且**未见说明**）: **12** 处
                  7 个在门禁/scripts · 3 个在 scripts · 4 个在 tests（契约测试的 `_members` 桩）
               ```
            653 ★★★ **7 个门禁候选逐个回代码核 ⇒ **全部有正当理由**（诚实负结果）**：
               ```
               ① parse_swapi              docstring 明写「拿不到就回空」⇒ 合法
               ② load_falsy_zero_baseline 语义上"没有基线文件" = "没有已记账存量" ⇒ 合法
               ③ members_of               该门禁是**诊断**（非硬门禁）
               ④ claimed_drift            docstring 说明 + **调用方有显式分支**（"曾经是 SKIP，那是假绿"）
               ⑤ reflection_files         调用方有 `if not refs: SKIP; return 0` ⇒ 合法
               ⑥ rule_registry            ★ **轮 193 我自己写的**，docstring 明写「空集会让检查**报错**」
               ⑦ ★★★ check_workspace_shadowing ⇒ **调用方有显式守卫**，而且是**正面样板**：
                  「`mcp-server/` 目录在，但读不到 `server.py` ⇒ **仓库不完整**」
                  「读不到 ⇒ **一个包都没查** ⇒ 遮蔽问题会**静默漏过**（而那正是本门禁要抓的）」⇒ return 1
               ```
            654 ★★★ **本轮真正的定则（可复用）**：
               ```
               **「缺源 ⇒ 返回值」本身不是缺陷** —— 缺陷是「**缺源 ⇒ 最终结论变成「通过」**」
               ⇒ ★ 所以判据**必须看到调用方**；而这个扫描**看不到** ⇒ ★★ **它只能当粗筛**
               ★ 与**事实 51** 同源：抓不到目标类别的检查，往往是"分析范围"与代码的
                 "组织单元"不匹配 —— 我分析的是**函数内**，而缺陷住在**调用方**
               ```
            655 ⚠⚠⚠ **而我本轮踩了三次自己的坑**：
               ```
               ① `ast.Dict` **没有 `.elts`**（用 keys/values）—— 把 List/Dict/Set/Tuple 写在同一支 ⇒ 崩
               ② `p.relative_to(ROOT)` 对**临时目录**抛 `ValueError` ⇒ ★ **正是轮 68 记过的那个**
                  （"生成器对 OUT/SCAN 在哪不能做假设"）；⚠ 而它**恰好挡住了负例自证**（事实 62）
               ③ 第一版"已说明"词表**漏了「拿不到 / 回空」** ⇒ 4 处已写明的被误报（14 → 12）
               ★ 三条同族：**我以为的形状/词表/路径与实际差一层**
                 （事实 114/115/116/135/136/137 同一主线）
               ```
               ★★ **负例自证**（事实 62）：合成两个文件（一个静默 `return False`、一个 docstring 写明理由）
                 ⇒ 扫描器**只列出静默的那个**、已说明的**不计入** ⇒ ✓ 判据有牙
                 （★ 否则"没发现缺陷"这个结论**没有保证**）。
               门禁 + `release_check` exit 0 · 回归 **1260 passed**。
               ⚑ **未查证**：⚠ **3 个 scripts + 4 个 tests 的候选未逐个核**（如实记）⇒ 它们**可能**含真问题；
                 ⚠ 判据**看不到调用方** ⇒ **只能当粗筛**（0 候选 ≠ 没问题）；
                 ⚠ 「已说明」是**词表匹配** ⇒ **不全会误报**（本轮已补一次，**仍可能不全**）；
                 ⚠ 只扫**顶层** `if not <path>...` 守卫 ⇒ **嵌套/别的形态未覆盖**；
                 ⚠ 本轮**没改**任何生产逻辑。
               下轮候选：① 把 ③④⑤ 那 7 个未核候选中的 **3 scripts + 4 tests** 也逐个核；
               ② 把「缺源 ⇒ 结论变成通过」做成**调用方级**的检查（而非只扫函数内）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+651 ", before, re.M):
    print("  游标 651 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+655 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 655 行已存在 ✓")

import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           429 🎯 **Spec Kit `071`：查上一轮的「根因」—— ****推翻它****：那是****测量假象******（轮 152）——
               `070` 报的根因是「两次 `start_sketch`+`end_sketch` **只留下 1 个草图**」
               ⇒ 而那是用 **`FeatureByPositionReverse`** 数出来的。
            430 ★★★ **本轮用三种独立方式核对 ⇒ 结论被推翻**（同一时刻同一次操作）：
               ```
               树总数            : 18 → 19 → 20 → 21        ★ 每轮 +1 ⇒ **都建了**
               按名查 FeatureByName: 草图1 → 草图2 → 草图3     ★ 都查得到
               活动 ActiveSketch  : 草图1 / 草图2 / 草图3
               ⚠ FeatureByPositionReverse: [] → ['草图1'] → ['草图2','草图1']   ← **滞后一格**
               ```
               ⇒ ★★★ **它枚举的是「已提交」的特征，而「刚建的那个」要等下一个特征建了才出现**
                 ⇒ **上一轮那句是测量假象**。
            431 ★★ **更正后的实况（比上一轮更严格）**：
               ```
               ✓ 前提**满足了**：按名查确实有 2 个草图（草图1 / 草图2）
               ✓ mark=1 各选一次（草图2=True · 草图1=True）
               ✗ **`InsertCompositeCurve` 仍返回 False**  ⇒ ★ **真因仍未查明**
               ```
               ⇒ ★ 上一轮把 `False` 定性成「前提未满足、**属应然**」—— **这个定性不成立了**，
                 它是**真的失败了**。
            432 ★★★ **本会话第 4 次自我更正**（事实 70 / 82 / 84 / **91**）：
               共同点都是「**在证据不足（或测量方法单一）时下了定性**」；
               ★ 而本轮的新教训更具体：**「我量到了 X」与「X 是真的」之间，
                 隔着一个「我的量法对不对」。**
               ⇒ 处置：**就地更正**事实 91（保留原话 + 写明依据）+ 更正能力条目里那句
                 「根因是前提没满足」；新事实 **92** 记下那个**可复用的测量陷阱**。
            433 ⚠ **门禁尽职了一次**：我在 `071` 的 `tasks.md` 里写了个**仓库外**的验收命令
               （`_diag_sketch_visibility.py` 在 `D:\AI\SW\`）⇒ `check_spec_acceptance_paths.py`
               **当场红**（`[bare-not-found]`）⇒ 按它给的修法把那次诊断**按仓库规范收进 `tools/`**
               （`tools/probe_sketch_enumeration_lag.py`，带来源块、可复跑、末行打印
               **滞后一格观测到: True**）。
               ⚑ **未查证**：⚠ **`InsertCompositeCurve` 的真因仍未查明**（前提已排除）；
                 ⚠ 其它候选（「要选边而不是整个草图」等）**都没验证**；
                 ⚠ 「滞后一格」只在**本机 SW 2026 SP4.1** 上量过，别处未验。
               已知事实 **92** 入库（91 已就地更正）· 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① 换**边/曲线**而不是整个草图去试 `InsertCompositeCurve`（别的候选）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+429 ", before, re.M):
    print("  游标 429 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+433 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 433 行已存在 ✓")

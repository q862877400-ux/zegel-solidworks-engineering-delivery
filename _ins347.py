import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           347 🎯 **Spec Kit `054`：系统扫一遍「死守卫」—— 规则 2 的****角度那一半**也是死的****（轮 135）——
               方法复用 `053`：在 `mcp-server/` + `scripts/` 里找**模块级常量**，
               名字像门禁（`*_RE`/`*_SUFFIX`/`*_NAMES`/`*_MARK`/`*_ALLOWED`…），
               数它**在同一文件里出现几次** ⇒ **只出现 1 次**（只有赋值那行）即可疑。
               ⇒ 结果：**扫过 21 个 · 只出现 1 次的 2 个**。
            348 ★★ **逐条人工判**：
               | 可疑 | 判定 |
               |---|---|
               | `tool_registry.py:79` **`_ANGLE_SUFFIX`** | ✗ **真·死守卫** —— 它与 `_LEN_SUFFIX` **并排定义**（L77 注释写着「长度以 `_mm`、角度以 `_deg` 结尾」）而**两个都没被用过** |
               | `sw_sketch_edit.py:67` `SKETCH_MIRROR_MARK` | ① **文档性常量**（注释明说"**不是参数**，是选实体时的 mark"）⇒ **假阳性** |
               ⇒ 假阳性 **1/2 = 50%** ⇒ ★ **本探针同样不能单独当门禁**（出清单、人工判）。
            349 ⚠⚠ **本轮真踩到的一个坑：词表里的子串** ——
               ```
               第一版 `_ANGLE_WORDS` 含 `rad` / `radians` ⇒ **子串命中 `radius`**
               ⇒ 把 `bend_radius_mm`（×4）与 `use_default_radius`（×3）共 **7 处**误判
               ⇒ 扫出 9 处可疑，真违规只有 1 处
               ⇒ ★ 最终词表**刻意不含** `rad`：("angle", "degrees", "draft")
               ```
               ★ 与事实 74 **同族**，而且**更细**：**同一个"按名字"的坑会以不同粒度反复出现**
                 （整句 → 词 → **子串**）。
            350 ★ **接上角度那一半** ⇒ `check_specs(all_specs())` = **0 问题**；
               真实违规只有 **1 处**：`solidworks_mold_parting_surface.angle`
               （文档写明「0.0 = 用文档默认」）⇒ 与那 3 个长度例外**同一条理由** ⇒ **显式豁免 + 理由**。
            351 ★★ **两轮合起来才完整，并解释了一个错觉**：
               ```
               规则 2 的两半：`_LEN_SUFFIX`（_mm）← 轮 134 接上 · `_ANGLE_SUFFIX`（_deg）← 轮 135 接上
               ⇒ ★ 两半**并排写在同一个注释下面**（L77）—— 即「**写在文档里的规则，两半都没实现**」
               ⇒ ★ 这解释了一个容易发生的错觉：**规则的"文本"存在**会让人以为规则的"实现"存在。**
               ```
               ★ 而 135 这一半是**系统扫**出来的，不是"顺手"发现的 ⇒
                 **一次顺手发现的价值，在于它能不能变成可重复的方法。**
               ⚑ **未查证**：探针假阳性 50% ⇒ 只出清单不做门禁；词表**有界选的**（`rad` 故意不收）；
                 ⚠ **本轮只扫了「常量」形态的死守卫** —— 别的形态（**写好却从没被调用的函数**、
                 **注册了却没接进 dispatch 的表**）**未扫**；角度豁免是**人工判**的。
               已知事实 **76** 入库 · 回归 **1176 passed**。
               下轮候选：① 扫**别的形态**的死守卫（没被调用的函数 / 没接进 dispatch 的表）；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+347 ", before, re.M):
    print("  游标 347 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+351 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 351 行已存在 ✓")

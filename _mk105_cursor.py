import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           589 🎯 **Spec Kit `105`：扫「数组实参没包 VARIANT」那一族 ⇒ **零遗留** —— 而判据经**三次**修正才站住**（轮 185）——
               动机：轮 167（`AddRelation`）与轮 183（`CreateSpline`）是**同一形状** ——
               **官方签名里是 `Object` 的数组实参，传裸 list/tuple ⇒ 静默返回 None/False**。⇒ 别处有没有？
            590 ★★★ **本轮的真正内容是**判据的三次修正**（如实记）：
               ```
               第一版（按「实参是**裸数组字面量**」）
                 ⇒ 命中 **0** 处 ⇒ ⚠ **太窄**：轮 183 的真形态是**形参**
                    （`get_com_member(..., "CreateSpline", points)`）
               第二版（加「回溯**变量赋值**」+「实参是**形参**也算」）
                 ⇒ 命中 **30** 处 ⇒ ⚠ **太宽**：`FeatureByName(name)` 的 `name` 是**字符串**、
                    `GetComponents(top_level_only)` 是 **bool** ⇒ **「实参是形参」根本不能当判据**
               第三版（★ **锚在官方签名上**：只有反射说那个参数是 **`Object`** 才算候选）
                 ⇒ 命中 **0** 处 ⇒ ★ **并用负例验证它站得住**（见下）
               ```
            591 ★★★ **负例验证（事实 62：负例是唯一的证明）**：把轮 183 **修复前**的 `sketch_relations.py`
               （`git show 482b2f3^:scripts/sketch_relations.py`）喂给第三版判据：
               ```
               L240 get_com_member(sketch_manager, 'CreateSpline', points)        ⇒ 签名 ['Object']       ⇒ **命中** ✓
               L239 get_com_member(sketch_manager, 'CreateSpline2', points, True) ⇒ ['Object','Boolean'] ⇒ **命中** ✓
               ⇒ ★ 判据**能抓到那个真形态** ⇒ 所以当前仓库的 **0 处** 是**真的**（这类写法**已绝迹**）
               ```
               ⇒ ★★ 结论是 **「扫过且干净」**，**不是**「没扫到」—— 两者的差别**只由负例决定**。
            592 ★ **收敛出的定则**：**判据要锚在**权威源**上**（官方签名、语言规则、失败文本），
               **不要锚在「我看到的形状」上** —— 形状会**同时**给出漏报与误报。
               ★ 本会话的判据失准已到第 N 次：`113` 兜底 · `114` 散文猜 · `115` 长度倒序 · `116` 变量名 ·
                 `118` 桩错 · `120` 正则太窄 · `121` 读文本不读判据 · **`125` 太窄 → 太宽 → 锚签名**。
            593 ★ 工具：`tools/scan_bare_array_args.py`（**纯静态**：只读源码 + 反射；检查量为 0 时**非 0 退出**）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ 只覆盖 `get_com_member` 族 ⇒ **不覆盖**原生 `obj.Member(...)` 调用；
                 ⚠ 「包了 VARIANT 但**类型包错**」的**看不见**；⚠ 「零遗留」**只对本轮判据成立**；
                 ⚠ 本轮**无真机验证**（纯静态）。
               下轮候选：① 把判据扩到原生调用（`obj.Member(...)`）；② 查 `surface_modeling` / `mold_tools`
                 两条 `stitched` 的拆条目；③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+589 ", before, re.M):
    print("  游标 589 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+593 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 593 行已存在 ✓")

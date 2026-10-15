import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           425 🎯 **Spec Kit `070`：补 `composite_curve` —— ****阴性结果****，但修掉了冒烟里一个不会失败的检查**（轮 151）——
               入口 `IModelDoc2.InsertCompositeCurve() -> Boolean`（**零参**）· Remarks 要求
               **用 mark=1 选实体**（★ **第二次**出现这个坑，`InsertDome` 也是）·
               官方示例给了**定量往返**抓手：`CompositeCurveFeatureData.GetEntitiesToJoinCount()`。
               ★ 实现时**用了 `call_com_member`**（零参成员用 `get_com_member` 会**替调用方悄悄调一次**，
                 事实 84 —— 本轮正确用上了）。
            426 ★★★ **结果：阴性 —— 而且根因在前提，不在功能**：
               ```
               真机：InsertCompositeCurve() 返回 **False**
               诊断：★ 两次 `start_sketch`+`sketch_line`+`end_sketch` **只留下 1 个草图**
                     （特征树里数出来的）⇒ **选不出 2 个草图** ⇒ 返回 False 是**应然的**
               ⚠ **为什么只留下 1 个，本轮未查明**（疑与事实 9「画草图前先选基准面」有关，**未验证**）
               ⇒ ★ **因此本条能力没有升级**，也没把 `insert_composite_curve` 记为可用。
               ```
            427 ★★★ **本轮最值钱的产出：修掉一个「不会失败」的检查**：
               ```
               冒烟里原有一句： chk("造出 2 个草图", **True**, "草图1 / 草图2")   ← 硬编码 True
               ⇒ ★ 它**不可能失败** ⇒ 整个冒烟**建在一个从未被验证的前提上**
               ⇒ 而那个前提**实际不成立**，冒烟却**一路绿到第 4 条**才红
               ⇒ ★★ 改成「**真的数特征树里 SKETCH 型条目**」之后，那条**当场变红**
                  ⇒ 前提问题**这才暴露出来**
               ```
               ★ 这是本会话反复记录的那个反模式的**我自己犯的一次**：
                 **一个不会失败的检查，等于没有检查**（事实 62/79/81/88 同一族）。
            428 ★ **一条方法论**：写冒烟时，「**环境准备**」那一步也**必须是被验证的断言**，
               不能是 `True` —— 因为**前提错了后面全错**，而**错法看起来像「功能不行」**
               （★ 差点把"我自己没造出 2 个草图"读成"这功能不可用"）。
               ⇒ 与事实 53（连续 ≥3 次修补就停下）**方向一致但更早**：
                 **在"修补"之前，先把"前提"验掉。**
               ⚑ **未查证**：⚠ 为什么两次建草图只留下 1 个**未查明**；
                 ⚠ `InsertCompositeCurve` **能不能建成仍未查明**；⚠ `GetEntitiesToJoinCount()` 读回**不可达**
                 （同轮 143 那一族）；⚠ `insert_composite_curve` **已写但未取证** ⇒ 能力**未升级**。
               已知事实 **91** 入库 · 回归 **1230 passed** · `release_check` exit 0。
               下轮候选：① **查清"两次建草图只留下 1 个"的根因**（这决定 composite_curve 能不能取证）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+425 ", before, re.M):
    print("  游标 425 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+428 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 428 行已存在 ✓")

import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\070-composite-curve-negative-result")
S.mkdir(parents=True, exist_ok=True)

spec = """# 070 · 补 `composite_curve` —— **阴性结果**，但修掉了冒烟里一个不会失败的检查

**Status**: Implemented（轮 151）· ⚠ **能力未升级**（未取证）

## 一、官方入口
```
IModelDoc2.InsertCompositeCurve() -> Boolean     ← **零参**，返回 True 才是成功
Remarks: 要先用 SelectByID2 以 **mark number of 1** 选实体
官方示例: SelectByID2("Sketch2","SKETCH",…,false,1,null,0) · SelectByID2("Sketch1",…,true,1,…)
          ⇒ 建完后 ((CompositeCurveFeatureData)feat.GetDefinition()).GetEntitiesToJoinCount()
          ⇒ ★★ 这是**定量往返**的抓手（我选 2 个 ⇒ 读回应当 2）
```

## 二、★★★ 结果：**阴性** —— 而且根因在前提，不在功能
```
真机：InsertCompositeCurve() 返回 **False**
根因：★ 两次 `start_sketch` + `sketch_line` + `end_sketch` **只留下 1 个草图**（特征树里数出来的）
      ⇒ **选不出 2 个草图**给它合成 ⇒ 返回 False 是**应然的**
⚠ **为什么只留下 1 个，本轮未查明**（疑与事实 9「画草图前先选基准面」有关，**但没验证**）
⇒ ★ **因此本条能力没有升级**，也没有把 `insert_composite_curve` 记为可用。
```

## 三、★★★ 本轮最值钱的产出：**修掉一个「不会失败」的检查**
```
冒烟里原有一句：  chk("造出 2 个草图（各含一条线）", True, "草图1 / 草图2")
                                                    ^^^^ **硬编码 True**
⇒ ★ 它**不可能失败** ⇒ 于是整个冒烟**建在一个从未被验证的前提上**
⇒ 而那个前提**实际不成立**（只有 1 个草图），冒烟却**一路绿到第 4 条**才红
⇒ ★★ 改成「**真的数特征树里 SKETCH 型条目**」之后，那条**当场变红**
   ⇒ 前提问题**这才暴露出来**
```
★ 这是本会话反复记录的那个反模式的**我自己犯的一次**：
**一个不会失败的检查，等于没有检查**（事实 62/79/81/88 同一族）。

## 四、判据
| ID | 判据 |
|---|---|
| SC-6601 | ★ 官方三源（反射 / swapi Remarks / 官方示例）|
| SC-6602 | ★★ 走官方要求的 **mark=1** 选实体（与 `insert_dome` 同一个坑）|
| SC-6603 | ★ **用 `call_com_member`**（零参成员 —— 用 `get_com_member` 会替调用方悄悄调一次）|
| SC-6604 | ★★★ **查出根因在前提**（只有 1 个草图），并**如实报阴性** |
| SC-6605 | ★★★ **修掉硬编码 `True` 的检查**，改成真的数 |
| SC-6606 | ★ **不升级能力**（未取证就不谎称可用）|
| SC-6607 | 已知事实 91 入库；门禁 + 回归不退化（回归 **1230 passed**）|

## 五、★ 一条方法论（本轮的正面收获）
```
写冒烟时，「**环境准备**」那一步也**必须是被验证的断言**，不能是 `True` ——
因为**前提错了后面全错**，而**错法看起来像「功能不行」**。
⇒ ★ 这正是我这一轮的实况：差点把「我自己没造出 2 个草图」读成「这功能不可用」。
```
⚠ 而我没有 —— 因为那条检查被改成真的数之后**当场红了**。

## ⚠ 明确记下的限度
* ⚠ **为什么两次建草图只留下 1 个，未查明**（疑与事实 9 有关，未验证）；
* ⚠ **`InsertCompositeCurve` 在这条后端上能不能建成，仍未查明**（前提没做对）；
* ⚠ `GetEntitiesToJoinCount()` 读回**不可达**（同轮 143 的 `IDomeFeatureData2` 那一族）；
* ⚠ 因此 `scripts/sw_part.insert_composite_curve` **已写但未取证** ⇒ 能力**未升级**。
"""

plan = """# 070 · Plan

## 步骤
1. 挑 `composite_curve`：官方 `InsertCompositeCurve()` **零参 + Boolean** ⇒ 看着很干净
2. 读 Remarks + 官方示例 ⇒ **mark=1 选实体** + 建完读 `GetEntitiesToJoinCount()`（**定量往返**抓手）
3. 实现（★ 用 `call_com_member`，因为零参成员用 `get_com_member` 会**替调用方悄悄调一次**）
4. 冒烟 ⇒ **返回 False** ⇒ ⚠ **不猜**，先做一次诊断
5. ★★ 诊断查出：**特征树里只有 1 个草图** ⇒ 前提不成立
6. ★★★ 顺带发现冒烟里那句 `chk(..., True, ...)` **硬编码了 True** ⇒ **不可能失败**
   ⇒ 改成真的数 ⇒ **当场变红** ⇒ 前提问题这才暴露
7. 如实收成**阴性结果**（**不升级能力**）+ 事实 91 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把「前提没做对」读成「功能不可用」 | ★ **先诊断再说**（本轮正是这么分辨的）|
| 冒烟里的准备步骤硬编码 True | ★ **改成真的断言**（本轮的核心修法）|
| 未取证就升级能力 | ★ **不升级**，并在 limitations 里写明 |
| 顺手猜"是不是没选基准面" | ★ **不写进结论**（限度里标"未验证"）|
"""

tasks = """# 070 · Tasks（全部完成，轮 151）

- [x] T-6601 三源查 `InsertCompositeCurve` + 官方示例
- [x] T-6602 实现 `insert_composite_curve`（用 `call_com_member`）
- [x] T-6603 ★★ 诊断：特征树里只有 **1** 个草图 ⇒ **前提不成立**
- [x] T-6604 ★★★ 修掉硬编码 `True` 的检查（改成真的数）
  `→ 验收:` `python tools/verify_composite_curve_smoke.py`（那条**当场变红**，前提问题暴露）
- [x] T-6605 如实收成阴性结果（**不升级能力**）+ 已知事实 91
- [x] T-6606 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 070 · Converge

**Converged**: 2026-10-01（轮 151）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-6601 三源 | ✅ |
| SC-6602 mark=1 选实体 | ✅ |
| SC-6603 用 `call_com_member` | ✅ |
| SC-6604 查出根因在前提 | ✅ 只有 1 个草图 |
| SC-6605 修掉硬编码 True | ✅ 那条当场变红 |
| SC-6606 不升级能力 | ✅ |
| SC-6607 事实 91 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1230 passed** |

## 二、★★★ 本轮是一次**阴性结果**，而它的价值在**过程里**
```
目标：补 composite_curve（一个"真缺"条目）
结果：**没能取证** —— 但**原因不是功能不行，是我自己没造好前提**
⇒ ★★ 而"前提没造好"这件事，是**修掉一句硬编码 True 之后才暴露的**
⇒ 若没修那一句：冒烟会**一路绿到第 4 条**，我会以为"选实体那一步有问题"，
   然后**去猜参数、去换选法** —— 而真因在**更前面**。
```
★ 这与事实 53（启发式连续 ≥3 次修补就停下）**方向一致但更早**：
**在"修补"之前，先把"前提"验掉。**

## 三、★ 三条可复用的
```
① 写冒烟时，**环境准备那一步也必须是被验证的断言**（不能是 True）
② 官方 Remarks 里的「mark=1」是**第二次**出现（轮 143 的 InsertDome 也是）⇒ 记进模式
③ 零参 COM 成员**必须用 `call_com_member`** —— 用 `get_com_member` 会**替调用方悄悄调一次**
   （事实 84；本轮正确用上了）
```

## 四、未查证
* ⚠ **为什么两次建草图只留下 1 个，未查明**；
* ⚠ **`InsertCompositeCurve` 能不能建成，仍未查明**；
* ⚠ `GetEntitiesToJoinCount()` 读回**不可达**（同轮 143 那一族）；
* ⚠ `insert_composite_curve` **已写但未取证** ⇒ 能力**未升级**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

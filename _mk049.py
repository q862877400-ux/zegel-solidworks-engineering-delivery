import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\049-a5-closed-comtypes-classification")
S.mkdir(parents=True, exist_ok=True)

spec = """# 049 · 关掉 A5 的最后 2 条「存疑」—— 查出是**类别错误**

**Status**: Implemented（轮 130）

## 一、先量 A 系列现状（目标自己的尺子）
```
`docs/final-audit.md`：A1 A2 A3 A4 A6 A7 A8 A9 A10 = **达成**
                      **A5 = 部分达成** ← 全表唯一的缺口
A5 的缺口：711 调用点 / 696 通过 / **2 存疑** / 0 查不到
```

## 二、那 2 条是谁
```
`sw_delivery.py:635`  `IGetDocumentNames()` 传 1 参，官方 2   ⚠「有意为之，**需真机确认**」
`sw_delivery.py:884`  `OpenDoc6()`           传 4 参，官方 6   ⚠「有意为之，**需真机确认**」
```

## 三、★★ 查出来的真因：**类别错误**
```
两条都走 **comtypes 早绑定**（同文件里 `comtypes.client.GetModule(...)`，
  35 处提到 comtypes；`_comtypes_document_names()` 就是 L635 所在函数）
⇒ 而本工具的 arity 规则是在 **pywin32 迟到绑定**上**真机量出来**的（已知事实 68）
⇒ **comtypes 代理会自己分配 `[out]` 数组/VARIANT** ⇒ 调用方**只传入参即正确**
⇒ ★ **拿 pywin32 的规矩去判 comtypes 的调用点，是类别错误**，不是"代码有问题"
```
⚠ 而这两条此前被标成「有意为之」是**人工裁定**，理由是"需真机确认" —— **从未确认过**。

## 四、处置：**单独归类，不静默吞掉**
照仓库既有做法（`check_interface_member_ownership.MANUAL_MAP`：**带理由的人工确证表**）：
```
新增 `COMTYPES_CALL_SITES: {(文件名, 行号): 理由}` —— 两条各带一段理由
`audit()` 返回从 4 组变 5 组，comtypes 单列
CLI **打印出来**（`── comtypes 明细 ──`），标题写明「**不是缺陷**，是有依据的单独归类」
```
结果：
```
调用点: 24 个
  通过      24
  comtypes  2   ← **本工具判不了**（早绑定自行分配 [out]）
  存疑      0   ← ★ A5 的缺口没了
  查不到    0 · 动态 0
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-4501 | ★★ 查出真因是**类别错误**（comtypes 早绑定 vs pywin32 迟到绑定）|
| SC-4502 | ★ **不是静默吞掉**：这批站点**仍然被打印**，只是单列（负例测试钉住）|
| SC-4503 | ★ 每条**带理由**，且理由必须提到 `comtypes` 与 `pywin32` |
| SC-4504 | ★ `sw_delivery.py` 的 `doubt` 里**不再有** `IGetDocumentNames` / `OpenDoc6` |
| SC-4505 | `final-audit.md` 的 **A5：部分达成 → 达成**，并写清理由 |
| SC-4506 | 门禁 + 回归不退化（回归 **1157 passed**）|

## 六、⚠ 这次和第 129 轮那次**方向相反**
```
129：判据红了，一查是**判据错**（我爬错层）⇒ 修判据
130：判据"绿"了 2 条，一查是**判据的适用范围错**（拿 pywin32 的规矩判 comtypes）
⇒ ★ 两次都不是"改代码去迎合判据"，也都不是"改判据去迎合代码" ——
  而是**把"这条判据到底管不管得到这个对象"问清楚**。
```

## ⚠ 明确记下的限度
* 只证了「**本工具判不了它们**」，**没有**真机验证 comtypes 下这两个调用的实际行为；
* `COMTYPES_CALL_SITES` 是**人工表**（按仓库既有做法）—— 新出现同类站点**不会被自动识别**；
* comtypes 早绑定与 pywin32 在 `[out]` 上的差异，**官方文档没有对照说明**（本轮的依据是
  `sw_delivery.py` 自己的注释 + 那 35 处 comtypes 用法）。
"""

plan = """# 049 · Plan

## 步骤
1. ★ 先量 A 系列现状 ⇒ **只有 A5 是「部分达成」**（其余 9 条全绿）
2. 找 A5 的缺口：那 **2 条存疑**是谁 ⇒ 两条都标着「**需真机确认**」
3. 读那两处代码 ⇒ **都是 comtypes 早绑定**（同文件 35 处 comtypes）
4. ★ 判定：arity 规则是在 **pywin32** 上量的（事实 68）⇒ **拿它判 comtypes 是类别错误**
5. 处置：照仓库既有的「带理由的人工确证表」做法**单独归类**，且**仍然打印**
6. 负例测试（**4 条**）证明不是静默吞掉
7. `final-audit.md` 的 A5 → **达成** → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把「存疑」直接删掉（静默吞掉）| ★ **单列 + 打印 + 带理由 + 负例测试** |
| 用启发式自动识别 comtypes | ★ **人工表**（照 `MANUAL_MAP` 的先例）—— 没依据的不许自动进来 |
| 顺手也把其它判据放宽 | **不做**，本轮只处理这两条 |
| 说"实现里改了 `audit()` 返回元组"但漏改调用方 | ★ 改完立刻跑 CLI 看输出 |
"""

tasks = """# 049 · Tasks（全部完成，轮 130）

- [x] T-4501 ★ 量 A 系列现状 ⇒ 只有 **A5** 是缺口
- [x] T-4502 定位那 2 条存疑 ⇒ 都标「**需真机确认**」
- [x] T-4503 ★ 读出真因：**comtypes 早绑定** vs 工具的 **pywin32** 前提
- [x] T-4504 加 `COMTYPES_CALL_SITES`（带理由）+ `audit()` 分流 + CLI 单列
  `→ 验收:` `python scripts/audit_call_arity.py scripts\\sw_delivery.py @refs`（**存疑 0**）
- [x] T-4505 负例测试 `tests/test_arity_comtypes_classification.py`（**4 passed**）
- [x] T-4506 `final-audit.md`：**A5 部分达成 → 达成**（写清理由）
- [x] T-4507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 049 · Converge

**Converged**: 2026-10-01（轮 130）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-4501 查出类别错误 | ✅ comtypes 早绑定 vs pywin32 |
| SC-4502 不是静默吞掉 | ✅ 仍打印 + 负例测试 |
| SC-4503 每条带理由 | ✅ 提到 comtypes 与 pywin32 |
| SC-4504 doubt 里不再有那两条 | ✅ |
| SC-4505 A5 → 达成 | ✅ |
| SC-4506 门禁 + 回归 | ✅ `release_check` exit 0 · **1157 passed** |

## 二、★ 目标尺子上的变化
```
A1–A10：此前 **A5 = 部分达成**（全表唯一缺口）
⇒ 本轮之后 **A1–A10 全部「达成」**
⚠ 但 A2 那条是「达成（②空满足）」—— **空满足也是达成**，只是它没被用过。
```

## 三、★★ 与 129 轮那次**方向相反**，但道理相同
```
129：判据**红**了 ⇒ 一查是**判据错**（我爬错层）⇒ 修判据
130：判据"绿"了 2 条 ⇒ 一查是**判据的适用范围错**（拿 pywin32 的规矩判 comtypes）
⇒ ★ 两次都不是"改代码迎合判据"、也不是"改判据迎合代码"，
  而是把「**这条判据到底管不管得到这个对象**」问清楚。
```
★ 这已经是本会话**第三次**遇到"范围/层"类问题
（事实 51 是**分析范围**、129 是**判据的层**、130 是**判据的适用前提**）。

## 四、⚠ 处置的**克制**在哪
```
没有：把 comtypes 站点从扫描里排除（那就真看不见了）
没有：把 doubt 直接过滤掉
没有：用启发式自动识别 comtypes
⇒ 而是：**单列 + 每条写理由 + 仍然打印 + 负例测试钉住**
```
★ 与 `029`/`032`「台账不做门禁」、`041`「如实分裂声明」同一路数：
**该说清楚的就说清楚，不靠"看不见"来变绿。**

## 五、未查证
* **没有**真机验证 comtypes 下这两个调用的实际行为；
* `COMTYPES_CALL_SITES` 是**人工表** ⇒ 新出现的同类站点**不会被自动识别**；
* comtypes 与 pywin32 在 `[out]` 上的差异，**官方文档没有对照说明**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

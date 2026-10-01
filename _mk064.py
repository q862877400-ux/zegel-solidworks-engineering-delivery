import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\064-call-com-member-migration")
S.mkdir(parents=True, exist_ok=True)

spec = """# 064 · 把「故意要调」的调用**改名表态** —— 一路踩出 3 个真缺陷

**Status**: Implemented（轮 145）

## 一、起因
`063`（轮 144）判明 `get_com_member` 的语义是「**取或调**」，并留了限度：
「⚠ 24 处里只读了 8 处」。
⇒ 本轮**把 24 处读完**，然后**让代码自述**。

## 二、★ 24/24 读完 —— **全部是故意调用**
| 类别 | 处数 | 例 |
|---|---|---|
| 拿**返回值**当成败 | 8 | `EditRebuild3` ×5 · `RunAnalysis` ×2 · `UpdateCutList` |
| 要的是**值** | 2 | `Scale` ×2 |
| **创建并拿对象** | 5 | `InsertGtol` · `InsertMoldShutOffSurface` · `CreateMassProperty2` · … |
| **纯执行**（返回值不用） | 9 | `Activate` · `StartDynamics` · `MeshAndRun` · … |

⇒ 既然**全是故意的**，问题就只剩一个：**代码里读不出来它在调。**
⇒ 加 **`call_com_member`**（与 `get_com_member` **行为完全相同**，差别在**名字**），
把这 24 处迁过去 —— **名字即意图**。

## 三、★★★ 迁移一路踩出 **3 个真缺陷**
```
① `scripts/sw_assembly.py`：用了 **12 处** `get_com_member` 却**只导入了 `safe_get_com_member`**
   ⇒ 那 12 处**会 NameError**（测试从没走到 ⇒ 一直没暴露）
   ★ 是我新写的"调用与导入一致性"判据**当场抓到**的。
② `scripts/check_member_names.py` 的 WRAPPER：**只认 `get_com_member`**
   ⇒ 一直**漏掉 `safe_get_com_member`**；我改名后那 24 处也不再被计数。
③ `scripts/audit_call_arity.py` 的 `WRAPPERS`：
   `{"_safe_member", "get_com_member", "get_com_member"}` ——★ **第三项重复**，
   显然 `safe_get_com_member` 写错了 ⇒ **它的调用点一直被漏计**。
```
⇒ ②③ **同一个根因**：「**有几个取成员的同义词**」这件事**没有单一真源**。

## 四、⚠ 我自己在这一轮犯的错（都记下来）
```
① 迁移 24 处**只改了调用、漏了导入**（11 个模块）——
   而「模块能 import 成功」**掩盖**了它（NameError 只在调用时炸）
   ⇒ 这才有了那条新判据（`hasattr` 而不是"能导入"）。
② 补测试桩时用正则批量改 ⇒ **弄坏了一个多行 lambda 的文件**（已 git 恢复，改用外科式改）
③ 测试桩有三类形态都要跟上：`connect.X = f` · `SimpleNamespace(...)` ·
   **记录式桩 `m.X = lambda ...`**（第三类漏了 ⇒ 两个契约测试红）
④ 多行 `from .sw_connect import (...)` 的 **except 回退那一份**漏了 ⇒ 又红一次
```
★ 一条**可复用的教训**：
**给一个被广泛导入的名字做"重命名式迁移"，等于同时改了所有导入点与所有桩** ——
**必须把"调用"与"导入"当成一件事来验**。

## 五、判据
| ID | 判据 |
|---|---|
| SC-6001 | ★★ 24/24 读完，**全部**是故意调用 |
| SC-6002 | ★ 加 `call_com_member`（名字即意图）并迁移 24 处 |
| SC-6003 | ★★★ **查出 `sw_assembly.py` 12 处会 NameError**（真缺陷）|
| SC-6004 | ★★ **查出两个漏计**（`check_member_names` 只认一个名字 · `WRAPPERS` 有重复项）|
| SC-6005 | ★★ 新判据用 **`hasattr`**（"能导入"不算 —— 那正是掩盖了缺陷的假绿）|
| SC-6006 | ★ 撤掉一条**做不成的**判据（"零参方法不许用 `get_com_member`"）并留档 |
| SC-6007 | ★ 记下我自己 4 处错；门禁 + 回归不退化（回归 **1210 passed**）|

## 六、★ 撤掉的那条判据（如实留档）
```
我想钉住「反射里有零参重载的方法，不许再用 get_com_member」⇒ **两版都失败**：
  第一版按**名字前缀**（Insert*/Run*/Select*/Load*…）⇒ 5 个假阳性
    （SelectionManager / LoadsAndRestraintsManager **是属性**）
  第二版按**反射零参重载**（更严）⇒ 把**所有只读 getter** 也报了（GetTitle / GetName…）
⇒ ★★ 根因：区分「getter」与「改东西的」**需要语义**，结构判不出来（事实 74 那一族的**第 6 次**）
⇒ 结论：那 24 处迁移是一次**逐条读过之后的判断**，**不是**可机械校验的规则 ⇒ 不设判据。
```

## ⚠ 明确记下的限度
* ⚠ 迁移是**判断**（24 处逐条读过），**没有**机器判据兜底；
* ⚠ 我**不做**"全仓库所有 `get_com_member` 都改名"—— 只有那 24 处是"名字像改东西"的；
* ⚠ `call_com_member` 与 `get_com_member` **行为完全相同** ⇒ 它是**命名**，不是新语义；
* ⚠ 那 12 处 `sw_assembly` 的 `NameError` **只在调用时**会出现 ⇒ 修了导入，
  但**没有**去跑那个函数的真机路径（未实测）。
"""

plan = """# 064 · Plan

## 步骤
1. `063` 留的尾巴：把 24 处读完
2. ⇒ **24/24 全是故意调用** ⇒ 问题变成「**代码读不出来它在调**」
3. 加 `call_com_member`（行为同 `get_com_member`，名字表态）并迁移 24 处
4. ⚠ 迁移漏了 11 个模块的 **import** ⇒ 而"能导入"掩盖了它 ⇒ 补 import
5. ★ 新判据（`hasattr` 而非"能导入"）⇒ **它当场抓出 `sw_assembly.py` 的 12 处 NameError**
6. ⚠ 一路又踩：测试桩三类形态 · 多行 except 回退 · 正则弄坏一个文件（已恢复）
7. ★★ 顺带查出**两个漏计**（`check_member_names` 只认一个名字 · `WRAPPERS` 重复项）
8. ⚠ 撤掉一条做不成的判据（名字前缀/零参重载都失败）+ 留档
9. 门禁（含报告数字）+ 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 改名漏导入 | ★ 判据用 **`hasattr`**（"能导入"是假绿）|
| 批量正则弄坏文件 | ★ 只处理**安全形态**；坏了就 `git checkout` 单个文件重来 |
| 只改生产代码不管测试桩 | ★ 三类桩都要跟上（`=` / `SimpleNamespace` / **记录式 lambda**）|
| 想给迁移加机器判据 | ★ **撤掉**（试了两版都不成立），如实留档 |
"""

tasks = """# 064 · Tasks（全部完成，轮 145）

- [x] T-6001 ★★ 24/24 读完 ⇒ 全部是故意调用
- [x] T-6002 加 `call_com_member` + 迁移 24 处
- [x] T-6003 ★★ 补 11 个模块的导入 + 三类测试桩
- [x] T-6004 ★★★ 新判据（`hasattr`）抓出 `sw_assembly.py` 12 处 NameError
  `→ 验收:` `python -m pytest tests/test_com_member_helpers.py -q`（**3 passed**）
- [x] T-6005 ★★ 修两个漏计（`check_member_names` WRAPPER · `audit_call_arity` WRAPPERS）
- [x] T-6006 ⚠ 撤掉做不成的判据 + 留档
- [x] T-6007 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 064 · Converge

**Converged**: 2026-10-01（轮 145）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-6001 24/24 读完 | ✅ 全是故意 |
| SC-6002 `call_com_member` + 迁移 | ✅ |
| SC-6003 查出 NameError 缺陷 | ✅ 12 处 |
| SC-6004 查出两个漏计 | ✅ |
| SC-6005 判据用 `hasattr` | ✅ |
| SC-6006 撤掉做不成的判据 | ✅ 已留档 |
| SC-6007 门禁 + 回归 | ✅ `release_check` exit 0 · **1210 passed** |

## 二、★★★ 本轮的价值几乎全在**副产物**上（第三次了）
```
目标：把 24 处调用"改名表态"（一个**纯命名**的改动）
⇒ 结果：踩出 **3 个真缺陷** ——
   ① `sw_assembly.py` 12 处**会 NameError**（只导入了 safe_ 那个）
   ② `check_member_names.py` 一直**漏掉 `safe_get_com_member`**
   ③ `audit_call_arity.py` 的 `WRAPPERS` **有个重复项**（本该是 `safe_get_com_member`）
⇒ ★ 而 ②③ 的根因是同一个：**"取成员的同义词有几个"没有单一真源**。
```
★ 与 `051`（补 `ellipse` ⇒ 量出整模块单位写错）· `062`（补 `dome` ⇒ 查出 `get_com_member` 缺陷）
**同一个形状**：**为了改一处而去看，看到的往往不止那一处。**

## 三、★★ 「能导入」是**假绿** —— 本轮的核心陷阱
```
迁移只改了**调用**、漏了 **import** ⇒ 11 个模块
⇒ 而 `import scripts.sw_view` **成功**（NameError 只在**调用时**才炸）
⇒ ★★ 我第一版判据写的是"用到就用得上吗"⇒ 用 `import` 判 ⇒ **全绿，什么也没抓到**
   ⇒ 改成 `hasattr` 之后，**当场**抓到 `sw_assembly.py` 那 12 处
```
★ 与事实 57/62/79/81 **同一族**（**绿有很多种假象**），而这次的具体形态是：
**"能导入" ≠ "名字在"**。

## 四、★★★ 一条可复用的教训：**重命名式迁移 = 调用 + 所有导入点 + 所有桩**
```
给一个**被广泛导入**的名字做重命名 ⇒ 你同时改了：
  ① 所有**调用点**；② 所有**导入行**（单行/多行/try-except 两份）；
  ③ 所有**测试桩**（三种形态：`X.f = g` / `SimpleNamespace(...)` / **记录式 lambda**）
⇒ 本轮 ④ 类里我漏了 ②（except 回退那份）与 ③（记录式 lambda），各红一次。
⇒ ★ **必须把"调用"与"导入"当成一件事来验**（本轮的判据就是这么来的）。
```

## 五、未查证
* 迁移是**判断**（24 处逐条读过），**没有**机器判据兜底；
* 那 12 处 `sw_assembly` 的 `NameError` ⇒ 修了导入，但**没跑**那个函数的真机路径；
* ⚠ **没有**把全仓库所有 `get_com_member` 都改名（只有那 24 处是"名字像改东西"的）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

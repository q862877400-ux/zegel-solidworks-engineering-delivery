import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           397 🎯 **Spec Kit `064`：把「故意要调」的调用****改名表态**** —— 一路踩出 3 个真缺陷**（轮 145）——
               `063` 留的尾巴：把 24 处读完 ⇒ ★ **24/24 全是故意调用**
               （拿返回值当成败 8 · 要的是值 2 · 创建并拿对象 5 · 纯执行 9）
               ⇒ 问题只剩一个：**代码里读不出来它在调**。
               ⇒ 加 **`call_com_member`**（与 `get_com_member` **行为完全相同**，差别在**名字**）
                 并迁移那 24 处 —— **名字即意图**。
            398 ★★★ **这次纯命名的改动踩出 3 个真缺陷**：
               ```
               ① scripts/sw_assembly.py：用了 **12 处** get_com_member 却**只导入了 safe_get_com_member**
                  ⇒ 那 12 处**会 NameError**（测试从没走到 ⇒ 一直没暴露）
                  ★ 是我新写的"调用与导入一致性"判据**当场抓到**的。
               ② scripts/check_member_names.py 的 WRAPPER **只认 get_com_member**
                  ⇒ 一直**漏掉 safe_get_com_member**；改名后那 24 处也不再被计数。
               ③ scripts/audit_call_arity.py 的 WRAPPERS =
                  {"_safe_member", "get_com_member", "get_com_member"} ——★ **第三项重复**，
                  显然 safe_get_com_member 写错了 ⇒ **它的调用点一直被漏计**。
               ⇒ ②③ 同根因：**"取成员的同义词有几个"没有单一真源。**
               ```
               ★ 与 `051`（补 ellipse ⇒ 量出整模块单位写错）· `062`（补 dome ⇒ 查出
                 `get_com_member` 缺陷）**同一个形状**：**为了改一处而去看，看到的往往不止那一处。**
            399 ★★ **「能导入」是假绿 —— 本轮的核心陷阱**：
               ```
               迁移只改了**调用**、漏了 **import** ⇒ 11 个模块
               ⇒ 而 `import scripts.sw_view` **成功**（NameError 只在**调用时**才炸）
               ⇒ ★ 第一版判据用 `import` 判 ⇒ **全绿，什么也没抓到**
               ⇒ 改成 **`hasattr`** 之后，**当场**抓到 sw_assembly 那 12 处
               ```
               ★ 与事实 57/62/79/81 **同一族**（绿有很多种假象）；本次的具体形态是
                 **"能导入" ≠ "名字在"**。
            400 ★★★ **一条可复用的教训**：**重命名式迁移 = 调用 + 所有导入点 + 所有桩**
               ```
               给一个**被广泛导入**的名字做重命名 ⇒ 同时改了：
                 ① 所有**调用点**；② 所有**导入行**（单行 / 多行 / try-except 两份）；
                 ③ 所有**测试桩**（三种形态：`X.f = g` / `SimpleNamespace(...)` / **记录式 lambda**）
               ⇒ 本轮我在 ② 的 except 回退那份、③ 的记录式 lambda 上**各红一次**。
               ⇒ ★ **必须把"调用"与"导入"当成一件事来验。**
               ```
            401 ⚠ **我自己的 4 处错**（都记下）：① 迁移漏导入（11 模块）· ② 正则批量改弄坏
               一个多行 lambda 的文件（已 git 恢复单个文件）· ③ 测试桩三类形态漏了第三类 ·
               ④ 多行 except 回退那份漏了。
               ★ 另**撤掉**一条做不成的判据（"零参方法不许用 get_com_member"）：
                 **两版都失败**（名字前缀 ⇒ 5 个假阳性；反射零参重载 ⇒ 把只读 getter 全报了）
                 ⇒ ★ 根因：区分「getter」与「改东西的」**需要语义**（事实 74 那一族的**第 6 次**）
                 ⇒ 那 24 处迁移是**逐条读过之后的判断**，**不是**可机械校验的规则 ⇒ **不设判据**。
               ⚑ **未查证**：sw_assembly 那 12 处**修了导入但没跑真机路径**；
                 迁移**没有**机器判据兜底；**没有**把全仓库所有 `get_com_member` 都改名。
               回归 **1210 passed** · `release_check` exit 0。
               下轮候选：① 回到「真缺」继续补；② 给剩下 3 条 `stitched` 冒烟；
               ③ 跑一次 sw_assembly 的相关真机路径（把"修了导入"变成"实测过"）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+397 ", before, re.M):
    print("  游标 397 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+401 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 401 行已存在 ✓")

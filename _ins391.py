import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           391 🎯 **Spec Kit `063`：审「取即调」的影响面 —— 结论是****改判****：那不是缺陷**（轮 144）——
               `062`（轮 143）把它写成「**危险设计**」⇒ 本轮**把影响面量清楚**再判。
            392 ★ **判法（结构）**：无实参 `get_com_member(obj,"Name")` 调用点 × 出厂反射
               （`Name` 是方法吗？**有几个参数**？）⇒ 有**零参重载**者，探测调用**会成功执行**。
               结果：**无实参调用点 471** ⇒ **193 处**有零参重载（绝大多数是**只读 getter** ⇒ 无害 ✓）；
               按「名字像改东西」缩清单得 **24** 处（`Insert*`/`Run*`/`Mesh*`/`Scale`/`Update*`/`Activate`…）。
            393 ★★★ **逐条读过 8 处之后 —— 改判**：
               ```
               sw_simulation: int(get_com_member(study,"RunAnalysis") or 0)   ⇒ 要的就是"调"的返回码 ✓
               sw_topology:   code = get_com_member(study,"MeshAndRun")       ⇒ 同上 ✓
               sw_view:       get_com_member(view,"Activate")                 ⇒ 探测即执行，正是意图 ✓
               sw_gtol:       gtol = get_com_member(model,"InsertGtol")       ⇒ 执行 + 查返回 ✓
               sw_mold:       feat = get_com_member(fm,"InsertMoldShutOffSurface") ⇒ 同上 ✓
               ```
               ⇒ ★★ **它不是缺陷，是**被依赖的特性** —— 作者就是把它当「**取或调**」用的。**
            394 ★ **处置（不打断 193 处依赖）**：① 正式语义入 docstring（「取或调」+ 影响面 + 危险面）·
               ② ★ 新增 `get_com_member_raw`（**只取不调**）· ③ **没有**改成「永不调用」·
               ④ **就地更正事实 84 的定性**（轮 143 写的「危险设计」）· ⑤ 审计脚本入库 + 6 条判据。
            395 ★★ **一条新认识：「名字没写的事」不等于「错」**：
               ```
               get_com_member 做了一件名字没写的事 ⇒ 我第一反应是"这是缺陷"
               ⇒ ★ 但"缺陷"的判据是「**调用方拿到的不是它要的**」，不是「函数做得比名字多」
               ⇒ 本轮去读调用方 ⇒ 它们**要的就是那个副作用**
               ⇒ ★★ 若没有这一步，我可能会**改掉一个 193 处依赖的特性** —— 那才是真正的破坏。
               ```
               ★ 本会话**第三次**同类自我更正（事实 70 · 82 · 84）—— 三次都不是"算错了"，
                 而是**在证据不足时下了定性**；修法一致：**就地更正 + 保留原话 + 写明依据**。
            396 ⚑ **未查证**：⚠ **24 处里只读了 8 处**，其余 **16 处未核**；判法是**结构**的
               ⇒ **说不出"作者是不是故意的"**（那必须逐条读）；
               `get_com_member_raw` **还没有调用点**（给将来用）。
               已知事实 **85** 入库（事实 84 已就地更正定性）· 回归 **1207 passed**。
               下轮候选：① 把剩下 **16 处**读完；② 回到「真缺」继续补；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+391 ", before, re.M):
    print("  游标 391 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+396 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 396 行已存在 ✓")

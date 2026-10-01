import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_com_member_helpers.py")
t = P.read_text(encoding="utf-8")

i = t.index("def _reflection_zero_arg_methods() -> set:")
NEW = '''#: ⚠⚠ **被撤掉的一条判据（轮 145，如实留档）**
#
# 我原本想钉住「反射里有**零参重载**的方法，不许再用 `get_com_member`」
# （理由是那个调用**会真的执行**它）。**两版都失败**：
# ```
# 第一版用**名字前缀**（Insert* / Run* / Select* / Load* …）
#   ⇒ 立刻 5 个假阳性：`SelectionManager` / `LoadsAndRestraintsManager` **是属性**
# 第二版改用**反射零参重载**（结构，更严）
#   ⇒ 它把**所有只读 getter** 也报了（GetTitle / GetName / GetCostingManager …）
# ```
# ⇒ ★★ **根因**：区分「getter」与「改东西的」**需要语义**，而**结构判不出来**
#   （事实 74 那一族的**第 6 次**）。
# ⇒ ★ **结论**：那 24 处从 `get_com_member` 迁到 `call_com_member` 是一次
#   **逐条读过之后的判断**（轮 144/145 各读了 8 处 + 16 处），
#   **不是**一条可以机械校验的规则 ⇒ **不设这条判据**。
#   ⚠ 留下的只有两条**结构性**的（下面那两个测试）：**导入一致** 与 **帮助函数行为**。
'''
t = t[:i] + NEW
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已撤掉那条判据（并把两版失败如实留档）")

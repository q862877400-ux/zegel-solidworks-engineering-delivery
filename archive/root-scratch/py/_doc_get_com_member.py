import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")

OLD = '''def get_com_member(obj, attr_name, *args):
    """
    兼容 pywin32 中“同一成员在不同环境下可能是属性也可能是方法”的情况。

    参数:
        obj: COM 对象
        attr_name: 成员名称
        *args: 当成员可调用时传入的参数

    返回:
        成员值或调用结果
    """'''

NEW = '''def get_com_member(obj, attr_name, *args):
    """★ 「**取或调**」—— 这是本函数的**真实语义**，2026-10-01（轮 144）写明白。

    :param obj: COM 对象
    :param attr_name: 成员名称
    :param args: 有实参 ⇒ 一定**调用**；无实参 ⇒ **见下**
    :returns: 成员值，或**调用的结果**

    ⚠⚠ **无实参时的行为（重要）**：本函数会**先无参调一次**，
    成功了就返回**调用的结果**；失败了（不是"找不到成员"）才把**成员本身**返回。
    ⇒ ★★ **对 COM 成员，「取」可能等于「调」。**

    ★ **审计结论（轮 144，`tools/audit_get_com_member_semantics.py`）**：
    这个"双用"**不是缺陷，是被依赖的特性** —— 全仓库**471** 个无实参调用点里，
    很多**正是靠它去执行**的（例：`get_com_member(study, "RunAnalysis")` 拿返回码、
    `get_com_member(view, "Activate")` 就是要激活视图、
    `get_com_member(fm, "InsertMoldShutOffSurface")` 就是要建面）。
    ⇒ ⚠ 所以**没有**把它改成"永不调用"。

    ⚠ **但仍然危险**，危险在于**名字读不出来它在调**：
    ```
    471 个无实参调用点
      ├─ 193 处的成员在反射里**有零参重载** ⇒ 探测调用**会成功执行**
      │    ├─ 其中绝大多数是**只读 getter**（GetTitle / GetPoints / IsCylinder…）
      │    │   ⇒ 「取即调」正是想要的 ✓
      │    └─ 24 处名字**像「改东西」**（Insert* / Run* / Mesh* / Scale / Update*…）
      │        ⇒ ⚠ 这些是**要人工确认"作者是不是故意的"**的
      └─ 其余：成员的必填参数 ⇒ 探测调用失败 ⇒ **返回成员本身**（轮 143 的修复覆盖这里）
    ```
    ⇒ ★ **要"只取不调"时，用 `get_com_member_raw`**（本模块下一个函数）。
    """'''
if "取或调" not in t:
    assert OLD in t, "get_com_member docstring 锚点不符"
    t = t.replace(OLD, NEW, 1)
    print("  ok get_com_member 的 docstring 已写明「取或调」语义 + 审计结论")

#: 加一个「只取不调」的显式替代
ANCHOR = "def safe_get_com_member(obj, attr_name, *args):"
ADD = '''def get_com_member_raw(obj, attr_name):
    """★ 「**只取不调**」—— `get_com_member` 的安全替代（2026-10-01 轮 144 加）。

    :returns: **成员本身**（方法对象或属性值），**绝不调用它**。

    ⚠ **什么时候必须用它**：当你要的是**方法对象**（例如要传给别处、或要自己控制
    参数与时机），而**不是**它的返回值时 —— 用 `get_com_member` 会**先无参调一次**，
    那对**有副作用**的成员（`Insert*` / `Run*` / `Save*` / `Scale`…）是**真做了那件事**。
    ⚠ 反过来：**要执行**的时候，继续用 `get_com_member`（那是它的语义）。
    """
    return getattr(obj, attr_name)


'''
if "def get_com_member_raw(" not in t:
    assert ANCHOR in t, "safe_get_com_member 锚点不符"
    t = t.replace(ANCHOR, ADD + ANCHOR, 1)
    print("  ok 已加 get_com_member_raw（只取不调）")
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")

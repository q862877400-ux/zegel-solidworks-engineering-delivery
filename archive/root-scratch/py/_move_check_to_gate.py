import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── ① 把第三版判据搬进 scripts/check_member_names.py（门禁的自然归宿）──
GATE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_names.py")
g = GATE.read_text(encoding="utf-8")

BLOCK = '''

# ══════════════════════════════════════════════════════════════════════
# 「**直接属性访问**」这一类的成员名检查（2026-10-01 轮 160 新增）
#
# ⚠⚠⚠ **为什么要加**：本文件原来只认 `get_com_member` / `call_com_member` /
#   `safe_get_com_member` 三种**包装形态** ⇒ ★ **直接属性访问（`obj.Member(...)`）
#   是它的盲区** —— 而 `077`（`model.GetSldWorksObject()`）与 `159`
#   （`asm_model.InterferenceDetection` / `GetInterference`）**两个真缺陷都是这个形态**。
#
# ★ 判据的**三版演进**（每一版的教训都留在代码里）：
#   ① 「大驼峰 + 不在反射里」⇒ 实测**假阳性 ≈100%**（`argparse` / `winreg` / OCP 全进来）⇒ 弃用；
#   ② 「对象名从 `get_com_member(<OBJ>, …)` 推导」⇒ 12 处，但仍混着 docstring 举例、
#      COM 基础设施、**跨函数同名变量**（事实 51）；
#   ③ **本函数**：`ast` 只查代码 + **按函数定作用域** + COM 基础设施白名单 +
#      **「从 COM 对象属性派生」的传播**。
#      ⇒ ⚠ 少了最后那条「传播」会**漏检**最常见的形态
#        （`interference = asm_model.InterferenceDetectionManager` 之后 `interference.X(...)`）
#        —— ★ 这是**「能响测试」当场抓出来的**（收窄修掉了假阳性，却引入了一个漏检）。
#
# ★ **判据已被证明能响**：`tests/test_direct_member_probe_can_fire.py`（6 条：
#   2 条正例喂真缺陷形态 ⇒ 必须命中；4 条反例 ⇒ 不许误报）。
# ══════════════════════════════════════════════════════════════════════
COM_INFRA = {"QueryInterface", "AddRef", "Release", "GetTypeInfo", "GetIDsOfNames", "Invoke"}
_WRAP_NAMES = {"get_com_member", "call_com_member", "safe_get_com_member", "get_com_member_raw"}


def _base_name(node):
    """取 `a.b.c` 的根标识符 `a`（不是 `a` 就返回 `None`）。"""
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


def find_direct_member_access(path, known):
    """在一个文件里找「**已当 COM 对象用过的**变量上、调用了**反射里没有**的大驼峰成员」。

    :param path: 要扫的 `.py` 路径。
    :param known: 出厂反射里的全部成员名（**唯一真源**）。
    :returns: `[{"file", "line", "fn", "obj", "name"}]`
    """
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    out = []
    for fn in [n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        com_objs = set()
        for sub in ast.walk(fn):
            if (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                    and sub.func.id in _WRAP_NAMES and sub.args):
                o = _base_name(sub.args[0])
                if o:
                    com_objs.add(o)
        #: ★ **传播**：从 COM 对象属性派生的变量也算 COM 对象（三层足够）
        for _ in range(3):
            grew = False
            for sub in ast.walk(fn):
                if (isinstance(sub, ast.Assign) and len(sub.targets) == 1
                        and isinstance(sub.targets[0], ast.Name)
                        and isinstance(sub.value, (ast.Attribute, ast.Call))):
                    v = sub.value.func if isinstance(sub.value, ast.Call) else sub.value
                    if _base_name(v) in com_objs and sub.targets[0].id not in com_objs:
                        com_objs.add(sub.targets[0].id)
                        grew = True
            if not grew:
                break
        if not com_objs:
            continue
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                o = _base_name(sub.func.value)
                name = sub.func.attr
                if o in com_objs and name not in known and name not in COM_INFRA:
                    out.append({"file": Path(path).name,
                                "line": getattr(sub, "lineno", 0),
                                "fn": fn.name, "obj": o, "name": name})
    return out
'''
if "def find_direct_member_access(" not in g:
    g = g.replace("def main(", BLOCK.strip() + "\n\n\ndef main(", 1)
    if "def find_direct_member_access(" not in g:      #: 没有 main() 就追加到末尾
        g = g.rstrip() + "\n" + BLOCK
    GATE.write_text(g, encoding="utf-8")
    ast.parse(g)
    print("  ok 判据已进 scripts/check_member_names.py")

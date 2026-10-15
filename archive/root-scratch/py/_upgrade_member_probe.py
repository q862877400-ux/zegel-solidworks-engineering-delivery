import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_direct_member_access.py")
t = P.read_text(encoding="utf-8")

NEW_BODY = '''

#: ⚠⚠⚠ **第三版判据**（轮 160）—— 前两版的教训都吃进来了：
#:   ① 第一版「大驼峰 + 不在反射里」⇒ 假阳性 ≈100%（标准库/pywin32/OCP 全都进来）；
#:   ② 第二版「对象名从 `get_com_member(<OBJ>, …)` 推导」把假阳性降到 12 处，
#:      但仍有 3 类噪音：**docstring 里的举例**、**COM 基础设施**（`QueryInterface`）、
#:      **跨函数变量名重合**（OCP 的 `wire`/`surface` 与 COM 的 `wire`/`surface` 同名 —— 事实 51）。
#: ⇒ 第三版：**(a) 用 `ast` 只查代码** · **(b) COM 对象名按「所在函数」定作用域** ·
#:            **(c) 加 COM 基础设施白名单**。
COM_INFRA = {"QueryInterface", "AddRef", "Release", "GetTypeInfo", "GetIDsOfNames", "Invoke"}


def _scan_file(path: Path, known: set) -> list:
    """用 `ast` 扫一个文件：**同一函数内**被当 COM 对象用过的标识符，再查它们身上的大驼峰调用。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []

    def ident(node) -> str | None:
        while isinstance(node, ast.Attribute):
            node = node.value
        return node.id if isinstance(node, ast.Name) else None

    out: list = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        #: (b) **按函数**收 COM 对象名（事实 51：范围要贴合组织单元）
        com_objs: set = set()
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) \\
                    and sub.func.id in _WRAPPERS and sub.args:
                o = ident(sub.args[0])
                if o:
                    com_objs.add(o)
        if not com_objs:
            continue
        #: (a) 只看**代码**（`ast` 天然不含 docstring/注释）
        for sub in ast.walk(fn):
            if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                o = ident(sub.func.value)
                name = sub.func.attr
                if o in com_objs and name not in known and name not in COM_INFRA:
                    out.append({"file": path.name, "line": getattr(sub, "lineno", 0),
                                "fn": fn.name, "obj": o, "name": name})
    return out
'''

OLD_TAIL = '''    rows = []
    _files = sorted((ROOT / "scripts").glob("*.py"))
    #: 第 1 遍：收 `<OBJ>`（被当 COM 对象用过的标识符）
    for p in _files:
        _t = p.read_text(encoding="utf-8", errors="replace")
        for _l in _t.splitlines():
            for _wm in WRAP_CALL.finditer(_l):
                COM_OBJECTS.add(_wm.group(2))
    print("  ★ 被当作 COM 对象用过的标识符: **%d** 个 ⇒ %s"
          % (len(COM_OBJECTS), sorted(COM_OBJECTS)[:14]))
    for p in _files:
        ev["scanned_files"] += 1
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:      # noqa: BLE001
            continue
        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            for wm in WRAP_CALL.finditer(line):
                COM_OBJECTS.add(wm.group(2))
            for m in CALL.finditer(line):
                obj, name = m.group(1), m.group(2)
                if name in known:
                    continue
                if obj not in COM_OBJECTS:      #: ★★ 只看**已知 COM 对象**
                    continue
                rows.append({"file": p.name, "line": i, "obj": obj, "name": name,
                             "text": s[:100]})'''

NEW_TAIL = '''    rows = []
    for p in sorted((ROOT / "scripts").glob("*.py")):
        ev["scanned_files"] += 1
        rows.extend(_scan_file(p, known))'''

assert OLD_TAIL in t, "扫描锚点不符"
t = t.replace(OLD_TAIL, NEW_TAIL, 1)
t = t.replace('COM_INFRA_PLACEHOLDER', '')
#: 把新函数插在 main() 之前
t = t.replace("def main() -> int:", NEW_BODY.strip() + "\n\n\ndef main() -> int:", 1)
t = t.replace('"text": s[:100]', '"text": ""')   #: 已无 s
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 探针已升第三版（ast + 按函数定作用域 + COM 基础设施白名单）")

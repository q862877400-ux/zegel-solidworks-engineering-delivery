import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\probe_direct_member_access.py")
t = P.read_text(encoding="utf-8")

OLD = '''#: ⚠ 已知的**非 COM** 大驼峰调用（Python 标准库 / 本仓库自己的类）⇒ 白名单，
#: 免得把 `Path.cwd()` 之类算进来。**白名单要小而明确**。
NOT_COM = {
    "Path", "PurePath", "WindowsPath", "PosixPath", "datetime", "Decimal",
    "ImportError", "RuntimeError", "ValueError", "TypeError", "KeyError",
    "AttributeError", "AssertionError", "FileNotFoundError", "OSError",
    "Exception", "BaseException", "StopIteration", "NotImplementedError",
    "SelectedEntities", "ShouldNotHappen", "BaseFlangeSpec", "ExportFormat",
}'''

NEW = '''#: ⚠⚠⚠ **第一版判据（"大驼峰 + 不在反射里"）实测假阳性率 ≈ 100%** ——
#: 323 处里全是 **Python 标准库 / pywin32 / OCP / winreg / argparse** 的对象
#: （`argparse.ArgumentParser` ×29 · `winreg.OpenKey` ×8 · `win32api.SetCursorPos` ×8 · …）
#: ⇒ ★ 印证**事实 74 那一族**：**「名字形态」判不出"是不是 COM 成员"** ⇒ **不接那条判据**。
#:
#: ★★ 第二版判据**有依据**（不是猜）：把对象名**限定到「已经被当作 COM 对象用过」的那些** ——
#: 即 `get_com_member(<OBJ>, …)` / `call_com_member(<OBJ>, …)` /
#: `safe_get_com_member(<OBJ>, …)` 的**第一个实参标识符**。
#: ⇒ 那些 `<OBJ>` **确实是 COM 对象** ⇒ 在它们身上的大驼峰调用就**值得查**。
COM_OBJECTS: set = set()
_WRAPPERS = {"get_com_member", "call_com_member", "safe_get_com_member", "get_com_member_raw"}
WRAP_CALL = re.compile(r"\\b(%s)\\s*\\(\\s*([A-Za-z_]\\w*)\\s*," % "|".join(sorted(_WRAPPERS)))'''

assert OLD in t, "白名单锚点不符"
t = t.replace(OLD, NEW, 1)

#: 收集 COM 对象名；并把过滤条件从"大驼峰"改成"在已知 COM 对象上"
OLD2 = '''        for i, line in enumerate(text.splitlines(), 1):
            s = line.strip()
            if s.startswith("#"):
                continue
            for m in CALL.finditer(line):
                obj, name = m.group(1), m.group(2)
                if obj in NOT_COM or name in known:
                    continue
                rows.append({"file": p.name, "line": i, "obj": obj, "name": name,
                             "text": s[:100]})'''
NEW2 = '''        for i, line in enumerate(text.splitlines(), 1):
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
assert OLD2 in t, "过滤锚点不符"
t = t.replace(OLD2, NEW2, 1)
#: 两遍扫描：先收 COM 对象名，再判调用
t = t.replace('    rows = []\n    for p in sorted((ROOT / "scripts").glob("*.py")):',
              '    rows = []\n    _files = sorted((ROOT / "scripts").glob("*.py"))\n'
              '    #: 第 1 遍：收 `<OBJ>`（被当 COM 对象用过的标识符）\n'
              '    for p in _files:\n'
              '        _t = p.read_text(encoding="utf-8", errors="replace")\n'
              '        for _l in _t.splitlines():\n'
              '            for _wm in WRAP_CALL.finditer(_l):\n'
              '                COM_OBJECTS.add(_wm.group(2))\n'
              '    print("  ★ 被当作 COM 对象用过的标识符: **%d** 个 ⇒ %s"\n'
              '          % (len(COM_OBJECTS), sorted(COM_OBJECTS)[:14]))\n'
              '    for p in _files:', 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 判据已换成「只知道 COM 对象上的大驼峰调用」")

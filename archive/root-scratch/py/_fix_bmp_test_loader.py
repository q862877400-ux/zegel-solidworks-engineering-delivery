import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_export_bmp_contract.py")
t = P.read_text(encoding="utf-8")
i = t.index("def _load():")
j = t.index("class _Model:")
NEW = '''def _load():
    """取仓库里**真**的 `sw_export` 模块。

    ⚠ 第一版想"把 `sw_connect` 等全换成最小桩" ⇒ **追名字追不完**
    （`create_empty_dispatch_variant` / `import_com_dependencies` / `read_custom_property`…）。
    ⇒ ★ 改成**用真模块**（它们**导入时不连 COM**），只把 `get_com_member` 换成记录器。
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import importlib
    if "sw_export" in sys.modules:
        del sys.modules["sw_export"]
    mod = importlib.import_module("sw_export")
    calls = []

    def rec(obj, name, *args):
        calls.append((name, args))
        return getattr(obj, "_ret", None)

    #: ★ 只替换这一个 —— `export_to_bmp` 是唯一用到它的地方
    mod.get_com_member = rec
    return mod, calls


'''
P.write_text(t[:i] + NEW + t[j:], encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok 已改成用真模块")

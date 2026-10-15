"""★ spec 240 判据：型材中心配合**改走官方入口**（`IAssemblyDoc::CreateMateData` + `CreateMate`）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_mate_official_entry.py
# 定位:   钉住 `scripts/sw_weldment.py::create_profile_center_mate` **不再**走
#         `IFeatureManager::CreateDefinition(swFmMateProfileCenter=101)` —— 官方**不支持**那条路
#         （该常量只被枚举页收录，两个官方 `CreateDefinition` 宿主页的 `Type` 清单里都没有它），
#         官方入口 = `IAssemblyDoc::CreateMateData(swMatePROFILECENTER=24)` + `IAssemblyDoc::CreateMate(data)`。
# 官方依据: ① `C:\\swapi\\types\\IAssemblyDoc\\CreateMateData.md`
#              —— `System.object CreateMateData(System.int Type)`；`## Remarks` 的 `Type` 清单含
#                 `swMatePROFILECENTER`；**无** `Obsolete`。
#           ② `C:\\swapi\\types\\IAssemblyDoc\\CreateMate.md`
#              —— `System.object CreateMate(System.object MateData)`；`## Remarks` 第 1..5 步
#                 给出调用序，且逐条列出 `IProfileCenterMateFeatureData`；**无** `Obsolete`。
#           ③ `C:\\swapi\\enums\\swMateType_e.md:34` —— `| swMatePROFILECENTER | 24 |`
#           ④ `C:\\swapi\\types\\IProfileCenterMateFeatureData\\_overview.md` —— 5 个属性、0 个方法；
#              `## Remarks` 第 2 步：「Specify EntitiesToMate or … pre-select … Mark = 1」。
#           ⑤ 反例（**为什么不能换回前代入口**）：`C:\\swapi\\types\\IAssemblyDoc\\AddMate{,2,3,4,5}.md`
#              **五页全带** `Obsolete`（`grep -c -i obsolete` = 1/1/1/2/2）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件 —— 本文件是自包含的测试单元。
# ⚠ 本文件为静态比对 + 假宿主，未在本机实测（见 AGENTS.md 铁律 2）。
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import importlib
import io
import re
import sys
import types
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
SWAPI_ENUM = Path(r"C:\swapi\enums\swMateType_e.md")

#: ★ 本函数**不得**经由这些名字到达 `CreateDefinition`（含**共用骨架**的间接路径）。
FORBIDDEN_CALLEES = frozenset({"CreateDefinition", "CreateFeature", "_create_from_definition"})
#: ★ 本函数**必须**调用的官方入口宿主。
REQUIRED_CALLS = frozenset({"call_assembly_doc"})
#: ★ 官方入口的两个成员名（必须**逐字**出现在调用里）。
REQUIRED_MEMBERS = frozenset({"CreateMateData", "CreateMate"})
#: ★ 已废弃族（`AddMate`/`AddMate2`…`AddMate5`，五页全带 `Obsolete`）。
DEPRECATED_FAMILY = re.compile(r"^AddMate\d*$")


# ── 桩 ───────────────────────────────────────────────────────────────

class _StubModule(types.ModuleType):
    """任意属性都返回可调用对象（宽松桩）——但**不**用于 `import_com_dependencies`。"""

    def __getattr__(self, name):  # noqa: D105
        return lambda *a, **k: None


def _faithful_get_com_member(obj, name, *args, **kwargs):
    """忠实转发到宿主对象自己的同名属性（与 `test_extended_modules_contract` 同一形态）。"""
    return getattr(obj, name)(*args, **kwargs)


def _install_stubs() -> None:
    """★ 必须先桩 `sw_preflight` —— 受管 3.13.12 缺 comtypes/win32com，
    否则它会**交互式**问「是否授权 AI 自动配置？[Y/N]」⇒ 无人值守挂死。"""
    for mod, attrs in (
        ("sw_connect", {"get_com_member": _faithful_get_com_member,
                        "call_com_member": _faithful_get_com_member,
                        "save_document": lambda *a, **k: None,
                        "out_i4": lambda value=0: ("<out_i4>", int(value)),
                        "create_empty_dispatch_variant": lambda: "<empty_dispatch>",
                        "safe_get_com_member": lambda obj, name, *a, **k: None,
                        "set_com_member": lambda obj, name, value: (setattr(obj, name, value), value)[1]}),
        ("sw_document_data", {"set_custom_properties": lambda *a, **k: None}),
        ("sw_preflight", {"import_com_dependencies": lambda: (None, None, None)}),
    ):
        module = _StubModule(mod)
        for key, value in attrs.items():
            setattr(module, key, value)
        sys.modules.setdefault(mod, module)
    sys.modules.setdefault("sw_part", _StubModule("sw_part"))
    #: ★ 兜底分支 `from sw_connect import …` 需要 `ROOT/scripts` 在 `sys.path` 上。
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))


def _load(name: str):
    _install_stubs()
    module = importlib.import_module(name)
    #: ★ 无条件覆盖模块自己的引用（不受 import 顺序影响）。
    module.get_com_member = _faithful_get_com_member
    module.call_com_member = _faithful_get_com_member
    return module


def _tree() -> ast.Module:
    return ast.parse((SCRIPTS / "sw_weldment.py").read_text(encoding="utf-8"))


def _find_function(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name:
            return node
    raise AssertionError(f"`sw_weldment.py` 里找不到模块级函数 `{name}`")


def _callee_names(fn: ast.AST) -> set:
    """★ 同时收**点式调用**（`obj.M(...)`）与**裸名调用**（`M(...)`）。

    ★★ 只收点式调用 = **空判据**（spec 239 踩过：`create_draft` 走共用骨架时读成 0 个调用）。
    """
    names: set = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Name):
            names.add(func.id)
        elif isinstance(func, ast.Attribute):
            names.add(func.attr)
        elif isinstance(func, ast.Call):        # `obj.M(...)(...)` 链式
            inner = func.func
            if isinstance(inner, ast.Attribute):
                names.add(inner.attr)
            elif isinstance(inner, ast.Name):
                names.add(inner.id)
    return names


def _literal_member_args(fn: ast.AST) -> set:
    """⇒ `call_assembly_doc(<doc>, "<成员名>", …)` 里的**字面量**成员名集合。"""
    members: set = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        fname = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else None)
        if fname != "call_assembly_doc":
            continue
        for arg in node.args[1:2]:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                members.add(arg.value)
    return members


def _module_functions(tree: ast.Module) -> dict:
    return {n.name: n for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}


def _transitive_callees(tree: ast.Module, fn: ast.AST, depth: int = 4) -> set:
    """★ 展开**经由共用骨架的间接路径**：函数 → 它调用的模块级函数 → …（限深 4）。"""
    funcs = _module_functions(tree)
    seen: set = set()
    frontier = _callee_names(fn)
    for _ in range(depth):
        nxt: set = set()
        for name in frontier:
            if name in seen:
                continue
            seen.add(name)
            target = funcs.get(name)
            if target is not None:
                nxt |= _callee_names(target)
        frontier = nxt - seen
        if not frontier:
            break
    return seen


# ── 判据 ─────────────────────────────────────────────────────────────

class TestMateOfficialEntry(unittest.TestCase):
    """spec 240：官方入口的**内容断言**（AST + 假宿主）。"""

    def test_calls_official_entry_members(self):
        """① 必须调 `call_assembly_doc`，且逐字传 `CreateMateData` 与 `CreateMate`。"""
        fn = _find_function(_tree(), "create_profile_center_mate")
        calls = _callee_names(fn)
        self.assertTrue(calls, "取点为空 ⇒ 判据空转（检查量为 0 判失败）")
        self.assertTrue(REQUIRED_CALLS <= calls,
                        f"`create_profile_center_mate` 未调 {sorted(REQUIRED_CALLS)}；实收 {sorted(calls)}")
        members = _literal_member_args(fn)
        self.assertTrue(REQUIRED_MEMBERS <= members,
                        f"`call_assembly_doc` 未逐字传 {sorted(REQUIRED_MEMBERS)}；实收 {sorted(members)}")

    def test_no_create_definition_path_direct_or_transitive(self):
        """② ★ 直接与**间接**都不得到达 `CreateDefinition`（共用骨架形态）。"""
        tree = _tree()
        fn = _find_function(tree, "create_profile_center_mate")
        direct = _callee_names(fn) & FORBIDDEN_CALLEES
        self.assertFalse(direct, f"`create_profile_center_mate` 直接调了 {sorted(direct)}")
        reach = _transitive_callees(tree, fn)
        indirect = reach & FORBIDDEN_CALLEES
        self.assertFalse(indirect, f"经共用骨架间接到达 {sorted(indirect)}")

    def test_unsupported_skeleton_is_gone(self):
        """③ 官方不支持的骨架 `_create_from_definition` 必须**整个消失**（否则站点会退化成 `dynamic`）。"""
        tree = _tree()
        self.assertNotIn("_create_from_definition", _module_functions(tree),
                         "`sw_weldment._create_from_definition` 仍在 ⇒ 无调用方时站点会退化成 `dynamic`")

    def test_no_deprecated_add_mate_family(self):
        """④ 不得用已废弃的 `AddMate*` 族（官方五页全带 `Obsolete`）。"""
        tree = _tree()
        fn = _find_function(tree, "create_profile_center_mate")
        hits = sorted(n for n in _callee_names(fn) if DEPRECATED_FAMILY.match(n))
        self.assertFalse(hits, f"用了已废弃的 {hits}")
        file_wide = sorted(n for n in _callee_names(tree) if DEPRECATED_FAMILY.match(n))
        self.assertFalse(file_wide, f"`sw_weldment.py` 全文出现已废弃调用 {file_wide}")

    def test_official_member_pages_are_not_obsolete(self):
        """⑤ `alt` 的自证：官方入口两页**不得**带 `Obsolete`；`AddMate*` 族**必须**带。

        ★ 真树上 `alt` 只在合成树触发 ⇒ 抽成**可单测**的纯断言（spec 239 的纪律）。
        """
        types_dir = Path(r"C:\swapi\types\IAssemblyDoc")
        if not types_dir.is_dir():
            self.skipTest("官方文档树不在 ⇒ [SKIP]（缺数据源 ≠ 检查失败）")
        for member in ("CreateMateData", "CreateMate"):
            page = types_dir / f"{member}.md"
            self.assertTrue(page.is_file(), f"官方页缺失：{page}")
            self.assertEqual(0, page.read_text(encoding="utf-8", errors="replace")
                             .lower().count("obsolete"), f"{member} 页带 Obsolete")
        for variant in ("AddMate", "AddMate2", "AddMate3", "AddMate4", "AddMate5"):
            page = types_dir / f"{variant}.md"
            if page.is_file():
                self.assertIn("obsolete",
                              page.read_text(encoding="utf-8", errors="replace").lower(),
                              f"{variant} 页**没有** Obsolete ⇒ 本条的「不得使用」前提变了")

    def test_mate_type_enum_value_is_24(self):
        """⑥ `SW_MATE_PROFILE_CENTER` == 24，且与官方枚举页一致（三源之一）。"""
        module = _load("sw_weldment")
        self.assertEqual(24, module.SW_MATE_PROFILE_CENTER)
        if not SWAPI_ENUM.is_file():
            self.skipTest("官方枚举页不在 ⇒ [SKIP]")
        text = SWAPI_ENUM.read_text(encoding="utf-8", errors="replace")
        self.assertRegex(text, r"\|\s*swMatePROFILECENTER\s*\|\s*24\s*\|")

    def test_fm_101_constant_kept_as_evidence_anchor(self):
        """⑦ `SW_FM_MATE_PROFILE_CENTER`（101）保留 —— 它是「官方枚举里确有这个 fm 条目」的锚点。"""
        module = _load("sw_weldment")
        self.assertEqual(101, module.SW_FM_MATE_PROFILE_CENTER)

    def test_call_sequence_data_then_props_then_create(self):
        """⑧ 调用序（官方 `CreateMate` 的 `## Remarks` 第 1..5 步）：CreateMateData → 设属性 → CreateMate。"""
        module = _load("sw_weldment")
        events: list = []

        class _Data:
            def __setattr__(self, name, value):
                events.append(("set", name, value))
                object.__setattr__(self, name, value)

        data = _Data()

        def _fake_call_assembly_doc(doc, member, *args):
            events.append(("call", member, args))
            if member == "CreateMateData":
                return data
            if member == "CreateMate":
                return "FEAT"
            raise AssertionError(f"未预期的成员：{member}")

        module.call_assembly_doc = _fake_call_assembly_doc
        result = module.create_profile_center_mate(
            object(), "ENTS", mate_alignment=1, offset_distance=0.5,
            flip_dimension=True, lock_rotation=False)

        self.assertEqual("FEAT", result)
        self.assertEqual(("call", "CreateMateData", (24,)), events[0])
        self.assertEqual(("call", "CreateMate", (data,)), events[-1])
        middle = [e for e in events[1:-1] if e[0] == "set"]
        self.assertEqual(["EntitiesToMate", "MateAlignment", "OffsetDistance",
                          "FlipDimension", "LockRotation"],
                         [e[1] for e in middle])
        self.assertEqual(["ENTS", 1, 0.5, True, False], [e[2] for e in middle])

    def test_entities_none_is_rejected(self):
        """⑨ 前置拒绝仍在：`entities=None` ⇒ `ValueError`（不得静默发起 COM 调用）。"""
        module = _load("sw_weldment")
        with self.assertRaises(ValueError):
            module.create_profile_center_mate(object(), None)

    def test_create_mate_data_none_is_rejected(self):
        """⑩ `CreateMateData` 回 `None` ⇒ 抛错，**不**继续调 `CreateMate`。"""
        module = _load("sw_weldment")
        seen: list = []

        def _fake(doc, member, *args):
            seen.append(member)
            return None

        module.call_assembly_doc = _fake
        with self.assertRaises(RuntimeError):
            module.create_profile_center_mate(object(), "ENTS")
        self.assertEqual(["CreateMateData"], seen)


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    unittest.main(verbosity=2)

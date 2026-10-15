"""★ 判据：`local` 桶调用点的**候选值集**门禁（spec 234）—— 可枚举性 + 官方两源存在性。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_arg_guard.py
# 定位:   证 `scripts/check_dispatch_arg_guard.py` 能红 —— 每条判据各一个**合成树端到端负例**
#         （未表态 / 能枚举却声明 dynamic / 全查得到却声明 probe / 枚举不出却声明 probe /
#          下界收缩 / 零检查），外加**读取器**的两条形态规则（`.items()` 按位置、`.get()` 取值）。
# 官方依据: 无（纯 AST + 合成转储/合成 swapi 树）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_dispatch_arg_guard.py"

#: 合成转储：`## IFixture` 头 + 两个成员行（★ 成员行格式与真转储一致）。
DUMP = """# 反射清单 :: 合成夹具
## IFixture
  Void GetRealMember()
  Void GetOtherMember()
"""

#: ★ 夹具自带的**已覆盖样本**（可枚举 + 全部查得到 + 无需声明）——
#: 每个负例都带上它，否则失败会**因错误的原因**（`zero-checked`）发生（spec 232/233 的教训）。
COVERED = '''
def _covered_sample(obj):
    for name in ("GetRealMember", "GetOtherMember"):
        get_com_member(obj, name)
'''

#: 负例 a：候选值查不到 + 未表态 ⇒ `[undeclared]`。
GHOST = COVERED + '''
def read(obj):
    for name in ("GetRealMember", "GetGhostMember"):
        get_com_member(obj, name)
'''

#: 负例 b：候选集枚举不出 + 未表态 ⇒ `[undeclared]`。
PARAM = COVERED + '''
def read(obj, names):
    for name in names:
        get_com_member(obj, name)
'''

#: 负例 c：**能枚举**却声明 `dynamic` ⇒ `[invalid-claim]`。
DYNAMIC_LIE = COVERED + '''
def read(obj):
    for name in ("GetRealMember",):
        #: dispatch-arg: dynamic 我懒得看
        get_com_member(obj, name)
'''

#: 负例 d：候选值**全部查得到**却声明 `probe` ⇒ `[invalid-claim]`。
PROBE_LIE = COVERED + '''
def read(obj):
    for name in ("GetRealMember",):
        #: dispatch-arg: probe 其实没有探测语义
        get_com_member(obj, name)
'''

#: 负例 e：候选集**枚举不出**却声明 `probe` ⇒ `[invalid-claim]`（该用 `dynamic`）。
PROBE_ON_DYNAMIC = COVERED + '''
def read(obj, names):
    for name in names:
        #: dispatch-arg: probe 用错了逃生门
        get_com_member(obj, name)
'''

#: 正例：枚举不出 + `dynamic` 带理由 ⇒ 绿（★ 证明逃生门**能用**，不是永远红）。
DYNAMIC_OK = COVERED + '''
def read(obj, names):
    for name in names:
        #: dispatch-arg: dynamic 成员名元组由调用方给
        get_com_member(obj, name)
'''

#: 负例 f：**零检查**（一个 `local` 调用点都没有）⇒ `[zero-checked]`。
NO_SITE = '''
def read(obj):
    return get_com_member(obj, "GetRealMember")
'''

#: 负例 g：候选值查不到但已按 `probe` 表态 ⇒ 绿（★ `probe` 的**正例**）。
PROBE_OK = COVERED + '''
def read(obj):
    for name in ("GetGhostMember",):
        #: dispatch-arg: probe 试名探测：两源均查不到，按序试
        get_com_member(obj, name)
'''


def make_tree(body: str) -> Path:
    """⇒ 仓库**外**的临时树（`scripts/` + `_raw/` + `swapi/`）。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh234-"))
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "scripts" / "sw_fixture.py").write_text(body, encoding="utf-8")
    (tmp / "_raw").mkdir()
    (tmp / "_raw" / "iface_fixture.txt").write_text(DUMP, encoding="utf-8")
    (tmp / "swapi" / "IFixture").mkdir(parents=True)
    (tmp / "swapi" / "IFixture" / "GetRealMember.md").write_text("# x", encoding="utf-8")
    return tmp


def run_gate(root: Path, *, baseline: str = "0,0,0"):
    env = dict(os.environ)
    env["DSH_DISPATCH_ARG_ROOT"] = str(root)
    env["DSH_DISPATCH_ARG_DUMPS"] = str(root / "_raw" / "iface_fixture.txt")
    env["DSH_DISPATCH_ARG_SWAPI"] = str(root / "swapi")
    env["DSH_DISPATCH_ARG_BASELINE_MIN"] = baseline
    #: ★ 本门禁内部调 `check_dispatch_entry_guard.scan()` ⇒ 它的扫描根也要指到合成树。
    env["DSH_DISPATCH_ROOT"] = str(root)
    env["DSH_DISPATCH_BASELINE_MIN"] = "0,0,0"
    env["DSH_DISPATCH_CLASSIFICATION"] = str(root / "docs" / "nonexistent.json")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def readings(out: str) -> tuple[int, int, int, int]:
    """⇒ `(sites, enum, values, violations)`；找不到即抛（★ 不许静默降级成 0）。"""
    m = re.search(r"local (\d+) · 可枚举 (\d+) · 候选值 (\d+) · 违规 (\d+)", out)
    if m is None:
        raise AssertionError("取不到读数：\n" + out)
    return tuple(int(x) for x in m.groups())


def load_gate():
    spec = importlib.util.spec_from_file_location("cda234t", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cda234t"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_is_green_with_expected_readings(self):
        proc = subprocess.run(
            [sys.executable, "-B", str(GATE)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(ROOT), stdin=subprocess.DEVNULL, timeout=180,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        self.assertEqual(proc.returncode, 0, out)
        self.assertEqual(readings(out), (46, 42, 131, 0), out)


class TestEndToEnd(unittest.TestCase):
    """★ 每条判据各一个合成树端到端负例。"""

    def test_covered_sample_alone_is_green(self):
        """★ 已覆盖样本 ⇒ 绿（否则下面的负例会**因错误的原因**通过）。"""
        rc, out = run_gate(make_tree(COVERED))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (1, 1, 2, 0), out)

    def test_uncovered_value_without_declaration_is_red(self):
        rc, out = run_gate(make_tree(GHOST))
        self.assertEqual(rc, 1, out)
        self.assertIn("[undeclared]", out)
        self.assertIn("GetGhostMember", out)

    def test_unresolvable_without_declaration_is_red(self):
        rc, out = run_gate(make_tree(PARAM))
        self.assertEqual(rc, 1, out)
        self.assertIn("[undeclared]", out)
        self.assertIn("枚举不出", out)

    def test_dynamic_claim_on_resolvable_site_is_red(self):
        rc, out = run_gate(make_tree(DYNAMIC_LIE))
        self.assertEqual(rc, 1, out)
        self.assertIn("[invalid-claim]", out)
        self.assertIn("能枚举却声明枚举不出", out)

    def test_probe_claim_when_all_values_exist_is_red(self):
        rc, out = run_gate(make_tree(PROBE_LIE))
        self.assertEqual(rc, 1, out)
        self.assertIn("[invalid-claim]", out)
        self.assertIn("无探测语义", out)

    def test_probe_claim_on_unresolvable_site_is_red(self):
        rc, out = run_gate(make_tree(PROBE_ON_DYNAMIC))
        self.assertEqual(rc, 1, out)
        self.assertIn("[invalid-claim]", out)
        self.assertIn("该用 `dynamic`", out)

    def test_dynamic_declaration_is_accepted(self):
        """★ 逃生门**能用**：枚举不出 + `dynamic` 带理由 ⇒ 绿。"""
        rc, out = run_gate(make_tree(DYNAMIC_OK))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (2, 1, 2, 0), out)

    def test_probe_declaration_is_accepted(self):
        """★ `probe` 的正例：候选值查不到 + 已按试名探测表态 ⇒ 绿。"""
        rc, out = run_gate(make_tree(PROBE_OK))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (2, 2, 3, 0), out)

    def test_zero_local_sites_is_red(self):
        rc, out = run_gate(make_tree(NO_SITE))
        self.assertEqual(rc, 1, out)
        self.assertIn("[zero-checked]", out)

    def test_shrunk_baseline_is_red(self):
        """★ 只增不减：下界调高 ⇒ `[baseline-shrunk]`。"""
        rc, out = run_gate(make_tree(COVERED), baseline="9,9,9")
        self.assertEqual(rc, 1, out)
        self.assertIn("[baseline-shrunk]", out)


class TestReader(unittest.TestCase):
    """★ 读取器的两条**形态规则**（都曾是本切片自己的错）。"""

    @staticmethod
    def _resolve(src: str, var: str, module_src: str = ""):
        import ast
        mod = load_gate()
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
        modenv = mod.scope_env(ast.parse(module_src)) if module_src else {}
        return mod.resolve(fn, var, mod.scope_env(fn), modenv)

    def test_items_takes_value_at_index_one(self):
        """★ `for k, v in D.items()` ⇒ `v` 取**值**（首版取键 ⇒ 语义键冒充成员名）。"""
        got, why = self._resolve(
            "def f(o):\n"
            "    d = {'mass': 'GetMassConstraint'}\n"
            "    for k, v in d.items():\n"
            "        get_com_member(o, v)\n", "v")
        self.assertEqual(got, ["GetMassConstraint"], why)

    def test_items_takes_key_at_index_zero(self):
        got, why = self._resolve(
            "def f(o):\n"
            "    d = {'GetMesh': 1}\n"
            "    for k, v in d.items():\n"
            "        get_com_member(o, k)\n", "k")
        self.assertEqual(got, ["GetMesh"], why)

    def test_get_returns_value_not_key(self):
        """★ `D.get(k)` 返回**值**（首版取键 ⇒ `mass`/`stress` 冒充成员名）。"""
        got, why = self._resolve(
            "def f(o, kind):\n"
            "    g = GETTERS.get(kind)\n"
            "    get_com_member(o, g)\n", "g", "GETTERS = {'mass': 'GetMassConstraint'}\n")
        self.assertEqual(got, ["GetMassConstraint"], why)

    def test_tuple_unpack_projection_is_positional(self):
        """★ `for a, b in ((s, x), (t, y))` ⇒ 按 `a` 的**下标**投影。"""
        got, why = self._resolve(
            "def f(o):\n"
            "    for a, b in (('GetA', 1), ('GetB', 2)):\n"
            "        get_com_member(o, a)\n", "a")
        self.assertEqual(got, ["GetA", "GetB"], why)

    def test_non_literal_returns_none_not_empty(self):
        """★ 「解析不出」必须返回 `None`，**不许静默降级成空集**。"""
        got, why = self._resolve(
            "def f(o, names):\n"
            "    for n in names:\n"
            "        get_com_member(o, n)\n", "n")
        self.assertIsNone(got, why)

    def test_declaration_association_skips_blank_lines_only(self):
        """★ 确定性关联：向上**只**跳空行，第一行非空行必须是声明。"""
        mod = load_gate()
        lines = ["x = 1", "", "#: dispatch-arg: dynamic 理由", "", "get_com_member(o, n)"]
        self.assertEqual(mod.declaration_above(lines, 5), ("dynamic", "理由"))
        self.assertIsNone(mod.declaration_above(["x = 1", "# 别的注释", "call()"], 3))


if __name__ == "__main__":
    unittest.main()

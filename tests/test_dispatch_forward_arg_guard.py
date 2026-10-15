"""★ 判据：分发口**调用点**的非字面量成员名实参门禁（spec 235）—— 可枚举或显式表态。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_forward_arg_guard.py
# 定位:   证 `scripts/check_dispatch_forward_arg_guard.py` 能红 —— 每条判据各一个
#         **合成树端到端负例**（未表态 / `upstream` 名字不符 / `upstream` 实参不是形参 /
#          能枚举却声明 `dynamic` / 全查得到却声明 `probe` / 枚举不出却声明 `probe` /
#          零检查 / 下界收缩），外加**读取器**的形态规则与**源隔离**一条。
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
GATE = ROOT / "scripts" / "check_dispatch_forward_arg_guard.py"

#: 合成转储：`## IFixture` 头 + 两个成员行（★ 成员行格式与真转储一致）。
DUMP = """# 反射清单 :: 合成夹具
## IFixture
  Void GetRealMember()
  Void GetOtherMember()
"""

#: 合成树里的**分发口**（成员名以形参转发给 `get_com_member`）。
ENTRY = '''
def _entry(obj, member):
    return get_com_member(obj, member)
'''

#: ★ 夹具自带的**已覆盖样本**（非字面量 + 可枚举 + 全部查得到 + 无需声明）——
#: 每个负例都带上它，否则失败会**因错误的原因**（`zero-checked`）发生（spec 232/233/234 的教训）。
COVERED = ENTRY + '''
def ok_caller(obj):
    for name in ("GetRealMember", "GetOtherMember"):
        _entry(obj, name)
'''

#: 负例 a：枚举不出 + 未表态 ⇒ `[undeclared]`。
UNSIGNED = COVERED + '''
def bad_caller(obj, member):
    return _entry(obj, member)
'''

#: 正例：枚举不出 + `upstream` 且 caller 名与理由都对 ⇒ 绿（★ 证明逃生门**能用**）。
UPSTREAM_OK = COVERED + '''
def bad_caller(obj, member):
    #: dispatch-fwd: upstream bad_caller 二级转发：成员名由调用方给
    return _entry(obj, member)
'''

#: 负例 b：`upstream` 声明的 caller 名与实际包围 `def` **不符** ⇒ `[invalid-claim]`。
UPSTREAM_WRONG_NAME = COVERED + '''
def bad_caller(obj, member):
    #: dispatch-fwd: upstream not_the_enclosing_def 名字写错
    return _entry(obj, member)
'''

#: 负例 c：`upstream` 但实参**不是**包围 `def` 的形参 ⇒ `[invalid-claim]`。
UPSTREAM_NONPARAM = COVERED + '''
def bad_caller(obj):
    name = pick_name()
    #: dispatch-fwd: upstream bad_caller 其实不是形参
    return _entry(obj, name)
'''

#: 正例：枚举不出 + `dynamic` 带理由 ⇒ 绿。
DYNAMIC_OK = COVERED + '''
def bad_caller(obj, names):
    out = []
    for name in names:
        #: dispatch-fwd: dynamic 成员名元组由调用方给
        out.append(_entry(obj, name))
    return out
'''

#: 负例 d：**能枚举**却声明 `dynamic` ⇒ `[invalid-claim]`。
DYNAMIC_LIE = COVERED + '''
def bad_caller(obj):
    for name in ("GetRealMember",):
        #: dispatch-fwd: dynamic 我懒得看
        _entry(obj, name)
'''

#: 负例 e：候选值**全部查得到**却声明 `probe` ⇒ `[invalid-claim]`。
PROBE_LIE = COVERED + '''
def bad_caller(obj):
    for name in ("GetRealMember",):
        #: dispatch-fwd: probe 其实没有探测语义
        _entry(obj, name)
'''

#: 负例 f：枚举不出却声明 `probe` ⇒ `[invalid-claim]`（该用 `dynamic`）。
PROBE_ON_DYNAMIC = COVERED + '''
def bad_caller(obj, names):
    out = []
    for name in names:
        #: dispatch-fwd: probe 用错了逃生门
        out.append(_entry(obj, name))
    return out
'''

#: 正例：候选值查不到 + 已按 `probe` 表态 ⇒ 绿。
PROBE_OK = COVERED + '''
def bad_caller(obj):
    for name in ("GetGhostMember",):
        #: dispatch-fwd: probe 试名探测：两源均查不到，按序试
        _entry(obj, name)
'''

#: 负例 g：**零检查**（一个非字面量调用点都没有）⇒ `[zero-checked]`。
NO_SITE = ENTRY + '''
def only_literal(obj):
    return _entry(obj, "GetRealMember")
'''


def make_tree(body: str) -> Path:
    """⇒ 仓库**外**的临时树（`scripts/` + `_raw/` + `swapi/`）。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh235-"))
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "scripts" / "sw_fixture.py").write_text(body, encoding="utf-8")
    (tmp / "_raw").mkdir()
    (tmp / "_raw" / "iface_fixture.txt").write_text(DUMP, encoding="utf-8")
    (tmp / "swapi" / "IFixture").mkdir(parents=True)
    (tmp / "swapi" / "IFixture" / "GetRealMember.md").write_text("# x", encoding="utf-8")
    return tmp


def run_gate(root: Path, *, baseline: str = "0,0,0"):
    """★ 合成树跑门禁：**本门禁自己的源开关**必须都指到合成树（否则会读真树）。"""
    env = dict(os.environ)
    env["DSH_DISPATCH_FWD_ROOT"] = str(root)
    env["DSH_DISPATCH_FWD_DUMPS"] = str(root / "_raw" / "iface_fixture.txt")
    env["DSH_DISPATCH_FWD_SWAPI"] = str(root / "swapi")
    env["DSH_DISPATCH_FWD_BASELINE_MIN"] = baseline
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def readings(out: str) -> tuple[int, int, int, int]:
    """⇒ `(sites, enum, values, violations)`；找不到即抛（★ 不许静默降级成 0）。"""
    m = re.search(r"非字面量 (\d+) · 可枚举 (\d+) · 候选值 (\d+) · 违规 (\d+)", out)
    if m is None:
        raise AssertionError("取不到读数：\n" + out)
    return tuple(int(x) for x in m.groups())


def load_gate():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("cdfa235t", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdfa235t"] = mod
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
        self.assertEqual(readings(out), (8, 4, 12, 0), out)


class TestEndToEnd(unittest.TestCase):
    """★ 每条判据各一个合成树端到端负例。"""

    def test_covered_sample_alone_is_green(self):
        """★ 已覆盖样本 ⇒ 绿（否则下面的负例会**因错误的原因**通过）。"""
        rc, out = run_gate(make_tree(COVERED))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (1, 1, 2, 0), out)

    def test_undeclared_nonliteral_site_is_red(self):
        rc, out = run_gate(make_tree(UNSIGNED))
        self.assertEqual(rc, 1, out)
        self.assertIn("[undeclared]", out)
        self.assertIn("枚举不出", out)

    def test_upstream_declaration_is_accepted(self):
        """★ 逃生门**能用**：枚举不出 + `upstream` 名字对 + 有理由 ⇒ 绿。"""
        rc, out = run_gate(make_tree(UPSTREAM_OK))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (2, 1, 2, 0), out)

    def test_upstream_with_wrong_caller_name_is_red(self):
        rc, out = run_gate(make_tree(UPSTREAM_WRONG_NAME))
        self.assertEqual(rc, 1, out)
        self.assertIn("[invalid-claim]", out)
        self.assertIn("不符", out)

    def test_upstream_on_non_parameter_is_red(self):
        rc, out = run_gate(make_tree(UPSTREAM_NONPARAM))
        self.assertEqual(rc, 1, out)
        self.assertIn("[invalid-claim]", out)
        self.assertIn("不是**包围 `def` 的形参", out)

    def test_dynamic_declaration_is_accepted(self):
        rc, out = run_gate(make_tree(DYNAMIC_OK))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (2, 1, 2, 0), out)

    def test_dynamic_claim_on_enumerable_site_is_red(self):
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

    def test_probe_declaration_is_accepted(self):
        rc, out = run_gate(make_tree(PROBE_OK))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (2, 2, 3, 0), out)

    def test_zero_checked_is_red(self):
        rc, out = run_gate(make_tree(NO_SITE))
        self.assertEqual(rc, 1, out)
        self.assertIn("[zero-checked]", out)

    def test_shrunk_baseline_is_red(self):
        """★ 只增不减：下界调高 ⇒ `[baseline-shrunk]`。"""
        rc, out = run_gate(make_tree(COVERED), baseline="9,9,9")
        self.assertEqual(rc, 1, out)
        self.assertIn("[baseline-shrunk]", out)

    def test_synthetic_tree_does_not_read_real_sources(self):
        """★ 源隔离：合成树只该看到**合成**转储/swapi（否则读数被真树污染，spec 234 的坑）。"""
        rc, out = run_gate(make_tree(COVERED))
        self.assertEqual(rc, 0, out)
        self.assertIn("官方成员名 3 个", out)
        self.assertNotIn("18460", out)


class TestReader(unittest.TestCase):
    """★ 读取器的**形态规则**（每条都钉住一个语义，不写散文）。"""

    @staticmethod
    def _cand(src: str, fn_name: str = "f"):
        import ast
        import check_dispatch_arg_guard as cdag
        mod = load_gate()
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == fn_name)
        calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call)
                 and isinstance(n.func, ast.Name) and n.func.id == "_entry"]
        arg = calls[0].args[1]
        return mod.candidates(arg, fn, cdag.scope_env(fn), cdag.scope_env(tree))

    def test_subscript_of_dict_literal_takes_values_not_keys(self):
        """★ `DICT[k]` 取的是**值**（与 234 的 `.get(k)` 同族：下标访问返回的是值）。"""
        got, why = self._cand(
            "GET = {'a': 'GetRealMember', 'b': 'GetOtherMember'}\n\n"
            "def f(o, k):\n"
            "    return _entry(o, GET[k])\n")
        self.assertEqual(got, ["GetRealMember", "GetOtherMember"], why)

    def test_ifexp_takes_both_branches(self):
        got, why = self._cand(
            "def f(o, hidden):\n"
            "    return _entry(o, 'GetA' if hidden else 'GetB')\n")
        self.assertEqual(got, ["GetA", "GetB"], why)

    def test_name_bound_to_literal_container_is_enumerable(self):
        got, why = self._cand(
            "def f(o):\n"
            "    names = ('GetA', 'GetB')\n"
            "    return _entry(o, names)\n")
        self.assertEqual(got, ["GetA", "GetB"], why)

    def test_non_closed_form_returns_none_not_empty(self):
        """★ 「解析不出」必须返回 `None`，**不许静默降级成空集**。"""
        got, why = self._cand(
            "def f(o, x):\n"
            "    return _entry(o, f'Get{x}')\n")
        self.assertIsNone(got, why)

    def test_declaration_association_skips_blank_lines_only(self):
        """★ 确定性关联：向上**只**跳空行，第一行非空行必须是声明。"""
        mod = load_gate()
        lines = ["x = 1", "", "#: dispatch-fwd: dynamic 理由", "", "_entry(o, n)"]
        self.assertEqual(mod.declaration_above(lines, 5), ("dynamic", "理由"))
        self.assertIsNone(mod.declaration_above(["x = 1", "# 别的注释", "call()"], 3))


if __name__ == "__main__":
    unittest.main()

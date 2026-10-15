"""★ 判据：分发口 `upstream` 声明的**上游覆盖**门禁（spec 236）—— 桶必须与事实相符。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_upstream_guard.py
# 定位:   证 `scripts/check_dispatch_upstream_guard.py` 能红 —— 每条判据各一个
#         **合成树端到端负例**（未表态桶 / 桶不在词表 / 缺理由 / `sites` 桶却无调用点 /
#          `sites` 桶的调用点非字面量 / 候选值官方查不到 / `orphan` 桶却有 ToolSpec 引用 /
#          `tool-only` 桶却有调用点 / 零检查 / 下界收缩），外加**取实参**的形态规则与
#         **源隔离**一条。
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
GATE = ROOT / "scripts" / "check_dispatch_upstream_guard.py"

#: 合成转储（★ 成员行格式与真转储一致；接口名在 `## <接口>` 头行）。
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

#: 合成树里的**上游 `def`**：它把形参 `member` 二级转发给分发口 ⇒ 产生一条非字面量调用点。
def mid(mode=None, reason="理由"):
    """⇒ 上游 `def mid` 的源码；`mode=None` ⇒ **不写桶**（未表态）。"""
    if mode is None:
        decl = "    #: dispatch-fwd: upstream mid\n"
    elif reason is None:
        decl = "    #: dispatch-fwd: upstream mid %s\n" % mode
    else:
        decl = "    #: dispatch-fwd: upstream mid %s %s\n" % (mode, reason)
    return "def mid(obj, member):\n%s    return _entry(obj, member)\n" % decl


#: `mid` 的一个**字面量**调用点（`sites` 桶的正样本）。
CALL_LITERAL = '''
def top(obj):
    return mid(obj, "GetRealMember")
'''

#: `mid` 的一个**非字面量**调用点（`sites` 桶的负样本）。
CALL_NONLITERAL = '''
def top(obj, m):
    return mid(obj, m)
'''

#: `mid` 的一个**官方查不到**的字面量调用点。
CALL_GHOST = '''
def top(obj):
    return mid(obj, "GetGhostMember")
'''

#: 合成 ToolSpec（`function="mid"` ⇒ `tool-only` 桶的事实依据）。
TOOLSPEC = 'SPEC = dict(module="sw_fixture", function="mid")\n'


def make_tree(body: str, *, toolspec: bool = False) -> Path:
    """⇒ 仓库**外**的临时树（`scripts/` + `mcp-server/` + `_raw/` + `swapi/`）。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh236-"))
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "scripts" / "sw_fixture.py").write_text(body, encoding="utf-8")
    if toolspec:
        (tmp / "mcp-server").mkdir()
        (tmp / "mcp-server" / "tool_specs_fixture.py").write_text(TOOLSPEC, encoding="utf-8")
    (tmp / "_raw").mkdir()
    (tmp / "_raw" / "iface_fixture.txt").write_text(DUMP, encoding="utf-8")
    (tmp / "swapi" / "IFixture").mkdir(parents=True)
    (tmp / "swapi" / "IFixture" / "GetRealMember.md").write_text("# x", encoding="utf-8")
    return tmp


def run_gate(root: Path, *, baseline: str = "0,0,0"):
    """★ 合成树跑门禁：**本门禁自己的源开关**必须都指到合成树（否则会读真树）。"""
    env = dict(os.environ)
    env["DSH_DISPATCH_UPSTREAM_ROOT"] = str(root)
    env["DSH_DISPATCH_UPSTREAM_DUMPS"] = str(root / "_raw" / "iface_fixture.txt")
    env["DSH_DISPATCH_UPSTREAM_SWAPI"] = str(root / "swapi")
    env["DSH_DISPATCH_UPSTREAM_BASELINE_MIN"] = baseline
    #: ★ 235 的取点件（`forward_sites`）也要指到合成树（否则 `rel` 会按真树算）。
    env["DSH_DISPATCH_FWD_ROOT"] = str(root)
    env["DSH_DISPATCH_FWD_DUMPS"] = str(root / "_raw" / "iface_fixture.txt")
    env["DSH_DISPATCH_FWD_SWAPI"] = str(root / "swapi")
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=180,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def readings(out: str) -> tuple[int, int, int, int]:
    """⇒ `(decls, sites, values, violations)`；找不到即抛（★ 不许静默降级成 0）。"""
    m = re.search(r"upstream 声明 (\d+) · 上游调用点 (\d+) · 候选值 (\d+) · 违规 (\d+)", out)
    if m is None:
        raise AssertionError("取不到读数：\n" + out)
    return tuple(int(x) for x in m.groups())


def load_gate():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("cdug236t", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["cdug236t"] = mod
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
        self.assertEqual(readings(out), (3, 10, 5, 0), out)
        #: ★ 三个桶各一个（3 条声明各落一桶）—— 这是本规格的**核心读数**。
        self.assertIn("桶 sites 1 / tool-only 1 / orphan 1", out)


class TestEndToEnd(unittest.TestCase):
    """★ 每条判据各一个合成树端到端负例。"""

    def test_sites_bucket_with_literal_call_site_is_green(self):
        rc, out = run_gate(make_tree(ENTRY + mid("sites") + CALL_LITERAL))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (1, 1, 1, 0), out)

    def test_orphan_bucket_is_green(self):
        """★ 0 调用点 + 0 ToolSpec 引用 ⇒ `orphan` 成立。"""
        rc, out = run_gate(make_tree(ENTRY + mid("orphan")))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (1, 0, 0, 0), out)

    def test_tool_only_bucket_is_green(self):
        """★ 0 AST 调用点 + 有 ToolSpec 引用 ⇒ `tool-only` 成立（★ 「0 调用点」≠「没人用」）。"""
        rc, out = run_gate(make_tree(ENTRY + mid("tool-only"), toolspec=True))
        self.assertEqual(rc, 0, out)
        self.assertEqual(readings(out), (1, 0, 0, 0), out)

    def test_missing_bucket_is_red(self):
        rc, out = run_gate(make_tree(ENTRY + mid(None)))
        self.assertEqual(rc, 1, out)
        self.assertIn("未表态", out)
        self.assertIn("上游桶", out)

    def test_unknown_bucket_is_red(self):
        rc, out = run_gate(make_tree(ENTRY + mid("banana")))
        self.assertEqual(rc, 1, out)
        self.assertIn("不在封闭词表", out)

    def test_missing_reason_is_red(self):
        rc, out = run_gate(make_tree(ENTRY + mid("sites", None)))
        self.assertEqual(rc, 1, out)
        self.assertIn("缺理由", out)

    def test_sites_bucket_without_call_sites_is_red(self):
        """★ 自证条件：声明 `sites` 但上游**无**调用点 ⇒ 事实是 `orphan` ⇒ 红。"""
        rc, out = run_gate(make_tree(ENTRY + mid("sites")))
        self.assertEqual(rc, 1, out)
        self.assertIn("与**事实** `orphan` 不符", out)

    def test_sites_bucket_with_nonliteral_call_site_is_red(self):
        """★ 上游调用点用**变量**传成员名 ⇒ 红（该点须另行表态）。"""
        rc, out = run_gate(make_tree(ENTRY + mid("sites") + CALL_NONLITERAL))
        self.assertEqual(rc, 1, out)
        self.assertIn("非字面量", out)

    def test_sites_bucket_with_unknown_value_is_red(self):
        """★ 上游调用点的字面量在官方两源查不到 ⇒ 红。"""
        rc, out = run_gate(make_tree(ENTRY + mid("sites") + CALL_GHOST))
        self.assertEqual(rc, 1, out)
        self.assertIn("查不到", out)

    def test_orphan_bucket_with_toolspec_ref_is_red(self):
        """★ 自证条件：声明 `orphan` 但名字出现在 ToolSpec ⇒ 事实是 `tool-only` ⇒ 红。"""
        rc, out = run_gate(make_tree(ENTRY + mid("orphan"), toolspec=True))
        self.assertEqual(rc, 1, out)
        self.assertIn("与**事实** `tool-only` 不符", out)

    def test_tool_only_bucket_with_call_sites_is_red(self):
        """★ 自证条件：声明 `tool-only` 但上游**有**调用点 ⇒ 事实是 `sites` ⇒ 红。"""
        rc, out = run_gate(make_tree(ENTRY + mid("tool-only") + CALL_LITERAL, toolspec=True))
        self.assertEqual(rc, 1, out)
        self.assertIn("与**事实** `sites` 不符", out)

    def test_zero_checked_is_red(self):
        """★ 假绿守卫：一条 `upstream` 声明都没有 ⇒ 红（事实 46）。"""
        rc, out = run_gate(make_tree(ENTRY + 'def top(obj):\n    return _entry(obj, "GetRealMember")\n'))
        self.assertEqual(rc, 1, out)
        self.assertIn("检查过的 `upstream` 声明 == 0", out)

    def test_shrunk_baseline_is_red(self):
        """★ 只增不减：下界调高 ⇒ 红。"""
        rc, out = run_gate(make_tree(ENTRY + mid("orphan")), baseline="9,9,9")
        self.assertEqual(rc, 1, out)
        self.assertIn("只增不减", out)

    def test_synthetic_tree_does_not_read_real_sources(self):
        """★ 源隔离：合成树只该看到**合成**转储/swapi（否则读数被真树污染，spec 234 的坑）。"""
        rc, out = run_gate(make_tree(ENTRY + mid("sites") + CALL_LITERAL))
        self.assertEqual(rc, 0, out)
        self.assertIn("官方成员名 3 个", out)
        self.assertNotIn("18460", out)


class TestArgForParam(unittest.TestCase):
    """★ 取实参的**形态规则**（每条钉住一个语义，不写散文）。"""

    @staticmethod
    def _call(src: str):
        import ast
        tree = ast.parse(src)
        return next(n for n in ast.walk(tree)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "mid")

    def test_positional_takes_by_index_of_param_name(self):
        """★ 按**形参名在形参表里的下标**取实参（`set_study_option_report` 的 `name` 不是最后一个）。"""
        mod = load_gate()
        call = self._call("mid(a, b, name, c)")
        arg, how = mod.arg_for_param(call, ["study", "family", "name", "value"], "name")
        self.assertEqual(how, "pos:2")
        self.assertEqual(arg.id, "name")

    def test_keyword_wins_over_position(self):
        """★ 关键字实参优先（★ 与位置下标可能不一致时不许猜）。"""
        mod = load_gate()
        call = self._call("mid(a, b, name=kw)")
        arg, how = mod.arg_for_param(call, ["study", "family", "name", "value"], "name")
        self.assertEqual(how, "kw:name")
        self.assertEqual(arg.id, "kw")

    def test_missing_param_returns_none_not_a_default(self):
        """★ 「取不到」必须显式返回 `None`，**不许静默降级**成空值/默认值。"""
        mod = load_gate()
        call = self._call("mid(a)")
        arg, how = mod.arg_for_param(call, ["study", "family", "name", "value"], "name")
        self.assertIsNone(arg)
        self.assertEqual(how, "missing")


if __name__ == "__main__":
    unittest.main()

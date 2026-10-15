"""★ 判据：`check_dispatch_byref_guard.py` —— 分发口调用点的标量 by-ref 占位（spec 231）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_byref_guard.py
# 定位:   证 spec 231 的门禁 ① **能红**（合成树端到端负例：裸传标量出参 ⇒ exit 1）、
#         ② **下界承重**（拔高下界即红）、③ **覆盖完整**（311 + 16 == 230 的 327）、
#         ④ **缺数据源走 SKIP**（显式指向不存在的路径）。
# 官方依据: 无（纯 AST + 反射转储）。by-ref 语义依据见 spec 228 §三。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_dispatch_byref_guard.py"

#: ★★ **门禁自己的下界**（★ 单一真源 —— 见 `TestRealTree` 里的订正说明）。
sys.path.insert(0, str(ROOT / "scripts"))
import check_dispatch_byref_guard as _byref_gate          # noqa: E402
import check_dispatch_entry_guard as _entry_gate          # noqa: E402

BASELINE_BYREF_SITES = _byref_gate.BASELINE_BYREF_SITES
#: ★★ **spec 230 的 `resolved_sites` 下界**（★ 从**另一个门禁** import ——
#:   它才是「可解析调用点」的真源；★ 本门禁的 `已核 + arity + 未绑定` 应当**等于**它）✓
SPEC230_RESOLVED_SITES = _entry_gate.BASELINE_RESOLVED_SITES

DECL = "#: dispatch-guard: exempt internal-helper\n"

#: 转发骨架（一级转发，成员名以形参 `member` 传）。
SKELETON = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj):
    return _dispatch(obj, "SomeMember", %s)
"""

#: 合成转储：`SomeMember` 的第 0 位是**标量出参** `Int32&`。
FIXTURE_DUMP = """# 反射清单 :: Fixture
# 由测试合成 —— 只含被测对象。

## Fixture
  Int32 SomeMember(Int32&)
"""

#: 合成转储：`SomeMember` 有 2 个形参（第 0 位是标量出参）⇒ 实参 1 个 ⇒ arity 不符。
FIXTURE_DUMP_ARITY2 = """# 反射清单 :: Fixture
## Fixture
  Int32 SomeMember(Int32&, Object)
"""


def run_gate(root: Path | None, *, dumps: str | None = None, baseline: str | None = None):
    env = dict(os.environ)
    for key, val in (("DSH_DISPATCH_BYREF_ROOT", str(root) if root else None),
                     ("DSH_DISPATCH_BYREF_DUMPS", dumps),
                     ("DSH_DISPATCH_BYREF_BASELINE_MIN", baseline),
                     ("DSH_DISPATCH_ROOT", None)):
        if val is None:
            env.pop(key, None)
        else:
            env[key] = val
    proc = subprocess.run(
        [sys.executable, "-B", str(GATE)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(ROOT), env=env, stdin=subprocess.DEVNULL, timeout=300,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def make_tree(files: dict[str, str]) -> Path:
    """⇒ 仓库**外**的临时树；`files` = `{"scripts/x.py": 源码, "dumps/y.txt": 文本}`。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh231-"))
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp


def summary(out: str) -> str:
    """⇒ 末尾那条汇总行。"""
    for line in reversed(out.splitlines()):
        if line.startswith("分发口 by-ref ·"):
            return line
    return ""


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_is_frozen_and_nonvacuous(self):
        rc, out = run_gate(None)
        self.assertEqual(rc, 0, out)
        self.assertIn("可核分发口 21", out)
        #: ★★★ **2026-10-10（规格 301）订正：`assertIn("已核调用点 311")` → 「实测 ≥ 下界」** ——
        #:   ★ **为什么是正当的**：★ 本判据的**意图**是「已核调用点**不低于门禁钉的下界**」
        #:     ⇒ ★★ **原判据用 `assertIn` 把「下界」当成了「实际值」**（★ 两者**当时恰好同值** ⇒ 巧合）
        #:     ⇒ ★★ 真树**涨到 316** 后，`assertIn("已核调用点 311")` 就**恒红**（★ 而"涨"是**好事**）。
        #:   ★★ **⇒ 正解：从输出里**解析实测值**，再与**下界**比** ✓
        #:   ★★ **依据**（`MEMORY.md` 规则 16）：「★ **别拿一个数去核另一个**」✓
        _m = re.search(r"已核调用点 (\d+)", out)
        self.assertIsNotNone(_m, out)
        self.assertGreaterEqual(int(_m.group(1)), BASELINE_BYREF_SITES, out)
        self.assertIn("违规 0", out)
        self.assertIn("[PASS]", out)

    def test_coverage_equals_spec230_resolved_sites(self):
        """★★ **覆盖完整**：本门禁的 `已核 + arity + 未绑定` == 另一门禁的**实测** `可解析调用点`。

        ★ 若哪天这几个数对不上 ⇒ 有调用点**被静默吞掉**（spec 230 教训）⇒ 当场红。

        ★★ **2026-10-10（规格 301）订正两处** ——
          ① ★ 原先硬写 `== 327`（★ 那是**当时**的读数）⇒ ★★ 真树涨到 **329** 后**恒红**；
          ② ★ 改成拿 `BASELINE_RESOLVED_SITES`（**下界** 327）比也**不对** ——
             ★★ 那是**只增不减的下界**，★ 而本判据要的是「**两个实测值相等**」
             ⇒ ★★★ **正解：两边都取**实测**（★ 各跑一次那个门禁）** ✓
          ★ 这**保留原意图**（★ 覆盖不许有洞），★ 且**不依赖某个快照的绝对值** ✓
        """
        rc, out = run_gate(None)
        self.assertEqual(rc, 0, out)
        m = re.search(r"已核调用点 (\d+)", out)
        a = re.search(r"arity 不符 (\d+)", out)
        u = re.search(r"形参未绑定 (\d+)", out)
        self.assertIsNotNone(m, out)
        self.assertIsNotNone(a, out)
        self.assertIsNotNone(u, out)
        #: ★★ **另一门禁的实测值**（★ 它是「可解析调用点」的真源）
        rc2, out2 = self._entry_gate_out()
        self.assertEqual(rc2, 0, out2)
        resolved = int(re.search(r"可解析调用点 (\d+)", out2).group(1))
        self.assertEqual(int(m.group(1)) + int(a.group(1)) + int(u.group(1)), resolved, out)
        #: ★ 并核「实测 ≥ 冻结的下界」（★ 下界只增不减）
        self.assertGreaterEqual(resolved, SPEC230_RESOLVED_SITES, out2)

    @staticmethod
    def _entry_gate_out():
        """★ 跑**另一个**门禁（`check_dispatch_entry_guard`）并回 `(rc, out)`。"""
        gate = ROOT / "scripts" / "check_dispatch_entry_guard.py"
        proc = subprocess.run([sys.executable, "-B", str(gate)], capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              cwd=str(ROOT), stdin=subprocess.DEVNULL, timeout=180)
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")

    def test_entries_baseline_shrink_is_red(self):
        rc, out = run_gate(None, baseline="22,311")
        self.assertEqual(rc, 1, out)
        self.assertIn("baseline-shrunk", out)
        self.assertIn("可核分发口 21 < 下界 22", out)

    def test_sites_baseline_shrink_is_red(self):
        """★ 下界承重：把 `sites` 下界抬到**实测 + 1** ⇒ 当场红。

        ★★ **2026-10-10（规格 301）改成**动态取实测值** —— ★ 原先硬写 `312`（★ 那时实测 311）。
          ★★ 真树已涨到 **316** ⇒ ★ 硬写的 `312` **不再承重**（★ 316 ≥ 312 ⇒ **不红**）
          ⇒ ★★ **判据静默失效**（★ 它本该证明「下界承重」）⇒ ★ 改成 `实测 + 1` ⇒ **涨多少都不失效** ✓
        """
        rc0, out0 = run_gate(None)
        self.assertEqual(rc0, 0, out0)
        actual = int(re.search(r"已核调用点 (\d+)", out0).group(1))
        rc, out = run_gate(None, baseline="21,%d" % (actual + 1))
        self.assertEqual(rc, 1, out)
        self.assertIn("已核调用点 %d < 下界 %d" % (actual, actual + 1), out)


class TestSyntheticTrees(unittest.TestCase):
    """合成树端到端（★ 夹具只含被测对象）。"""

    def _tree(self, call_arg: str, dump: str = FIXTURE_DUMP):
        tmp = make_tree({
            "scripts/sw_fixture.py": DECL + SKELETON % call_arg,
            "dumps/iface_fixture.txt": dump,
        })
        return tmp, str(tmp / "dumps" / "iface_fixture.txt")

    def test_bare_scalar_out_param_is_red(self):
        """★★★ **核心负例**：该位签名说 `Int32&`，调用点裸传 `5` ⇒ 当场红。"""
        tmp, dumps = self._tree("5")
        rc, out = run_gate(tmp, dumps=dumps, baseline="0,0")
        self.assertEqual(rc, 1, out)
        self.assertIn("[bare-byref]", out)
        self.assertIn("SomeMember", out)
        self.assertIn("第 0 位应为 Int32&", out)
        self.assertIn("违规 1", out)

    def test_byref_wrapper_is_green(self):
        tmp, dumps = self._tree("out_i4()")
        rc, out = run_gate(tmp, dumps=dumps, baseline="0,0")
        self.assertEqual(rc, 0, out)
        self.assertIn("已核调用点 1", out)
        self.assertIn("违规 0", out)

    def test_byref_variable_is_green(self):
        """★ `v = out_i4()` 后传 `v` ⇒ 合法（`byref_variables` 口径）。"""
        src = DECL + """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj):
    v = out_i4()
    return _dispatch(obj, "SomeMember", v)
"""
        tmp = make_tree({"scripts/sw_fixture.py": src, "dumps/iface_fixture.txt": FIXTURE_DUMP})
        rc, out = run_gate(tmp, dumps=str(tmp / "dumps" / "iface_fixture.txt"), baseline="0,0")
        self.assertEqual(rc, 0, out)
        self.assertIn("违规 0", out)

    def test_nonliteral_member_is_not_judged(self):
        """调用点传的成员名是变量 ⇒ 不在解析面内 ⇒ 不判罪（只计数）。"""
        src = DECL + """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj, name):
    return _dispatch(obj, name, 5)
"""
        tmp = make_tree({"scripts/sw_fixture.py": src, "dumps/iface_fixture.txt": FIXTURE_DUMP})
        rc, out = run_gate(tmp, dumps=str(tmp / "dumps" / "iface_fixture.txt"), baseline="0,0")
        self.assertEqual(rc, 0, out)
        self.assertIn("非字面量调用点 1", out)
        self.assertIn("已核调用点 0", out)

    def test_arity_mismatch_is_counted_not_convicted(self):
        """实参个数与候选签名对不上 ⇒ 归 **`starred` 桶**（★ 只计数、★ **不判罪**）。

        ★★★ **2026-10-10（规格 301）订正：期望桶从 `arity` 改成 `starred`** ——
          ★★ **为什么**：★ 本夹具逐字是 `Int32 SomeMember(Int32&, Object)`、★ 调用传 **1** 个实参 ⇒
            `com = 1`、★ `counted_positions = 2` ⇒ ★★ **命中 `spec 271` 的窄规则**
            （★ `len(com) == 1` 且 最少计入形参 ≥2 且 ★ **缺的形参不全是 by-ref**）——
            ★ 缺的那个是 **`Object`（普通入参、不是 `&` 出参）** ⇒ ★★ **判 `starred`** ✓
          ★★★ **⇒ 这是 `spec 271` 的**正当**行为**（★ 它把 `starargs` 与 `real-gap` 分开了），
            ★ **不是缺陷** ⇒ ★ 本判据的**期望值**跟着改（★ `MEMORY.md` 规则 28：
            「改实现前先搜『有没有测试钉住旧行为』—— ★ 不同步改就等于**在断言错的东西**」）✓
        ★★ **判据的意图不变**：★ 「对不上就**只计数、不判罪**」⇒ ★ `[PASS]` + ★ **已核 0** ✓
        """
        tmp, dumps = self._tree("5", dump=FIXTURE_DUMP_ARITY2)
        rc, out = run_gate(tmp, dumps=dumps, baseline="0,0")
        self.assertEqual(rc, 0, out)
        #: ★★ **可观察量**：★ 本门禁**不打印** `starred` 桶名（★ 那是 `audit_byref_args` 层的分类），
        #:   它只把 `starred` **从 `arity` 桶里挪走** ⇒ ★★ 可观察的是：
        #:     ★ **`arity 不符 0`**（★ 不再算 arity）+ ★ **`[PASS]`**（★ **没判罪**）✓
        self.assertIn("arity 不符 0", out, "★ 应**不再**算作 `arity`（★ spec 271 的窄规则把它归 `starred`）")
        self.assertIn("[PASS]", out, "★ 只计数、★ 不判罪 ⇒ 必须 `[PASS]`")
        self.assertNotIn("[FAIL]", out)

    def test_zero_checked_with_nonzero_baseline_is_red(self):
        """★ 假绿守卫：下界非 0 而核了 0 个 ⇒ 红（解析器/取点失效不许 PASS）。"""
        src = DECL + """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj, name):
    return _dispatch(obj, name, 5)
"""
        tmp = make_tree({"scripts/sw_fixture.py": src, "dumps/iface_fixture.txt": FIXTURE_DUMP})
        rc, out = run_gate(tmp, dumps=str(tmp / "dumps" / "iface_fixture.txt"), baseline="0,1")
        self.assertEqual(rc, 1, out)
        self.assertIn("zero-checked", out)

    def test_missing_dumps_path_is_skip(self):
        """★★ 缺数据源：覆盖变量**显式指向不存在的路径** ⇒ `[SKIP]` + exit 0。"""
        tmp, _ = self._tree("5")
        rc, out = run_gate(tmp, dumps=str(tmp / "dumps" / "nonexistent.txt"), baseline="0,0")
        self.assertEqual(rc, 0, out)
        self.assertIn("[SKIP]", out)

    def test_no_raw_dir_is_skip(self):
        """★ 工作区里没有 `_raw/**` 且未给覆盖 ⇒ 也走 `[SKIP]`。"""
        tmp, _ = self._tree("5")
        rc, out = run_gate(tmp, baseline="0,0")
        self.assertEqual(rc, 0, out)
        self.assertIn("[SKIP]", out)


if __name__ == "__main__":
    unittest.main()

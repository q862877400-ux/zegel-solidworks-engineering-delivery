"""★ 判据：`check_dispatch_blindspot_guard.py` —— 分发口调用点的解析盲区（spec 232）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁的判据）
# 文件:   tests/test_dispatch_blindspot_guard.py
# 定位:   证 spec 232 的门禁 ① **真树读数**（362 已覆盖 · 5 形态全 0 · exit 0）、
#         ② **5 种盲区形态各自承重**（每形态一个合成树端到端负例 ⇒ exit 1）、
#         ③ **不是一律红**（只含现有三种形态的合成树 ⇒ exit 0）、
#         ④ **下界承重**（拔高下界即红）、⑤ **零检查守卫**。
# 官方依据: 无（纯 AST）。形态清单来自真树量测（`output/_probe232_blindspots.py`）。
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
GATE = ROOT / "scripts" / "check_dispatch_blindspot_guard.py"

#: ★★ **门禁自己的下界**（★ 单一真源 —— 见 `TestRealTree` 里的订正说明）。
sys.path.insert(0, str(ROOT / "scripts"))
import check_dispatch_blindspot_guard as _blindspot_gate          # noqa: E402

BASELINE_COVERED = _blindspot_gate.BASELINE_COVERED

#: 分发口骨架（成员名以形参 `member` 转发给 COM 包装器 `get_com_member`）。
ENTRY = """
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)
"""

#: ★ 基础夹具：**另含一个「已覆盖」调用点**（同文件裸名形态）。
#: ★★ 没有它，`covered == 0` 会让 `[zero-checked]` 先红 ⇒ 负例「**因错误的原因**」通过。
BASE = ENTRY + """

def covered_caller(obj):
    return _dispatch(obj, "SomeMember", 1)
"""


def run_gate(root: Path | None, *, baseline: str | None = None):
    env = dict(os.environ)
    for key, val in (("DSH_DISPATCH_BLINDSPOT_ROOT", str(root) if root else None),
                     ("DSH_DISPATCH_BLINDSPOT_BASELINE_MIN", baseline)):
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
    """⇒ 仓库**外**的临时树（★ 本仓多条判据以「临时目录在仓库外」为隐含前提）。"""
    tmp = Path(tempfile.mkdtemp(prefix="dsh232-"))
    for rel, text in files.items():
        p = tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    return tmp


def form_count(out: str, form: str) -> int:
    """⇒ 输出里形态 `form` 的计数。"""
    m = re.search(r"\(%s\).*?=\s*(\d+)\s*$" % re.escape(form), out, re.M)
    assert m is not None, out
    return int(m.group(1))


#: 五种盲区形态的「另一侧」源码（都调用 `sw_fixture._dispatch`）。
ALIAS_SOURCES = {
    "a": 'import sw_fixture as X\n\n\ndef use(o):\n    return X._dispatch(o, "SomeMember", 1)\n',
    "b": ('from sw_fixture import _dispatch as g\n\n\n'
          'def use(o):\n    return g(o, "SomeMember", 1)\n'),
    "c": ('import scripts.sw_fixture\n\n\n'
          'def use(o):\n    return scripts.sw_fixture._dispatch(o, "SomeMember", 1)\n'),
    "d": None,          #: 写在 sw_fixture.py **自己**里
    "e": ('import sw_fixture\n\n\n'
          'def use(o):\n    return getattr(sw_fixture, "_dispatch")(o, "SomeMember", 1)\n'),
}


class TestRealTree(unittest.TestCase):
    """真树读数（★ 防止判据变成空判据）。"""

    def test_real_tree_is_frozen_and_nonvacuous(self):
        rc, out = run_gate(None)
        self.assertEqual(rc, 0, out)
        #: ★★★ **2026-10-10（规格 301）订正：改成「实测 ≥ 下界」** ——
        #:   ★ **为什么是正当的**：★ 本判据的**意图**是「已覆盖调用点**不低于门禁钉的下界**」
        #:     ⇒ ★★ **原判据用 `assertIn` 把「下界」当成了「实际值」**（★ 两者**当时恰好同值** ⇒ 巧合）
        #:     ⇒ ★★ 真树**涨到 364** 后，`assertIn("已覆盖调用点 362")` 就**恒红**（★ 而"涨"是**好事**）。
        #:   ★★ **⇒ 正解：从输出里**解析实测值**，再与**下界**比** ✓
        #:   ★★ **依据**（`MEMORY.md` 规则 16）：「★ **别拿一个数去核另一个**」✓
        _m = re.search(r"已覆盖调用点 (\d+)", out)
        self.assertIsNotNone(_m, out)
        self.assertGreaterEqual(int(_m.group(1)), BASELINE_COVERED, out)
        self.assertIn("分发口 37 个", out)
        self.assertIn("违规 0", out)
        self.assertIn("[PASS]", out)

    def test_all_five_forms_are_zero_on_real_tree(self):
        """★★ 真树读数：5 种盲区形态**全部 = 0**（本切片的核心事实）。"""
        rc, out = run_gate(None)
        self.assertEqual(rc, 0, out)
        for form in "abcde":
            self.assertEqual(form_count(out, form), 0, "形态 %s 非 0：\n%s" % (form, out))

    def test_covered_baseline_shrink_is_red(self):
        """★ 下界承重：把下界抬到**实测 + 1** ⇒ 当场红。

        ★★ **2026-10-10（规格 301）改成**动态取实测值** —— ★ 原先硬写 `363`（★ 那时实测 362）。
          ★★ 真树已涨到 **364** ⇒ ★ 硬写的 `363` **不再承重**（★ 364 ≥ 363 ⇒ **不红**）
          ⇒ ★★ **判据静默失效**（★ 它本该证明「下界承重」）⇒ ★ 改成 `实测 + 1` ⇒ **涨多少都不失效** ✓
        """
        rc0, out0 = run_gate(None)
        self.assertEqual(rc0, 0, out0)
        actual = int(re.search(r"已覆盖调用点 (\d+)", out0).group(1))
        rc, out = run_gate(None, baseline=str(actual + 1))
        self.assertEqual(rc, 1, out)
        self.assertIn("baseline-shrunk", out)
        self.assertIn("已覆盖调用点 %d < 下界 %d" % (actual, actual + 1), out)


class TestSyntheticTrees(unittest.TestCase):
    """合成树端到端（★ 夹具只含被测对象 + 一个已覆盖调用点）。"""

    def test_each_form_is_load_bearing(self):
        """★★★ **核心负例**：5 种形态**各自**都能把门禁弄红（不是只证一种）。"""
        for form, src in ALIAS_SOURCES.items():
            with self.subTest(form=form):
                if form == "d":
                    files = {"scripts/sw_fixture.py":
                             BASE + '\n\ndef self_dotted(obj):\n'
                                    '    return sw_fixture._dispatch(obj, "SomeMember", 1)\n'}
                else:
                    files = {"scripts/sw_fixture.py": BASE, "scripts/other.py": src}
                tmp = make_tree(files)
                rc, out = run_gate(tmp, baseline="0")
                self.assertEqual(rc, 1, "形态 %s 未红：\n%s" % (form, out))
                self.assertIn("[blindspot]", out)
                self.assertEqual(form_count(out, form), 1, out)
                #: ★ 红的原因必须是盲区，不是零检查（否则是「因错误的原因通过」）。
                self.assertNotIn("zero-checked", out)

    def test_covered_only_tree_is_green(self):
        """★ 门禁**不是**一律红：只含现有三种形态 ⇒ `exit 0`。"""
        tmp = make_tree({"scripts/sw_fixture.py": BASE + """

def cross_file(obj):
    return _dispatch(obj, "SomeMember", 1)
"""})
        rc, out = run_gate(tmp, baseline="0")
        self.assertEqual(rc, 0, out)
        self.assertIn("违规 0", out)
        self.assertIn("[PASS]", out)

    def test_zero_covered_is_red(self):
        """★ 假绿守卫：有分发口但一个调用点都取不到 ⇒ `[zero-checked]` 红。"""
        tmp = make_tree({"scripts/sw_fixture.py": ENTRY})
        rc, out = run_gate(tmp, baseline="0")
        self.assertEqual(rc, 1, out)
        self.assertIn("zero-checked", out)

    def test_getattr_on_other_module_is_not_a_blindspot(self):
        """★★ 形态 e 的**假阳性边界**：`getattr(<别的对象>, "_dispatch")()` 不算盲区。

        ★ 理由：`_checked` / `_num` / `_read` 这类入口在**多个模块重名** ——
        松判定会把无关对象的 `getattr` 全算进来（spec 229 教训：裸名索引会合并同名 `def`）。
        """
        src = ('import other_mod\n\n\n'
               'def use(o):\n    return getattr(other_mod, "_dispatch")(o, 1)\n')
        tmp = make_tree({"scripts/sw_fixture.py": BASE, "scripts/other.py": src})
        rc, out = run_gate(tmp, baseline="0")
        self.assertEqual(rc, 0, out)
        self.assertEqual(form_count(out, "e"), 0, out)


if __name__ == "__main__":
    unittest.main()

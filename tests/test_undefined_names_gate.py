"""★ 未定义名门禁的契约：判据、两类跳过、注解不算读、以及**负例自证**。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_undefined_names_gate.py
# 定位:   ★ 2026-10-03（轮 404）24h 计划 v2 收敛报告 §五 第 ⑤ 条的配套测试。
#   ★★ 被锁的判据（**每条都配反例**，★ 因为"门禁写了≠门禁有效"—— 事实 62）：
#     ① ★ 名字在**全文件**没绑定过却被读 ⇒ **必须报**（★ 这正是不导入的形态）；
#     ② ★ `globals().update(...)` / `import *` ⇒ **整份跳过**（★ 名字来源看不见）；
#     ③ ★ **注解里的名字不算读**（★ Python 3.14 起注解惰性，PEP 649）；
#     ④ ★ `KNOWN_BROKEN` 的条目**只 WARN 不拦**（★ 而它必须**写清理由**）。
# 官方依据: Python 语言作用域规则 · PEP 649（惰性注解）· `ast` 标准库。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_undefined_names as C                                  # noqa: E402


def _scan(tmp_path: Path, src: str) -> list:
    p = tmp_path / "sample.py"
    p.write_text(src, encoding="utf-8")
    return C.scan_file(p)


def test_reports_a_name_never_bound_anywhere(tmp_path: Path) -> None:
    """★ ① **本门禁存在的理由**：不导入就用的名字必须被报出来。

    ★ 形态取自**轮 403 的真 bug**（`export_to_image` 用了 `out_i4()` 而模块漏了导入）。"""
    hits = _scan(tmp_path, "def f():\n    return out_i4()\n")
    assert [h[2] for h in hits] == ["out_i4"], "全文件没绑定过的名字必须被报出来"


def test_does_not_report_a_bound_name(tmp_path: Path) -> None:
    """★ 反例：绑过了就不许报（★ 否则门禁会变成噪音）。"""
    assert _scan(tmp_path, "def out_i4():\n    return 0\n\n\ndef f():\n    return out_i4()\n") == []
    assert _scan(tmp_path, "import os\n\n\ndef f():\n    return os.getcwd()\n") == []
    assert _scan(tmp_path, "def f(x):\n    return x\n") == []


def test_skips_dynamic_global_injection(tmp_path: Path) -> None:
    """★★ ② 真例：`mcp-server/server.py` 的 `globals().update(exports)` ——

    ★ 那 100+ 个名字**在静态源码里根本不存在** ⇒ ★ 不跳过会假阳性 **300+ 处**
    （★ 而那个文件明明能跑）。"""
    src = ("def _inject():\n    exports = {'a': 1}\n    globals().update(exports)\n\n\n"
           "def f():\n    return connect_solidworks()\n")
    assert _scan(tmp_path, src) == [], "动态注入全局的文件必须整份跳过"
    assert _scan(tmp_path, "def f():\n    globals()['x'] = 1\n    return y\n") == []


def test_skips_star_import(tmp_path: Path) -> None:
    """★ ② 的另一半：`from x import *` ⇒ 名字来源看不见 ⇒ 整份跳过。"""
    assert _scan(tmp_path, "from os import *\n\n\ndef f():\n    return getcwd()\n") == []


def test_annotations_are_not_reads(tmp_path: Path) -> None:
    """★★ ③ Python 3.14 起注解**惰性**（PEP 649）⇒ 注解里的未定义名**不会** NameError。"""
    assert _scan(tmp_path, "def f(x: Nope) -> AlsoNope:\n    return x\n") == []


def test_known_broken_entries_are_not_gating_but_are_documented() -> None:
    """★★ ⓓ `KNOWN_BROKEN` 是**白名单而不是修复** —— 而它现在是**空的**。

    ★★★ 2026-10-03（轮 431）唯一那条（`scripts/sw_selection_tx.py`）**已按决断删除**：
      它要管理的 `AccessSelections` 在本机后端上**调不通**（**事实 47**）⇒ 补全了也没用；
      而**无任何模块导入它**。
    ★ 而**本测试保留的契约**（★ 它本来就写着）：
      ⓐ 名单里每条**都必须有**那个文件（★ 删了文件就该删名单）；
      ⓑ 每条理由都要够长（★ 空理由等于静默豁免）。
    """
    for path, why in C.KNOWN_BROKEN.items():
        assert len(why) > 60, "%s 的理由太短 ⇒ 等于静默豁免" % path
        assert (ROOT / path).exists(), "%s 不存在了 ⇒ 名单该删掉它" % path
def test_gate_is_wired_and_classified() -> None:
    """★ 门禁必须**接线**且**登记分类**（★ 那是 `check_gate_wiring.py` 的两条硬要求）。"""
    rc = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")
    assert "_run_undefined_names_gate" in rc
    assert 'str(ROOT / "scripts" / "check_undefined_names.py")' in rc
    assert '"undefined_names": undef' in rc, "★ 结果必须进 `_gate_results`（否则静默跳过看不见）"

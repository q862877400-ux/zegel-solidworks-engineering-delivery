"""★ 测「负例输入自证」门禁（`scripts/check_negative_input_selfproof.py`）—— ★ 含**负例**（事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_negative_input_selfproof_gate.py
# 定位:   ★ 2026-10-07（接手轮）：本道闸对 `tools/verify_union_349.py:112` 报了**假阳性** ——
#           `d = base / name.replace("：", "_")` **不是造负例输入**，而是给负例**目录名**消毒；
#           ★ 真正的坏输入由下一行 `write_all(d, **kw)` 的实参造出来 ✓
#         ★★ 处置 = 给门禁加**带非空理由的显式豁免**标记 `negproof-exempt: <理由>` ✓
#         ★★★ 事实 62：「一个门禁「写了」不等于它「有效」—— **负例测试是唯一的证明**」⇒
#           本测试**必须**同时钉住两件事：
#             ① ★ **豁免不能变成后门** —— ★ `negproof-exempt:` **理由为空**时**不生效** ✓
#             ② ★ **原判据不能被放松** —— ★ 没有标记、又没有自证的那一类**仍然要报** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_negative_input_selfproof as gate                            # noqa: E402

#: ★ 天真的「变换 + 负例名下 + 无自证」样本 —— ★ 这是**必须被抓**的形态（轮 84 那件事）✓
BAD_SRC = """\
def build():
    for name in ("负例①", "负例②"):
        text = template.replace("TABLE", "")
        write_broken(name, text)
"""

#: ★ 同一段，但**给了带理由的豁免** ⇒ ★ 不应再报 ✓
EXEMPT_SRC = """\
def build():
    for name in ("负例①", "负例②"):
        # negproof-exempt: 这里只是给负例目录名消毒，坏输入由下一行走参数造出来
        path = "/tmp/" + name.replace("：", "_")
        write_broken(name, path)
"""

#: ★★ **后门样本**：标记在、★ **理由为空** ⇒ ★ **必须仍然报** ✓
EMPTY_REASON_SRC = """\
def build():
    for name in ("负例①", "负例②"):
        # negproof-exempt:
        text = template.replace("TABLE", "")
        write_broken(name, text)
"""

#: ★ 自证样本（原判据的正例）⇒ ★ 不报 ✓
PROVED_SRC = """\
def build():
    for name in ("负例①", "负例②"):
        text = template.replace("TABLE", "")
        assert text != template, "变换没生效"
        write_broken(name, text)
"""


def _write(tmp_path: Path, src: str) -> Path:
    p = tmp_path / "probe_fixture.py"
    p.write_text(src, encoding="utf-8")
    return p


def test_unproved_transform_is_reported(tmp_path: Path) -> None:
    """★★ **负例**（事实 62）：★ 「变换造负例输入、且没有自证」⇒ **必须报** ✓"""
    hits = gate.scan(_write(tmp_path, BAD_SRC))
    assert hits, "★ 无自证的负例变换没有被抓到 ⇒ 门禁抓不到它真正要抓的东西"
    assert hits[0][2] is False, "★ 该条不该被判成「自证」：%r" % (hits,)
    assert hits[0][3] is None, "★ 该条没有豁免标记：%r" % (hits,)


def test_proved_transform_is_not_reported(tmp_path: Path) -> None:
    """★ 正例：★ 有 `assert ... != ...` 自证 ⇒ 不报 ✓"""
    hits = gate.scan(_write(tmp_path, PROVED_SRC))
    assert hits and hits[0][2] is True, "★ 自证的应当被认下：%r" % (hits,)


def test_exempt_with_reason_is_accepted(tmp_path: Path) -> None:
    """★ 带**非空理由**的 `negproof-exempt:` ⇒ 认下、且**回传理由**（★ 可审计）✓"""
    hits = gate.scan(_write(tmp_path, EXEMPT_SRC))
    assert hits, "★ 样本本身应当落在判据里（否则这条测试是空转）"
    assert hits[0][2] is False, "★ 它本来就没有自证 ⇒ `proved` 应为 False"
    assert hits[0][3], "★ 豁免理由没被读回来：%r" % (hits,)
    assert "消毒" in hits[0][3], "★ 理由要逐字带回：%r" % (hits,)


def test_exempt_without_reason_is_a_backdoor(tmp_path: Path) -> None:
    """★★★ **后门负例**：★ 标记在、**理由为空** ⇒ ★ **必须仍然报**（★ 否则豁免变成万能通行证）✓"""
    hits = gate.scan(_write(tmp_path, EMPTY_REASON_SRC))
    assert hits, "★ 样本本身应当落在判据里"
    assert hits[0][3] is None, "★ 空理由**不许**被当成豁免：%r" % (hits,)


def test_gate_passes_on_current_tree() -> None:
    """★ 正例：★ 真仓当前的 `tools/` 应当**全绿**（`verify_union_349.py` 已带理由豁免）✓"""
    assert gate.main() == 0, "★ 真仓里还有「未自证」的负例变换 ⇒ 见门禁输出"

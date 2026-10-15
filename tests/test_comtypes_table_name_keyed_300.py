"""★ 规格 300 判据：`COMTYPES_CALL_SITES` 的键必须是**成员名** —— ★ 加注释不得再让它失配。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/audit_call_arity.py`（★ `COMTYPES_CALL_SITES` · `audit()`）
#         `tests/test_arity_comtypes_classification.py`（★ 原判据：断言 `("sw_delivery.py", 671)`）
#         `MEMORY.md` 规则 32（★ 「证据表不许钉行号」—— 本规格的**依据**）
# 定位:   ★★ 起因：★ **同一形态第三次** —— 工作树里给 `sw_delivery.py:248` 加一行注释
#         ⇒ ★ 671/965 各 **+1** 漂到 672/966 ⇒ ★ 那条测试报「应当恰好 2 条 comtypes，★ 实际 0」✗
#         ★★★ 前两次（轮 87/115 与轮 116）都是**改行号** ⇒ ★ 那只是把下一次漂移往后推
#         ⇒ ★★ 本轮做表注释里自己写的「更稳的做法」：★ **按成员名登记**。
# 官方依据: 不适用（本项目内部纪律）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读 + 临时副本（★ `tmp_path` 在仓库外）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import audit_call_arity as ac          # noqa: E402

DELIVERY = ROOT / "scripts" / "sw_delivery.py"
RAW = Path(r"D:\AI\SW\_raw")

#: ★★ 两条登记项（★ 按**成员名** —— 那正是本规格要钉的形态）
EXPECTED = {("sw_delivery.py", "IGetDocumentNames"), ("sw_delivery.py", "OpenDoc6")}


def _refs():
    return [str(p) for p in RAW.rglob("iface_*.txt")]


def test_the_table_is_keyed_by_member_not_line():
    """★★★ FR-001：表的键必须是**成员名**。

    ★★ 依据（`MEMORY.md` 规则 32 逐字）：「★★★ **证据表不许钉行号**」。
    """
    keys = set(ac.COMTYPES_CALL_SITES)
    assert EXPECTED <= keys, (
        "★ 表里缺 %r ⇒ ★ 键可能还是行号" % sorted(EXPECTED - keys))
    bad = [(f, m) for (f, m) in keys if isinstance(m, int)]
    assert not bad, (
        "★★ 表里仍有**按行号**登记的键 %r —— ★ 加一行注释就会漂（★ 那正是本规格要消掉的形态）" % bad)


def test_adding_a_comment_does_not_break_it(tmp_path):
    """★★★ FR-002（★ **本规格的根本判据**）：★ 在文件里**插入若干行** ⇒ ★ 审计**仍**认出那两条。

    ★ 做法：★ 把 `sw_delivery.py` 拷到**仓库外**的临时目录、★ **在开头插 5 行注释**、
      ★ 再用**同一个** `audit()` 跑它 ⇒ ★★ **comtypes 组必须仍是 2 条**。
    ★★ 为什么用临时副本：★ 改真树会污染工作树（★ 且本仓纪律禁止乱改既有文件）。
    """
    refs = _refs()
    if not refs or not DELIVERY.is_file():
        import pytest
        pytest.skip("缺反射转储或目标文件")

    work = tmp_path / "sw_delivery.py"
    shutil.copy2(DELIVERY, work)
    original = work.read_text(encoding="utf-8")
    #: ★★ 在**文件开头**插 5 行注释 ⇒ ★ 所有行号 **+5**（★ 远超那 +1 的漂移量）
    patched = "\n".join("# 注入的注释行 %d" % i for i in range(5)) + "\n" + original
    work.write_text(patched, encoding="utf-8")

    _ok, _doubt, _missing, _dynamic, comtypes = ac.audit(str(work), refs)
    assert len(comtypes) == 2, (
        "★★★ 插入 5 行后 comtypes 组变成 %d 条（★ 应是 2）⇒ ★ 键**仍然是行号**"
        "（★ 那正是本规格要消掉的失配形态）" % len(comtypes))


def test_audit_finds_both_sites():
    """★★★ FR-003：**端到端**真跑 `audit()` ⇒ ★ 两条都落进 `comtypes` 组（★ 不是只看表）。"""
    refs = _refs()
    if not refs or not DELIVERY.is_file():
        import pytest
        pytest.skip("缺反射转储或目标文件")
    _ok, _doubt, _missing, _dynamic, comtypes = ac.audit(str(DELIVERY), refs)
    members = {m for (_ln, m, _argc, _r) in comtypes}
    assert members == {"IGetDocumentNames", "OpenDoc6"}, (
        "★ comtypes 组的成员是 %r（★ 应是那两条）" % sorted(members))


def test_reasons_survive_the_rekeying():
    """★★ FR-004：★ 改键**不许**把理由弄丢（★ 理由才是这张表存在的意义）。"""
    for key, reason in ac.COMTYPES_CALL_SITES.items():
        assert len(reason) > 60, "%s 的理由太短: %r" % (key, reason)
        assert "comtypes" in reason, "%s 的理由要点明 comtypes" % (key,)
        assert "不是缺陷" in reason or "不缺陷" in reason, (
            "%s 的理由没写**定性**（★ 读者要知道「它不是 bug」）" % (key,))


def test_bucket_order_is_unchanged():
    """★★ FR-005：★ 边界冻结 —— `audit()` 的**四桶分流顺序**未变（★ 只改了键）。

    ★ 顺序逐字（★ 来自实现）：★ `comtypes` 先判（★ 已知站点）⇒ `dynamic` ⇒ `missing`
      ⇒ `ok` ⇒ 否则 `doubt`。
    ★★ 判据：★ `IGetDocumentNames`（★ 官方 arity 2、★ 调用只传 1）**必须**落进 `comtypes`
      —— ★ 若它落进 `doubt` ⇒ ★ 说明「先判 comtypes」那一步被挪到后面去了。
    """
    refs = _refs()
    if not refs or not DELIVERY.is_file():
        import pytest
        pytest.skip("缺反射转储或目标文件")
    _ok, doubt, _missing, _dynamic, comtypes = ac.audit(str(DELIVERY), refs)
    doubt_members = {d[1] for d in doubt}
    assert "IGetDocumentNames" not in doubt_members, (
        "★ `IGetDocumentNames` 落进了 `doubt` ⇒ ★ 「先判 comtypes」那一步的顺序被改了")
    assert "OpenDoc6" not in doubt_members, "★ `OpenDoc6` 落进了 `doubt` ⇒ 同上"

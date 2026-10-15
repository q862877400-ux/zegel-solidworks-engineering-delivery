"""★ 规格 315 的门禁契约测试：语料校验 + 反向验证（负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_corpus_315.py
# 定位:   规格 `specs/315-eval-corpus` 的 FR-010/FR-011 的契约测试
# 官方依据: `tools/check_corpus.py`（门禁本体）· `corpus/*.yaml`（被校验对象）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

import yaml                                                             # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "check_corpus", ROOT / "tools" / "check_corpus.py")
cc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cc)


def test_corpus_files_exist() -> None:
    """三份语料都在。"""
    for n in ("l1-mainline", "l2-longtail", "l3-semantic"):
        assert (ROOT / "corpus" / ("%s.yaml" % n)).is_file(), n


def test_corpus_passes_gate() -> None:
    """★ 语料必须通过门禁（0 处问题）。"""
    problems = cc.check(ROOT)
    assert problems == [], "语料有问题：%s" % problems[:10]


def test_gate_selftest_passes() -> None:
    """★ 门禁的反向验证必须通过（10 例）。"""
    assert cc.selftest() is True


def test_l1_counts() -> None:
    """L1 = 60 条，6 类产品各 10 条。"""
    l1 = cc.load(ROOT / "corpus" / "l1-mainline.yaml")
    assert len(l1) == 60, len(l1)
    import collections
    pc = collections.Counter(x["product_class"] for x in l1)
    assert set(pc) == set(cc.PRODUCT_CLASSES), pc
    assert all(v == 10 for v in pc.values()), pc


def test_l2_covers_all_task_groups() -> None:
    """★ L2 必须覆盖全部工程任务组。"""
    l2 = cc.load(ROOT / "corpus" / "l2-longtail.yaml")
    surf = cc.tool_surface()
    task_groups = {g for g in cc.groups_of(surf) if g not in cc.INFRA}
    covered = {x["target_group"] for x in l2}
    assert task_groups <= covered, "未覆盖：%s" % sorted(task_groups - covered)


def test_l3_distribution() -> None:
    """L3 = 60 条，类别 24/12/12/12，分组 20/40。"""
    import collections
    l3 = cc.load(ROOT / "corpus" / "l3-semantic.yaml")
    assert len(l3) == 60
    assert dict(collections.Counter(x["category"] for x in l3)) == cc.CATEGORY_PLAN
    assert dict(collections.Counter(x["split"] for x in l3)) == cc.SPLIT_PLAN


def test_all_tool_names_are_real() -> None:
    """★ 所有引用的工具名都必须在真实工具面上（★ 这是语料的锚点）。"""
    surf = cc.tool_surface()
    bad: list[str] = []
    for f, key in (("l1-mainline", "tools"), ("l2-longtail", "tools")):
        for x in cc.load(ROOT / "corpus" / ("%s.yaml" % f)):
            for chain in (x.get(key) or []):
                for t in (chain or []):
                    if t not in surf:
                        bad.append("%s/%s: %s" % (f, x.get("id"), t))
    assert bad == [], bad


def test_every_item_declares_owner_judgment() -> None:
    """★ 每条都必须声明 needs_owner_judgment（★ 不许静默冒充定论）。"""
    for f in ("l1-mainline", "l2-longtail", "l3-semantic"):
        for x in cc.load(ROOT / "corpus" / ("%s.yaml" % f)):
            assert "needs_owner_judgment" in x, "%s/%s" % (f, x.get("id"))


def test_gate_catches_broken_corpus() -> None:
    """★ 反向验证（独立复现）：故意改坏一份语料，门禁必须报错。"""
    import tempfile
    base1 = cc.load(ROOT / "corpus" / "l1-mainline.yaml")
    base2 = cc.load(ROOT / "corpus" / "l2-longtail.yaml")
    base3 = cc.load(ROOT / "corpus" / "l3-semantic.yaml")
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        (t / "corpus").mkdir()
        b1 = [dict(x) for x in base1]
        b1[0]["tools"] = [["solidworks_根本不存在的工具"]]
        for n, d in (("l1-mainline", b1), ("l2-longtail", base2),
                     ("l3-semantic", base3)):
            (t / "corpus" / ("%s.yaml" % n)).write_text(
                yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")
        assert len(cc.check(t)) > 0, "改坏了语料却没报错 ⇒ 门禁是废的"

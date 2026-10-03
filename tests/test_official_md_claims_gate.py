"""★ 门禁 `check_official_md_claims.py` 的负例测试 —— ★ 用**修复前的原文**当输入。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁的负例测试）
# 文件:   tests/test_official_md_claims_gate.py
# 定位:   ★ 2026-10-03（接手轮）★ 事实 62 的落点：★ **门禁"写了"不等于"有效"**，
#   ★ 唯一的证明是**拿它去抓那个真实的 bug**。
#
#   ★★★ **负例输入取自修复前的原文**（★ 不是手写一个"像 bug 的样本"——
#     ★ 那是事实 62 明确否掉的弱做法）：
#     ```
#     git show 9db64e7:scripts/sw_curve_and_split.py
#       ⇒ "selection_mark": "★ 官方 Remarks **未给** mark 表 —— 本模块不假定",
#       ⇒     ⚠ ★ 调用前要有**可选的分割工具**（草图 / 曲线 / 面）—— ★ 官方**没给 mark 表**，
#     ```
#     ★ 而官方页 `C:\swapi\types\IModelDoc2\InsertSplitLineProject.md` 的 `## Remarks` 里有：
#       "…with a mark value of **4**." / "…with mark values of **1**."
#
#   ⚠ 需要本机官方源（`C:\swapi`）⇒ 缺了就 **skip 并写明原因**（★ 不假装通过）。
#   ⚠ **不连 SolidWorks、不依赖 `mcp` 库**（★ 本测试是纯静态的）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_official_md_claims as G                                   # noqa: E402

pytestmark = pytest.mark.skipif(
    not (Path(r"C:\swapi") / "types").is_dir(),
    reason="官方源 C:\\swapi 不在本机 ⇒ 门禁本身会 SKIP，本测试无从判定",
)

#: ★★ **修复前的原文**（`git show 9db64e7:scripts/sw_curve_and_split.py`，逐字）
PREFIX_BUG = '''\
def insert_split_line_project(model, is_directional=False, flip_dir=False):
    """★ **分割线（投影）**：`IModelDoc2.InsertSplitLineProject(IsDirectional, FlipDir)`。

    ⚠ ★ 调用前要有**可选的分割工具**（草图 / 曲线 / 面）—— ★ 官方**没给 mark 表**，
      ★ 故本模块**不假定 mark**，如实把这一点写进返回值。
    """
    return {"ok": False,
            "selection_mark": "★ 官方 Remarks **未给** mark 表 —— 本模块不假定",
            "verified_by": "tree_delta"}
'''

#: ★ 修复后的形态（★ 写明官方真的给了 mark）
FIXED = '''\
def insert_split_line_project(model, is_directional=False, flip_dir=False):
    """★ 投影型分割线 —— 官方 `## Remarks` 逐字给了 mark 表：草图 4 · 面 1。"""
    return {"selection_mark": "官方 Remarks 逐字：草图 mark = 4 · 面 mark = 1"}
'''

#: ★ 一个"官方确实没给 mark"的真断言 ⇒ **不该**被报（假阳性对照）
TRUE_CLAIM = '''\
def insert_revolved_ref_surface(model, angle):
    """★ 旋转曲面 `IFeatureManager.InsertRevolvedRefSurface`。

    ★ 官方 `## Remarks` 只说要先用 `SelectByID2` 选 —— ★ 而**没给 mark**
      ⇒ ★ 本模块**不假定 mark**。
    """
    return {"selection_mark": "官方 Remarks 未给 mark"}
'''


def _scan(tmp_path: Path, filename: str, source: str):
    """★ 把源码放进临时树、改指 `REPO`，跑门禁的扫描（★ 不动真仓库）。"""
    d = tmp_path / "scripts"
    d.mkdir(parents=True, exist_ok=True)
    (d / filename).write_text(source, encoding="utf-8")
    old_repo, old_dirs = G.REPO, G.SCAN_DIRS
    G.REPO, G.SCAN_DIRS = tmp_path, ("scripts",)
    try:
        return G.scan()
    finally:
        G.REPO, G.SCAN_DIRS = old_repo, old_dirs


def test_gate_catches_the_real_prefix_bug(tmp_path):
    """★★ 事实 62 的核心：**拿修复前的原文**跑门禁 ⇒ 必须报出那一条。"""
    violations, total, unresolved, _quoted, _ex = _scan(tmp_path, "x.py", PREFIX_BUG)
    assert total >= 1, "门禁没扫到任何断言 ⇒ 判据坏了"
    assert violations, "★ 门禁**抓不到真 bug** ⇒ 这道门禁无效（事实 62）"
    joined = " ".join(v["claim"] for v in violations)
    assert "未给" in joined or "没给" in joined
    #: ★ 主语要认对（★ 否则修法会指错地方）
    assert any(v["member"] == "InsertSplitLineProject" for v in violations), \
        "主语认错了：%r" % [v["member"] for v in violations]
    #: ★ 官方页里的原文要带回来（★ 让人一眼看到"页里其实有"）
    assert any("mark value of 4" in v["page_says"] for v in violations)


def test_gate_passes_on_the_fixed_text(tmp_path):
    """★ 修复后的写法**不该**被报（★ 否则门禁是在逼人删掉正确信息）。"""
    violations, total, _u, _q, _ex = _scan(tmp_path, "x.py", FIXED)
    assert total == 0 or not violations, violations


def test_gate_does_not_flag_a_true_claim(tmp_path):
    """★ 假阳性对照：★ `InsertRevolvedRefSurface` 官方**确实没有** mark ⇒ 不该报。"""
    violations, _t, _u, _q, _ex = _scan(tmp_path, "x.py", TRUE_CLAIM)
    assert not violations, violations


def test_retracted_quote_is_not_a_live_claim(tmp_path):
    """★ 「我已撤回」的引述不算活断言 —— ★ 否则**记下自己的错**反而会被门禁挡。"""
    src = "# ★★ 此前这里逐字写着：官方**没给 mark 表** —— 那句是错的\n" \
          "def f():\n" \
          "    \"\"\"InsertSplitLineProject 的 mark 表见官方页。\"\"\"\n" \
          "    return 1\n"
    violations, total, _u, quoted, _ex = _scan(tmp_path, "x.py", src)
    assert total == 1 and quoted == 1
    assert not violations, violations


def test_ambiguous_subject_is_skipped_not_flagged(tmp_path):
    """★ 窗口内**两个**合法主语 ⇒ **跳过并计数**（★ 不猜、也不报）——
    ★ 这条是防假阳性的关键：猜错主语会把**对的断言**报成违规。

    ⚠ 第一版这里我写错了：★ 用 `SelectByID2` + `InsertSplitLineProject` 造"歧义"，
      ★ 而 `SelectByID2` 在 `SUBJECT_EXCLUDE` 里 ⇒ 过滤后**只剩一个**主语
      ⇒ ★ 门禁**唯一地**解析到了 `InsertSplitLineProject`（★ 比我以为的更准）。
      ⇒ ★ 真正要造歧义，得放**两个都不在排除表里**的成员。
    """
    src = ("# 见 InsertSplitLineProject 与 InsertSplitLineSil 两处\n"
           "x = 1  # ★ 官方没给 mark 表\n")
    violations, total, unresolved, _q, _ex = _scan(tmp_path, "x.py", src)
    assert total == 1 and unresolved == 1
    assert not violations, violations


def test_excluded_member_is_never_the_subject(tmp_path):
    """★ `SelectByID2` **签名里就有 `Mark`** ⇒ 对它说"官方没给 mark"是自相矛盾
    ⇒ ★ 它被排除出主语候选，★ 于是同一行里剩下的 `InsertSplitLineProject` 被**唯一**认出。"""
    src = ("# 见 IModelDocExtension.SelectByID2 与 IModelDoc2.InsertSplitLineProject\n"
           "x = 1  # ★ 官方没给 mark 表\n")
    violations, total, unresolved, _q, _ex = _scan(tmp_path, "x.py", src)
    assert total == 1 and unresolved == 0
    assert [v["member"] for v in violations] == ["InsertSplitLineProject"]

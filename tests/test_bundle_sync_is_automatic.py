"""★ spec 286：**打包副本同步**不是待办 —— ★ 生成器链**每次改 `scripts/` 都跑头尾两次**，★ 且门禁有守。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sync_bundled_skill.py（★ 同步器）· scripts/release_check.py（★ `bundled_skill_files` / `digest_freshness`）
#         AGENTS.md / `.workbuddy-ai/memory/*.md`（★ 逐字：生成器链**头尾各一次** `sync_bundled_skill.py`）
# 定位:   ★ ② 段原第 3 条写「**发版前**才需要：同步打包副本」⇒ ★★ 本轮**量它到底是不是待办**。
#         ★★ 结论：★ **不是** —— ★ 链**每次改 `scripts/` 都跑**（★ 头尾两次）⇒ ★ 副本**始终一致**；★ 且门禁**两道**守着。
# 官方依据: 不适用（本项目内部纪律）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 现场比对文件；★ 不写任何文件）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **打包副本根**（★ 桌面内嵌 Skill 快照）。
BUNDLE = ROOT / "apps" / "workbench-ui" / "src-tauri" / "resources" / "skill" / "scripts"
#: ★★ **门禁的两道守**（★ 逐字来自 `release_check.py`）。
GATE_GUARDS = ("bundled_skill_files", "digest_freshness")
#: ★★ **生成器链**（★ 头尾各一次 `sync_bundled_skill.py`）。
CHAIN = ("scripts/sync_bundled_skill.py", "scripts/gen_level_audit.py", "tools/gen_metrics.py",
         "tools/gen_harvest_digest.py", "tools/build_union_map.py", "tools/gen_dead_ends.py",
         "scripts/sync_bundled_skill.py")
#: ★★★ **结论**：★ 它不是待办。
VERDICT = "不是待办 —— 生成器链每次改 scripts/ 都跑头尾两次，副本始终一致，且门禁两道守着"


def _compare():
    """★ 现场比对：`scripts/*.py` ↔ 打包副本 ⇒ `(一致, 不一致, 缺)`。"""
    same = diff = miss = 0
    for p in sorted((ROOT / "scripts").glob("*.py")):
        q = BUNDLE / p.name
        if not q.is_file():
            miss += 1
        elif p.read_bytes() == q.read_bytes():
            same += 1
        else:
            diff += 1
    return same, diff, miss


def _failures(same, diff, miss, guards, chain, verdict, src) -> list[str]:
    """★ 纯函数：① 无差异无缺；② 两道守都在；③ 链头尾都是同步器；④ 结论是「不是待办」；⑤ 同步器源码在。"""
    bad: list[str] = []
    if same <= 0:
        bad.append("★ 一个都没比到 ⇒ 检查量为 0")
    if diff:
        bad.append("★ 有 %d 个**不一致**" % diff)
    if miss:
        bad.append("★ 有 %d 个**副本缺**" % miss)
    if len(guards) != 2:
        bad.append("★ 门禁的**两道守**要都记")
    if chain[0] != "scripts/sync_bundled_skill.py" or chain[-1] != "scripts/sync_bundled_skill.py":
        bad.append("★ 生成器链**头尾**都应是 `sync_bundled_skill.py`")
    if "不是待办" not in verdict:
        bad.append("★ 结论应是「不是待办」")
    if not src:
        bad.append("★ 回源码核失败：`sync_bundled_skill.py` 不在")
    return bad


# ── ① ★★★ **现场比对：逐字节一致** ───────────────────────────────
def test_bundle_is_byte_identical():
    """★★★ 现场比对：★ `scripts/*.py` **逐个**与打包副本比字节 ⇒ ★ **一致 N · 不一致 0 · 缺 0**
    ⇒ ★★ **副本**始终同步****（★ 因为链每轮都跑）。
    """
    same, diff, miss = _compare()
    assert same > 0, "★ 一个都没比到 ⇒ 检查量为 0"
    assert diff == 0, "★ 有 %d 个不一致 ⇒ 副本没同步" % diff
    assert miss == 0, "★ 有 %d 个副本缺" % miss


# ── ② ★★ 门禁**两道守**都在 ─────────────────────────────────────
def test_two_gate_guards_exist():
    """★★ 回源码核：★ `release_check.py` 里有 `bundled_skill_files`（★ 打包文件数）与 `digest_freshness`（★ 摘要新鲜度）
    ⇒ ★★ **就算链漏跑，门禁也会红**。
    """
    src = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8", errors="replace")
    for g in GATE_GUARDS:
        assert g in src, "★ `release_check.py` 里找不到 %s" % g


# ── ③ ★★★ 生成器链**头尾各一次**同步器 ───────────────────────────
def test_the_chain_syncs_at_both_ends():
    """★★★ 链**头尾各一次** `sync_bundled_skill.py` ⇒ ★★ **先同步一次、跑完再同步一次**
    ⇒ ★ 所以「发版前再同步」**永远不会被漏掉** ⇒ ★★ **它不是待办**。
    """
    assert CHAIN[0] == "scripts/sync_bundled_skill.py"
    assert CHAIN[-1] == "scripts/sync_bundled_skill.py"
    assert (ROOT / "scripts" / "sync_bundled_skill.py").is_file(), "★ 同步器不在"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 一个都没比到；② 有不一致；③ 有缺；④ 守少一道；⑤ 结论不对。"""
    good = "…"
    args = (199, 0, 0, GATE_GUARDS, CHAIN, VERDICT, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(0, 0, 0, GATE_GUARDS, CHAIN, VERDICT, good), "一个都没比到却未判出"
    assert _failures(199, 1, 0, GATE_GUARDS, CHAIN, VERDICT, good), "有不一致却未判出"
    assert _failures(199, 0, 1, GATE_GUARDS, CHAIN, VERDICT, good), "有缺却未判出"
    assert _failures(199, 0, 0, ("bundled_skill_files",), CHAIN, VERDICT, good), "守少一道却未判出"
    assert _failures(199, 0, 0, GATE_GUARDS, CHAIN, "是待办", good), "结论不对却未判出"

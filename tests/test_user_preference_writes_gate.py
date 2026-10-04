"""★ 用户偏好写入门禁的负例测试（★ 含**用修复前的原文**证明它能响）。

★ 事实 62：**没有负例的判据不算数** —— ★ 正例取自 `git show d082449e^:…`（★ 处置前那一版）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁的负例测试）
# 文件:   `scripts/check_user_preference_writes.py`（★ 被测）
# 定位:   ★★★ 三条契约，每条一个负例：
#     ① **裸写必须被抓**（★ 正例 = 修复前的 `sw_export.py` 那一行逐字）；
#     ② `with preference_guard(...)` 里的写**不许误伤**；
#     ③ `preference-guard:` 标记**必须带非空理由**（★ 光盖章不算 —— 否则判据退化成摆设）。
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_user_preference_writes as gate  # noqa: E402

#: ★ 正例：**修复前** `scripts/sw_export.py::export_to_stl` 的逐字形态
PRE_FIX = '''
def export_to_stl(model, output_path, quality="fine"):
    quality_map = {"coarse": 1, "fine": 0}
    if quality in quality_map:
        model.SetUserPreferenceIntegerValue(78, quality_map[quality])  # swSTLQuality
    return _export_generic(model, output_path)
'''

#: ★ 反例 1：走 guard（★ 被认可的姿势）
GUARDED = '''
def export_to_stl(model, output_path, quality="fine"):
    with preference_guard(model, [Preference("integer", 78, 0)]) as rep:
        return _export_generic(model, output_path)
'''

#: ★ 反例 2：带**非空理由**的确认标记（★ 用于「设」「还原」分居两函数的情形）
MARKED = '''
def ensure_default_templates(sw):
    # preference-guard: 旧值记进 restore，由 restore_default_templates 在 finally 里还原
    sw.SetUserPreferenceToggle(111, True)
    return {}
'''

#: ★ 反例 3：**只有标记、没有理由** ⇒ 必须仍然被抓（★ 否则"盖章"就能过）
MARKER_NO_REASON = '''
def ensure_default_templates(sw):
    # preference-guard:
    sw.SetUserPreferenceToggle(111, True)
    return {}
'''


def _hits(src: str, rel: str = "x.py") -> list[dict]:
    return gate.scan_one(rel, src, exempt_files=set())


def test_positive_the_pre_fix_line_is_caught() -> None:
    """★★★ 核心正例：**修复前**那一行必须被抓住。"""
    hits = _hits(PRE_FIX)
    assert hits, "★ 裸写 `model.SetUserPreferenceIntegerValue(78, …)` **没被抓住**"
    assert hits[0]["func"] == "SetUserPreferenceIntegerValue" and hits[0]["line"] == 5, hits


def test_negative_guarded_write_is_allowed() -> None:
    """★ 走 `preference_guard` 的写**不许误伤**。"""
    assert not _hits(GUARDED), _hits(GUARDED)


def test_negative_marked_write_with_reason_is_allowed() -> None:
    """★ 带非空理由的标记 ⇒ 放行（★ 那是"设/还原分居"的合法写法）。"""
    assert not _hits(MARKED), _hits(MARKED)


def test_negative_marker_without_reason_is_still_caught() -> None:
    """★★ **只有标记、没有理由** ⇒ 必须抓（★ 否则判据退化成"盖个章"）。"""
    assert _hits(MARKER_NO_REASON), "★ 空理由的标记竟然放行了"


def test_the_real_pre_fix_file_from_git_is_caught() -> None:
    """★★ 拿 **git 里处置前那一版真文件**再证一次（★ 比手写样本硬）。"""
    for rev, path in (("a96f89a", "scripts/sw_export.py"),
                      ("a96f89a", "subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py")):
        raw = subprocess.run(["git", "-C", str(ROOT), "show", "%s:%s" % (rev, path)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace")
        if raw.returncode != 0 or not raw.stdout:
            continue                                           # ★ 取不到就跳过这一份（不假装证明）
        hits = _hits(raw.stdout, rel=path)
        assert hits, "★ %s@%s 里的裸写没被抓到" % (path, rev)


def test_exemptions_need_reason_and_evidence() -> None:
    """★ 豁免条目**缺 reason/evidence** ⇒ 无效（★ 名单不是"免死金牌"）。"""
    data, bad = gate.load_exemptions()
    assert not bad, bad
    for item in data.get("exemptions") or []:
        assert str(item.get("reason") or "").strip(), item
        assert str(item.get("evidence") or "").strip(), item


def test_current_tree_is_clean() -> None:
    """★ 全仓现状（★ 门禁的实际输出）。"""
    violations, bad, seen = gate.scan()
    assert seen > 300, "★ 只扫了 %d 个文件 ⇒ 扫描根可能挂错了" % seen
    assert not bad, bad
    assert not violations, "★ 全仓有 %d 处不可还原的偏好写入：%r" % (len(violations), violations[:3])


# ── 直接运行 ──────────────────────────────────────────────────────────────

def _main() -> int:
    fails = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  [ok] %s" % name)
            except AssertionError as exc:
                fails.append(name)
                print("  [FAIL] %s: %s" % (name, exc))
    print("★ %d 条失败" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_main())

"""★ 门禁的契约与两侧负例：相对导入必须带兜底（规格 210 · B3 的真机产物）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_relative_imports.py` + `scripts/sw_simulation_loads.py` 的修法
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 起因（真机）：
#   ★★ 存活普查跑到 `solidworks_simulation_apply_link_connector` 时报
#     `ImportError: attempted relative import with no known parent package` ✗
#   ⇒ ★ 追到函数内**无兜底**的相对导入 ⇒ ★ 按仓库既有写法（try 相对 / 回退绝对）修 ✓
# 判据:   ★★ **两侧都要证**（★ 事实 62：一个门禁「写了」不等于它「有效」）：
#     · ★ **负例**：★ **修复前**的原文（`git show HEAD:<file>`）⇒ ★ **必须命中** ✓
#     · ★ **正例**：★ **修复后**的文件 ⇒ ★ **必须 0 命中** ✓
#   ★ 另有**契约**：★ 门禁判据必须用 `startswith("try:")` ——
#     ★ 因为修法带 `# noqa` 注释，★ 用 `== "try:"` 会把**已修好的**算成没兜底 ✗
# 官方依据: 无 —— ★ Python 语言语义，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_relative_imports as G                               # noqa: E402


def _scan_text(text: str) -> list:
    """★ 把一段源码放进临时 `scripts/` 里扫（★ 只用门禁自己的 `scan`）✓"""
    d = Path(tempfile.mkdtemp())
    (d / "scripts").mkdir()
    (d / "scripts" / "m.py").write_text(textwrap.dedent(text), encoding="utf-8")
    return G.scan(d)


def test_unguarded_relative_import_is_caught():
    """★★ **负例**：★ 无兜底的相对导入 ⇒ ★ **必须被扫出来** ✓"""
    assert len(_scan_text("""
        def f():
            from .sw_part import sketch
            return sketch
    """)) == 1


def test_guarded_relative_import_is_accepted_even_with_a_trailing_comment():
    """★★ **契约（我第一版栽在这）**：★ 修法带 `# noqa` 注释 ⇒
    ★ 判据必须用 `startswith("try:")` ⇒ ★ **带注释的 try 也要认** ✓"""
    assert _scan_text("""
        def f():
            try:                                    # noqa: SIM105
                from .sw_part import sketch
            except ImportError:
                from sw_part import sketch
            return sketch
    """) == []


def test_the_repaired_file_is_clean_and_the_old_one_was_not():
    """★★★ **两侧一起证**（★ 事实 62：用**修复前**的原文当负例输入）✓"""
    #: ★★★ **负例必须钉在一个"确定的旧提交"上，★ 不能钉 `HEAD`** ——
    #:   ★ 真机踩过：★ 我第一版写 `git show HEAD:…` ⇒ ★★ 而**修复一提交，HEAD 就含修复**
    #:     ⇒ ★ 负例的前提**自动失效** ⇒ 测试变红 ✗（★ 而它**看起来像门禁坏了**）✓
    #:   ★ 正解：★ 钉 **`d6bb5c27`**（★ 修复前的那一个提交）✓
    FIXED_AT = "62796a28"        # ★ `sw_simulation_loads.py` **修复前**的最后一个提交 ✓
    #:   ★（★ 我第一次写 `d6bb5c27` ⇒ ★ 那**已经是修复后**了 ⇒ 负例前提失效 ✗ ——
    #:     ★ **钉旧提交也要实测确认**，★ 不能凭"它看起来在前面"就选 ✓）
    before = subprocess.run(["git", "show", "%s:scripts/sw_simulation_loads.py" % FIXED_AT],
                            cwd=str(ROOT), capture_output=True,
                            encoding="utf-8", errors="replace").stdout
    assert before, "★ 取不到修复前的原文（★ 该提交还在吗）"
    assert len(_scan_text(before)) == 17, "★ 修复前应当命中 17 处"
    now = (ROOT / "scripts" / "sw_simulation_loads.py").read_text(encoding="utf-8")
    assert _scan_text(now) == [], "★ 修复后应当 0 命中"


def test_the_repo_stays_within_the_ratchet_baseline():
    """★ **棘轮**：★ 全仓存量**只许变少、不许变多** ✓"""
    found = G.scan(ROOT)
    assert len(found) <= G.BASELINE_COUNT, \
        "★ 无兜底的相对导入增长了：%d > %d" % (len(found), G.BASELINE_COUNT)

"""★ 规格 295 判据：R8 比对前必须剥掉**非数据字段**（日期），而真数据变化仍须报红。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_union_conventions.py` 的 `check_docs()`（R8 新鲜度）
#         `scripts/gen_level_audit.py:81`（★ 把 `date.today()` 写进正文 —— 病灶）
#         `docs/AUTO_HANDOFF.md` ③ 第 **74** 条（★ 上一轮记下的坑）
# 定位:   ① 只差日期的盘上文件**不得**被判成「与最新数据不一致」（★ 否则每天一次假红）；
#         ② 真数据变化**必须**仍然报红（★ 不能把门禁改瞎）；
#         ③ 归一化**可指认**（★ 不是静默吞掉）；
#         ④ 边界冻结：不改生成器、不改 `capabilities.yaml`；
#         ⑤ 归一化函数的**正负例**（★ 事实 62：写了 ≠ 有效）。
# 官方依据: 不适用（纯静态：读文本 + 调门禁函数，**不连 SolidWorks**）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_union_conventions.py"
GEN = ROOT / "scripts" / "gen_level_audit.py"
AUDIT = ROOT / "docs" / "union-level-audit.md"


def _gate():
    """把门禁当模块加载（★ 它不是包，用 `spec_from_file_location`）。"""
    spec = importlib.util.spec_from_file_location("_uc_gate_295", GATE)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_uc_gate_295"] = mod
    spec.loader.exec_module(mod)
    return mod


#: ★ 生成日期那行的形状（★ 病灶就在这里）
DATE_LINE = re.compile(r"生成日期：\d{4}-\d{2}-\d{2}")


def test_normalizer_is_declared_and_named():
    """★ FR-003：归一化必须**可指认** —— 门禁里有一个具名的归一化函数。"""
    m = _gate()
    fn = getattr(m, "normalize_generated_text", None)
    assert callable(fn), (
        "`check_union_conventions` 里没有 `normalize_generated_text` —— "
        "★ R8 需要它把「非数据字段」剥掉再比对（★ 不能靠静默吞掉差异）"
    )


def test_normalizer_keeps_data_lines_and_drops_dates():
    """★ FR-005：归一化函数的**正负例**（★ 事实 62：写了 ≠ 有效）。"""
    m = _gate()
    fn = m.normalize_generated_text

    #: ★ 正例①：只差日期 ⇒ 归一化后**相等**
    a = "> 生成日期：2026-10-09 ｜ 数据源：`capabilities.yaml`\n| 1 | cap-a | verified |\n"
    b = "> 生成日期：2026-10-10 ｜ 数据源：`capabilities.yaml`\n| 1 | cap-a | verified |\n"
    assert fn(a) == fn(b), "★ 只差日期的两份应归一化到同一结果"

    #: ★ 正例②：日期**占位**后，数据行原样保留（★ 不能把整行删掉、也不能把数据也吞了）
    assert "cap-a" in fn(a), "★ 归一化不得吞掉数据行"
    assert "生成日期" in fn(a), "★ 归一化应保留字段名（★ 只是把值换成占位）"

    #: ★ 负例：**真数据变化** ⇒ 归一化后**必须不同**
    c = "> 生成日期：2026-10-10 ｜ 数据源：`capabilities.yaml`\n| 1 | cap-a | stitched |\n"
    assert fn(a) != fn(c), "★★ 归一化把「level 变了」也吞了 ⇒ 门禁被改瞎"


def test_date_only_difference_is_not_a_freshness_failure(monkeypatch):
    """★★★ FR-001：盘上文件**只差日期** ⇒ 门禁**不得**报 R8 不一致。"""
    m = _gate()
    on_disk = AUDIT.read_text(encoding="utf-8")
    #: ★ 造「昨天生成的」那份（★ 只动日期，★ 数据一字不改）
    stale = DATE_LINE.sub("生成日期：2026-10-09", on_disk)
    assert stale != on_disk, "★ 这份文件里没有 `生成日期：YYYY-MM-DD` ⇒ 判据失效"

    real_read = Path.read_text

    def fake_read(self, *a, **kw):
        if self.name == "union-level-audit.md":
            return stale
        return real_read(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", fake_read)
    bad = m.check_docs()
    hits = [b for b in bad if "union-level-audit" in b]
    assert not hits, (
        "★★★ 只差日期就被判成「与最新数据不一致」⇒ **每天一次假红**（★ 本轮要修的就是它）：\n  "
        + "\n  ".join(hits)
    )


def test_real_data_difference_is_still_red(monkeypatch):
    """★★★ FR-002：**真数据变化**必须仍然报红（★ 不能把门禁改瞎）。"""
    m = _gate()
    on_disk = AUDIT.read_text(encoding="utf-8")
    #: ★ 把某条能力的 level 改掉（★ 这是**真**数据变化，不是日期）
    #: ★ 数据行的 level 是**反引号包着的**（逐字：`` | `verified` | ``）
    tampered = on_disk.replace("| `verified` |", "| `stitched` |", 1)
    assert tampered != on_disk, "★ 这份文件里没有 `` | `verified` | `` ⇒ 判据失效"

    real_read = Path.read_text

    def fake_read(self, *a, **kw):
        if self.name == "union-level-audit.md":
            return tampered
        return real_read(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", fake_read)
    bad = m.check_docs()
    hits = [b for b in bad if "union-level-audit" in b]
    assert hits, (
        "★★★ 真数据被改了却**不报红** ⇒ 门禁被改瞎了（★ 比假红更糟）"
    )


def test_generator_and_manifest_untouched():
    """★ FR-004：边界冻结 —— 本轮**只改比对口径**，不改生成器、不改 `capabilities.yaml`。

    ★ 判据：生成器**仍然**把日期写进正文（★ 那是**它的**正当行为 ——
      ★ 归一化是**读者**的责任，不是让生成器**停止记录**生成时间）。
    """
    src = GEN.read_text(encoding="utf-8")
    assert "date.today()" in src, (
        "★ 生成器不再写生成日期了 —— 那不是本轮的目标："
        "★ 归一化该发生在**比对侧**，生成物**仍应**记录它是什么时候生成的"
    )
